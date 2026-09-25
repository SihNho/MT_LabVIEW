"""Throwaway census (card 79-2): which subject fields do recent hypothesis reviews carry? Deleted after use."""
import glob, re, os
os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
Q = re.compile(r"^##\s+Question\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)
S = re.compile(r"tools[\\/](?:recipes|bench)[\\/]([\w.-]+)\.py", re.I)
for p in sorted(glob.glob("archive/peer/2026-09-2*.md")):
    b = open(p, encoding="utf-8", errors="replace").read()
    if "**role:** hypothesis" not in b and "**agent:** codex" not in b:
        continue
    m = Q.search(b)
    q = m.group(1) if m else ""
    hdr = re.findall(r"^\-\s*\*\*(?:task|slug|script|log):\*\*.*$", b, re.M)
    print(os.path.basename(p)[:55], "|", S.findall(q)[:4], "|", hdr[:2], "|",
          [x[:70] for x in re.findall(r"^\s*(?:Script|Log|Row|Stage|Card)\s*:.*$", q, re.M | re.I)[:2]])
print('RESULT {"schema":"result_line/1","status":"PASS"}')
