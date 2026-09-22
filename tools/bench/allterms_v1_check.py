r"""allterms_v1_check - FUNCTIONAL acceptance of `OpAllTerms_v1.vi` (structural was allterms_v1.log 45/1).

PREDICTION CONTRACT
  F1 v1 returns the SAME six columns as v0 on the D1 bed: 5,811 rows, identical term_uid/term_name/
     is_source/wire_uid/owner_uid/owner_class row for row (it is v0's build plus two nodes).
  F2 the seventh column `frame_diagram` is NON-ZERO on the 1,036 rows whose owner class carries
     Inner/Frame - the OPEN-B question `allterms_s4.log` could not answer.
  F3 frame_diagram values resolve to real objects: each one appears in `report_all(bed,'Diagram')`.
  F4 the wire join is unchanged: 1,913 termed + 7 termless = 1,920, severed == the 11 known uids.
  H  the bed, the ORIGINAL and v0 are byte-unchanged; no VI is run except the op itself.
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import allterms as A                                                               # noqa: E402
import bench_prep                                                                  # noqa: E402

BED = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
V0 = os.path.join(g.CLAUDEDEV, "OpAllTerms_v0.vi")
V1 = os.path.join(g.CLAUDEDEV, "OpAllTerms_v1.vi")
BED_JSON = os.path.join(HERE, "allterms_bed_20260923.json")
OUT = os.path.join(HERE, "allterms_v1_check.json")
EXPECT = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
P, F, REC = [0], [0], {}


def gate(label, ok, detail=""):
    (P if ok else F)[0] += 1
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def fact(line):
    print("  FACT  {0}".format(line), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


pins = dict((p, md5(p)) for p in (BED, V0, g.ORIGINAL))
fact("handles at start {0}".format(bench_prep.labview_handles()))
fact("v1 md5 {0} size {1}".format(md5(V1), os.path.getsize(V1)))

rows, dt = A.read_terms(BED, op=V1)
fact("v1 on the bed: {0} rows in {1:.2f} s, columns {2}".format(
    len(rows), dt, sorted(rows[0]) if rows else []))
gate("F1a 5,811 rows", len(rows) == 5811, str(len(rows)))
gate("F1b the seventh column is present", bool(rows) and "frame_diagram" in rows[0], "")

base = json.load(open(BED_JSON, encoding="utf-8"))["terminals"]
six = ("term_uid", "term_name", "is_source", "wire_uid", "owner_uid", "owner_class")
b = dict((r["term_uid"], tuple(r[f] for f in six)) for r in base)
n1 = dict((r["term_uid"], tuple(r[f] for f in six)) for r in rows)
diff = [u for u in b if b[u] != n1.get(u)]
gate("F1c v1's six columns are IDENTICAL to v0's, row for row", not diff and len(b) == len(n1),
     "{0} differing term_uid(s) {1}".format(len(diff), diff[:5]))

inner = [r for r in rows if "Inner" in r["owner_class"] or "Frame" in r["owner_class"]]
nz = [r for r in inner if r["frame_diagram"]]
fact("inner/frame rows {0}; of those frame_diagram != 0: {1}; sample {2}".format(
    len(inner), len(nz), [(r["term_uid"], r["owner_class"], r["frame_diagram"]) for r in inner[:5]]))
gate("F2 frame_diagram is non-zero on every inner/frame row", len(inner) and len(nz) == len(inner),
     "{0} of {1}".format(len(nz), len(inner)))

diags = set(int(o["uid"]) for o in g.report_all(BED, "Diagram"))
vals = set(r["frame_diagram"] for r in rows if r["frame_diagram"])
fact("distinct frame_diagram values {0}; Diagram objects on the bed {1}; not a Diagram: {2}".format(
    len(vals), len(diags), sorted(vals - diags)[:8]))
gate("F3 every frame_diagram value IS a Diagram object on the bed", vals and not (vals - diags),
     "{0} value(s), {1} stray".format(len(vals), len(vals - diags)))

uids, dtw = A.all_wire_uids(BED)
wires = A.join_wires(rows, uids)
sev = sorted(w["wire_uid"] for w in A.severed(wires))
termed = sum(1 for w in wires if not w["termless"])
gate("F4 join unchanged: 1913 termed + 7 termless, severed == the 11",
     len(uids) == 1920 and termed == 1913 and sev == EXPECT,
     "{0} uids / {1} termed / severed {2}".format(len(uids), termed, sev))

REC.update({"v1_md5": md5(V1), "rows": len(rows), "seconds": round(dt, 2),
            "inner_rows": len(inner), "inner_nonzero": len(nz),
            "distinct_frame_diagrams": len(vals), "bed_diagrams": len(diags),
            "wire_uids": len(uids), "termed": termed, "severed": sev,
            "wire_traverse_s": round(dtw, 2)})
after = dict((p, md5(p)) for p in pins)
gate("H every pinned file is byte-unchanged", after == pins,
     str([os.path.basename(p) for p in pins if after[p] != pins[p]]))
fact("gscript ref_counts {0}".format(g.ref_counts()))
fact("handles at end {0}".format(bench_prep.labview_handles()))
json.dump(REC, open(OUT, "w", encoding="utf-8"), indent=1)
print("\n=== GATES: {0} pass / {1} fail   JSON {2}".format(P[0], F[0], OUT), flush=True)
sys.exit(1 if F[0] else 0)
