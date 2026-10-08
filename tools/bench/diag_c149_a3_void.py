# ---
# labview: read
# hardware: none
# ---
r"""diag_c149_a3_void - card 149-a3-2 step 5 (PD363(c)): Void-type census of WIRE terminals, PLAIN gscript reads only (no edit verb, no
`Is Broken?`, no stagekit / discard_work - fp-63). argv[1] = 's06' (the adopted claudeDev\D1_ring_p4s06_20261008_174730.vi 569ffbf5) or
's05' (claudeDev\D1_ring_p4s05_20261008_002621.vi 3f9ac26b). Either way a never-saved BYTE COPY is made first (the input itself is never opened),
loaded in a fresh LabVIEW, read, LabVIEW killed, the copy deleted. One file per run (two ~600 MB loads in one instance exceed X10's 680 MB).
WHAT EXISTS (checked first): allterms.read_terms (whole-VI terminal table, one op run), gscript.report_all(t, 'Terminal') (Traverse order =
read_term_type's `index`), gscript.read_term_type (OpTermDataType_v0, read-only, PER TERMINAL - no bulk type reader exists in tools/*.py),
gscript.ensure_loaded / exec_state / ref_counts, bench_prep.labview_handles. Open/close/cleanup copied from diag_c149_a1_3_types.py / _wire.py.
ORDER + CAP: wired terminals (wire_uid != 0) sorted by (wire uid DESC, term uid); type reads stop at TCAP s per file (the per-read time is not
known: diag_c149_a1_3_types.log read 11 terminals in a 96 s run including the load) - the measured rate and the coverage are FACTS of the run.
Void flag: any type descriptor name containing 'void' (case-insensitive) or no bytes / parse error (recorded separately).
PREDICTION CONTRACT: K1 input md5 == pin; K0 no LabVIEW at start; K3 copy byte-identical; R terminal table rows > 0; T every attempted read
returned bytes or an error string; COV coverage RECORDED (complete == every wired terminal read within TCAP: not predicted); X input md5
unchanged; G LabVIEW gone; C copy deleted. Void counts are the measurement (not predicted).
    py tools/bgrun.py --material --max-min 16 --log tools/bench/diag_c149_a3_void_<tag>.log -- py -u tools/bench/diag_c149_a3_void.py <tag>"""
import hashlib, json, os, shutil, subprocess, sys, time                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE); sys.path.insert(0, ROOT)   # noqa: E702
import gscript as g                                                                           # noqa: E402
import allterms as A                                                                          # noqa: E402
import bench_prep as BP                                                                       # noqa: E402
from tools import protocol                                                                    # noqa: E402
TAG = sys.argv[1] if len(sys.argv) > 1 else "s06"
INP = {"s06": ("D1_ring_p4s06_20261008_174730.vi", "569ffbf51eb6051bf0fdb58946f9bb02"),
       "s05": ("D1_ring_p4s05_20261008_002621.vi", "3f9ac26b69179eb53c202d90407ce7ee")}[TAG]
BED, BEDM = os.path.join(g.CLAUDEDEV, INP[0]), INP[1]
TCAP = 600.0
COPY = os.path.join(g.CLAUDEDEV, "_c149a32_void_%s_%s.vi" % (TAG, time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "diag_c149_a3_void_%s.json" % TAG)
G = {"pass": 0, "fail": 0, "first": None}
R = {"tag": TAG, "vi": BED, "md5": BEDM, "copy": COPY, "tcap_s": TCAP, "rows": [], "types": {}}


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
    return "LabVIEW.exe" in subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True).stdout


def body():
    gate("K1 input md5 == pin", md5(BED) == BEDM, md5(BED))
    if not gate("K0 no LabVIEW running at start", not lv_running()):
        return
    shutil.copyfile(BED, COPY)
    if not gate("K3 byte copy identical", md5(COPY) == BEDM, os.path.basename(COPY)):
        return
    t0 = time.time()
    g.ensure_loaded(COPY)
    fact("loaded in {0:.1f} s; ExecState {1}; handles {2}".format(time.time() - t0, g.exec_state(COPY), BP.labview_handles()))
    rows, dt = A.read_terms(COPY)
    R["rows"] = rows
    order = [int(o["uid"]) for o in g.report_all(COPY, "Terminal")]
    idx = dict((u, i) for i, u in enumerate(order))
    wired = sorted((r for r in rows if int(r["wire_uid"] or 0)), key=lambda r: (-int(r["wire_uid"]), int(r["term_uid"])))
    fact("terminal table {0} rows in {1:.1f} s; Traverse order {2}; wired terminals {3} on {4} wires".format(
        len(rows), dt, len(order), len(wired), len(set(int(r["wire_uid"]) for r in wired))))
    gate("R terminal table rows > 0 and every wired terminal in the Traverse order", wired and all(int(r["term_uid"]) in idx for r in wired),
         [r["term_uid"] for r in wired if int(r["term_uid"]) not in idx][:10])
    t1, n = time.time(), 0
    for r in wired:
        if time.time() - t1 > TCAP:
            break
        u = int(r["term_uid"])
        try:
            t = g.read_term_type(COPY, u, index=idx.get(u))
        except Exception as e:                                                    # noqa: BLE001
            t = {"err": "%s: %s" % (type(e).__name__, str(e)[:200])}
        ty = t.get("types") or {}
        names = [str(d.get("name")) for d in (ty.get("tds") or [])]
        R["types"][str(u)] = {"wire": int(r["wire_uid"]), "src": bool(r["is_source"]), "owner": int(r["owner_uid"]), "cls": r["owner_class"],
                              "name": r["term_name"], "tds": names, "codes": [d.get("code") for d in (ty.get("tds") or [])],
                              "top": ty.get("top"), "hex": (t.get("bytes_hex") or "")[:200], "err": t.get("err") or ty.get("err"),
                              "void": any("void" in x.lower() for x in names)}
        n += 1
        if n in (10, 50, 200) or n % 500 == 0:
            fact("rate after {0} reads: {1:.2f} s/read".format(n, (time.time() - t1) / n))
    el = time.time() - t1
    R["coverage"] = {"read": n, "wired": len(wired), "seconds": round(el, 1), "s_per_read": round(el / max(n, 1), 3),
                     "complete": n == len(wired), "last_wire": int(wired[n - 1]["wire_uid"]) if n else None}
    fact("COVERAGE {0}".format(R["coverage"]))
    gate("T every attempted read returned bytes or an error string",
         all(v["hex"] or v["err"] for v in R["types"].values()), [k for k, v in R["types"].items() if not (v["hex"] or v["err"])][:10])
    vo = [(k, v) for k, v in R["types"].items() if v["void"]]
    er = [(k, v) for k, v in R["types"].items() if v["err"] and not v["void"]]
    fact("VOID {0} terminals; read errors {1}".format(len(vo), len(er)))
    for k, v in vo[:60]:
        fact("VOID w{0} t{1} {2} #{3} {4} {5!r} tds {6}".format(v["wire"], k, "SRC" if v["src"] else "snk", v["owner"], v["cls"], v["name"], v["tds"]))
    gate("COV every wired terminal read within TCAP (coverage is a FACT; FAIL = census incomplete)", R["coverage"]["complete"], R["coverage"])
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
