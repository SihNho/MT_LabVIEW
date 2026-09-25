r"""parity_l2a1_82 - card 82-1 P2/P4 (Pre-decided 187(a)+(b)): READ-ONLY reader-parity measurement on a scratch of D1_k.
Per diagram the L2-A1 plan touches: the REAL Diagram.Nodes[] (class, uid) vs SimReader's listing BEFORE the fit (stagexec at
git HEAD, md5 029ea027...) and AFTER the fit (the working stagexec: ControlTerminals excluded from Nodes[]). Also proves
every ControlTerminal plan end by the 179(b) route (Addr.ct: own uid, owner Diagram, report_all('ControlTerminal')).
PRIOR ART: stagexec.LVReader/SimReader/Addr (reused, no copy); wiki_build.read_live (the graph read the executor uses);
diag_ctlterm_read_80.py (179(b) reader, same Stage skeleton). No op VI built, nothing mutated, nothing saved.
PREDICTION CONTRACT:
  B0 scratch graph == the plan's base graph (compare n == 0)       B1 BEFORE-fit one-side-only rows: REPORTED (expected >0:
  the moved ControlTerminals #5634 #17487 #23541 #17272 listed by SimReader only, on #639)   A1 AFTER-fit one-side-only == 0
  C1 each ControlTerminal plan end addressable by 179(b) on the REAL read      H D1_k md5 unchanged, scratch gone, handles
  before/after RECORDED, LabVIEW gone at exit. Offline re-evaluation data -> tools/bench/parity_l2a1_82_real.json.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/parity_l2a1_82.log -- py -u tools/bench/parity_l2a1_82.py"""
import importlib.util, json, os, subprocess, sys, tempfile, time                  # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, gscript as g, stagesim as SS, stagexec as SX              # noqa: E401,E402
PLAN = os.path.join(K.BENCH, "sim/l2a1/plan_l2a1.json")
P = json.load(open(PLAN, encoding="utf-8"))
BASE = json.load(open(os.path.join(K.ROOT, P["finalized"]["base"]["path"]), encoding="utf-8"))
BED, BED_MD5 = BASE["vi"], BASE["md5"]
ST0 = SX._j(SX._abs(P["finalized"]["step_files"][0]["path"]))["state"]


def old_stagexec():
    """stagexec as it was before card 82-1 (git HEAD), imported from %TEMP% - the BEFORE-fit SimReader."""
    src = subprocess.run(["git", "show", "HEAD:tools/stagexec.py"], cwd=K.ROOT, capture_output=True, timeout=60).stdout
    p = os.path.join(tempfile.gettempdir(), "stagexec_head_82.py")
    open(p, "wb").write(src)
    spec = importlib.util.spec_from_file_location("stagexec_head_82", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m, K.md5(p)


def body(s):
    print(__doc__, flush=True)
    s.start()
    s.discard_work()                                                                # a diagnostic: nothing is saved
    bp = K.mod("bench_prep")
    h0 = bp.labview_handles()
    OLD, om = old_stagexec()
    s.fact("BEFORE-fit stagexec = git HEAD, md5 {0}".format(om))
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=BASE["fs_tunnel_pairs"])
    real = SX.dedupe(lv["terminals"])
    d0 = SX.compare(ST0["terminals"], real, {"obj": {}, "term": {}})
    s.gate("B0 scratch graph == the plan's step_00 graph (terminals, edges, dangling)", d0["n"] == 0, {k: v[:6] for k, v in d0.items() if isinstance(v, list) and v}, fatal=True)
    rd = SX.LVReader(g, s.work)
    diags = SX.touched_diagrams(P, ST0)
    cls_r, cls_s = SX.classes_of(real, lv["objs"]), SX.classes_of(ST0["terminals"], ST0.get("objs"))
    realdump, dl = {}, rd.diagrams()
    for i, d in enumerate(dl):                           # HOLDOUT (review 2026-09-25-parity-l2a1-82-hyp.md test 3): ALL diagrams
        realdump[str(d)] = [[cls_r.get(u, "?"), u] for u in rd.node_uids(i)]
    s.fact("REAL Nodes[] read on {0} diagrams; sizes on the touched ones: {1}".format(
        len(dl), dict((str(d), len(realdump.get(str(d)) or [])) for d in diags)))

    class Fixed(object):                                                            # replays the real listing offline
        def diagrams(self):
            return [int(k) for k in realdump]

        def node_uids(self, didx):
            return [u for _c, u in realdump[str(self.diagrams()[didx])]]
    out = {"diagrams": diags, "real": realdump}
    for tag, mod in (("BEFORE", OLD), ("AFTER", SX)):
        rows, n = SX.reader_parity(Fixed(), mod.SimReader(SX._StateHolder(ST0)), diags, cls_r, cls_s)
        out[tag] = {"n": n, "rows": rows}
        for r in rows:
            s.fact("PARITY {0} diagram #{1}: real {2} sim {3} | only_real {4} | only_sim {5}".format(
                tag, r["diagram"], r.get("n_real"), r.get("n_sim"), r.get("only_real"), r.get("only_sim")))
        s.row("{0}-fit one-side-only Nodes[] entries".format(tag), n, ">0" if tag == "BEFORE" else 0)
    s.gate("A1 AFTER-fit SimReader Nodes[] == REAL Nodes[] on every touched diagram (0 one-side-only; TRAINING set)", out["AFTER"]["n"] == 0, out["AFTER"]["n"])
    alld = [int(k) for k in realdump]
    rows, n = SX.reader_parity(Fixed(), SX.SimReader(SX._StateHolder(ST0)), alld, cls_r, cls_s)
    bad = [r for r in rows if r["only_real"] or r["only_sim"]]
    for r in bad[:25]:
        s.fact("HOLDOUT diagram #{0}: real {1} sim {2} | only_real {3} | only_sim {4}".format(
            r["diagram"], r["n_real"], r["n_sim"], r["only_real"][:8], r["only_sim"][:8]))
    out["HOLDOUT"] = {"n": n, "diagrams": len(alld), "bad": bad}
    s.row("HOLDOUT AFTER-fit one-side-only entries over ALL {0} diagrams ({1} diagrams differ)".format(len(alld), len(bad)), n, 0)
    ad, cts = SX.Addr(rd, ST0.get("owners")), []
    for a in P["actions"]:
        for side, src in (("src", True), ("dst", False)):
            e = a.get(side)
            if isinstance(e, dict) and SS.obj_class(ST0, e.get("uid")) == SX.FP:
                x, _err = s.safe("179(b) #{0}".format(e["term_uid"]), lambda t=e["term_uid"]: ad.ct(real, t), None)
                cts.append((a["id"], e["term_uid"], x[1] if x else None))
                s.fact("CT {0} #{1}: {2}".format(a["id"], e["term_uid"], x[1] if x else "NOT ADDRESSABLE"))
    s.gate("C1 every ControlTerminal plan end addressable by 179(b) on the REAL read ({0} ends)".format(len(cts)),
           cts and all(c[2] for c in cts), cts)
    h1 = bp.labview_handles()
    s.fact("PH handles RECORDED: after open {0} -> after reads {1}".format(h0, h1))
    out.update(cts=cts, handles=[h0, h1])
    json.dump(out, open(os.path.join(K.BENCH, "parity_l2a1_82_real.json"), "w", encoding="utf-8"), indent=1, default=str)
    s.R["parity"] = out
    s.dump()


def offline():
    """--offline: re-evaluate AFTER-fit parity against the SAVED real listing (no LabVIEW) - for the fit iterations."""
    D = json.load(open(os.path.join(K.BENCH, "parity_l2a1_82_real.json"), encoding="utf-8"))

    class Fixed(object):
        def diagrams(self):
            return [int(k) for k in D["real"]]

        def node_uids(self, didx):
            return [u for _c, u in D["real"][str(self.diagrams()[didx])]]
    cls_r = dict((u, c) for v in D["real"].values() for c, u in (v or []))
    sim = SX.SimReader(SX._StateHolder(ST0))
    rows, n = SX.reader_parity(Fixed(), sim, D["diagrams"], cls_r, SX.classes_of(ST0["terminals"], ST0.get("objs")))
    for r in rows:
        print("  FACT  PARITY AFTER(offline TRAINING SET, stagexec md5 {0}) diagram #{1}: real {2} sim {3} | only_real {4} | only_sim {5}".format(
            K.md5(SX.__file__), r["diagram"], r.get("n_real"), r.get("n_sim"), r.get("only_real"), r.get("only_sim")), flush=True)
        ro = [u for _c, u in D["real"][str(r["diagram"])]]                  # review test 2: ORDER, not only the set
        sd = sim.diagrams()
        so = sim.node_uids(sd.index(r["diagram"])) if r["diagram"] in sd else []
        print("  FACT  ORDER diagram #{0}: real order == SimReader order on common uids: {1}".format(
            r["diagram"], [u for u in ro if u in so] == [u for u in so if u in ro]), flush=True)
    print("  {0}  A1off AFTER-fit one-side-only == 0 on the saved real listing (TRAINING SET, not a holdout)  {1}".format(
        "PASS" if n == 0 else "FAIL", n), flush=True)
    alld = [int(k) for k in D["real"]]
    rh, nh = SX.reader_parity(Fixed(), sim, alld, cls_r, SX.classes_of(ST0["terminals"], ST0.get("objs")))
    bad = [(r["diagram"], r["only_real"][:4], r["only_sim"][:4]) for r in rh if r["only_real"] or r["only_sim"]]
    print("  FACT  HOLDOUT(offline) {0} diagrams: one-side-only {1} on {2} diagram(s) {3}".format(len(alld), nh, len(bad), bad[:6]), flush=True)
    n += nh
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if n == 0 else "FAIL",
                                  "gates": {"pass": int(n == 0), "fail": int(n != 0)},
                                  "first_fail": None if n == 0 else "A1off", "artefacts": []}), flush=True)
    return 0 if n == 0 else 1


if __name__ == "__main__" and "--offline" in sys.argv:
    sys.exit(offline())
if __name__ == "__main__":
    st = time.strftime("%Y%m%d_%H%M%S")
    s = K.Stage(BED, BED_MD5, "parity82", work_name="D1_k_scratch_parity82_{0}.vi".format(st), preload=False,
                deadline_min=22, out_json=os.path.join(K.BENCH, "parity_l2a1_82.json"), task="card 82-1")
    rc = K.run(body, s)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4.0)
    tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("H1 LabVIEW process gone at the end", "labview.exe" not in tl)
    s.gate("H2 D1_k md5 unchanged", K.md5(BED) == BED_MD5, K.md5(BED))
    s.gate("H3 scratch copy deleted", not os.path.exists(s.work), s.work)
    s.summary()
    sys.exit(1 if s.fails else 0)
