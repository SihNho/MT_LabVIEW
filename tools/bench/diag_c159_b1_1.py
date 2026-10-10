# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_159-b1-1.md
# ---
r"""Card 159-b1-1 (docs/d1/ring-p5b.md PD388(a)(b)): OFFLINE, no LabVIEW, no COM.
 1. the item-by-item expected Error List of base 94ffff94 (claudeDev D1_ring_p5s02a_20261010_023239.vi, never opened here);
 2. the CEN2 12th wire: regenerate the p5s02a simulated end (stagesim.simulate on the P5-1 graph, output only under
    tools/bench/sim/ring_p5s02a_c159/) and diff its new wires against the real 94ffff94 graph read;
 3. delete the failed copy claudeDev D1_ring_p5s02a_20261009_152721.vi (md5 cac5236b checked first) and its resume record.

WHAT EXISTS (checked first, CALLED not copied): invcheck.md5 / Gates / card_pins (pins, gate counter, RESULT line);
errorlist_check._hit / compare (the checker's own matcher: classifies each observed item by the expected row's norm_all and
proves the written file licenses all 56 items, extra 0 / missing 0); allterms.join_wires / severed + vigraph.dedupe_rows
(termless and source-only wires, as attrib_c159_p5s02a used them); stagesim.simulate (the simulated end) and stagesim._ints
(every integer an action names, for the 'no A24..A80 action touches it' check); stagekit.sim_census_snapshot (the CEN2 scope:
new {uid: class} between step_00 and the sim end, kept to the pred's census classes, stagekit.py:2250-2267 / 2414-2426).
The new-class objects and their clearing actions are READ from attrib_c159_p5s02a.json (pinned d7c9ef00), not recomputed.
The per-endpoint wire key below is specific to this card (no shared sim-vs-real key with base-uid / created-object naming exists:
stagekit.term_identity_pairs needs a run's bind map, which an offline read of a separately saved file does not have).

PREDICTION CONTRACT (gates):
  K   every card input md5 == the card pin; plan_in / pred / stored sim end md5 == the stored dry's
  V0  VI pins before: 023239 94ffff94, s09 eb1d0f31, P5-1a 2482fe7b, P5-1 7f2582ae, failed copy 152721 cac5236b
  E1  56 observed items; every item classified by exactly one class rule
  E2  per class: objects (graph) == items (count), every object has clears_by (action+step / standing+cause / delete_wire 10394)
  E3  the written expected file licenses the 56 items exactly (errorlist_check.compare: extra 0, missing 0)
  E4  totals: 56 = sum per class; after step 2 = 51, after step 3 = 45 (prediction from attrib_c159_p5s02a.md)
  C1  regenerated sim end == stored sim end (state equal) and sim census Wire == 11 (the dry's figure)
  C2  real new Wire objects (P5-2a graph minus P5-1 graph, by uid) == 12 (the pred's MEASURED-SCRATCH figure)
  C3  keyed diff of the new wires: exactly one real-only wire, none sim-only (recorded as a FACT whatever it is)
  D1  failed copy md5 == cac5236b171aab9d82283d7dff9611ef, resume record names it; both deleted, nothing else (run with --delete;
      every gate but C3 must have passed - PD388(a) decides the delete, C3 is PD388(b)'s measurement)
  V1  VI pins after == before
"""
import collections
import copy
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import invcheck as IC          # noqa: E402
import errorlist_check as EC   # noqa: E402
import allterms as AT          # noqa: E402  (join_wires / severed are pure; gscript is imported, never called)
import vigraph as V            # noqa: E402
import stagesim as SS          # noqa: E402
import stagekit as K           # noqa: E402  (sim_census_snapshot only; nothing of the LabVIEW fleet is called)

B = "tools/bench/"
CARD = os.path.join(ROOT, B + "cards/task_159-b1-1.json")
CD = IC.CD
OBS = B + "errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json"
P51EXP = B + "errorlist_expected_D1_ring_p5s01_20261009_124542.json"
ATTR = B + "attrib_c159_p5s02a.json"
PLAN_R = B + "plan_ring_p5s02r_in.json"
G51 = B + "graph_ring_p5s01_20261009_125622.json"
G52 = B + "graph_ring_p5s02a_20261010_032547.json"
PLAN_A = B + "plan_ring_p5s02a.json"
PLAN_A_IN = B + "plan_ring_p5s02a_in.json"
PRED_A = B + "plan_ring_p5s02a_pred.json"
SIM_OUT = os.path.join(HERE, "sim", "ring_p5s02a_c159")
OUT_EXP = B + "errorlist_expected_D1_ring_p5s02a_20261010_023239.json"
OUT_RAW = os.path.join(HERE, "diag_c159_b1_1_raw.json")
EXTRA_PINS = {PLAN_A_IN: "af3e925d", PRED_A: "ed84b5fd", B + "sim/ring_p5s02a/step_23_wire.json": "b1892ad9"}
VIS = {"94ffff94 base 023239": (CD + r"\D1_ring_p5s02a_20261010_023239.vi", "94ffff94"),
       "s09": (CD + r"\D1_ring_p4s09_20261009_060515.vi", "eb1d0f31"),
       "P5-1a": (CD + r"\D1_ring_p5s01a_20261009_101219.vi", "2482fe7b"),
       "P5-1": (CD + r"\D1_ring_p5s01_20261009_124542.vi", "7f2582ae")}
FAILED = CD + r"\D1_ring_p5s02a_20261009_152721.vi"
FAILED_MD5 = "cac5236b171aab9d82283d7dff9611ef"
RESUME = os.path.join(HERE, "resume", "resume_plan_ring_p5s02a_20261009_153334.json")
STEP2, STEP3 = (24, 60), (61, 80)            # ring-p5.md:376 (PD387(f)); delete_wire 10394 = step 2's first action (ring-p5b.md PD388(a))
ATTR_MD = "tools/bench/attrib_c159_p5s02a.md"
# class -> (norm_all of the expected row, cite of the class). The four inherited classes keep the P5-1 file's keys
# (errorlist_expected_D1_ring_p5s01_20261009_124542.json:12-75); the three new classes use their own wording's key.
CLASSES = (("whilesubvi", ["inputofwhileloop", "inputofsubvi"]), ("nosource", ["hasnosource"]),
           ("undirected", ["undirectedtunnel"]), ("looseends", ["wirewirehaslooseends"]),
           ("notconnected", ["completelyunconnectedwire"]), ("unwiredinput", ["buildarray", "containsunwiredorbadterminal"]),
           ("twotypes", ["twoterminalsofdifferenttypes"]))
G = IC.Gates()
R = {}


def fact(msg, extra=None):
    print("FACT | {0} | {1}".format(msg, json.dumps(extra, default=str)[:2500] if extra is not None else ""), flush=True)


def jl(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


def vi_pins():
    return dict((k, IC.md5(p)) for k, (p, _m) in VIS.items())


# ------------------------------------------------------------------------------------------------ K / V0
print("---------- [K] pins", flush=True)
bad = dict((p, IC.md5(p)) for p, m in IC.card_pins(CARD) if IC.md5(p) != m)
bad.update(dict((p, IC.md5(os.path.join(ROOT, p))) for p, m in EXTRA_PINS.items() if not IC.md5(os.path.join(ROOT, p)).startswith(m)))
G("K every card input md5 == card pin; plan_in af3e925d, pred ed84b5fd, stored sim end b1892ad9", not bad, bad)
V0 = vi_pins()
G("V0 VI pins before " + json.dumps(V0), all(V0[k].startswith(m) for k, (_p, m) in VIS.items()) and IC.md5(FAILED) in (FAILED_MD5, "MISSING"),
  {"failed_152721": IC.md5(FAILED)})

# ------------------------------------------------------------------------------------------------ graphs (P5-1, P5-2a)
GR, W, S, TERMS = {}, {}, {}, {}
for k, p in (("p51", G51), ("p52a", G52)):
    d = GR[k] = jl(p)
    TERMS[k], rec = V.dedupe_rows(d["terminals"])
    W[k] = AT.join_wires(TERMS[k], [o["uid"] for o in d["objs"] if o.get("class") == "Wire"])
    S[k] = AT.severed(W[k])
termless = dict((k, set(w["wire_uid"] for w in W[k] if w["termless"])) for k in W)
srconly = dict((k, set(w["wire_uid"] for w in S[k] if not w["termless"] and w["n_sink"] == 0)) for k in S)
fact("termless P5-1 {0} / P5-2a {1}; P5-2a-only {2}".format(len(termless["p51"]), len(termless["p52a"]),
                                                           sorted(termless["p52a"] - termless["p51"])))
fact("source-only P5-1 {0} / P5-2a {1}".format(sorted(srconly["p51"]), sorted(srconly["p52a"])))

# ------------------------------------------------------------------------------------------------ plan actions (A24..A80)
acts = jl(PLAN_R)["actions"]
touch = collections.defaultdict(list)                          # integer named by an action -> [A#]
for n, a in enumerate(acts, 1):
    if STEP2[0] <= n <= STEP3[1]:
        for u in SS._ints(a, set()):
            touch[u].append(n)


def step_of(n):
    return 2 if STEP2[0] <= n <= STEP2[1] else 3 if STEP3[0] <= n <= STEP3[1] else None


def wire_terms(k, wu):
    return [r["term_uid"] for r in TERMS[k] if r["wire_uid"] == wu]


def untouched(k, uid):
    """[] when no A24..A80 action names the object's uid or any terminal uid on it, else the action numbers."""
    return sorted(set(n for u in [uid] + wire_terms(k, uid) for n in touch.get(u, [])))


# ------------------------------------------------------------------------------------------------ [E] expected list
print("---------- [E] expected Error List of 94ffff94, item by item", flush=True)
items = jl(OBS)["items"]
cls_of = {}
for it in items:
    txt = "%s %s" % (it.get("raw") or "", it.get("detail") or "")
    hits = [c for c, na in CLASSES if EC._hit({"norm_all": na}, txt)]
    cls_of[it["index"]] = hits[0] if len(hits) == 1 else ("AMBIGUOUS:" + ",".join(hits) if hits else "NONE")
by_cls = collections.defaultdict(list)
for i in sorted(cls_of):
    by_cls[cls_of[i]].append(i)
G("E1 56 observed items, each in exactly one class " + json.dumps(dict((c, len(v)) for c, v in by_cls.items())),
  len(items) == 56 and all(c in dict(CLASSES) for c in by_cls), dict(by_cls))

AT_ = jl(ATTR)
P51C = "errorlist_expected_D1_ring_p5s01_20261009_124542.json"
new_objs = collections.defaultdict(list)                       # class -> [object dict from the attribution]
for c in ("nosource", "undirected", "whilesubvi"):
    seen = set()
    for it in AT_["items"]:
        if it["class"] == c:
            for x in it["candidates"]:
                if x["uid"] not in seen:
                    seen.add(x["uid"])
                    new_objs[c].append(x)
for x in AT_["net3"]:
    new_objs["notconnected" if x["uid"] == 10394 else "looseends"].append(x)


def act_clear(x, cite):
    acts_ = x.get("actions") or []
    ns = sorted(set(int(a.split()[0][1:]) for a in acts_))
    if not ns:
        return None
    n = ns[0]
    cb = {"kind": "action", "action": acts_[0], "step": step_of(n)}
    if n in (28, 35, 32, 39, 70, 80) and x.get("kind") == "wire":
        cb["assumption"] = "MERGE: the connect lands on a terminal already carrying this stub and leaves one ok wire (ring-p5b.md PD388(c)); unmeasured"
    if x.get("kind") == "tunnel" or (x.get("kind") == "wire" and any(s.get("cls") == "LoopTunnel" and s.get("tcls") == "OuterTerminal" for s in x.get("sinks") or [])):
        cb["via"] = "the action wires the tunnel's inner terminal; the tunnel gets a source and its outer-side wire with it (attrib_c159_p5s02a.md:32-35)"
    cb["cite"] = cite
    return cb


objs_of = {}   # class -> [(object description, clears_by)]
# new classes and the net-3, from the attribution
for c, lines in (("nosource", "28-32"), ("undirected", "33-34"), ("whilesubvi", "35"), ("looseends", "44-45")):
    objs_of[c] = [({"kind": x["kind"], "uid": x["uid"], "evidence": x.get("evidence")},
                   act_clear(x, "%s:%s; %s" % (ATTR_MD, lines, x.get("evidence")))) for x in new_objs[c]]
# not connected: the termless wires of the P5-2a graph
nc = []
for u in sorted(termless["p52a"]):
    if u == 10394:
        nc.append(({"kind": "wire", "uid": u, "evidence": "graph_ring_p5s02a wire 10394 (termless; P5-1: #3052 'File # Saved' 3060 -> #376 5772)"},
                   {"kind": "delete_wire", "action": "delete_wire 10394", "step": 2,
                    "cite": "docs/d1/ring-p5b.md PD388(a): step 2's FIRST action; %s:41-43 (A13 re-made the pair as wire 11774)" % ATTR_MD}))
    elif u in termless["p51"] and not untouched("p52a", u):
        nc.append(({"kind": "wire", "uid": u, "evidence": "graph_ring_p5s02a wire %d termless, termless in graph_ring_p5s01 too" % u},
                   {"kind": "standing", "cause": "inherited termless wire (P5-1 not-connected entries 9 L2-A3 + 11 B1-new + 2 session-6, %s:28-43,52-67); "
                    "no A24..A80 action names its uid" % P51C}))
    else:
        nc.append(({"kind": "wire", "uid": u}, None))
objs_of["notconnected"] = nc
# loose ends: new stubs (above) + the inherited source-only wires + inherited items with no 1:1 graph object
le = list(objs_of["looseends"])
for u in sorted(srconly["p52a"] & srconly["p51"]):
    tt = untouched("p52a", u)
    le.append(({"kind": "wire", "uid": u, "evidence": "graph_ring_p5s02a wire %d source-only, source-only in graph_ring_p5s01 too" % u},
               None if tt else {"kind": "standing", "cause": "inherited source-only wire (base, loop 637; %s:13); no A24..A80 action names it or its terminals" % ATTR_MD}))
for j in range(max(0, len(by_cls["looseends"]) - len(le))):
    le.append(({"kind": "item-only", "uid": None, "evidence": "inherited loose-ends item without a 1:1 graph object (%s:56 OPEN: class vs shape not 1:1 in the base)" % ATTR_MD},
               {"kind": "standing", "cause": "inherited: P5-1 expected loose-ends entries 20 + 1 (%s:44-51,68-75), count unchanged by the graph diff "
                "(attrib classes.looseends new 2 resolved 0); no graph object to touch" % P51C}))
objs_of["looseends"] = le
# Build Array / two types: inherited, one item each
ba = [o for o in GR["p52a"]["objs"] if o["uid"] == 2626]
tba = untouched("p52a", 2626)
objs_of["unwiredinput"] = [({"kind": "node", "uid": 2626, "class": ba[0]["class"] if ba else None,
                             "evidence": "P5-1 cite: PD225(c) L2-A3 class, open row 2626"},
                            None if tba else {"kind": "standing", "cause": "inherited (%s:11-19, PD225(c) open row 2626); no A24..A80 action names #2626 or its terminals" % P51C})]
objs_of["twotypes"] = [({"kind": "unidentified", "uid": None, "evidence": "P5-1 cite: PD225(c) open row, B1-new src+sink RBW wires (no uid recorded)"},
                        {"kind": "standing", "cause": "inherited (%s:20-27); attrib classes.twotypes new 0 resolved 0 - no graph change in step 1" % P51C})]
fact("A24..A80 actions naming #2626 / its terminals", tba)

rows, e2bad = [], {}
for c, idx in by_cls.items():
    ob = objs_of.get(c, [])
    # pairing BY COUNT inside a class set: objects ordered by clearing step (step 2, step 3, standing), items by index
    order = sorted(ob, key=lambda t: (9 if not t[1] else {"delete_wire": 0, "action": t[1].get("step") or 9}.get(t[1]["kind"], 8),
                                      t[0].get("uid") or 0))
    if len(order) != len(idx) or any(cb is None for _o, cb in order):
        e2bad[c] = {"items": len(idx), "objects": len(order), "no_clears_by": [o for o, cb in order if cb is None]}
    exact = len(idx) == 1
    for i, (o, cb) in zip(idx, order):
        it = items[i]
        rows.append({"item": i, "norm_all": dict(CLASSES)[c], "count": 1, "label": "%s [item %d]" % (it.get("raw"), i), "class": c,
                     "object": o, "pairing": "exact (1 item <-> 1 object)" if exact else
                     "class set %d items <-> %d objects, paired BY COUNT (item order vs object order step 2, step 3, standing); which item is "
                     "which object is not readable (no uid route, errorlist uid_route)" % (len(idx), len(order)),
                     "clears_by": cb or {"kind": "unattributed"}, "cite": (cb or {}).get("cite") or (cb or {}).get("cause") or "UNATTRIBUTED"})
    for i in idx[len(order):]:
        rows.append({"item": i, "norm_all": dict(CLASSES)[c], "count": 1, "label": items[i].get("raw"), "class": c, "object": None,
                     "clears_by": {"kind": "unattributed"}, "cite": "UNATTRIBUTED: more items than graph objects"})
rows.sort(key=lambda r: r["item"])
G("E2 per class objects == items and every object has a clears_by", not e2bad, e2bad)

ck = collections.Counter(r["clears_by"]["kind"] for r in rows)
ccls = collections.Counter(r["class"] for r in rows)
gone = lambda r, s: r["clears_by"]["kind"] in ("action", "delete_wire") and (r["clears_by"].get("step") or 99) <= s   # noqa: E731
after2 = sum(1 for r in rows if not gone(r, 2))
after3 = sum(1 for r in rows if not gone(r, 3))
by_act = collections.Counter("%s s%s" % (r["clears_by"].get("action"), r["clears_by"].get("step")) for r in rows if r["clears_by"]["kind"] != "standing")
EXP = {"schema": "errorlist-expected/1", "bed": CD + r"\D1_ring_p5s02a_20261010_023239.vi", "bed_md5": "94ffff9413599d5153a5e6fb409294ab",
       "decided_by": "card 159-b1-1 (docs/d1/ring-p5b.md PD388(a), ring-p5.md PD387(d)): one row per observed item (56), each with its own clears_by; "
                     "objects and actions of the new classes from %s (d7c9ef00); w10394 cleared by delete_wire 10394, step 2's first action" % ATTR,
       "measured_from": OBS, "measured_md5": "25d6084b2c2988338659758c1315a3fb", "base_expected": B + P51C, "total": len(rows),
       "counts": {"by_clears_by": dict(ck), "by_class": dict(ccls), "by_action": dict(by_act),
                  "after_step2": after2, "after_step3": after3,
                  "note": "after_step2/3 = base items not cleared by then (removal only, MERGE assumed per PD388(c)); items NEW from step-2/3 actions are not predicted here"},
       "expected": rows,
       "format_note": "same entry form as %s (norm_all / count / label / cite, checker errorlist_check.compare); one entry per item, count 1; "
                      "extra keys item / class / object / pairing / clears_by are ignored by the checker" % P51C}
json.dump(EXP, open(os.path.join(ROOT, OUT_EXP), "w", encoding="utf-8"), indent=1)
ex, mi, _u = EC.compare(copy.deepcopy(items), jl(OUT_EXP)["expected"])
G("E3 written expected file licenses the 56 observed items exactly (errorlist_check.compare)", not ex and not mi, {"extra": ex, "missing": mi})
fact("clears_by kinds", dict(ck))
fact("per class", dict(ccls))
fact("per action", dict(by_act))
G("E4 totals 56; after step 2 = %d (pred 51); after step 3 = %d (pred 45)" % (after2, after3), len(rows) == 56 and after2 == 51 and after3 == 45)

# ------------------------------------------------------------------------------------------------ [C] CEN2 wire
print("---------- [C] CEN2: regenerate the p5s02a simulated end, diff its new wires with the real 94ffff94 graph", flush=True)
os.makedirs(SIM_OUT, exist_ok=True)
logl = []
Sres = SS.simulate(os.path.join(ROOT, PLAN_A_IN), os.path.join(ROOT, G51), out_root=SIM_OUT, plan_out_dir=SIM_OUT, log=logl.append)
fact("simulate final {0} failed {1}; {2} log lines".format(Sres.get("final"), Sres.get("failed"), len(logl)))
steps = sorted(f for f in os.listdir(os.path.join(SIM_OUT, "ring_p5s02a")) if f.startswith("step_"))
s0 = json.load(open(os.path.join(SIM_OUT, "ring_p5s02a", steps[0]), encoding="utf-8"))["state"]
s_end = json.load(open(os.path.join(SIM_OUT, "ring_p5s02a", steps[-1]), encoding="utf-8"))["state"]
stored_end = jl(B + "sim/ring_p5s02a/step_23_wire.json")["state"]
classes = tuple(jl(PRED_A)["census"])                          # the pred's classes, as RingSession.SRC (stagekit.py:2307)
c0, c1 = K.sim_census_snapshot(s0, classes), K.sim_census_snapshot(s_end, classes)
sim_new = dict((u, c1[u]) for u in set(c1) - set(c0))
sim_cen = collections.Counter(sim_new.values())
G("C1 regenerated sim end == stored step_23 state ({0}) and sim census Wire == 11 (got {1})".format(steps[-1], sim_cen.get("Wire")),
  s_end == stored_end and sim_cen.get("Wire") == 11, dict(sim_cen))

wobj = dict((k, set(o["uid"] for o in GR[k]["objs"] if o.get("class") == "Wire")) for k in GR)
real_new = sorted(wobj["p52a"] - wobj["p51"])
real_gone = sorted(wobj["p51"] - wobj["p52a"])
G("C2 real new Wire objects (P5-2a graph minus P5-1 graph, by uid) == 12 (got %d; gone %d)" % (len(real_new), len(real_gone)),
  len(real_new) == 12, {"new": real_new, "gone": real_gone})

base_terms = set(r["term_uid"] for r in TERMS["p51"])
base_frames = set(int(r.get("frame_diagram") or 0) for r in TERMS["p51"]) | set(int(k) for k in (GR["p51"].get("owners") or {}))


def ends_by_wire(rows_):
    out = collections.defaultdict(list)
    for r in rows_:
        if r.get("wire_uid"):
            out[r["wire_uid"]].append(r)
    return out


def ekey(r):
    # a created object's terminal: (new, owner class) - its NAME is not compared: the sim names shift-register / selector-tunnel
    # terminals '' where LabVIEW reports 'queue out' / 'x,y,z array' (diag_c159_b1_1_pre.log C3 FACT lines)
    t = r["term_uid"] if r["term_uid"] in base_terms else ("new", r.get("owner_class"))
    f = int(r.get("frame_diagram") or 0)
    return (bool(r["is_source"]), t, f if f in base_frames else "new")


def wkey(wu, eb):
    e = eb.get(wu)
    return ("termless", wu) if not e else tuple(sorted((ekey(r) for r in e), key=str))


def desc(wu, eb):
    return {"wire": wu, "ends": [{"src": bool(r["is_source"]), "owner": r["owner_uid"], "cls": r.get("owner_class"), "term_uid": r["term_uid"],
                                  "term": r.get("term_name"), "frame": r.get("frame_diagram")} for r in eb.get(wu, [])] or "termless",
            "pos": next((o.get("pos") for o in GR["p52a"]["objs"] if o["uid"] == wu), None)}


eb_sim, eb_real = ends_by_wire(s_end["terminals"]), ends_by_wire(TERMS["p52a"])
ks = collections.Counter(wkey(u, eb_sim) for u, c in sim_new.items() if c == "Wire")
kr = collections.Counter(wkey(u, eb_real) for u in real_new)
real_only = [u for u in real_new if (kr - ks)[wkey(u, eb_real)] > 0]
sim_only_k = list((ks - kr).elements())
fact("CEN2 real-only new wires", [desc(u, eb_real) for u in real_only])
fact("CEN2 sim-only new wire keys", sim_only_k)
uid_by_key = lambda eb: dict((wkey(u, eb), u) for u in eb)                 # noqa: E731
sk_all, rk_all = uid_by_key(eb_sim), uid_by_key(eb_real)
cpart = {"real_only_in_sim": dict((u, sk_all.get(wkey(u, eb_real))) for u in real_only),
         "sim_only": [{"sim_wire": [u for u, c in sim_new.items() if c == "Wire" and wkey(u, eb_sim) == k],
                       "ends": [(bool(r["is_source"]), r["owner_uid"], r.get("owner_class"), r["term_uid"], r.get("term_name"), r.get("frame_diagram"))
                                for u, c in sim_new.items() if c == "Wire" and wkey(u, eb_sim) == k for r in eb_sim[u]],
                       "real_wire_same_key": rk_all.get(k)} for k in sim_only_k]}
fact("CEN2 counterparts (same endpoint key on the other side, any uid; None = no wire with those ends)", cpart)
R["cen2_counterparts"] = cpart
# the whole wire set too (any other sim-vs-real difference, outside the census scope)
all_s = collections.Counter(wkey(u, eb_sim) for u in eb_sim)
all_r = collections.Counter(wkey(u, eb_real) for u in eb_real)
fact("whole termed-wire set: sim end {0} / real {1}; real-only keys {2}; sim-only keys {3}".format(
    sum(all_s.values()), sum(all_r.values()), sum((all_r - all_s).values()), sum((all_s - all_r).values())),
    {"real_only": [k for k in (all_r - all_s)][:12], "sim_only": [k for k in (all_s - all_r)][:12]})
fact("termless: sim end objs carry the base's Wire objects; real P5-2a termless {0}, P5-1 termless {1}, real-only termless {2}".format(
    len(termless["p52a"]), len(termless["p51"]), sorted(termless["p52a"] - termless["p51"])))
G("C3 keyed diff of the census-scope new wires: one real-only wire, no sim-only (real-only %s)" % real_only,
  len(real_only) == 1 and not sim_only_k, {"real_only": real_only, "sim_only": sim_only_k})
R["cen2"] = {"sim_census": dict(sim_cen), "real_new": real_new, "real_gone": real_gone, "real_only": [desc(u, eb_real) for u in real_only],
             "sim_only_keys": [str(k) for k in sim_only_k], "is_10394": real_only == [10394],
             "whole_real_only": [str(k) for k in (all_r - all_s)], "whole_sim_only": [str(k) for k in (all_s - all_r)],
             "sim_steps": steps, "sim_log_tail": logl[-5:]}

# ------------------------------------------------------------------------------------------------ [D] delete the failed copy
print("---------- [D] delete the failed copy and its resume record", flush=True)
m_failed = IC.md5(FAILED)
# ALREADY: both files gone = deleted by the recorded run tools/bench/diag_c159_b1_1.log:28-29 (md5 checked there); nothing is deleted twice
already = m_failed == "MISSING" and not os.path.exists(RESUME)
rec = {} if already else json.load(open(RESUME, encoding="utf-8"))
names_it = already or os.path.normcase(str(rec.get("file") or "")) == os.path.normcase(FAILED)
# PD388(a) decides the delete on its own; C3 is (b)'s measurement (recorded, hands back on its own) and does not gate it
pre_ok = all(ok for lab, ok, _d in G.rows if not lab.startswith("C3"))
ok_pre = m_failed == FAILED_MD5 and names_it and pre_ok and "--delete" in sys.argv   # without --delete: everything but the delete
fact("failed copy md5 {0}; resume record {1} file={2}; already deleted {3}".format(m_failed, os.path.relpath(RESUME, ROOT), rec.get("file"), already))
if ok_pre:
    os.remove(FAILED)
    os.remove(RESUME)
G("D1 failed copy md5 == cac5236b (got %s), resume record names it; both deleted (every earlier gate but C3 passed), or both already gone" % m_failed[:8],
  (ok_pre or already) and not os.path.exists(FAILED) and not os.path.exists(RESUME),
  {"deleted": [FAILED, os.path.relpath(RESUME, ROOT)] if ok_pre else [], "already": already})
V1 = vi_pins()
G("V1 VI pins after == before " + json.dumps(V1), V1 == V0)

R.update({"vi_before": V0, "vi_after": V1, "after_step2": after2, "after_step3": after3, "clears_by": dict(ck), "per_class": dict(ccls),
          "per_action": dict(by_act), "deleted": [FAILED, os.path.relpath(RESUME, ROOT)] if ok_pre else []})
json.dump(R, open(OUT_RAW, "w", encoding="utf-8"), indent=1, default=str)
arts = [{"path": p.replace("\\", "/"), "md5": IC.md5(os.path.join(ROOT, p))} for p in (OUT_EXP, os.path.relpath(OUT_RAW, ROOT))]
print(G.result(arts), flush=True)
sys.exit(1 if G.failed else 0)
