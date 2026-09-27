"""Card 115-5 V4/V5 (OFFLINE, no LabVIEW): re-verdict the saved 115-3 Error List read of D1_l2_r1_20260928_055441.vi
against the new explicit expected file, through errorlist_check's own lookup (no --expected path given).

Existing tools used (checked first): tools/errorlist_check.py find_reusable / reverdict (lazy LabVIEW imports, card
81-1); the shape is tools/bench/diag_c111d_reverdict.py. Nothing new is built; no VI is opened, run, saved or deleted.

PREDICTION CONTRACT: K R1 md5 f465196b.., B3 md5 1b5c12d7.., capture md5 81661d28.. unchanged before and after;
E1 file total == sum(count) == 55, bed_md5 == the read's md5; E3 lookup picks the new file, 0 derived licences,
find_reusable returns the 060555 read; E2 verdict OK, extra 0, missing 0, every entry used exactly its count;
C classes loose 24 / no-source 1 / not-connected 20 / other 10 == 55.
"""
import json, os, shutil, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import errorlist_check as C          # noqa: E402
import protocol                       # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED = os.path.join(CD, "D1_l2_r1_20260928_055441.vi")
B3 = os.path.join(CD, "D1_l2_b3_20260928_032703.vi")
PIN = {BED: "f465196bb5016638b146e771ba54c5af", B3: "1b5c12d71ca48f22e3f4b80316c67e51"}
READ = os.path.join(HERE, "errorlist_D1_l2_r1_20260928_055441_20260928_060555.json")
READ_MD5 = "81661d28b1ac1af66bca2f8c97a02ee6"
RAW = READ[:-5] + "_raw.json"
EXP = os.path.join(HERE, "errorlist_expected_D1_l2_r1_20260928_055441.json")
gates = {}

import subprocess                     # noqa: E402
# V2: guard_peer's own verdict on a build-shaped command, run as the hook runs it (payload on stdin)
_pl = json.dumps({"tool_name": "Bash", "tool_input": {"command": "py tools/bgrun.py --material --max-min 5 --log "
                  "tools/bench/diag_c115e_x.log -- py -u tools/recipes/stage_d1_l2r2.py"}})
_gp = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "hooks", "guard_peer.py")], input=_pl, cwd=ROOT,
                     capture_output=True, text=True, timeout=120)
print("GUARD_PEER rc=%d stderr=%r" % (_gp.returncode, _gp.stderr[-600:]))
gates["V2_guard_peer_not_armed_by_sel_log"] = _gp.returncode == 0 and "diag_c115d_sel" not in _gp.stderr

before = {p: C.md5(p) for p in PIN}
gates["K_vi_md5_pinned_before"] = all(before[p] == PIN[p] for p in PIN)
gates["K_capture_md5"] = C.md5(READ) == READ_MD5
e = json.load(open(EXP, encoding="utf-8"))
src = json.load(open(READ, encoding="utf-8"))
tot = sum(int(x["count"]) for x in e["expected"])
gates["E1_total_55"] = (tot == e["total"] == 55)
gates["E1_md5_matches_read"] = (e["bed_md5"] == src["bed_md5_before"] == src["bed_md5_after"] == PIN[BED])
print("E1 entries %d total %d md5 %s" % (len(e["expected"]), tot, e["bed_md5"]))

p, raw, why = C.find_reusable(BED, src["bed_md5_before"])
print("find_reusable ->", p, raw, why)
gates["E3_find_reusable_060555"] = bool(p) and os.path.basename(p) == os.path.basename(READ)

tmp = tempfile.mkdtemp(prefix="c115e_")
verdict, out = C.reverdict(BED, READ, RAW, out_dir=tmp)
R = json.load(open(out, encoding="utf-8"))
keep = os.path.join(HERE, "errorlist_check_c115e_reuse.json")
shutil.copyfile(out, keep)
print("reverdict ->", verdict, "saved", keep)
gates["E3_lookup_picks_file"] = bool(R["expected_file"]) and os.path.normcase(os.path.abspath(R["expected_file"])) == \
    os.path.normcase(os.path.abspath(EXP))
gates["E3_no_derived_licences"] = not [u for u in R["licence_usage"] if u["kind"] not in ("explicit", "header_of_next")]
print("extra %d %s missing %d items %d" % (len(R["extra"]), R["extra"], len(R["missing"]), R["item_count"]))
for x, u in zip(e["expected"], R["licence_usage"]):
    print("  used %2d / %2d  %s" % (u["used"], x["count"], x["label"]))
gates["E2_verdict_OK"] = verdict == "OK"
gates["E2_extra_0"] = not R["extra"]
gates["E2_missing_0"] = not R["missing"]
gates["E2_each_entry_used_exactly"] = all(u["used"] == int(x["count"]) for x, u in zip(e["expected"], R["licence_usage"]))
gates["E2_all_55_licensed"] = R["item_count"] == 55 and all(i.get("licensed_by") for i in R["items"])

cls = {"loose": 0, "nosource": 0, "unconn": 0, "other": 0}
for x, u in zip(e["expected"], R["licence_usage"]):
    k = x["norm_all"][0]
    key = ("loose" if k == "wirehaslooseends" else "nosource" if "hasnosource" in k else
           "unconn" if k == "completelyunconnectedwire" else "other")
    cls[key] += u["used"]
print("CLASSES", cls)
gates["C_classes_24_1_20_10"] = cls == {"loose": 24, "nosource": 1, "unconn": 20, "other": 10}
shutil.rmtree(tmp, ignore_errors=True)
after = {p: C.md5(p) for p in PIN}
gates["K_vi_md5_unchanged_after"] = after == before
for k, v in gates.items():
    print("  GATE %s  %s" % ("PASS" if v else "FAIL", k))
nf = sum(1 for v in gates.values() if not v)
print("ERRORLIST-VERDICT: %s %s" % (verdict, keep))
print(protocol.result_line(protocol.make_result(
    len(gates) - nf, nf, next((k for k, v in gates.items() if not v), None),
    artefacts=[{"path": os.path.relpath(EXP, ROOT).replace("\\", "/"), "md5": C.md5(EXP)},
               {"path": os.path.relpath(keep, ROOT).replace("\\", "/"), "md5": C.md5(keep)}])))
sys.exit(1 if nf else 0)
