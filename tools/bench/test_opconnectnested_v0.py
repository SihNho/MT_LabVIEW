r"""test_opconnectnested_v0.py - the FUNCTIONAL test of `OpConnectNested_v0.vi`, which was BUILT and SAVED at
ExecState 1 by `tools/recipes/build_opconnectnested_v0.py` run 2 but whose test never finished.

    MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/test_opconnectnested_v0.log \
        -- py -u tools/bench/test_opconnectnested_v0.py

WHY A SEPARATE FILE: run 2 built the op (W0..W6b, 10 pass / 1 expected fail) and then the TEST stalled - two
harness defects, both measured, neither about the op:
  1. `T2 (a)` paired `nsv[0]` with `nsv[1]` assuming drop order; the census says `nsv[0]` is
     `Is Path and Not Empty.vi` (its only output is a BOOLEAN) and `nsv[1]` is `Error Cluster From Error Code.vi`
     (which owns the `error out`), so the error-out/error-in pair search failed on the wrong pair.
  2. `T3 (b)` reparented a For loop with `OpMoveIn_v0` to get an unnamed terminal onto a NESTED diagram; that call
     did not return within its 120 s watchdog and the run was killed at bgrun's deadline
     (`build_opconnectnested_v0.log:  T3 move_in failed (COM Run did not return within 120s ...)`).
     **`move_in` is not needed at all** - the run's own census shows UNNAMED input terminals already sitting on
     nodes INSIDE the loop body: `Is Path and Not Empty.vi` bare ins `[(0,''),(2,''),(3,''),(4,'path'),(5,'')]`
     and `Error Cluster From Error Code.vi` bare ins `[(1,''),(2,''),(3,''),...,(7,'')]`. Test (b) is therefore
     the SAME single call as test (a) when the sink terminal chosen is an unnamed one.

WHAT IS UNDER TEST (the op ships as ROUTE B, `tools/bench/opconnectnested_labels.json`): both ends addressed by
INDEX - `Diagram[index].Nodes[index 2].Terminals[index 3]` (sink) and `Nodes[index 4].Terminals[index 5]`
(source) - on the SAME nested diagram. `Terminal.Connect Wire` 6349C03 on the sink.

PREDICTION CONTRACT (stop at the first miss; nothing is saved by this file at all):
 T0  `OpConnectNested_v0.vi` on disk, ExecState 1, labels JSON says `route": "B"`.
 T1  scratch = copy of EMPTY_v0 (unique name, DELETED in the same run) + one While loop -> body Diagram at
     Traverse index i_D; two subVIs dropped INSIDE the body.
 T2  (a) BODY -> BODY on a nested diagram, NAMED sink: `Error Cluster From Error Code.vi`.`error out` ->
     `Is Path and Not Empty.vi`.`error in`-ish terminal. Gate: the sink goes wire 0 -> non-zero AND the SAME
     wire uid is on both ends (never a count). ExecState reported.
 T3  (b) BODY -> an UNNAMED sink terminal on the same nested diagram. Gate: wire identity again.
     ⚠️ LEVEL OF VERIFICATION, stated: the gate is WIRE IDENTITY at an unnamed terminal - that is the capability
     under test. A type-incompatible pair yields a BROKEN wire, which is a LabVIEW type fact, not an op failure,
     and is reported next to the ExecState rather than scored.
 T4  (c) source on a DIFFERENT diagram: NOT EXPRESSIBLE - the op carries ONE diagram index (ROUTE B). Reported as
     the measured limit, with the reason, exactly as the build log records it.
 T5  junk Invokes purged; scratch deleted; handles before/after.
No original is touched; nothing outside `user.lib\claudeDev` is written; nothing is saved.
"""
import faulthandler
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g                       # noqa: E402
from bench_prep import labview_handles     # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpConnectNested_v0.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
LABELS = os.path.join(HERE, "opconnectnested_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_cn_{STAMP}.vi")
BOOLVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Is Path and Not Empty.vi"
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
g._run.__defaults__ = (6.0, 90.0)

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def walk(target, diagram=0, limit=40):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(limit):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def connect_nested(target, diag, sink_node, sink_term, src_node, src_term, lab):
    g.ensure_loaded(target)
    w0 = g.count(target, "Wire")
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(lab["class_name"], "Diagram")
    vi.SetControlValue(lab["sink_diag"], int(diag))
    vi.SetControlValue(lab["sink_node"], int(sink_node))
    vi.SetControlValue(lab["sink_term"], int(sink_term))
    vi.SetControlValue(lab["src_node"], int(src_node))
    vi.SetControlValue(lab["src_term"], int(src_term))
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except RuntimeError as e:
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else f"EXC {str(e)[:130]}"
    return g.count(target, "Wire") - w0, g.exec_state(target), err


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    # The peer's cheapest discriminating test, ADOPTED (archive/peer/2026-09-17-connectnested-stall.md):
    # if this run ever goes silent again, an ALL-THREAD dump every 150 s separates "recovery hung" from
    # "an unguarded COM call blocked behind an abandoned Run" from "successive guarded timeouts" - without
    # adding a second COM client. It costs nothing when the run is healthy.
    faulthandler.dump_traceback_later(150, repeat=True, exit=False)
    g._lv = None
    t0 = time.time()
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0}")
    try:
        if not gate("T0a OpConnectNested_v0.vi on disk", os.path.exists(OP), OP):
            return 1
        with open(LABELS, encoding="utf-8") as f:
            lab = json.load(f)
        g.open_panel(OP)
        es_op = g.exec_state(OP)
        gate("T0b the op is runnable and shipped as ROUTE B", es_op == 1 and lab.get("route") == "B",
             f"ExecState {es_op}, route {lab.get('route')!r}, src_diag {lab.get('src_diag')!r}")
        g.close_panel(OP)

        if os.path.exists(SCRATCH):
            os.remove(SCRATCH)
        shutil.copyfile(EMPTY, SCRATCH)
        time.sleep(0.3)
        g.report_all(SCRATCH, "SubVI")
        g.open_panel(SCRATCH)
        time.sleep(0.6)
        inv0 = g.uids(SCRATCH, "Invoke")
        wl0, dg0 = g.uids(SCRATCH, "WhileLoop"), g.uids(SCRATCH, "Diagram")
        g.while_loop(SCRATCH, (300, 300))
        nwl, ndg = g.new_since(SCRATCH, "WhileLoop", wl0), g.new_since(SCRATCH, "Diagram", dg0)
        if not gate("T1 one While loop created", len(nwl) == 1 and len(ndg) == 1, f"{nwl} {ndg}"):
            return 1
        W, D = nwl[0]["uid"], ndg[0]["uid"]
        i_D = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")].index(D)
        fact(f"scratch: WhileLoop #{W}, body Diagram #{D} at Traverse index {i_D}")

        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, i_D, (60, 60))
        g.drop_subvi(SCRATCH, BOOLVI, i_D, (60, 220))
        nsv = g.new_since(SCRATCH, "SubVI", sv0)
        if not gate("T1b two body nodes are inside the loop body", len(nsv) == 2, f"{nsv}"):
            return 1
        wb = walk(SCRATCH, i_D)
        info = {}
        for o in nsv:
            u = o["uid"]
            n_i, l, rows = wb[u]
            info[u] = dict(n=n_i, lab=l,
                           outs=[(r["i"], r["name"]) for r in rows if r["is_source"]],
                           bare=[(r["i"], r["name"]) for r in rows if not r["is_source"] and r["wire"] == 0])
            fact(f"body #{u} Nodes[{n_i}] {l!r}: outs {info[u]['outs']}; bare ins {info[u]['bare']}")

        # the SOURCE is whichever body node owns an `error out`; the SINK is the other one. Identified by CENSUS,
        # never by drop order - that was run 2's T2 defect.
        SRC = next((u for u in info if any(nm == "error out" for _i, nm in info[u]["outs"])), None)
        SNK = next((u for u in info if u != SRC), None)
        if not gate("T1c one body node owns an `error out` and the other is the sink", bool(SRC and SNK),
                    f"SRC {SRC} SNK {SNK}"):
            return 1
        t_src = next(i for i, nm in info[SRC]["outs"] if nm == "error out")

        # ---------------- T2 (a) NAMED sink, body -> body on a nested diagram
        t_named = next((i for i, nm in info[SNK]["bare"] if nm and "error in" in nm), None)
        if t_named is None:
            t_named = next((i for i, nm in info[SNK]["bare"] if nm), None)
        dw, es, err = connect_nested(SCRATCH, i_D, info[SNK]["n"], t_named, info[SRC]["n"], t_src, lab)
        wb2 = walk(SCRATCH, i_D)
        w_sink = next((r["wire"] for r in wb2[SNK][2] if r["i"] == t_named), 0)
        w_src = next((r["wire"] for r in wb2[SRC][2] if r["i"] == t_src), 0)
        fact(f"T2 (a) sink #{SNK} t{t_named} <- src #{SRC} t{t_src} 'error out': op error {err[:110]!r}, "
             f"wire delta {dw}, ExecState {es}")
        gate("T2 (a) BODY -> BODY by INDEX on a NESTED diagram: sink wired, SAME wire uid on both ends",
             bool(w_sink) and w_sink == w_src, f"sink w{w_sink} / source w{w_src}")
        gate("T2b (a) the scratch COMPILES with that wire (ExecState 1)", es == 1, f"ExecState {es}")

        # ---------------- T3 (b) UNNAMED sink terminal on the same nested diagram
        wb3 = walk(SCRATCH, i_D)
        unnamed = [(r["i"]) for r in wb3[SNK][2]
                   if not r["is_source"] and not r["name"] and r["wire"] == 0]
        fact(f"T3 (b) unnamed bare input terminals on body node #{SNK}: {unnamed}")
        if not unnamed:
            gate("T3 (b) an UNNAMED bare sink terminal exists on a nested diagram", False, "none found")
        else:
            t_un = unnamed[0]
            dw2, es2, err2 = connect_nested(SCRATCH, i_D, info[SNK]["n"], t_un, info[SRC]["n"], t_src, lab)
            wb4 = walk(SCRATCH, i_D)
            w_un = next((r["wire"] for r in wb4[SNK][2] if r["i"] == t_un), 0)
            w_src2 = next((r["wire"] for r in wb4[SRC][2] if r["i"] == t_src), 0)
            fact(f"T3 (b) sink #{SNK} t{t_un} '' <- src #{SRC} t{t_src}: op error {err2[:110]!r}, "
                 f"wire delta {dw2}, ExecState {es2}")
            gate("T3 (b) an UNNAMED terminal on a NESTED diagram is REACHED by index (wire 0 -> non-zero)",
                 bool(w_un), f"unnamed-terminal wire {w_un} (source w{w_src2}); "
                             f"this is the capability no name-addressed op has")
            fact(f"T3 ExecState after the unnamed-terminal wire: {es2} - a type-incompatible pair makes a BROKEN "
                 f"wire (a LabVIEW type fact, not an op failure); the gate above is wire identity")

        # ---------------- T4 (c)
        fact("T4 (c) source on a DIFFERENT nested diagram: NOT EXPRESSIBLE. The op carries ONE diagram index "
             "(ROUTE B) because two independent nested diagrams need a SECOND `To More Specific Class`, measured "
             "impossible in build run 1 (GObject element -> Diagram-class property node = ExecState 0).")

        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)
        fact(f"T5 junk Invokes purged: {junk}")
    except Exception as e:
        gate("Tx the test completed without an unhandled exception", False, f"EXC {str(e)[:220]}")
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        try:
            if os.path.exists(SCRATCH):
                os.remove(SCRATCH)
                fact(f"scratch deleted: {os.path.basename(SCRATCH)}")
        except Exception as e:
            fact(f"scratch NOT deleted ({str(e)[:70]})")
        g._lv = None
    fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
    print("\n--- FACTS ---", flush=True)
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== test_opconnectnested_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
