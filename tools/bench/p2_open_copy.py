"""p2_open_copy.py - open the D0 plain copy for the USER to run (P2, 2026-09-18).
Preloads the ORIGINAL read-only (subVI hierarchy resident by name, the drive_original_copy.py trick) so the copy
in claudeDev links without a "Find the VI named" dialog. Nothing is run, nothing is saved; md5 of the original is
printed before and after. The user runs the VI by hand."""
import hashlib
import os
import sys
import time

import pythoncom
from win32com.client import dynamic

ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi"
COPY = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_D0_copy_20260918.vi"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


print("md5 original BEFORE", md5(ORIG), flush=True)
pythoncom.CoInitialize()
app = dynamic.Dispatch("LabVIEW.Application")
print("LabVIEW", app.Version, flush=True)
vi_orig = app.GetVIReference(ORIG, "", False, 0)
print("original resident, ExecState", int(vi_orig.ExecState), flush=True)
vi = app.GetVIReference(COPY, "", False, 0)
print("copy loaded, ExecState", int(vi.ExecState), "(1 = idle/runnable, 0 = broken)", flush=True)
vi._FlagAsMethod("OpenFrontPanel")
vi.OpenFrontPanel(True, 1)
print("copy front panel open", flush=True)
time.sleep(2)
print("md5 original AFTER ", md5(ORIG), flush=True)
# keep the references alive so the hierarchy stays resident while the user works; bgrun's deadline ends us
hold = float(sys.argv[1]) if len(sys.argv) > 1 else 3600
print("holding references %.0f s (the user runs the VI by hand now)" % hold, flush=True)
time.sleep(hold)
