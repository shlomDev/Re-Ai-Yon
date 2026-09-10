const HEALTH_URL = "http://127.0.0.1:8765/extension-health";
const SELECT_URL = "http://127.0.0.1:8765/select-meeting";
const MEETING_HOSTS = ["meet.google.com", "teams.microsoft.com", "teams.live.com", "zoom.us", "zoom.com", "webex.com", "app.chime.aws"];
function isMeetingUrl(raw) {
  try { const url = new URL(raw); return url.protocol === "https:" && MEETING_HOSTS.some(host => url.hostname === host || url.hostname.endsWith("." + host)); }
  catch (_) { return false; }
}
async function openInReAion(tabId, rawUrl, title) {
  if (!tabId || !isMeetingUrl(rawUrl)) return;
  try {
    const response = await fetch(SELECT_URL, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify({url:rawUrl.split("#")[0], title:title || "Interview"}), signal:AbortSignal.timeout(4000)});
    if (!response.ok) throw new Error("Companion returned " + response.status);
    await chrome.sidePanel.open({tabId});
  } catch (_) {}
}
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => chrome.contextMenus.create({id:"open-in-reaion", title:"Open meeting in ReAion", contexts:["link","page"]}));
});
chrome.contextMenus.onClicked.addListener((info, tab) => openInReAion(tab?.id, info.linkUrl || tab?.url || "", tab?.title));


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
