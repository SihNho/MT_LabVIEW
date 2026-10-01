"""diag_c128_4_checks - card 128-4 OFFLINE (no LabVIEW, no COM; files only). EXISTING FIRST: diag_c127_4_checks.py (run-and-grep
shape), the self-tests below (re-run, not rebuilt), 128-2's donor list (diag_c128_2_donors.log:53).
  D1 BYTE-COPY vi.lib Error to Warning.vi / Merge Errors.vi -> claudeDev DonorErrSel_ErrToWarning.vi / DonorErrSel_MergeErrors.vi
     (shutil.copyfile only; source never opened for writing); md5(copy) == md5(source); uid of record #157 / #529 (128-2 C1)
  D2 census_samples.json parses; its new section create_primitive_nested:vilib_donor cites lines that carry their `expect`
  S  every existing stage_prerun self-test + selftest_census_predict + selftest_case_frame_c124 + c125_1_offline_measure,
     each in its own process, RESULT line PASS (exit 0)
PREDICTION: D1 2/2 md5 equal; D2 PASS; S all PASS (stage_prerun changed only in x5_count / patch_stagekit / main's D reset).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c128_4_checks.log -- py -u tools/bench/diag_c128_4_checks.py"""
import concurrent.futures as CF, hashlib, json, os, shutil, subprocess, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P    # noqa: E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()   # noqa: E731
ok, OUT = [], {}


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, str(d)[:900]), flush=True)


LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DON = [("Error to Warning.vi", "DonorErrSel_ErrToWarning.vi", 157, "Unbundler"),
       ("Merge Errors.vi", "DonorErrSel_MergeErrors.vi", 529, "Select (Function)")]
OUT["donors"] = []
for src, dst, uid, what in DON:
    s, d = os.path.join(LIB, src), os.path.join(CD, dst)
    ms = md5(s)
    shutil.copyfile(s, d)
    rec = {"source": s, "path": d, "md5": md5(d), "source_md5": ms, "uid": uid, "what": what,
           "uid_from": "diag_c128_2_donors.log:53 (DONORS) / :57,:62 (C1 creates)"}
    OUT["donors"].append(rec)
    gate("D1 byte copy {0} -> {1}: md5 equal, source md5 unchanged".format(src, dst), rec["md5"] == ms == md5(s), rec)
CS = json.load(open(os.path.join(B, "census_samples.json"), encoding="utf-8"))
sec = CS["ops"].get("create_primitive_nested:vilib_donor") or {}
bad = []
for v in sec.get("variants", []):
    for c in v["cites"]:
        lines = open(os.path.join(ROOT, c["file"]), encoding="utf-8", errors="replace").read().splitlines()
        if c["expect"] not in lines[c["line"] - 1]:
            bad.append(c)
gate("D2 census_samples.json parses; vilib_donor section 2 variants, every cite line carries its expect", len(sec.get("variants", [])) == 2
     and not bad, {"bad": bad, "md5": md5(os.path.join(B, "census_samples.json"))})
TESTS = sorted(f for f in os.listdir(B) if f.startswith("selftest_stage_prerun") and f.endswith(".py")) + \
    ["selftest_census_predict.py", "selftest_case_frame_c124.py", "c125_1_offline_measure.py"]


def one(f):
    lg = os.path.join(B, ("c125_1_offline_measure_c128_4.log" if f.startswith("c125_1") else
                          "selftest_c128_4_" + f[len("selftest_"):-3] + ".log"))
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(B, f)], cwd=ROOT, capture_output=True, text=True,
                           timeout=600, encoding="utf-8", errors="replace")
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        out, rc = str(e.stdout or "") + "\nTIMEOUT 600 s", -9
    open(lg, "w", encoding="utf-8").write(out)
    res = [ln for ln in out.splitlines() if ln.startswith("RESULT")][-1:]
    fails = [ln.strip()[:200] for ln in out.splitlines() if ln.lstrip().startswith("FAIL")][:3]
    return f, rc, res, fails, os.path.relpath(lg, ROOT)


with CF.ThreadPoolExecutor(2) as ex:
    for f, rc, res, fails, lg in ex.map(one, TESTS):
        OUT.setdefault("selftests", {})[f] = {"rc": rc, "result": res, "fails": fails, "log": lg}
        gate("S {0} exit 0 and RESULT PASS".format(f), rc == 0 and bool(res) and '"status":"PASS"' in res[0],
             {"rc": rc, "result": res, "fails": fails, "log": lg})
json.dump(OUT, open(os.path.join(B, "diag_c128_4_checks.json"), "w", encoding="utf-8"), indent=1)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None),
                                  [{"path": d["path"], "md5": d["md5"]} for d in OUT["donors"]])), flush=True)
sys.exit(1 if nf else 0)
