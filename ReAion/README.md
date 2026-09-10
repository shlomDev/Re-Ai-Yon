# ReAion

ReAion is a live interview assistant that detects interview questions and shows suggested answers in a side panel while keeping the interview visible.

## What the tool does

- Detects interviewer questions automatically.
- Generates suggested answers without requiring an Ask button for every question.
- Shows large question and answer text in a side panel.
- Advances the teleprompter as you speak.
- Supports multilingual interviews, including Hebrew.
- Is designed for Google Meet, Microsoft Teams, Zoom, Webex, Amazon Chime and other interview platforms.

![ReAion demo](docs/images/ReAion-demo.gif)

## How to run it

### Windows

1. Double-click `Launch_ReAion.bat`.
2. Paste your interview link and click **Start Interview**.

On the first run, ReAion installs its dependencies automatically. It opens the interview in Chrome but stays armed and idle until the meeting UI confirms that you have actually joined the call. Only then does ReAion start listening and launch the answer panel.

### Quick mock test

```bash
python mock_interview.py --serve
```

Then open `http://127.0.0.1:8765` in your browser.
