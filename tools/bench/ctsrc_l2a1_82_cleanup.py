r"""ctsrc_l2a1_82_cleanup - the hygiene tail ctsrc_l2a1_82.py did not reach (bgrun TIMEOUT inside Stage.close's
restart_labview, tools/bench/ctsrc_l2a1_82.log). No LabVIEW scripting: kill LabVIEW, delete the run's scratch, check D1_k.
PREDICTION: LabVIEW gone, scratch D1_k_scratch_ctsrc82_* deleted, D1_k md5 6cf5b077... unchanged.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/ctsrc_l2a1_82_cleanup.log -- py -u tools/bench/ctsrc_l2a1_82_cleanup.py"""
import glob, hashlib, json, os, subprocess, sys, time                           # noqa: E401
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
BED, BED_MD5 = os.path.join(CD, "D1_k_20260925_100155.vi"), "6cf5b0777aafa12112d8a786a9eed1ed"
g = []


def gate(label, ok, detail=""):
    g.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


st = subprocess.run(["powershell", "-NoProfile", "-Command", "Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                     "ForEach-Object { '{0} {1:yyyy-MM-dd HH:mm:ss}' -f $_.Id, $_.StartTime }"],
                    capture_output=True, text=True, timeout=60).stdout.strip()
print("  FACT  LabVIEW instance(s) before the kill (pid start-time; review archive/peer/2026-09-25-hyp-ctsrc82-timeout.md "
      "test 4 - the bgrun kill was 15:03:05): {0!r}".format(st), flush=True)
print(subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60).stdout.strip()[:200])
time.sleep(5.0)
tl = subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
gate("C1 LabVIEW process gone", "labview.exe" not in tl)
for p in glob.glob(os.path.join(CD, "D1_k_scratch_ctsrc82_*.vi")):
    for _ in range(5):
        try:
            os.remove(p)
            break
        except OSError as e:
            print("  retry delete {0}: {1}".format(os.path.basename(p), e), flush=True)
            time.sleep(3.0)
    gate("C2 scratch deleted {0}".format(os.path.basename(p)), not os.path.exists(p))
gate("C2b no D1_k_scratch_ctsrc82_* left", not glob.glob(os.path.join(CD, "D1_k_scratch_ctsrc82_*.vi")))
m = hashlib.md5(open(BED, "rb").read()).hexdigest()
gate("C3 D1_k md5 unchanged", m == BED_MD5, m)
nf = sum(1 for _l, ok in g if not ok)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if not nf else "FAIL",
                              "gates": {"pass": len(g) - nf, "fail": nf},
                              "first_fail": next((l for l, ok in g if not ok), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
