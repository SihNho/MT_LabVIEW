# -*- coding: utf-8 -*-
"""M3a-4 STEP 1 (cycle27-plan Pre-decided 131 (1)): the SEVERED-ROW TABLE, derived OFFLINE.

TOUCHES NO LabVIEW: plain file reads only; no COM, no gscript, no stagekit, no claudeDev.
PRIOR ART CHECKED: `docs/toolkit-capabilities.md` has no severed-row reader, `ls tools/bench` no
`*severed*` script; `tools/bench/c53_row_class.py` (the 17 CUT terminals) is READ, not rebuilt.
PREDICTION CONTRACT -- P1 build_d1_m3a1.log holds 5 BGRUN blocks, the LAST the delivering run,
with exactly 7 `[2b] MOVE #` lines. P2 NONE of the 11 removed wire uids appears anywhere in that
log -> every row `unaccounted` with a reason naming what the log lacks. P3 all 11 still get a
NAMED (source -> sink) pair from OTHER on-disk files. P4 all 11 attributed to a move call.
"""
import io, json, re, sys
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
ROOT = Path(__file__).resolve().parents[2]
BENCH = ROOT / "tools" / "bench"
LOG = BENCH / "build_d1_m3a1.log"
UIDS = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
# The four endpoints already read FROM THE MACHINE in cycle 67 (STATUS.md labview-lock
# purpose_dispatch4). Not in any of the files parsed below; carried with their citation.
PRIOR = {1731: ("LeftShiftRegister", 4344, "source"), 3947: ("LeftShiftRegister", 4274, "source"),
         9635: ("LoopTunnel", 9641, "source"), 7337: ("RightShiftRegister", 4334, "sink")}
PRIOR_SRC = "STATUS.md labview-lock purpose_dispatch4 (cycle-67 material dispatch 4 machine read)"
gates = []
def gate(ok, label, detail=""):
    gates.append((ok, label)); print(("  PASS  " if ok else "  FAIL  ") + label + ("  " + detail if detail else ""))

log = LOG.read_text(encoding="utf-8", errors="replace").splitlines()
starts = [i for i, t in enumerate(log) if t.startswith("BGRUN START")]
lo = starts[-1]
print("[A] %s : %d lines, %d BGRUN blocks, last block starts at :%d" % (LOG.name, len(log), len(starts), lo + 1))
gate(len(starts) == 5, "P1a build_d1_m3a1.log holds 5 BGRUN blocks", "got %d" % len(starts))

# --- the seven move_in calls of the last block -------------------------------------------
RE_BEF = re.compile(r"\[2b\] #(\d+) '(.*)' BEFORE the move: (\d+) terminal\(s\), (\d+) WIRED\s+\((.*?)[;)]")
RE_MOV = re.compile(r"\[2b\] MOVE #(\d+) '(.*?)' -> Diagram #(\d+)")
RE_AFT = re.compile(r"\[2b\] #(\d+) AFTER the move: (\d+) terminal\(s\), (\d+) WIRED \(was (\d+)\)")
moves, order = {}, []
for i in range(lo, len(log)):
    m = RE_BEF.search(log[i])
    if m:
        order.append(int(m.group(1)))
        moves[order[-1]] = {"node_uid": order[-1], "label": m.group(2), "node_class": m.group(5),
                            "terms_before": int(m.group(3)), "wired_before": int(m.group(4)),
                            "before_line": i + 1, "move_line": None, "after_line": None, "wired_after": None}
    for rx, k, v in ((RE_MOV, "move_line", None), (RE_AFT, "after_line", 3)):
        m = rx.search(log[i])
        if m and int(m.group(1)) in moves:
            moves[int(m.group(1))][k] = i + 1
            if v:
                moves[int(m.group(1))]["wired_after"] = int(m.group(v))
gate(len(order) == 7, "P1b the last block holds exactly 7 move_in calls", str(order))
for d in (moves[u] for u in order):
    print("      MOVE #%-6d %-28s %-26s %d WIRED -> %s  (:%d BEFORE, :%d MOVE, :%d AFTER)"
          % (d["node_uid"], d["label"][:28], d["node_class"][:26], d["wired_before"], d["wired_after"],
             d["before_line"], d["move_line"], d["after_line"]))
print("[A] wired terminals severed by the seven moves: %d ; wired AFTER, summed: %d"
      % (sum(moves[u]["wired_before"] for u in order), sum(moves[u]["wired_after"] for u in order)))
hits = {u: [i + 1 for i, t in enumerate(log) if re.search(r"(?<![0-9])%d(?![0-9])" % u, t)] for u in UIDS}
tot = sum(len(v) for v in hits.values())
gate(tot == 0, "P2 none of the 11 removed wire uids appears anywhere in build_d1_m3a1.log", "total hits %d" % tot)
print("[B] the log DOES print wire uids on %d lines - all POST-move ([4]/[5]/[6] censuses of the NEW wires)"
      % sum(1 for t in log if re.search(r"wire=[1-9][0-9]*", t)))

# --- crossref 1: tools/bench/c53_row_class.log, the 17 CUT terminals ----------------------
C53 = BENCH / "c53_row_class.log"
c53 = C53.read_text(encoding="utf-8", errors="replace").splitlines()
RE_ROW = re.compile(r"^(\d+)\s+(\d+)\s+(.*?)\s+(sink|SRC)\s+(\S+)\s+(\d+)\s+(\d+)\s*$")
cut = {}
for i, t in enumerate(c53):
    m = RE_ROW.match(t)
    if m:
        cut.setdefault(int(m.group(6)), []).append(
            {"node_uid": int(m.group(1)), "terminal": int(m.group(2)), "name": m.group(3).strip().strip("'"),
             "is_source": m.group(4) == "SRC", "action": m.group(5), "src": "tools/bench/c53_row_class.log:%d" % (i + 1)})
print("[C] c53_row_class.log: %d distinct cut-wire uids, %d of the 11" % (len(cut), len([u for u in UIDS if u in cut])))

# --- crossref 2: tools/bench/build_d1_m3a1.json, the seven planned internal rows ----------
jt = (BENCH / "build_d1_m3a1.json").read_text(encoding="utf-8", errors="replace")
RE_J = re.compile(r'"sink_uid":\s*(\d+),\s*"sink_name":\s*"(.*?)",\s*"sink_t_recorded":\s*(\d+),\s*'
                  r'"src_uid":\s*(\d+),\s*"src_name":\s*"(.*?)",\s*"src_t_recorded":\s*(\d+),\s*"evidence":\s*"(.*?)"', re.S)
rows = {}
for m in RE_J.finditer(jt):
    w = re.search(r"w(\d+)|wire (\d+)", m.group(7))
    if w:
        f = "tools/bench/build_d1_m3a1.json:%d" % (jt[:m.start()].count("\n") + 1)
        rows[int(w.group(1) or w.group(2))] = [
            {"node_uid": int(m.group(4)), "terminal": int(m.group(6)), "name": m.group(5), "is_source": True,
             "action": "planned internal row", "src": f, "evidence": m.group(7)},
            {"node_uid": int(m.group(1)), "terminal": int(m.group(3)), "name": m.group(2), "is_source": False,
             "action": "planned internal row", "src": f, "evidence": m.group(7)}]
print("[D] build_d1_m3a1.json: %d planned rows carry a wire uid, %d of the 11" % (len(rows), len([u for u in UIDS if u in rows])))

# --- assemble ----------------------------------------------------------------------------
REASON = ("build_d1_m3a1.log never prints a wire uid before the seven move_in calls: its [2b] BEFORE/AFTER lines "
          "record only per-node terminal counts (e.g. :%d '1 terminal(s), 1 WIRED'), and every wire= column in the "
          "file belongs to the POST-move [4]/[5]/[6] censuses of the NEW wires.")
out, named, attributed = [], 0, 0
for u in UIDS:
    ends = list(cut.get(u, [])) + rows.get(u, [])
    if u in PRIOR:
        c, uid, side = PRIOR[u]
        ends.append({"node_uid": uid, "owner_class": c, "terminal": None, "name": None,
                     "is_source": side == "source", "action": "machine read, cycle 67", "src": PRIOR_SRC})
    seen = {}  # one row per (owner, terminal, side); every citing file kept in `src`
    for e in ends:
        k = (e["node_uid"], e["terminal"], e["is_source"])
        h = seen.get(k)
        seen[k] = dict(e) if not h else dict(h, src=h["src"] + ("" if e["src"] in h["src"] else " ; " + e["src"]))
    ends = list(seen.values())
    mv = next((mu for mu in order if mu in [e["node_uid"] for e in ends]), None)
    nm = any(e["is_source"] for e in ends) and any(not e["is_source"] for e in ends)
    named += bool(nm); attributed += bool(mv)
    out.append({"wire_uid": u, "status": "accounted" if hits[u] else "unaccounted",
                "reason": None if hits[u] else REASON % moves[order[0]]["before_line"],
                "log_lines_in_build_d1_m3a1": hits[u], "crossref_named": bool(nm),
                "severing_move": None if not mv else dict(moves[mv]), "endpoints": ends})
gate(named == 11, "P3 all 11 get a named (source -> sink) pair from other on-disk files", "named %d/11" % named)
gate(attributed == 11, "P4 all 11 attributed to one of the seven move calls", "attributed %d/11" % attributed)
for r in out:
    s = r["severing_move"] or {}
    print("  w%-6d %-12s severed by MOVE #%s '%s' (:%s)\n           %s"
          % (r["wire_uid"], r["status"], s.get("node_uid"), s.get("label"), s.get("move_line"),
             " / ".join("%s#%d t%s '%s'%s" % (e.get("owner_class", "Node"), e["node_uid"], e["terminal"],
                                              e["name"] or "", " SRC" if e["is_source"] else "") for e in r["endpoints"])))
OUT = BENCH / "m3a1_severed_rows.json"
OUT.write_text(json.dumps({"source_log": str(LOG), "last_block_first_line": lo + 1, "moves": [moves[u] for u in order],
                           "uids": UIDS, "rows": out}, indent=1, ensure_ascii=False), encoding="utf-8")
print("[E] WROTE %s (%d B)" % (OUT, OUT.stat().st_size))
nf = [l for ok, l in gates if not ok]
print("GATE: %d pass / %d fail%s" % (len(gates) - len(nf), len(nf), ("; failing: " + " | ".join(nf)) if nf else ""))
