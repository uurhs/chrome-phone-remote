
const image=document.querySelector('#screen'),status=document.querySelector('#status');
async function api(path,data){const r=await fetch(path,{method:data?'POST':'GET',headers:data?{'Content-Type':'application/json'}:{},body:data?JSON.stringify(data):undefined});const v=await r.json();if(!r.ok){if(r.status===403&&path!=='/api/pair')showPairing();throw Error(v.error||r.status)}return v}
let remoteStarted=false, refreshTimer=null, reconnectTimer=null, tabSignature='';
function showPairing(){
  remoteStarted=false;
  clearInterval(refreshTimer);refreshTimer=null;
  clearTimeout(reconnectTimer);reconnectTimer=null;
  if(video){video.onclose=null;video.close();video=null}
  if(previousURL){URL.revokeObjectURL(previousURL);previousURL=null}
  image.removeAttribute('src');
  document.querySelector('#remote').style.display='none';
  document.querySelector('#pair').style.display='block';
  document.querySelector('#pairError').textContent='PCに表示された最新のコードで接続してください / Enter the current PC code';
}

const fail=e=>status.textContent='エラー: '+e.message;
let volumeDragging=false, volumeTimer=null, pendingVolume=null;
const volumeSlider=document.querySelector('#volume'),volumeValue=document.querySelector('#volumeValue'),muteButton=document.querySelector('#mute');
function showVolume(v){
  volumeSlider.disabled=!v?.available;muteButton.disabled=!v?.available;for(const id of ['playPause','seekBack','seekForward','volumeDown','volumeUp'])document.getElementById(id).disabled=!v?.available;
  if(!v?.available){volumeValue.textContent='--%';muteButton.textContent='🔇';return}
  if(!volumeDragging){volumeSlider.value=v.value;volumeValue.textContent=v.value+'%'}
  muteButton.textContent=v.muted?'🔇':'🔊';document.querySelector('#playPause').textContent=v.paused?'▶':'Ⅱ';
}
let loadingTabs=false;
async function loadTabs(){
  if(loadingTabs)return;loadingTabs=true;
  try{
    const v=await api('/api/tabs'),box=document.querySelector('#tabs');
    const signature=JSON.stringify(v.tabs.map(t=>[t.id,t.title,t.url]));
    if(document.activeElement!==box){
      if(signature!==tabSignature){box.replaceChildren();for(const t of v.tabs)box.add(new Option((t.title||t.url||'タブ').slice(0,65),t.id));tabSignature=signature}
      box.value=v.selected;
    }
    showVolume(v.connected?v.volume:null);
    status.textContent=v.connected?(v.error||'画面をタップして操作できます'):'拡張機能の接続を待っています';
  }catch(e){fail(e)}finally{loadingTabs=false}
}
function showRemote(){
  document.querySelector('#pair').style.display='none';document.querySelector('#remote').style.display='block';
  if(remoteStarted)return;
  remoteStarted=true;connectVideo();loadTabs();refreshTimer=setInterval(loadTabs,1500);
}
document.querySelector('#pairButton').onclick=async()=>{try{await api('/api/pair',{code:document.querySelector('#code').value.trim()});showRemote()}catch(e){document.querySelector('#pairError').textContent=e.message}};
api('/api/session').then(v=>{if(v.authenticated)showRemote()}).catch(()=>{});
let video, previousURL=null;
function connectVideo(){
  if(!remoteStarted)return;
  if(video&&[WebSocket.OPEN,WebSocket.CONNECTING].includes(video.readyState))return;
  video=new WebSocket((location.protocol==='https:'?'wss://':'ws://')+location.host+'/ws/phone');
  video.binaryType='blob';
  video.onmessage=e=>{const next=URL.createObjectURL(e.data),old=previousURL;if(old)setTimeout(()=>URL.revokeObjectURL(old),2000);image.onload=updateStage;image.src=next;previousURL=next};
  video.onclose=()=>{video=null;if(remoteStarted)reconnectTimer=setTimeout(connectVideo,1500)};
}
document.querySelector('#refreshTabs').onclick=loadTabs;
document.querySelector('#tabs').onchange=async e=>{try{await api('/api/action',{action:'select',id:Number(e.target.value)})}catch(err){fail(err)}};
async function action(name,extra={}){try{await api('/api/action',{action:name,...extra})}catch(e){fail(e)}}
document.querySelectorAll('[data-action]').forEach(b=>b.onclick=()=>action(b.dataset.action));
document.querySelector('#go').onclick=()=>action('navigate',{value:document.querySelector('#url').value});
document.querySelector('#url').onkeydown=e=>{if(e.key==='Enter')document.querySelector('#go').click()};
document.querySelector('#type').onclick=()=>{action('type',{value:document.querySelector('#text').value});document.querySelector('#text').value=''};
document.querySelector('#enter').onclick=()=>action('enter');
muteButton.onclick=()=>action('mute');
volumeSlider.onpointerdown=()=>volumeDragging=true;
volumeSlider.oninput=()=>{
  volumeDragging=true;pendingVolume=Number(volumeSlider.value);volumeValue.textContent=pendingVolume+'%';
  if(!volumeTimer)volumeTimer=setTimeout(sendVolume,80);
};
function sendVolume(){volumeTimer=null;if(pendingVolume===null)return;const value=pendingVolume;pendingVolume=null;action('volume',{value});if(pendingVolume!==null)volumeTimer=setTimeout(sendVolume,80)}
let volumeReleaseTimer=null;
function finishVolume(){
  if(volumeTimer)clearTimeout(volumeTimer);sendVolume();
  clearTimeout(volumeReleaseTimer);
  volumeReleaseTimer=setTimeout(()=>{volumeDragging=false;loadTabs()},350);
}
volumeSlider.onchange=finishVolume;
volumeSlider.onpointerup=finishVolume;
volumeSlider.onpointercancel=finishVolume;
volumeSlider.onblur=finishVolume;

const stage=document.querySelector('#stage'), zoomLabel=document.querySelector('#zoomReset'), modeButton=document.querySelector('#mode');
let zoom=1, panX=0, panY=0, mode='scroll', ratio=0, gesture=null, pinch=null;
const pointers=new Map();
function updateStage(){
  if(!image.naturalWidth||!image.naturalHeight)return;
  const next=image.naturalHeight/image.naturalWidth;
  if(Math.abs(next-ratio)>0.005){ratio=next;stage.style.height=Math.round(stage.clientWidth*ratio)+'px'}
  positionImage();
}
function positionImage(){
  const width=stage.clientWidth*zoom,height=stage.clientHeight*zoom;
  panX=Math.max(stage.clientWidth-width,Math.min(0,panX));
  panY=Math.max(stage.clientHeight-height,Math.min(0,panY));
  image.style.width=width+'px';image.style.left=panX+'px';image.style.top=panY+'px';
  zoomLabel.textContent=Math.round(zoom*100)+'%';
}
function setMode(next){mode=next;modeButton.textContent='操作: '+(mode==='pan'?'画面移動':'スクロール')}
function zoomAt(next,clientX,clientY){
  const stageRect=stage.getBoundingClientRect(),old=zoom;
  zoom=Math.max(1,Math.min(4,next));
  const x=clientX-stageRect.left,y=clientY-stageRect.top;
  panX=x-(x-panX)*(zoom/old);panY=y-(y-panY)*(zoom/old);
  positionImage();
  if(zoom>1)setMode('pan');else setMode('scroll');
}
document.querySelector('#zoomIn').onclick=()=>zoomAt(zoom*1.5,stage.getBoundingClientRect().left+stage.clientWidth/2,stage.getBoundingClientRect().top+stage.clientHeight/2);
document.querySelector('#zoomOut').onclick=()=>zoomAt(zoom/1.5,stage.getBoundingClientRect().left+stage.clientWidth/2,stage.getBoundingClientRect().top+stage.clientHeight/2);
zoomLabel.onclick=()=>{zoom=1;panX=panY=0;positionImage();setMode('scroll')};
modeButton.onclick=()=>setMode(mode==='pan'?'scroll':'pan');
window.addEventListener('resize',()=>{ratio=0;updateStage()});
function xy(e){const r=image.getBoundingClientRect();return{x:Math.max(0,Math.min(1,(e.clientX-r.left)/r.width)),y:Math.max(0,Math.min(1,(e.clientY-r.top)/r.height))}}
let scrollDelta=0,scrollPoint=null,scrollTimer=null;
function flushScroll(){
  scrollTimer=null;
  if(Math.abs(scrollDelta)<0.5)return;
  const delta=Math.max(-800,Math.min(800,scrollDelta));scrollDelta-=delta;
  action('scroll',{...scrollPoint,dy:delta});
  if(Math.abs(scrollDelta)>=0.5)scrollTimer=setTimeout(flushScroll,32);
}
function queueScroll(delta,e){scrollDelta+=delta;scrollPoint=xy(e);if(!scrollTimer)scrollTimer=setTimeout(flushScroll,32)}
function distance(){const [a,b]=[...pointers.values()];return Math.hypot(a.x-b.x,a.y-b.y)}
function center(){const [a,b]=[...pointers.values()];return{x:(a.x+b.x)/2,y:(a.y+b.y)/2}}
stage.onpointerdown=e=>{
  e.preventDefault();stage.setPointerCapture(e.pointerId);
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pointers.size===1){gesture={id:e.pointerId,lastX:e.clientX,lastY:e.clientY,startX:e.clientX,startY:e.clientY,moved:false};pinch=null}
  if(pointers.size===2){pinch={distance:Math.max(1,distance()),zoom};if(gesture)gesture.moved=true}
};
stage.onpointermove=e=>{
  if(!pointers.has(e.pointerId))return;e.preventDefault();
  pointers.set(e.pointerId,{x:e.clientX,y:e.clientY});
  if(pointers.size>=2){if(pinch){const c=center();zoomAt(pinch.zoom*distance()/pinch.distance,c.x,c.y)}return}
  if(!gesture||gesture.id!==e.pointerId)return;
  const dx=e.clientX-gesture.lastX,dy=e.clientY-gesture.lastY;
  if(Math.hypot(e.clientX-gesture.startX,e.clientY-gesture.startY)>6)gesture.moved=true;
  if(gesture.moved){
    if(mode==='pan'){panX+=dx;panY+=dy;positionImage()}
    else queueScroll(-dy*(image.naturalHeight||stage.clientHeight)/image.getBoundingClientRect().height,e)
  }
  gesture.lastX=e.clientX;gesture.lastY=e.clientY;
};
function finishPointer(e){
  if(!pointers.has(e.pointerId))return;e.preventDefault();
  if(e.type!=='pointercancel'&&pointers.size===1&&gesture&&gesture.id===e.pointerId&&!gesture.moved)action('click',xy(e));
  pointers.delete(e.pointerId);
  if(!pointers.size){gesture=null;pinch=null;if(scrollTimer){clearTimeout(scrollTimer);flushScroll()}}
  else {gesture=null;pinch=null}
}
stage.onpointerup=finishPointer;stage.onpointercancel=finishPointer;

document.querySelector('#playPause').onclick=()=>action('playpause');
document.querySelector('#seekBack').onclick=()=>action('seek',{value:-10});
document.querySelector('#seekForward').onclick=()=>action('seek',{value:10});
function adjustVolume(delta){if(volumeSlider.disabled)return;const value=Math.max(0,Math.min(100,Number(volumeSlider.value)+delta));volumeSlider.value=value;volumeValue.textContent=value+'%';action('volume',{value})}
document.querySelector('#volumeDown').onclick=()=>adjustVolume(-5);
document.querySelector('#volumeUp').onclick=()=>adjustVolume(5);
document.querySelector('#quality').onchange=e=>{const value=e.target.value;stage.style.display=value==='off'?'none':'block';if(value!=='off'){ratio=0;updateStage()}action('quality',{value})};
document.querySelector('#reconnect').onclick=async()=>{const id=Number(document.querySelector('#tabs').value);if(id)await action('select',{id});loadTabs()};
