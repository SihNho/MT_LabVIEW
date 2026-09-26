r"""diag_c97_tools_fixprobe.py - card 97-2, READ-ONLY: is there a small existing VI with a For loop INSIDE a While loop
(+ a node chain in the For body) to use as the tools' self-test fixture?  Candidates are NI example TARGETS, read on a
BYTE COPY (scratch_c97_fp_*.vi in claudeDev, deleted at the end). Nothing is edited, nothing saved, no VI is run.
PRIOR ART: graph_harness_copyloop_c95.json (For only, no While) and graph_oploopcast_v0_c95.json (For only) - neither fits.
PREDICTION: each candidate prints its structures with owner chain; LabVIEW killed at the end; RESULT line last.
"""
import os, shutil, subprocess, sys, time  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))  # noqa: E702
import gscript as g  # noqa: E402
import protocol as P  # noqa: E402
import build_d1_v0 as B  # noqa: E402
g._run.__defaults__ = (6.0, 90.0)
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects")
CANDS = [os.path.join(EX, "Test - Navigating Structures Target.vi"), os.path.join(EX, "Test - Navigating Nodes and Wires Target.vi"),
         os.path.join(EX, "Test - Using Traverse.vi")]
STRUCT = ("WhileLoop", "ForLoop", "CaseStructure", "FlatSequence", "EventStructure", "Diagram", "TopLevelDiagram")
npass, nfail, scr = 0, 0, []
for i, src in enumerate(CANDS):
    if not os.path.exists(src):
        print("  FACT  missing", src); continue
    dst = os.path.join(g.CLAUDEDEV, "scratch_c97_fp_%d_%s.vi" % (i, time.strftime("%H%M%S")))
    shutil.copyfile(src, dst); scr.append(dst)
    try:
        g.ensure_loaded(dst)
        objs = g.report_all(dst, "GObject")
        cls = {}
        for o in objs:
            cls[o["class"]] = cls.get(o["class"], 0) + 1
        print("  FACT  %s ES=%s classes=%s" % (os.path.basename(src), g.exec_state(dst), cls), flush=True)
        for o in objs:
            if o["class"] in STRUCT[:5]:
                try:
                    oc, ou = B.owner_of(dst, int(o["uid"]), strict=False)
                    oc2, ou2 = B.owner_of(dst, int(ou), strict=False) if ou else ("", 0)
                except Exception as e:  # noqa: BLE001
                    oc, ou, oc2, ou2 = "ERR", str(e)[:60], "", 0
                print("  FACT     %s #%s owner %s#%s <- %s#%s" % (o["class"], o["uid"], oc, ou, oc2, ou2), flush=True)
        npass += 1
    except Exception as e:  # noqa: BLE001
        nfail += 1; print("  FAIL  read %s: %s" % (os.path.basename(src), str(e)[:200]), flush=True)
for p in scr:
    try:
        g.close_panel(p)
    except Exception:  # noqa: BLE001
        pass
subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)
for p in scr:
    try:
        os.remove(p)
    except OSError as e:
        print("  FACT  could not delete", p, e)
gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
left = [p for p in scr if os.path.exists(p)]
print("  FACT  LabVIEW gone:", gone, "scratch left:", left)
print(P.result_line({"status": "PASS" if not nfail and gone and not left else "FAIL", "gates": {"pass": npass, "fail": nfail},
                     "first_fail": None, "artefacts": []}))
