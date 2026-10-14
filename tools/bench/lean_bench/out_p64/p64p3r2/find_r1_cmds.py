# read-only: print the p64_* command lines that the retry-1 session (session_p64p3_fail2.log) ran through Bash
import json, os, re, sys                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
LOG = os.path.join(HERE, "..", "..", "session_p64p3_fail2.log")
seen = []
for ln in open(LOG, encoding="utf-8", errors="replace"):
    for m in re.finditer(r'"command":\s*"((?:[^"\\]|\\.)*)"', ln):
        c = json.loads('"%s"' % m.group(1))
        if re.search(r"p64_(own|abba|leg|sum|beadmap)\.py", c) and c not in seen:
            seen.append(c)
for c in seen:
    print("----\n" + c)
