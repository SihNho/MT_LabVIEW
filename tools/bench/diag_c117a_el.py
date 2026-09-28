r"""diag_c117a_el - card 117-1 L4 (PD233(c), 231(d)): the FULL Error List of the SAVED L2-R2 file (tools/bench/stage_d1_l2r2.json l2r2 final + md5)
read by tools/errorlist_check.py main() UNCHANGED (Ctrl+E/Ctrl+L, per-item double-click, Esc, md5 before/after, lv_errorlist max_steps 180) against
the R1 bed's expected file. PRIOR ART: diag_c116b_scratch_el.py MODE 'final' (this is its cut; the ONLY change: the pin is PD233(c)'s
loose-ends == 22 instead of plan_l2r2_pred.json's 24; the other classes are REPORTED with the 116-2 scratch measurement 1 / 20 / 10 beside them,
diag_c116b_scratch_el.log:114-116). PASS writes errorlist_expected_D1_l2_r2_<ts>.json (R1's entries, each count = the count this read USED,
nothing new licensed) and errorlist_check.reverdict must say OK; otherwise the mismatch table is printed and no file is written.
PREDICTION: reader gates True; extra []; loose-ends 22; reverdict OK; file md5 unchanged; LabVIEW gone. Never saves or runs a VI.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c117a_el.log -- py -u tools/bench/diag_c117a_el.py"""
import glob, json, os, subprocess, sys, time                                         # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench"), os.path.join("tools", "recipes")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
PREV = os.path.join(B, "errorlist_expected_D1_l2_r1_20260928_055441.json")
ST = json.load(open(os.path.join(B, "stage_d1_l2r2.json"), encoding="utf-8"))["l2r2"]
NEW, PIN = ST["final"], ST["md5"]
STEM = os.path.splitext(os.path.basename(NEW or "none"))[0]
LOOSE_PIN, SCRATCH_116_2 = 22, {"loose": 22, "nosource": 1, "notconn": 20, "other": 10}
gates, out = [], []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def klass(label):
    t = str(label).lower()
    return "nosource" if "has no source" in t else ("loose" if "loose ends" in t else ("notconn" if "not connected to anything" in t else "other"))


gate("K saved L2-R2 on disk, md5 == stage_d1_l2r2.json pin, name D1_l2_r2_*", bool(NEW) and os.path.exists(NEW) and EC.md5(NEW) == PIN
     and os.path.basename(NEW).startswith("D1_l2_r2_"), (NEW, PIN))
if gates[-1][1]:
    before = set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM)))
    EC._lv_imports()
    E, _orig, RD = EC.E, EC.E.read, {}

    def _read(*a, **k):
        k["max_steps"] = 180
        r = _orig(*a, **k); RD["max_steps"] = r.get("max_steps"); return r              # noqa: E702
    E.read, sys.argv = _read, [sys.argv[0], "--vi", NEW, "--expected", PREV]
    EC.main()
    new = sorted(p for p in set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM))) - before if not p.endswith(("_raw.json", "_reuse.json")))
    gate("R the reader wrote ONE read file (max_steps {0})".format(RD.get("max_steps")), len(new) == 1, new)
    if len(new) == 1:
        R = json.load(open(new[0], encoding="utf-8"))
        for k, v in sorted((R.get("gates") or {}).items()):
            gate("EL {0}".format(k), v)
        pv = json.load(open(PREV, encoding="utf-8"))
        use = R.get("licence_usage") or []
        rows = [(e.get("label"), int(e.get("count", 1)), use[i]["used"] if i < len(use) else None) for i, e in enumerate(pv["expected"])]
        got = {"loose": 0, "nosource": 0, "notconn": 0, "other": 0}
        for lab, c, u in rows:
            print("  FACT TABLE {0:<90} R1 {1:>3} used {2}".format(str(lab)[:90], c, u), flush=True)
            got[klass(lab)] += u or 0
        for x in R.get("extra") or []:
            print("  FACT EXTRA {0}".format(x), flush=True); got[klass(x.get("label") if isinstance(x, dict) else x)] += 1   # noqa: E702
        got["total"] = sum(got[k] for k in ("loose", "nosource", "notconn", "other"))
        print("  FACT items {0}; classes read {1}; 116-2 scratch {2}".format(R.get("item_count"), got, SCRATCH_116_2), flush=True)
        gate("NC extra == [] (no item outside R1's licence classes)", not R.get("extra"), len(R.get("extra") or []))
        gate("PIN loose-ends == {0} (PD233(c))".format(LOOSE_PIN), got["loose"] == LOOSE_PIN, got)
        if all(ok for _l, ok in gates):
            d = dict(pv, bed=NEW, bed_md5=PIN, expected=[dict(e, count=u) for e, (_l, _c, u) in zip(pv["expected"], rows) if u],
                     total=sum(u for _l, _c, u in rows if u),
                     decided_by="card 117-1 L4 (mechanical, diag_c117a_el.py): R1's licences, each count set to the count this read USED; loose-ends == 22 "
                                "(docs/d1-loop12-17-split-plan.md PD233(c)); nothing new licensed",
                     measured_from=os.path.relpath(new[0], ROOT), r2_delta=[[lab, c, u] for lab, c, u in rows if u != c])
            d.pop("r1_delta", None)
            out.append(os.path.join(B, "errorlist_expected_%s.json" % STEM))
            json.dump(d, open(out[-1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            verdict, rv = EC.reverdict(NEW, new[0], new[0].replace(".json", "_raw.json"), expected_path=out[-1])
            gate("V reverdict of this read against {0}: OK".format(os.path.basename(out[-1])), verdict == "OK", rv)
        else:
            print("  FACT NO expected file written (mismatch table above)", flush=True)
subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
gate("H LabVIEW gone; file md5 unchanged by the read", gone and bool(NEW) and EC.md5(NEW) == PIN)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(p, ROOT), "md5": EC.md5(p)} for p in out])), flush=True)
sys.exit(0 if ff is None else 1)
