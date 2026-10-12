# ---
# labview: none
# hardware: none
# evidence: tools/bench/graph_ring_p5s02d_20261010_154830.json
# ---
r"""selftest_c166_ident - card 166-a1-6 (OFFLINE, no LabVIEW): self-test of the NODE IDENTITY block of tools/stagekit.py (node_ident,
ident_matches, deleted_nodes_by_ident, e5_check, row_uid_reused; term_identity_pos's new `uid_reused`), on stored graph reads only.
Found before writing: the identity code existed only in tools/bench/prep_c164_a3_7_ident.py ident()/matches() (moved to stagekit unchanged);
the E5 test existed only inline in the graph-read diags (diag_c141_3 .. diag_c165_a3_4 _graph.py `e5 = {...}`, e.g. diag_c164_a3_5_graph.py:63-70),
now stagekit.e5_check; the reuse detectors are stagekit.term_identity_pos reuse_noted (deleted WIRE uids) / recycled (position keys).
PREDICTION CONTRACT:
  P1-P3 step 4 (base graph_ring_p5s02c 3d5196ab, adopted graph_ring_p5s02d 2a5fa0c4, plan diag_c164_a3_5_graph_plan.json): node_ident of
     #23042 / #23501 == the prep_c164_a3_7_ident.log IDENT base tuples; I1 #23501 identity GONE, I2 #23042 identity GONE; e5_check(base)
     ok, deleted_nodes_present [], uid_reused == [#23501 LoopTunnel -> ParameterTerminal]; e5_check without base (old uid rule) ==
     the stored E5 FAIL (deleted_nodes_present [23501], diag_c164_a3_5_graph.log:305).
  P4 row_uid_reused(p5s02c rows, p5s02d rows) holds 23501 and 23481 (fp-88); term_identity_pairs(...)['uid_reused'] the same list.
  N1 a planted survivor (adopted copy + an object of #23501's base identity under uid 99923501, its rows copied) -> PRESENT, survivors
     {23501: [99923501]}, e5 ok False; N2 the same for #23042 (Comparison on 23405 at its base pos) -> PRESENT; N3 #23501 kept as a
     LoopTunnel moved elsewhere (same uid, same class) -> PRESENT (stricter only); N4 a rename-only real row -> no uid_reused entry;
     a term moved to another owner -> one entry.
  S  stricter only over every stored graph-read pair whose E5 ran (chain base = the previous step's graph): the old rule recomputed ==
     the stored E5 line's deleted_nodes_present; no old-PASS becomes BLOCK (a newly BLOCKED row is printed as RETURN); the only old-BLOCK
     that becomes PASS is a uid whose class changed (uid_reused) - listed; the other E5 parts equal.
  F  stored inputs unchanged (md5).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c166_ident.log -- py -u tools/bench/selftest_c166_ident.py"""
import copy
import hashlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K  # noqa: E402
import protocol  # noqa: E402

G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def J(name):
    return K.jload(HERE, name)


PINS = {"graph_ring_p5s02c_20261010_131658.json": "3d5196ab", "graph_ring_p5s02d_20261010_154830.json": "2a5fa0c4"}
before = dict((f, md5(os.path.join(HERE, f))) for f in PINS)
gate("F0 stored step-4 graphs == their pins", all(before[f].startswith(p) for f, p in PINS.items()), before)
GB, GA = J("graph_ring_p5s02c_20261010_131658.json"), J("graph_ring_p5s02d_20261010_154830.json")
ED = J("diag_c164_a3_5_graph_plan.json")["edits"]
O0, T0, W0 = K._graph_parts(GB)
O1, T1, W1 = K._graph_parts(GA)

# ---------------------------------------------------------------- P: step 4
want = {23042: ("Comparison", "Diagram", 23405, (15713, 30518)), 23501: ("LoopTunnel", "WhileLoop", 23041, (15675, 11867))}
got = dict((u, K.node_ident(u, O0, T0, W0)) for u in want)
gate("P1 node_ident on the base == prep_c164_a3_7_ident.log IDENT tuples (#23042, #23501)", got == want, got)
d = K.deleted_nodes_by_ident(ED["deleted_nodes"], GB, GA)
print("  FACT deleted_nodes_by_ident step 4: {0}".format(d), flush=True)
gate("I1 #23501 identity GONE in the adopted graph (uid 23501 now another node -> uid_reused)", 23501 in d["gone"] and 23501 not in d["present"]
     and [x["uid"] for x in d["uid_reused"]] == [23501], d["uid_reused"])
gate("I2 #23042 identity GONE in the adopted graph", 23042 in d["gone"] and 23042 not in d["present"], d["gone"])
e_new = K.e5_check(ED, GA, GB)
e_old = K.e5_check(ED, GA)
print("  FACT e5_check new: {0}".format(e_new), flush=True)
print("  FACT e5_check old (no base, uid rule): {0}".format(e_old), flush=True)
gate("P2 e5_check(base) ok, deleted_nodes_present [], uid_reused #23501 LoopTunnel -> ParameterTerminal", e_new["ok"] and e_new["deleted_nodes_present"] == []
     and e_new["uid_reused"][0]["base"][0] == "LoopTunnel" and e_new["uid_reused"][0]["after"][0] == "ParameterTerminal", e_new["uid_reused"])
gate("P3 e5_check without base == the stored E5 FAIL (deleted_nodes_present [23501], diag_c164_a3_5_graph.log:305)",
     (not e_old["ok"]) and e_old["deleted_nodes_present"] == [23501], e_old["deleted_nodes_present"])
ru = K.row_uid_reused(T0, T1)
print("  FACT row_uid_reused step 4: {0} entries: {1}".format(len(ru), ru), flush=True)
sim_end = J(os.path.join("sim", "ring_p5s02d", "step_19_wire.json"))["state"]["terminals"]
tp = K.term_identity_pairs(T0, sim_end, T1, bind={})
gate("P4 row_uid_reused(p5s02c, p5s02d) holds 23501 (LoopTunnel node -> term of #12170) and 23481 (term of #23042 -> term of #12170); "
     "term_identity_pairs carries the same list", {23501, 23481} <= set(x["uid"] for x in ru) and tp["uid_reused"] == ru,
     [x["uid"] for x in ru])

# ---------------------------------------------------------------- N: planted cases
def plant(G0, src_uid, new_uid, base_G, pos=None):
    g = copy.deepcopy(G0)
    o = dict((int(x["uid"]), x) for x in base_G["objs"])[src_uid]
    g["objs"].append(dict(o, uid=new_uid, pos=list(pos or o["pos"])))
    for i, r in enumerate(r for r in base_G["terminals"] if int(r.get("owner_uid") or 0) == src_uid):
        g["terminals"].append(dict(r, owner_uid=new_uid, term_uid=new_uid * 10 + i, wire_uid=0))
    return g


GN1 = plant(GA, 23501, 99923501, GB)
n1 = K.e5_check(ED, GN1, GB)
gate("N1 planted survivor of #23501 (LoopTunnel, While 23041, base pos) under uid 99923501 -> CAUGHT: present [23501], survivors, ok False",
     n1["deleted_nodes_present"] == [23501] and n1["survivors"] == {23501: [99923501]} and not n1["ok"], (n1["deleted_nodes_present"], n1["survivors"]))
GN2 = plant(GA, 23042, 99923042, GB)
n2 = K.e5_check(ED, GN2, GB)
gate("N2 planted survivor of #23042 (Comparison on 23405, base pos) under uid 99923042 -> CAUGHT", n2["deleted_nodes_present"] == [23042]
     and n2["survivors"] == {23042: [99923042]} and not n2["ok"], (n2["deleted_nodes_present"], n2["survivors"]))
GN3 = copy.deepcopy(GA)
for o in GN3["objs"]:
    if int(o["uid"]) == 23501:
        o.update({"class": "LoopTunnel", "owner": "WhileLoop", "pos": [1, 2]})
n3 = K.e5_check(ED, GN3, GB)
gate("N3 uid 23501 still a LoopTunnel at another pos (same uid, same class) -> PRESENT (stricter only)", n3["deleted_nodes_present"] == [23501] and not n3["ok"],
     n3["deleted_nodes_present"])
r4 = [dict(r, term_name="renamed") if int(r["term_uid"]) == 31736 else r for r in T1]
r4b = [dict(r, owner_uid=12169, owner_class="Local") if int(r["term_uid"]) == 31736 else r for r in T1]   # run 1: owner_class left 'Comparison' -> 12169 also listed
a4, b4 = K.row_uid_reused(T1, r4), K.row_uid_reused(T1, r4b)
gate("N4 rename-only row -> no uid_reused entry; term 31736 moved to owner 12169 -> one entry", a4 == [] and [x["uid"] for x in b4] == [31736], (a4, b4))

# ---------------------------------------------------------------- S: stricter only over the stored E5 pairs
CHAIN = [("diag_c143_1", "graph_ring_p4s02_20261003_112505.json", "graph_ring_p4s01_20261002_234419.json"),
         ("diag_c144_2", "graph_ring_p4s03_20261007_205535.json", "graph_ring_p4s02_20261003_112505.json"),
         ("diag_c145_2", "graph_ring_p4s04_20261007_223245.json", "graph_ring_p4s03_20261007_205535.json"),
         ("diag_c147_a1_1", "graph_ring_p4s05_20261008_013759.json", "graph_ring_p4s04_20261007_223245.json"),
         ("diag_c149_a3_2", "graph_ring_p4s06_20261008_192149.json", "graph_ring_p4s05_20261008_013759.json"),
         ("diag_c150_a3_2", "graph_ring_p4s07_20261008_224835.json", "graph_ring_p4s06_20261008_192149.json"),
         ("diag_c151_a1_1", "graph_ring_p4s08_20261009_033522.json", "graph_ring_p4s07_20261008_224835.json"),
         ("diag_c152_b3_1", "graph_ring_p4s09_20261009_062044.json", "graph_ring_p4s08_20261009_033522.json"),
         ("diag_c154_a3_3", "graph_ring_p5s01a_20261009_103621.json", "graph_ring_p4s09_20261009_062044.json"),
         ("diag_c155_a3_2", "graph_ring_p5s01_20261009_125622.json", "graph_ring_p5s01a_20261009_103621.json"),
         ("diag_c158_a3_2b", "graph_ring_p5s02a_20261010_032547.json", "graph_ring_p5s01_20261009_125622.json"),
         ("diag_c162_a1_2", "graph_ring_p5s02b_20261010_111905.json", "graph_ring_p5s02a_20261010_032547.json"),
         ("diag_c163_a2_2", "graph_ring_p5s02c_20261010_131658.json", "graph_ring_p5s02b_20261010_111905.json"),
         ("diag_c164_a3_5", "graph_ring_p5s02d_20261010_154830.json", "graph_ring_p5s02c_20261010_131658.json"),
         ("diag_c165_a3_4", "graph_ring_p5s02e_20261012_173009.json", "graph_ring_p5s02d_20261010_154830.json")]
print("  FACT not scored: diag_c141_3 (graph_ring_p4s01) - no stored graph read of its base file", flush=True)
cache = {}
s_rows, newly_blocked, freed = [], [], []
for diag, ga, gb in CHAIN:
    for f in (ga, gb):
        cache.setdefault(f, J(f))
    ed = J(diag + "_graph_plan.json")["edits"]
    line = [(i, x) for i, x in enumerate(open(os.path.join(HERE, diag + "_graph.log"), encoding="utf-8", errors="replace"), 1)
            if re.match(r"\s+(PASS|FAIL)\s+E5 ", x)]
    stored = re.search(r"'deleted_nodes_present': \[([^\]]*)\]", line[0][1]) if line else None
    stored_dn = [int(x) for x in stored.group(1).split(",") if x.strip()] if stored else None
    old, new = K.e5_check(ed, cache[ga]), K.e5_check(ed, cache[ga], cache[gb])
    same_rest = all(old[k] == new[k] for k in ("made", "deleted_wires_present", "new_wires_missing"))
    row = (diag, line[0][0] if line else None, line[0][1].split()[0] if line else None, stored_dn, old["deleted_nodes_present"],
           new["deleted_nodes_present"], [x["uid"] for x in new["uid_reused"]], old["ok"], new["ok"])
    s_rows.append(row)
    print("  S {0} log:{1} stored {2} dn_present {3} | old {4} | new {5} uid_reused {6} | ok old {7} new {8}".format(*row), flush=True)
    gate("S1 {0}: old rule recomputed == stored E5 deleted_nodes_present; made / wires parts old == new".format(diag),
         stored_dn == old["deleted_nodes_present"] and same_rest, (stored_dn, old["deleted_nodes_present"], same_rest))
    if old["ok"] and not new["ok"]:
        newly_blocked.append((diag, ga, new["deleted_nodes_present"], new["survivors"]))
    if not old["ok"] and new["ok"]:
        freed.append((diag, sorted(set(old["deleted_nodes_present"]) - set(new["deleted_nodes_present"])), new["uid_reused"]))
for x in newly_blocked:
    print("  RETURN newly BLOCKED adopted row: diag {0} graph {1} uid {2} survivors {3}".format(*x), flush=True)
gate("S2 no stored E5 that passed is BLOCKED by the identity rule", not newly_blocked, newly_blocked)
ok_free = all(set(u) == set(r["uid"] for r in ru_) and all(r["base"][0] != r["after"][0] for r in ru_) for _d, u, ru_ in freed)
gate("S3 every old-BLOCK that now passes is a uid whose class changed (uid_reused), listed: {0}".format([(f[0], f[1]) for f in freed]),
     ok_free and [f[0] for f in freed] == ["diag_c164_a3_5"], freed)
after = dict((f, md5(os.path.join(HERE, f))) for f in PINS)
gate("F1 stored inputs unchanged", after == before, after)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(0 if not G["fail"] else 1)
