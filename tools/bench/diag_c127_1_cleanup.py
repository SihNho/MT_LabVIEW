"""diag_c127_1_cleanup - card 127-1: diag_c127_1_fsinner.py hit BGRUN TIMEOUT (40 min) inside S_latest, so its own close() never
ran. This finishes that step: taskkill LabVIEW (stagexec.kill_labview_at_exit), delete ONLY this card's scratch
scratch_c127_1_fsinner_20261001_222233.vi, verify the bed and the original md5s. PREDICTION: LabVIEW gone, scratch gone, md5s equal."""
import hashlib, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec, protocol                                                                  # noqa: E401
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(CD, "scratch_c127_1_fsinner_20261001_222233.vi")
PINS = {os.path.join(CD, "D1_ring_p3a_20261001_180540.vi"): "4dfa44aac8fb32f706b3eb792ee7d3cc",
        os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi"): "2a78e17c449cacdaf5da389818526859"}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
gates = []
gates.append(("LabVIEW gone", stagexec.kill_labview_at_exit()))
if os.path.exists(SCR):
    os.remove(SCR)
gates.append(("scratch deleted", not os.path.exists(SCR)))
for p, m in PINS.items():
    got = md5(p); print("MD5", os.path.basename(p), got, "want", m)                          # noqa: E702
    gates.append(("md5 %s" % os.path.basename(p), got == m))
for n, ok in gates:
    print("PASS " if ok else "FAIL ", n)
bad = [n for n, ok in gates if not ok]
print(protocol.result_line({"status": "FAIL" if bad else "PASS", "gates": {"pass": len(gates) - len(bad), "fail": len(bad)},
                            "first_fail": bad[0] if bad else None, "artefacts": []}))
