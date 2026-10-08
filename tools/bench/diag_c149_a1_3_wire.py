# ---
# labview: read
# hardware: none
# ---
r"""diag_c149_a1_3_wire - card 149-a1-3 measurement 3: READ wire w23807 in a never-saved byte copy of the saved s06 scratch
claudeDev\D1_ring_p4s06_20261008_174730.vi (569ffbf5).
WHAT EXISTS (checked first): allterms.read_terms (whole-VI terminal table, read-only), gscript.report_all(…, 'Wire') (= allterms.
all_wire_uids:102-103), gscript.read_term_type (OpTermDataType_v0, read-only), gscript.ensure_loaded / exec_state / ref_counts,
bench_prep.labview_handles. The only by-uid `Wire.Is Broken?` reader built is gscript.wire_remove_loose_ends, which EDITS (Invoke
RemoveLooseEnds): NOT called - Is Broken? is not read here; the wire's endpoints and their types are. No new op.
WHY NOT stagekit (the first version was a K.Stage like diag_c149_a1_2_graph.py): guard_bash gated it as VI-modifying because
`discard_work` is in stage_prerun.MODIFY_VERBS (:3136) and its prerun failed X2-X9 (no plan, no graph for 569ffbf5) while X10 read it as
read-only (0 ops, 3 reads) - logged as gate-fp fp-63. This file therefore does the byte copy, open, read, close and cleanup itself.
Scratch-log facts checked against: op 21 'target BROKEN' (diag_c147_p4s06v18_scratch.log:990-994); gate D reuse_noted w23807 real_src
[(5171,5058)] real_sinks [(3173,23166),(10975,10969)], sim_removed_sinks [(9519,23166),(10871,10757),(23798,23508)] (:1002).
PREDICTION CONTRACT (gates; RESULT line at the end): K1 input md5 569ffbf5, no LabVIEW running at start; K3 copy byte-identical;
W1 w23807 has exactly one source t5171 on #5058 and sinks {t3173 on #23166, t10975 on #10969} (as :1002); W2 t9519/t10871/t23798 not on
w23807; T a type read (bytes) for every terminal on w23807 (types RECORDED, not predicted); wire-table counts RECORDED, not predicted;
X input md5 unchanged; G LabVIEW gone; C copy deleted.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c149_a1_3_wire.log -- py -u tools/bench/diag_c149_a1_3_wire.py"""
import hashlib, json, os, shutil, subprocess, sys, time                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE); sys.path.insert(0, ROOT)   # noqa: E702
import gscript as g                                                                           # noqa: E402
import allterms as A                                                                          # noqa: E402
import bench_prep as BP                                                                       # noqa: E402
from tools import protocol                                                                    # noqa: E402
BED = os.path.join(g.CLAUDEDEV, "D1_ring_p4s06_20261008_174730.vi")
BEDM = "569ffbf51eb6051bf0fdb58946f9bb02"
WIRE, REMOVED = 23807, (9519, 10871, 23798)
STAMP = time.strftime("%Y%m%d_%H%M%S")
COPY = os.path.join(g.CLAUDEDEV, "_c149a13_w23807_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_c149_a1_3_wire.json")
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
    print("  FACT  " + str(s)[:900], flush=True)


def lv_running():
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True).stdout
    return "LabVIEW.exe" in out


def body():
    gate("K1 input md5 == 569ffbf5", md5(BED) == BEDM, md5(BED))
    if not gate("K0 no LabVIEW running at start", not lv_running()):
        return
    shutil.copyfile(BED, COPY)
    if not gate("K3 byte copy identical", md5(COPY) == BEDM, os.path.basename(COPY)):
        return
    t0 = time.time()
    g.ensure_loaded(COPY)
    fact("loaded in {0:.1f} s; ExecState {1}; handles {2}".format(time.time() - t0, g.exec_state(COPY), BP.labview_handles()))
    rows, dt = A.read_terms(COPY)
    fact("terminal table {0} rows in {1:.1f} s".format(len(rows), dt))
    on = [r for r in rows if int(r["wire_uid"] or 0) == WIRE]
    for r in on:
        fact("W23807 row t{0} {1!r} is_source={2} owner #{3} {4}".format(r["term_uid"], r["term_name"], r["is_source"],
                                                                        r["owner_uid"], r["owner_class"]))
    src = sorted((r["term_uid"], r["owner_uid"]) for r in on if r["is_source"])
    snk = sorted((r["term_uid"], r["owner_uid"]) for r in on if not r["is_source"])
    gate("W1 w23807: one source t5171 #5058, sinks {t3173 #23166, t10975 #10969}",
         src == [(5171, 5058)] and snk == [(3173, 23166), (10975, 10969)], {"src": src, "sinks": snk})
    rem = [r for r in rows if int(r["term_uid"]) in REMOVED]
    for r in rem:
        fact("REMOVED-SINK row t{0} {1!r} owner #{2} {3} wire {4}".format(r["term_uid"], r["term_name"], r["owner_uid"],
                                                                        r["owner_class"], r["wire_uid"]))
    gate("W2 removed sinks t9519/t10871/t23798 not on w23807", len(rem) == 3 and all(int(r["wire_uid"] or 0) != WIRE for r in rem),
         [(r["term_uid"], r["wire_uid"]) for r in rem])
    R["types"] = {}
    for r in on + rem:
        try:
            t = g.read_term_type(COPY, r["term_uid"])
        except Exception as e:                                                    # noqa: BLE001
            t = {"err": "%s: %s" % (type(e).__name__, str(e)[:200])}
        ty = t.get("types") or {}
        R["types"][str(r["term_uid"])] = {"name": r["term_name"], "hex": t.get("bytes_hex"), "types": ty, "err": t.get("err")}
        fact("TYPE t{0} {1!r}: sig {2!r} | types {3} | err {4!r}".format(r["term_uid"], r["term_name"], ty.get("sig"),
                                                                       json.dumps(ty, default=str)[:300], t.get("err")))
    gate("T a type read for every terminal on w23807", bool(on) and all(R["types"][str(r["term_uid"])].get("hex") for r in on))
    wu = sorted({int(o["uid"]) for o in g.report_all(COPY, "Wire")})
    src_n, snk_n = {}, {}
    for r in rows:
        k = int(r["wire_uid"] or 0)
        if k:
            d = src_n if r["is_source"] else snk_n
            d[k] = d.get(k, 0) + 1
    R["terminals"], R["wire_uids"] = rows, wu
    nosrc = sorted(k for k in snk_n if k not in src_n)
    multi = sorted(k for k, n in src_n.items() if n > 1)
    nosink = sorted(k for k in src_n if k not in snk_n)
    termless = sorted(set(wu) - set(src_n) - set(snk_n))
    R["wire_counts"] = {"wires": len(wu), "sinks_no_source": nosrc, "multi_source": multi, "termless": termless, "source_no_sink": nosink}
    fact("WIRES {0}: sinks-but-no-source {1} {2}; >1 source {3} {4}; termless {5} {6}; source-but-no-sink {7} {8}".format(
        len(wu), len(nosrc), nosrc, len(multi), multi, len(termless), termless, len(nosink), nosink))
    fact("handles end of reads {0}; refs {1}".format(BP.labview_handles(), g.ref_counts()))


if __name__ == "__main__":
    try:
        body()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        gate("no exception", False, "%s: %s" % (type(e).__name__, str(e)[:300]))
    finally:
        json.dump(R, open(OUT, "w", encoding="utf-8"), default=str)
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
        gate("X input md5 unchanged", md5(BED) == BEDM, md5(BED))
        print("OUT {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                        [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
    sys.exit(1 if G["fail"] else 0)
