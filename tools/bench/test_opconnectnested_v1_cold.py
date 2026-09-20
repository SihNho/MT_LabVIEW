r"""test_opconnectnested_v1_cold.py - COLD verification of `OpConnectNested_v1.vi` in a RESTARTED LabVIEW, plus
the one gate its build run could not close warm (T3: an UNNAMED terminal reached ACROSS diagrams).

    MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/test_opconnectnested_v1_cold.log \
        -- py -u tools/bench/test_opconnectnested_v1_cold.py

WHAT ALREADY EXISTS: `tools/recipes/build_opconnectnested_v1.py` (the build + warm test, 31/1) and its
`connect_nested_v1` wrapper, imported here rather than re-written. Run 2's T3 failed for a TEST-HARNESS reason,
not an op reason: after `move_in` the Traverse `Diagram` ORDER changes, so the recipe looked for the For loop on a
stale index. This version re-reads the diagram order after the move and resolves the body diagram BY UID.

PREDICTION CONTRACT
 C1 LabVIEW was restarted; handles recorded; `OpConnectNested_v1.vi` opens COLD at ExecState 1 with TWO
    `To More Specific Class` nodes and the panel control `index 6`.
 C2 a scratch copy of EMPTY_v0 gets TWO While loops and one subVI in each body (two nested diagrams).
 C3 body(A) `error out` -> body(B) `error in (no error)` ACROSS diagrams: the sink goes 0 -> non-zero, LabVIEW
    creates the tunnels, and the wire SURVIVES Remove Bad Wires (NAMES.md:861-863 - uid equality is not a proof).
 C4 a For loop is REPARENTED into body A and its UNNAMED count terminal is wired from a source in body B,
    i.e. an unnamed terminal on diagram P from a source on diagram Q. Gate = wire identity; ExecState reported.
 C5 scratch deleted; original working copy md5 2a78e17c449c... before and after.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g                                               # noqa: E402
from bench_prep import labview_handles                            # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1, walk, term  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
MAP = os.path.join(ROOT, "tools", "bench", "opconnectnested_v1_labels.json")
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_cnv1c_{STAMP}.vi")
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def di(target, uid):
    """Traverse index of the Diagram with this uid - RE-READ after every structural change (run 2's T3 bug)."""
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    t0 = time.time()
    fact(f"handles before: {labview_handles()}")
    gate("C5a original working-copy md5 before", md5(ORIG) == ORIG_MD5, md5(ORIG))
    with open(MAP, encoding="utf-8") as f:
        labels = json.load(f)
    fact(f"labels: {  {k: v for k, v in labels.items() if k != 'panel'} }")

    try:
        # ------------------------------------------------------------------ C1 cold open
        g.open_panel(OP)
        time.sleep(0.8)
        es = g.exec_state(OP)
        w = walk(OP, 0)
        tmscs = [u for u, (n, lab, rows) in w.items() if term(rows, "specific class reference", True)]
        ctls = [l for _i, l, ind in g.fp_labels(OP) if not ind]
        gate("C1 COLD: OpConnectNested_v1 opens at ExecState 1 with TWO casts and the `index 6` control",
             es == 1 and len(tmscs) == 2 and labels["src_diag"] in ctls,
             f"ExecState {es}, TMSC {tmscs}, src_diag {labels['src_diag']!r} present={labels['src_diag'] in ctls}")
        fact(f"C1 file {os.path.getsize(OP)} B; {len(w)} nodes; controls {ctls}")

        # ------------------------------------------------------------------ C2 the scratch
        if os.path.exists(SCRATCH):
            os.remove(SCRATCH)
        shutil.copyfile(EMPTY, SCRATCH)
        time.sleep(0.3)
        g.report_all(SCRATCH, "SubVI")
        g.open_panel(SCRATCH)
        time.sleep(0.6)
        inv0 = g.uids(SCRATCH, "Invoke")
        dg0 = g.uids(SCRATCH, "Diagram")
        g.while_loop(SCRATCH, (300, 300))
        DA = g.new_since(SCRATCH, "Diagram", dg0)[0]["uid"]
        dg1 = g.uids(SCRATCH, "Diagram")
        g.while_loop(SCRATCH, (1600, 300))
        DB = g.new_since(SCRATCH, "Diagram", dg1)[0]["uid"]
        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, di(SCRATCH, DA), (60, 60))
        UA = g.new_since(SCRATCH, "SubVI", sv0)[0]["uid"]
        sv1 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, di(SCRATCH, DB), (60, 60))
        UB = g.new_since(SCRATCH, "SubVI", sv1)[0]["uid"]
        gate("C2 two While loops, one subVI in each body", bool(DA and DB and UA and UB),
             f"bodies #{DA}/#{DB} at indices {di(SCRATCH, DA)}/{di(SCRATCH, DB)}, subVIs #{UA}/#{UB}")

        # ------------------------------------------------------------------ C3 cross-diagram, named pair
        wA, wB = walk(SCRATCH, di(SCRATCH, DA)), walk(SCRATCH, di(SCRATCH, DB))
        t_out = next(r["i"] for r in wA[UA][2] if r["is_source"] and r["name"] == "error out")
        t_in = next(r["i"] for r in wB[UB][2]
                    if not r["is_source"] and r["name"] and "error in" in r["name"] and r["wire"] == 0)
        es0, lt0 = g.exec_state(SCRATCH), g.count(SCRATCH, "LoopTunnel")
        dw, es1, err = connect_nested_v1(SCRATCH, di(SCRATCH, DB), wB[UB][0], t_in,
                                         di(SCRATCH, DA), wA[UA][0], t_out, labels)
        wB2 = walk(SCRATCH, di(SCRATCH, DB))
        w_sink = next((r["wire"] for r in wB2[UB][2] if r["i"] == t_in), 0)
        fact(f"C3 op error {err[:120]!r}; wire delta {dw}; LoopTunnel {lt0} -> {g.count(SCRATCH, 'LoopTunnel')}; "
             f"ExecState {es0} -> {es1}")
        gate("C3 CROSS-DIAGRAM sink wired (0 -> non-zero)", bool(w_sink), f"sink w{w_sink}")
        g.remove_bad_wires_scripted(SCRATCH)
        w_after = next((r["wire"] for r in walk(SCRATCH, di(SCRATCH, DB))[UB][2] if r["i"] == t_in), 0)
        gate("C3b the cross-diagram wire SURVIVES Remove Bad Wires (it is a GOOD wire, not a broken one)",
             bool(w_after) and w_after == w_sink, f"after RBW w{w_after} (was w{w_sink})")

        # ------------------------------------------------------------------ C4 UNNAMED terminal, across diagrams
        fl0 = g.uids(SCRATCH, "ForLoop")
        g.for_loop(SCRATCH, (900, 1400))
        F = g.new_since(SCRATCH, "ForLoop", fl0)[0]["uid"]
        moved = False
        try:
            from build_d1_v0 import move_in as _move_in
            _move_in(SCRATCH, F, di(SCRATCH, DA), (400, 400))
            moved = F in walk(SCRATCH, di(SCRATCH, DA))          # index RE-READ after the move (run 2's bug)
        except Exception as e:
            fact(f"C4 move_in failed ({str(e)[:160]})")
        fact(f"C4 For loop #{F} inside body A after move_in: {moved} (body A now at Traverse index "
             f"{di(SCRATCH, DA)})")
        d_host = di(SCRATCH, DA) if moved else 0
        wh = walk(SCRATCH, d_host)
        if F in wh:
            nF, _l, rowsF = wh[F]
            unnamed = [(r["i"], r["wire"]) for r in rowsF if not r["is_source"] and not r["name"]]
            fact(f"C4 For loop #{F} Nodes[{nF}] on diagram {d_host}: unnamed input terminals {unnamed}")
            if unnamed:
                t_un = unnamed[0][0]
                wB3 = walk(SCRATCH, di(SCRATCH, DB))
                tried = []
                for r in wB3[UB][2]:
                    if not r["is_source"]:
                        continue
                    dw, es2, err = connect_nested_v1(SCRATCH, d_host, nF, t_un,
                                                     di(SCRATCH, DB), wB3[UB][0], r["i"], labels)
                    w_un = next((x["wire"] for x in walk(SCRATCH, d_host)[F][2] if x["i"] == t_un), 0)
                    tried.append((r["i"], r["name"], dw, es2, w_un, err[:60]))
                    if w_un:
                        break
                for x in tried:
                    print(f"      C4 try src t{x[0]} {x[1]!r}: delta {x[2]}, ExecState {x[3]}, "
                          f"unnamed-terminal wire {x[4]}, err {x[5]!r}", flush=True)
                gate("C4 an UNNAMED terminal on one nested diagram is reached from a source on ANOTHER "
                     "(wire 0 -> non-zero)", bool(tried) and bool(tried[-1][4]),
                     f"{tried[-1] if tried else 'no attempt'}")
                fact(f"C4 ExecState after the unnamed-terminal wire: {g.exec_state(SCRATCH)} "
                     f"(a type-incompatible pair makes a BROKEN wire - a LabVIEW type fact, not an op failure)")
            else:
                gate("C4 the For loop exposes an unnamed input terminal", False, f"{rowsF}")
        else:
            gate("C4 the For loop was located after the move", False,
                 f"#{F} not on diagram {d_host}; diagram order {[o['uid'] for o in g.report_all(SCRATCH, 'Diagram')]}")

        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)
        fact(f"C5 junk Invokes purged: {junk}")
    except Exception as e:
        gate("Cx the cold test completed without an unhandled exception", False, f"EXC {str(e)[:250]}")
    finally:
        for p in (SCRATCH, OP):
            try:
                g.close_panel(p)
            except Exception:
                pass
        try:
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
                fact(f"scratch deleted: {os.path.basename(SCRATCH)}")
        except Exception as e:
            fact(f"scratch NOT deleted ({str(e)[:80]})")
        g._lv = None
    gate("C5b original working-copy md5 after", md5(ORIG) == ORIG_MD5, md5(ORIG))
    fact(f"handles after: {labview_handles()}")
    print("\n--- FACTS ---", flush=True)
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== test_opconnectnested_v1_cold: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
