r"""diag_c115b_errorlist - card 115-2 R7: the FULL Error List of the saved L2-R1 file (claudeDev\D1_l2_r1_*.vi, path + md5 pinned from
tools/bench/stage_d1_l2r1.json) read by tools/errorlist_check.py main() UNCHANGED (scratch copy, Ctrl+E/Ctrl+L, per-item double-click, Esc,
file md5 before/after) against the B3 bed's expected file, lv_errorlist.read max_steps=180. Never saves or runs a VI. THEN, offline: the lost
items (B3 count - used) must be on RETIRED objects: the read carries no per-item uid (show_error.uid_route 'none'), so they are attributed by
CLASS against the retired stubs of graph_l2b3_20260928.json - 'has no source' <= the sink-only stubs, 'loose ends' <= the source-only stubs,
every other class loses 0. ONLY IF every reader gate holds, extra == [] and that attribution holds: the L2-R1 expected file = B3's entries with
each count set to the count this read USED, and errorlist_check.reverdict must say OK. Otherwise the mismatch table is printed, no file written.
PRIOR ART: diag_c114_errorlist.py (this is its cut: B2b -> B3 became B3 -> R1). PREDICTION: gates True; extra []; lost only no-source/loose-ends.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c115b_errorlist.log -- py -u tools/bench/diag_c115b_errorlist.py"""
import glob, json, os, sys                                                           # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench"), os.path.join("tools", "recipes")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
PREV = os.path.join(B, "errorlist_expected_D1_l2_b3_20260928_032703.json")
ST = json.load(open(os.path.join(B, "stage_d1_l2r1.json"), encoding="utf-8"))["l2r1"]
NEW, PIN = ST["final"], ST["md5"]
STEM = os.path.splitext(os.path.basename(NEW))[0]
G = json.load(open(os.path.join(B, "graph_l2b3_20260928.json"), encoding="utf-8"))
RET = set(u for c in json.load(open(os.path.join(B, "facts_c114e_inventory.json"), encoding="utf-8"))["candidates"]
          if c.get("class") in ("RightShiftRegister", "LeftShiftRegister") for u in [int(c["uid"])])
byw = {}
for r in G["terminals"]:
    if r["wire_uid"]:
        byw.setdefault(int(r["wire_uid"]), []).append(r)
STUB = dict((w, rs) for w, rs in byw.items() if all(int(r["owner_uid"]) in RET for r in rs))
N_SINKONLY = sum(1 for rs in STUB.values() if not any(r["is_source"] for r in rs))
N_SRCONLY = sum(1 for rs in STUB.values() if all(r["is_source"] for r in rs))
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def klass(label):
    l = str(label).lower()
    return "nosource" if "has no source" in l else ("loose" if "loose ends" in l else "other")


print("  FACT retired stubs {0}: sink-only {1}, source-only {2}".format(sorted(STUB), N_SINKONLY, N_SRCONLY), flush=True)
gate("K new file on disk, md5 == stage_d1_l2r1.json pin", bool(NEW) and os.path.exists(NEW) and EC.md5(NEW) == PIN, (NEW, PIN))
out_exp = None
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
        lost = {"nosource": 0, "loose": 0, "other": 0}
        for lab, c, u in rows:
            print("  FACT TABLE {0:<90} B3 {1:>3} used {2}".format(str(lab)[:90], c, u), flush=True)
            lost[klass(lab)] += c - (u or 0)
        gate("NC extra == [] (no new item, so no new class)", not R.get("extra"), len(R.get("extra") or []))
        gate("LO lost items only on retired objects by class: no-source {0} <= {1} sink-only stubs, loose-ends {2} <= {3} source-only stubs, other 0".format(
             lost["nosource"], N_SINKONLY, lost["loose"], N_SRCONLY), 0 <= lost["nosource"] <= N_SINKONLY and 0 <= lost["loose"] <= N_SRCONLY and lost["other"] == 0, lost)
        if all(R.get("gates", {}).values()) and not R.get("extra") and gates[-1][1]:
            d = dict(pv, bed=NEW, bed_md5=PIN, expected=[dict(e, count=u) for e, (_l, _c, u) in zip(pv["expected"], rows) if u],
                     decided_by="card 115-2 R7 (mechanical, script diag_c115b_errorlist.py): B3's explicit licences (errorlist_expected_D1_l2_b3_20260928_032703.json), "
                                "each count lowered to the count this read used; nothing new licensed (extra == []); lost items attributed by class to the retired stubs",
                     measured_from=os.path.relpath(new[0], ROOT), r1_delta=[[lab, c, u] for lab, c, u in rows if u != c])
            d.pop("b3_delta", None)
            out_exp = os.path.join(B, "errorlist_expected_%s.json" % STEM)
            json.dump(d, open(out_exp, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
            verdict, rv = EC.reverdict(NEW, new[0], new[0].replace(".json", "_raw.json"), expected_path=out_exp)
            gate("V reverdict of this read against {0}: OK".format(os.path.basename(out_exp)), verdict == "OK", rv)
        else:
            print("  FACT NO expected file written: reader gates, extra items or lost attribution (mismatch table above)", flush=True)
            gate("V precondition of the expected file (reader gates, extra == [], LO)", False)
import subprocess, time                                                              # noqa: E401,E402
subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
gate("H LabVIEW gone; new file md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
     and bool(NEW) and EC.md5(NEW) == PIN)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [{"path": os.path.relpath(out_exp, ROOT), "md5": EC.md5(out_exp)}] if out_exp else [])), flush=True)
sys.exit(0 if ff is None else 1)
