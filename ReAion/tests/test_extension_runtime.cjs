// Execute the actual content script in a minimal DOM fixture, without Chrome.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync('chrome_extension/content.js','utf8');
async function scenario(inCall, armed) {
  let clicks=0, timers=[], messages=[];
  const mic={getAttribute:k=>k==='aria-label'?'Turn on microphone':'',textContent:'',getClientRects:()=>[{}],click:()=>clicks++};
  const leave={getAttribute:k=>k==='aria-label'?'Leave call':'',textContent:'',getClientRects:()=>[{}]};
  const context={window:{},location:{pathname:'/test-call',href:'https://teams.microsoft.com/test-call'},
    document:{querySelectorAll:()=>inCall?[mic,leave]:[mic],getElementById:()=>null},
    chrome:{runtime:{sendMessage:async m=>{messages.push(m);return {armed};}}},
    setTimeout:fn=>timers.push(fn),console};
  vm.runInNewContext(source,context);
  await new Promise(resolve=>setImmediate(resolve));
  await timers.shift()();
  assert.equal(clicks,inCall&&armed?1:0);
  assert.equal(messages[0].payload.in_call,inCall);
}
(async()=>{
  await scenario(false,true);
  await scenario(true,false);
  await scenario(true,true);
  console.log('PASS: extension does not touch pre-join/unselected microphone; enables it once in selected active call');
})().catch(e=>{console.error(e);process.exitCode=1;});
