"""inspect_motion_vis.py - READ-ONLY inspection of every VI on the motor / stage serial path.

Why: the user reports the motor path was badly delayed, that 115200 baud and a partial loop split were done deliberately
and it still felt like one loop carried too much. The serial HARDWARE is already cleared (2026-09-11): both instruments are
on the Sunix card, whose RX FIFO trigger of 14 bytes costs about 0.35 ms per short reply at 115200, and the 16 ms FTDI
latency timer found on COM5/COM6 belongs to other ports. So the delay must be in the software or the controller, and the
two shapes that would explain it are a FIXED WAIT after each write, or a read that blocks on the VISA timeout
(Mercury_comm.vi's own help text says the default is 5000 ms).

What this does, per VI: `node_info` names every TOP-LEVEL diagram node by its style ("Wait (ms)", "VISA Read",
"Wait Until Next ms Multiple", ...), which is exactly what identifies the two shapes above; plus object counts so we know
how much logic is hidden inside structures (node_info does not descend into sub-diagrams), plus a probe of the ActiveX VI
properties that would reveal reentrancy.

SAFETY: nothing is created, modified or saved. Lab VIs are COPIED to claudeDev and the copies are inspected, then deleted.
Vendor VIs inside instr.lib (including .llb members) are opened read-only by path and never saved. No hardware is touched:
opening a driver VI does not run it.
  py tools/bgrun.py --max-min 30 --log tools/bench/inspect_motion_vis.log -- py -u tools/bench/inspect_motion_vis.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

LVROOT = r"C:\Program Files\National Instruments\LabVIEW 2026"
LAB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
ASI = os.path.join(LVROOT, "instr.lib", "ASI TG-1000")
MERC_LL = os.path.join(LVROOT, "instr.lib", "Mercury", "GCS_LabVIEW", "Low Level")

# (label, path, copy_first) — lab code is copied, vendor code is read in place
LAB_VIS = [
    ("Mercury_comm (lab)", os.path.join(LAB, "PI Trans", "Mercury_comm.vi")),
    ("Motor control v5 (lab)", os.path.join(LAB, "SiHyeong Modified", "Motor control v5_No Recording.vi")),
    ("Global motor pos (lab)", os.path.join(LAB, "four-fold tracking", "Global motor pos.vi")),
    ("ASI_adjust focus (lab)", os.path.join(LAB, "Madcity", "ASI_adjust focus-subvi.vi")),
    ("Max Trans Pos (lab)", os.path.join(LAB, "DY", "Background VIs", "Max Trans Pos.vi")),
]
VENDOR_VIS = [
    ("ASI Send Serial Command", os.path.join(ASI, "Public", "Utility", "Send Serial Command.vi")),
    ("ASI Parse Serial Response", os.path.join(ASI, "Public", "Utility", "Parse Serial Response.vi")),
    ("ASI Get Current Position", os.path.join(ASI, "Public", "Status", "Get Current Position.vi")),
    ("ASI Move Axis to Position", os.path.join(ASI, "Public", "Action", "Move Axis to Position.vi")),
    ("ASI Initialize", os.path.join(ASI, "Public", "Initialize.vi")),
]
# PI GCS command VIs live inside .llb containers; probe the plausible ones
PI_LLBS = ["General command.llb", "Support.llb", "Communication.llb", "Limits.llb", "Old commands.llb", "Special command.llb"]
PI_NAMES = ["MOV.vi", "POS?.vi", "VEL.vi", "TMN?.vi", "TMX?.vi", "SetCommand.vi", "GOH.vi", "SendCommand.vi", "GetAnswer.vi"]
INTERESTING = ("wait", "visa", "delay", "timeout", "serial", "bytes at port", "tick", "time")
g._run.__defaults__ = (6.0, 45.0)


def props(path):
    """Probe the ActiveX VI properties that would show reentrancy / execution system. Read-only."""
    out = {}
    try:
        vi = g.lv().GetVIReference(path, "", False, 0)
    except Exception as e:
        return {"(reference failed)": str(e)[:90]}
    for name in ("ReentrantExecution", "Reentrant", "ExecutionPriority", "PreferredExecSystem", "ExecSystem", "VIType"):
        try:
            out[name] = vi.__getattr__(name)
        except Exception:
            pass
    return out


def inspect(label, path):
    print(f"\n{'=' * 78}\n== {label}\n   {path}", flush=True)
    if not os.path.exists(path.split('.llb')[0] + '.llb') and not os.path.exists(path):
        print("   MISSING", flush=True); return
    try:
        counts = {c: g.count(path, c) for c in ("Node", "SubVI", "Function", "Constant", "Diagram",
                                                "CaseStructure", "WhileLoop", "ForLoop", "Sequence", "Wire")}
        print("   objects:", {k: v for k, v in counts.items() if v}, flush=True)
    except Exception as e:
        print("   count failed:", str(e)[:140], flush=True); return
    print("   VI properties:", props(path), flush=True)
    try:
        info = g.node_info(path, max_n=250)
    except Exception as e:
        print("   node_info failed:", str(e)[:140], flush=True); return
    print(f"   top-level nodes: {len(info)}", flush=True)
    for i, style, text in info:
        mark = "  <<<" if any(k in (style or "").lower() for k in INTERESTING) else ""
        print(f"      [{i:3}] {style!r:38} {text!r}{mark}", flush=True)
    hot = [s for _, s, _ in info if any(k in (s or "").lower() for k in INTERESTING)]
    print(f"   TIMING/SERIAL nodes on the top level: {sorted(set(hot)) if hot else 'none'}", flush=True)
    if counts.get("Diagram", 1) > 1:
        print(f"   NOTE: {counts['Diagram']} diagrams - {counts['Diagram'] - 1} sub-diagram(s) NOT covered by node_info", flush=True)


def main():
    g._lv = None
    print("READ-ONLY inspection. Nothing is saved. No hardware is touched.", flush=True)
    # lab VIs: inspect copies
    for label, src in LAB_VIS:
        if not os.path.exists(src):
            print(f"\n== {label}: MISSING {src}", flush=True); continue
        dst = os.path.join(g.CLAUDEDEV, "INSPECT_" + os.path.basename(src))
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copyfile(src, dst)
        try:
            inspect(label + "  [copy]", dst)
        finally:
            try:
                g.close_panel(dst)
            except Exception:
                pass
            time.sleep(0.3)
            try:
                os.remove(dst)
            except OSError as e:
                print("   copy not removed:", e, flush=True)
    # vendor VIs: read in place
    for label, p in VENDOR_VIS:
        inspect(label, p)
    # PI GCS command VIs inside .llb containers
    print(f"\n{'=' * 78}\n== probing the PI GCS .llb containers for the command VIs", flush=True)
    found = []
    for llb in PI_LLBS:
        for name in PI_NAMES:
            p = os.path.join(MERC_LL, llb, name)
            try:
                n = g.count(p, "Node")
                found.append((llb, name, n)); print(f"   FOUND {llb}\\{name}: {n} nodes", flush=True)
            except Exception:
                pass
    if not found:
        print("   none of the probed names resolved - list the .llb contents another way", flush=True)
    for llb, name, _ in found:
        inspect(f"PI {name} ({llb})", os.path.join(MERC_LL, llb, name))
    print("\nDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
