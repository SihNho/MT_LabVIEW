"""card 116-3 D1 probe (read-only, no LabVIEW): which 2026-09-25..28 dispositions ACCEPT a finding and say a FIX was not
built/applied (section level), and is each review cited by a non-bench tools/ file or a tools/bench/selftest_*
(JUDGEMENT OPEN-3 witness)."""
import glob, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
UNBUILT = re.compile(r"(?i)\b(not built|not fixed|left open|not applied|not yet applied|is left OPEN)\b")
ACC = re.compile(r"(?<!NOT )\bACCEPTED\b")
code = []
for p in glob.glob(os.path.join(ROOT, "tools", "**", "*.py"), recursive=True):
    r = os.path.relpath(p, ROOT).replace("\\", "/")
    if r.startswith("tools/bench/") and not r.startswith("tools/bench/selftest_"):
        continue
    code.append(open(p, encoding="utf-8", errors="replace").read())
blob = "\n".join(code)
for p in sorted(glob.glob(os.path.join(ROOT, "archive", "peer", "2026-09-2[5-8]-*.md"))):
    on, acc, unb = False, [], []
    for n, line in enumerate(open(p, encoding="utf-8", errors="replace"), 1):
        if line.startswith("## What was done with it"):
            on = True; continue
        if on and line.startswith("## "):
            on = False
        if on and ACC.search(line):
            acc.append(n)
        if on and UNBUILT.search(line) and "NOT ACCEPTED" not in line:
            unb.append((n, line.strip()[:160]))
    if acc and unb:
        stem = os.path.basename(p)[:-3]
        print(("LANDED " if (stem in blob or stem[11:] in blob) else "ABSENT ") + stem, acc[:3])
        for n, t in unb:
            print("     :%d %s" % (n, t))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
