# ---
# labview: none
# hardware: none
# ---
"""Card 164-3-3 (read-only, offline): how a wire removed by `delete_wire` is represented in stagesim END graphs and in
the REAL graphs read after a stage was adopted.

Found before writing: stagesim.wire_rows / termless_wire / md5_file / _j (tools/stagesim.py:215-225,617-625) are the
shared readers; no shared "Wire object present" function exists (the same expression sits inline in termless_wire
:625 and sourceless_wire :637), so the one expression below is the only local logic.

Prediction contract:
  P1 plan_ring_p5s02d.json md5 725cd68e and plan_ring_p5s02r_in.json md5 9dadb0c1, before AND after (2 gates each).
  P2 every plan below loads; every delete_wire action has an integer wire_uid (gate per plan).
  P3 for each delete_wire wire: sim end-graph rows count + Wire object y/n from finalized.last_step (printed, no gate on
     the value - this is a measurement); real graph rows + object y/n in every graph_ring_* file of the chain.
Writes nothing but its log (stdout).
"""
import json, os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import stagesim as S
import protocol

ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
PINS = {"tools/bench/plan_ring_p5s02d.json": "725cd68e", "tools/bench/plan_ring_p5s02r_in.json": "9dadb0c1"}
PLANS = ["plan_ring_p4_s01", "plan_ring_p4_s02", "plan_ring_p4_s02v18", "plan_ring_p4_s03v18", "plan_ring_p4_s04v18",
         "plan_ring_p4_s05v18", "plan_ring_p4_s06v18", "plan_ring_p4_s07v18", "plan_ring_p4_s08v18", "plan_ring_p4_s09v18",
         "plan_ring_p5s01", "plan_ring_p5s01a", "plan_ring_p5s01b", "plan_ring_p5s02a", "plan_ring_p5s02b",
         "plan_ring_p5s02c", "plan_ring_p5s02d"]
P, F = [0], [0]


def gate(ok, label):
    print("GATE", "PASS" if ok else "FAIL", "|", label)
    (P if ok else F)[0] += 1


def pins(tag):
    for p, m in PINS.items():
        got = S.md5_file(os.path.join(ROOT, p))
        gate(got.startswith(m), "{0} {1} md5 {2} == {3}".format(tag, p, got[:8], m))


def has_wire_obj(st, w):
    return any(int(o["uid"]) == w and o.get("class") == "Wire" for o in st["objs"])


def line_of(path, needle):
    with open(path, encoding="utf-8") as f:
        for i, ln in enumerate(f, 1):
            if needle in ln:
                return i
    return 0


def rows_txt(st, w):
    rs = S.wire_rows(st, w)
    return len(rs), ",".join("t{0}{1}#{2}".format(r["term_uid"], "S" if r["is_source"] else "", r["owner_uid"]) for r in rs)


pins("BEFORE")
graphs = sorted(g for g in glob.glob(os.path.join(ROOT, "tools/bench/graph_ring_p[45]s*.json")) if "fsowner" not in g)
G = {}
for g in graphs:
    rel = S._rel(g)
    d = S._j(g)
    G[rel] = (S.md5_file(g), d)
    print("GRAPH", rel, G[rel][0][:8], "src", json.dumps(d.get("source"))[:160], "vi", json.dumps(d.get("vi"))[:120])
for name in PLANS:
    path = os.path.join(ROOT, "tools/bench", name + ".json")
    if not os.path.exists(path):
        print("PLAN", name, "MISSING")
        continue
    p = S._j(path)
    fin = p.get("finalized") or {}
    base = (fin.get("base") or p.get("base") or {}).get("path")
    last = (fin.get("last_step") or {}).get("path")
    print("PLAN", name, S.md5_file(path)[:8], "base", base, "last_step", last, "at", fin.get("at"), "final", p.get("final"))
    dws = [a for a in p.get("actions", []) if a.get("op") == "delete_wire"]
    gate(all(isinstance(a.get("wire_uid"), int) for a in dws), "{0}: {1} delete_wire, all int wire_uid".format(name, len(dws)))
    st = S._j(os.path.join(ROOT, last))["state"] if last and os.path.exists(os.path.join(ROOT, last)) else None
    bst = G.get(base, (None, None))[1]
    for a in dws:
        w = a["wire_uid"]
        ln = line_of(path, '"id": "{0}"'.format(a["id"]))
        print("DW", name, a["id"], "w{0}".format(w), "{0}:{1}".format(S._rel(path), ln))
        if bst is not None:
            n, t = rows_txt(bst, w)
            print("  BASE", base, "rows", n, t, "obj", "Y" if has_wire_obj(bst, w) else "N")
        if st is not None:
            n, t = rows_txt(st, w)
            print("  SIMEND", last, "rows", n, t, "obj", "Y" if has_wire_obj(st, w) else "N")
        else:
            print("  SIMEND none (no finalized.last_step on disk)")
        for rel, (m, d) in G.items():
            n, t = rows_txt(d, w)
            o = has_wire_obj(d, w)
            if n or o:
                print("  REAL", rel, m[:8], "rows", n, t, "obj", "Y" if o else "N")
        print("  REAL-ABSENT-IN", ",".join(os.path.basename(r)[11:-21] for r, (m, d) in G.items()
                                             if not S.wire_rows(d, w) and not has_wire_obj(d, w)))
pins("AFTER")
print(protocol.result_line({"status": "PASS" if not F[0] else "FAIL", "gates": {"pass": P[0], "fail": F[0]},
                            "first_fail": None, "artefacts": []}))
