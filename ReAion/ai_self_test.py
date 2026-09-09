#!/usr/bin/env python
from answer_engine import ai_status, generate_answer

st = ai_status()
print("Answer provider :", st.get("provider", "unknown"))
print("Provider ready  :", "PASS" if st.get("ready", st.get("running")) else "FAIL")
print("Detail          :", st.get("detail", ""))

if not st.get("ready", st.get("running")):
    raise SystemExit(2)

q = "How would you troubleshoot a server that suddenly lost network connectivity?"
answer, source = generate_answer(q)

print("Answer backend  :", source)
print("Test answer     :", answer)

if "fallback" in source:
    raise SystemExit(2)

print("AI SELF TEST: PASS")
