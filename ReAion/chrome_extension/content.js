(() => {
  "use strict";
  if (window.__interviewCopilotLoaded) return;
  window.__interviewCopilotLoaded = true;
  let micHandled = false;

  const HEARTBEAT_URL = "http://127.0.0.1:8765/heartbeat";
  let cameraPromptShownForUrl = false;

  function meetCode() {
    const m = location.pathname.match(/^\/([a-z]{3}-[a-z]{4}-[a-z]{3})(?:\/|$)/i);
    return m ? m[1].toLowerCase() : null;
  }

  function labelOf(el) {
    return [
      el.getAttribute("aria-label") || "",
      el.getAttribute("data-tooltip") || "",
      el.getAttribute("data-tooltip-id") || "",
      el.textContent || ""
    ].join(" ").replace(/\s+/g, " ").trim();
  }

  function controls() {
    return Array.from(document.querySelectorAll(
      'button[aria-label], [role="button"][aria-label], button[data-tooltip], [role="button"][data-tooltip]'
    ));
  }

  const leavePatterns = [
    /leave call/i, /leave meeting/i, /end call/i, /hang up/i, /exit call/i,
    /עזיבת השיחה/i, /יציאה מהשיחה/i, /ניתוק השיחה/i
  ];

  const micMutedPatterns = [
    /turn on microphone/i, /unmute microphone/i, /^unmute\b/i,
    /microphone.*off/i, /הפעל.*מיקרופון/i, /בטל.*השתקה.*מיקרופון/i
  ];

  const micOnPatterns = [
    /turn off microphone/i, /mute microphone/i, /^mute\b/i,
    /microphone.*on/i, /כבה.*מיקרופון/i, /השתק.*מיקרופון/i
  ];

  const cameraOffPatterns = [
    /turn on camera/i, /turn on video/i, /camera.*off/i, /video.*off/i,
    /הפעל.*מצלמה/i, /הפעל.*וידאו/i
  ];

  const cameraOnPatterns = [
    /turn off camera/i, /turn off video/i, /camera.*on/i, /video.*on/i,
    /כבה.*מצלמה/i, /כבה.*וידאו/i
  ];

  function findControl(patterns) {
    for (const el of controls()) {
      if (!el.getClientRects().length || el.disabled) continue;
      const text = labelOf(el);
      if (patterns.some(re => re.test(text))) return el;
    }
    return null;
  }

  function looksLikeInCall() {
    for (const el of controls()) {
      if (!el.getClientRects().length || el.disabled) continue;
      const text = labelOf(el);
      if (leavePatterns.some(re => re.test(text))) return true;
    }
    return false;
  }

  function ensureMicrophoneOn() {
    const mutedButton = findControl(micMutedPatterns);
    if (mutedButton) {
      try {
        mutedButton.click();
        console.log("[Interview Transcriber] Microphone auto-enabled.");
      } catch (_) {}
      return;
    }
    if (findControl(micOnPatterns)) return;
  }

  function createCameraPrompt(cameraButton) {
    if (cameraPromptShownForUrl || document.getElementById("giauto-camera-prompt")) return;
    cameraPromptShownForUrl = true;

    const box = document.createElement("div");
    box.id = "giauto-camera-prompt";
    Object.assign(box.style, {
      position: "fixed",
      right: "24px",
      bottom: "96px",
      zIndex: "2147483647",
      width: "310px",
      padding: "16px",
      borderRadius: "12px",
      background: "#202124",
      color: "white",
      fontFamily: "Arial, sans-serif",
      fontSize: "14px",
      boxShadow: "0 8px 30px rgba(0,0,0,.45)"
    });

    const title = document.createElement("div");
    title.textContent = "Turn camera on?";
    Object.assign(title.style, {
      fontSize: "17px",
      fontWeight: "600",
      marginBottom: "8px"
    });

    const text = document.createElement("div");
    text.textContent = "Microphone is handled automatically. Camera stays off unless you approve.";
    Object.assign(text.style, {
      opacity: "0.9",
      lineHeight: "1.4",
      marginBottom: "14px"
    });

    const row = document.createElement("div");
    Object.assign(row.style, {
      display: "flex",
      gap: "8px",
      justifyContent: "flex-end"
    });

    function mkButton(label, primary) {
      const b = document.createElement("button");
      b.textContent = label;
      Object.assign(b.style, {
        border: primary ? "none" : "1px solid #5f6368",
        background: primary ? "#8ab4f8" : "transparent",
        color: primary ? "#202124" : "white",
        borderRadius: "18px",
        padding: "8px 16px",
        cursor: "pointer",
        fontWeight: "600"
      });
      return b;
    }

    const no = mkButton("Keep camera off", false);
    const yes = mkButton("Turn camera on", true);

    no.addEventListener("click", () => box.remove());
    yes.addEventListener("click", () => {
      try { const current = findControl(cameraOffPatterns); if (current) current.click(); } finally { box.remove(); }
    });

    row.append(no, yes);
    box.append(title, text, row);
    document.documentElement.appendChild(box);
  }

  function handleCamera() {
    const cameraOff = findControl(cameraOffPatterns);
    if (cameraOff) {
      createCameraPrompt(cameraOff);
      return;
    }
    if (findControl(cameraOnPatterns)) cameraPromptShownForUrl = true;
  }

  async function tick() {
    try {
      const inCall = looksLikeInCall();
      const response = await chrome.runtime.sendMessage({type:'meeting-heartbeat', payload:{
        meet_code: meetCode() || '', in_call:inCall, url:location.href
      }});
      if (response?.armed && inCall) {
        if (!micHandled) { ensureMicrophoneOn(); micHandled = true; }
        handleCamera();
      } else if (!inCall) {
        micHandled = false;
        cameraPromptShownForUrl = false;
        document.getElementById('giauto-camera-prompt')?.remove();
      }
    } catch (_) {}
    setTimeout(tick, 1500);
  }
  tick();
})();
