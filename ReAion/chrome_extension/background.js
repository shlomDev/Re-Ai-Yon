const HEALTH_URL = "http://127.0.0.1:8765/extension-health";

chrome.sidePanel?.setPanelBehavior({openPanelOnActionClick: true}).catch(() => {});

async function health() {
  try {
    await fetch(HEALTH_URL, {
      method: "POST",
      mode: "cors",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({version: chrome.runtime.getManifest().version, ts: Date.now()})
    });
  } catch (_) {}
}

chrome.runtime.onInstalled.addListener(() => {
  chrome.alarms.create("health", {periodInMinutes: 1});
  health();
});

chrome.runtime.onStartup.addListener(() => {
  chrome.alarms.create("health", {periodInMinutes: 1});
  health();
});

chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "health") health();
});

chrome.alarms.create("health", {periodInMinutes: 1});
health();

// Relay from meeting pages through the extension, keeping localhost access off
// arbitrary web-page origins. Only accept heartbeat messages from our scripts.
chrome.runtime.onMessage.addListener((message, sender, respond) => {
  if (message.type !== 'meeting-heartbeat' || !sender.tab) return;
  fetch('http://127.0.0.1:8765/heartbeat', {
    method:'POST', headers:{'Content-Type':'application/json'},
    body:JSON.stringify({...message.payload, url:sender.url}),
    signal:AbortSignal.timeout(4000)
  }).then(r=>r.json()).then(respond).catch(()=>respond({armed:false}));
  return true;
});
