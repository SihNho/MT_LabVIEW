# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a3_6_licence - card 150-a3-6 step 6 (OFFLINE). COPY of prep_c150_a3_1_licence.py (da47cb38) with ONLY: plan / licence s07 -> s08
(plan_ring_p4_s08v18.json, rebased c328fdaf); gate L0 pins c328fdaf; gate X11 = "X11 flags exactly what --buildarray-check reported" (prep_c150_a3_6_x11.log:
CLEAN, so rename_by_uid may be EMPTY - not invented); X11-after passes on an empty flag list; card id strings. --- original docstring follows ---
prep_c150_a3_1_licence - card 150-a3-1 step 4 (OFFLINE, no LabVIEW). Writes tools/bench/plan_ring_p4_s07v18_licence.json (pb-licence/1, the
form of plan_ring_p4_s06v18_licence.json 7f70bbf9) FROM the rebased plan plan_ring_p4_s07v18.json (08c2ad4d) - nothing typed (PD365(d)):
  rename_by_uid = one entry per node that stage_prerun.buildarray_open_sibling (X11) flags, term_uids = the dst term uids of the flagged rows;
  renames      = every BASE sink terminal (uid, owner) that an s07 `wire` row wires (dst a dict whose term_uid is a non-source row of the plan's
                 finalized base), grouped by owner, from/to UNSET (= any name, tools/stagekit.py:1412-1421).
Existing tools checked: stage_prerun.buildarray_open_sibling / pb_licences (X11 reader), stagekit.licence_renames (TD/PB reader); the s06 licence
was hand-assembled by card 147-a1-3/147-c3-2 - no licence writer exists in tools/ (grep 'pb-licence/1' tools/*.py: readers only).
PREDICTION CONTRACT: L0 plan md5 08c2ad4d; X11 flags exactly one node (#2626, row p4_rbB_sel_t4168 = op 150); R renames >= 1 entry, every
term uid a base sink; W written, licence_renames() reads back the same (uid, owner) set with (None, None); X11 after: every flag licensed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c150_a3_6_licence.log -- py -u tools/bench/prep_c150_a3_6_licence.py"""
import collections, hashlib, json, os, sys                                                 # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stage_shared as SH                                                                   # noqa: E402  base_sink_renames (card 162-a2-3)
from tools import protocol  # noqa: E402
import stage_prerun as SPR                                                                  # noqa: E402
# The real TD/PB reader stagekit.licence_renames is exercised by the MAIN recipe's dry run (REN = K.licence_renames(...)); this offline script
# reads the file back with the same rule (tools/stagekit.py:1412-1421, copied) so it imports no LabVIEW-run module.


class K(object):
    @staticmethod
    def licence_renames(lic):
        if not isinstance(lic, dict) or "renames" not in lic:
            return None
        out = {}
        for e in lic.get("renames") or []:
            for u in e.get("term_uids") or []:
                out[(int(u), int(e["node"]))] = (e.get("from"), e.get("to"))
        return out
B = os.path.join(ROOT, "tools", "bench")
PLAN = os.path.join(B, "plan_ring_p4_s08v18.json")
LIC = os.path.join(B, "plan_ring_p4_s08v18_licence.json")
X11LOG = os.path.join(B, "prep_c150_a3_6_x11.log")
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


gate("L0 plan md5 == c328fdaf (rebased, card 150-a3-6)", md5(PLAN).startswith("c328fdaf"), md5(PLAN))
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
                "why": "X11 (stage_prerun.buildarray_open_sibling) flags row(s) {0} on #{1} wiring {2} while sibling input(s) {3} are open rows at the s08 end (PD365(d), "
                       "PD352(d) extended to the session that carries v18 op 150); read by this script from the rebased plan, not typed".format(
                           rows, n, sorted(set(f["wired"] for f in x11 if int(f["node"]) == n)), sorted(set(o for f in x11 if int(f["node"]) == n for o in f["open"])))})
ren, own, wr = SH.base_sink_renames(A, bt, "PD365(d) (chat-T6 rule, applied to s08 by card 150-a3-5/6): BASE sink terminal(s) of #{0} wired by s08 row(s) {1}; from/to unset = any name "
                                           "(stagekit.licence_renames, tools/stagekit.py:1412-1421)")   # card 162-a2-3: shared, was a copied block
print("FACT renames {0} entr(y/ies), {1} term uid(s), owners {2}".format(len(ren), sum(len(e["term_uids"]) for e in ren), sorted(own)), flush=True)
for e in ren:
    print("FACT  rename node #{0} term_uids {1} rows {2} names {3}".format(e["node"], e["term_uids"], wr[e["node"]], [bt[u]["term_name"] for u in e["term_uids"]]), flush=True)
gate("R renames >= 1 entry; every term uid a base SINK of its owner", bool(ren) and all(not bt[u].get("is_source") and int(bt[u]["owner_uid"]) == e["node"] for e in ren for u in e["term_uids"]), ren)
lic = {"schema": "pb-licence/1", "stage": "ring_p4_s08v18", "plan": rel(PLAN),
       "decided_by": "docs/d1/ring-p4c.md PD365(d) (cycle 150 judgement) and PD366(g), cards 150-a3-5/150-a3-6 step 6: rename_by_uid where X11 flags a row (s08: "
                     "--buildarray-check CLEAN, so none); renames = every BASE sink terminal (uid, owner) an s08 connect row wires, from/to unset; written by "
                     "tools/bench/prep_c150_a3_6_licence.py (card 150-a3-6), never typed",
       "why_a_file": "decision 8 / stage_prerun X6: a recipe never re-types a uid; docs/protocol/stageplan.json has additionalProperties false, so the licence cannot be a "
                     "field of the plan (form copied from tools/bench/plan_ring_p4_s06v18_licence.json, read by stage_prerun.pb_licences and stagekit.licence_renames)",
       "precedent": "tools/bench/plan_ring_p4_s07v18_licence.json (card 150-a3-1); tools/bench/plan_ring_p4_s06v18_licence.json (pb-licence/1, card 147-a1-3 / 147-c3-2)",
       "source_plan_md5": md5(PLAN), "rename_by_uid": rbu, "renames": ren}
json.dump(lic, open(LIC, "w", encoding="utf-8"), indent=1)
back = K.licence_renames(J(LIC))
want = dict(((u, e["node"]), (None, None)) for e in ren for u in e["term_uids"])
gate("W licence written; stagekit.licence_renames reads back {0} (uid, owner) keys == script's, all (None, None)".format(len(back or {})), back == want, back)
x11b = SPR.buildarray_open_sibling(P, licences=SPR.pb_licences(PLAN))
gate("X11 after: every flag ({0}) licensed by {1}".format(len(x11b), rel(LIC)), len(x11b) == len(x11) and all(f["licensed"] for f in x11b), x11b)
print("FACT md5 {0} {1}".format(md5(LIC), rel(LIC)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": rel(LIC), "md5": md5(LIC)}])), flush=True)
sys.exit(0)
