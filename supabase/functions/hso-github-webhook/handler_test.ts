import { createWebhookHandler, type WebhookDependencies } from "./handler.ts";

const secret="test-webhook-secret-value-32-bytes-minimum";
const token="a-separate-reconciliation-token-value";
const now=1_795_632_000_000;
const id="run-9-attempt-1-pull_request-abcd1234";
const body='{"action":"synchronize","number":9,"repository":{"full_name":"owner/repo","html_url":"https://github.com/owner/repo"},"pull_request":{"number":9,"title":"test","html_url":"https://github.com/owner/repo/pull/9","head":{"sha":"abc"},"base":{"ref":"main"}}}';
function eq(a:unknown,b:unknown){if(JSON.stringify(a)!==JSON.stringify(b))throw new Error("expected "+JSON.stringify(b)+" got "+JSON.stringify(a));}
async function sign(ts:string,delivery:string,raw:string,keyText=secret){
 const key=await crypto.subtle.importKey("raw",new TextEncoder().encode(keyText),{name:"HMAC",hash:"SHA-256"},false,["sign"]);
 const result=await crypto.subtle.sign("HMAC",key,new TextEncoder().encode(ts+"."+delivery+"."+raw));
 return Array.from(new Uint8Array(result),b=>b.toString(16).padStart(2,"0")).join("");
}
function fake(overrides:Partial<WebhookDependencies>={}){
 const state={inbox:[] as unknown[],changes:[] as unknown[],touches:[] as string[],sync:[] as string[],updates:[] as string[]};
 const deps:WebhookDependencies={
  getSigningSecret:()=>secret,getSyncToken:()=>token,now:()=>now,
  async persistIntegrationEvent(row){if(state.inbox.length)return {duplicate:true};state.inbox.push(row);return {id:"event-1",duplicate:false};},
  async persistChangeEvent(row){state.changes.push(row);},
  async touchSource(at){state.touches.push(at);},
  async triggerReconciliation(delivery){state.sync.push(delivery);return {runId:"run-1",status:"partial",githubStatus:"connected"};},
  async linkSyncRun(){},
  async updateIntegrationEvent(_id,status){state.updates.push(status);},
  ...overrides,
 };
 return {deps,state};
}
async function req(ts=String(Math.floor(now/1000)),delivery=id,extra:Record<string,string>={}){
 return new Request("https://example.test/hook",{method:"POST",headers:{
  "content-type":"application/json","x-hso-timestamp":ts,"x-hso-delivery":delivery,"x-hso-event":"pull_request",
  "x-hso-signature":"sha256="+await sign(ts,delivery,body),...extra,
 },body});
}

Deno.test("valid signed event persists rows and correlates reconciliation",async()=>{
 const {deps,state}=fake();const res=await createWebhookHandler(deps)(await req());const data=await res.json();
 eq(res.status,202);eq(data.sync_successful,true);eq(state.inbox.length,1);eq(state.changes.length,1);
 eq(state.touches.length,1);eq(state.sync,[id]);eq(state.updates,["processed"]);
});
Deno.test("invalid HMAC rejected before writes",async()=>{
 const {deps,state}=fake();const r=await req();r.headers.set("x-hso-signature","sha256="+"0".repeat(64));
 eq((await createWebhookHandler(deps)(r)).status,401);eq(state.inbox.length,0);eq(state.sync.length,0);
});
Deno.test("missing and expired timestamps rejected",async()=>{
 const {deps,state}=fake();
 const missing=new Request("https://example.test/hook",{method:"POST",headers:{"content-type":"application/json","x-hso-delivery":id,"x-hso-signature":"x"},body});
 eq((await createWebhookHandler(deps)(missing)).status,401);
 eq((await createWebhookHandler(deps)(await req(String(Math.floor(now/1000)-600)))).status,401);
 eq(state.inbox.length,0);
});
Deno.test("delivery ID and exact payload are signature-bound",async()=>{
 const {deps,state}=fake();const ts=String(Math.floor(now/1000));const sig=await sign(ts,id,body);
 const altered=new Request("https://example.test/hook",{method:"POST",headers:{"content-type":"application/json","x-hso-timestamp":ts,"x-hso-delivery":id+"-other","x-hso-event":"pull_request","x-hso-signature":"sha256="+sig},body});
 eq((await createWebhookHandler(deps)(altered)).status,401);eq(state.inbox.length,0);
});
Deno.test("duplicate delivery returns 409 and never repeats side effects",async()=>{
 const {deps,state}=fake();const h=createWebhookHandler(deps);eq((await h(await req())).status,202);eq((await h(await req())).status,409);
 eq(state.inbox.length,1);eq(state.changes.length,1);eq(state.touches.length,1);eq(state.sync.length,1);
});
Deno.test("missing reconciliation token fails closed before persistence",async()=>{
 const {deps,state}=fake({getSyncToken:()=>undefined});
 eq((await createWebhookHandler(deps)(await req())).status,503);
 eq(state.inbox.length,0);eq(state.changes.length,0);eq(state.sync.length,0);
});

Deno.test("legacy raw-body GitHub signature is rejected",async()=>{
 const {deps,state}=fake();const key=await crypto.subtle.importKey("raw",new TextEncoder().encode("legacy-secret"),{name:"HMAC",hash:"SHA-256"},false,["sign"]);
 const raw=await crypto.subtle.sign("HMAC",key,new TextEncoder().encode(body));
 const oldSig=Array.from(new Uint8Array(raw),b=>b.toString(16).padStart(2,"0")).join("");
 const r=new Request("https://example.test/hook",{method:"POST",headers:{"content-type":"application/json","x-hso-timestamp":String(Math.floor(now/1000)),"x-hso-delivery":id,"x-hso-event":"pull_request","x-hub-signature-256":"sha256="+oldSig,"x-github-delivery":id},body});
 eq((await createWebhookHandler(deps)(r)).status,401);eq(state.inbox.length,0);eq(state.sync.length,0);
});
