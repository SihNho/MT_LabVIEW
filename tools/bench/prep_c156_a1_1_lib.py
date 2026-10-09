# ---
# labview: none
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/brief_156-a1-1.md
# ---
r"""prep_c156_a1_1_lib - card 156-a1-1 (OFFLINE, json only): the plan-maker blocks that the cycle-155 makers hold as inline copies, ONCE, so the
four card-156 makers (prep_c156_a1_1_{mk,pred,licence,inv}.py) CALL them instead of pasting a fifth copy (docs/script-writing.md rules 1, 4).
The cycle-155 makers are module-level scripts (importing one runs it), and tools/stagekit.py is pinned (aec03c6c) and outside this card's write
globs, so the blocks live here; moving them into stagekit is OPEN (facts file).
  Gate(...)      == gate() of prep_c155_a4_1_mk.py:62 / _pred.py:51 / _licence.py:32 / _inv.py:60 (fatal flag kept)
  step_facts     == prep_c155_a4_1_mk.py:460-469 (= prep_c155_a2_1_mk.py:255-264)
  tie_rows       == prep_c155_a4_1_mk.py:477-506 (= prep_c155_a2_1_mk.py:274-287)
  main_of        == prep_c155_a4_1_mk.py:423-426 (= prep_c155_a2_1_mk.py:229)
  sg_census      == prep_c155_a4_1_mk.py:540-553 (= prep_c155_a2_1_mk.py:336-347)
Self-test (--selftest): replays cycle 155's recorded data - step_facts over the REALSIM step files listed in prep_c155_a4_1_session.json == its
realsim_states; sg_census over plan_ring_p5s02.json == its sink_gate_census; main_of over 155's step-1 ops == its main_peak_mb 680.0
(tie_rows needs a pass-A result: exercised by the maker's TIE gate). PREDICTION: 3/0.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c156_a1_1_lib.log -- py -u tools/bench/prep_c156_a1_1_lib.py --selftest"""
import hashlib, json, os, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                   # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731


class Gate(object):
    """Gate counter: g(label, ok, detail, fatal=True) prints 'GATE PASS|FAIL | label | detail'; a fatal FAIL prints the C6 RESULT line and
    exits 1. g.result(arts) prints the RESULT line. Same text as the cycle-155 makers' gate(). Self-test: --selftest."""

    def __init__(self, width=900, fatal_default=True):
        self.G, self.ARTS, self.width, self.fatal_default = {"pass": 0, "fail": 0, "first": None}, [], width, fatal_default

    def __call__(self, label, ok, d="", fatal=None):
        fatal = self.fatal_default if fatal is None else fatal
        self.G["pass" if ok else "fail"] += 1
        self.G["first"] = self.G["first"] or (None if ok else label)
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:self.width]), flush=True)
        if not ok and fatal:
            self.result()
            sys.exit(1)

    def result(self, arts=None):
        print(protocol.result_line(protocol.make_result(self.G["pass"], self.G["fail"], self.G["first"], self.ARTS if arts is None else arts)), flush=True)
        return 1 if self.G["fail"] else 0


def step_facts(tag, R_, quiet=False):
    """{step n: md5 of the step file's state} for a stagesim.simulate result; prints one 'FACT STEP' line per step (op, id, ok/PROVISIONAL/
    ERROR, model source, file + md5, state md5). Self-test: --selftest (== prep_c155_a4_1_session.json realsim_states)."""
    out = {}
    for st in (R_ or {}).get("steps") or []:
        p_ = (st.get("file") or {}).get("path")
        sj = J(p_)
        out[st["n"]] = hashlib.md5(json.dumps(sj["state"], sort_keys=True, default=str).encode("utf-8")).hexdigest()
        if not quiet:
            print("FACT STEP {0} n {1:02d} op {2} id {3}: {4} model {5}; file {6} md5 {7}; state {8}".format(
                  tag, st["n"], st.get("op"), st.get("id"), "ERROR " + str(st.get("error")) if st.get("error") else ("PROVISIONAL" if st.get("provisional") else "ok"),
                  st.get("model_source"), p_ and rel(p_), p_ and md5(p_), out[st["n"]][:8]), flush=True)
    return out


def tie_rows(SA, ACTS, ok_pairs, key_parts, card):
    """(ties, untied, open_rows): every end cdiff row of a pass-A sim tied to the FIRST action of the unbroken run of steps that carry it (or to a
    declared step-0 open pair in `ok_pairs` {(node, term): why}); open_rows = one {node, term, why} per distinct pair, in tie order. Self-test:
    the maker's TIE gate (needs a live pass-A result)."""
    ties, untied = {}, []
    for key in SA["end_cdiff_rows"]:
        n0 = SA["steps"][-1]["n"]
        for st in reversed(SA["steps"]):
            if st.get("cdiff_rows") is not None and key in st["cdiff_rows"]:
                n0 = st["n"]
            else:
                break
        p = (key_parts(key)[0], key_parts(key)[2])
        if n0 >= 1:
            ties[key] = {"n": n0, "id": ACTS[n0 - 1]["id"], "op": ACTS[n0 - 1]["op"], "class": ACTS[n0 - 1].get("class") or ACTS[n0 - 1]["op"], "pair": p}
        elif p in ok_pairs:
            ties[key] = {"n": 0, "id": ok_pairs[p], "op": "base", "class": "step0-declared", "pair": p}
        else:
            untied.append((key, n0))
    orows, seen = [], set()
    for k in sorted(ties, key=lambda k: (ties[k]["n"], k)):
        t = ties[k]
        if t["pair"] not in seen:
            seen.add(t["pair"])
            orows.append({"node": int(t["pair"][0]), "term": t["pair"][1], "why": ("{0}: made by action {1} (#{2} {3} {4})".format(
                card, t["id"], t["n"], t["op"], t["class"]) if t["n"] >= 1 else "{0}: open at step 0 = declared open row of the base plan".format(card))[:300]})
    return ties, untied, orows


def main_of(n, KINDS, SX, SPR, MODEL, START, reads=2):
    """(MAIN MB, x10_model_peak dict, checkpoints) of the op prefix 1..n: Executor peak at START with a checkpoint at every BIND op + `reads`
    whole-VI reads of the main recipe source (prep_c152_b2_1_mk.py:79). Self-test: --selftest (155's step-1 MAIN 680.0)."""
    cps = sorted({0, n} | set(k for k in range(1, n + 1) if KINDS[k - 1] in SX.BIND_KINDS))
    mp = SPR.x10_model_peak(KINDS[:n], cps, model=MODEL, start_mb=START)
    return round(mp["peak_mb"] + reads * float(MODEL["read_mb"]["value"]), 1), mp, cps


def sg_census(p, SX):
    """The ControlTerminal-sink rows of a FINAL plan: every wire action whose sim effect's dst terminal is a ControlTerminal (stagexec.is_ct)
    in the previous step's state; route 'indicator' (its source was already wired -> needs a declared sink gate) else 'ctlsink'. Self-test:
    --selftest (== prep_c155_a4_1_session.json sink_gate_census)."""
    fz = p.get("finalized") or {}
    SF = dict((int(x["n"]), x["path"]) for x in fz.get("step_files") or [])
    SGC = []
    for n, a in enumerate(p["actions"], 1):
        if a.get("op") != "wire" or n not in SF or (n - 1) not in SF:
            continue
        eff_ = J(SF[n]).get("effect") or {}
        prev = J(SF[n - 1])["state"]["terminals"]
        du, su = eff_.get("dst_term_uid"), eff_.get("src_term_uid")
        rd = next((r for r in prev if r["term_uid"] == du), None)
        rs = next((r for r in prev if r["term_uid"] == su), None)
        if rd is not None and SX.is_ct(rd):
            route = "indicator" if (rs is not None and rs.get("wire_uid")) else "ctlsink"
            SGC.append({"n": n, "id": a["id"], "sink": [rd["owner_uid"], rd["term_name"]], "dst_term_uid": du, "src_term_uid": su, "route": route,
                        "needs_sink_gate": route == "indicator"})
    return SGC


if __name__ == "__main__" and "--selftest" in sys.argv:
    import stagexec as SX, stage_prerun as SPR, stagesim as SS                                # noqa: E401
    g = Gate(fatal_default=False)
    B = os.path.join(ROOT, "tools", "bench")
    S5 = J(os.path.join(B, "prep_c155_a4_1_session.json"))
    R_ = {"steps": [{"n": s["n"], "op": s["op"], "id": s["id"], "file": {"path": os.path.join(ROOT, s["file"])}} for s in S5["steps"]]}
    hb = step_facts("SELFTEST", R_, quiet=True)
    g("T1 step_facts over 155's {0} REALSIM step files == session realsim_states".format(len(hb)),
      dict((str(k), v) for k, v in hb.items()) == dict((str(k), v) for k, v in S5["realsim_states"].items()))
    P5 = J(os.path.join(B, "plan_ring_p5s02.json"))
    g("T2 sg_census(plan_ring_p5s02.json) == session sink_gate_census", sg_census(P5, SX) == S5["sink_gate_census"], sg_census(P5, SX))
    ops = SX.compile_plan(P5)
    m, _mp, _c = main_of(len(ops), [o["kind"] for o in ops], SX, SPR, SPR.load_memory_model(), S5["start_mb"])
    g("T3 main_of(155 step 1, {0} ops) {1} == session main_peak_mb {2}".format(len(ops), m, S5["main_peak_mb"]), m == S5["main_peak_mb"])
    sys.exit(g.result())
