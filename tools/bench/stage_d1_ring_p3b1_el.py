r"""stage_d1_ring_p3b1_el - card 129-2: the Error List of a SAVED RING P3b-1 file, read by tools/errorlist_check.py main() UNCHANGED (scratch
copy, Ctrl+E/Ctrl+L, per-item double-click in a full read, Esc, md5 before/after, max_steps 180). NEEDS flags.gui (GUI reader).
EXPECTED (both modes): errorlist_expected_scratch_ring_p3b1_pred.json, written here by script = the P3a bed's expected file (55) with the
pred's `removed` items taken off the LAST 'wirehaslooseends' entry (P3a's own pinned item, card 124-7; w27378, pred row_sources) -> 54.
MODE 'scratch' (argv[1]): the file is stage_d1_ring_p3b1_scratch_pin.json ring_p3b1.final (claudeDev\scratch_c129_ring_p3b1_*.vi), read
`--count-only --role scratch`. PASS (reader gates, missing [], total in {predicted_total, predicted_total + len(unwired_created_sinks)}
= {54, 57}) writes tools/bench/plan_ring_p3b1_pin.json = the PINNED new items; the scratch file is deleted.
MODE 'final': the file is stage_d1_ring_p3b1.json ring_p3b1.final (D1_ring_p3b1_*.vi), FULL read `--role final`; PASS (missing [], new
items == the pin as a multiset of norm(raw)) writes errorlist_expected_D1_ring_p3b1_<ts>.json and reverdict must say OK.
PRIOR ART: tools/bench/stage_d1_ring_p3a_el.py (card 124-7; this is its cut + the removed-item expected file). Never saves or runs a VI.
PREDICTION: reader gates True; missing []; new 0 (alternative 3); total 54 (alt 57); LabVIEW gone.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_ring_p3b1_el_scratch.log -- py -u tools/bench/stage_d1_ring_p3b1_el.py scratch"""
import collections, copy, glob, json, os, subprocess, sys, time                      # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench"), os.path.join("tools", "recipes")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
MODE = "final" if "final" in sys.argv[1:] else "scratch"
PRED = json.load(open(os.path.join(B, "plan_ring_p3b1_pred.json"), encoding="utf-8"))["errorlist"]
PREV = os.path.join(B, "errorlist_expected_scratch_ring_p3b1_pred.json")
PINF = os.path.join(B, "plan_ring_p3b1_pin.json")
ST = json.load(open(os.path.join(B, "stage_d1_ring_p3b1_scratch_pin.json" if MODE == "scratch" else "stage_d1_ring_p3b1.json"), encoding="utf-8"))["ring_p3b1"]
NEW, PIN = ST["final"], ST["md5"]
STEM = os.path.splitext(os.path.basename(NEW or "none"))[0]
ALT = PRED["predicted_total"] + len(PRED.get("unwired_created_sinks") or [])
gates, out = [], []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


ms = lambda raws: sorted(collections.Counter(EC.norm(r) for r in raws).items())    # noqa: E731
base = json.load(open(os.path.join(ROOT, PRED["base_file"]), encoding="utf-8"))
pe = copy.deepcopy(base)
li = [i for i, e in enumerate(pe["expected"]) if any("wirehaslooseends" in k for k in e.get("norm_all") or [])]
rm = sum(PRED["removed"].values())
pe["expected"][li[-1]]["count"] -= rm
pe["expected"][li[-1]]["cite"] += " | card 129-2: -{0} for {1} (plan_ring_p3b1_pred.json errorlist.removed / row_sources)".format(rm, sorted(PRED["removed"]))
pe.update(total=base["total"] - rm, decided_by="card 129-2 (stage_d1_ring_p3b1_el.py, mechanical): {0} with pred.removed taken off".format(PRED["base_file"]))
json.dump(pe, open(PREV, "w", encoding="utf-8"), indent=1, ensure_ascii=False); out.append(PREV)
gate("X expected file: P3a {0} - removed {1} == predicted_total {2} (entry #{3} count -> {4})".format(base["total"], rm, PRED["predicted_total"], li[-1],
     pe["expected"][li[-1]]["count"]), pe["total"] == PRED["predicted_total"] == PRED["bed_total"] - rm and pe["expected"][li[-1]]["count"] >= 0, PREV)
gate("K mode {0}: file on disk, md5 == its stage JSON pin".format(MODE), bool(NEW) and os.path.exists(NEW) and EC.md5(NEW) == PIN
     and os.path.basename(NEW).startswith("scratch_c129_ring_p3b1" if MODE == "scratch" else "D1_ring_p3b1_"), (NEW, PIN))
if MODE == "final":
    pin = json.load(open(PINF, encoding="utf-8"))
    gate("P pin file present (scratch {0}, new items {1})".format(os.path.basename(pin["scratch"]), pin["new_count"]), pin.get("schema") == "ring-p3b1-pin/1", PINF)
if all(ok for _l, ok in gates):
    before = set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM)))
    EC._lv_imports()
    E, _orig, RD = EC.E, EC.E.read, {}

    def _read(*a, **k):
        k["max_steps"] = 180
        r = _orig(*a, **k); RD["max_steps"] = r.get("max_steps"); return r              # noqa: E702
    E.read, sys.argv = _read, [sys.argv[0], "--vi", NEW, "--expected", PREV] + (["--count-only", "--role", "scratch"] if MODE == "scratch" else ["--role", "final"])
    EC.main()
    new = sorted(p for p in set(glob.glob(os.path.join(B, "errorlist_%s_*.json" % STEM))) - before if not p.endswith(("_raw.json", "_raw_full.json", "_reuse.json")))
    gate("R the reader wrote ONE read file (max_steps {0})".format(RD.get("max_steps")), len(new) == 1, new)
    if len(new) == 1:
        R = json.load(open(new[0], encoding="utf-8"))
        for k, v in sorted((R.get("gates") or {}).items()):                          # the reader's own integrity gates
            gate("EL {0}".format(k), v)
        extra = R.get("extra") or []
        for x in extra:
            print("  FACT NEW-ITEM {0}".format(x), flush=True)
        cc = EC.class_counts(R.get("items"))
        print("  FACT items {0}; expected {1}; new {2}; predicted new {3} (alternative total {4}); read_mode {5}; per class {6}".format(
            R.get("item_count"), pe["total"], len(extra), PRED["new_items_predicted"], ALT, R.get("read_mode"), json.dumps(cc, sort_keys=True)), flush=True)
        gate("M missing == [] (all {0} expected items present at their exact counts)".format(pe["total"]), not R.get("missing"), R.get("missing"))
        gate("N item count == expected {0} + new {1}".format(pe["total"], len(extra)), R.get("item_count") == pe["total"] + len(extra), R.get("item_count"))
        if MODE == "scratch":
            gate("T total in the predicted set {{{0}, {1}}} (plan_ring_p3b1_pred.json errorlist)".format(PRED["predicted_total"], ALT),
                 R.get("item_count") in (PRED["predicted_total"], ALT), R.get("item_count"))
            if all(ok for _l, ok in gates):
                out.append(PINF)
                json.dump({"schema": "ring-p3b1-pin/1", "new_count": len(extra), "new_items": extra, "new_norm": ms(extra), "predicted": PRED["new_items_predicted"],
                           "total": R.get("item_count"), "per_class": cc, "read": os.path.relpath(new[0], ROOT), "expected": os.path.relpath(PREV, ROOT),
                           "scratch": NEW, "scratch_md5": PIN, "t": time.time()}, open(PINF, "w", encoding="utf-8"), indent=1)
        else:
            gate("PIN new items == the scratch pin (multiset of norm(raw)): {0}".format(pin["new_count"]), ms(extra) == [tuple(x) for x in pin["new_norm"]], (ms(extra), pin["new_norm"]))
            if all(ok for _l, ok in gates):
                add = [{"norm_all": [k], "count": c, "label": next(x for x in extra if EC.norm(x) == k), "cite": "card 129-2: RING P3b-1 new item pinned by the scratch read {0}".format(pin["read"])}
                       for k, c in ms(extra)]
                d = dict(pe, bed=NEW, bed_md5=PIN, total=pe["total"] + len(extra), expected=pe["expected"] + add, measured_from=os.path.relpath(new[0], ROOT),
                         decided_by="mechanical, stage_d1_ring_p3b1_el.py final: P3a's {0} - {1} removed + the {2} new item(s) pinned on the scratch "
                                    "(plan_ring_p3b1_pin.json, PD235(f))".format(base["total"], rm, len(extra)))
                out.append(os.path.join(B, "errorlist_expected_%s.json" % STEM))
                json.dump(d, open(out[-1], "w", encoding="utf-8"), indent=1, ensure_ascii=False)
                verdict, rv = EC.reverdict(NEW, new[0], new[0].replace(".json", "_raw.json"), expected_path=out[-1])
                gate("V reverdict of this read against {0}: OK".format(os.path.basename(out[-1])), verdict == "OK", rv)
subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
gate("H LabVIEW gone; file md5 unchanged by the read", gone and bool(NEW) and EC.md5(NEW) == PIN)
if MODE == "scratch" and NEW and os.path.basename(NEW).startswith("scratch_c129_ring_p3b1") and os.path.exists(NEW):
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
