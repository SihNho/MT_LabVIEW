# ---
# labview: build
# hardware: none
# ---
r"""diag_c153_a2_8_readout - card 153-a2-8 step 1 (brief_153-a2-8.md): READ why find_donor returned None on the NI For Loop
scripting example in card 153-a2-2 (diag_c153_a2_2_queue_hygiene.log:9), instead of guessing. Read-only on a never-saved byte copy
scratch_c153_a2_8r_<stamp>.vi in claudeDev (deleted at the end); no op VI edited, no bed opened, no VI run.
EXISTING FIRST: gscript.count / report_all / node_terms_uid / uids (the same readers find_donor used, tools/bench/diag_c153_a2_2_queue_hygiene.py:55-66).
PREDICTION (none is asserted; this is a readout): prints Diagram count, report_all('Function') rows, report_all of a few node
classes, and for Diagram 0..3 up to 60 node_terms_uid rows (uid, class from the class maps, terminal names + is_source).
Gates: S byte copy, X LabVIEW gone, X scratch gone.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c153_a2_8_readout.log -- py -u tools/bench/diag_c153_a2_8_readout.py"""
import hashlib, os, shutil, subprocess, sys, time, traceback                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)               # noqa: E702
sys.path[:0] = [TOOLS, HERE]
import gscript as g                                                                             # noqa: E402
import bench_prep                                                                               # noqa: E402
import protocol as P                                                                            # noqa: E402
CD, TS, G = g.CLAUDEDEV, time.strftime("%Y%m%d_%H%M%S"), {}
EX = os.path.join(CD, "NIScriptingExamples", "Structures", "VI Scripting with Structures - For Loop.vi")
SRC = os.path.join(CD, "scratch_c153_a2_8r_%s.vi" % TS)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"


def gate(label, ok, detail=""):
    G[label] = bool(ok)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)
    return bool(ok)


def fact(*a):
    print("  FACT  " + " ".join(str(x) for x in a)[:3000], flush=True)


try:
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                     # noqa: E702
    fact("handles after restart", g.lv_counts())
    shutil.copyfile(EX, SRC); time.sleep(0.3)                                                  # noqa: E702
    gate("S source scratch is a byte copy of the For Loop example", md5(SRC) == md5(EX), (os.path.basename(SRC), md5(SRC)))
    g.ensure_loaded(SRC)
    CLS = {}
    for cls in ("Function", "Node", "SubVI", "Constant", "Control", "Indicator", "Terminal", "PropertyNode", "InvokeNode", "ForLoop",
                "Diagram", "Wire"):
        try:
            rows = g.report_all(SRC, cls)
            fact("report_all(%r): %d rows" % (cls, len(rows)), [(r["uid"], r["class"], r["owner"]) for r in rows][:40])
            for r in rows:
                CLS.setdefault(int(r["uid"]), r["class"])
        except Exception as e:                                                                  # noqa: BLE001
            fact("report_all(%r) raised" % cls, repr(e)[:200])
    try:
        fact("count(Diagram)", g.count(SRC, "Diagram"), "count(Function)", g.count(SRC, "Function"))
    except Exception as e:                                                                      # noqa: BLE001
        fact("count raised", repr(e)[:200])
    for d in range(4):
        for k in range(60):
            try:
                uid, rows = g.node_terms_uid(SRC, d, k)
            except Exception as e:                                                              # noqa: BLE001
                fact("D%d N%d node_terms_uid raised" % (d, k), repr(e)[:200]); break           # noqa: E702
            fact("D%d N%d uid %r class %r terms %r" % (d, k, uid, CLS.get(int(uid or 0)),
                                                       [(r["name"], r["is_source"], r["wire"]) for r in rows]))
            if not uid:
                break
    g.close_panel(SRC)
except Exception as e:                                                                          # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    try:
        g.reset(); fact("ref_counts", g.ref_counts(), "handles before kill", g.lv_counts())     # noqa: E702
    except Exception as e:                                                                      # noqa: BLE001
        fact("close-out read raised", repr(e)[:200])
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)  # noqa: E702
    gate("X LabVIEW gone (tasklist)", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    for _ in range(5):
        os.path.exists(SRC) and os.remove(SRC)
        if not os.path.exists(SRC):
            break
        time.sleep(3)
    gate("X scratch readout copy deleted", not os.path.exists(SRC), SRC)
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
    sys.exit(1 if bad else 0)
