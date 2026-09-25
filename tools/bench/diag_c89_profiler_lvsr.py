# -*- coding: utf-8 -*-
# (no shebang on purpose: the `py` launcher honours `#!/usr/bin/env python`, resolves `python` to the WindowsApps
#  stub on this PATH, which prints "Python" and exits 9009 - measured twice in diag_c89_profiler_lvsr_run.log)
"""
Card 89-3 step 2: READ the `LVSR` (VI settings) block of D1_s1_copy.vi OFFLINE, so the "Allow debugging"
question is answered from the file's bytes, not from a LabVIEW session (the card allows a headless read only,
and no VI-Server op for the `Execution.Allow Debugging` property exists: docs/vi-server-ids.json has no such
ID, gscript.py has no VI-property reader - checked 2026-09-26, grep "Debug|Allow" -> 0 hits).

FOUND FIRST (what already exists): tools/bench/t2_rsrc_blockdiff.py `parse_rsrc()` - a MEASURED RSRC
block-table parser (checks C1-C7) - is reused as-is; nothing new is parsed here except the LVSR payload.

Prediction contract:
  P1 every file parses (C1..C7 all ok)                        -> gate
  P2 every file has exactly ONE LVSR section                    -> gate
  P3 LVSR payload length is 160 B on the LV2026 files (t2_rsrc_blockdiff.py docstring line 71) -> gate
  P4 the LVSR of D1_s1_copy.vi is byte-identical to the ORIGINAL's except (at most) the bytes a resave changes
     -> reported, NOT a gate (a diff is data for the flag decode, which waits for the peer fact answer)
  The flag decode (which bit = "debugging allowed") is NOT asserted here; the hex is printed for the plan.
Read-only: opens 'rb'. No LabVIEW. Result line: protocol.result_line.
"""
import hashlib
import os
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import t2_rsrc_blockdiff as T2   # noqa: E402
import protocol as P             # noqa: E402

CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
FILES = [
    ("D1_s1_copy", os.path.join(CD, "D1_s1_copy.vi")),
    ("ORIGINAL", os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")),   # drive_m8.py:28
    ("kswap", os.path.join(CD, "D1_s1_kswap_20260926_004935.vi")),
    ("OpDelete_v0 (scripted op)", os.path.join(CD, "OpDelete_v0.vi")),
    ("vi.lib HighResRelSecs", r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\High Resolution Relative Seconds.vi"),
]
LOG = os.path.join(HERE, "diag_c89_profiler_lvsr.log")
lines = []


def say(s=""):
    print(s, flush=True)
    lines.append(s)


def hexrow(b):
    return " ".join("%02x" % c for c in b)


def main():
    n_pass = n_fail = 0
    first = None
    payloads, decoded = {}, {}
    for tag, path in FILES:
        if not os.path.isfile(path):
            say("SKIP %s: not on disk (%s)" % (tag, path))
            continue
        data = open(path, "rb").read()
        rec, checks = T2.parse_rsrc(data, tag)
        ok_parse = all(c["ok"] for c in checks)
        say("=" * 90)
        say("%s  %s  %d B  md5 %s  saved-version %s" % (tag, path, len(data), hashlib.md5(data).hexdigest(),
                                                        rec.get("version_candidates")))
        for c in checks:
            if not c["ok"]:
                say("  parse check FAIL %s %s" % (c["check"], c["detail"]))
        secs = [s for s in rec["sections"] if s["ident"] == "LVSR"]
        g1 = ok_parse
        g2 = len(secs) == 1
        say("GATE P1 parse ok: %s | P2 one LVSR section: %s (%d)" % (g1, g2, len(secs)))
        n_pass += int(g1) + int(g2)
        n_fail += int(not g1) + int(not g2)
        if not g1 and first is None:
            first = "P1 %s" % tag
        if not g2:
            if first is None:
                first = "P2 %s" % tag
            continue
        s = secs[0]
        pl = data[s["start_abs"]:s["start_abs"] + s["payload_len"]]
        payloads[tag] = pl
        g3 = len(pl) == 160
        say("GATE P3 LVSR payload 160 B: %s (%d)" % (g3, len(pl)))
        n_pass += int(g3)
        n_fail += int(not g3)
        if not g3 and first is None:
            first = "P3 %s len %d" % (tag, len(pl))
        for i in range(0, len(pl), 16):
            say("  LVSR+%03d  %s" % (i, hexrow(pl[i:i + 16])))
        if len(pl) >= 32:
            ver, execf, vif2 = struct.unpack(">3I", pl[:12])
            inst = struct.unpack(">I", pl[24:28])[0]
            # pylabview LVinstrument.py (archive/peer/2026-09-26-c89-profiler-fact2.md:37-39): LVSRData.instrState
            # u32 @0x18, VI_IN_ST_FLAGS.DebugCapable = 1<<9 (set = debugging ALLOWED); execFlags u32 @4,
            # VI_EXEC_FLAGS.IsReentrant = 1<<5, LibProtected = 1<<13.
            say("  version=0x%08x execFlags=0x%08x viFlags2=0x%08x instrState=0x%08x" % (ver, execf, vif2, inst))
            say("  DECODE (pylabview): DebugCapable(instrState bit9)=%s  IsReentrant(execFlags bit5)=%s  "
                "LibProtected(bit13)=%s" % (bool(inst & 0x200), bool(execf & 0x20), bool(execf & 0x2000)))
            decoded[tag] = bool(inst & 0x200)
    if "D1_s1_copy" in payloads and "ORIGINAL" in payloads:
        a, b = payloads["D1_s1_copy"], payloads["ORIGINAL"]
        diff = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
        say("P4 (report) D1_s1_copy vs ORIGINAL LVSR differing byte offsets: %s" % diff)
    for tag in payloads:
        for other in payloads:
            if tag < other:
                a, b = payloads[tag], payloads[other]
                d = [i for i in range(min(len(a), len(b))) if a[i] != b[i]]
                say("  diff %-28s vs %-28s : %s" % (tag, other, d))
    # ---- P5 (optional, `--com`): the SAME property read HEADLESS through ActiveX `VirtualInstrument.AllowDebugging`
    # (NI: properties-and-methods/activex/vi/allowdebugging.html, fact2.md:30). Read only; the VI is loaded, never
    # run, never saved; the instance this starts is stopped at the end (standing restart permission).
    if "--com" in sys.argv:
        import subprocess
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        vals = {}
        try:
            app = dynamic.Dispatch("LabVIEW.Application")
            say("COM: LabVIEW.Application attached/started, version %s" % app.Version)
            for tag, path in FILES[:1]:
                vi = app.GetVIReference(path, "", False, 0)
                vals[tag] = {"AllowDebugging": bool(vi.AllowDebugging), "ExecState": int(vi.ExecState),
                             "ReentrancyType": int(vi.ReentrancyType), "ExecPriority": int(vi.ExecPriority)}
                say("COM %s: %s" % (tag, vals[tag]))
                del vi
            del app
        except Exception as e:                                           # noqa: BLE001
            say("COM read raised %r" % e)
        pythoncom.CoUninitialize()
        subprocess.run(["powershell", "-NoProfile", "-Command",
                        "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
        import time
        time.sleep(8)
        gone = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower().count("labview.exe") == 0
        say("LabVIEW closed after the read: %s" % gone)
        g5 = "D1_s1_copy" in vals and vals["D1_s1_copy"]["AllowDebugging"] == decoded.get("D1_s1_copy")
        say("GATE P5 COM AllowDebugging == offline DebugCapable bit: %s (COM=%s, LVSR=%s)"
            % (g5, (vals.get("D1_s1_copy") or {}).get("AllowDebugging"), decoded.get("D1_s1_copy")))
        n_pass += int(g5)
        n_fail += int(not g5)
        if not g5 and first is None:
            first = "P5 COM vs LVSR mismatch"
        g6 = gone
        say("GATE P6 LabVIEW gone: %s" % g6)
        n_pass += int(g6)
        n_fail += int(not g6)
        if not g6 and first is None:
            first = "P6 LabVIEW still running"
    with open(LOG, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    r = P.make_result(n_pass, n_fail, first, [{"path": os.path.relpath(LOG, ROOT),
                                             "md5": hashlib.md5(open(LOG, "rb").read()).hexdigest()}])
    print(P.result_line(r), flush=True)


if __name__ == "__main__":
    main()
