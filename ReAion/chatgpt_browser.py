"""Experimental visible UI automation, never private APIs or credential extraction.

A successful send only means the prompt appeared as a user message. The answer
stays in ChatGPT; this adapter does not expose an answer-extraction interface.
"""
from dataclasses import dataclass
from urllib.parse import urlparse
from app_paths import private_path
from chatgpt_windows import build_interview_prompt

@dataclass
class BrowserStatus:
    supported: bool
    ready: bool
    detail: str
    url: str = ''

class ChatGPTBrowserClient:
    def __init__(self, url='https://chatgpt.com/', user_data_dir=None, headless=False):
        self.validate_url(url)
        self.url = url
        self.user_data_dir = user_data_dir or str(private_path('chatgpt_browser_profile'))
        self.headless = headless
        self._context = self._page = self._pw = None
        self._uncertain = False

    @staticmethod
    def validate_url(url):
        parsed = urlparse(url)
        if (parsed.scheme != 'https' or parsed.hostname != 'chatgpt.com' or
                parsed.username or parsed.password or parsed.port not in (None, 443)):
            raise ValueError('ChatGPT URL must use https://chatgpt.com/')

    def status(self):
        try: import playwright.sync_api  # noqa: F401
        except ImportError:
            return BrowserStatus(False, False, 'Playwright is missing; browser connection unavailable')
        if self._page is None:
            return BrowserStatus(True, False, 'Browser login and composer have not been verified', self.url)
        try:
            self.validate_url(self._page.url)
            ready = not self._uncertain and self._page.locator('#prompt-textarea').is_visible()
            return BrowserStatus(True, ready, 'Composer visible; live submission still requires testing' if ready else
                                 'ChatGPT is unavailable or the last send was not confirmed', self._page.url)
        except Exception:
            return BrowserStatus(True, False, 'Browser closed or page unavailable', self.url)

    def _ensure_page(self):
        if self._page and not self._page.is_closed(): return self._page
        self.close()
        from playwright.sync_api import sync_playwright
        self._pw = sync_playwright().start()
        try:
            self._context = self._pw.chromium.launch_persistent_context(self.user_data_dir, headless=self.headless)
            self._page = self._context.pages[0] if self._context.pages else self._context.new_page()
            self._page.goto(self.url, wait_until='domcontentloaded')
            return self._page
        except Exception:
            self.close()
            raise

    def submit_question(self, question):
        if not question.strip(): raise ValueError('Question is empty')
        if self._uncertain: raise RuntimeError('Previous send unconfirmed. Check ChatGPT before restarting the session.')
        page = self._ensure_page()
        self.validate_url(page.url)
        composer = page.locator('#prompt-textarea')
        composer.wait_for(state='visible', timeout=15000)
        # Never overwrite a draft the user has typed in this conversation.
        draft = composer.evaluate('(el) => el.value ?? el.innerText')
        if draft.strip(): raise RuntimeError('ChatGPT contains an unsent draft; send or clear it first')
        if page.locator('[data-testid="stop-button"]').count():
            raise RuntimeError('ChatGPT is still answering the previous question')
        prompt = build_interview_prompt(question)
        composer.fill(prompt)
        self.validate_url(page.url)
        self._uncertain = True
        composer.press('Enter')
        # No blind retry: Enter can succeed even if the UI acknowledgement times out.
        page.locator('[data-message-author-role="user"]').filter(has_text=prompt).last.wait_for(state='visible', timeout=15000)
        self._uncertain = False
        return page.title() or 'ChatGPT'

    def close(self):
        try:
            if self._context: self._context.close()
        finally:
            if self._pw: self._pw.stop()
            self._context = self._page = self._pw = None
