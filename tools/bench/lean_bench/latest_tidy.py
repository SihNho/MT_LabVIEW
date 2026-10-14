"""latest_tidy - lean task latest (after p6fix_tidy.py): list md5 of every *latest* file in claudeDev\\bench\\lean; with
--rm-unsaved <name> [...] delete a named leftover ONLY when its name is a latest work name and its md5 equals its read-only
source (RingPickSlot_v0 6fcf153f, or the p6fix file it was copied from) = an unsaved stage work copy of a failed build run.
Prints whether LabVIEW is running."""
import hashlib, os, subprocess, sys                                                      # noqa: E401
D = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
SRC_MD5 = {"RingPickSlot_latest_": "6fcf153f7b8fecda727f5dcf944faab9",
           "D1_ring_p6latest_replay_gap_": "2c499c7ba1a38c813d784efe7eacee76", "D1_ring_p6latest_replay_w40_": "db5e2e958201df1f1de928558aeff3ac",
           "D1_ring_p6latest_replay_w100_": "ae8474bc8b33506c3659af407c2e7696", "D1_ring_p6latest_replay_2": "ae83d1aa088ba4546c65e039c6b4d16d",
           "D1_ring_p6latest_2": "3e847397eb120860adb2e868792345f7"}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
for f in sorted(os.listdir(D)):
    if "latest" in f:
        print(md5(os.path.join(D, f)), os.path.getsize(os.path.join(D, f)), f)
if "--rm-unsaved" in sys.argv:
    for n in sys.argv[sys.argv.index("--rm-unsaved") + 1:]:
        p = os.path.join(D, n)
        want = [m for k, m in SRC_MD5.items() if n.startswith(k)]
        if len(want) == 1 and os.path.isfile(p) and md5(p) == want[0]:
            os.remove(p); print("REMOVED (byte copy of its source %s, never saved): %s" % (want[0][:8], n))   # noqa: E702
        else:
            print("KEPT (not an unsaved source copy):", n)
lv = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout.lower().count("labview")
print("LabVIEW processes:", lv)
