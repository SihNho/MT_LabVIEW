r"""diag_c114_errorlist - card 114-1 P7: the FULL Error List of the saved L2-B3 file (claudeDev\D1_l2_b3_*.vi, path + md5 pinned from
tools/bench/stage_d1_l2b3.json) read by tools/errorlist_check.py main() UNCHANGED (scratch copy, Ctrl+E/Ctrl+L, per-item double-click, Esc,
bed md5 before/after) against the B2b bed's expected file (65 items), lv_errorlist.read max_steps=180. Never saves or runs a VI. THEN, offline:
ONLY IF every reader gate holds and extra == [] (no item outside B2b's licences), the L2-B3 expected file = B2b's entries with each count set to
the count this read USED (nothing new licensed; lowered counts = the B3 rows' effect, `b3_delta`), and errorlist_check.reverdict of this read
against it must say OK. Otherwise the mismatch table is printed and NO expected file is written.
PRIOR ART: diag_c113d_errorlist.py (this is its cut: B2a file/expected -> B2b, B2b -> B3). PREDICTION: gates all True; extra []; reverdict OK.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c114_errorlist.log -- py -u tools/bench/diag_c114_errorlist.py"""
import glob, json, os, sys                                                           # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench"), os.path.join("tools", "recipes")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
PREV = os.path.join(B, "errorlist_expected_D1_l2_b2b_20260928_015450.json")
ST = json.load(open(os.path.join(B, "stage_d1_l2b3.json"), encoding="utf-8"))["l2b3"]
NEW, PIN = ST["final"], ST["md5"]
STEM = os.path.splitext(os.path.basename(NEW))[0]
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


gate("K new file on disk, md5 == stage_d1_l2b3.json pin", os.path.exists(NEW) and EC.md5(NEW) == PIN, (NEW, PIN))
out_exp, verdict = None, None
if gates[-1][1]:
    before = set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM)))
    EC._lv_imports()
    E, _orig, RD = EC.E, EC.E.read, {}

    def _read(*a, **k):
        k["max_steps"] = 180
        r = _orig(*a, **k); RD["max_steps"] = r.get("max_steps"); return r              # noqa: E702
    E.read, sys.argv = _read, [sys.argv[0], "--vi", NEW, "--expected", PREV]
    rc = EC.main()
    new = sorted(p for p in set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM))) - before if not p.endswith(("_raw.json", "_reuse.json")))
    gate("R the reader wrote ONE read file (max_steps {0})".format(RD.get("max_steps")), len(new) == 1, new)
    if len(new) == 1:
        R = json.load(open(new[0], encoding="utf-8"))
        for k, v in sorted((R.get("gates") or {}).items()):
            gate("EL {0}".format(k), v)
        print("  FACT items {0} / window N {1}; extra {2}; errors {3}".format(R.get("item_count"), R.get("n_reported"), len(R.get("extra") or []), R.get("errors")), flush=True)
        for x in R.get("extra") or []:
            print("  FACT EXTRA {0}".format(x), flush=True)
        pv = json.load(open(PREV, encoding="utf-8"))
        use = R.get("licence_usage") or []
        rows = [(e.get("label"), int(e.get("count", 1)), use[i]["used"] if i < len(use) else None) for i, e in enumerate(pv["expected"])]
        for lab, c, u in rows:
            print("  FACT TABLE {0:<90} B2b {1:>3} used {2}".format(str(lab)[:90], c, u), flush=True)
        if all(R.get("gates", {}).values()) and not R.get("extra"):
            d = dict(pv, bed=NEW, bed_md5=PIN, expected=[dict(e, count=u) for e, (_l, _c, u) in zip(pv["expected"], rows) if u],
                     decided_by="card 114-1 P7 (mechanical, script diag_c114_errorlist.py): B2b's explicit licences (errorlist_expected_D1_l2_b2b_20260928_015450.json), "
                                "each count lowered to the count this read used; nothing new licensed (extra == [])",
                     measured_from=os.path.relpath(new[0], ROOT), b3_delta=[[lab, c, u] for lab, c, u in rows if u != c])
            d.pop("b2b_delta", None)
            d.pop("b2a_delta", None)
            out_exp = os.path.join(B, "errorlist_expected_%s.json" % STEM)
            json.dump(d, open(out_exp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            verdict, rv = EC.reverdict(NEW, new[0], new[0].replace(".json", "_raw.json"), expected_path=out_exp)
            gate("V reverdict of this read against {0}: OK".format(os.path.basename(out_exp)), verdict == "OK", rv)
        else:
            print("  FACT NO expected file written: reader gates or extra items (mismatch table above)", flush=True)
            gate("V extra == [] and every reader gate True (precondition of the expected file)", False, len(R.get("extra") or []))
import subprocess, time                                                              # noqa: E401,E402
subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
gate("H LabVIEW gone; new file md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
     and EC.md5(NEW) == PIN)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(out_exp, ROOT), "md5": EC.md5(out_exp)}] if out_exp else [])), flush=True)
sys.exit(0 if ff is None else 1)
