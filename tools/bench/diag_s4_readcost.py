r"""diag_s4_readcost - card chat-S4 item B, the LabVIEW MEASUREMENT: what one per-BIND whole-VI read costs today (seconds and
private MB), split into its parts, and what the nearest EXISTING per-node route costs and returns, on a never-saved byte copy of
the P4 session-1 file (path + md5 from diag_s4_readcost_plan.json). READ-ONLY: no edit, no save, no VI run; the copy is deleted
at close (s.discard_work) and LabVIEW is killed at exit.
EXISTING TOOLS FOUND FIRST: the whole read = wiki_build.read_live:233 (report_all GObject census + allterms.read_terms
OpAllTerms_v1 + join); NO op reads ONE owner's terminals by uid - the 137-3 "read_terms by owner uid" row was a WHOLE read_terms
filtered in Python (diag_c137_3_lookup.py:50-52). The nearest per-node route is report_all('Diagram') -> gscript.node_labels(d)
(Diagram.Nodes[] uid order, gscript.py:3639) -> gscript.node_terms_uids(d, i) (OpNodeTermsUid_v0, gscript.py:1223): name /
is_source / wire / term uid, but NOT term_class / owner_class / frame_diagram; a Constant is not in Nodes[] (diag_c137_3_lookup.log:39-43).
PREDICTION: whole read_live 15-30 s and ~+2 MB each (diag_chat_m1_mem.log basis); the per-node route < 3 s and ~0 MB per node; per-node
rows equal the whole read's (term_uid, name, is_source, wire) for Nodes[] owners; tunnels / registers / Diagram-owned control
terminals not addressable this way. Gates check only that the measurement completed; the numbers are FACTS.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_s4_readcost.log -- py -u tools/bench/diag_s4_readcost.py"""
import collections, json, os, sys, time                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K, allterms as AT                                               # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_s4_readcost_plan.json"), encoding="utf-8"))
GR = json.load(open(os.path.join(ROOT, PL["graph"]), encoding="utf-8"))
OUT = os.path.join(HERE, "diag_s4_readcost.json")
DRY = bool(getattr(g.report_all, "_dry", False))
RES = {"costs": [], "nodes": []}
s = K.Stage(PL["input"]["vi"], PL["input"]["md5"], "scratch_s4_readcost", preload=False, deadline_min=35, reserve_s=120,
            out_json=os.path.join(HERE, "diag_s4_readcost_stage.json"), task="card chat-S4 B measurement (read-only)")


def mb():
    return None if DRY else round((K.private_bytes() or 0) / 1048576.0, 2)


def note(tag, t0, m0):
    m1 = mb()
    d = None if m0 is None or m1 is None else round(m1 - m0, 2)
    RES["costs"].append({"tag": tag, "secs": round(time.time() - t0, 2), "dmb": d, "mb": m1})
    print("COST {0:<40} secs {1:7.2f}  dMB {2}  private {3}".format(tag, time.time() - t0, d, m1), flush=True)


def body(_):
    print(__doc__, flush=True)
    s.start(); s.discard_work(); W = s.work                                        # noqa: E702
    wb, fsp = K.mod("wiki_build"), GR["fs_tunnel_pairs"]
    print("METER start private {0} MB".format(mb()), flush=True)
    m0, t0 = mb(), time.time(); lv = wb.read_live(W, fs_pairs=fsp); note("whole read_live #1", t0, m0)        # noqa: E702
    m0, t0 = mb(), time.time(); lv = wb.read_live(W, fs_pairs=fsp); note("whole read_live #2", t0, m0)        # noqa: E702
    m0, t0 = mb(), time.time(); lv = wb.read_live(W, fs_pairs=fsp); note("whole read_live #3", t0, m0)        # noqa: E702
    m0, t0 = mb(), time.time(); g.report_all(W, "GObject"); note("part report_all GObject #1", t0, m0)       # noqa: E702
    m0, t0 = mb(), time.time(); g.report_all(W, "GObject"); note("part report_all GObject #2", t0, m0)       # noqa: E702
    m0, t0 = mb(), time.time(); AT.read_terms(W, op=AT.OP_ALLTERMS_V1); note("part read_terms OpAllTerms_v1 #1", t0, m0)   # noqa: E702
    m0, t0 = mb(), time.time(); AT.read_terms(W, op=AT.OP_ALLTERMS_V1); note("part read_terms OpAllTerms_v1 #2", t0, m0)   # noqa: E702
    m0, t0 = mb(), time.time(); dl = [int(o["uid"]) for o in g.report_all(W, "Diagram")]; note("route report_all Diagram #1", t0, m0)   # noqa: E702
    m0, t0 = mb(), time.time(); dl = [int(o["uid"]) for o in g.report_all(W, "Diagram")]; note("route report_all Diagram #2", t0, m0)   # noqa: E702
    rows = K.mod("stagexec").dedupe((lv or {}).get("terminals") or GR["terminals"])
    s.fact("W the whole read returned {0} rows (the recorded graph holds {1})".format(len(rows), len(GR["terminals"])))
    by = collections.defaultdict(list)
    for r in rows:
        by[r["owner_uid"]].append(r)
    pick, per = [], collections.Counter()
    for u in sorted(by):
        c = by[u][0]["owner_class"]
        if per[c] < 2 and len(pick) < 30:
            per[c] += 1; pick.append(u)                                            # noqa: E702
    for u in pick:
        rs = by[u]; c = rs[0]["owner_class"]                                       # noqa: E702
        fd = collections.Counter(r.get("frame_diagram") for r in rs).most_common(1)[0][0]
        rec = {"owner": u, "class": c, "n_whole": len(rs), "term_classes": sorted(set(r["term_class"] for r in rs)), "frame": fd}
        try:
            di = dl.index(int(fd)) if int(fd) in dl else None
            if di is None:
                rec["addressable"] = "frame #{0} not in the Diagram list".format(fd)
            else:
                m0, t0 = mb(), time.time(); nl = [int(x["uid"]) for x in g.node_labels(W, di)]; note("node_labels d{0} (#{1} {2})".format(di, u, c), t0, m0)   # noqa: E702
                if u not in nl:
                    rec["addressable"] = "not in Diagram[{0}].Nodes[] ({1} nodes)".format(di, len(nl))
                else:
                    m0, t0 = mb(), time.time(); nu, nr = g.node_terms_uids(W, di, nl.index(u)); note("node_terms_uids #{0} {1}".format(u, c), t0, m0)   # noqa: E702
                    got = set((int(x["uid"]), x["name"], bool(x["is_source"]), int(x["wire"])) for x in nr)
                    want = set((r["term_uid"], r["term_name"], bool(r["is_source"]), r["wire_uid"]) for r in rs)
                    rec.update({"addressable": "yes", "echo": nu, "n_node": len(nr), "equal": got == want,
                                "only_node": sorted(got - want)[:6], "only_whole": sorted(want - got)[:6]})
        except Exception as e:                                                     # noqa: BLE001
            rec["addressable"] = "error {0}".format(str(e)[:160])
        RES["nodes"].append(rec)
        print("NODE {0}".format(json.dumps(rec, default=str)), flush=True)
    s.gate("N every sampled owner was measured ({0} owners, {1} classes)".format(len(pick), len(per)), len(RES["nodes"]) == len(pick), len(pick))
    if not DRY:
        json.dump(RES, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    s.fact("J measurement json -> {0}".format(OUT))


if __name__ == "__main__":
    rc = K.run(body, s)
    gone = DRY or K.mod("stagexec").kill_labview_at_exit()
    print("GATE GONE LabVIEW gone: {0}".format("PASS" if gone else "FAIL"), flush=True)
    sys.exit(rc if gone else 1)
