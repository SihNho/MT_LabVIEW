# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_165-1-1.json
# ---
"""Card 165-1-1: keep the PRE-CHANGE stagexec / stagesim bytes for the before/after compile comparison (read-only on the
repo; writes only under %TEMP%\\c165_a1_1\\). Also the git HEAD versions, so the facts file can say which one is 'before'.

Prediction contract: tools/stagexec.py md5 a4df7e15..., tools/stagesim.py 95a162ba..., tools/stagekit.py dd57c1ca... (the
card's pins); the copies hash equal to the sources; HEAD md5s printed (equal or not - a fact)."""
import hashlib
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

OUT = os.path.join(tempfile.gettempdir(), "c165_a1_1")
os.makedirs(OUT, exist_ok=True)
PIN = {"stagexec": "a4df7e15", "stagesim": "95a162ba", "stagekit": "dd57c1ca"}
G = [0, 0, None]


def md5b(b):
    return hashlib.md5(b).hexdigest()


def gate(lab, ok, d=""):
    G[0 if ok else 1] += 1
    if not ok and G[2] is None:
        G[2] = lab
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, d), flush=True)


for m in ("stagexec", "stagesim", "stagekit"):
    b = open(os.path.join(ROOT, "tools", m + ".py"), "rb").read()
    gate("PIN {0} {1}".format(m, PIN[m]), md5b(b).startswith(PIN[m]), md5b(b))
    if m == "stagekit":
        continue
    dst = os.path.join(OUT, m + "_pre.txt")
    if not os.path.isfile(dst):                       # never overwrite: the first copy is the pre-change one
        open(dst, "wb").write(b)
    gate("COPY {0} == source".format(dst), md5b(open(dst, "rb").read()) == md5b(b), md5b(open(dst, "rb").read()))
    h = subprocess.run(["git", "show", "HEAD:tools/{0}.py".format(m)], cwd=ROOT, capture_output=True).stdout
    open(os.path.join(OUT, m + "_head.txt"), "wb").write(h)
    print("FACT HEAD tools/{0}.py md5 {1} ({2} bytes); working copy {3}".format(m, md5b(h), len(h), md5b(b)), flush=True)
print(protocol.result_line(protocol.make_result(G[0], G[1], G[2], [])), flush=True)
sys.exit(1 if G[1] else 0)
