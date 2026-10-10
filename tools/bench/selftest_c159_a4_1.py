# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-a4-1.md
# ---
r"""selftest_c159_a4_1 - card 159-a4-1 (docs/d1/ring-p5.md PD387(e); docs/violation-decisions.md device-failed 2026-10-10 03:2x),
OFFLINE: no LabVIEW, no COM; every dry runs as `py tools/stage_prerun.py --dry <recipe> --no-record --json-out <%TEMP%>` (COM stubbed);
fixtures (recipe copies, preds, fp-77 scripts) are written under %TEMP% only. Shared functions under test (called, not copied):
stage_prerun.dry_unverified_labels / merge_unverified / the dry's result-gate rule / offline_override_delegations (is_vi_modifying),
stagekit.census_unpredicted_reason / sim_census_snapshot / SimCensus / Stage.census_gate / RingSession.gate_cen2.
PREDICTION (gates):
 P0  card input pins: diag_c158_a2_2_dry.log ae9c4d64, _scr_dry.log 81ef40d0, _prerun.log d4b548c7, _scr_prerun.log 0f20126a,
     _checklaunch.py b144b581, _facts.md 6376951c.
 A1  stored c158 dry log: dry_unverified_labels -> exactly 2 labels, CEN2 (UNVERIFIED-DRY, :70) and PB (UNVERIFIED, :73); the stored
     final line says `unverified 1` (the defect: CEN2 printed, not counted).  A2  the same on the stored scratch dry log (:82, :88, :93).
 A3  a docstring line naming UNVERIFIED-DRY is not counted; a PASS gate line whose detail says UNVERIFIED-DRY is; an UNPREDICTED line
     is; merge_unverified keeps 'address {..}' once against 'address {..} after mutation ...'.
 B1  census_unpredicted_reason: c158 pred (census = the 6 classes of dry.log:70, census_overall UNPREDICTED) -> a reason; current pred
     (MEASURED-SCRATCH) -> None; empty census -> reason; PASS with no unpredicted rows -> None; overall absent -> reason.
 C1  Stage.census_gate (gate recorded, not written): SimCensus pair in a DRY -> a gate (PASS equal / FAIL unequal); plain dicts in a
     DRY -> UNVERIFIED-DRY, no gate; `unpredicted=` -> UNPREDICTED, no gate, R['unpredicted'].
 D1  live dry, stage_d1_ring_p5s02a.py with the c158 pred (copy): CEN2 UNPREDICTED and counted; status PASS-UNVERIFIED; PB is on the
     simulated end (its line is PASS or UNVERIFIED-DRY, never a stub PASS); the final count == len(unverified list) and includes CEN2.
 D2  live dry, fixture pred = the current pred with census = its own simulated census (fully declared, census_overall PASS): CEN2 PASS
     on the simulated end; PB, D, TD PASS; DRY PASS, unverified 0.
 D3  live dry of the recipe as stored (MEASURED-SCRATCH pred ed84b5fd): CEN2 is COMPUTED on the simulated end (a PASS/FAIL CEN2 line
     naming stagesim), not UNVERIFIED-DRY. Recorded as a fact whichever verdict (judgement: see OPEN in the facts file).
 D4  live dry of the scratch pair stage_d1_ring_p5s02a_scratch.py (runs the pair's R.body): D / TD / PB PASS, CEN2 computed.
 E1  live dry of a %TEMP% probe recipe: a result gate 'PB ...' TRUE on stub input -> UNVERIFIED-DRY, counted; 'PB ...' TRUE on clean
     data -> PASS; a non-result gate TRUE on stub input -> PASS (unchanged rule).
 F1  fp-77: a stagekit-importing script whose only verb calls are super()/Base. delegations inside same-named overrides of a
     SimBackend / DryPlanBE subclass -> not VI-modifying.  F2 a script calling s.connect(...) -> modifying.  F3 the same delegation
     in an LVBackend subclass -> modifying.  F4 mixed bases (SimBackend, object) -> modifying.  F5 an override that calls a DIFFERENT
     verb -> modifying.  F6 tools/bench/selftest_c157_innerface.py -> not modifying.
 G1  every stored stageplan tools/bench/plan_*.json compiles with stagexec.compile_plan (stagexec.py 7a712ccb, not an output of this
     card): count ok / failed and a digest of the op-kind lists, printed for the before/after record.
Usage: py tools/bgrun.py --material --max-min 15 --log tools/bench/selftest_c159_a4_1.log -- py -u tools/bench/selftest_c159_a4_1.py"""
import glob
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import protocol  # noqa: E402
import stage_prerun as SP  # noqa: E402
import stagekit as K  # noqa: E402
import stagexec as SX  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}
TMP = tempfile.mkdtemp(prefix="c159_a4_1_")
RECIPE = os.path.join(TOOLS, "recipes", "stage_d1_ring_p5s02a.py")
PLAN = os.path.join(HERE, "plan_ring_p5s02a.json")
PRED = os.path.join(HERE, "plan_ring_p5s02a_pred.json")
DRYLOG = os.path.join(HERE, "diag_c158_a2_2_dry.log")
SCRLOG = os.path.join(HERE, "diag_c158_a2_2_scr_dry.log")


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)
    return ok


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def lines(p):
    return open(p, encoding="utf-8", errors="replace").read().splitlines()


def jdump(obj, name):
    p = os.path.join(TMP, name)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    return p


def recipe_copy(name, pred_path):
    """The stored recipe with ONLY its PRED and OUT_JSON literals pointed at %TEMP% (a test fixture, not a recipe)."""
    src = open(RECIPE, encoding="utf-8").read()
    src = src.replace('PRED = os.path.join(K.BENCH, "plan_ring_p5s02a_pred.json")', "PRED = r'{0}'".format(pred_path))
    src = src.replace('OUT_JSON = os.path.join(K.BENCH, "launch_c156_p5s02a.json")', "OUT_JSON = r'{0}'".format(os.path.join(TMP, name + ".json")))
    src = src.replace("sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))", "sys.path.insert(0, r'{0}')".format(TOOLS))
    p = os.path.join(TMP, name + ".py")
    open(p, "w", encoding="utf-8").write(src)
    return p


def dry(recipe, tag):
    """`stage_prerun.py --dry <recipe> --no-record --json-out` in a fresh process -> (trace dict, stdout text)."""
    out = os.path.join(TMP, tag + "_trace.json")
    r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "stage_prerun.py"), "--dry", recipe, "--no-record", "--json-out", out],
                       cwd=ROOT, capture_output=True, text=True, timeout=420)
    text = r.stdout + r.stderr
    with open(os.path.join(TMP, tag + ".out"), "w", encoding="utf-8") as f:
        f.write(text)
    try:
        tr = json.load(open(out, encoding="utf-8"))
    except (OSError, ValueError):
        tr = {}
    final = [ln for ln in text.splitlines() if ln.startswith("=== DRY ")]
    print("FACT dry {0}: {1}".format(tag, (final or ["<no === DRY line>"])[-1][:300]), flush=True)
    return tr, text


def gate_line(text, prefix):
    """The first gate output line whose label starts with `prefix` -> (token, line) or (None, None)."""
    for ln in text.splitlines():
        m = SP.DRY_UNV_RE.match(ln)
        if m and m.group(2).startswith(prefix):
            return m.group(1), ln
    return None, None


# ---------------------------------------------------------------------------------------------- P0
CARD = json.load(open(os.path.join(HERE, "cards", "task_159-a4-1.json"), encoding="utf-8"))
want = dict((i["path"], i["md5"]) for i in CARD["inputs"] if "diag_c158_a2_2" in i["path"])
got = dict((p, md5(os.path.join(ROOT, p))) for p in want)
gate("P0 card input pins (stored c158-a2-2 logs / checklaunch / facts)", got == want, dict((os.path.basename(k), v[:8]) for k, v in got.items()))

# ---------------------------------------------------------------------------------------------- A
print("---------- A stored logs through dry_unverified_labels", flush=True)
for tag, p, n_final in (("A1", DRYLOG, 78), ("A2", SCRLOG, 93)):
    L = lines(p)
    labs = SP.dry_unverified_labels(L)
    fin = L[n_final - 1]
    gate("{0} {1}: labels == [CEN2, PB] (2); stored final line says 'unverified 1' (CEN2 printed, not counted)".format(tag, os.path.basename(p)),
         len(labs) == 2 and labs[0].startswith("CEN2 ") and labs[1].startswith("PB ") and "unverified 1," in fin, (labs, fin[-140:]))
doc = "CEN2 == pred census (UNVERIFIED-DRY in a dry run); TD every"
mix = ["  " + doc, "  PASS  R9 readback x  {'a': 1} (UNVERIFIED-DRY)", "  UNPREDICTED  CEN2 c  (declared set empty {})",
       "  UNVERIFIED  address {'n': 1} after mutation Stage._op x: boom", "  PASS  E1 fine  detail"]
labs = SP.dry_unverified_labels(mix)
merged = SP.merge_unverified(["address {'n': 1}"], labs)
gate("A3 docstring line not counted; PASS-with-UNVERIFIED-DRY and UNPREDICTED lines counted; address entry merged once",
     labs == ["R9 readback x", "CEN2 c", "address {'n': 1} after mutation Stage._op x: boom"] and merged == ["address {'n': 1}", "R9 readback x", "CEN2 c"],
     (labs, merged))

# ---------------------------------------------------------------------------------------------- B
print("---------- B census_unpredicted_reason", flush=True)
cur = json.load(open(PRED, encoding="utf-8"))
m = re.search(r"declared (\{.*\})\)\s*$", lines(DRYLOG)[69])
c158_census = json.loads(m.group(1)) if m else None
c158 = dict(cur, census=c158_census, census_overall="UNPREDICTED")
c158.pop("census_source", None)
cases = [("c158 pred (6 classes, UNPREDICTED)", c158, True), ("current pred " + str(cur.get("census_overall")), cur, False),
         ("empty census", dict(cur, census={}), True), ("PASS, no unpredicted rows", dict(cur, census_overall="PASS", census_unpredicted=[]), False),
         ("overall absent", dict((k, v) for k, v in cur.items() if k != "census_overall"), True)]
res = [(n, K.census_unpredicted_reason(p)) for n, p, _ in cases]
gate("B1 census_unpredicted_reason: reason iff not covering (c158 / empty / absent), None for MEASURED and PASS-complete",
     c158_census == {"CaseStructure": 1, "Diagram": 2, "InnerTerminal": 2, "OuterTerminal": 1, "Tunnel": 1, "Wire": 1}
     and all(bool(r) == want_r for (n, r), (_n, _p, want_r) in zip(res, cases)), res)

# ---------------------------------------------------------------------------------------------- C
print("---------- C Stage.census_gate", flush=True)
REC = []
st = K.Stage(cur["bed"], cur["bed_md5"], "c159_cg", out_json=os.path.join(TMP, "cg.json"))
st.gate = lambda label, ok, detail="", fatal=False, kind=None: REC.append((label, bool(ok))) or ok
a = K.SimCensus({1: "Wire", 2: "Function"})
b = K.SimCensus({1: "Wire", 2: "Function", 3: "Wire", 4: "Function"})
had = hasattr(K.g.report_all, "_dry")
old_dry = getattr(K.g.report_all, "_dry", None)
K.g.report_all._dry = True
try:
    buf = io.StringIO()
    with redirect_stdout(buf):
        g1 = st.census_gate("CEN2 eq", a, b, {"Wire": 1, "Function": 1})
        g2 = st.census_gate("CEN2 ne", a, b, {"Wire": 2, "Function": 1})
        g3 = st.census_gate("CEN2 plain", {1: "Wire"}, {1: "Wire", 3: "Wire"}, {"Wire": 1})
        g4 = st.census_gate("CEN2 partial", a, b, {"Wire": 1}, unpredicted="census_overall UNPREDICTED")
finally:
    if had:
        K.g.report_all._dry = old_dry
    else:
        del K.g.report_all._dry
out = buf.getvalue()
gate("C1 dry: SimCensus pair -> gate (eq PASS, ne FAIL); plain dicts -> UNVERIFIED-DRY, no gate; unpredicted= -> UNPREDICTED, no gate",
     REC == [("CEN2 eq", True), ("CEN2 ne", False)] and g1 == {"Wire": 1, "Function": 1} and g3 is None
     and "UNVERIFIED-DRY  CEN2 plain" in out and "UNPREDICTED  CEN2 partial" in out and g4 == {"Wire": 1, "Function": 1}
     and st.R.get("unpredicted") == ["CEN2 partial"], (REC, out[-400:]))

# ---------------------------------------------------------------------------------------------- D
print("---------- D live dries of stage_d1_ring_p5s02a.py (copies with %TEMP% preds) and as stored", flush=True)
tr1, t1 = dry(recipe_copy("d1_c158pred", jdump(c158, "pred_c158.json")), "d1")
k_cen, l_cen = gate_line(t1, "CEN2 ")
k_pb, l_pb = gate_line(t1, "PB ")
fin1 = [ln for ln in t1.splitlines() if ln.startswith("=== DRY ")]
gate("D1 c158 pred: CEN2 UNPREDICTED and counted; status PASS-UNVERIFIED; PB on the simulated end (PASS or UNVERIFIED-DRY); final count == list",
     k_cen == "UNPREDICTED" and any(u.startswith("CEN2 ") for u in tr1.get("unverified") or []) and tr1.get("status") == "PASS-UNVERIFIED"
     and k_pb in ("PASS", "UNVERIFIED-DRY", "UNVERIFIED") and fin1 and "unverified {0},".format(len(tr1.get("unverified") or [])) in fin1[-1],
     {"cen2": l_cen and l_cen[:160], "pb": l_pb and l_pb[:120], "unverified": tr1.get("unverified"), "status": tr1.get("status")})
print("FACT D1 PB line: {0}".format((l_pb or "")[:200]), flush=True)

P_ = json.load(open(PLAN, encoding="utf-8"))
sf = P_["finalized"]["step_files"]
s0 = K.sim_census_snapshot(json.load(open(os.path.join(ROOT, sf[0]["path"]), encoding="utf-8"))["state"], tuple(cur["census"]))
s1 = K.sim_census_snapshot(json.load(open(os.path.join(ROOT, sf[-1]["path"]), encoding="utf-8"))["state"], tuple(cur["census"]))
simc = {}
for u in set(s1) - set(s0):
    simc[s1[u]] = simc.get(s1[u], 0) + 1
full = dict(cur, census=simc, census_overall="PASS", census_unpredicted=[])
full.pop("census_source", None)
print("FACT D2 fixture census = the plan's own simulated census {0} (current pred {1})".format(json.dumps(simc, sort_keys=True),
      json.dumps(cur["census"], sort_keys=True)), flush=True)
tr2, t2 = dry(recipe_copy("d2_full", jdump(full, "pred_full.json")), "d2")
ks = dict((p, gate_line(t2, p)[0]) for p in ("CEN2 ", "PB ", "D ", "TD "))
gate("D2 fully declared (sim census, PASS): CEN2 / PB / D / TD PASS on the simulated end; DRY PASS, unverified 0",
     ks == {"CEN2 ": "PASS", "PB ": "PASS", "D ": "PASS", "TD ": "PASS"} and tr2.get("status") == "PASS" and tr2.get("unverified") == []
     and "stagesim simulated end" in (gate_line(t2, "CEN2 ")[1] or ""), {"gates": ks, "status": tr2.get("status"), "unverified": tr2.get("unverified")})

tr3, t3 = dry(RECIPE, "d3")
k3, l3 = gate_line(t3, "CEN2 ")
gate("D3 recipe as stored (pred {0}): CEN2 computed on the simulated end (PASS/FAIL line naming stagesim), not UNVERIFIED-DRY".format(md5(PRED)[:8]),
     k3 in ("PASS", "FAIL") and "stagesim simulated end" in (l3 or ""), (l3 or "")[:400])
print("FACT D3 status {0} first_fail {1} unverified {2}".format(tr3.get("status"), str(tr3.get("first_fail"))[:300], tr3.get("unverified")), flush=True)
tr5, t5 = dry(os.path.join(TOOLS, "recipes", "stage_d1_ring_p5s02a_scratch.py"), "d4")
k5 = dict((p, gate_line(t5, p)[0]) for p in ("CEN2 ", "PB ", "D ", "TD "))
gate("D4 scratch pair as stored (runs R.body): D / TD / PB PASS on the simulated end (pair statements scoped), CEN2 computed (PASS/FAIL), not stub",
     k5["PB "] == k5["D "] == k5["TD "] == "PASS" and k5["CEN2 "] in ("PASS", "FAIL") and "stagesim simulated end" in (gate_line(t5, "CEN2 ")[1] or ""),
     {"gates": k5, "status": tr5.get("status"), "unverified": tr5.get("unverified")})

# ---------------------------------------------------------------------------------------------- E
print("---------- E result gate TRUE on stub input", flush=True)
probe = os.path.join(TMP, "c159_taint_probe.py")
open(probe, "w", encoding="utf-8").write("""import os, sys
sys.path.insert(0, r'{tools}')
import stagekit as K
PLAN = os.path.join(K.BENCH, "plan_ring_p5s02a.json")
B = K.jload(K.ROOT, K.jload(PLAN)["finalized"]["base"]["path"])


def body(s):
    s.start()
    s.gate("PB stub-input probe", bool(K.g.exec_state(s.work)), "")
    s.gate("PB clean probe", True, "")
    s.gate("XX stub-input non-result probe", bool(K.g.exec_state(s.work)), "")


if __name__ == "__main__":
    st = K.Stage(B["vi"], B["md5"], "c159_taint", preload=False, out_json=r'{out}')
    sys.exit(K.run(body, st))
""".format(tools=TOOLS, out=os.path.join(TMP, "taint.json")))
tr4, t4 = dry(probe, "e1")
ke = dict((p, gate_line(t4, p)[0]) for p in ("PB stub", "PB clean", "XX stub"))
gate("E1 'PB' TRUE on stub input -> UNVERIFIED-DRY counted; 'PB' clean -> PASS; non-result TRUE on stub -> PASS",
     ke == {"PB stub": "UNVERIFIED-DRY", "PB clean": "PASS", "XX stub": "PASS"} and tr4.get("unverified") == ["PB stub-input probe"]
     and tr4.get("status") == "PASS-UNVERIFIED", {"gates": ke, "unverified": tr4.get("unverified"), "status": tr4.get("status")})

# ---------------------------------------------------------------------------------------------- F (fp-77)
print("---------- F fp-77 is_vi_modifying", flush=True)
HEAD = "import os, sys\nsys.path.insert(0, r'{0}')\nimport stagekit as K\nimport stagexec as SX\n".format(TOOLS)
FIX = {
    "f1_offline_override": (HEAD + "class SynthBE(SX.SimBackend):\n    def connect(self, *a, **k):\n        return super(SynthBE, self).connect(*a, **k)\n"
                            "    def move_in(self, *a, **k):\n        return SX.SimBackend.move_in(self, *a, **k)\n"
                            "class B2(SX.DryPlanBE):\n    def delete_object(self, *a):\n        return super().delete_object(*a)\n", False),
    "f2_real_modifying": (HEAD + "s = K.Stage('x.vi', 'm', 'n')\ns.connect('a', 'b')\n", True),
    "f3_lvbackend_override": (HEAD + "class L(SX.LVBackend):\n    def connect(self, *a, **k):\n        return super().connect(*a, **k)\n", True),
    "f4_mixed_bases": (HEAD + "class M(SX.SimBackend, object):\n    def connect(self, *a, **k):\n        return super().connect(*a, **k)\n", True),
    "f5_other_verb": (HEAD + "class O(SX.SimBackend):\n    def read(self):\n        self.connect('a', 'b')\n        return []\n", True),
}
fres = {}
for name, (src, want_mod) in FIX.items():
    p = os.path.join(TMP, name + ".py")
    open(p, "w", encoding="utf-8").write(src)
    fres[name] = (SP.is_vi_modifying(p), want_mod, SP.vi_modifying_calls(p))
fres["f6_selftest_c157_innerface"] = (SP.is_vi_modifying(os.path.join(HERE, "selftest_c157_innerface.py")), False, None)
gate("F1-F6 fp-77: offline-backend delegations not modifying; real call, LVBackend / mixed-base override, other-verb call still modifying; c157 innerface not",
     all(v[0] == v[1] for v in fres.values()), fres)

# ---------------------------------------------------------------------------------------------- G
print("---------- G stored stageplans compile (stagexec unchanged)", flush=True)
ok_n, bad, dig = 0, [], hashlib.md5()
for p in sorted(glob.glob(os.path.join(HERE, "plan_*.json"))):
    try:
        d = json.load(open(p, encoding="utf-8"))
    except ValueError:
        continue
    if not (isinstance(d, dict) and d.get("schema") == "stageplan/1"):
        continue
    try:
        kinds = [o["kind"] for o in SX.compile_plan(d)]
        ok_n += 1
        dig.update((os.path.basename(p) + ":" + ",".join(kinds) + "\n").encode("utf-8"))
    except Exception as e:  # noqa: BLE001
        bad.append((os.path.basename(p), type(e).__name__))
        dig.update((os.path.basename(p) + ":ERR " + type(e).__name__ + "\n").encode("utf-8"))
print("FACT G stageplans compiled ok {0}, raised {1} {2}; kinds digest {3}; stagexec md5 {4}".format(ok_n, len(bad), bad[:8], dig.hexdigest(), md5(os.path.join(TOOLS, "stagexec.py"))), flush=True)
gate("G1 stagexec.py unchanged (7a712ccb, compile_plan's code) and every stored stageplan compiled or raised as recorded above",
     md5(os.path.join(TOOLS, "stagexec.py")).startswith("7a712ccb") and ok_n > 0, (ok_n, len(bad)))

print("FACT md5 stage_prerun {0} stagekit {1}; temp dir {2}".format(md5(os.path.join(TOOLS, "stage_prerun.py")), md5(os.path.join(TOOLS, "stagekit.py")), TMP), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
