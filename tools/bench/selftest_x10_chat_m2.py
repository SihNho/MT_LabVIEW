r"""selftest_x10_chat_m2 - card chat-M2 (gate-fp fp-35, user 2026-10-03 option (나)) self-test of stage_prerun X10's ONE
narrow release, x10_probe_release / PROBE-EXEMPT. OFFLINE, no LabVIEW, no COM. PRIOR ART: selftest_x10_c138_2.py (temp
scripts + synthetic dry traces fed to SP.x10_gate).
PREDICTION: P1 a declared probe (literal, looped read, warn-only meter called, work = claudeDev scratch copy discarded, no save)
-> ok True, why starts 'PROBE-EXEMPT'; P2 the same literal on a script that saves (source s.save() + dry 'Stage.save') -> FAIL,
why names the save; P3 NO literal, same looped-read edit script -> unchanged: FAIL UNMEASURED 'inside a loop'; P3b no literal,
read-only script -> unchanged PASS modelled run; P4 literal + meter stop_mb=700 -> FAIL; P5 literal + work == input VI -> FAIL;
P6 literal + work not discarded -> FAIL; P7 literal + an Executor -> FAIL; P8 wrong literal text -> FAIL.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_x10_chat_m2.log -- py -u tools/bench/selftest_x10_chat_m2.py"""
import os, sys, tempfile                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_prerun as SP, protocol as P                                             # noqa: E401,E402
res, tmp = [], []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


def script(text):
    fd, p = tempfile.mkstemp(prefix="x10probe_chat_m2_", suffix=".py")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(text)
    tmp.append(p)
    return p


CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
IN = os.path.join(CD, "bed.vi")
WK = os.path.join(CD, "scratch_probe_20261003_000000.vi")
MD5 = "49cf7f770fc331e06607687af640ad5e"
LIT = 'X10_PROBE = "memory ceiling, scratch only"\n'
HEAD = "import stagekit as K, stagexec as SX\nDRY = True\n"
BODY = ("M = SX.Meter(lambda: (None, None), stop_mb={stop})\n\n"
        "def body(s):\n    s.start(); s.discard_work()\n    M('load', 0)\n"
        "    for k in range(3):\n        s.census_snapshot()\n        M('read', k)\n    s.const_row({{}}, tag='e')\n{extra}")
MAIN = "\nif __name__ == '__main__':\n    K.run(body, K.Stage('a', 'b', 'c'))\n"
TR = {"executors": [], "ops": ["const_row"], "first_mutation": "Stage._op const_row", "input_md5": MD5, "input_vi": IN,
      "fails": [], "works": [WK], "discards": [WK], "saves": [], "x10_reads": ["Stage.census"]}


def probe(lit=LIT, stop="None", extra=""):
    return script(HEAD + lit + BODY.format(stop=stop, extra=extra) + MAIN)


ok, det = SP.x10_gate(probe(), [], trace=TR)
gate("P1 declared probe -> PROBE-EXEMPT pass", ok is True and det.get("why", "").startswith("PROBE-EXEMPT"), det.get("why"))
ok, det = SP.x10_gate(probe(extra="    s.save()\n"), [], trace=dict(TR, saves=["Stage.save"]))
gate("P2 same literal, script saves -> FAIL naming the save", ok is False and "NOT exempt" in det.get("why", "")
     and "save" in det["why"], det.get("why"))
NOLIT = probe(lit="")
ok, det = SP.x10_gate(NOLIT, [], trace=TR)
gate("P3 no literal, looped read -> unchanged FAIL UNMEASURED 'inside a loop'", ok is False and "UNMEASURED" in det.get("why", "")
     and "inside a loop" in det["why"] and "PROBE" not in det["why"], det.get("why"))
RO = script("import stagekit as K\n\ndef body(s):\n    s.start()\n    s.census_snapshot()\n" + MAIN)
ok, det = SP.x10_gate(RO, [], trace={"executors": [], "ops": [], "x10_reads": ["Stage.census"]})
gate("P3b no literal, read-only script -> unchanged modelled PASS (one run, no PROBE)", ok is True and len(det.get("runs") or []) == 1
     and "probe" not in det, det.get("runs"))
ok, det = SP.x10_gate(probe(stop="700"), [], trace=TR)
gate("P4 literal + meter stop_mb=700 -> FAIL (no warn-only meter)", ok is False and "warn-only meter" in det.get("why", ""),
     det.get("why"))
ok, det = SP.x10_gate(probe(), [], trace=dict(TR, works=[IN], discards=[IN]))
gate("P5 literal + work IS the input VI -> FAIL", ok is False and "IS the input VI" in det.get("why", ""), det.get("why"))
ok, det = SP.x10_gate(probe(), [], trace=dict(TR, discards=[]))
gate("P6 literal + work not discarded -> FAIL", ok is False and "discard_work" in det.get("why", ""), det.get("why"))
ok, det = SP.x10_gate(probe(), [{"plan": "x.json", "kinds": ["wire"]}], trace=dict(TR, executors=[{"plan": "x.json"}]))
gate("P7 literal + an Executor -> FAIL", ok is False and "Executor" in det.get("why", ""), det.get("why"))
ok, det = SP.x10_gate(probe(lit='X10_PROBE = "anything"\n'), [], trace=TR)
gate("P8 wrong literal text -> FAIL", ok is False and "literal" in det.get("why", ""), det.get("why"))
for p in tmp:
    try:
        os.remove(p)
    except OSError:
        pass
npass = sum(1 for _n, o in res if o)
print("=== SELFTEST x10 chat-M2: {0} pass / {1} fail".format(npass, len(res) - npass), flush=True)
first = next((n for n, o in res if not o), None)
print(P.result_line({"status": "PASS" if npass == len(res) else "FAIL", "gates": {"pass": npass, "fail": len(res) - npass},
                     "first_fail": first, "artefacts": []}), flush=True)
sys.exit(0 if npass == len(res) else 1)
