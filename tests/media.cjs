const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('extension/worker.js','utf8')+'\nglobalThis.subject={execute,readVolume,setActive:id=>active=id};';
const media={volume:.3,muted:false,paused:true,currentTime:25,duration:60,play:async()=>{media.paused=false},pause:()=>{media.paused=true}};
const player={getVolume:()=>media.volume*100,setVolume:n=>{media.volume=n/100},isMuted:()=>media.muted,mute:()=>{media.muted=true},unMute:()=>{media.muted=false}};
const document={getElementById:()=>player,querySelector:()=>media};
const calls=[];
const chrome={alarms:{onAlarm:{addListener(){}},create(){}},debugger:{sendCommand:async(target,method,params)=>{calls.push(method);return params.expression?{result:{value:await vm.runInNewContext(params.expression,{document,Number,Math})}}:{}},onEvent:{addListener(){}},onDetach:{addListener(){}}},storage:{local:{get:async()=>({})}},runtime:{onMessage:{addListener(){}}}};
const context={chrome,WebSocket:{OPEN:1,CONNECTING:0},setTimeout,Date,Math,Number,Uint8Array,atob};
vm.runInNewContext(source,context);const subject=context.subject;subject.setActive(1);
(async()=>{
 await subject.execute({action:'volume',value:72});assert.equal(media.volume,.72);
 await subject.execute({action:'mute'});assert.equal(media.muted,true);
 await subject.execute({action:'playpause'});assert.equal(media.paused,false);
 await subject.execute({action:'seek',value:10});assert.equal(media.currentTime,35);
 await subject.execute({action:'quality',value:'off'});assert.equal(calls.at(-1),'Page.stopScreencast');
 console.log('Media control tests passed');
})().catch(e=>{console.error(e);process.exitCode=1});
