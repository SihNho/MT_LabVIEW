# ---
# labview: build
# hardware: none
# ---
r"""diag_c153_a2_8_queue_hygiene - card 153-a2-8 (RETRY of 153-a2-2; brief_153-a2-8.md, docs/d1/ring-p4d.md PD371(d) + PD372(e)):
20-call op-hygiene records for the four OpQueue*_v0 ops (CLAUDE.md reference hygiene rule 2) before P5's lossless FIFO uses them.
A COPY of tools/bench/diag_c153_a2_2_queue_hygiene.py; the ONLY logic change is find_donor + the donor's Traverse class.
WHY: 153-a2-2 gate D failed because the NI For Loop example has NO Function-class node at all - READ by
tools/bench/diag_c153_a2_8_readout.log: count(Diagram) 2, report_all('Function') 0 rows, Diagram 0 Nodes[] = five Property nodes
(#399 #427 #267 #92 #291, each with named source outputs 'reference out' / 'error out' / ...), Diagram 1..3 empty.
EXISTING FIRST: gscript.hygiene_run (tools/gscript.py:366), gscript.queue_node (:1480) takes ANY Traverse class + index + named
OUTPUT (routeb_v1 passes the measured traverse class, build_d1_routeb_v1.py:1003; diag_c118_p1.py:75 passes 'SubVI'); a node's named
output is an accepted donor shape (diag_queue_donor2.py:16, round 1 12/0). So the donor is the first Diagram-0 node with a named
source output, addressed as Traverse 'Node' (the class report_all('Node') read on this file), its index re-read per call.
No op VI is edited or saved; no bed opened; no VI is run. Source = never-saved byte copy scratch_c153_a2_8_<stamp>.vi; hygiene copies
in claudeDev\scratch_c153_a2_8_<stamp>_hyg\, closed WITHOUT saving + deleted by hygiene_run each round.
MEASUREMENT CHOICE: total=20, per_round=5, recycle=True (4 never-saved byte copies per op; with one round max_dev_closed is 0 by construction).
PREDICTION: D donor found (Property #399 'reference out') / each op: 20 calls, 0 errors, exactly 1 new Function per call, h_closed within
+-100, refs live delta 0 -> record PASS / pins (s09 bed, 7 tools, 4 op VIs) unchanged / the 4 empty a2-2 _hyg dirs + own scratch gone / LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c153_a2_8_queue_hygiene.log -- py -u tools/bench/diag_c153_a2_8_queue_hygiene.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE)               # noqa: E702
sys.path[:0] = [TOOLS, HERE]
import gscript as g                                                                             # noqa: E402
import bench_prep                                                                               # noqa: E402
import protocol as P                                                                            # noqa: E402
CD, TS, G = g.CLAUDEDEV, time.strftime("%Y%m%d_%H%M%S"), {}
EX = os.path.join(CD, "NIScriptingExamples", "Structures", "VI Scripting with Structures - For Loop.vi")
SRC, HYG = os.path.join(CD, "scratch_c153_a2_8_%s.vi" % TS), os.path.join(CD, "scratch_c153_a2_8_%s_hyg" % TS)
OLD = [os.path.join(CD, "scratch_c153_a2_2_20261009_0746%s_hyg" % s) for s in ("25", "36", "44", "45")]
OPS = [("obtain", "OpQueueObtain_v0"), ("enqueue", "OpQueueEnqueue_v0"), ("dequeue", "OpQueueDequeue_v0"), ("release", "OpQueueRelease_v0")]
LOG = "tools/bench/diag_c153_a2_8_queue_hygiene.log"
DCLS = "Node"


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"


PINS = [os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi")] + [os.path.join(TOOLS, t) for t in (
    "stagekit.py", "addrcheck.py", "stagexec.py", "gscript.py", "stage_prerun.py", "stagesim.py", "vigraph.py")] + [
    os.path.join(CD, k + ".vi") for _, k in OPS]
PIN0, N, OUT = dict((p, md5(p)) for p in PINS), {"n": 0}, {"pins_before": {}, "records": {}}


def gate(label, ok, detail=""):
    G[label] = bool(ok)
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)
    return bool(ok)


def fact(*a):
    print("  FACT  " + " ".join(str(x) for x in a)[:1500], flush=True)


def loc():
    N["n"] += 1
    return (40 + (N["n"] % 10) * 70, 320 + ((N["n"] // 10) % 6) * 70)


def find_donor(W):
    """(diagram_index, node uid, first named OUTPUT, n Nodes) of the first Diagram-0 node (any class; Traverse 'Node') with a named
    source output - read, never assumed (153-a2-2's version required class Function, which this example has none of)."""
    nodes = set(int(o["uid"]) for o in g.report_all(W, DCLS))
    for k in range(60):
        uid, rows = g.node_terms_uid(W, 0, k)
        if not uid:
            break
        outs = [str(r["name"]) for r in rows if r["is_source"] and str(r["name"] or "").strip()]
        if int(uid) in nodes and outs:
            return 0, int(uid), outs[0], len(nodes)
    return None


def workload(kind, DON):
    st = {}

    def one(c, k, cls, src_uid, name):
        new = g.queue_node(k, c, cls, g._uid_index(c, cls, src_uid), name, DON[0], loc())
        if len(new) != 1:
            raise RuntimeError("queue_node(%s) new Function uids %r (want exactly 1)" % (k, new))
        return int(new[0])

    def work(c):
        if kind != "obtain" and st.get("path") != c:  # a fresh copy each round: ONE queue obtained on it, then the measured calls
            st["path"], st["q"] = c, one(c, "obtain", DCLS, DON[1], DON[2])
        if kind == "obtain":
            one(c, "obtain", DCLS, DON[1], DON[2])
        else:
            one(c, kind, "Function", st["q"], "queue out")
        return ""
    return work


try:
    fact("op VI mtimes", [(k, time.strftime("%Y-%m-%d %H:%M", time.localtime(os.path.getmtime(os.path.join(CD, k + ".vi"))))) for _, k in OPS])
    fact("md5 BEFORE", dict((os.path.basename(p), m) for p, m in PIN0.items()))
    gate("P0 s09 bed md5 eb1d0f31", PIN0[PINS[0]].startswith("eb1d0f31"), PIN0[PINS[0]])
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                     # noqa: E702
    fact("handles after restart", g.lv_counts())
    shutil.copyfile(EX, SRC); time.sleep(0.3); os.makedirs(HYG, exist_ok=True)                 # noqa: E702
    gate("S source scratch is a byte copy of the For Loop example", md5(SRC) == md5(EX), (os.path.basename(SRC), md5(SRC)))
    g.ensure_loaded(SRC)
    DON = find_donor(SRC)
    g.close_panel(SRC)
    if gate("D a node with a named output exists on the example (Traverse %r)" % DCLS, bool(DON), repr(DON)):
        for kind, key in OPS:
            op = os.path.join(CD, key + ".vi")
            try:
                rec = g.hygiene_run(op, workload(kind, DON), SRC, total=20, per_round=5, recycle=True, card="153-a2-8", log=LOG,
                                    scratch_dir=HYG, say=lambda m: fact("HYG", m), workload_text="queue_node('%s') on never-saved byte copies of "
                                    "%s (donor Traverse %s #%d %r; non-obtain: one Obtain per copy, then the measured calls on its 'queue out'), 4 x 5"
                                    % (kind, os.path.basename(EX), DCLS, DON[1], DON[2]))
            except Exception as e:                                                              # noqa: BLE001
                traceback.print_exc(); rec = {"status": "EXC %r" % e}                           # noqa: E702
            rp = g.op_hygiene_record_path(op)
            OUT["records"][key] = {"path": rp, "md5": md5(rp), "status": rec.get("status"), "h_pre": rec.get("h_pre"),
                                   "h_post": rec.get("h_post"), "h_closed": rec.get("h_closed")}
            if not gate("H %s: calls %s errors %s h_pre %s h_post %s h_closed %s max_dev %s refs %s; record md5 %s" % (
                    key, rec.get("calls"), rec.get("errors"), rec.get("h_pre"), rec.get("h_post"), rec.get("h_closed"),
                    rec.get("max_dev_closed"), rec.get("refs_live_delta"), md5(rp)), rec.get("status") == "PASS", rec.get("error_samples")):
                fact("STOP at the first failing op (card rule): %s; later ops not measured" % key)
                break
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
        os.path.exists(SRC) and os.remove(SRC); shutil.rmtree(HYG, ignore_errors=True)         # noqa: E702
        if not os.path.exists(SRC) and not os.path.exists(HYG):
            break
        time.sleep(3)
    for d in OLD:  # the 4 EMPTY dirs left by card 153-a2-2; os.rmdir refuses a non-empty dir, so nothing else can go
        try:
            os.path.isdir(d) and fact("old dir", os.path.basename(d), "entries", os.listdir(d)) is None and os.rmdir(d)
        except OSError as e:
            fact("old dir NOT removed", os.path.basename(d), repr(e)[:200])
    left = [p for p in os.listdir(CD) if p.startswith("scratch_c153_a2_") or p.startswith("scratch_hyg_")]
    gate("X no scratch_c153_a2_* / scratch_hyg_* left in claudeDev", not left, left)
    PIN1 = dict((p, md5(p)) for p in PINS)
    gate("X pins unchanged (s09 bed, 7 tools, 4 op VIs)", PIN1 == PIN0, [os.path.basename(p) for p in PINS if PIN1[p] != PIN0[p]])
    OUT["pins"] = dict((os.path.basename(p), m) for p, m in PIN1.items())
    json.dump(OUT, open(os.path.join(HERE, "diag_c153_a2_8_queue_hygiene_out.json"), "w", encoding="utf-8"), indent=1, default=str)
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": r["path"], "md5": r["md5"]} for r in OUT["records"].values() if r["md5"] != "MISSING"]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
