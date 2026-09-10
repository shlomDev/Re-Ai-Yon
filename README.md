# ReAion

ReAion is a live interview assistant that keeps the interview visible while showing the detected question and a suggested answer in a side panel.

## What the tool does

- Listens to the interview and detects interviewer questions.
- Generates suggested answers automatically.
- Shows the question and answer in a large, readable side panel.
- Advances the teleprompter as you speak, with manual **Next lines** control as a fallback.
- Supports multilingual interviews, including Hebrew.
- Is designed for Google Meet, Microsoft Teams, Zoom, Webex, Amazon Chime and other browser/desktop interview platforms.
- Can use your candidate profile, answer bank and interview guidance as context.
- Keeps the app open after the interview and shows questions asked, questions answered, weak answers, STAR opportunities and confidence.
- Detects supported meeting links automatically and offers **Open meeting in ReAion** from Chrome's context menu; no URL textbox is required.

<p align="center">
  <img src="docs/assets/ReAion_demo_fluent.gif" alt="ReAion Demo" width="100%">
</p>

## How to run it

### Windows

1. Double-click `ReAion/Launch_ReAion.bat`.
2. Open your interview link in Chrome.
3. Open the ReAion side panel, or right-click the meeting link and choose **Open meeting in ReAion**.

ReAion detects the meeting tab automatically and starts listening only after it detects that you have actually joined the call. It never clicks Join for you.

### Quick mock test

```bash
cd ReAion
python mock_interview.py --serve
```

Then open `http://127.0.0.1:8765` in your browser.