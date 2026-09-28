r"""stage_d1_qrt_pool_el - card 119-4 L2 (part 2) and L5: the FULL Error List of a SAVED QRT POOL file, read by tools/errorlist_check.py main() UNCHANGED
(scratch copy, Ctrl+E/Ctrl+L, per-item double-click, Esc, md5 before/after, max_steps 180) against R2's expected file (53 items, exact counts, required).
Items no R2 licence covers are the pool's NEW items (`extra`; derived licences are off because --expected is given, errorlist_check.py:477).
MODE 'scratch' (argv[1]): the file is stage_d1_qrt_pool_scratch.json qrt_pool.final (claudeDev\scratch_c119_pool_*.vi). PASS (reader gates, R2's 53 all
present = missing []) writes tools/bench/plan_qrt_pool_pin.json = the PINNED new items (count + raw labels); gate PRED compares the count with
plan_qrt_pool_pred.json (0, PD235(f)); the scratch file is deleted. MODE 'final': the file is stage_d1_qrt_pool.json qrt_pool.final (D1_qrt_pool_*.vi);
PASS (missing [], new items == the pin, as a multiset of norm(raw)) writes errorlist_expected_D1_qrt_pool_<ts>.json (R2's entries + one entry per
pinned new label) and reverdict must say OK. PRIOR ART: diag_c116b_scratch_el.py (card 116-2; this is its cut, class pin -> new-item pin).
Never saves or runs a VI. PREDICTION: reader gates True; missing []; new items 0 (== pred); LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_qrt_pool_el_scratch.log -- py -u tools/bench/stage_d1_qrt_pool_el.py scratch"""
import collections, glob, json, os, subprocess, sys, time                            # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench"), os.path.join("tools", "recipes")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
MODE = (sys.argv[1:2] or ["scratch"])[0]
PREV = os.path.join(B, "errorlist_expected_D1_l2_r2_20260928_110756.json")
PINF = os.path.join(B, "plan_qrt_pool_pin.json")
ST = json.load(open(os.path.join(B, "stage_d1_qrt_pool_scratch.json" if MODE == "scratch" else "stage_d1_qrt_pool.json"), encoding="utf-8"))["qrt_pool"]
NEW, PIN = ST["final"], ST["md5"]
STEM = os.path.splitext(os.path.basename(NEW or "none"))[0]
PRED = json.load(open(os.path.join(B, "plan_qrt_pool_pred.json"), encoding="utf-8"))["errorlist"]
gates, out = [], []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


ms = lambda raws: sorted(collections.Counter(EC.norm(r) for r in raws).items())    # noqa: E731
gate("K mode {0}: file on disk, md5 == its stage JSON pin".format(MODE), bool(NEW) and os.path.exists(NEW) and EC.md5(NEW) == PIN
     and os.path.basename(NEW).startswith("scratch_c119_" if MODE == "scratch" else "D1_qrt_pool_"), (NEW, PIN))
if MODE == "final":
    pin = json.load(open(PINF, encoding="utf-8"))
    gate("P pin file present (scratch {0}, new items {1})".format(os.path.basename(pin["scratch"]), pin["new_count"]), pin.get("schema") == "qrt-pool-pin/1", PINF)
if all(ok for _l, ok in gates):
    before = set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM)))
    EC._lv_imports()
    E, _orig, RD = EC.E, EC.E.read, {}

    def _read(*a, **k):
        k["max_steps"] = 180
        r = _orig(*a, **k); RD["max_steps"] = r.get("max_steps"); return r              # noqa: E702
    # card chat-P2 item 3: the SCRATCH read is count-only (full read follows inside EC.main if the class counts differ); the FINAL read is always full
    E.read, sys.argv = _read, [sys.argv[0], "--vi", NEW, "--expected", PREV] + (["--count-only", "--role", "scratch"] if MODE == "scratch" else ["--role", "final"])
    EC.main()
    new = sorted(p for p in set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM))) - before if not p.endswith(("_raw.json", "_raw_full.json", "_reuse.json")))
    gate("R the reader wrote ONE read file (max_steps {0})".format(RD.get("max_steps")), len(new) == 1, new)
    if len(new) == 1:
        R = json.load(open(new[0], encoding="utf-8"))
        for k, v in sorted((R.get("gates") or {}).items()):                          # the reader's own integrity gates
            gate("EL {0}".format(k), v)
        for u in R.get("licence_usage") or []:
            print("  FACT USAGE {0:<8} used {1:>3}  {2}".format(u.get("kind"), u.get("used"), str(u.get("from"))[:90]), flush=True)
        extra = R.get("extra") or []
        for x in extra:
            print("  FACT NEW-ITEM {0}".format(x), flush=True)
        print("  FACT items {0}; R2 licensed {1}; new {2}; predicted new {3}".format(R.get("item_count"), PRED["r2_total"], len(extra), PRED["new_items_predicted"]), flush=True)
        gate("M missing == [] (all {0} R2 items present at their exact counts)".format(PRED["r2_total"]), not R.get("missing"), R.get("missing"))
        gate("N item count == R2 {0} + new {1}".format(PRED["r2_total"], len(extra)), R.get("item_count") == PRED["r2_total"] + len(extra), R.get("item_count"))
        if MODE == "scratch":
            if all(ok for _l, ok in gates):
                out.append(PINF)
                json.dump({"schema": "qrt-pool-pin/1", "new_count": len(extra), "new_items": extra, "new_norm": ms(extra), "predicted": PRED["new_items_predicted"],
                           "total": R.get("item_count"), "read": os.path.relpath(new[0], ROOT), "scratch": NEW, "scratch_md5": PIN, "t": time.time()},
                          open(PINF, "w", encoding="utf-8"), indent=1)
            gate("PRED new items {0} == plan prediction {1} (PD235(f))".format(len(extra), PRED["new_items_predicted"]), len(extra) == PRED["new_items_predicted"], extra)
        else:
            gate("PIN new items == the scratch pin (multiset of norm(raw)): {0}".format(pin["new_count"]), ms(extra) == [tuple(x) for x in pin["new_norm"]], (ms(extra), pin["new_norm"]))
            if all(ok for _l, ok in gates):
                pv = json.load(open(PREV, encoding="utf-8"))
                add = [{"norm_all": [k], "count": c, "label": next(x for x in extra if EC.norm(x) == k), "cite": "card 119-4: QRT POOL new item pinned by the scratch read {0}".format(pin["read"])}
                       for k, c in ms(extra)]
                d = dict(pv, bed=NEW, bed_md5=PIN, total=PRED["r2_total"] + len(extra), expected=pv["expected"] + add, measured_from=os.path.relpath(new[0], ROOT),
                         decided_by="card 119-4 L5 (mechanical, stage_d1_qrt_pool_el.py final): R2's 53 licences unchanged + the {0} new item(s) pinned on the scratch "
                                    "(plan_qrt_pool_pin.json, PD234(g)/PD235(f))".format(len(extra)))
                out.append(os.path.join(B, "errorlist_expected_%s.json" % STEM))
                json.dump(d, open(out[-1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
                verdict, rv = EC.reverdict(NEW, new[0], new[0].replace(".json", "_raw.json"), expected_path=out[-1])
                gate("V reverdict of this read against {0}: OK".format(os.path.basename(out[-1])), verdict == "OK", rv)
subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
gate("H LabVIEW gone; file md5 unchanged by the read", gone and bool(NEW) and EC.md5(NEW) == PIN)
if MODE == "scratch" and NEW and os.path.basename(NEW).startswith("scratch_c119_") and os.path.exists(NEW):
    for _i in range(5):
        try:
            os.remove(NEW); break                                                   # noqa: E702
        except OSError:
            time.sleep(3)
    gate("H2 the saved scratch is deleted", not os.path.exists(NEW), NEW)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(p, ROOT), "md5": EC.md5(p)} for p in out])), flush=True)
sys.exit(0 if ff is None else 1)
