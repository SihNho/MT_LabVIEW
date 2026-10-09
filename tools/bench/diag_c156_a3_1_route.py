# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a3-1.md
# ---
r"""diag_c156_a3_1_route - card 156-a3-1 measurements 1 and 3 (offline, json only, no LabVIEW, no COM).
Prior art found and CALLED unchanged: stagexec.connect_route / Addr / SimReader / _StateHolder / dedupe / compile_plan /
base_registers / BIND_KINDS (stagexec 25a1494c, the call shape of stagexec.py:2953 and :3783 and the self-tests at :4803-4857).
Nothing is copied: the script only loads the plan + sim step files and calls those functions.
PREDICTIONS (peer archive/peer/2026-10-09-c156-a2-2-p5s02a-innerface.md s4):
  P1 op 16 (src #24360 -> dst 5760) on the sim state, as stored: route 'cfw'.
  P2 same with ONLY #24360's wire_uid set to 0: ExecStop 'ADDRESS: #24360 is an INNER face of LoopTunnel #24357 ...'.
  P3/P4 op 17 (src #24367 -> dst 5778): the same pair ('cfw' / INNER-face stop naming #24367).
  P5 pins: stagexec 25a1494c, stagesim eb99c6ba, plan 4284c22a unchanged.
States tried: step_15 (the brief's file) AND the executor's own prev state for the op (step(first act - 1), stagexec.py:2431).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c156_a3_1_route.log -- py -u tools/bench/diag_c156_a3_1_route.py"""
import copy, hashlib, json, os, sys                                                       # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                     # noqa: E402
G = {"pass": 0, "fail": 0, "first": None}
SIM = os.path.join(ROOT, "tools", "bench", "sim", "ring_p5s02a")
PLAN = os.path.join(ROOT, "tools", "bench", "plan_ring_p5s02a.json")
PINS = {"tools/stagexec.py": "25a1494c", "tools/stagesim.py": "eb99c6ba", "tools/bench/plan_ring_p5s02a.json": "4284c22a",
        "tools/bench/sim/ring_p5s02a/step_15_tunnel.json": "b7da7fa7", "tools/bench/sim/ring_p5s02a/summary.json": "f0705439"}
md = lambda k: hashlib.md5(open(os.path.join(ROOT, k), "rb").read()).hexdigest()[:8]    # noqa: E731


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


def fact(m):
    print("  FACT  " + m, flush=True)


P = json.load(open(PLAN, encoding="utf-8"))
A = P["actions"]
STEPS = dict((int(s["n"]), os.path.join(ROOT, s["path"])) for s in P["finalized"]["step_files"])
_cache = {}


def step(n):
    if n not in _cache:
        _cache[n] = json.load(open(STEPS[n], encoding="utf-8"))
    return _cache[n]


def term_of(end):
    return int(end["term_uid"]) if isinstance(end, dict) and end.get("term_uid") is not None else None


def row(state, t):
    r = [x for x in state["terminals"] if x["term_uid"] == t]
    return [(x["owner_uid"], x["owner_class"], x["term_class"], x["term_name"], x["is_source"], x["wire_uid"], x["frame_diagram"])
            for x in r]


def route(state, src, dst, zero_src=False):
    """connect_route on the sim state (as the dry backend builds its Addr, stagexec.py:3519 + :2433); zero_src sets ONLY src's
    wire_uid to 0. Returns (kind or 'STOP', how/text)."""
    st = copy.deepcopy(state)
    if zero_src:
        for x in st["terminals"]:
            if x["term_uid"] == src:
                x["wire_uid"] = 0
    real = SX.dedupe(st["terminals"])
    addr = SX.Addr(SX.SimReader(SX._StateHolder(st)), st.get("owners"))
    loop_of = dict((u, v["loop"]) for u, v in SX.base_registers(st).items())             # stagexec.py:2325 (base registers)
    try:
        kind, _rs, _rd, info = SX.connect_route(addr, real, src, dst, loop_of)
        return kind, {"src_how": info.get("src_how"), "dst_how": info.get("dst_how"), "dst": info.get("dst")}
    except SX.ExecStop as e:
        return "STOP", str(e)


print("---------- [0] pins", flush=True)
m0 = dict((k, md(k)) for k in PINS)
gate("P5 pins at start == card inputs", all(m0[k] == PINS[k] for k in PINS), m0)
OPS = SX.compile_plan(P)
fact("compiled ops {0}: {1}".format(len(OPS), [(k, o["kind"], o["acts"]) for k, o in enumerate(OPS, 1)]))

print("---------- [1] op 16 / op 17 route, wire present vs wire 0", flush=True)
CASES = [("op16", 16, 24360, 5760, "ADDRESS: #24360 is an INNER face of LoopTunnel #24357"),
         ("op17", 17, 24367, 5778, "ADDRESS: #24367 is an INNER face of LoopTunnel #24361")]
for lab, k, src, dst, want_stop in CASES:
    op = OPS[k - 1]
    ai, ao = A[op["in_act"] - 1], A[op["out_act"] - 1]
    fact("{0} kind {1} acts {2} in_act {3} src {4} out_act {5} dst {6}".format(lab, op["kind"], op["acts"], op["in_act"],
                                                                                 ai["src"], op["out_act"], ao["dst"]))
    gate("{0} plan ends == ({1} -> {2})".format(lab, src, dst), term_of(ai["src"]) == src and term_of(ao["dst"]) == dst)
    prev_n = op["acts"][0] - 1
    for sn in sorted(set([15, prev_n])):
        stt = step(sn)["state"]
        fact("{0} step_{1:02d} src row {2}".format(lab, sn, row(stt, src)))
        fact("{0} step_{1:02d} dst row {2}".format(lab, sn, row(stt, dst)))
        k1, h1 = route(stt, src, dst)
        k0, h0 = route(stt, src, dst, zero_src=True)
        fact("{0} step_{1:02d} AS STORED -> {2} {3}".format(lab, sn, k1, h1))
        fact("{0} step_{1:02d} WIRE 0    -> {2} {3}".format(lab, sn, k0, h0))
        gate("P{0} {1} step_{2:02d} as stored: route 'cfw'".format(1 if k == 16 else 3, lab, sn), k1 == "cfw", k1)
        gate("P{0} {1} step_{2:02d} src wire 0: the INNER-face stop".format(2 if k == 16 else 4, lab, sn),
             k0 == "STOP" and str(h0).startswith(want_stop), str(h0)[:200])

print("---------- [3] the ambiguous fate and every op after a move_in whose source is in allow_either", flush=True)
for sn in (9, 10):
    stt = step(sn)["state"]
    w = sorted((x["term_uid"], x["owner_uid"], x["owner_class"], x["term_class"], x["is_source"])
               for x in stt["terminals"] if x["wire_uid"] == 24330)
    fact("step_{0:02d} rows on wire 24330: {1}".format(sn, w))
for sn in (10, 11, 12):
    eff = step(sn).get("effect") or {}
    fact("step_{0:02d} ({1}) only_sink {2}".format(sn, A[sn - 1].get("id"), eff.get("only_sink")))
    fact("step_{0:02d} ({1}) only_source {2} allow_either {3}".format(sn, A[sn - 1].get("id"), eff.get("only_source"),
                                                                       eff.get("allow_either")))
SUM = json.load(open(os.path.join(SIM, "summary.json"), encoding="utf-8"))
first_mv = min(k for k, o in enumerate(OPS, 1) if o["kind"] == "move_in")
allow = set()
rows3 = []
for k, op in enumerate(OPS, 1):
    if k <= first_mv:                                        # the executor accumulates allow per op (stagexec.py:2466, :2533)
        for n in op["acts"]:
            allow.update((step(n).get("effect") or {}).get("allow_either") or [])
        continue
    if op["kind"] == "tunnel":
        s_end, d_end = A[op["in_act"] - 1]["src"], A[op["out_act"] - 1]["dst"]
    elif op["kind"] in ("connect", "wire_sr"):
        s_end, d_end = A[op["acts"][0] - 1].get("src"), A[op["acts"][0] - 1].get("dst")
    else:
        s_end = d_end = None
    s_t, d_t = term_of(s_end), term_of(d_end)
    inn = s_t is not None and s_t in allow
    fact("op {0} {1} acts {2} src {3} dst {4} src in allow_either-so-far {5}".format(k, op["kind"], op["acts"], s_end, d_end, inn))
    if inn and d_t is not None:
        stt = step(op["acts"][0] - 1)["state"]
        k1, h1 = route(stt, s_t, d_t)
        k0, h0 = route(stt, s_t, d_t, zero_src=True)
        rows3.append((k, s_t, d_t, k1, k0))
        fact("ROW3 op {0} src #{1} -> dst {2} (state step_{3:02d}; src row {4}): WIRED -> {5} {6} | WIRE 0 -> {7} {8}".format(
            k, s_t, d_t, op["acts"][0] - 1, row(stt, s_t), k1, str(h1)[:160], k0, str(h0)[:200]))
    for n in op["acts"]:
        allow.update((step(n).get("effect") or {}).get("allow_either") or [])
fact("allow_either accumulated over all steps {0}; summary.json top-level keys {1}".format(sorted(allow), sorted(SUM)[:12]))
gate("ROW3 at least one op after a move_in has an allow_either source", bool(rows3), rows3)

print("---------- [4] checkpoint inputs", flush=True)
fact("BIND_KINDS {0}; move_in ops {1}; ops whose kind is in BIND_KINDS {2}".format(
    SX.BIND_KINDS, [k for k, o in enumerate(OPS, 1) if o["kind"] == "move_in"],
    [k for k, o in enumerate(OPS, 1) if o["kind"] in SX.BIND_KINDS]))
fact("plan actions carrying a 'checkpoint' key: {0}".format([a.get("id") for a in A if "checkpoint" in a]))

m1 = dict((k, md(k)) for k in PINS)
gate("P5b pins unchanged during the run", m1 == m0, [k for k in m0 if m0[k] != m1[k]])
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
