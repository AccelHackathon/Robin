"""Opaque, revocable database sessions. Password hashes follow PRD section 9 (Argon2)."""

import asyncio
import hashlib
import secrets
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import HTTPException, Request
from psycopg.rows import dict_row
from app import db
from app.config import settings

COOKIE = "robin_session"
ANON_CSRF = "robin_form"
hasher = PasswordHasher()
DUMMY_HASH = hasher.hash(secrets.token_urlsafe(24))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def secure_cookie(request):
    return request.url.scheme == "https" or (settings.public_base_url or "").startswith(
        "https://"
    )


async def session(request: Request, required=True):
    if not db.pool:
        if required:
            raise HTTPException(
                503, "The service is temporarily unavailable. Please try again."
            )
        return None
    token = request.cookies.get(COOKIE, "")
    async with db.pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                """SELECT s.*,a.email FROM web_sessions s JOIN accounts a ON a.id=s.account_id
                WHERE s.token_hash=%s AND s.expires_at>now()""",
                (digest(token),),
            )
            result = await cur.fetchone()
    if not result and required:
        raise HTTPException(303, headers={"Location": "/login"})
    return result


async def new_session(response, request, account_id):
    token = secrets.token_urlsafe(32)
    csrf = secrets.token_urlsafe(32)
    async with db.pool.connection() as conn:
        await conn.execute(
            "INSERT INTO web_sessions(token_hash,account_id,csrf_token,expires_at) VALUES (%s,%s,%s,now()+interval '7 days')",
            (digest(token), account_id, csrf),
        )
    response.set_cookie(
        COOKIE,
        token,
        httponly=True,
        secure=secure_cookie(request),
        samesite="lax",
        max_age=604800,
        path="/",
    )
    return response


def check_csrf(request, form, expected):
    origin = request.headers.get("origin")
    allowed = {str(request.base_url).rstrip("/")}
    if settings.public_base_url:
        allowed.add(settings.public_base_url.rstrip("/"))
    if origin and origin.rstrip("/") not in allowed:
        raise HTTPException(403, "Please reload this page and try again.")
    value = str(form.get("csrf", ""))
    if not expected or not secrets.compare_digest(value, expected):
        raise HTTPException(403, "This form expired. Reload the page and try again.")


async def verify_password(stored, password):
    try:
        return await asyncio.to_thread(hasher.verify, stored, password)
    except (VerificationError, InvalidHashError):
        return False
