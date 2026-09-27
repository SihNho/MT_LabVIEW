"""Card 111-4 E2/E3 (OFFLINE, no LabVIEW): re-verdict the 111-1 read of D1_l2_b1_20260927_193100.vi against the new
explicit expected file, through errorlist_check's own lookup (no --expected path given).

Existing tools used (checked first): tools/errorlist_check.py find_reusable / reverdict (lazy LabVIEW imports, card
81-1; reverdict is what cycle_runner.errorlist_hook calls when the bed md5 is unchanged). Nothing new is built.

PREDICTION CONTRACT: E3 reverdict's expected_file == tools/bench/errorlist_expected_D1_l2_b1_20260927_193100.json,
derived licences 0 (PD195(b)), find_reusable returns the _c111 read; E2 verdict OK, extra 0, missing 0, every explicit
entry used exactly its count, 99 items licensed; E1 file total == sum(count) == 99, bed_md5 == the read's md5.
"""
import json, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as C          # noqa: E402
import protocol                       # noqa: E402

BED = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_b1_20260927_193100.vi"
READ = os.path.join(HERE, "errorlist_D1_l2_b1_20260927_193100_c111.json")
RAW = READ[:-5] + "_raw.json"
EXP = os.path.join(HERE, "errorlist_expected_D1_l2_b1_20260927_193100.json")
gates = {}

e = json.load(open(EXP, encoding="utf-8"))
src = json.load(open(READ, encoding="utf-8"))
tot = sum(int(x["count"]) for x in e["expected"])
gates["E1_total_99"] = (tot == e["total"] == 99)
gates["E1_md5_matches_read"] = (e["bed_md5"] == src["bed_md5_before"] == src["bed_md5_after"])
gates["E1_every_entry_cites_PD225"] = all("PD225" in x.get("cite", "") and "facts_c111" in x.get("cite", "")
                                          for x in e["expected"])
print("E1 entries %d total %d md5 %s" % (len(e["expected"]), tot, e["bed_md5"]))

p, raw, why = C.find_reusable(BED, src["bed_md5_before"])
print("find_reusable ->", p, raw, why)
gates["E3_find_reusable_c111"] = bool(p) and os.path.basename(p) == os.path.basename(READ)

tmp = tempfile.mkdtemp(prefix="c111d_")
verdict, out = C.reverdict(BED, READ, RAW, out_dir=tmp)          # expected_path=None -> the checker's own lookup
R = json.load(open(out, encoding="utf-8"))
keep = os.path.join(HERE, "errorlist_check_c111d_reuse.json")
shutil.copyfile(out, keep)
print("reverdict ->", verdict, "saved", keep)
print("expected_file", R["expected_file"], "stage_file", R["stage_file"], "plan_file", R["plan_file"])
gates["E3_lookup_picks_file"] = bool(R["expected_file"]) and os.path.normcase(os.path.abspath(R["expected_file"])) == \
    os.path.normcase(os.path.abspath(EXP))
derived = [u for u in R["licence_usage"] if u["kind"] not in ("explicit", "header_of_next")]
gates["E3_no_derived_licences"] = not derived
print("extra %d missing %d items %d" % (len(R["extra"]), len(R["missing"]), R["item_count"]))
for x, u in zip(e["expected"], R["licence_usage"]):
    print("  used %2d / %2d  %s" % (u["used"], x["count"], x["label"]))
gates["E2_verdict_OK"] = verdict == "OK"
gates["E2_extra_0"] = not R["extra"]
gates["E2_missing_0"] = not R["missing"]
gates["E2_each_entry_used_exactly"] = all(u["used"] == int(x["count"]) for x, u in zip(e["expected"], R["licence_usage"]))
gates["E2_all_99_licensed"] = R["item_count"] == 99 and all(i.get("licensed_by") for i in R["items"])
shutil.rmtree(tmp, ignore_errors=True)
for k, v in gates.items():
    print("GATE %-30s %s" % (k, "PASS" if v else "FAIL"))
nf = sum(1 for v in gates.values() if not v)
print("ERRORLIST-VERDICT: %s %s" % (verdict, keep))
print(protocol.result_line(protocol.make_result(len(gates) - nf, nf,
                                                next((k for k, v in gates.items() if not v), None),
                                                artefacts=[{"path": os.path.relpath(EXP, ROOT).replace("\\", "/"),
                                                            "md5": C.md5(EXP)}])))
