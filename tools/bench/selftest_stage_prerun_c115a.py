r"""selftest_stage_prerun_c115a - card 115-1 A1/A2: stage_prerun X13 OPMODEL CONFORMANCE. PURE PYTHON, no LabVIEW.

Existed first: stage_prerun X11/X12 self-tests (selftest_stage_prerun_c114*.py, the shape copied); stagesim G68-G71 (toy
graph). This file tests the NEW sample replay only; no existing gate is touched.
Prediction contract: T1-T8 PASS -
  T1 ops [wire]: connect_from_wire.json PASS on both samples, wire_sr.json not-replayed + a WARN line, no fail
  T2 same with stagesim.cfw_border_rule disabled: FAIL naming raw/connect_from_wire_1.json field source_wire (A2)
  T3 ops [tunnel, wire]: tunnel.json PASS (tunnel_1 recreate, tunnel_2 new + join_stub kept)
  T4 ops without a model file (gate, decide): one WARN each, no fail, no file checked
  T5 a tampered copy of the model (cfw_2's sink 23241 moved to another wire after the op): FAIL field groups
  T6 cfw_border_rule restored after the disabled run (module attribute is the original function)
  T7 x13_gate over the finalized plans l2b3 / l2b2b / l2b2a: ok
  T8 `stage_prerun.py --prerun tools/bench/plan_l2b3.json --no-record` prints a PASS X13 line and exits 0
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_stage_prerun_c115a.log -- py -u tools/bench/selftest_stage_prerun_c115a.py
"""
import copy, json, os, shutil, subprocess, sys, tempfile                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); ROOT = os.path.dirname(TOOLS)  # noqa: E702
sys.path.insert(0, TOOLS)
import stage_prerun as SP, stagesim as SS, protocol                                    # noqa: E401,E402
G = []


def gate(l, ok, d=""):
    G.append((l, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", l, str(d)[:500]), flush=True)


orig = SS.cfw_border_rule
c1 = SP.opmodel_conformance(["wire"])
gate("T1 ops [wire]: connect_from_wire.json PASS (2 samples), wire_sr.json not-replayed + WARN, 0 fails",
     c1["files"]["connect_from_wire.json"] == {"status": "PASS", "samples": 2, "fails": []} and
     c1["files"]["wire_sr.json"]["status"] == "not-replayed" and any("wire_sr.json" in w for w in c1["warns"]) and
     not c1["fails"], (c1["files"], c1["warns"]))
c2 = SP.opmodel_conformance(["wire"], disable=("cfw_border_rule",))
f2 = [(x["sample"], x["field"], x["measured"], x["simulated"]) for x in c2["fails"]]
gate("T2 cfw_border_rule disabled: FAIL names raw/connect_from_wire_1.json field source_wire (recreated vs kept)",
     ("raw/connect_from_wire_1.json", "source_wire", "recreated", "kept") in f2 and
     c2["files"]["connect_from_wire.json"]["status"] == "FAIL", f2)
c3 = SP.opmodel_conformance(["tunnel", "wire"])
gate("T3 ops [tunnel, wire]: tunnel.json PASS on 2 samples, no fail",
     c3["files"].get("tunnel.json", {}).get("status") == "PASS" and c3["files"]["tunnel.json"]["samples"] == 2 and
     not c3["fails"], c3["files"])
c4 = SP.opmodel_conformance(["gate", "decide"])
gate("T4 ops without a model file: one WARN each, no file checked, no fail",
     not c4["files"] and not c4["fails"] and len(c4["warns"]) == 2 and all("no model file" in w for w in c4["warns"]),
     c4["warns"])
tmp = tempfile.mkdtemp(prefix="c115a_")
try:
    md = os.path.join(tmp, "opmodels")
    os.makedirs(os.path.join(md, "raw"))
    shutil.copy(os.path.join(SP.OPMODEL_DIR, "connect_from_wire.json"), md)
    for n in (1, 2):
        shutil.copy(os.path.join(SP.OPMODEL_DIR, "raw", "connect_from_wire_{0}.json".format(n)), os.path.join(md, "raw"))
    rp = os.path.join(md, "raw", "connect_from_wire_2.json")
    raw = json.load(open(rp, encoding="utf-8"))
    for c in raw["diff"]["terms_changed"]:
        if c["term_uid"] == 23241:
            c["changed"]["wire_uid"] = [23519, 99999]
    for e in raw["diff"]["edges_rewired"]:
        if e["sink"] == 23241:
            e["wire"] = [23519, 99999]
    json.dump(raw, open(rp, "w", encoding="utf-8"))
    c5 = SP.opmodel_conformance(["wire"], model_dir=md)
    f5 = [(x["sample"], x["field"]) for x in c5["fails"]]
    gate("T5 tampered sample (23241 on its own wire after the op): FAIL names raw/connect_from_wire_2.json field groups",
         ("raw/connect_from_wire_2.json", "groups") in f5 and ("raw/connect_from_wire_1.json", "groups") not in f5, f5)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
gate("T6 cfw_border_rule restored after the disabled run", SS.cfw_border_rule is orig)
plans = [json.load(open(os.path.join(HERE, "plan_{0}.json".format(s)), encoding="utf-8")) for s in ("l2b3", "l2b2b", "l2b2a")]
ok7, det7, w7 = SP.x13_gate(plans)
gate("T7 x13_gate over plan_l2b3 / l2b2b / l2b2a: ok ({0} WARN)".format(len(w7)), ok7, (det7, w7))
p = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "stage_prerun.py"), "--prerun",
                    os.path.join(HERE, "plan_l2b3.json"), "--no-record"], cwd=ROOT, capture_output=True, text=True,
                   timeout=600)
x13 = [l for l in p.stdout.splitlines() if "X13" in l]
gate("T8 --prerun plan_l2b3.json --no-record: a PASS X13 line, rc 0",
     any("PASS" in l and "X13" in l for l in p.stdout.splitlines() if "FAIL" not in l) and p.returncode == 0,
     (p.returncode, x13[:3], p.stdout.splitlines()[-3:]))
n = sum(1 for _l, ok in G if ok)
first = next((l for l, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n, len(G) - n, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n, len(G) - n, first)))
sys.exit(0 if first is None else 1)
