const base = 'http://127.0.0.1:8765';
const state = document.getElementById('state');
async function api(path, body) {
  const r = await fetch(base + path, {method: body ? 'POST' : 'GET',
    headers: {'Content-Type': 'application/json'}, body: body ? JSON.stringify(body) : undefined,
    signal: AbortSignal.timeout(4000)});
  if (!r.ok) throw new Error('Companion returned ' + r.status);
  return r.json();
}
async function refresh() {
  try {
    const d = await api('/panel-state');
    state.textContent = d.state;
    for (const [id,key] of [['question','question'],['answer','answer'],['page','progress'],['detail','detail']])
      document.getElementById(id).textContent = d[key] || '';
    document.getElementById('next').disabled = !d.answer;
  } catch(e) {
    state.textContent = 'COMPANION DISCONNECTED';
    document.getElementById('answer').textContent = '';
    document.getElementById('question').textContent = '';
    document.getElementById('detail').textContent = 'Launch ReAion on this computer. ' + e.message;
  } finally { setTimeout(refresh, 1000); }
}
document.getElementById('next').onclick = () => api('/panel-next', {}).catch(e => state.textContent = e.message);
document.getElementById('start').onclick = async () => {
  try {
    const [tab] = await chrome.tabs.query({active:true, currentWindow:true});
    await api('/select-meeting', {url:tab.url, title:tab.title || 'Interview'});
    await chrome.scripting.executeScript({target:{tabId:tab.id}, files:['content.js']});
    document.getElementById('detail').textContent = 'Meeting selected. Join normally; listening starts when call controls are detected.';
  } catch(e) { document.getElementById('detail').textContent = e.message; }
};
document.getElementById('stop').onclick = () => api('/stop', {}).catch(e => state.textContent = e.message);
refresh();
