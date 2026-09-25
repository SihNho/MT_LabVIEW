r"""c87_errorlist_reverdict - cycle-87 firefighter: re-verdict the cycle-87 Error List read of the L2-A1 bed OFFLINE
with the patched plan_for_bed (tools/bench/sim/<stage>/ plans now found). No LabVIEW, no GUI. Prints the derived
licences, the licence usage, and what stays `extra`; ends with one RESULT line."""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import errorlist_check as EC

BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_a1_20260925_235224.vi"
MAIN = os.path.join(HERE, "errorlist_D1_l2_a1_20260925_235224_20260926_001456.json")
RAW = MAIN.replace(".json", "_raw.json")

sp, pp, plan = EC.plan_for_bed(BED)
print("stage_file", sp)
print("plan_file ", pp)
print("open_rows ", len((plan or {}).get("open_rows") or []))
for r in EC.derive_expected(plan) if plan else []:
    print("  LICENCE", r["kind"], r["from"], "count", r["count"])
verdict, out = EC.reverdict(BED, MAIN, RAW)
R = json.load(open(out, encoding="utf-8"))
print("verdict", verdict, "->", out)
for u in R["licence_usage"]:
    print("  USED", u["used"], u["kind"], u["from"])
print("extra", len(R["extra"]))
for e in R["extra"]:
    print("  EXTRA", e)
print("missing", R["missing"])
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if verdict == "OK" else "FAIL",
                              "gates": {"pass": 1 if verdict == "OK" else 0, "fail": 0 if verdict == "OK" else 1},
                              "first_fail": None if verdict == "OK" else "ERRORLIST %s: %d extra" % (verdict, len(R["extra"])),
                              "artefacts": [{"path": os.path.relpath(out, os.path.dirname(HERE)), "md5": EC.md5(out)}]}))
