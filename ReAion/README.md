# ReAion

ReAion is a live interview assistant that detects interview questions and shows suggested answers in a side panel while keeping the interview visible.

## What the tool does

- Detects interviewer questions automatically.
- Generates suggested answers without requiring an Ask button for every question.
- Shows large question and answer text in a side panel.
- Advances the teleprompter as you speak.
- Supports multilingual interviews, including Hebrew.
- Is designed for Google Meet, Microsoft Teams, Zoom, Webex, Amazon Chime and other interview platforms.

![ReAion interface example](docs/images/answer-panel-example.png)

## How to run it

### Windows

1. Run `install.bat` once.
2. Run `start_auto_watcher.bat`.
3. Open your interview in Chrome.
4. Open the ReAion extension side panel.
5. Click **Use current meeting**.

### Quick mock test

```bash
python mock_interview.py --serve
```

Then open `http://127.0.0.1:8765` in your browser.
