# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-2.md
# ---
r"""prep_c163_a1_2_mk - card 163-a1-2 (OFFLINE, json only): re-make plan_ring_p5s02c.json as group I alone (A41..A52) on graph 431cfd83 with
START = stage_prerun.x10_start(f9ae7751) (the launch gate's start, memory_model start_rule), PD396(c). It RUNS prep_c163_a1_1_mk.py's flow (no copy of
its logic): the 163-a1-1 file is history and has no parameters, so its text is executed with seven literal one-line substitutions (each asserted to
occur exactly once): START -> x10_start called, card id, session file, the previous-plan copy name. The PD396(c) rule in that flow then picks I or I+J.
PREDICTION CONTRACT: KEEP I+J plan / in copied aside byte-equal (014c7d52 / caa0f639); every 163-a1-1 gate PASS; X10 at START 607.1 (function value):
  MAIN(I+J) 677.0 > 675, MAIN(I) 658.3 <= 675 -> PLAN-I chosen I, ids A41..A52; REALSIM final True, failed None, 12/12, 0 PROVISIONAL, 0 UNROUTABLE.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c163_a1_2_mk.log -- py -u tools/bench/prep_c163_a1_2_mk.py"""
import hashlib, json, os, shutil, sys                                                        # noqa: E401
B = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(B, "..", "..")); SRC = os.path.join(B, "prep_c163_a1_1_mk.py")  # noqa: E702
h = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                  # noqa: E731
KEEP = [(os.path.join(B, a), os.path.join(B, b), w) for a, b, w in (("plan_ring_p5s02c.json", "plan_ring_p5s02c_ij.json", "014c7d5277b100761a8a6f4abcca915e"),
                                                                     ("plan_ring_p5s02c_in.json", "plan_ring_p5s02c_ij_in.json", "caa0f639d8b5f074953f4015ed594fae"))]
for a, b, w in KEEP:                                                                         # step 1: keep I+J aside BEFORE anything is rebuilt
    if not os.path.isfile(b) and h(a) == w:
        shutil.copyfile(a, b)
    print("FACT KEEP {0} -> {1}: md5 {2} (pin {3})".format(os.path.basename(a), os.path.basename(b), h(b) if os.path.isfile(b) else None, w), flush=True)
KEPT = [(os.path.basename(b), os.path.isfile(b) and h(b) == w) for a, b, w in KEEP]
if not all(k for _, k in KEPT):
    print('RESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":0,"fail":1},"first_fail":"KEEP I+J copies","artefacts":[]}'); sys.exit(1)
PINS = dict((os.path.join(ROOT, i["path"]), i["md5"]) for i in json.load(open(os.path.join(B, "cards", "task_163-a1-2.json"), encoding="utf-8"))["inputs"]
            if not os.path.basename(i["path"]).startswith("plan_ring_p5s02c"))
M1 = dict((os.path.basename(p), h(p) == w) for p, w in PINS.items())
SUBS = [("601.2, 41, 52, 60", "SPR.x10_start(md5(VI2B))[0], 41, 52, 60"), ('CARD = "c163-a1-1"', 'CARD = "c163-a1-2"'),
        ('"prep_c163_a1_1_session.json"', '"prep_c163_a1_2_session.json"'), ('"plan_ring_p5s02c_prev.json"', '"plan_ring_p5s02c_ij.json"'),
        ('"card 163-a1-1 PROBE', '"card 163-a1-2 PROBE'), ("(card 163-a1-1, PD396(b)(c))", "(card 163-a1-2, PD396(c), START = x10_start)"),
        ('json.dump({"card": "163-a1-1",', 'json.dump({"card": "163-a1-2",'), ("sys.exit(gate.result())", "exec(EXTRA); sys.exit(gate.result())")]
EXTRA = """gate("M1 card 163-a1-2 input pins (other than the rebuilt plan files) == card: {0}".format(M1_), all(M1_.values()))
gate("KEEP I+J plan / in kept aside byte-equal {0}".format(KEPT_), all(k for _, k in KEPT_))
gate("PLAN-I chosen {0} = A{1}..A{2}; MAIN(I) {3} <= {4} at START {5} = stage_prerun.x10_start(f9ae7751) [{6}]; MAIN(I+J) at the same start {7}".format(
     CHOSEN, LO, HI, MAIN, LIMIT, START, XS[1], CAND["I+J"].get("main")), CHOSEN == "I" and HI == I_END and MAIN <= LIMIT and START == XS[0])"""
code = open(SRC, encoding="utf-8").read()
for o, n in SUBS:
    assert code.count(o) == 1, ("substitution must occur once", o, code.count(o))
    code = code.replace(o, n)
exec(compile(code, SRC, "exec"), {"__name__": "__main__", "__file__": SRC, "EXTRA": EXTRA, "M1_": M1, "KEPT_": KEPT})
