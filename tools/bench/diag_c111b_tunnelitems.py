r"""diag_c111b_tunnelitems - card 111-2 A4: how many Error List items does ONE cut loop-tunnel wire raise (and one unwired new SR)?
FIXTURE: a scratch byte copy (discard_work, deleted at close) of the L2-A3 bed claudeDev\D1_l2_a3_20260927_151224.vi (md5 14337cfd),
whose Error List is KNOWN: 29 items (errorlist_D1_l2_a3_..._202005_reuse.json: loose 13, unconnected 9, no-source 3, tunnel-to-input 2,
BuildArray 1, Image In 1; no undirected-tunnel, no SR item). Nothing is saved, no VI is run. B1 is not touched.
MUTATIONS = the B1 situation, one object each (graph_l2a3_bed_20260927.json):
 (a) delete wire 9097 = LSR #9025 -> For#1359 tunnel #9087 outer t9092; inner wire 9076 keeps ONE sink (#8634 'array')
 (b) delete wire 29787 = #29240 -> For#29874 tunnel #29777 outer t29782; inner wire 29766 keeps TWO sinks (#29625 'index (col)', #29973 'element')
 (c) add_shift_reg on WhileLoop #10170 (as B1's srb1), left unwired
PRIOR ART: stagekit.delete_wire / add_shift_reg (the B1 stage's own ops), errorlist_check.open_diagram + lv_errorlist.read (card 111-1).
PREDICTION (recorded, not assumed): the item classes that grow over the 29, per mutation class; gates are only on the mechanics:
 M the 3 ops return no error; E ExecState 0 after; L the Error List read is complete (n_reported == items read);
 H scratch deleted, bed md5 unchanged, LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c111b_tunnelitems.log -- py -u tools/bench/diag_c111b_tunnelitems.py"""
import collections, json, os, re, subprocess, sys, time                             # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, errorlist_check as EC                           # noqa: E401,E402
PL = json.load(open(os.path.join(K.BENCH, "diag_c111b_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
BED, BED_MD5 = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]
BASE, CUTS, SZ = os.path.join(K.BENCH, PL["input"]["base_errorlist"]), PL["cuts"], PL["sizes"]
OUT = os.path.join(K.BENCH, "errorlist_scratch_c111b_tunnelitems.json")
FUNC, REC_DIR = "errorlist.loop_tunnel_cut_items", os.path.join(K.BENCH, "scratch_verify")
KEYS = [("undirected_tunnel", "undirectedtunnel"), ("tunnel_to_input", "outputlooptunnel"), ("sr_unwired_inside", "unwiredfrominsidetheloop"),
        ("sr_type_undefined", "datatypeisundefined"), ("no_source", "hasnosource"), ("unconnected", "notconnectedtoan"),
        ("loose_ends", "looseends"), ("node_unwired", "containsunwired"), ("subvi_not_wired", "isnotwired"),
        ("different_types", "differenttypes"), ("different_dims", "differentdimensions")]


def cls(raw):
    k = re.sub(r"[^a-z]", "", (raw or "").lower()).replace("anvthing", "anything")
    return next((n for n, kw in KEYS if kw in k), "other")


def census(items):
    return collections.Counter(cls(i.get("raw")) for i in items)


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work(); W = s.work                                         # noqa: E702
    base = json.load(open(BASE, encoding="utf-8"))["items"]
    c0 = census(base)
    s.fact("BASE census (29 expected) {0} n={1}".format(dict(c0), len(base)))
    rows = K.mod("wiki_build").read_live(W, fs_pairs=[])["terminals"]
    ends = lambda w: [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"]) for r in rows if int(r["wire_uid"] or 0) == w]  # noqa: E731
    for c in CUTS:
        s.fact("L2-A3 scratch cut {0}: wire {1} ends {2}; inner wire {3} ends {4}".format(c["tag"], c["wire"], ends(c["wire"]),
                                                                                        c["inner_wire"], ends(c["inner_wire"])))
    s.gate("F every cut wire ends on its tunnel (outer face, sink)", all(any(e[0] == c["tunnel"] and not e[3] for e in ends(c["wire"]))
                                                                        for c in CUTS), [ends(c["wire"]) for c in CUTS], fatal=True)
    ops = [s.delete_wire(c["wire"], c["tag"]) for c in CUTS]
    li = s.uid_index("WhileLoop", PL["sr_loop"])
    s.fact("WhileLoop sr_loop traverse index {0}".format(li))
    s.gate("F WhileLoop sr_loop has a traverse index", li is not None, li, fatal=True)
    ops.append(s.add_shift_reg(li, 120, "WhileLoop"))
    s.fact("OPS {0}".format(ops))
    es = s.es("after a+b+c")
    s.gate("E ExecState 0 after the 3 mutations", es == 0, es)
    if getattr(g.report_all, "_dry", False):                                        # the read below is GUI + tasklist only
        s.fact("DRY: Error List read skipped (GUI/tasklist, no COM)"); return      # noqa: E702
    EC._lv_imports()
    R = {"gui_acts_outer": [], "errors": []}
    g.open_panel(W); time.sleep(1.0)                                                # noqa: E702
    R["bd"] = EC.open_diagram(W, R)
    r = EC.E.read(W, OUT, log=lambda x: print(x, flush=True), max_steps=SZ["MAX_STEPS"])
    items = r.get("items") or []
    s.gate("L Error List read complete (n_reported == items)", r.get("n_reported") == len(items) and len(items) > 0,
           (r.get("n_reported"), len(items), r.get("errors")))
    c1 = census(items)
    delta = dict((k, c1.get(k, 0) - c0.get(k, 0)) for k in sorted(set(c0) | set(c1)))
    s.fact("AFTER census {0} n={1}".format(dict(c1), len(items)))
    s.fact("DELTA over the L2-A3 base {0}".format(delta))
    for i in items:
        if cls(i.get("raw")) in ("undirected_tunnel", "tunnel_to_input", "sr_unwired_inside", "sr_type_undefined", "node_unwired", "other"):
            s.fact("ITEM {0} | {1} | {2}".format(i.get("index"), i.get("raw"), (i.get("detail") or "")[:160]))
    s.R["c111b"] = {"base": dict(c0), "after": dict(c1), "delta": delta, "n_after": len(items), "ops": [str(o) for o in ops]}
    s.dump()


if __name__ == "__main__":
    st = K.Stage(BED, BED_MD5, "scratch_c111b_tun", deadline_min=SZ["DEADLINE_MIN"], out_json=os.path.join(K.BENCH, "diag_c111b_tunnelitems.json"),
                 task="card 111-2 A4")
    K.run(body, st)
    DRY = bool(getattr(g.report_all, "_dry", False))                                # diag_c108d_selind.py's dry test
    if not DRY:
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        st.gate("H LabVIEW gone at exit; bed md5 unchanged", gone and K.md5(BED) == BED_MD5, (gone, K.md5(BED)))
    rc = st.summary()
    if rc == 0 and not DRY:
        os.makedirs(REC_DIR, exist_ok=True)
        json.dump({"function": FUNC, "status": "PASS", "t": time.time(), "card": "111-2", "fixture": "D1_l2_a3 bed byte copy",
                   "delta": (st.R.get("c111b") or {}).get("delta"), "log": "tools/bench/diag_c111b_tunnelitems.log"},
                  open(os.path.join(REC_DIR, "{0}_{1}.json".format(FUNC, st.stamp)), "w", encoding="utf-8"), indent=1)
    sys.exit(rc)
