# ---
# labview: none
# hardware: none
# ---
"""Card 153-a2-1: stat the original 4.5 VI (size, mtime, md5, saved-version bytes) - byte read only, never opened.
Prediction: md5 2f048e3a (measured 07:17 by diag_c153_a2_1_md5.py), which differs from the census-time c39f36e0;
this script records size/mtime/version so the difference can be dated. RESULT pass 1 if the file reads."""
import datetime, hashlib, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

TR = os.path.dirname(ROOT)
for name in ("Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi", "Min_Track N beads V6_ParallelLoop.vi"):
    p = os.path.join(TR, name)
    b = open(p, "rb").read()
    st = os.stat(p)
    vers = {k: b.count(bytes.fromhex(k)) for k in ("19008000", "26008000")}
    print(name, "| size", st.st_size, "| mtime", datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"),
          "| md5", hashlib.md5(b).hexdigest(), "| version-byte counts", vers)
others = sorted(f for f in os.listdir(TR) if f.lower().endswith(".vi"))
for f in others:
    st = os.stat(os.path.join(TR, f))
    print("dir:", f, st.st_size, datetime.datetime.fromtimestamp(st.st_mtime).isoformat(timespec="seconds"))
print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
