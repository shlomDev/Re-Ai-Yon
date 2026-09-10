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

![ReAion demo](ReAion_demo_fluent.gif)

## How to run it

### Windows

1. Double-click `ReAion/Launch_ReAion.bat`.
2. Paste your interview link and click **Start Interview**.

ReAion installs anything it needs on the first run, opens the interview in Chrome, and waits. It starts listening only after it detects that you have actually joined the call.

### Quick mock test

```bash
cd ReAion
python mock_interview.py --serve
```

Then open `http://127.0.0.1:8765` in your browser.