const code=document.querySelector('#code'), status=document.querySelector('#status');
chrome.storage.local.get('token').then(v=>{if(v.token)status.textContent='登録済み・自動接続 / Registered, reconnects automatically'});
document.querySelector('#start').onclick=async()=>{
  status.textContent='接続中…';
  try{const result=await chrome.runtime.sendMessage({kind:'start',code:code.value.trim()});status.textContent=result.error||'接続しました。スマホから操作できます。'}
  catch(e){status.textContent=e.message}
};

document.querySelector('#stop').onclick=async()=>{await chrome.runtime.sendMessage({kind:'stop'});status.textContent='切断しました / Disconnected'};
