const {test} = require('node:test');
const assert = require('node:assert/strict');
const {readFileSync} = require('node:fs');
const vm = require('node:vm');
const source = readFileSync(require('node:path').join(__dirname, 'Code.gs'), 'utf8');
const owner = 'suhasreddykotla222@gmail.com';
function entry(id='wl_user_new', overrides={}) {
  return {id, email:'synthetic@example.test', state:'pending', waitlist_id:'waitlist_test', created_at:new Date().toISOString(), ...overrides};
}
function harness(options={}) {
  const properties = {WORKOS_API_KEY:'TEST-KEY-NOT-REAL', WORKOS_WAITLIST_ID:'waitlist_test', OWNER_EMAIL:owner,
    GO_LIVE_AT:new Date(Date.now()-60000).toISOString(), SEND_ENABLED:'true', ...options.props};
  const sent = [], calls = [], triggers = [];
  let unlocks = 0;
  const context = {
    PropertiesService:{getScriptProperties:()=>({getProperty:key=>properties[key]??null,setProperty:(key,value)=>{properties[key]=value;}})},
    Session:{getEffectiveUser:()=>({getEmail:()=>options.sender||owner})},
    MailApp:{getRemainingDailyQuota:()=>options.quota??100,sendEmail:mail=>{if(options.failMail) throw Error('PRIVATE PROVIDER ERROR'); sent.push(mail);}},
    UrlFetchApp:{fetch:(url,config)=>{
      calls.push({url, config});
      assert.ok(url.startsWith('https://api.workos.com/user_management/waitlists'));
      assert.equal(config.method,'get');
      const body = url.endsWith('/waitlists') ? {data:[{id:'waitlist_test'}]} : {data:options.entries||[entry()],list_metadata:{after:null}};
      return {getResponseCode:()=>options.httpStatus||200,getContentText:()=>JSON.stringify(body)};
    }},
    LockService:{getScriptLock:()=>({tryLock:()=>options.lock!==false,releaseLock:()=>unlocks++})},
    ScriptApp:{getProjectTriggers:()=>triggers,newTrigger:handler=>({timeBased:()=>({everyMinutes:n=>({create:()=>{assert.equal(n,5); triggers.push({getHandlerFunction:()=>handler});}})})})},
  };
  vm.createContext(context); vm.runInContext(source,context);
  return {context,properties,sent,calls,triggers,unlocks:()=>unlocks};
}
test('new request receives one complete template; repeat polls do not resend',()=>{
  const h=harness(); h.context.pollWaitlist(); h.context.pollWaitlist();
  assert.equal(h.sent.length,1); assert.equal(h.sent[0].to,'synthetic@example.test');
  assert.equal(h.sent[0].replyTo,owner);
  for(const phrase of ['registration or license number','country of practice','country code','official professional registry','do not send passwords','does not automatically approve access']) assert.ok(h.sent[0].body.toLowerCase().includes(phrase.toLowerCase()));
  assert.equal(JSON.parse(h.properties.DELIVERY_wl_user_new).state,'sent');
  assert.equal(h.unlocks(),2);
});
test('pause and preview never send',()=>{
  const h=harness({props:{SEND_ENABLED:'false'}}); h.context.pollWaitlist();h.context.previewNewRequests();assert.equal(h.sent.length,0);
});
test('existing, approved, future and already processed requests are not emailed',()=>{
  const h=harness({entries:[entry('wl_user_old',{created_at:'2020-01-01T00:00:00Z'}),entry('wl_user_future',{created_at:'2099-01-01T00:00:00Z'})]});
  h.context.pollWaitlist(); assert.equal(h.sent.length,0);
  const invalid=harness({entries:[entry('wl_user_approved',{state:'approved'})]});
  assert.throws(()=>invalid.context.pollWaitlist(),/Unexpected waitlist entry/); assert.equal(invalid.sent.length,0);
});
test('zero quota defers mail',()=>{const h=harness({quota:0});h.context.pollWaitlist();assert.equal(h.sent.length,0);assert.equal(h.properties.DELIVERY_wl_user_new,undefined);});
test('send failure is held for owner review and never automatically retried',()=>{
  const h=harness({failMail:true}); assert.throws(()=>h.context.pollWaitlist(),/outcome uncertain/);
  assert.equal(JSON.parse(h.properties.DELIVERY_wl_user_new).state,'needs_review');
  h.context.pollWaitlist(); assert.equal(h.sent.length,0);
});
test('invalid recipient, mixed waitlist and provider failure fail closed',()=>{
  for(const options of [{entries:[entry('wl_user_bad',{email:'one@example.test,two@example.test'})]}, {entries:[entry('wl_user_bad',{waitlist_id:'waitlist_other'})]}, {httpStatus:401}]) {
    const h=harness(options);assert.throws(()=>h.context.pollWaitlist());assert.equal(h.sent.length,0);
  }
});
test('missing secret or wrong sender cannot send',()=>{
  for(const options of [{props:{WORKOS_API_KEY:''}},{sender:'other@example.test'}]){
    const h=harness(options); assert.throws(()=>h.context.pollWaitlist());assert.equal(h.sent.length,0);
  }
});
test('test message goes only to owner',()=>{
  const h=harness();h.context.sendTestToOwner();assert.equal(h.sent.length,1);assert.equal(h.sent[0].to,owner);assert.ok(h.sent[0].subject.startsWith('[TEST]'));
});
test('enabling twice creates only one five-minute trigger; pause keeps delivery records',()=>{
  const h=harness();h.context.enableAutomation();h.context.enableAutomation();assert.equal(h.triggers.length,1);
  h.context.pollWaitlist();h.context.pauseAutomation();assert.equal(h.properties.SEND_ENABLED,'false');assert.ok(h.properties.DELIVERY_wl_user_new);
});
test('concurrent run cannot send',()=>{const h=harness({lock:false});h.context.pollWaitlist();assert.equal(h.sent.length,0);assert.equal(h.calls.length,0);});
test('initialization is dry and preserves the activation boundary',()=>{
  const h=harness({props:{GO_LIVE_AT:null,SEND_ENABLED:null,WORKOS_WAITLIST_ID:null}});h.context.initializeAutomation();
  const start=h.properties.GO_LIVE_AT;h.context.initializeAutomation();assert.equal(h.properties.GO_LIVE_AT,start);assert.equal(h.properties.SEND_ENABLED,'false');assert.equal(h.sent.length,0);assert.equal(h.triggers.length,0);
});
test('batch respects quota and maximum ten recipients per run',()=>{
  const entries=Array.from({length:15},(_,i)=>entry('wl_user_'+i,{email:`synthetic${i}@example.test`}));
  for(const [quota,count] of [[100,10],[2,2]]){const h=harness({entries,quota});h.context.pollWaitlist();assert.equal(h.sent.length,count);}
});
