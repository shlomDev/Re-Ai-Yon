"""Deterministic interview rehearsal using the real pipeline and panel HTTP API.

No meeting join, audio recording, login or model call. --serve opens a browser
preview with synthetic Q&A so the actual panel and Next lines can be exercised.
"""
import argparse
import json
import os
import tempfile
import threading
import time
import webbrowser
from pathlib import Path
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen

QUESTION = 'A server has an IP address but cannot reach its gateway. Walk me through your checks.'
ANSWER = ('I would first establish whether this affects one server or the whole VLAN. '
          'I would check the link state, cable and switch port before changing configuration. '
          'Next I would verify the interface, IP address, subnet mask, route and VLAN assignment. '
          'On Linux I would use ip link, ip addr, ip route and ip neigh to inspect the current state. '
          'I would compare against a working server, make one controlled change, and verify gateway connectivity.')

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--serve', action='store_true')
    args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='copilot-mock-') as folder:
        os.environ['INTERVIEWCOPILOT_DATA_DIR']=folder
        from live_session import LiveSession
        from runtime_state import read_state, read_json
        from auto_meet_watch import Handler
        from app_paths import private_path
        class MockHandler(Handler):
            def do_GET(self):
                assets={'/':'sidepanel.html','/sidepanel.js':'sidepanel.js','/sidepanel.css':'sidepanel.css'}
                if self.path not in assets:return super().do_GET()
                asset=Path(__file__).parent/'chrome_extension'/assets[self.path]
                body=asset.read_text()
                if self.path=='/':
                    body=body.replace('<button id="start">Use current meeting</button>', '<button id="start" disabled>SIMULATED INTERVIEW</button>')
                body=body.encode()
                self.send_response(200)
                self.send_header('Content-Type','text/html' if self.path=='/' else 'text/javascript' if self.path.endswith('.js') else 'text/css')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers();self.wfile.write(body)
        calls=[]
        def answer(question):
            calls.append(question)
            return ANSWER, 'SIMULATED ANSWER — fixture, not a live AI response'
        session=LiveSession(answer)
        server=ThreadingHTTPServer(('127.0.0.1',8765 if args.serve else 0),MockHandler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        try:
            session.ingest({'speaker':'interviewer','text':QUESTION})
            url=f'http://127.0.0.1:{server.server_port}/panel-state'
            with urlopen(Request(url,headers={'Host':'127.0.0.1:8765'})) as r: state=json.load(r)
            assert state['question']==QUESTION and state['answer']
            first=state['answer']
            session.ingest({'speaker':'candidate','text':first})
            assert read_state()['answer'] != first and len(calls)==1
            session.ingest({'speaker':'interviewer','text':QUESTION})
            assert len(calls)==1
            print('PASS: interviewer question -> fixture answer -> actual HTTP panel -> microphone progress; no duplicate request')
            print('NOT TESTED: live audio, Whisper, ChatGPT login/submission, extension installation, operating-system installers')
            if args.serve:
                print('Preview: http://127.0.0.1:8765 — Ctrl+C to stop')
                webbrowser.open('http://127.0.0.1:8765')
                command_id=None
                while True:
                    command=read_json(private_path('panel_next.json'),{})
                    if command.get('id') != command_id:
                        command_id=command.get('id');session.advance()
                    session.emit();time.sleep(.25)
        except KeyboardInterrupt:pass
        finally:server.shutdown();server.server_close()
    return 0

if __name__=='__main__':raise SystemExit(main())
