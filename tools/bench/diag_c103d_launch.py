"""card 103-4 (no LabVIEW, no launch): what the stage launch gate answers for the PART-B command next cycle, and the md5s of the
Part-A file and S1 (both must be unchanged). check_launch RECORDS NOTHING (stage_prerun.py check_launch docstring)."""
import json, os, sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T); os.chdir(os.path.dirname(T))
import stage_prerun as SP, protocol
pa = json.load(open(os.path.join(T, "bench", "stage_d1_dispA.json"), encoding="utf-8"))["partA"]
cmd = ('py tools/bgrun.py --material --max-min 40 --log tools/bench/stage_d1_dispB_r1.log -- py -u tools/recipes/'
       'stage_d1_disp.py --from-step 33 --base "{0}"').format(pa["file"])
ok, why = SP.check_launch(cmd)
print("LAUNCH", "ALLOW" if ok else "REFUSE", (why or "")[:900].replace("\n", " | "))
units = [(s, None) for s in SP.launched_stage_scripts(cmd)]
recs = SP.read_records()
sha = SP.sha256(units[0][0]); pm = SP.plan_md5s(units[0][0])
for kind in ("dry", "prerun"):
    m = [r for r in recs if r.get("kind") == kind and r.get("sha256") == sha and r.get("status") == "PASS" and r.get("plan_md5s") == pm]
    print("RECORD", kind, "PASS records for current sha", sha[:12], len(m), "newest", m[-1]["iso"] if m else None,
          "from_step", m[-1].get("from_step") if m else None)
ok_nocap = SP._check_units.__code__  # noqa: F841 - not used; the cap alone is reported below
runs, ck = SP.read_stage_runs(), SP.cycle_key()
cap_ok, cap_why, _c = SP.check_cap(cmd, units[0][0], runs, ck)
print("CAP", ck, "allow" if cap_ok else "refuse", (cap_why or "")[:300].replace("\n", " | "))
a, s1 = SP.md5(pa["file"]), SP.md5(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi")
print("MD5 dispA", a, a == pa["md5"], "S1", s1, s1 == "3e3d23cefd3a334001aa9d6156bf1aee")
good = a == pa["md5"] and s1 == "3e3d23cefd3a334001aa9d6156bf1aee"
print(protocol.result_line(protocol.make_result(int(good), int(not good), None if good else "md5 changed")))
