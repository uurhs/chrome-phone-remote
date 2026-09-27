let quality='balanced';
const BASE='http://127.0.0.1:8765';
let token='', needsInitialAttach=true, active=null, polling=false, lastError='', video=null, volumeState=null, lastVolumeRead=0;
async function api(path, body){
  const response=await fetch(BASE+path,{method:'POST',headers:{'Content-Type':'application/json','X-Remote-Token':token},body:JSON.stringify(body)});
  if(response.status===403){token='';if(video)video.close();video=null;await chrome.storage.local.remove('token');if(active!==null){try{await chrome.debugger.detach({tabId:active})}catch(e){}active=null}}
  if(!response.ok)throw Error((await response.json()).error||`HTTP ${response.status}`);
  return response.json();
}
async function cmd(method, params={}){
  if(active===null)throw Error('No tab selected');
  return chrome.debugger.sendCommand({tabId:active},method,params);
}
async function attach(tabId){
  if(active===tabId){await restartCapture();return;}
  if(active!==null){try{await chrome.debugger.detach({tabId:active})}catch(e){}active=null}
  await chrome.debugger.attach({tabId},'1.3');
  active=tabId;volumeState=null;lastVolumeRead=0;
  await chrome.storage.local.set({lastTabId:tabId});
  await cmd('Page.enable');
  await restartCapture();
  await api('/bridge/selected',{id:tabId});
}
async function restartCapture(){
  if(active===null)return;
  try{await cmd('Page.stopScreencast')}catch(e){}
  if(quality==='off')return;
  const settings={low:[40,800,600],balanced:[55,1100,800],high:[80,1600,1200]}[quality];
  await cmd('Page.startScreencast',{format:'jpeg',quality:settings[0],maxWidth:settings[1],maxHeight:settings[2],everyNthFrame:1});
}
function connectVideo(){
  if(!token||video&&[WebSocket.OPEN,WebSocket.CONNECTING].includes(video.readyState))return;
  video=new WebSocket('ws://127.0.0.1:8765/ws/bridge?token='+encodeURIComponent(token));
  video.onopen=()=>restartCapture().catch(e=>{lastError=e.message});
  video.onclose=()=>{if(active!==null)cmd('Page.stopScreencast').catch(()=>{});setTimeout(connectVideo,1500)};
}
chrome.debugger.onEvent.addListener((source,method,params)=>{
  if(source.tabId!==active||method!=='Page.screencastFrame')return;
  cmd('Page.screencastFrameAck',{sessionId:params.sessionId}).catch(()=>{});
  if(!video||video.readyState!==WebSocket.OPEN||video.bufferedAmount>500000)return;
  const m=params.metadata||{};
  video.send(JSON.stringify({type:'dimensions',id:active,width:(m.deviceWidth||1280)/(m.deviceScaleFactor||1),height:(m.deviceHeight||800)/(m.deviceScaleFactor||1)}));
  const binary=Uint8Array.from(atob(params.data),c=>c.charCodeAt(0));
  video.send(binary);
});
chrome.debugger.onDetach.addListener(source=>{if(source.tabId===active){active=null;volumeState=null;lastError='タブ接続が解除されました / Select the tab again'}});
const READ_VOLUME=`(()=>{const p=document.getElementById('movie_player'),v=document.querySelector('video');if(!v)return {available:false};return {available:true,paused:v.paused,value:Math.round(typeof p?.getVolume==='function'?p.getVolume():v.volume*100),muted:typeof p?.isMuted==='function'?p.isMuted():v.muted}})()`;
async function readVolume(){
  if(active===null)return {available:false};
  const result=await cmd('Runtime.evaluate',{expression:READ_VOLUME,returnByValue:true});
  return result.result?.value||{available:false};
}
async function changeVolume(action,value){
  const amount=Math.max(0,Math.min(100,Number(value)||0));
  const expression=action==='volume'
    ?`(()=>{const p=document.getElementById('movie_player'),v=document.querySelector('video');if(!v)return false;if(typeof p?.setVolume==='function'){p.setVolume(${amount});if(typeof p.isMuted==='function'&&p.isMuted())p.unMute()}else{v.volume=${amount}/100;v.muted=false}return true})()`
    :`(()=>{const p=document.getElementById('movie_player'),v=document.querySelector('video');if(!v)return false;if(typeof p?.isMuted==='function'){p.isMuted()?p.unMute():p.mute()}else v.muted=!v.muted;return true})()`;
  const result=await cmd('Runtime.evaluate',{expression,returnByValue:true});
  if(!result.result?.value)throw Error('このタブに動画がありません');
  volumeState=await readVolume();lastVolumeRead=Date.now();
}
async function execute(message){
  const {action,id,x,y,dy,value}=message;
  if(action==='quality'){quality=value;await restartCapture();return}
  if(action==='playpause'||action==='seek'){
    const delta=Math.max(-30,Math.min(30,Number(value)||0));
    const expression=action==='playpause'
      ?`(async()=>{const v=document.querySelector('video');if(!v)return false;if(v.paused)await v.play();else v.pause();return true})()`
      :`(()=>{const v=document.querySelector('video');if(!v)return false;const max=Number.isFinite(v.duration)?v.duration:Infinity;v.currentTime=Math.max(0,Math.min(max,v.currentTime+${delta}));return true})()`;
    const result=await cmd('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true,userGesture:true});
    if(result.exceptionDetails||!result.result?.value)throw Error('動画を操作できません / Video unavailable');
    lastVolumeRead=0;return;
  }
  if(action==='volume'||action==='mute'){await changeVolume(action,value);return}
  if(action==='select'){
    await attach(id);
    // Activate the tab within Chrome without focusing its window.
    await chrome.tabs.update(id,{active:true});
    return;
  }
  if(action==='new'){
    const tab=await chrome.tabs.create({url:'about:blank',active:false});
    await attach(tab.id);return;
  }
  if(action==='navigate'){
    await chrome.tabs.update(active,{url:value});return;
  }
  if(action==='reload'){await chrome.tabs.reload(active);return}
  if(action==='back'||action==='forward'){
    const history=await cmd('Page.getNavigationHistory');
    const index=history.currentIndex+(action==='back'?-1:1);
    if(index>=0&&index<history.entries.length)await cmd('Page.navigateToHistoryEntry',{entryId:history.entries[index].id});
    return;
  }
  if(action==='click'){
    await cmd('Input.dispatchMouseEvent',{type:'mousePressed',x,y,button:'left',clickCount:1});
    await cmd('Input.dispatchMouseEvent',{type:'mouseReleased',x,y,button:'left',clickCount:1});return;
  }
  if(action==='scroll'){
    await cmd('Input.dispatchMouseEvent',{type:'mouseWheel',x,y,deltaX:0,deltaY:dy});return;
  }
  if(action==='type'){await cmd('Input.insertText',{text:value});return}
  if(action==='enter'){
    await cmd('Input.dispatchKeyEvent',{type:'keyDown',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});
    await cmd('Input.dispatchKeyEvent',{type:'keyUp',key:'Enter',code:'Enter',windowsVirtualKeyCode:13});return;
  }
  throw Error('Unknown action');
}
async function poll(){
  if(polling)return;polling=true;
  while(token){
    try{
      const tabs=(await chrome.tabs.query({})).filter(t=>(/^(https?:|about:blank)/.test(t.url||''))).map(t=>({id:t.id,title:t.title,url:t.url}));
      if(Date.now()-lastVolumeRead>900){lastVolumeRead=Date.now();try{volumeState=await readVolume()}catch(e){volumeState={available:false}}}
      const result=await api('/bridge/poll',{tabs,selected:active,error:lastError,volume:volumeState});
      if(!token)break;
      if(needsInitialAttach&&active===null){
        needsInitialAttach=false;
        const stored=await chrome.storage.local.get('lastTabId');
        const candidates=await chrome.tabs.query({});
        const allowed=t=>/^https?:/.test(t.url||'');
        const target=candidates.find(t=>t.id===stored.lastTabId&&allowed(t))||candidates.find(t=>t.active&&allowed(t))||candidates.find(allowed);
        if(target){try{await attach(target.id)}catch(e){lastError=e.message}}
      }
      if(result.action){try{await execute(result);lastError=''}catch(e){lastError=e.message}}
      await new Promise(resolve=>setTimeout(resolve,100));
    }catch(e){lastError=e.message;await new Promise(resolve=>setTimeout(resolve,1500))}
  }
  polling=false;
}
async function resume(){
  if(!token){const saved=await chrome.storage.local.get('token');token=saved.token||'';}
  if(token){connectVideo();poll();}
}
chrome.runtime.onMessage.addListener((message,sender,sendResponse)=>{
  if(message.kind==='stop'){
    (async()=>{
      if(token){try{await api('/bridge/forget',{})}catch(e){}}
      token='';if(video)video.close();video=null;
      if(active!==null){try{await chrome.debugger.detach({tabId:active})}catch(e){}}
      active=null;await chrome.storage.local.remove(['token','code','lastTabId']);sendResponse({ok:true});
    })().catch(e=>sendResponse({error:e.message}));return true;
  }
  if(message.kind!=='start')return;
  (async()=>{
    const entered=String(message.code||'').trim();
    if(entered){
      const response=await fetch(BASE+'/bridge/pair',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({code:entered})});
      const result=await response.json();if(!response.ok)throw Error(result.error||'Pairing failed');
      token=result.token;await chrome.storage.local.set({token});await chrome.storage.local.remove('code');
    }else{const saved=await chrome.storage.local.get('token');token=saved.token||'';if(!token)throw Error('初回は6桁コードを入力 / Enter the code for first pairing');}
    await api('/bridge/poll',{tabs:[],selected:active});
    needsInitialAttach=true;connectVideo();poll();sendResponse({ok:true});
  })().catch(e=>sendResponse({error:e.message}));return true;
});
chrome.alarms.onAlarm.addListener(alarm=>{if(alarm.name==='remote-reconnect')resume()});
chrome.alarms.create('remote-reconnect',{periodInMinutes:1});
resume();
