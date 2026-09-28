r"""diag_c120_fs - card 120-2 Part F (PD237(k)), MEASURE ONLY, on a never-saved byte copy of the SAVED pool bed (its own nesting): source = BARE
Obtain #23118 'queue out' t25591 on FS2 frame #13236 (2 of 10); sink = a duplicate of the pool's Enqueue #23136 (create_primitive_nested, self-donor
as cards 118-1/119-1) on #639 = body of While #637 on #686 = FS1 frame 9 of 10; both FS on TopLevelDiagram #536 (facts_c120_qrtw.json:303-352,749-834).
Route = stagexec.connect_route's 'nested' for a BARE Nodes[] source (stagexec.py:857-859) -> connect_nested_v1 (stagexec.py:1940-1945). Readers reused:
wiki_build.read_live/read_fs_tunnels, build_d1_v0.owner_of, Stage.broken_wire_count; no alternative route (F3). Plan diag_c120_fs_plan.json.
PREDICTION = measurement gates only (route outcome = a ROW + the scratch_verify record status): F1a/F1b/F2a/F2b/F2d/F4 PASS.
    py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c120_fs.log -- py -u tools/bench/diag_c120_fs.py"""
import json, os, sys, time                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K                                                               # noqa: E402
g = K.g
PL = json.load(open(os.path.join(ROOT, "tools/bench/diag_c120_fs_plan.json"), encoding="utf-8"))   # one base resolves it (gate fp-5)
BED, BEDM, SRC, SNK = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"], PL["src"], PL["sink"]
OUTJ, SV, OM = os.path.join(HERE, "diag_c120_fs.json"), os.path.join(HERE, "scratch_verify"), os.path.join(HERE, "opmodels", "connect_across_fs.json")
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c120_fs", preload=False, deadline_min=33, reserve_s=180, out_json=OUTJ, task="card 120-2 F")
WB, BD, NC = K.mod("wiki_build"), K.mod("build_d1_v0"), K.mod("build_opconnectnested_v1")
SIG = ("term_uid", "term_name", "owner_uid", "owner_class", "term_class", "frame_diagram")
def up(u):
    out = []
    for _k in range(12):
        c, o = s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(s.work, u, strict=False), ("?", 0))[0] or ("?", 0)
        out.append((u, str(c), int(o or 0)))
        if not o or c in ("TopLevelDiagram", "?"):
            break
        u = int(o)
    return out
def tidx(diag, node, name, src):
    di = g._uid_index(s.work, "Diagram", diag); ni = g._node_index(s.work, di, node); u, rows = g.node_terms_uid(s.work, di, ni)   # noqa: E702
    t = [r["i"] for r in rows if r["name"] == name and bool(r["is_source"]) == src]
    if (len(t) != 1 or u != node) and not DRY:
        raise RuntimeError("#{0}.{1!r}: {2} match(es), node echo {3}".format(node, name, len(t), u))
    t = t or [0]
    return di, ni, t[0]
def walk(rows, pairs, start, stop):
    byt, byw, byo, par = {}, {}, {}, {}
    for r in rows:
        byt[r["term_uid"]] = r; byo.setdefault(r["owner_uid"], []).append(r)        # noqa: E702
        if r["wire_uid"]:
            byw.setdefault(r["wire_uid"], []).append(r)
    for p in pairs:
        par[p["term_a"]], par[p["term_b"]] = p["term_b"], p["term_a"]
    hops, cur, seen, end = [], [byt[start]] if start in byt else [], set(), None
    while cur and len(hops) < 60:
        nxt = []
        for r in cur:
            w = r["wire_uid"]
            if not w or w in seen:
                continue
            seen.add(w); sinks = [x for x in byw.get(w, []) if not x["is_source"]]   # noqa: E702
            hops.append({"wire": w, "from": [r.get(k) for k in SIG], "to": [[x.get(k) for k in SIG] for x in sinks]})
            for x in sinks:
                if x["owner_uid"] == stop:
                    end = x; continue                                                 # noqa: E702
                nxt += ([byt[par[x["term_uid"]]]] if par.get(x["term_uid"]) in byt else
                        [y for y in byo.get(x["owner_uid"], []) if y["is_source"] and str(x["owner_class"]).endswith("Tunnel")])
        cur = nxt
    return hops, end
def body(_):
    s.start(); s.scratches.append(s.work); W = s.work                                 # noqa: E702
    s.head("[F1] nesting read back + the sink")
    ca, cb = up(SRC["diagram"]), up(SNK["diagram"])
    s.fact("F1a chain #{0}: {1}".format(SRC["diagram"], ca)); s.fact("F1a chain #{0}: {1}".format(SNK["diagram"], cb))   # noqa: E702
    fa = [o for u, c, o in ca if c == "FlatSequence"]; fb = [o for u, c, o in cb if c == "FlatSequence"]   # noqa: E702
    s.gate("F1a src frame in FlatSequence A, sink body in While #{0} in FlatSequence B != A, both reach the TopLevelDiagram".format(SNK["loop"]),
           DRY or (len(fa) == 1 and len(fb) == 1 and fa != fb and (SNK["diagram"], "WhileLoop", SNK["loop"]) in cb
                   and ca[-1][1] == cb[-1][1] == "TopLevelDiagram"), (fa, fb))
    enq, e = s.safe("create sink", lambda: g.create_primitive_nested(W, SNK["diagram"], "enqueue_dup", tuple(SNK["pos"]), donor={"donor": W, "uid": SNK["donor"]}))
    s.gate("F1b one Enqueue duplicated onto Diagram #{0} (owner checked in the verb)".format(SNK["diagram"]), enq and not e, (enq, e), fatal=True)
    s.head("[F2] one connect through the 'nested' route")
    lv0 = WB.read_live(W, fs_pairs=[]); es0 = s.es("before connect")                  # noqa: E702
    (sd, sn, st), (dd, dn, dt) = tidx(SRC["diagram"], SRC["node"], SRC["name"], True), tidx(SNK["diagram"], enq, SNK["name"], False)
    rec = s._op("connect_nested_v1", lambda: NC.connect_nested_v1(W, dd, dn, dt, sd, sn, st, json.load(open(NC.MAP_OUT, encoding="utf-8"))),
                "D[{0}].N[{1}].t{2} <- D[{3}].N[{4}].t{5}".format(dd, dn, dt, sd, sn, st))
    s.gate("F2a the connect call returned (its own error is data)", "result" in rec, rec.get("err"))
    lv1 = WB.read_live(W, fs_pairs=[]); es1 = s.es("after connect")                   # noqa: E702
    u0 = set(o["uid"] for o in lv0["objs"]); new = [o for o in lv1["objs"] if o["uid"] not in u0]   # noqa: E702
    cls = {}
    for o in new:
        cls[o["class"]] = cls.get(o["class"], 0) + 1
        if not (o["class"].endswith("Terminal") or o["class"] == "Wire"):
            o["owner_uid"] = s.safe("owner", lambda: BD.owner_of(W, o["uid"], strict=False), ("?", 0))[0]
    fsn = set(o["uid"] for o in new if o["class"] in WB.FS_KINDS)
    pairs = s.safe("read_fs_tunnels", lambda: WB.read_fs_tunnels(W, lv1["objs"], fsn), [])[0] or [] if fsn else []
    hops, end = walk(lv1["terminals"], pairs, SRC["term"], enq)
    tun = [(o["uid"], o["class"], o.get("owner_uid")) for o in new if not (o["class"].endswith("Terminal") or o["class"] == "Wire")]
    s.fact("F2 new objects by class {0}; non-terminal {1}".format(cls, tun)); s.fact("F2 FS tunnel faces {0}".format(pairs))   # noqa: E702
    for h in hops:
        s.fact("HOP w{0} from {1} to {2}".format(h["wire"], h["from"], h["to"]))
    s.gate("F2b after-graph read and the chain walked from t{0}".format(SRC["term"]), DRY or (lv1["terminals"] and hops is not None), len(hops))
    rbw = s.broken_wire_count(allow_mutation=True, tag="F2d") if not DRY else {}
    alive = set(g.uids(W, "Wire")) if not DRY else set()
    seg = dict((h["wire"], h["wire"] in alive) for h in hops)
    s.gate("F2d Remove Bad Wires ran on the scratch (per-segment survival = not broken)", DRY or "bad" in rbw, rbw)
    ok = bool(end) and end["term_name"] == SNK["name"] and hops and hops[0]["from"][0] == SRC["term"] and all(seg.values()) and not rec.get("err") \
        and not (rec.get("result") or [0, 0, ""])[2]
    s.row("F route closes t{0} -> #{1}.'queue' with every segment surviving RBW".format(SRC["term"], enq), ok, "measured, not predicted")
    R = {"function": "stagexec.connect_route 'nested' -> build_opconnectnested_v1.connect_nested_v1", "status": "PASS" if ok else "FAIL",
         "t": time.time(), "card": "120-2 F", "log": "tools/bench/diag_c120_fs.log", "input_md5": BEDM, "plan": "tools/bench/diag_c120_fs_plan.json",
         "fixture": "never-saved byte copy of claudeDev\\D1_qrt_pool_20260928_141055.vi (deleted)", "src": SRC, "sink_uid": enq,
         "call": rec, "es": [es0, es1], "new_by_class": cls, "new_objects": tun, "fs_pairs": pairs, "hops": hops,
         "end": end, "segment_survives_rbw": seg, "rbw": rbw, "chain_a": ca, "chain_b": cb}
    if not DRY:
        p = os.path.join(SV, "stagexec.connect_nested_across_fs_c120_{0}.json".format(s.stamp))
        json.dump(R, open(p, "w", encoding="utf-8"), indent=1, default=str)
        json.dump({"schema": "opmodel/1", "op": "connect_nested_v1 across flat sequences (route 'nested')", "wrapper": R["function"],
                   "measured_on": "claudeDev\\D1_qrt_pool_20260928_141055.vi 93539368 (never-saved byte copy)", "n_samples": 1,
                   "verdict": "single sample", "samples": [{"raw": os.path.relpath(p, HERE), "fits": ok, "target": {"src": SRC, "sink": enq},
                   "checks": {"new_tunnels": tun, "hops": len(hops), "segment_survives_rbw": seg},
                   "common": {"new_objs_by_class": cls, "exec_state_after": es1, "op_err": rec.get("err"), "result": rec.get("result")}}]},
                  open(OM, "w", encoding="utf-8"), indent=1, default=str)
        s.fact("SCRATCH-VERIFY record {0} ({1}); opmodel {2}".format(p, R["status"], OM))
    s.gate("F4 records written", DRY or (os.path.exists(OM)))
    s.dump()
if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
