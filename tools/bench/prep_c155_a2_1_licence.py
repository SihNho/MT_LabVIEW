# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_155-a2-1.md
# ---
r"""prep_c155_a2_1_licence - card 155-a2-1 (OFFLINE). COPY of prep_c154_a3_2b_licence.py (0c045f1e) with ONLY: plan / licence P5-1a -> P5-1b
(plan_ring_p5s01b.json, md5 read from the session table prep_c155_a2_1_session.json); X11 log prep_c155_a2_1_x11.log; the base = finalized.base
(the real P5-1a graph bd67a511); card / stage strings; the local copy of licence_renames replaced by the shared stagekit.licence_renames (the
function it was copied from). Rule unchanged (PD365(d)): rename_by_uid = one entry per node X11 flags; renames = every BASE sink terminal an
action wires BY TERM UID (dst a dict with term_uid), from/to unset; ZERO ALLOWED; name-form and symbolic dsts are printed only.
PREDICTION CONTRACT: L0 plan md5 == session table's; X11 flags == the --buildarray-check log; R every term uid a base sink; W licence_renames reads
back the same keys; X11 after: every flag licensed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c155_a2_1_licence.log -- py -u tools/bench/prep_c155_a2_1_licence.py"""
import collections, hashlib, json, os, sys                                                 # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_shared as SH                                                                   # noqa: E402  base_sink_renames (card 162-a2-3)
from tools import protocol  # noqa: E402
import stage_prerun as SPR                                                                  # noqa: E402
import stagekit as K                                                                        # noqa: E402  licence_renames (shared)
B = os.path.join(ROOT, "tools", "bench")
PLAN = os.path.join(B, "plan_ring_p5s01b.json")
LIC = os.path.join(B, "plan_ring_p5s01b_licence.json")
X11LOG = os.path.join(B, "prep_c155_a2_1_x11.log")
SESS = os.path.join(B, "prep_c155_a2_1_session.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1200]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
        sys.exit(1)


gate("L0 plan md5 == session table's {0}".format(J(SESS)["plan"]["md5"][:8]), md5(PLAN) == J(SESS)["plan"]["md5"], md5(PLAN))
X11FLAGS = [ln for ln in open(X11LOG, encoding="utf-8", errors="replace").read().splitlines() if ln.startswith("FLAG ")]
X11CLEAN = any(ln.startswith("CLEAN ") for ln in open(X11LOG, encoding="utf-8", errors="replace").read().splitlines())
print("FACT X11 log {0} md5 {1}: CLEAN {2}, FLAG lines {3}".format(rel(X11LOG), md5(X11LOG), X11CLEAN, X11FLAGS), flush=True)
P = J(PLAN)
BASE = J(P["finalized"]["base"]["path"])
bt = dict((int(r["term_uid"]), r) for r in BASE["terminals"])
x11 = SPR.buildarray_open_sibling(P, licences={})
print("FACT X11 (licences ignored) flags {0}".format(x11), flush=True)
nodes = sorted(set(int(f["node"]) for f in x11))
gate("X11 flags node(s) {0} rows {1} == the --buildarray-check log ({2} FLAG line(s), CLEAN {3})".format(nodes, [f["row"] for f in x11], len(X11FLAGS), X11CLEAN),
     len(x11) == len(X11FLAGS) and (X11CLEAN == (not x11)) and all(("row " + f["row"] + " ") in " ".join(X11FLAGS) for f in x11), x11)
A = P["actions"]
rbu = []
for n in nodes:
    rows = [f["row"] for f in x11 if int(f["node"]) == n]
    tus = sorted(set(int(a["dst"]["term_uid"]) for a in A if a.get("id") in rows and isinstance(a.get("dst"), dict) and a["dst"].get("term_uid") is not None))
    rbu.append({"node": n, "term_uids": tus,
                "require": "every listed uid is an input of #{0} in the real end read with the same uid, unwired unless this session wires it, else the licence is void".format(n),
                "why": "X11 (stage_prerun.buildarray_open_sibling) flags row(s) {0} on #{1} (PD365(d)); read by this script from the plan, not typed".format(rows, n)})
ren, own, wr = SH.base_sink_renames(A, bt, "PD365(d) (chat-T6 rule, applied to P5-1b by card 155-a2-1): BASE sink terminal(s) of #{0} wired by P5-1b row(s) {1}; from/to unset = any name "
                                           "(stagekit.licence_renames)")   # card 162-a2-3: shared, was a copied block
print("FACT renames {0} entr(y/ies), {1} term uid(s), owners {2}".format(len(ren), sum(len(e["term_uids"]) for e in ren), sorted(own)), flush=True)
for e in ren:
    print("FACT  rename node #{0} term_uids {1} rows {2} names {3}".format(e["node"], e["term_uids"], wr[e["node"]], [bt[u]["term_name"] for u in e["term_uids"]]), flush=True)
for a in A:
    d_ = a.get("dst")
    if str(a.get("op")).lower() in ("wire", "tunnel") and d_ is not None and not (isinstance(d_, dict) and d_.get("term_uid") is not None):
        print("FACT NON-UID dst row {0} ({1}): {2!r} - not in the copied rule (dst term_uid only)".format(a["id"], a["op"], d_), flush=True)
gate("R renames == the copied rule's entries ({0}; ZERO ALLOWED); every term uid a base SINK of its owner".format(len(ren)),
     all(not bt[u].get("is_source") and int(bt[u]["owner_uid"]) == e["node"] for e in ren for u in e["term_uids"]), ren)
lic = {"schema": "pb-licence/1", "stage": "ring_p5s01b", "plan": rel(PLAN),
       "decided_by": "docs/d1/ring-p4c.md PD365(d) and PD366(g), applied to P5-1b by card 155-a2-1 (brief_155-a2-1.md item 6 / brief_154-a4-1.md item 5): "
                     "rename_by_uid where X11 flags a row; renames = every BASE sink terminal (uid, owner) a P5-1b row wires BY TERM UID, from/to unset; "
                     "written by tools/bench/prep_c155_a2_1_licence.py, never typed",
       "why_a_file": "decision 8 / stage_prerun X6: a recipe never re-types a uid; docs/protocol/stageplan.json has additionalProperties false, so the licence cannot be a "
                     "field of the plan (form copied from tools/bench/plan_ring_p5s01a_licence.json, read by stage_prerun.pb_licences and stagekit.licence_renames)",
       "precedent": "tools/bench/plan_ring_p5s01a_licence.json (card 154-a3-2b)",
       "source_plan_md5": md5(PLAN), "rename_by_uid": rbu, "renames": ren}
json.dump(lic, open(LIC, "w", encoding="utf-8"), indent=1)
back = K.licence_renames(J(LIC))
want = dict(((u, e["node"]), (None, None)) for e in ren for u in e["term_uids"])
gate("W licence written; licence_renames reads back {0} (uid, owner) keys == script's, all (None, None)".format(len(back or {})), back == want, back)
x11b = SPR.buildarray_open_sibling(P, licences=SPR.pb_licences(PLAN))
gate("X11 after: every flag ({0}) licensed by {1}".format(len(x11b), rel(LIC)), len(x11b) == len(x11) and all(f["licensed"] for f in x11b), x11b)
print("FACT md5 {0} {1}".format(md5(LIC), rel(LIC)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": rel(LIC), "md5": md5(LIC)}])), flush=True)
sys.exit(0)
