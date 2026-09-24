r"""diag_replay_cleanup - card 76-1 hygiene tail that diag_replay_measure.py run 2 never reached (it died on its own
AttributeError at :87 before [H]). NO LabVIEW: deletes the one leftover scratch, re-checks the pins, confirms no
LabVIEW process. PREDICTION: scratch gone; S1/S3/gb/gb_orig/GI md5 == the run-2 pins_before; LabVIEW.exe absent.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/replay_vis_76_cleanup.log -- py -u tools/bench/diag_replay_cleanup.py"""
import os, sys, subprocess                                                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
import protocol                                                                          # noqa: E402
SCR = os.path.join(K.CLAUDEDEV, "replay_measure_76_20260925_033351_GB.vi")
PINS = {"S1": (os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"),
        "S3": (os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi"), "1a11d92aacabf7ec844d65b8af19f39f"),
        "gb": (os.path.join(K.CLAUDEDEV, "background VIs_COPY", "get buff image-lost frames.vi"), "9aaaef21e8426035f64a04ec816491d0"),
        "gb_orig": (r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs\get buff image-lost frames.vi", "9aaaef21e8426035f64a04ec816491d0"),
        "GI": (r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Get Image.vi", "be7a516355ccb2c0fdbfe935c9146a07")}
ok, fails = 0, []
def gate(label, cond, detail=""):
    global ok
    print("  {0}  {1}  {2}".format("PASS" if cond else "FAIL", label, detail))
    if cond: ok += 1
    else: fails.append(label)
if os.path.exists(SCR):
    os.remove(SCR)
gate("C1 leftover scratch deleted", not os.path.exists(SCR), SCR)
for k, (p, m) in PINS.items():
    got = K.md5(p)
    gate("C2 pin {0}".format(k), got == m, got)
tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True, errors="replace").stdout
gate("C3 LabVIEW.exe absent", "LabVIEW.exe" not in tl)
print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": ok, "fail": len(fails)},
                            "first_fail": fails[0] if fails else None, "artefacts": []}))
sys.exit(0 if not fails else 1)
