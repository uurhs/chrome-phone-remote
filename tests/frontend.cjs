const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const elements=new Map();
function element(id){if(!elements.has(id))elements.set(id,{style:{},value:'',textContent:'',disabled:false,replacements:0,clientWidth:400,clientHeight:300,naturalWidth:800,naturalHeight:600,replaceChildren(){this.replacements++},add(){},removeAttribute(){},getBoundingClientRect(){return{left:0,top:0,width:400,height:300}},setPointerCapture(){}});return elements.get(id)}
const document={querySelector:element,getElementById:id=>element('#'+id),querySelectorAll:()=>[],activeElement:null};
let next=0;const timers=new Map(),intervals=new Map();
let response={authenticated:false};let responseStatus=200;
class Socket{static OPEN=1;static CONNECTING=0;constructor(){this.readyState=1}close(){this.readyState=3}}
const context={document,window:{addEventListener(){}},location:{protocol:'http:',host:'localhost'},WebSocket:Socket,Option:function(t,v){this.value=v},URL:{revokeObjectURL(){},createObjectURL(){return'blob:test'}},fetch:async()=>({ok:responseStatus===200,status:responseStatus,json:async()=>response}),setTimeout:f=>{timers.set(++next,f);return next},clearTimeout:id=>timers.delete(id),setInterval:f=>{intervals.set(++next,f);return next},clearInterval:id=>intervals.delete(id),console};
vm.runInNewContext(fs.readFileSync('static/remote.js','utf8')+`\nglobalThis.subject={showRemote,showPairing,loadTabs,api,drag:()=>{volumeDragging=true;finishVolume();return volumeReleaseTimer},dragging:()=>volumeDragging};`,context);
(async()=>{
 await new Promise(setImmediate);
 response={tabs:[{id:1,title:'YouTube',url:'https://youtube.com'}],selected:1,connected:true,volume:{available:true,value:50}};
 context.subject.showRemote();context.subject.showRemote();await new Promise(setImmediate);
 assert.equal(intervals.size,1,'one status loop');
 const box=element('#tabs'),replaced=box.replacements;
 await context.subject.loadTabs();assert.equal(box.replacements,replaced,'unchanged list remains stable');
 document.activeElement=box;response={...response,tabs:[...response.tabs,{id:2,title:'New'}]};await context.subject.loadTabs();assert.equal(box.replacements,replaced,'focused list is not replaced');
 const release=context.subject.drag();timers.get(release)();assert.equal(context.subject.dragging(),false);
 await new Promise(setImmediate);responseStatus=403;response={error:'expired'};
 await assert.rejects(()=>context.subject.api('/api/tabs'));
 assert.equal(intervals.size,0);assert.equal(element('#pair').style.display,'block');
 console.log('Frontend recovery checks passed');
})().catch(e=>{console.error(e);process.exitCode=1});
