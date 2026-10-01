r"""diag_c126_1_hyg - card 126-1 STEP 2 (brief_126-1.md, PD253(b)): OpFsAddFrame_v0's op-hygiene THROUGH gscript.hygiene_run (recycle).
EXISTING FIRST: the workload is diag_c125_5_opfs.py add() verbatim (raw op call: _set_common + rfi 0 + After T + _run, echo/err read back)
on FS #1309 of fresh never-saved byte copies of the NI example `VI Scripting with Structures - For Loop.vi` (claudeDev copy), labels
tools/bench/opfs_v0_labels.json; runner gscript.hygiene_run (STEP 1, self-test 13/0); frame count = report_all Diagram owners (as before).
The op VI is NOT changed (md5 cfaa304f... read before and after). No stage recipe, no bed touched.
PREDICTION: H0 op md5 == cfaa304f6fcfbc7190f7c5d55ced2bb6 / H1 20 rounds x 100 Add Frame(0, After T): 0 errors (echo 1309, err ''),
every round 101 frames / H2 h_closed flat +-100 across the 20 rounds (h_pre - h_closed = the copy's load cost, h_post - h_pre ~ 0) /
H3 record op_hygiene/OpFsAddFrame_v0.json status PASS with md5 == the op's / X op md5 unchanged, no scratch left, LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c126_1_hyg.log -- py -u tools/bench/diag_c126_1_hyg.py"""
import json, os, subprocess, sys, time, traceback                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)                    # noqa: E702
import gscript as g                                                                         # noqa: E402
import protocol as P                                                                        # noqa: E402
import bench_prep                                                                           # noqa: E402
OPA, OPM = os.path.join(g.CLAUDEDEV, "OpFsAddFrame_v0.vi"), "cfaa304f6fcfbc7190f7c5d55ced2bb6"
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Structures", "VI Scripting with Structures - For Loop.vi")
FS, LOGP = 1309, "tools/bench/diag_c126_1_hyg.log"
L = json.load(open(os.path.join(HERE, "opfs_v0_labels.json"), encoding="utf-8"))["OpFsAddFrame_v0"]
G, TI = {}, {}
g._run.__defaults__ = (6.0, 120.0)


def gate(label, ok, detail=""):
    G[label] = bool(ok)
    print("%s | %s | %s" % ("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)
    return bool(ok)


def add(t):
    if t not in TI:
        TI.clear(); TI[t] = g._uid_index(t, "FlatSequence", FS)                             # noqa: E702
    vi = g.op(OPA); g._set_common(vi, t, L, "FlatSequence", TI[t])                         # noqa: E702
    vi.SetControlValue(L["rfi"], 0); vi.SetControlValue(L["after"], True); g._run(vi)       # noqa: E702
    echo, err = int(vi.GetControlValue(L["fs_echo"]) or 0), g._err(vi, L["Err"]) or ""
    return "" if (echo, err) == (FS, "") else "echo %s err %r" % (echo, err)


def frames_ok(t):
    n = len([o for o in g.report_all(t, "Diagram") if o["owner"] == "FlatSequenceFrame"])
    return [] if n == 101 else ["frames %d != 101" % n]


def md5(p):
    return g._md5_file(p)


try:
    gate("H0 op md5 == cfaa304f (unchanged since card 125-5)", md5(OPA) == OPM, md5(OPA))
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                  # noqa: E702
    print("FACT start counts %s" % g.lv_counts(), flush=True)
    rec = g.hygiene_run(OPA, add, EX, total=2000, per_round=100, recycle=True, check=frames_ok, card="126-1", log=LOGP,
                        workload_text="20 rounds x 100 raw OpFsAddFrame_v0 calls, Add Frame(0, After T) on FS #%d of a fresh never-saved byte copy "
                                      "of %s per round, closed without saving + deleted each round (gscript.hygiene_run, PD242(b))" % (FS, os.path.basename(EX)))
    pre_minus_closed = [a - b for a, b in zip(rec["h_pre"], rec["h_closed"])]
    post_minus_pre = [a - b for a, b in zip(rec["h_post"], rec["h_pre"])]
    print("FACT h_pre %s" % rec["h_pre"], flush=True)
    print("FACT h_post %s" % rec["h_post"], flush=True)
    print("FACT h_closed %s" % rec["h_closed"], flush=True)
    print("FACT h_post-h_pre %s | h_pre-h_closed %s" % (post_minus_pre, pre_minus_closed), flush=True)
    print("FACT gdi pre/post/closed %s / %s / %s" % (rec["gdi_pre"], rec["gdi_post"], rec["gdi_closed"]), flush=True)
    print("FACT user pre/post/closed %s / %s / %s" % (rec["user_pre"], rec["user_post"], rec["user_closed"]), flush=True)
    print("FACT private_closed %s" % rec["private_closed"], flush=True)
    gate("H1 20 x 100 Add Frame: 0 errors, 101 frames every round", rec["errors"] == 0 and not rec["check_problems"] and rec["calls"] == 2000,
         (rec["errors"], rec["error_samples"][:3], rec["check_problems"][:3]))
    gate("H2 h_closed flat +-100 across 20 rounds (max dev %s), refs live delta 0" % rec["max_dev_closed"],
         rec["max_dev_closed"] is not None and rec["max_dev_closed"] <= 100 and rec["refs_live_delta"] == 0, (rec["h_closed"], rec["refs_live_delta"]))
    gate("H3 record op_hygiene/OpFsAddFrame_v0.json PASS, md5 == op", rec["status"] == "PASS" and rec["md5"] == OPM, (rec["status"], rec["md5"]))
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    left = [f for f in os.listdir(g.CLAUDEDEV) if f.startswith("scratch_hyg_OpFsAddFrame")]
    for f in left:
        os.remove(os.path.join(g.CLAUDEDEV, f))
    gate("X no hygiene copy left open on disk (left before cleanup: %d)" % len(left), not left, left[:3])
    gate("X op md5 unchanged", md5(OPA) == OPM, md5(OPA))
    bad = [k for k, v in G.items() if not v]
    rp = g.op_hygiene_record_path(OPA)
    arts = [{"path": p, "md5": md5(p)} for p in (rp, os.path.join(ROOT, "tools", "gscript.py")) if os.path.exists(p)]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
