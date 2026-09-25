"""Card 88-3: offline re-verdict of the L2-A1 bed's saved Error List read with the new explicit expected file, plus the
PD194(c) graph-placement dry check. NO LabVIEW, no GUI.

Prior art (checked before writing): errorlist_check.reverdict() / find_reusable() (tools/errorlist_check.py:183-242,
card 81-1) already do the offline re-judgement; stage_prerun.find_graph() (tools/stage_prerun.py:112-127) already
searches tools/bench/sim/*/ (cycle-87 firefighter). This file only calls them and prints the gates.

PREDICTION CONTRACT:
  G1 WIRE_CLASSES no longer holds 'isnotconnectedtoanything' / 'zerosources'; holds exactly the 4 pre-87 classes
  G2 find_reusable(bed, 51d9b8a3...) returns the 001456 read (35 raw items)
  G3 reverdict with errorlist_expected_D1_l2_a1_20260925_235224.json -> verdict OK, extra 0, missing 0
  G4 every explicit entry used exactly its count (sum 35); every plan-derived licence used 0
  G5 find_graph('6cf5b077...') returns tools/bench/sim/l2a1/graph_k_80_owners.json (no --graph)
  G6 the bed md5 file on disk is not read or touched (nothing opened under claudeDev)
"""
import json, os, re, sys

TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(TOOLS, "bench")
sys.path.insert(0, TOOLS)
import errorlist_check as EC                                                        # noqa: E402
import stage_prerun as SP                                                           # noqa: E402
import protocol                                                                     # noqa: E402

BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_a1_20260925_235224.vi"
BED_MD5 = "51d9b8a3af5b4240cdc2ad193d9b4f41"
EXP = os.path.join(BENCH, "errorlist_expected_D1_l2_a1_20260925_235224.json")
GRAPH_PREFIX = "6cf5b077"

P, F, first = 0, 0, None


def gate(label, ok, detail=""):
    global P, F, first
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)
    if ok:
        P += 1
    else:
        F += 1
        first = first or label


gate("G1 WIRE_CLASSES reverted to the 4 pre-87 classes",
     tuple(EC.WIRE_CLASSES) == ("wirehaslooseends", "hasnosource", "outputlooptunneltoaninput",
                                "twoterminalsofdifferenttypes"), EC.WIRE_CLASSES)

main_json, raw_json, why = EC.find_reusable(BED, BED_MD5, BENCH)
gate("G2 reusable read found (001456)", bool(main_json) and "20260926_001456" in (main_json or ""), main_json or why)

exp = json.load(open(EXP, encoding="utf-8"))
print("  FACT  expected file md5 %s, %d entries, sum count %d" % (
    EC.md5(EXP), len(exp["expected"]), sum(e["count"] for e in exp["expected"])))
out = None
if main_json:
    verdict, out = EC.reverdict(BED, main_json, raw_json, BENCH, None, EXP)
    R = json.load(open(out, encoding="utf-8"))
    gate("G3 verdict OK, 0 extra, 0 missing", verdict == "OK" and not R["extra"] and not R["missing"],
         "verdict %s extra %d missing %d -> %s" % (verdict, len(R["extra"]), len(R["missing"]), out))
    for x in R["extra"]:
        print("  FACT  EXTRA %r" % x)
    for x in R["missing"]:
        print("  FACT  MISSING %r" % x)
    use = R["licence_usage"]
    expl = [u for u in use if u["kind"] == "explicit"]
    der = [u for u in use if u["kind"] not in ("explicit", "header_of_next")]
    for u, e in zip(expl, exp["expected"]):
        print("  FACT  explicit used %d/%d  %s" % (u["used"], e["count"], e["label"]))
    ok4 = (len(expl) == len(exp["expected"]) and all(u["used"] == e["count"] for u, e in zip(expl, exp["expected"]))
           and sum(u["used"] for u in expl) == 35 and all(u["used"] == 0 for u in der))
    gate("G4 each explicit entry used exactly its count (35), plan-derived licences 0", ok4,
         "derived %s" % [(u["kind"], u["used"]) for u in der])
else:
    gate("G3 verdict OK, 0 extra, 0 missing", False, "no read to re-judge")
    gate("G4 usage", False, "no read")

full = None
gp = os.path.join(BENCH, "sim", "l2a1", "graph_k_80_owners.json")
m = re.search(r'"md5"\s*:\s*"([0-9a-f]{32})"', open(gp, encoding="utf-8", errors="replace").read(800))
full = m.group(1) if m else None
print("  FACT  graph_k_80_owners.json header md5 %s" % full)
found = SP.find_graph(full) if full else None
gate("G5 find_graph(%s...) without --graph -> sim/l2a1/graph_k_80_owners.json" % GRAPH_PREFIX,
     bool(full and full.startswith(GRAPH_PREFIX) and found and os.path.normcase(found) == os.path.normcase(gp)),
     found)
gate("G6 no LabVIEW: labview modules not imported", not any(k in sys.modules for k in ("pythoncom", "win32com")),
     sorted(k for k in sys.modules if k.startswith(("pythoncom", "win32com"))))

print("=== GATES: %d pass / %d fail" % (P, F))
arts = [{"path": os.path.relpath(p, os.path.dirname(TOOLS)).replace("\\", "/"), "md5": EC.md5(p)}
        for p in (EXP, out) if p and os.path.exists(p)]
print(protocol.result_line(protocol.make_result(P, F, first, arts)))
