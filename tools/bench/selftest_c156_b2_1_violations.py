# ---
# labview: none
# hardware: none
# ---
r"""selftest_c156_b2_1_violations - card 156-b2-1 (PD379(g), docs/d1/ring-p5.md:205-206): tools/violations.py DEC_RE and
_stamp read a ten-minute decision header 'HH:Mx' as 'HH:M9'. Before, '## slug — 2026-10-09 12:2x' missed the HH:MM group,
was stamped date-only ('2026-10-09 00:00') and sorted before the retrospective that raised the slug.
OFFLINE: no LabVIEW, no COM; imports tools/violations.py (argparse/re/glob only) and reads docs/violation-decisions.md.
FOUND FIRST: no existing self-test of violations.DEC_RE (grep 'DEC_RE' tools/bench -> none); tools/violations.py is the
one owner of the parse, so this file calls violations.DEC_RE / violations._stamp and does not re-implement them.
PREDICTION (7 gates, 0 fail):
  G1 '## device-failed — 2026-10-09 12:2x' -> ('device-failed','2026-10-09','12:2x'), stamp '2026-10-09 12:29'
  G2 '## wrong-ordering - 2026-10-09 07:0x' -> stamp '2026-10-09 07:09'
  G3 '## scope-creep — 2026-10-09 13:55'     -> stamp '2026-10-09 13:55' (unchanged)
  G4 '## scope-creep — 2026-10-09'           -> stamp '2026-10-09 00:00' (unchanged)
  G5 '2026-10-09T08:4X' (T separator, capital X) -> '2026-10-09 08:49'
  G6 docs/violation-decisions.md: every header the OLD regex matched gets the same stamp from the new parse, except
     headers whose time is 'HH:Mx' (old: date-only)                      -> 0 other differences
  G7 decisions() runs on the real file and returns a non-empty dict"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
sys.path.insert(0, TOOLS)
import protocol  # noqa: E402
import violations as V  # noqa: E402

RES = {"pass": 0, "fail": 0, "first": None}
# The pre-card regex, kept here ONLY as the reference for G6 (the comparison baseline), not used as a parser.
OLD_RE = re.compile(r"^##\s*([a-z0-9-]+)\s*[-—]\s*(\d{4}-\d{2}-\d{2})(?:[ T]+(\d{2}:\d{2}))?", re.M)


def gate(label, ok, detail=""):
    RES["pass" if ok else "fail"] += 1
    if not ok and RES["first"] is None:
        RES["first"] = f"{label}: {detail}"[:200]
    print(f"GATE {label} {'PASS' if ok else 'FAIL'} {detail}")


def stamp_of(line):
    m = V.DEC_RE.findall(line)
    if len(m) != 1:
        return None, m
    slug, date, hhmm = m[0]
    return V._stamp(date, hhmm), m[0]


st, m = stamp_of("## device-failed — 2026-10-09 12:2x\n")
gate("G1", st == "2026-10-09 12:29" and m == ("device-failed", "2026-10-09", "12:2x"), f"{st} {m}")
st, m = stamp_of("## wrong-ordering - 2026-10-09 07:0x\n")
gate("G2", st == "2026-10-09 07:09", f"{st} {m}")
st, m = stamp_of("## scope-creep — 2026-10-09 13:55\n")
gate("G3", st == "2026-10-09 13:55", f"{st} {m}")
st, m = stamp_of("## scope-creep — 2026-10-09\n")
gate("G4", st == "2026-10-09 00:00", f"{st} {m}")
st, m = stamp_of("## scope-creep — 2026-10-09T08:4X\n")
gate("G5", st == "2026-10-09 08:49", f"{st} {m}")

with open(V.DECISIONS, encoding="utf-8", errors="replace") as f:
    body = f.read()
old = OLD_RE.findall(body)
new = V.DEC_RE.findall(body)
diffs, xheaders = [], 0
if len(old) != len(new):
    diffs.append(f"count old {len(old)} new {len(new)}")
for (s0, d0, h0), (s1, d1, h1) in zip(old, new):
    a, b = V._stamp(d0, h0), V._stamp(d1, h1)
    if (s0, d0) != (s1, d1):
        diffs.append(f"{s0}/{d0} vs {s1}/{d1}")
    elif a != b:
        if not h0 and re.fullmatch(r"\d{2}:\d[xX]", h1 or ""):
            xheaders += 1
        else:
            diffs.append(f"{s0} {a} -> {b}")
gate("G6", not diffs, f"headers {len(new)}, HH:Mx headers now timed {xheaders}, other diffs {diffs[:3]}")

dec = V.decisions()
gate("G7", isinstance(dec, dict) and len(dec) > 0, f"{len(dec)} slugs with a decision")

print(protocol.result_line({"status": "PASS" if RES["fail"] == 0 else "FAIL",
                            "gates": {"pass": RES["pass"], "fail": RES["fail"]},
                            "first_fail": RES["first"], "artefacts": []}))
sys.exit(0 if RES["fail"] == 0 else 1)
