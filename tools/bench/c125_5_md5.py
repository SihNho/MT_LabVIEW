r"""c125_5_md5 - card 125-5 close-out (no LabVIEW): md5 of the beds, the new artefacts and the card's files; LabVIEW process absent;
no scratch_c125_5* left in claudeDev. PREDICTION: P3a 4dfa44aa / P2b 652b1447 unchanged, LabVIEW absent, 0 scratch files.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/c125_5_md5.log -- py -u tools/bench/c125_5_md5.py"""
import glob, hashlib, os, subprocess, sys                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                        # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
F = [os.path.join(CD, f) for f in ("D1_ring_p3a_20261001_180540.vi", "D1_ring_p2b_20261001_140658.vi", "OpFsDiagrams_v0.vi", "OpFsAddFrame_v0.vi", "DonorFs_v0.vi")]
F += [os.path.join(ROOT, "tools", p) for p in ("bench/opfs_v0_labels.json", "bench/op_hygiene/OpFsDiagrams_v0.json", "bench/op_hygiene/OpFsAddFrame_v0.json",
      "gscript.py", "bench/diag_c125_5_opfs.log", "bench/diag_c125_5_stub.log", "bench/diag_c125_5_opfs.py", "bench/diag_c125_5_stub.py",
      "bench/diag_c125_5_fsscr.py", "bench/diag_c125_5_fsscr_plan.json", "bench/diag_c125_5_fsfind.py", "bench/diag_c125_5_fsfind.log", "bench/diag_c125_5_stub.json")]
for p in F:
    print("MD5 %s  %s" % (hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING", p))
lv = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
sc = glob.glob(os.path.join(CD, "scratch_c125_5*"))
ok = [hashlib.md5(open(F[0], "rb").read()).hexdigest() == "4dfa44aac8fb32f706b3eb792ee7d3cc",
      hashlib.md5(open(F[1], "rb").read()).hexdigest() == "652b1447ebbda761a7d5ba36455a0fa1", not lv, not sc]
print("CHECK beds unchanged %s %s | LabVIEW absent %s | scratch left %s" % (ok[0], ok[1], not lv, sc))
print(P.result_line(P.make_result(sum(ok), len(ok) - sum(ok), None if all(ok) else "close-out check", [])))
