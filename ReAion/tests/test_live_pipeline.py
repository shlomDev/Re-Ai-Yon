import json
import os
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from live_session import LiveSession, JsonlReader
from runtime_state import publish, read_state
from teleprompter import chunk_answer
from meetings.base import MeetingContext, detect_provider

class LiveTests(unittest.TestCase):
    def test_question_answer_mic_progress_and_duplicate(self):
        answer = 'Check the cable and link. ' * 12
        engine = Mock(return_value=(answer, 'mock fixture'))
        states = []
        session = LiveSession(engine, states.append)
        question = {'speaker':'interviewer', 'text':'A server cannot reach its gateway. What would you check?'}
        session.ingest(question)
        self.assertEqual(states[-1]['state'], 'ANSWER READY')
        self.assertEqual(states[-1]['question'], question['text'])
        self.assertLessEqual(len(states[-1]['answer'].split()), 28)
        session.ingest({'speaker':'candidate','text':session.prompter.current()})
        self.assertEqual(session.prompter.index, 1)
        session.ingest(question)
        self.assertEqual(engine.call_count, 1)

    def test_candidate_question_never_generates_answer(self):
        engine = Mock()
        session = LiveSession(engine, lambda _:None)
        session.ingest({'speaker':'candidate','text':'How would you troubleshoot DHCP?'})
        session.flush()
        engine.assert_not_called()

    def test_external_delivery_is_not_an_answer(self):
        states=[]
        session=LiveSession(lambda _:('Read ChatGPT window','ChatGPT browser'),states.append)
        session.answer('Explain DHCP.')
        self.assertEqual(states[-1]['state'],'SENT TO AI WINDOW')
        self.assertEqual(states[-1]['answer'],'')

    def test_error_clears_previous_answer(self):
        states=[]
        engine=Mock(side_effect=[('first answer','mock'),RuntimeError('offline')])
        session=LiveSession(engine,states.append)
        session.answer('First question')
        session.answer('Second question')
        self.assertEqual(states[-1]['state'],'ANSWER ERROR')
        self.assertEqual(states[-1]['answer'],'')

    def test_long_sentence_is_bounded(self):
        self.assertTrue(all(len(c.split())<=28 for c in chunk_answer('word '*150)))

    def test_incremental_feed_does_not_replay_or_lose_partial_line(self):
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'feed.jsonl'
            path.write_bytes(b'{"text":"one"}\n{"text":')
            reader=JsonlReader(path)
            self.assertEqual(reader.read(),[{'text':'one'}])
            self.assertEqual(reader.read(),[])
            with path.open('ab') as f:f.write(b'"two"}\n')
            self.assertEqual(reader.read(),[{'text':'two'}])

    def test_chrome_does_not_override_teams(self):
        self.assertEqual(detect_provider(MeetingContext(url='https://teams.microsoft.com/l/meetup',process_name='chrome.exe')),'teams')
        self.assertEqual(detect_provider(MeetingContext(process_name='chrome.exe')),'generic')

    def test_bom_config(self):
        import auto_meet_watch as watcher
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'interviews.json'
            path.write_text(json.dumps({'interviews':[{'id':'fixture'}]}),encoding='utf-8-sig')
            with patch.object(watcher,'CONFIG_FILE',path):
                self.assertEqual(watcher.load_config(),[{'id':'fixture'}])

    def test_health_fails_when_selected_provider_unavailable(self):
        import health_check
        with patch('answer_engine.ai_status',return_value={'ready':False,'fallback_ready':True}):
            self.assertFalse(health_check.health()['ok'])

    def test_browser_reuse_on_owner_thread(self):
        import answer_engine
        from chatgpt_browser import ChatGPTBrowserClient
        answer_engine.close_answer_engine()
        with patch.dict(answer_engine.SETTINGS['answer_engine'],provider='chatgpt_browser'), patch.object(ChatGPTBrowserClient,'submit_question',return_value='ChatGPT') as send, patch('chatgpt_browser.ChatGPTBrowserClient',wraps=ChatGPTBrowserClient) as constructor:
            answer_engine.generate_answer('First question?')
            answer_engine.generate_answer('Second question?')
            self.assertEqual(constructor.call_count,1)
            self.assertEqual(send.call_count,2)
        answer_engine.close_answer_engine()

    def test_browser_rejects_untrusted_destination(self):
        from chatgpt_browser import ChatGPTBrowserClient
        for url in ('http://chatgpt.com','https://chatgpt.com.evil.example','https://user@chatgpt.com'):
            with self.assertRaises(ValueError):ChatGPTBrowserClient(url=url)

    def test_private_data_never_falls_back_to_project(self):
        import runtime_data
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,INTERVIEWCOPILOT_DATA_DIR=folder):
            self.assertEqual(runtime_data.text('candidate_profile.md','missing'),'missing')

    def test_http_panel_real_state_and_origin_rejection(self):
        import auto_meet_watch as watcher
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ,INTERVIEWCOPILOT_DATA_DIR=folder):
            server=ThreadingHTTPServer(('127.0.0.1',0),watcher.Handler)
            thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
            url=f'http://127.0.0.1:{server.server_port}'
            try:
                publish({'state':'ANSWER READY','question':'Fixture question','answer':'Fixture answer'})
                req=Request(url+'/panel-state',headers={'Host':'127.0.0.1:8765','Origin':'chrome-extension://fixture'})
                with urlopen(req) as r:self.assertEqual(json.load(r)['answer'],'Fixture answer')
                bad=Request(url+'/panel-state',headers={'Host':'127.0.0.1:8765','Origin':'https://untrusted.example'})
                with self.assertRaises(HTTPError) as err:urlopen(bad)
                self.assertEqual(err.exception.code,403)
            finally:server.shutdown();server.server_close();thread.join()

if __name__=='__main__':unittest.main()
