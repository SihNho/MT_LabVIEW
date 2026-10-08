# ---
# labview: none
# hardware: none
# ---
"""Card 153-a2-1: read the ORIGINAL's #376 'frame index' source from the on-disk census (no LabVIEW).

Prior art found: tools/bench/orig_3state_nodeterms.json (vi = Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi,
md5 before/after c39f36e0..., 2026-09-18) is an existing per-terminal census of the TRUE original; S1 side is
docs/wiki/subvi/D1_s1_copy.json:36385-36392 (cited at docs/cycle27-plan.md:3748-3751). No new reader is built.

Prediction contract: (P1) the original census holds node #376 with a terminal 'frame index', is_source False;
(P2) that terminal's wire uid = 3268 (same as S1 w3268); (P3) no Node terminal in the census is a SOURCE of
w3268 (its source is a diagram-owned terminal, as in S1 where it is Terminal #644 owner Diagram #639);
(P4) #5119's 'x-y' output wire != 3268. Gates print per item, then the C6 RESULT line.
"""
import json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

ORIG = os.path.join(ROOT, "tools", "bench", "orig_3state_nodeterms.json")
S1 = os.path.join(ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json")


def load_lines(p):
    raw = open(p, encoding="utf-8").read()
    return json.loads(raw), raw.split("\n")


def line_of(lines, start, needle):
    for i in range(start, len(lines)):
        if needle in lines[i]:
            return i + 1
    return None


d, lines = load_lines(ORIG)
print("ORIG vi:", d.get("vi"), "md5:", d.get("md5"))
gates = []
hits_376, src_3268, sinks_3268, out_5119 = [], [], [], []
for dk, dv in d["diagrams"].items():
    for n in dv["nodes"]:
        for t in n["terms"]:
            row = (dk, dv["owner"], n["uid"], t["i"], t["name"], t["is_source"], t["wire"])
            if n["uid"] == 376:
                hits_376.append(row)
            if t.get("wire") == 3268:
                (src_3268 if t["is_source"] else sinks_3268).append(row)
            if n["uid"] == 5119:
                out_5119.append(row)
for r in hits_376:
    print("ORIG #376:", r)
for r in out_5119:
    print("ORIG #5119:", r)
print("ORIG w3268 node sources:", src_3268)
print("ORIG w3268 node sinks:", sinks_3268)

# file:line of the #376 record and its frame index terminal
ln376 = None
for i, l in enumerate(lines):
    if l.strip() == '"uid": 376,':
        ln376 = i + 1
        break
lnfi = line_of(lines, ln376 or 0, '"name": "frame index"') if ln376 else None
print("ORIG line #376 uid:", ln376, "| 'frame index' term line:", lnfi,
      "| its wire line:", line_of(lines, lnfi or 0, '"wire"') if lnfi else None)

fi = [r for r in hits_376 if r[4] == "frame index"]
gates.append(("P1 #376 has 'frame index' input", len(fi) == 1 and fi[0][5] is False))
gates.append(("P2 'frame index' wire == 3268", len(fi) == 1 and fi[0][6] == 3268))
gates.append(("P3 no Node terminal sources w3268", len(src_3268) == 0))
x_y = [r for r in out_5119 if r[5] is True]
gates.append(("P4 #5119 output wire != 3268", len(x_y) >= 1 and all(r[6] != 3268 for r in x_y)))

# S1 side
s1, s1lines = load_lines(S1)
print("S1 lines 36380-36395:")
for i in range(36379, 36395):
    print(" ", i + 1, s1lines[i].rstrip())

npass = sum(1 for _, ok in gates if ok)
for label, ok in gates:
    print("GATE", "PASS" if ok else "FAIL", label)
first_fail = next((label for label, ok in gates if not ok), None)
print(protocol.result_line({"status": "PASS" if first_fail is None else "FAIL",
                            "gates": {"pass": npass, "fail": len(gates) - npass}, "first_fail": first_fail,
                            "artefacts": []}))
