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
    const finished = d.state === 'INTERVIEW COMPLETE';
    document.getElementById('live-view').hidden = finished;
    document.getElementById('summary-view').hidden = !finished;
    if (finished && d.summary) {
      document.getElementById('questions-asked').textContent = d.summary.questions_asked || 0;
      document.getElementById('questions-answered').textContent = d.summary.questions_answered || 0;
      document.getElementById('weak-answers').textContent = d.summary.weak_answers || 0;
      document.getElementById('star-opportunities').textContent = d.summary.star_opportunities || 0;
      document.getElementById('confidence').textContent = (d.summary.confidence || 0) + '%';
    }
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
document.getElementById('generate-report').onclick = async () => {
  try { const d = await api('/generate-report', {}); document.getElementById('detail').textContent = d.message; }
  catch(e) { document.getElementById('detail').textContent = e.message; }
};
document.getElementById('export-pdf').onclick = () => window.print();
document.getElementById('practice').onclick = () => {
  document.getElementById('detail').textContent = 'Practice mode: start a new session to replay these questions.';
};
async function autoSelectCurrentMeeting() {
  try {
    const [tab] = await chrome.tabs.query({active:true, currentWindow:true});
    if (!tab?.url || !/^https:\/\/(?:[^/]*\.)?(?:meet\.google\.com|teams\.microsoft\.com|teams\.live\.com|zoom\.us|zoom\.com|webex\.com|app\.chime\.aws)\//i.test(tab.url)) return;
    await api('/select-meeting', {url:tab.url, title:tab.title || 'Interview'});
    await chrome.scripting.executeScript({target:{tabId:tab.id}, files:['content.js']});
    document.getElementById('detail').textContent = 'Meeting detected automatically. Join normally; listening starts when call controls are detected.';
    document.getElementById('meeting-url').value = tab.url.split('#')[0];
  } catch(e) { document.getElementById('detail').textContent = e.message; }
}

document.getElementById('open-link').onclick = async () => {
  const input = document.getElementById('meeting-url');
  const raw = input.value.trim();
  if (!validMeetingUrl(raw)) { document.getElementById('detail').textContent = 'Enter a supported HTTPS meeting link.'; input.focus(); return; }
  try {
    const [tab] = await chrome.tabs.query({active:true, currentWindow:true});
    if (!tab?.id) throw new Error('No active browser tab found.');
    await api('/select-meeting', {url:raw.split('#')[0], title:tab.title || 'Interview'});
    if (tab.url !== raw) await chrome.tabs.update(tab.id, {url:raw});
    document.getElementById('detail').textContent = 'Meeting opened. Join normally; listening starts after call controls are detected.';
  } catch (e) { document.getElementById('detail').textContent = e.message; }
};
document.getElementById('stop').onclick = () => api('/stop', {}).catch(e => state.textContent = e.message);
refresh();

autoSelectCurrentMeeting();
