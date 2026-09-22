# -*- coding: utf-8 -*-
"""M3a-4 STEP 1 ADDENDUM: close the SEVERED-WIRE COUNT. 19 wired ends -> 12 wires -> 11 removed.

TOUCHES NO LabVIEW: plain file reads only; no COM, no gscript, no stagekit, no claudeDev.
PRIOR ART CHECKED, deliberately NOT rebuilt: `tools/bench/diag_c90_severed_rows.py` +
`tools/bench/m3a1_severed_rows.json` + `docs/m3a1-severed-rows.md` already deliver the 11-row
table (commit 3b95af8). None of them names the TWELFTH severed wire or closes the count, which is
what the next stage needs to know how many rows it owes. Nothing in those three is rewritten here.
PREDICTION CONTRACT
 P1 the last BGRUN block's seven `move_in` calls sever 19 wired ends, 0 left wired.
 P2 `[2c]` declares 7 internal rows, both ends of each among the seven moved nodes -> 14 ends.
 P3 the other 5 ends are the terminals still BARE at `[4]`'s first tables: #48 t3,t4 / #10407 t1,t4,t6.
 P4 the pre-move census gives those 5 the uids {1731,3947,9635,7337,9113}: 4 removed, 9113 NOT.
 P5 `[5b]`'s readback `UID 2` is 9113, a uid PRE-EXISTING in that census (the wire was RE-SOURCED),
    while `[5]`'s readback is absent from it (a NEW wire), so the old inner wire stayed broken.
 P6 so 7+5=12 severed, 1 repaired, 12-1 == 11 == the removed set, which equals the 11 already on disk.
"""
import io, json, re, sys                                                             # noqa: E401
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
BENCH = Path(__file__).resolve().parents[2] / "tools" / "bench"
LOG = BENCH / "build_d1_m3a1.log"
REMOVED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
gates = []


def gate(ok, label, detail=""):
    gates.append((ok, label))
    print(("  PASS  " if ok else "  FAIL  ") + label + ("  " + detail if detail else ""))


log = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
lo = [i for i, t in enumerate(log) if t.startswith("BGRUN START")][-1]
print("[A] %s: %d lines, delivering block starts at :%d" % (LOG.name, len(log), lo + 1))

# P1 -- the 19 severed wired ends
RE_BEF = re.compile(r"\[2b\] #(\d+) '(.*?)' BEFORE the move: (\d+) terminal\(s\), (\d+) WIRED")
RE_AFT = re.compile(r"\[2b\] #(\d+) AFTER the move: (\d+) terminal\(s\), (\d+) WIRED \(was (\d+)\)")
before, after, order = {}, {}, []
for i in range(lo, len(log)):
    m = RE_BEF.search(log[i])
    if m:
        order.append(int(m.group(1)))
        before[order[-1]] = (m.group(2), int(m.group(4)), i + 1)
    m = RE_AFT.search(log[i])
    if m:
        after[int(m.group(1))] = (int(m.group(3)), i + 1)
ends, left = sum(v[1] for v in before.values()), sum(v[0] for v in after.values())
print("[A] seven moved nodes %s ; wired ends severed %d ; still wired %d" % (order, ends, left))
gate(len(order) == 7 and ends == 19 and left == 0, "P1 seven moves sever 19 wired ends, 0 remain",
     "moves=%d ends=%d left=%d" % (len(order), ends, left))

# P2 -- the seven internal rows
internal = [{"sink_uid": int(m.group(1)), "sink_t": int(m.group(2)), "src_uid": int(m.group(3)),
             "src_t": int(m.group(4)), "line": i + 1}
            for i in range(lo, len(log))
            for m in [re.search(r"\[2c\] row #(\d+) t(\d+) <- #(\d+) t(\d+) : \{", log[i])] if m]
both = [r for r in internal if r["sink_uid"] in order and r["src_uid"] in order]
for r in internal:
    print("      :%d  #%d t%d <- #%d t%d" % (r["line"], r["sink_uid"], r["sink_t"], r["src_uid"], r["src_t"]))
gate(len(internal) == 7 and len(both) == 7, "P2 7 internal rows, both ends moved -> 14 of the 19 ends",
     "internal=%d both=%d" % (len(internal), len(both)))

# P3 -- the 5 external ends = terminals still BARE at [4]'s FIRST table per node
RE_T4 = re.compile(r"FACT\s+\[4\] (?:VISA RightIn|VISA LeftIn) #(\d+) t(\d+)\s+'(.*?)'\s+is_source=(\w+)\s+wire=(\d+)")
bare, done = {}, set()
for i in range(lo, len(log)):
    m = RE_T4.search(log[i])
    if m and (int(m.group(1)), int(m.group(2))) not in done:
        done.add((int(m.group(1)), int(m.group(2))))
        if int(m.group(5)) == 0:
            bare.setdefault(int(m.group(1)), {})[int(m.group(2))] = (m.group(3), m.group(4) == "True", i + 1)
ext = sorted((u, t) for u in bare for t in bare[u])
print("[C] BARE at [4]: %s" % ["#%d t%d '%s' :%d" % (u, t, bare[u][t][0], bare[u][t][2]) for u, t in ext])
gate(set(ext) == {(48, 3), (48, 4), (10407, 1), (10407, 4), (10407, 6)},
     "P3 exactly 5 external ends: #48 t3,t4 and #10407 t1,t4,t6", str(ext))

# P4/P5 -- the pre-move census, and which severed wire the stage re-sourced
cen = json.loads((BENCH / "main_vi_nodeterms.json").read_text(encoding="utf-8", errors="replace"))


def walk(o):
    if isinstance(o, dict):
        if "tree_uid" in o and isinstance(o.get("terms"), list):
            yield o
        for v in o.values():
            for x in walk(v):
                yield x
    elif isinstance(o, list):
        for v in o:
            for x in walk(v):
                yield x


pre, allw = {}, set()
for n in walk(cen):
    for t in n["terms"]:
        allw.add(t.get("wire"))
        pre[(n["tree_uid"], t.get("i"))] = (t.get("wire"), t.get("name"), t.get("is_source"))
extw = {k: pre.get(k, (None, None, None)) for k in ext}
for (u, t), v in sorted(extw.items()):
    print("[D] pre-move #%d t%d '%s' carried wire %s -> %s"
          % (u, t, v[1], v[0], "removed" if v[0] in REMOVED else "NOT removed"))
inrem = sorted(v[0] for v in extw.values() if v[0] in REMOVED)
notrem = [v[0] for v in extw.values() if v[0] not in REMOVED]
gate(len(inrem) == 4 and notrem == [9113], "P4 4 of the 5 external wires are removed; the odd one is 9113",
     "in=%s out=%s" % (inrem, notrem))
cfw = {}
for i in range(lo, len(log)):
    m = re.search(r"\[(5b?)\] connect_from_wire\(wire=(\d+).*?'UID 2': (\d+)", log[i])
    if m:
        cfw[m.group(1)] = (int(m.group(2)), int(m.group(3)), i + 1)
for k in sorted(cfw):
    print("[E] [%s] connect_from_wire(wire=%d) -> UID 2 = %d (:%d) : %s"
          % (k, cfw[k][0], cfw[k][1], cfw[k][2], "PRE-EXISTING -> RE-SOURCED" if cfw[k][1] in allw else "NEW wire"))
gate(cfw.get("5b", (0, 0, 0))[1] == 9113 and 9113 in allw and cfw.get("5", (0, 0, 0))[1] not in allw,
     "P5 [5b] re-sourced pre-existing wire 9113; [5] minted a new wire",
     "5b=%s 5=%s" % (cfw.get("5b", (0, 0, 0))[1], cfw.get("5", (0, 0, 0))[1]))

# P6 -- the arithmetic closes, and matches the table already on disk
severed = len(both) + len(ext)
prows = sorted(r["wire_uid"] for r in json.loads(
    (BENCH / "m3a1_severed_rows.json").read_text(encoding="utf-8", errors="replace"))["rows"])
print("[F] %d internal + %d external = %d severed ; repaired by [5b] = 1 (w9113) ; %d - 1 = %d"
      % (len(both), len(ext), severed, severed, severed - 1))
gate(severed - 1 == len(REMOVED) == 11, "P6a 12 severed - 1 repaired == 11 removed", "%d-1" % severed)
gate(prows == sorted(REMOVED) and 9113 not in prows,
     "P6b m3a1_severed_rows.json's 11 rows == the removed set, and exclude 9113", str(prows))

OUT = BENCH / "m3a1_severed_arith.json"
OUT.write_text(json.dumps({
    "source_log": str(LOG), "delivering_block_first_line": lo + 1,
    "moved_nodes": [{"uid": u, "label": before[u][0], "wired_before": before[u][1],
                     "wired_after": after[u][0], "before_line": before[u][2]} for u in order],
    "wired_ends_severed": ends, "internal_rows": internal,
    "external_ends": [{"node_uid": u, "terminal": t, "name": extw[(u, t)][1], "is_source": extw[(u, t)][2],
                       "pre_move_wire": extw[(u, t)][0], "removed": extw[(u, t)][0] in REMOVED,
                       "bare_line": bare[u][t][2], "census": "tools/bench/main_vi_nodeterms.json"} for u, t in ext],
    "repaired_wire": {"wire_uid": 9113, "row": "[5b]", "line": cfw.get("5b", (0, 0, 0))[2],
                      "note": "severed with #10407 t6, RE-SOURCED from new LoopTunnel #24018; never removed"},
    "arithmetic": {"wired_ends": ends, "internal_wires": len(both), "external_wires": len(ext),
                   "severed_wires": severed, "repaired": 1, "removed": severed - 1},
    "removed_set": REMOVED}, indent=1, ensure_ascii=False), encoding="utf-8")
print("[G] WROTE %s (%d B)" % (OUT, OUT.stat().st_size))
nf = [l for ok, l in gates if not ok]
print("GATE: %d pass / %d fail%s" % (len(gates) - len(nf), len(nf), ("; failing: " + " | ".join(nf)) if nf else ""))
sys.exit(1 if nf else 0)
