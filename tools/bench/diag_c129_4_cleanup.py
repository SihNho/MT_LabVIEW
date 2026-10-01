r"""diag_c129_4_cleanup - card 129-4 step 1: kill the ORPHAN LabVIEW left by card 129-2's killed scratch run and delete its
scratch VI. Prior art: stagexec.kill_labview_at_exit (reused, not rebuilt).
PREDICTION: exactly one LabVIEW.exe (PID 15600, started 2026-10-02 01:26:17) before; none after; the file
claudeDev\scratch_c129_ring_p3b1_20261002_012612.vi exists before and not after; the bed D1_ring_p3a_20261001_180540.vi
keeps md5 4dfa44aac8fb32f706b3eb792ee7d3cc.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c129_4_cleanup.log -- py -u tools/bench/diag_c129_4_cleanup.py"""
import os, subprocess, sys                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol, stagexec as SX                                                     # noqa: E401,E402
import stagekit as K                                                                # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
SCR = os.path.join(CD, "scratch_c129_ring_p3b1_20261002_012612.vi")
BED = os.path.join(CD, "D1_ring_p3a_20261001_180540.vi")
p = f = 0


def gate(ok, label):
    global p, f
    print(("PASS  " if ok else "FAIL  ") + label, flush=True)
    p, f = p + bool(ok), f + (not ok)


tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe", "/FO", "CSV", "/NH"], capture_output=True, text=True).stdout
print("FACT  tasklist before:", tl.strip(), flush=True)
gate('"15600"' in tl and tl.lower().count("labview.exe") == 1, "C1a exactly one LabVIEW.exe, PID 15600, before")
gone = SX.kill_labview_at_exit()
gate(gone, "C1b LabVIEW verified gone after kill")
name = os.path.basename(SCR)
ex = os.path.exists(SCR)
gate(ex and name.startswith("scratch_c129_"), "C1c scratch file present before delete: " + name)
if ex and name.startswith("scratch_c129_"):
    os.remove(SCR)
gate(not os.path.exists(SCR), "C1d scratch file gone")
m = K.md5(BED)
gate(m == "4dfa44aac8fb32f706b3eb792ee7d3cc", "C1e bed md5 unchanged " + m)
print(protocol.result_line(protocol.make_result(p, f, None if f == 0 else "cleanup")), flush=True)
