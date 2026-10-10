# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-c3-1.md
# ---
r"""prep_c160_c3_1_licence - card 160-c3-1 (OFFLINE, json only): plan_ring_p5s02b_licence.json for P5-2 step 2 (plan_ring_p5s02b.json f4520b10,
md5 read from the session table prep_c160_b3_1_session.json). Flow of prep_c156_a1_1_licence.py (43e40d7b, a top-level script: importing it runs it,
so it is not imported); Gate from prep_c156_a1_1_lib.Gate; licence read-back by stagekit.licence_renames; X11 by stage_prerun.buildarray_open_sibling
/ pb_licences. Rule unchanged (PD365(d)): rename_by_uid = one entry per node X11 flags; renames = every BASE sink terminal an action wires BY TERM
UID, from/to unset; ZERO ALLOWED. The rename-table block below is the 156 licence's lines 49-60 (OPEN: copied; no shared function holds it).
PREDICTION CONTRACT: L0 plan md5 == session table's; X11 flags == the --buildarray-check log (prep_c160_c3_1_x11.log: CLEAN, 0 flags); R every term
uid a base sink of its owner; W licence_renames reads back the same keys; X11 after: every flag licensed (0 == 0).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c160_c3_1_licence.log -- py -u tools/bench/prep_c160_c3_1_licence.py"""
import collections, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import stage_prerun as SPR                                                                  # noqa: E402
import stagekit as K                                                                        # noqa: E402  licence_renames (shared)
import stage_shared as SH                                                                   # noqa: E402  base_sink_renames (card 162-a2-3)
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate (shared)
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
PLAN = os.path.join(B, "plan_ring_p5s02b.json")
LIC = os.path.join(B, "plan_ring_p5s02b_licence.json")
X11LOG = os.path.join(B, "prep_c160_c3_1_x11.log")
SESS = os.path.join(B, "prep_c160_b3_1_session.json")
gate = L.Gate(width=1200)
gate("L0 plan md5 == session table's {0}".format(J(SESS)["plan"]["md5"][:8]), md5(PLAN) == J(SESS)["plan"]["md5"], md5(PLAN))
X11L = open(X11LOG, encoding="utf-8", errors="replace").read().splitlines()
X11FLAGS = [ln for ln in X11L if ln.startswith("FLAG ")]
X11CLEAN = any(ln.startswith("CLEAN ") for ln in X11L)
print("FACT X11 log {0} md5 {1}: CLEAN {2}, FLAG lines {3}".format(rel(X11LOG), md5(X11LOG), X11CLEAN, X11FLAGS), flush=True)
P = J(PLAN)
BASE = J(P["finalized"]["base"]["path"])
bt = dict((int(r["term_uid"]), r) for r in BASE["terminals"])
x11 = SPR.buildarray_open_sibling(P, licences={})
print("FACT X11 (licences ignored) flags {0}".format(x11), flush=True)
nodes = sorted(set(int(f["node"]) for f in x11))
gate("X11 flags node(s) {0} == the --buildarray-check log ({1} FLAG line(s), CLEAN {2})".format(nodes, len(X11FLAGS), X11CLEAN),
     len(x11) == len(X11FLAGS) and (X11CLEAN == (not x11)) and all(("row " + f["row"] + " ") in " ".join(X11FLAGS) for f in x11), x11)
A = P["actions"]
rbu = []
for n in nodes:
    rows = [f["row"] for f in x11 if int(f["node"]) == n]
    tus = sorted(set(int(a["dst"]["term_uid"]) for a in A if a.get("id") in rows and isinstance(a.get("dst"), dict) and a["dst"].get("term_uid") is not None))
    rbu.append({"node": n, "term_uids": tus, "require": "every listed uid is an input of #{0} in the real end read with the same uid, unwired unless this session wires it".format(n),
                "why": "X11 flags row(s) {0} on #{1} (PD365(d)); read from the plan, not typed".format(rows, n)})
ren, own, wr = SH.base_sink_renames(A, bt, "PD365(d) (chat-T6 rule, applied to P5-2 step 2 by card 160-c3-1): BASE sink terminal(s) of #{0} wired by P5-2 row(s) {1}; "
                                           "from/to unset")   # card 162-a2-3: tools/stage_shared.py, was a copied block
print("FACT renames {0} entr(y/ies), {1} term uid(s), owners {2}".format(len(ren), sum(len(e["term_uids"]) for e in ren), sorted(own)), flush=True)
for e in ren:
    print("FACT  rename node #{0} term_uids {1} rows {2} names {3}".format(e["node"], e["term_uids"], wr[e["node"]], [bt[u]["term_name"] for u in e["term_uids"]]), flush=True)
gate("R renames ({0}; ZERO ALLOWED); every term uid a base SINK of its owner".format(len(ren)),
     all(not bt[u].get("is_source") and (int(bt[u]["owner_uid"]) == e["node"]) for e in ren for u in e["term_uids"]), ren)
lic = {"schema": "pb-licence/1", "stage": "ring_p5s02b", "plan": rel(PLAN),
       "decided_by": "docs/d1/ring-p4c.md PD365(d) and PD366(g), applied to P5-2 step 2 (docs/d1/ring-p5b.md PD390(c), PD391) by card 160-c3-1: rename_by_uid "
                     "where X11 flags a row; renames = every BASE sink terminal a P5-2 step-2 row wires BY TERM UID, from/to unset; written by "
                     "tools/bench/prep_c160_c3_1_licence.py, never typed",
       "why_a_file": "decision 8 / stage_prerun X6: a recipe never re-types a uid; the licence cannot be a field of the plan (form of plan_ring_p5s02a_licence.json)",
       "precedent": "tools/bench/plan_ring_p5s02a_licence.json (card 156-a1-1)", "source_plan_md5": md5(PLAN), "rename_by_uid": rbu, "renames": ren}
json.dump(lic, open(LIC, "w", encoding="utf-8"), indent=1)
back = K.licence_renames(J(LIC))
want = dict(((u, e["node"]), (None, None)) for e in ren for u in e["term_uids"])
gate("W licence_renames reads back {0} keys == script's".format(len(back or {})), back == want, back)
x11b = SPR.buildarray_open_sibling(P, licences=SPR.pb_licences(PLAN))
gate("X11 after: every flag ({0}) licensed".format(len(x11b)), len(x11b) == len(x11) and all(f["licensed"] for f in x11b), x11b)
print("FACT md5 {0} {1}".format(md5(LIC), rel(LIC)), flush=True)
sys.exit(gate.result([{"path": rel(LIC), "md5": md5(LIC)}]))
