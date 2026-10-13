"""p63_tidy - list md5 of every file in claudeDev\\bench\\lean; with --rm-unsaved <name> [...] delete a named leftover ONLY when
its md5 equals the read-only input 09a23608 (an unsaved stage work copy), and print whether LabVIEW is running. P6-3 helper."""
import hashlib, os, subprocess, sys                                                      # noqa: E401
D = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean"
IN_MD5 = "09a23608c223a9a31ea6ca3638c1241c"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
for f in sorted(os.listdir(D)):
    print(md5(os.path.join(D, f)), os.path.getsize(os.path.join(D, f)), f)
if "--rm-unsaved" in sys.argv:
    for n in sys.argv[sys.argv.index("--rm-unsaved") + 1:]:
        p = os.path.join(D, n)
        if n != "D1_ring_p6_replay_20261013_135743.vi" and os.path.isfile(p) and md5(p) in (IN_MD5, "0295a8d349a3b61151cd87797119b9b1"):
            os.remove(p); print("REMOVED (byte copy of the input, never saved):", n)               # noqa: E702
        else:
            print("KEPT (not an unsaved input copy):", n)
lv = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout.lower().count("labview")
print("LabVIEW processes:", lv)
