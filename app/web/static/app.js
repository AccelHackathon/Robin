// Progressive enhancement. Navigation and saving remain server-rendered.
const flow = document.querySelector('.flow');
if (flow && !location.pathname.match(/^\/(login|signup)$/)) {
  requestAnimationFrame(() => window.scrollTo({top: Math.max(0, flow.getBoundingClientRect().top + scrollY - 24)}));
}
function wireDrop(zone, input, callback) {
  if (!zone || !input) return;
  input.addEventListener('change', () => callback(input.files));
  zone.addEventListener('dragover', e => { e.preventDefault(); zone.classList.add('dragging'); });
  zone.addEventListener('dragleave', () => zone.classList.remove('dragging'));
  zone.addEventListener('drop', e => {e.preventDefault();zone.classList.remove('dragging');input.files=e.dataTransfer.files;callback(input.files);});
}
function pendingDB() {
  return new Promise((resolve,reject)=>{const request=indexedDB.open('robin-pending-policy',1);request.onupgradeneeded=()=>request.result.createObjectStore('files');request.onsuccess=()=>resolve(request.result);request.onerror=()=>reject(request.error);});
}
const landing=document.querySelector('#landing-files');
wireDrop(document.querySelector('#landing-drop'),landing,async files=>{
  const status=document.querySelector('#landing-status');
  const chosen=Array.from(files);
  if(chosen.some(f=>f.size>20*1024*1024)||chosen.length>20){status.textContent='Choose up to 20 files, each 20 MB or smaller.';return;}
  try {const db=await pendingDB();const tx=db.transaction('files','readwrite');const store=tx.objectStore('files');store.clear();store.put({files:chosen,at:Date.now()},'selection');tx.oncomplete=()=>db.close();status.textContent=`${chosen.length} document(s) selected. Create or sign in to your account to save them.`;}
  catch{status.textContent='Please continue to your account, then select your documents there.';}
});
const documentInput=document.querySelector('#document-files');
wireDrop(document.querySelector('#upload-drop'),documentInput,files=>{document.querySelector('#file-status').textContent=`${files.length} file(s) selected. Choose Save documents to upload.`;});
if(documentInput){(async()=>{try{const db=await pendingDB();const request=db.transaction('files').objectStore('files').get('selection');request.onsuccess=()=>{const saved=request.result;if(saved && Date.now()-saved.at<3600000){const dt=new DataTransfer();saved.files.forEach(f=>dt.items.add(f));documentInput.files=dt.files;document.querySelector('#file-status').textContent=`${saved.files.length} file(s) from the home page are ready to save.`;}db.close();};}catch{}})();}
const uploadForm=document.querySelector('#upload-form');
if(uploadForm)uploadForm.addEventListener('submit',()=>{const button=document.querySelector('#upload-button');button.textContent='Saving…';button.disabled=true;});
// Clear the temporary local selection only after the server shows the matching files as saved.
if(documentInput && document.querySelector('.file-list')){(async()=>{try{const db=await pendingDB();const req=db.transaction('files').objectStore('files').get('selection');req.onsuccess=()=>{const saved=req.result;const names=Array.from(document.querySelectorAll('.file-name a')).map(x=>x.textContent);if(saved && saved.files.every(f=>names.includes(f.name))){const tx=db.transaction('files','readwrite');tx.objectStore('files').clear();tx.oncomplete=()=>db.close();}else db.close();};}catch{}})();}
const coverageList=document.querySelector('#coverage-list');
const statusLabel={pending:'Your documents are waiting to be read.',processing:'Your agent is reading your documents.',partial:'Your documents are saved. Some details still need confirmation.',complete:'Your document analysis is ready.',failed:'Analysis could not finish. Your documents are safe; you can retry.'};
function text(tag,value,cls){const element=document.createElement(tag);element.textContent=value;if(cls)element.className=cls;return element;}
async function refreshProfile(){
  try{
    const response=await fetch('/onboarding/profile.json',{headers:{Accept:'application/json'}});
    if(response.status===401||response.redirected){document.querySelector('#analysis-status').textContent='Sign in again to view your policy.';return;}
    if(!response.ok)throw new Error('unavailable');
    const data=await response.json();
    document.querySelector('#analysis-status').textContent=statusLabel[data.status]||'Checking your documents…';
    document.querySelector('#telegram-status').textContent=data.telegram_linked ? (data.welcome_status==='failed'?'Telegram connected. The welcome message could not be sent.':'Telegram connected.'):'Telegram is not connected yet.';
    const connect=document.querySelector('.connect');
    if(connect && (data.link_expired||data.telegram_linked)){connect.hidden=true;}
    if(data.link_expired&&!data.telegram_linked)document.querySelector('#telegram-status').textContent='Your Telegram link has expired. Get a new link below.';
    document.querySelector('#retry-form').hidden=!['failed','partial'].includes(data.status);
    const tasks=document.querySelector('#missing-tasks');tasks.replaceChildren(...data.tasks.map(x=>text('li',x)));
    const opened=new Set(Array.from(coverageList.querySelectorAll('details[open]')).map(x=>x.dataset.guarantee));
    coverageList.replaceChildren(...data.guarantees.sort((a,b)=>(a.subscribed==='unknown')-(b.subscribed==='unknown')).map(f=>{
      const row=text('details','','coverage-row');row.dataset.guarantee=f.guarantee;row.open=opened.has(f.guarantee);
      const summary=text('summary','');summary.append(text('strong',f.label));
      summary.append(text('span',{'yes':'Selected','no':'Not selected','unknown':'To confirm'}[f.subscribed],'coverage-state'));row.append(summary);
      if(f.ceiling)row.append(text('p',`Contract limit: ${Number(f.ceiling.amount).toLocaleString('en-GB')} ${f.ceiling.unit}`));
      if(f.deductible_detail)row.append(text('p',`Deductible: ${f.deductible_detail.amount} ${f.deductible_detail.unit}`));
      if(f.quote)row.append(text('blockquote',f.quote));
      const link=text('a',`Read source · page ${f.page}`);link.href=`/clauses/${f.source_clause_id}`;row.append(link);
      if(f.confidence==='low')row.append(text('p','Candidate clause — needs confirmation.','hint'));
      return row;
    }));
    if(!['pending','processing'].includes(data.status) && (data.telegram_linked || !document.querySelector('.connect:not([hidden])')))return;
  }catch{document.querySelector('#analysis-status').textContent='Unable to refresh right now. Your saved setup is unchanged.';}
  setTimeout(refreshProfile,5000);
}
if(coverageList)refreshProfile();
