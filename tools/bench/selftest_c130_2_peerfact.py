r"""selftest_c130_2_peerfact - card 130-2 item 5, OFFLINE, no paid call: tools/peer.ps1 -ClassifyAnswerFile (the same
Test-ContentEmptyFactAnswer the live gemini fact arm applies before its exit code) on saved answer texts.
PREDICTION CONTRACT
  E1 the peer_c129_6_undo.log:6-24 gemini answer (artifact pointers, no URL) -> rc 4 (= fact chain FALLBACK, peer.ps1 rc 4)
  E2 a blank answer -> rc 4
  K1 a real answer with an ni.com URL -> rc 0 (no fallback)
  K2 a URL-bearing answer that also says "artifact" -> rc 0 (a URL keeps it)
  K3 a short plain answer with no URL and no artifact pointer -> rc 0 (not over-triggered)
  D1 -Kind fact -DryRun still prints the 2-step fact chain (dispatches nothing)
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c130_2_peerfact.log -- py -u tools/bench/selftest_c130_2_peerfact.py
"""
import os, subprocess, sys, tempfile                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                               # noqa: E402
PS = os.path.join(ROOT, "tools", "peer.ps1")
G = []


def gate(ok, label, detail=""):
    G.append((bool(ok), label)); print("GATE %-70s %s %s" % (label, "PASS" if ok else "FAIL", str(detail)[:200]), flush=True)


def classify(text):
    fd, p = tempfile.mkstemp(suffix=".txt", prefix="c130_2_ans_")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    cp = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS, "-ClassifyAnswerFile", p],
                        cwd=ROOT, capture_output=True, text=True, timeout=120, encoding="utf-8", errors="replace")
    os.remove(p)
    return cp.returncode, (cp.stdout + cp.stderr).strip()


lines = open(os.path.join(ROOT, "tools", "bench", "peer_c129_6_undo.log"), encoding="utf-8", errors="replace").read().splitlines()
undo = "\n".join(lines[5:24])
gate("walkthrough.md" in undo and "http" not in undo, "E0 peer_c129_6_undo.log:6-24 is the artifact-pointer answer", undo[:80])
for lab, txt, want in (("E1 c129-6 gemini answer -> rc 4 (fallback)", undo, 4),
                       ("E2 blank answer -> rc 4", "   \n", 4),
                       ("K1 answer with an ni.com URL -> rc 0", "VI:Transaction groups undo steps. Source: https://www.ni.com/docs/en-US/x", 0),
                       ("K2 URL + the word artifact -> rc 0", "See the artifact; source https://forums.ni.com/t5/x", 0),
                       ("K3 plain short answer, no URL, no artifact -> rc 0", "undoLimit is a LabVIEW.ini token; default 99.", 0)):
    rc, out = classify(txt)
    gate(rc == want, lab, "rc %s | %s" % (rc, out[:150]))
cp = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", PS, "-Kind", "fact", "-Slug", "c130-2-dry",
                     "-Task", "dry run only", "-DryRun"], cwd=ROOT, capture_output=True, text=True, timeout=180,
                    encoding="utf-8", errors="replace")
o = cp.stdout + cp.stderr
gate(cp.returncode == 0 and "FACT CHAIN STEP 1/2 (dry run)" in o and "FACT CHAIN STEP 2/2, fallback only (dry run)" in o,
     "D1 -Kind fact -DryRun prints the 2-step chain, rc 0", "rc %s" % cp.returncode)
n = sum(1 for ok, _l in G if ok)
print("=== GATES: %d pass / %d fail" % (n, len(G) - n))
print(P.result_line(P.make_result(n, len(G) - n, next((l for ok, l in G if not ok), None))), flush=True)
sys.exit(0 if n == len(G) else 1)
