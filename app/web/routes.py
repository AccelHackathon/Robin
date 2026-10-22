"""Workstream B: server-rendered onboarding, documents, consent and read-only tracking."""

from __future__ import annotations
import asyncio
import re
import secrets
from pathlib import Path
from urllib.parse import quote
from uuid import UUID
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse, FileResponse, Response, JSONResponse
from fastapi.templating import Jinja2Templates
from psycopg.errors import UniqueViolation
from psycopg.types.json import Jsonb
from app import db
from app.web import logging as web_logging  # noqa: F401
from app.config import settings
from app.web.auth import (
    session,
    new_session,
    check_csrf,
    verify_password,
    hasher,
    DUMMY_HASH,
    COOKIE,
    ANON_CSRF,
    digest,
    secure_cookie,
)
from app.ingestion.pdf import MAX_BYTES, sniff_type, sha256
from app.agents.intake.guarantees import GUARANTEES
from app.agents.intake.graph import rows

router = APIRouter(tags=["web"])
ROOT = Path(__file__).parent
templates = Jinja2Templates(directory=str(ROOT / "templates"))
STEPS = ["business", "documents", "mandate", "done"]
MANDATE_VERSION = "2026-10-22-v1"
MANDATE_SCOPE = {
    "allowed": [
        "obtain documents",
        "transmit confirmed facts and evidence",
        "contact insurer, broker and expert",
        "request status",
        "follow up",
    ],
    "excluded": ["accept an offer", "settle", "waive rights", "collect funds"],
}


def uid(value):
    try:
        return str(UUID(str(value)))
    except (ValueError, TypeError):
        raise HTTPException(404, "Not found.")


def page(request, name, **context):
    response = templates.TemplateResponse(request=request, name=name, context=context)
    response.headers["Cache-Control"] = "no-store"
    response.headers["Referrer-Policy"] = (
        "no-referrer" if "token" in request.query_params else "same-origin"
    )
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self'; form-action 'self'; frame-ancestors 'none'; base-uri 'self'"
    )
    return response


def redirect(path):
    return RedirectResponse(path, status_code=303)


async def state_for(aid):
    result = await rows("SELECT * FROM onboarding WHERE account_id=%s", (aid,))
    return result[0] if result else {}


async def form_session(request):
    s = await session(request)
    form = await request.form()
    check_csrf(request, form, s["csrf_token"])
    return s, form


async def queue(conn, aid, kind, payload):
    await conn.execute(
        "INSERT INTO events(source,kind,account_id,payload) VALUES (%s,%s,%s,%s)",
        ("web", kind, aid, Jsonb({"account_id": str(aid), **payload})),
    )


@router.get("/static/{asset:path}")
async def static(asset: str):
    target = (ROOT / "static" / asset).resolve()
    if not target.is_relative_to((ROOT / "static").resolve()) or not target.is_file():
        raise HTTPException(404)
    return FileResponse(target)


@router.get("/")
async def home(request: Request):
    s = await session(request, False)
    return page(request, "home.html", user=s)


@router.get("/signup")
@router.get("/login")
async def auth_page(request: Request):
    s = await session(request, False)
    if s:
        return redirect("/onboarding/resume")
    csrf = secrets.token_urlsafe(32)
    response = page(
        request,
        "auth.html",
        signup=request.url.path == "/signup",
        csrf=csrf,
        error=None,
        urgent=request.query_params.get("urgent") == "1",
    )
    response.set_cookie(
        ANON_CSRF,
        csrf,
        httponly=True,
        samesite="strict",
        secure=secure_cookie(request),
        max_age=3600,
        path="/",
    )
    return response


@router.post("/signup")
@router.post("/login")
async def authenticate(request: Request):
    if not db.pool:
        raise HTTPException(503, "Account setup is temporarily unavailable.")
    form = await request.form()
    csrf = request.cookies.get(ANON_CSRF)
    check_csrf(request, form, csrf)
    signup = request.url.path == "/signup"
    email = str(form.get("email", "")).strip().lower()
    password = str(form.get("password", ""))
    error = None
    account_id = None
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) or len(email) > 254:
        error = "Enter a valid email address."
    elif not 12 <= len(password) <= 256:
        error = "Use a password between 12 and 256 characters."
    else:
        # IP/email attempts are hashed; raw credentials are never logged.
        key = digest((request.client.host if request.client else "") + "|" + email)
        async with db.pool.connection() as conn:
            count = await (
                await conn.execute(
                    "SELECT count(*) FROM web_auth_attempts WHERE key=%s AND created_at>now()-interval '10 minutes'",
                    (key,),
                )
            ).fetchone()
            if count[0] >= 10:
                raise HTTPException(429, "Too many attempts. Try again in 10 minutes.")
            await conn.execute("INSERT INTO web_auth_attempts(key) VALUES (%s)", (key,))
        if signup:
            password_hash = await asyncio.to_thread(hasher.hash, password)
            try:
                async with db.pool.connection() as conn:
                    account_id = (
                        await (
                            await conn.execute(
                                "INSERT INTO accounts(email,password_hash) VALUES (%s,%s) RETURNING id",
                                (email, password_hash),
                            )
                        ).fetchone()
                    )[0]
                    await conn.execute(
                        "INSERT INTO onboarding(account_id,urgent) VALUES (%s,%s)",
                        (account_id, form.get("urgent") == "1"),
                    )
            except UniqueViolation:
                error = "Unable to create this account. Try signing in instead."
        else:
            found = await rows(
                "SELECT id,password_hash FROM accounts WHERE email=%s", (email,)
            )
            valid = await verify_password(
                found[0]["password_hash"] if found else DUMMY_HASH, password
            )
            if valid and found:
                account_id = found[0]["id"]
            else:
                error = "The email or password is incorrect."
    if error:
        return page(
            request,
            "auth.html",
            signup=signup,
            csrf=csrf,
            error=error,
            email=email,
            urgent=form.get("urgent") == "1",
        )
    response = redirect("/onboarding/resume")
    response.delete_cookie(ANON_CSRF, path="/")
    return await new_session(response, request, account_id)


@router.post("/logout")
async def logout(request: Request):
    s, _ = await form_session(request)
    async with db.pool.connection() as conn:
        await conn.execute(
            "DELETE FROM web_sessions WHERE token_hash=%s AND account_id=%s",
            (s["token_hash"], s["account_id"]),
        )
    response = redirect("/")
    response.delete_cookie(COOKIE, path="/")
    return response


@router.get("/onboarding/resume")
async def resume(request: Request):
    s = await session(request)
    state = await state_for(s["account_id"])
    step = state.get("step", "business")
    return redirect("/onboarding/" + (step if step in STEPS else "business"))


@router.get("/onboarding/business")
async def business(request: Request):
    s = await session(request)
    aid = s["account_id"]
    found = await rows(
        "SELECT * FROM businesses WHERE account_id=%s ORDER BY created_at LIMIT 1",
        (aid,),
    )
    return page(
        request,
        "business.html",
        user=s,
        business=found[0] if found else {},
        state=await state_for(aid),
        step=0,
        error=None,
    )


@router.post("/onboarding/business")
async def save_business(request: Request):
    s, form = await form_session(request)
    aid = s["account_id"]
    names = [
        "name",
        "siret",
        "address",
        "activity",
        "representative_name",
        "representative_role",
        "phone",
        "insurer_name",
        "insurer_contact_email",
        "broker_name",
        "tenant_or_owner",
    ]
    values = {k: str(form.get(k, "")).strip() for k in names}
    error = None
    if any(len(v) > 1000 for v in values.values()):
        error = "Please keep each field under 1,000 characters."
    elif not values["name"] or not values["representative_name"]:
        error = "Add your business name and your name."
    elif values["siret"] and not re.fullmatch(
        r"\d{14}", values["siret"].replace(" ", "")
    ):
        error = "A SIRET has 14 digits. You can leave it empty for now."
    elif values["tenant_or_owner"] not in ("tenant", "owner", "unknown"):
        error = "Choose your premises status."
    elif values["insurer_contact_email"] and not re.fullmatch(
        r"[^\s@]+@[^\s@]+\.[^\s@]+", values["insurer_contact_email"]
    ):
        error = "Enter a valid insurer email or leave it empty."
    values["vat_recoverable"] = {"yes": True, "no": False, "unknown": None}.get(
        str(form.get("vat_recoverable"))
    )
    state = await state_for(aid)
    incident = str(form.get("incident", "")).strip()[:5000]
    urgent = bool(form.get("urgent")) or state.get("urgent", False)
    if error:
        return page(
            request,
            "business.html",
            user=s,
            business=values,
            state={**state, "urgent": urgent, "incident": incident},
            step=0,
            error=error,
        )
    async with db.pool.connection() as conn:
        await conn.execute("SELECT id FROM accounts WHERE id=%s FOR UPDATE", (aid,))
        existing = await (
            await conn.execute(
                "SELECT id FROM businesses WHERE account_id=%s ORDER BY created_at LIMIT 1",
                (aid,),
            )
        ).fetchone()
        if existing:
            await conn.execute(
                "UPDATE businesses SET "
                + ",".join(k + "=%s" for k in values)
                + " WHERE id=%s AND account_id=%s",
                (*values.values(), existing[0], aid),
            )
        else:
            await conn.execute(
                "INSERT INTO businesses(account_id,"
                + ",".join(values)
                + ") VALUES ("
                + ",".join(["%s"] * (len(values) + 1))
                + ")",
                (aid, *values.values()),
            )
        next_step = "mandate" if urgent else "documents"
        await conn.execute(
            "UPDATE onboarding SET step=%s,urgent=%s,incident=%s,updated_at=now() WHERE account_id=%s",
            (next_step, urgent, incident, aid),
        )
    return redirect("/onboarding/" + next_step)


@router.get("/onboarding/documents")
async def documents(request: Request):
    s = await session(request)
    docs = await rows(
        "SELECT id,filename,doc_type,readable,page_count,metadata FROM documents WHERE account_id=%s ORDER BY created_at",
        (s["account_id"],),
    )
    return page(
        request,
        "documents.html",
        user=s,
        documents=docs,
        step=1,
        error=request.query_params.get("error"),
    )


@router.post("/onboarding/documents")
async def upload(request: Request):
    s, form = await form_session(request)
    aid = s["account_id"]
    files = form.getlist("files")
    staged = []
    if len(files) > 20:
        raise HTTPException(422, "Choose no more than 20 files at a time.")
    for file in files:
        if not getattr(file, "filename", None):
            continue
        content = await file.read(MAX_BYTES + 1)
        await file.close()
        if len(content) > MAX_BYTES:
            return redirect(
                "/onboarding/documents?error="
                + quote("Files must be 20 MB or smaller.")
            )
        try:
            mime = sniff_type(content)
        except ValueError as exc:
            return redirect("/onboarding/documents?error=" + quote(str(exc)))
        filename = Path(file.filename.replace("\\", "/")).name[:200]
        staged.append((filename, mime, content, sha256(content)))
    async with db.pool.connection() as conn:
        await conn.execute("SELECT id FROM accounts WHERE id=%s FOR UPDATE", (aid,))
        count = await (
            await conn.execute(
                "SELECT count(*) FROM documents WHERE account_id=%s AND origin='web_upload' AND created_at>now()-interval '1 hour'",
                (aid,),
            )
        ).fetchone()
        if count[0] + len(staged) > 20:
            raise HTTPException(429, "Upload limit reached. Try again in an hour.")
        for filename, mime, content, checksum in staged:
            existing = await (
                await conn.execute(
                    "SELECT id FROM documents WHERE account_id=%s AND sha256=%s",
                    (aid, checksum),
                )
            ).fetchone()
            if existing:
                continue
            doc = await (
                await conn.execute(
                    """INSERT INTO documents(account_id,doc_type,origin,filename,mime_type,sha256,content,readable,metadata)
                VALUES (%s,'other','web_upload',%s,%s,%s,%s,false,%s) RETURNING id""",
                    (
                        aid,
                        filename,
                        mime,
                        checksum,
                        content,
                        Jsonb({"analysis_status": "pending"}),
                    ),
                )
            ).fetchone()
            await queue(
                conn,
                aid,
                "document_added",
                {
                    "document_id": str(doc[0]),
                    "provider_ref": "web-document-" + str(doc[0]),
                },
            )
        if staged:
            await conn.execute(
                "UPDATE onboarding SET intake_status='pending',updated_at=now() WHERE account_id=%s",
                (aid,),
            )
    return redirect("/onboarding/documents")


@router.post("/onboarding/documents/continue")
async def documents_continue(request: Request):
    s, _ = await form_session(request)
    async with db.pool.connection() as conn:
        await conn.execute(
            "UPDATE onboarding SET step='mandate' WHERE account_id=%s",
            (s["account_id"],),
        )
    return redirect("/onboarding/mandate")


@router.get("/documents/{document_id}")
async def download(document_id: str, request: Request):
    s = await session(request)
    found = await rows(
        "SELECT filename,mime_type,content FROM documents WHERE id=%s AND account_id=%s",
        (uid(document_id), s["account_id"]),
    )
    if not found:
        raise HTTPException(404)
    doc = found[0]
    return Response(
        bytes(doc["content"] or b""),
        media_type=doc["mime_type"],
        headers={
            "Content-Disposition": "attachment; filename*=UTF-8''"
            + quote(doc["filename"] or "document", safe=""),
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.get("/onboarding/mandate")
async def mandate(request: Request):
    s = await session(request)
    business = await rows(
        "SELECT * FROM businesses WHERE account_id=%s ORDER BY created_at LIMIT 1",
        (s["account_id"],),
    )
    if not business:
        return redirect("/onboarding/business")
    return page(
        request,
        "mandate.html",
        user=s,
        business=business[0],
        step=2,
        error=None,
        version=MANDATE_VERSION,
    )


@router.post("/onboarding/mandate")
async def sign(request: Request):
    s, form = await form_session(request)
    aid = s["account_id"]
    name = str(form.get("signer_name", "")).strip()
    role = str(form.get("signer_role", "")).strip()
    business = await rows(
        "SELECT * FROM businesses WHERE account_id=%s ORDER BY created_at LIMIT 1",
        (aid,),
    )
    if not business:
        return redirect("/onboarding/business")
    if (
        not name
        or not role
        or len(name) > 200
        or len(role) > 200
        or not form.get("mandate")
        or not form.get("data_processing")
    ):
        return page(
            request,
            "mandate.html",
            user=s,
            business=business[0],
            step=2,
            error="Confirm the mandate and data processing, and add your name and role.",
            version=MANDATE_VERSION,
        )
    async with db.pool.connection() as conn:
        await conn.execute("SELECT id FROM accounts WHERE id=%s FOR UPDATE", (aid,))
        completed = await (
            await conn.execute(
                "SELECT completed_at,urgent,incident FROM onboarding WHERE account_id=%s",
                (aid,),
            )
        ).fetchone()
        if completed[0]:
            return redirect("/onboarding/done")
        await conn.execute(
            """INSERT INTO mandates(account_id,version,scope,signer_name,signer_role,proof)
          VALUES (%s,%s,%s,%s,%s,%s)""",
            (
                aid,
                MANDATE_VERSION,
                Jsonb(MANDATE_SCOPE),
                name,
                role,
                Jsonb(
                    {
                        "method": "typed_name_and_checkbox",
                        "account_email": s["email"],
                        "mandate_version": MANDATE_VERSION,
                    }
                ),
            ),
        )
        for purpose in ["mandate", "data_processing"] + (
            ["telegram"] if form.get("telegram") else []
        ):
            await conn.execute(
                "INSERT INTO consents(account_id,purpose,version) VALUES (%s,%s,%s)",
                (aid, purpose, MANDATE_VERSION),
            )
        await conn.execute(
            "UPDATE onboarding SET step='done',completed_at=now(),intake_status='pending',updated_at=now() WHERE account_id=%s",
            (aid,),
        )
        await queue(
            conn,
            aid,
            "onboarding_done",
            {
                "urgent": completed[1],
                "incident": completed[2],
                "provider_ref": "web-onboarding-" + str(aid),
            },
        )
        if form.get("telegram"):
            await conn.execute(
                "INSERT INTO link_codes(code,account_id,expires_at) VALUES (%s,%s,now()+interval '15 minutes')",
                (secrets.token_urlsafe(24), aid),
            )
    return redirect("/onboarding/done")


@router.get("/onboarding/done")
async def done(request: Request):
    s = await session(request)
    aid = s["account_id"]
    state = await state_for(aid)
    if not state.get("completed_at"):
        return redirect("/onboarding/resume")
    codes = await rows(
        "SELECT code,expires_at FROM link_codes WHERE account_id=%s AND used_at IS NULL AND expires_at>now() ORDER BY created_at DESC LIMIT 1",
        (aid,),
    )
    consent = await rows(
        "SELECT 1 FROM consents WHERE account_id=%s AND purpose='telegram' AND revoked_at IS NULL",
        (aid,),
    )
    username = settings.telegram_bot_username
    if username:
        username = username.lstrip("@")
    url = (
        f"https://t.me/{username}?start={codes[0]['code']}"
        if username
        and re.fullmatch(r"[A-Za-z0-9_]{5,32}", username)
        and codes
        and consent
        else None
    )
    claims = await rows(
        "SELECT id,summary,status FROM claims WHERE account_id=%s ORDER BY created_at DESC",
        (aid,),
    )
    return page(
        request,
        "done.html",
        user=s,
        state=state,
        step=3,
        telegram_url=url,
        channel_consent=bool(consent),
        bot_configured=bool(username),
        claims=claims,
    )


@router.post("/onboarding/telegram-link")
async def renew_link(request: Request):
    s, _ = await form_session(request)
    aid = s["account_id"]
    consent = await rows(
        "SELECT 1 FROM consents WHERE account_id=%s AND purpose='telegram' AND revoked_at IS NULL",
        (aid,),
    )
    if not consent:
        raise HTTPException(403, "Telegram consent is required.")
    async with db.pool.connection() as conn:
        await conn.execute("SELECT id FROM accounts WHERE id=%s FOR UPDATE", (aid,))
        await conn.execute(
            "UPDATE link_codes SET expires_at=now() WHERE account_id=%s AND used_at IS NULL",
            (aid,),
        )
        await conn.execute(
            "INSERT INTO link_codes(code,account_id,expires_at) VALUES (%s,%s,now()+interval '15 minutes')",
            (secrets.token_urlsafe(24), aid),
        )
    return redirect("/onboarding/done")


@router.post("/onboarding/retry")
async def retry(request: Request):
    s, _ = await form_session(request)
    aid = s["account_id"]
    async with db.pool.connection() as conn:
        await conn.execute("SELECT id FROM accounts WHERE id=%s FOR UPDATE", (aid,))
        pending = await (
            await conn.execute(
                "SELECT 1 FROM events WHERE account_id=%s AND source='web' AND kind='document_added' AND status IN ('pending','processing')",
                (aid,),
            )
        ).fetchone()
        if not pending:
            await queue(conn, aid, "document_added", {"reason": "retry"})
    return redirect("/onboarding/done")


@router.get("/onboarding/profile.json")
async def profile(request: Request):
    s = await session(request)
    aid = s["account_id"]
    state = await state_for(aid)
    profile = await rows(
        """SELECT DISTINCT ON(guarantee) guarantee,subscribed,ceiling,deductible_detail,quote,page,confidence,source_clause_id,version
        FROM coverage_profile WHERE account_id=%s ORDER BY guarantee,version DESC,created_at DESC""",
        (aid,),
    )
    for f in profile:
        f["label"] = GUARANTEES.get(f["guarantee"], (f["guarantee"],))[0]
        f["subscribed"] = (
            "yes"
            if f["subscribed"] is True
            else "no"
            if f["subscribed"] is False
            else "unknown"
        )
    tasks = await rows(
        "SELECT description FROM intake_tasks WHERE account_id=%s AND resolved_at IS NULL ORDER BY created_at",
        (aid,),
    )
    linked = await rows("SELECT 1 FROM telegram_links WHERE account_id=%s", (aid,))
    welcome = await rows(
        "SELECT delivery_status,failed_reason FROM communications WHERE account_id=%s AND channel='telegram' AND direction='outbound' ORDER BY created_at LIMIT 1",
        (aid,),
    )
    return JSONResponse(
        {
            "status": state.get("intake_status", "pending"),
            "error": state.get("intake_error"),
            "guarantees": profile,
            "tasks": [t["description"] for t in tasks],
            "telegram_linked": bool(linked),
            "welcome_status": welcome[0]["delivery_status"] if welcome else "not_sent",
            "link_expired": not bool(
                await rows(
                    "SELECT 1 FROM link_codes WHERE account_id=%s AND used_at IS NULL AND expires_at>now()",
                    (aid,),
                )
            ),
        },
        headers={"Cache-Control": "no-store"},
    )


@router.get("/clauses/{clause_id}")
async def clause(clause_id: int, request: Request):
    s = await session(request)
    found = await rows(
        """SELECT c.*,d.filename FROM clauses c JOIN documents d ON d.id=c.document_id
       JOIN account_contracts a ON a.document_id=d.id WHERE c.id=%s AND a.account_id=%s AND (d.account_id IS NULL OR d.account_id=%s)""",
        (clause_id, s["account_id"], s["account_id"]),
    )
    if not found:
        raise HTTPException(404)
    return page(request, "clause.html", user=s, clause=found[0])


@router.get("/claims/{claim_id}/track")
async def tracking(claim_id: str, request: Request):
    claim_id = uid(claim_id)
    token = request.query_params.get("token", "")
    s = await session(request, False)
    if token:
        claims = await rows(
            "SELECT * FROM claims WHERE id=%s AND tracking_token_hash=%s",
            (claim_id, digest(token)),
        )
    elif s:
        claims = await rows(
            "SELECT * FROM claims WHERE id=%s AND account_id=%s",
            (claim_id, s["account_id"]),
        )
    else:
        claims = []
    if not claims:
        raise HTTPException(404, "Tracking link not found or expired.")
    claim = claims[0]
    aid = claim["account_id"]
    items = await rows(
        """SELECT l.* FROM loss_items l JOIN claims c ON c.id=l.claim_id
      WHERE c.id=%s AND c.account_id=%s AND NOT EXISTS(SELECT 1 FROM loss_items n WHERE n.supersedes=l.id AND n.claim_id=c.id) ORDER BY l.created_at""",
        (claim_id, aid),
    )
    communications = await rows(
        "SELECT created_at,channel,direction,subject,body,delivery_status FROM communications WHERE claim_id=%s AND account_id=%s ORDER BY created_at DESC",
        (claim_id, aid),
    )
    actions = await rows(
        "SELECT created_at,tool,ok FROM actions WHERE claim_id=%s AND account_id=%s ORDER BY created_at DESC",
        (claim_id, aid),
    )
    deadlines = await rows(
        """SELECT t.* FROM scheduled_tasks t JOIN claims c ON c.id=t.claim_id WHERE c.id=%s AND c.account_id=%s ORDER BY t.due_at""",
        (claim_id, aid),
    )
    return page(
        request,
        "tracking.html",
        user=s,
        claim=claim,
        items=items,
        communications=communications,
        actions=actions,
        deadlines=deadlines,
    )


@router.post("/claims/{claim_id}/tracking-link")
async def create_tracking_link(claim_id: str, request: Request):
    s, _ = await form_session(request)
    claim_id = uid(claim_id)
    token = secrets.token_urlsafe(32)
    async with db.pool.connection() as conn:
        row = await (
            await conn.execute(
                "UPDATE claims SET tracking_token_hash=%s WHERE id=%s AND account_id=%s RETURNING id",
                (digest(token), claim_id, s["account_id"]),
            )
        ).fetchone()
    if not row:
        raise HTTPException(404)
    return redirect(f"/claims/{claim_id}/track?token={token}")


@router.post("/onboarding/telegram-consent")
async def telegram_consent(request: Request):
    s, form = await form_session(request)
    aid = s["account_id"]
    state = await state_for(aid)
    if not state.get("completed_at") or not form.get("telegram"):
        raise HTTPException(422, "Complete setup and confirm Telegram consent first.")
    async with db.pool.connection() as conn:
        await conn.execute("SELECT id FROM accounts WHERE id=%s FOR UPDATE", (aid,))
        await conn.execute(
            """INSERT INTO consents(account_id,purpose,version)
            SELECT %s,'telegram',%s WHERE NOT EXISTS
            (SELECT 1 FROM consents WHERE account_id=%s AND purpose='telegram' AND revoked_at IS NULL)""",
            (aid, MANDATE_VERSION, aid),
        )
        await conn.execute(
            "UPDATE link_codes SET expires_at=now() WHERE account_id=%s AND used_at IS NULL",
            (aid,),
        )
        await conn.execute(
            "INSERT INTO link_codes(code,account_id,expires_at) VALUES (%s,%s,now()+interval '15 minutes')",
            (secrets.token_urlsafe(24), aid),
        )
    return redirect("/onboarding/done")
