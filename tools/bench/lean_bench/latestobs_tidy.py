"""latestobs_tidy - lean task latest retry: list md5 of every *latestobs* / scratch_latestobs file in claudeDev\\bench\\lean; with
--rm <name>=<md5> [...] delete a named leftover of a FAILED build run ONLY when its name is a latestobs build name and its md5
equals the md5 given (an unsaved observer work copy == RingPickSlot_latest 8fc2ec26; a run's own logger / donor scratch).
Prints whether LabVIEW is running."""
import hashlib, os, subprocess, sys                                                      # noqa: E401
D = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
OK_PREFIX = ("RingPickSlot_latestobs_", "PickLog_latestobs_", "scratch_latestobs_bdon_", "D1_ring_p6latestobs_replay_w100_")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
for f in sorted(os.listdir(D)):
    if "latestobs" in f:
        print(md5(os.path.join(D, f)), os.path.getsize(os.path.join(D, f)), f)
if "--rm" in sys.argv:
    for a in sys.argv[sys.argv.index("--rm") + 1:]:
        n, want = a.split("=", 1)
        p = os.path.join(D, n)
        if n.startswith(OK_PREFIX) and os.path.isfile(p) and md5(p) == want:
            os.remove(p); print("REMOVED (md5 %s as given): %s" % (want[:8], n))          # noqa: E702
        else:
            print("KEPT (name or md5 does not match):", n)
lv = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout.lower().count("labview")
print("LabVIEW processes:", lv)
