"""p6fix_tidy - list md5 of every file in claudeDev\\bench\\lean; with --rm-unsaved <name> [...] delete a named leftover ONLY when its
name is a p6fix work name and its md5 equals the read-only bed c2d9c13c (an unsaved stage work copy of a failed build run); print
whether LabVIEW is running. p6fix helper (after p63_tidy.py)."""
import hashlib, os, subprocess, sys                                                      # noqa: E401
D = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
BED_MD5 = "c2d9c13cb40c0a5cab7433896d1df157"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
for f in sorted(os.listdir(D)):
    print(md5(os.path.join(D, f)), os.path.getsize(os.path.join(D, f)), f)
if "--rm-unsaved" in sys.argv:
    for n in sys.argv[sys.argv.index("--rm-unsaved") + 1:]:
        p = os.path.join(D, n)
        if n.startswith("D1_ring_p6fix_") and os.path.isfile(p) and md5(p) == BED_MD5:
            os.remove(p); print("REMOVED (byte copy of the bed, never saved):", n)                  # noqa: E702
        else:
            print("KEPT (not an unsaved bed copy):", n)
lv = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout.lower().count("labview")
print("LabVIEW processes:", lv)
