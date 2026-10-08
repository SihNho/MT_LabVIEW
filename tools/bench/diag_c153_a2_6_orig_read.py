# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/brief_153-a2-6.md
# ---
r"""diag_c153_a2_6_orig_read - card 153-a2-6 (retry of 153-a2-1, PD371(c)): ONE read-only read of a claudeDev BYTE COPY of the CURRENT
original `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` (md5 2f048e3a, census-time c39f36e0): which terminal feeds 'frame index'
of its `save trace.vi` call #376.
PRIOR ART (grepped first, nothing new built): readers gscript.report_all(W,'GObject') (leaf class + owner class) and
allterms.read_terms(W, OpAllTerms_v1) (term_uid, name, is_source, wire_uid, owner_uid, owner_class, frame_diagram) = the two inputs
wiki_build.read_live (wiki_build.py:233-256) used for S1's docs/wiki/subvi/D1_s1_copy.json. Skeleton = diag_c149_a1_3_wire.py (plain
gscript; the stagekit form is gated VI-modifying via discard_work - gate-fp fp-63, deduped by this card). No original is opened.
Census side: tools/bench/orig_3state_nodeterms.json. S1 side: w3268 <- term #644 owner Diagram #639 (While #637 body),
D1_s1_copy.json:36385-36392 / docs/cycle27-plan.md:3748-3751.
PREDICTION: K0 no LabVIEW at start; copy md5 == original md5 == 2f048e3a; R1 #376 has ONE 'frame index' sink row; R2 its wire == 3268;
R3 ONE source row, owner_class Diagram whose own owner class is WhileLoop (=> the loop's iteration terminal i, the only diagram-owned
SOURCE); R4 that source is term #644 on Diagram #639 (S1's uids); R5 w3268 node-sink owners == census {2136,3191,376,10068,1114,29240};
R6 #5119 'x-y' does not feed #376; H handles flat +-100; G LabVIEW gone; C copy deleted; X original md5 after == before; I invariants.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c153_a2_6_orig_read.log -- py -u tools/bench/diag_c153_a2_6_orig_read.py"""
import datetime, hashlib, json, os, shutil, subprocess, sys, time                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE); sys.path.insert(0, ROOT)   # noqa: E702
import gscript as g                                                                           # noqa: E402
import allterms as A                                                                          # noqa: E402
import bench_prep as BP                                                                       # noqa: E402
from tools import protocol                                                                    # noqa: E402
ORIG = os.path.join(os.path.dirname(ROOT), "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
OMD5 = "2f048e3a18de3b5e3ca8368f6a24dae0"
COPY = os.path.join(g.CLAUDEDEV, "scratch_c153_a2_6_orig.vi")
OUT = os.path.join(HERE, "diag_c153_a2_6_orig_read.json")
CENSUS_SINKS = {2136, 3191, 376, 10068, 1114, 29240}
INV = [("604529e8", "tools/stagekit.py"), ("207beb0d", "tools/addrcheck.py"), ("1bab9cf9", "tools/stagexec.py"), ("1a80236e", "tools/gscript.py"),
       ("c739eb86", "tools/stage_prerun.py"), ("78b8d5a1", "tools/stagesim.py"), ("13be0847", "tools/vigraph.py"),
       ("eb1d0f31", os.path.join(g.CLAUDEDEV, "D1_ring_p4s09_20261009_060515.vi")), ("22f967b5", "tools/bench/graph_ring_p4s09_20261009_062044.json"),
       ("b9e6849f", "tools/bench/orig_3state_nodeterms.json"), ("5de014fe", "docs/wiki/subvi/D1_s1_copy.json")]
G = {"pass": 0, "fail": 0, "first": None}
R = {"copy": COPY}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and not G["first"]:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)
    return ok


def fact(s):
    print("  FACT  " + str(s)[:1200], flush=True)


def lv_running():
    return "LabVIEW.exe" in subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True).stdout


def inv(tag):
    bad = [(p, md5(p if os.path.isabs(p) else os.path.join(ROOT, p))) for pin, p in INV
           if not md5(p if os.path.isabs(p) else os.path.join(ROOT, p)).startswith(pin)]
    fact("INV {0}: {1}".format(tag, "all {0} pinned md5s OK".format(len(INV)) if not bad else bad))
    return not bad


def stat(tag):
    b, st = open(ORIG, "rb").read(), os.stat(ORIG)
    fact("ORIGINAL {0}: size {1} mtime {2} md5 {3}".format(tag, st.st_size, datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
                                                          hashlib.md5(b).hexdigest()))
    return hashlib.md5(b).hexdigest()


def body():
    R["m0"], R["i0"] = stat("BEFORE"), inv("BEFORE")
    gate("K1 original md5 == 2f048e3a", R["m0"] == OMD5, R["m0"])
    if not gate("K0 no LabVIEW running at start", not lv_running()) or os.path.exists(COPY):
        gate("K2 no stale copy", not os.path.exists(COPY), COPY)
        return
    shutil.copyfile(ORIG, COPY)
    if not gate("C1 ONE byte copy {0}: copy md5 == original md5".format(os.path.basename(COPY)), md5(COPY) == R["m0"], md5(COPY)):
        return
    t0 = time.time()
    g.ensure_loaded(COPY)
    h0 = BP.labview_handles()
    fact("loaded copy in {0:.1f} s; ExecState {1}; handles {2}".format(time.time() - t0, g.exec_state(COPY), h0))
    objs = dict((int(o["uid"]), (o["class"], o["owner"])) for o in g.report_all(COPY, "GObject"))
    rows, dt = A.read_terms(COPY, op=A.OP_ALLTERMS_V1)
    h1 = BP.labview_handles()
    fact("READ GObject census {0} objects; OpAllTerms_v1 {1} terminal rows in {2:.1f} s; handles {3} -> {4}; refs {5}".format(
        len(objs), len(rows), dt, h0, h1, g.ref_counts()))
    fact("OBSERVED #376 class/owner {0}".format(objs.get(376)))
    fi = [r for r in rows if r["owner_uid"] == 376 and r["term_name"] == "frame index"]
    for r in fi:
        fact("OBSERVED #376 'frame index' row {0}".format(json.dumps(r)))
    gate("R1 #376 has ONE 'frame index' sink row", len(fi) == 1 and not fi[0]["is_source"], len(fi))
    w = fi[0]["wire_uid"] if len(fi) == 1 else None
    on = [r for r in rows if w is not None and r["wire_uid"] == w]
    src, snk = [r for r in on if r["is_source"]], [r for r in on if not r["is_source"]]
    for r in src:
        fact("OBSERVED SOURCE of w{0}: {1} | term leaf class {2!r} | owner #{3} is {4}".format(
            w, json.dumps(r), objs.get(r["term_uid"], ("?",))[0], r["owner_uid"], objs.get(r["owner_uid"])))
    fact("OBSERVED SINKS of w{0}: {1}".format(w, sorted((r["owner_uid"], r["owner_class"], r["term_name"]) for r in snk)))
    gate("R2 'frame index' wire == 3268 (census + S1 uid)", w == 3268, w)
    ok3 = len(src) == 1 and src[0]["owner_class"] == "Diagram" and (objs.get(src[0]["owner_uid"]) or ("", ""))[1] == "WhileLoop"
    gate("R3 ONE source: a Diagram-owned terminal on a WhileLoop body (= the loop's i)", ok3, [(r["term_uid"], r["owner_uid"], r["owner_class"]) for r in src])
    gate("R4 SAME as S1: source term #644 owner Diagram #639", len(src) == 1 and (src[0]["term_uid"], src[0]["owner_uid"]) == (644, 639),
         [(r["term_uid"], r["owner_uid"]) for r in src])
    nodes = set(r["owner_uid"] for r in snk if r["owner_class"] != "Diagram")
    gate("R5 w3268 sink owners == census set", nodes == CENSUS_SINKS, sorted(nodes ^ CENSUS_SINKS))
    xy = [r for r in rows if r["owner_uid"] == 5119 and r["term_name"] == "x-y"]
    xs = [(r["owner_uid"], r["term_name"]) for r in rows if xy and r["wire_uid"] == xy[0]["wire_uid"] and not r["is_source"]]
    fact("OBSERVED #5119 'x-y' {0} -> sinks {1}".format([(r["wire_uid"], r["is_source"]) for r in xy], xs))
    gate("R6 #5119 'x-y' does not feed #376", len(xy) == 1 and xy[0]["wire_uid"] != w and all(o != 376 for o, _ in xs), xs)
    gate("H handles flat +-100 over the reads", h0 is not None and h1 is not None and abs(h1 - h0) <= 100, (h0, h1))
    R["read"] = {"frame_index": fi, "sources": src, "sinks": snk, "x_y": xy, "x_y_sinks": xs, "handles": [h0, h1],
                 "source_owner": objs.get(src[0]["owner_uid"]) if src else None}


if __name__ == "__main__":
    try:
        body()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        gate("no exception", False, "%s: %s" % (type(e).__name__, str(e)[:300]))
    finally:
        json.dump(R, open(OUT, "w", encoding="utf-8"), default=str, indent=1)
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True)
        for _ in range(20):
            if not lv_running():
                break
            time.sleep(1)
        gate("G LabVIEW gone", not lv_running())
        if os.path.exists(COPY):
            try:
                os.remove(COPY)
            except OSError as e:
                fact("copy delete failed: %s" % e)
        gate("C copy deleted", not os.path.exists(COPY), os.path.basename(COPY))
        gate("X original md5 after == before", stat("AFTER") == R.get("m0"))
        gate("I invariant md5s unchanged before and after", inv("AFTER") and R.get("i0"))
        print("OUT {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                        [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
    sys.exit(1 if G["fail"] else 0)
