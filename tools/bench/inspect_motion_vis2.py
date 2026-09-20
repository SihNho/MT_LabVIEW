"""inspect_motion_vis2.py - READ-ONLY inspection of the motor / stage serial path, crash-tolerant and sub-diagram aware.

v1 was void: LabVIEW died at the first VI and the remaining nine results were RPC errors. The 3-cell probe
(nodeinfo_crash_probe.log) could not reproduce the crash with the same VI and the same call order, so it is recorded as a
transient, and the fix is structural rather than causal: **one VI per subprocess behind its own fresh LabVIEW**, so a crash
costs one VI instead of the batch.

v1 also asked the wrong question. `node_info` sees only the TOP-LEVEL diagram, and these driver VIs keep everything inside
case structures: `Mercury_comm.vi` reports 13 nodes of which exactly 2 are top level (an Unbundle By Name and a Case
Structure). So this version walks EVERY diagram index with `net_map`, whose per-node terminal names identify primitives —
a fixed delay shows up as a terminal called "milliseconds to wait", a blocking read as VISA Read's "byte count".

What we are looking for, from the user's account that the motor path was badly delayed despite 115200 baud:
  * a fixed `Wait (ms)` between write and read — would pin the round trip regardless of baud rate;
  * a read by byte count rather than termination character — would block until the VISA timeout
    (`Mercury_comm.vi`'s own help says the default is 5000 ms);
  * anything non-reentrant that both the frame loop and the motor loop call.

SAFETY: nothing is created, modified or saved. Lab VIs are inspected as copies in claudeDev and the copies are deleted.
Vendor VIs are opened read-only in place. Opening a driver VI does not run it, so no hardware is touched.
  py tools/bgrun.py --max-min 40 --log tools/bench/inspect_motion_vis2.log -- py -u tools/bench/inspect_motion_vis2.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
LVROOT = r"C:\Program Files\National Instruments\LabVIEW 2026"
LAB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
ASI = os.path.join(LVROOT, "instr.lib", "ASI TG-1000")
MERC_LL = os.path.join(LVROOT, "instr.lib", "Mercury", "GCS_LabVIEW", "Low Level")

TARGETS = [  # (label, path, copy_first)
    ("Mercury_comm (lab)", os.path.join(LAB, "PI Trans", "Mercury_comm.vi"), True),
    ("Motor control v5 (lab)", os.path.join(LAB, "SiHyeong Modified", "Motor control v5_No Recording.vi"), True),
    ("Global motor pos (lab)", os.path.join(LAB, "four-fold tracking", "Global motor pos.vi"), True),
    ("ASI_adjust focus (lab)", os.path.join(LAB, "Madcity", "ASI_adjust focus-subvi.vi"), True),
    ("Max Trans Pos (lab)", os.path.join(LAB, "DY", "Background VIs", "Max Trans Pos.vi"), True),
    ("ASI Send Serial Command", os.path.join(ASI, "Public", "Utility", "Send Serial Command.vi"), False),
    ("ASI Get Current Position", os.path.join(ASI, "Public", "Status", "Get Current Position.vi"), False),
    ("ASI Move Axis to Position", os.path.join(ASI, "Public", "Action", "Move Axis to Position.vi"), False),
]

# Pass 2: the PI GCS command VIs the lab wrapper actually calls per command, located 2026-09-12 inside the .llb containers.
# These are the per-command path for the magnet motor, so a fixed Wait here is the one that would hurt most.
PI_TARGETS = [
    ("PI MOV (General command.llb)", os.path.join(MERC_LL, "General command.llb", "MOV.vi"), False),
    ("PI POS? (General command.llb)", os.path.join(MERC_LL, "General command.llb", "POS?.vi"), False),
    ("PI VEL (General command.llb)", os.path.join(MERC_LL, "General command.llb", "VEL.vi"), False),
    ("PI TMN? (Limits.llb)", os.path.join(MERC_LL, "Limits.llb", "TMN?.vi"), False),
    ("PI TMX? (Limits.llb)", os.path.join(MERC_LL, "Limits.llb", "TMX?.vi"), False),
    ("PI GOH (Limits.llb)", os.path.join(MERC_LL, "Limits.llb", "GOH.vi"), False),
]
if "--pi" in sys.argv:
    TARGETS = PI_TARGETS

CHILD = r'''
import os, shutil, sys, time
sys.path.insert(0, r"{tools}")
import gscript as g
g._lv = None; g._run.__defaults__ = (6.0, 45.0)
src, copy_first = r"{src}", {copy}
dst = src
if copy_first:
    dst = os.path.join(g.CLAUDEDEV, "INSPECT_" + os.path.basename(src))
    if os.path.exists(dst):
        os.remove(dst)
    shutil.copyfile(src, dst)
try:
    counts = {{c: g.count(dst, c) for c in ("Node", "SubVI", "Diagram", "CaseStructure", "WhileLoop",
                                            "ForLoop", "Sequence", "Constant", "Wire")}}
    print("counts:", {{k: v for k, v in counts.items() if v}}, flush=True)
    try:
        print("top-level styles:", [(i, s) for i, s, _ in g.node_info(dst, max_n=80)], flush=True)
    except Exception as e:
        print("node_info:", str(e)[:120], flush=True)
    nd = counts.get("Diagram", 1)
    t0 = time.time()
    for d in range(min(nd, 20)):
        try:
            nodes, nets = g.net_map(dst, diagram_index=d, max_nodes=60, max_terms=24)
        except Exception as e:
            print("  diagram %d: net_map failed %s" % (d, str(e)[:90]), flush=True); continue
        if not nodes:
            continue
        print("  --- diagram %d: %d node(s)" % (d, len(nodes)), flush=True)
        for n, (style, label, terms) in nodes.items():
            names = [nm for _, nm, _ in terms if nm]
            print("     node %s %r terms=%s" % (n, label, names[:14]), flush=True)
        if time.time() - t0 > 420:
            print("  (time budget reached, stopping the diagram walk)", flush=True); break
finally:
    if copy_first:
        try:
            g.close_panel(dst); time.sleep(0.3); os.remove(dst)
        except Exception:
            pass
print("CHILD OK", flush=True)
'''


def alive():
    return subprocess.run(["powershell", "-NoProfile", "-Command",
                           "if (Get-Process -Name LabVIEW -ErrorAction SilentlyContinue) {'alive'} else {'DEAD'}"],
                          capture_output=True, text=True, timeout=60).stdout.strip()


def main():
    for label, path, copy_first in TARGETS:
        print(f"\n{'=' * 78}\n== {label}\n   {path}", flush=True)
        # a VI inside an .llb is not a filesystem entry, so check the CONTAINER instead (the whole PI pass was
        # skipped as MISSING on 2026-09-12 because of this)
        probe_path = path.split(".llb")[0] + ".llb" if ".llb" in path else path
        if not os.path.exists(probe_path):
            print("   MISSING", flush=True); continue
        try:
            subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400, cwd=ROOT)
        except subprocess.TimeoutExpired:
            print("   lv_restart TIMEOUT", flush=True); continue
        code = CHILD.format(tools=TOOLS, src=path, copy=copy_first)
        try:
            p = subprocess.run([sys.executable, "-u", "-c", code], timeout=900, cwd=ROOT, capture_output=True, text=True)
            print(p.stdout.rstrip(), flush=True)
            if p.stderr.strip():
                print("   STDERR:", p.stderr.strip()[-500:], flush=True)
        except subprocess.TimeoutExpired:
            print("   child TIMEOUT", flush=True)
        print(f"   LabVIEW after: {alive()}", flush=True)
    if "--pi" in sys.argv:
        print("\nDONE (PI pass)", flush=True); return 0
    # the PI GCS command VIs live inside .llb containers - find them, then inspect in a later pass
    print(f"\n{'=' * 78}\n== probing the PI GCS .llb containers", flush=True)
    subprocess.run([sys.executable, os.path.join(TOOLS, "lv_restart.py")], timeout=400, cwd=ROOT)
    probe = ("import os,sys; sys.path.insert(0, r'%s'); import gscript as g; g._lv=None; g._run.__defaults__=(6.0,30.0)\n"
             "root=r'%s'\n"
             "for llb in ('General command.llb','Support.llb','Communication.llb','Limits.llb','Old commands.llb','Special command.llb'):\n"
             "    for nm in ('MOV.vi','POS?.vi','VEL.vi','TMN?.vi','TMX?.vi','SetCommand.vi','GOH.vi','SendCommand.vi','GetAnswer.vi','ReadAnswer.vi'):\n"
             "        p=os.path.join(root,llb,nm)\n"
             "        try:\n"
             "            print('FOUND', llb+'\\\\'+nm, g.count(p,'Node'), 'nodes,', g.count(p,'Diagram'), 'diagrams', flush=True)\n"
             "        except Exception:\n"
             "            pass\n") % (TOOLS, MERC_LL)
    try:
        p = subprocess.run([sys.executable, "-u", "-c", probe], timeout=900, cwd=ROOT, capture_output=True, text=True)
        print(p.stdout.rstrip() or "   (nothing resolved)", flush=True)
        if p.stderr.strip():
            print("   STDERR:", p.stderr.strip()[-400:], flush=True)
    except subprocess.TimeoutExpired:
        print("   probe TIMEOUT", flush=True)
    print("\nDONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
