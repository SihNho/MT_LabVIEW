r"""opmodels_onlysink - card chat-S3 (docs/stage-simulator-plan.md "Op effect models"): the ONLY-SINK sub-rule that chat-S1
left AMBIGUOUS (opmodels/move_in.json, delete_object.json `ambiguous`): when a node is moved out / deleted, what happens to
a wire whose ONLY sink was that node - deleted outright (w8385 const->#7201, w25200 const->#25149) or kept as a
source-side half-wire (w25190 const->#25091, w2160 Function->#1628, w2187 LoopTunnel->#1628)?
HYPOTHESES the cases separate: H-CONST (deleted iff the source is a constant), H-HIST (the fate depends on the edit
history of the scratch: #25091/#25149 were measured after other edits), H-TUNNEL (a tunnel/structure source keeps it).
CASES - each on its OWN fresh dated scratch copy of claudeDev\D1_s4_loop17.vi (4b621946), chosen offline from
tools/bench/opmodels/bed_s4_loop17.json (every sink terminal of the target is on a 2-terminal wire = a sole-sink wire):
  R1 move_in #25091 -> body #23405 alone (repro of move_in_2: w25190 const KEPT; w24756 is branched, control)
  R2 move_in #25149 -> body #23405 alone (repro of the RBW_2 setup: w25200 const DELETED; w25196 Function)
  D1 delete Function #24065: w24648 DigitalNumericConstant, w24417 Function
  D2 delete Function #5556 : w5584 DigitalNumericConstant, w5580 Function
  D3 delete Function #23175: w5090 LoopTunnel (tunnel source)
  D4 delete Function #9703 : w27107 SelectorTunnel, w27156 Function
  D5 delete Function #26411: w26716 BooleanConstant, w26713 EnumConstant, w26722 Function
  D6 delete Function #29716: w29930 StringConstant, w30456 Function
Per case: READ BEFORE (allterms.read_terms + report_all GObject) -> op -> READ AFTER (before the junk purge) -> per
sole-sink wire a SAMPLE {wire, source class, source uid, op, fate: deleted | kept_half | other, positions}. Raw ->
tools/bench/opmodels/raw/onlysink_<case>.json; samples -> tools/bench/opmodels/onlysink_samples.json.
PRIOR ART (used unchanged): opmodels_measure.py's snap/Cell shape, stagekit.Stage/scratch/drop_scratch/close,
allterms.read_terms, gscript.report_all, build_d1_v0.move_in/diag_index, build_opfsinnertunnelconnect_v0.del_node,
build_d1_m3a1.node_census + purge_junk. No new op.
PREDICTION CONTRACT: C1 every op returns without raising; C2 the target node is gone (delete) / owned by #23405 (move);
C3 every listed sole-sink wire yields a sample with fate deleted|kept_half (not 'other'); N >= 4 NEW samples (15 listed);
hygiene: scratches deleted, bed md5 unchanged, pins hold, refs opened == closed, files left []. The FATE itself is the
measured quantity - no fate is predicted. No VI run, no original opened (preload=False), nothing saved.
    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/opmodels_onlysink.log -- py -u tools/bench/opmodels_onlysink.py"""
import collections, json, os, sys                                                  # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import stagekit as K, gscript as g, allterms as A                                  # noqa: E401,E402

BED, BED_MD5 = os.path.join(K.CLAUDEDEV, "D1_s4_loop17.vi"), "4b621946492da3d2fbb96b6053e715ec"
RAW = os.path.join(K.BENCH, "opmodels", "raw")
PINS = tuple(K.DEFAULT_PINS) + (("S4 loop17 bed", BED, BED_MD5),)
BODY = 23405
CASES = [("R1", "move", 25091, "Function", (4800, 6760), [25190]),
         ("R2", "move", 25149, "Function", (4900, 6700), [25200, 25196]),
         ("D1", "delete", 24065, "Function", None, [24648, 24417]),
         ("D2", "delete", 5556, "Function", None, [5584, 5580]),
         ("D3", "delete", 23175, "Function", None, [5090]),
         ("D4", "delete", 9703, "Function", None, [27107, 27156]),
         ("D5", "delete", 26411, "Function", None, [26716, 26713, 26722]),
         ("D6", "delete", 29716, "Function", None, [29930, 30456])]
SAMPLES = []


def snap(sc):
    return A.read_terms(sc)[0], g.report_all(sc, "GObject")


def byw(terms):
    out = collections.defaultdict(list)
    for r in terms:
        if r["wire_uid"]:
            out[r["wire_uid"]].append(r)
    return out


def case(s, tag, verb, uid, cls, pos, wires):
    B, C82, M = K.mod("build_d1_v0"), K.mod("build_opfsinnertunnelconnect_v0"), K.mod("build_d1_m3a1")
    s.head("CASE {0}: {1} {2} #{3}".format(tag, verb, cls, uid))
    sc = s.scratch(tag)
    tb, ob = snap(sc)
    WB, OB = byw(tb), dict((int(o["uid"]), o) for o in ob)
    sole = [w for w, rs in WB.items() if len(rs) == 2 and any(r["owner_uid"] == uid and not r["is_source"] for r in rs)
            and any(r["is_source"] and r["owner_uid"] != uid for r in rs)]
    s.gate("C0 {0} the offline-chosen sole-sink wires {1} are exactly the live ones {2}".format(tag, sorted(wires), sorted(sole)),
           sorted(sole) == sorted(wires), sorted(sole))
    nodes0 = M.node_census(sc, tag)[0]
    if verb == "move":
        res, err = s.safe(tag, lambda: B.move_in(sc, uid, B.diag_index(sc, BODY), pos))
    else:
        res, err = s.safe(tag, lambda: C82.del_node(sc, cls, uid, tag))
    s.gate("C1 {0} op returned without raising".format(tag), not err, err)
    ta, oa = snap(sc)
    WA, OA = byw(ta), dict((int(o["uid"]), o) for o in oa)
    if verb == "move":
        ow, _e = s.safe("owner_of", lambda: B.owner_of(sc, uid))
        s.gate("C2 {0} #{1} owned by #{2} after the move".format(tag, uid, BODY), ow and ow[1] == BODY, ow)
    else:
        s.gate("C2 {0} #{1} gone after the delete".format(tag, uid), uid not in OA, uid in OA)
    for w in sorted(set(wires) | set(sole)):
        rs = WB.get(w, [])
        src = next((r for r in rs if r["is_source"]), {})
        now = WA.get(w, [])
        still_src = [r for r in now if r["term_uid"] == src.get("term_uid")]
        fate = "deleted" if (w not in OA and not now) else ("kept_half" if still_src and len(now) == 1 else "other")
        so = OB.get(int(src.get("owner_uid") or 0), {})
        smp = {"case": tag, "op": verb, "node": uid, "wire": w, "src_uid": src.get("owner_uid"),
               "src_class": src.get("owner_class"), "src_term_uid": src.get("term_uid"), "fate": fate,
               "wire_obj_after": w in OA, "rows_after": [(r["term_uid"], r["owner_uid"], r["is_source"]) for r in now],
               "src_pos": so.get("pos"), "node_pos": OB.get(uid, {}).get("pos"), "src_owner_obj": so.get("owner")}
        SAMPLES.append(smp)
        s.fact("SAMPLE {0}".format(smp))
        s.gate("C3 {0} w{1} ({2}) fate is deleted|kept_half".format(tag, w, src.get("owner_class")),
               fate in ("deleted", "kept_half"), fate)
    rec = {"case": tag, "verb": verb, "uid": uid, "err": err, "wires": wires,
           "before_wires": dict((str(w), WB.get(w)) for w in wires), "after_wires": dict((str(w), WA.get(w)) for w in wires),
           "wire_objs": [sum(1 for o in ob if o["class"] == "Wire"), sum(1 for o in oa if o["class"] == "Wire")]}
    with open(os.path.join(RAW, "onlysink_{0}.json".format(tag)), "w", encoding="utf-8") as f:
        json.dump(rec, f, default=str, indent=0)
    s.safe(tag + " purge", lambda: C82.purge_junk(sc, nodes0, tag, []))
    s.drop_scratch(sc, "H4 " + tag)


def body(s):
    print(__doc__, flush=True)
    os.makedirs(RAW, exist_ok=True)
    s.start(); s.discard_work()                                                    # noqa: E702
    s.fact("HANDLES after open {0!r}".format(K.mod("bench_prep").labview_handles()))
    for c in CASES:
        case(s, *c)
    table = collections.defaultdict(collections.Counter)
    for x in SAMPLES:
        kind = "constant" if str(x["src_class"]).endswith("Constant") else (
            "tunnel" if "Tunnel" in str(x["src_class"]) else "node")
        table[(x["op"], kind)][x["fate"]] += 1
    for k in sorted(table):
        s.fact("TABLE op={0} source={1}: {2}".format(k[0], k[1], dict(table[k])))
    s.gate("N >= 4 new samples with a fate", sum(1 for x in SAMPLES if x["fate"] in ("deleted", "kept_half")) >= 4, len(SAMPLES))
    with open(os.path.join(K.BENCH, "opmodels", "onlysink_samples.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "onlysink-samples/1", "bed": {"path": BED, "md5": BED_MD5}, "samples": SAMPLES,
                   "table": dict(("{0}|{1}".format(*k), dict(v)) for k, v in table.items())}, f, indent=1, default=str)


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "opmodels_onlysink", preload=False, deadline_min=27, pins=PINS)
    sys.exit((K.run(body, st), K.mod("bench_prep").restart_labview())[0])
