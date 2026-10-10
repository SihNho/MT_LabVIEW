# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c164_a3_7_ident.log
# ---
r"""prep_c164_a3_7_write - card 164-3-7 (OFFLINE, files only, no LabVIEW): brief_164-3-7.md step 3 (a)+(b) and step 5, ONLY when the identity
re-check tools/bench/prep_c164_a3_7_ident.log ended `STRUCTURAL CONDITION HOLDS` and RESULT PASS.
(a) memory_model.json load_by_vi gets ONE key = hashlib md5 of the adopted file claudeDev\D1_ring_p5s02d_20261010_152518.vi, value from the
    graph read's `MEM after load: X MB private` line (found by search in diag_c164_a3_5_graph.log, expected line 24), entry format of the
    existing entries {value, vi, cite}; JSON compare old vs new: only that key differs, fail_above_mb 680.0.
(b) plan_ring_p5s02d_pred.json `census` = the scratch's MEASURED new-object census, parsed by the shared stagekit.scratch_census (expected
    line 223 of diag_c164_p5s02d_scratch.log, == its _sum.json); `census_overall` MEASURED-SCRATCH, `census_source` cites the log and the graph
    reads; nothing else changes (same keys as prep_c163_a2_2_census.py wrote for step 3).
Byte copies of both files before the write: tools/bench/diag_c164_a3_7_{memory_model,pred}_before.json. Hashes: prep_c156_a1_1_lib.md5.
Each file is written only if its serialisation round-trips the old bytes exactly (so no other line moves).
PREDICTION: W0..W9 PASS; memory_model 8fb432e4 -> new, pred 87a65b89 -> new; every VI pin equal before and after.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a3_7_write.log -- py -u tools/bench/prep_c164_a3_7_write.py"""
import json
import os
import re
import shutil
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stagekit as K  # noqa: E402
import prep_c156_a1_1_lib as L  # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
ADOPTED = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi")
ORIG = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
VIS = [(os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"), "eb1d0f31"), (os.path.join(CD, "D1_ring_p5s01_20261009_124542.vi"), "7f2582ae"),
       (os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"), "94ffff94"), (os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"), "f9ae7751"),
       (os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"), "564d8cbe"), (ADOPTED, "6dcd5c3d"), (ORIG, "2a78e17c")]
MM, PRED, PLAN = os.path.join(B, "memory_model.json"), os.path.join(B, "plan_ring_p5s02d_pred.json"), os.path.join(B, "plan_ring_p5s02d.json")
IDLOG, GLOG = os.path.join(B, "prep_c164_a3_7_ident.log"), os.path.join(B, "diag_c164_a3_5_graph.log")
SLOG, SJ = os.path.join(B, "diag_c164_p5s02d_scratch.log"), os.path.join(B, "diag_c164_p5s02d_scratch_sum.json")
MMB, PRB = os.path.join(B, "diag_c164_a3_7_memory_model_before.json"), os.path.join(B, "diag_c164_a3_7_pred_before.json")
gate = L.Gate(fatal_default=False)


def pins(tag):
    ok = True
    for p, pin in VIS:
        m = L.md5(p)
        ok = ok and m.startswith(pin)
        print("FACT PIN {0} {1} md5 {2} vs {3} {4}".format(tag, os.path.basename(p), m, pin, "equal" if m.startswith(pin) else "UNEQUAL"), flush=True)
    return ok


def dumps(obj, like):
    """the serialisation that reproduces `like` (bytes of the old file), or None."""
    for kw in ({"indent": 1}, {"indent": 1, "ensure_ascii": False}):
        for tail in ("", "\n"):
            if (json.dumps(json.loads(like), **kw) + tail) == like:
                return json.dumps(obj, **kw) + tail
    return None


gate("W0 every VI pin equal BEFORE (5 in-between files, adopted 6dcd5c3d, original 2a78e17c)", pins("BEFORE"))
idl = open(IDLOG, encoding="utf-8").read()
gate("W1 identity re-check: STRUCTURAL CONDITION HOLDS and RESULT PASS 12/0 in prep_c164_a3_7_ident.log",
     "FACT STRUCTURAL CONDITION HOLDS" in idl and '"status":"PASS","gates":{"pass":12,"fail":0}' in idl)
gate("W2 inputs: memory_model 8fb432e4, pred 87a65b89, plan 97837e2a", L.md5(MM).startswith("8fb432e4") and L.md5(PRED).startswith("87a65b89")
     and L.md5(PLAN).startswith("97837e2a"), (L.md5(MM), L.md5(PRED), L.md5(PLAN)))
mem = [(i, ln.rstrip()) for i, ln in enumerate(open(GLOG, encoding="utf-8", errors="replace"), 1) if "MEM after load:" in ln]
val = float(re.search(r"MEM after load: ([\d.]+) MB private", mem[0][1]).group(1)) if len(mem) == 1 else None
gate("W3 one `MEM after load` line in diag_c164_a3_5_graph.log (line 24, 603.9)", len(mem) == 1 and mem[0][0] == 24 and val == 603.9, mem)
meas, ln_no, seg0 = K.scratch_census(SLOG, SJ)
gate("W4 scratch census = the ONE CENSUS-ALL new-uids line (223) of the last segment == _sum.json (stagekit.scratch_census)", ln_no == 223, (ln_no, seg0, meas))
am = L.md5(ADOPTED)
mm_old_txt, pr_old_txt = open(MM, encoding="utf-8").read(), open(PRED, encoding="utf-8").read()
mm_old, pr_old = json.loads(mm_old_txt), json.loads(pr_old_txt)
NL = dict((p, "\r\n" if b"\r\n" in open(p, "rb").read() else "\n") for p in (MM, PRED))
print("FACT line endings {0}".format(dict((os.path.basename(k), repr(v)) for k, v in NL.items())), flush=True)
go = gate.G["fail"] == 0 and am.startswith("6dcd5c3d")          # W0-W4 all PASS, adopted md5 pinned
if go:
    shutil.copyfile(MM, MMB)
    shutil.copyfile(PRED, PRB)
    mm_new = json.loads(mm_old_txt)
    gate("W5 the adopted md5 {0} is not yet a load_by_vi key".format(am), am not in mm_new["load_by_vi"])
    mm_new["load_by_vi"][am] = {"value": val, "vi": "claudeDev\\D1_ring_p5s02d_20261010_152518.vi (P5-2 step 4 ADOPTED in-between file = the scratch "
                                "work copy, card 164-3-5; adopted after the identity re-check of card 164-3-7, prep_c164_a3_7_ident.log)",
                                "cite": "tools/bench/diag_c164_a3_5_graph.log:24 (MEM after load: 603.9 MB private)"}
    t1 = dumps(mm_new, mm_old_txt)
    pr_new = json.loads(pr_old_txt)
    prev = {"census": pr_new.get("census"), "census_overall": pr_new.get("census_overall")}
    pr_new["census"] = dict(sorted(meas.items()))
    pr_new["census_overall"] = "MEASURED-SCRATCH"
    pr_new["census_source"] = {"card": "164-3-7", "decided": "brief_164-3-7.md step 3(b): the step-4 scratch census is recorded into the pred after "
                               "the identity re-check (prep_c164_a3_7_ident.log STRUCTURAL CONDITION HOLDS); CEN2 stays an equality",
                               "log": "tools/bench/diag_c164_p5s02d_scratch.log", "line": ln_no, "segment_from": seg0, "log_md5": L.md5(SLOG),
                               "net_line": 222, "expect": "CENSUS-ALL new uids by class (every class)",
                               "graph_reads": ["tools/bench/diag_c164_a3_5_graph.log:304-314", "tools/bench/diag_c164_a3_5_reads.log",
                                               "tools/bench/prep_c164_a3_7_ident.log"],
                               "what": "stagekit.census_gate counts NEW uids per class (after - before); re-used uids (23501, 23481) are not new",
                               "previous": prev}
    t2 = dumps(pr_new, pr_old_txt)
    gate("W6 both files' serialisation round-trips their old bytes (no other line moves)", t1 is not None and t2 is not None, (t1 is None, t2 is None))
    if t1 is not None and t2 is not None and am not in mm_old["load_by_vi"]:
        open(MM, "w", encoding="utf-8", newline=NL[MM]).write(t1)          # the old file's line ending (both CRLF, run 1 wrote LF)
        open(PRED, "w", encoding="utf-8", newline=NL[PRED]).write(t2)
        a, b = K.jload(MMB), K.jload(MM)
        top = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
        keys = sorted(set(b["load_by_vi"]) ^ set(a["load_by_vi"]))
        same = all(a["load_by_vi"][k] == b["load_by_vi"][k] for k in a["load_by_vi"])
        gate("W7 memory_model compare: only load_by_vi differs, by exactly the one new key; old keys equal; fail_above_mb 680.0",
             top == ["load_by_vi"] and keys == [am] and same and b["fail_above_mb"]["value"] == 680.0, (top, keys, same, b["fail_above_mb"]["value"]))
        c, d = K.jload(PRB), K.jload(PRED)
        ch = sorted(k for k in set(c) | set(d) if c.get(k) != d.get(k))
        gate("W8 pred compare: only census / census_overall / census_source differ; census == measured; plan md5 key unchanged",
             ch == ["census", "census_overall", "census_source"] and d["census"] == meas and d["plan"]["md5"] == L.md5(PLAN), ch)
        nb = [open(p, "rb").read() for p in (MMB, MM, PRB, PRED)]
        gate("W8b both files keep the old line ending, no bare LF (bytes)", all((b"\r\n" in x) == (NL[MM] == "\r\n") and x.count(b"\n") == x.count(b"\r\n")
                                                                            for x in nb[:2]) and all(x.count(b"\n") == x.count(b"\r\n") for x in nb[2:])
             if NL[MM] == NL[PRED] == "\r\n" else True, [(x.count(b"\n"), x.count(b"\r\n")) for x in nb])
        print("FACT memory_model {0} -> {1}; pred {2} -> {3}; new key {4} value {5}; census {6}".format(
            L.md5(MMB), L.md5(MM), L.md5(PRB), L.md5(PRED), am, val, json.dumps(meas, sort_keys=True)), flush=True)
else:
    print("FACT condition or input pin not met: NEITHER file written", flush=True)
gate("W9 every VI pin equal AFTER", pins("AFTER"))
sys.exit(gate.result([{"path": "tools/bench/memory_model.json", "md5": L.md5(MM)}, {"path": "tools/bench/plan_ring_p5s02d_pred.json", "md5": L.md5(PRED)}]))
