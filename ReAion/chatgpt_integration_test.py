#!/usr/bin/env python
import argparse

from chatgpt_windows import ChatGPTWindowsClient


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--submit", action="store_true",
        help="Actually submit one harmless test question to the focused ChatGPT Companion Window"
    )
    args = parser.parse_args()
    client = ChatGPTWindowsClient()
    status = client.status()
    print("ChatGPT Windows support:", "PASS" if status.supported else "SKIP")
    print("ChatGPT app readiness  :", "PASS" if status.ready else "FAIL")
    print("Detail                 :", status.detail)
    if not status.ready:
        return 2
    if args.submit:
        title = client.submit_question("How would you troubleshoot a server with no network connectivity?")
        print("Automatic submission   : PASS")
        print("Answer window           :", title)
    else:
        print("Automatic submission   : NOT RUN (add --submit)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

