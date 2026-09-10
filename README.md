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

![ReAion interface example](ReAion/docs/images/answer-panel-example.jpg)

## How to run it

### Windows

1. Open the `ReAion` folder.
2. Run `install.bat` once.
3. Run `start_auto_watcher.bat`.
4. Open your interview in Chrome.
5. Open the ReAion extension side panel and select **Use current meeting**.

### Quick mock test

```bash
cd ReAion
python mock_interview.py --serve
```

Then open `http://127.0.0.1:8765` in your browser.
