# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c165_a3_4_graph.log
# ---
r"""diag_c166_a1_1_mm - card 166-a1-1 step 6 (OFFLINE, files only): memory_model.json load_by_vi gets ONE key = hashlib md5 of the P5
final claudeDev\D1_ring_p5_20261010_172913.vi, value = the graph read's `MEM after load: X MB private` line (found by search in
diag_c165_a3_4_graph.log), entry format of the existing entries {value, vi, cite}. Same job as prep_c164_a3_7_write.py (a); calls
prep_c156_a1_1_lib (md5, Gate) and diag_c166_a1_1_lib (rewrite_json, changed_keys). Runs only after steps 2-4 passed: the graph log
and the tunnel log must each end RESULT PASS with 0 fails.
PREDICTION CONTRACT: M0 graph read PASS 15/0 + tunnel read PASS; M1 memory_model ff0fabca; M2 one MEM line (24, 647.8); M3 key not yet
present; M4 written in the old layout; M5 JSON compare: only load_by_vi differs, by the one key, old keys equal, fail_above_mb 680.0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c166_a1_1_mm.log -- py -u tools/bench/diag_c166_a1_1_mm.py"""
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import prep_c156_a1_1_lib as L  # noqa: E402
import diag_c166_a1_1_lib as J  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
FINAL = os.path.join(CD, "D1_ring_p5_20261010_172913.vi")
MM, MMB = os.path.join(B, "memory_model.json"), os.path.join(B, "diag_c166_a1_1_memory_model_before.json")
GLOG, TLOG = os.path.join(B, "diag_c165_a3_4_graph.log"), os.path.join(B, "diag_c166_a1_1_tun.log")
gate = L.Gate(fatal_default=False)


def result_of(log):
    r = [ln for ln in open(log, encoding="utf-8", errors="replace") if ln.startswith("RESULT ")]
    return json.loads(r[-1][7:]) if r else {}


rg, rt = result_of(GLOG), result_of(TLOG)
gate("M0 steps 2-4 passed: graph read {0}, tunnel read {1}".format(rg.get("gates"), rt.get("gates")),
     rg.get("status") == "PASS" and rg["gates"]["fail"] == 0 and rt.get("status") == "PASS" and rt["gates"]["fail"] == 0, (rg, rt))
gate("M1 memory_model.json md5 ff0fabca", L.md5(MM).startswith("ff0fabca"), L.md5(MM))
mem = [(i, ln.rstrip()) for i, ln in enumerate(open(GLOG, encoding="utf-8", errors="replace"), 1) if "MEM after load:" in ln]
val = float(re.search(r"MEM after load: ([\d.]+) MB private", mem[0][1]).group(1)) if len(mem) == 1 else None
gate("M2 one `MEM after load` line in diag_c165_a3_4_graph.log", len(mem) == 1 and val is not None, mem)
am = L.md5(FINAL)
print("FACT P5 final md5 {0}; MEM line {1}".format(am, mem), flush=True)
old = json.load(open(MM, encoding="utf-8"))
gate("M3 the P5 final md5 {0} (pin 75773b0d) is not yet a load_by_vi key".format(am), am.startswith("75773b0d") and am not in old["load_by_vi"])
if gate.G["fail"] == 0:
    new = json.load(open(MM, encoding="utf-8"))
    new["load_by_vi"][am] = {"value": val, "vi": "claudeDev\\D1_ring_p5_20261010_172913.vi (P5 FINAL = byte copy of the P5-2 step 5 ADOPTED "
                             "scratch work copy D1_ring_p5s02e_20261010_172913.vi, card 165-3-4; close-out read card 166-a1-1, PD403(b))",
                             "cite": "tools/bench/diag_c165_a3_4_graph.log:{0} (MEM after load: {1} MB private)".format(mem[0][0], val)}
    ok, _o = J.rewrite_json(MM, new, MMB)
    gate("M4 memory_model.json written in its old layout and line ending (backup {0})".format(os.path.basename(MMB)), ok)
    if ok:
        a, b = json.load(open(MMB, encoding="utf-8")), json.load(open(MM, encoding="utf-8"))
        keys = sorted(set(b["load_by_vi"]) ^ set(a["load_by_vi"]))
        same = all(a["load_by_vi"][k] == b["load_by_vi"][k] for k in a["load_by_vi"])
        top = J.changed_keys(a, b)
        gate("M5 JSON compare: only load_by_vi differs, by exactly the one new key; old keys equal; fail_above_mb 680.0",
             top == ["load_by_vi"] and keys == [am] and same and b["fail_above_mb"]["value"] == 680.0, (top, keys, same, b["fail_above_mb"]))
        print("FACT memory_model {0} -> {1}; new key {2} = {3}".format(L.md5(MMB), L.md5(MM), am, json.dumps(b["load_by_vi"][am])), flush=True)
else:
    print("FACT a precondition failed: memory_model.json NOT written", flush=True)
sys.exit(gate.result([{"path": "tools/bench/memory_model.json", "md5": L.md5(MM)}]))
