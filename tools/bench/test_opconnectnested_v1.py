r"""test_opconnectnested_v1.py - the DISCRIMINATING test of `OpConnectNested_v0.vi`, written to the peer's
prescription in `archive/peer/2026-09-17-connectnested-t2b.md` (codex, ANSWERED, accepted whole).

    MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/test_opconnectnested_v1.log \
        -- py -u tools/bench/test_opconnectnested_v1.py

WHY v1 EXISTS. v0 proved the op REACHES the terminals it is given (same wire uid on both ends, including an
UNNAMED terminal on a nested diagram) but its `ExecState 1` gate was INVALID, and the peer named three reasons -
all of them mine, none of them the op's:
  (i)   the pair was type-incompatible (`error out` into a `path` input);
  (ii)  a freshly created While loop has an UNWIRED CONDITIONAL TERMINAL, which is a broken VI by itself
        (`tools/recipes/build_opstopfromnode_v0.py:438-441`, which scores ExecState as a TRANSITION for exactly
        this reason);
  (iii) `Error Cluster From Error Code.vi` has a REQUIRED `error code` input that the scratch left unwired - a
        required terminal with no wire is a broken VI independently of (i) and (ii). I had not listed this one.
And the peer's headline: `Terminal.Connect Wire` behaves like the wiring tool - *"the wire will be there"* even
when it is broken - so wire identity proves GRAPH MUTATION, never a compilable connection. The v0 label
"functionally verified" is withdrawn.

THE TEST, verbatim from the peer's "cheapest discriminating test":
  begin from a nested scratch that ALREADY reads ExecState 1 (While condition wired, every required input
  satisfied); record that the target sink has NO wire; invoke `OpConnectNested_v0` ONCE with a KNOWN
  TYPE-COMPATIBLE source and sink; then require all THREE postconditions together.

PREDICTION CONTRACT (stop at the first miss; this file saves nothing, ever):
 V0  `OpConnectNested_v0.vi` present, ExecState 1, labels say route "B".
 V1  scratch = copy of EMPTY_v0 (unique name, DELETED in the same run) + one While loop; two subVIs INSIDE the
     body: `Error Cluster From Error Code.vi` (owns `error out`) and `Is Path and Not Empty.vi`.
 V2  EVERY required/bare NAMED input of both body nodes gets a literal with `OpCreateConstOnTerm_v0` (22/0,
     toolkit row) - this is cause (iii) removed.
 V3  the While loop's conditional terminal is driven from the Boolean body output with `OpStopFromNode_v0`
     (measured wire 0 -> 387, ExecState 1, toolkit row) - this is cause (ii) removed.
 V4  ⚠️ THE PRECONDITION GATE: the scratch reads **ExecState 1 BEFORE the op under test runs**. If it does not,
     the run STOPS and reports which cause survived - it does NOT proceed to a gate it already knows is invalid.
 V5  the chosen SINK terminal is recorded as UNWIRED immediately before the call (the peer's missing assertion -
     without it "wire delta 0" cannot distinguish a branch from a no-op).
 V6  ONE call to `OpConnectNested_v0`, TYPE-COMPATIBLE: source = `error out` (error cluster) -> sink = the body
     node's error-cluster input on the SAME nested diagram. Then all three postconditions:
       V6a the sink and the source carry the SAME wire uid;
       V6b the sink went UNWIRED -> WIRED;
       V6c `ExecState` is STILL 1  <- the one v0 could not ask. This is what turns "a wire is present" into
           "a compilable wire", and it is the gate that lets D1 depend on this op.
 V7  scratch deleted; junk Invokes purged; handles before/after.
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
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
sys.path.insert(0, HERE)
import gscript as g                       # noqa: E402
from bench_prep import labview_handles     # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpConnectNested_v0.vi")
OP_CONST = os.path.join(g.CLAUDEDEV, "OpCreateConstOnTerm_v0.vi")
OP_STOP = os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
LABELS = os.path.join(HERE, "opconnectnested_labels.json")
CONST_LABELS = os.path.join(HERE, "opcreateconstonterm_labels.json")
STOP_LABELS = os.path.join(HERE, "opstopfromnode_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_cn1_{STAMP}.vi")
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
    faulthandler.dump_traceback_later(150, repeat=True, exit=False)
    g._lv = None
    t0 = time.time()
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0}")
    try:
        for p in (OP, OP_CONST, OP_STOP, EMPTY):
            if not gate(f"V0 {os.path.basename(p)} on disk", os.path.exists(p), p):
                return 1
        with open(LABELS, encoding="utf-8") as f:
            lab = json.load(f)
        with open(CONST_LABELS, encoding="utf-8") as f:
            clab = json.load(f)
        with open(STOP_LABELS, encoding="utf-8") as f:
            slab = json.load(f)
        from build_opcreateconstonterm_v0 import create_const_on_term

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
        if not gate("V1 one While loop created", len(nwl) == 1 and len(ndg) == 1, f"{nwl} {ndg}"):
            return 1
        W, D = nwl[0]["uid"], ndg[0]["uid"]
        i_D = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")].index(D)
        loop_i = [o["uid"] for o in g.report_all(SCRATCH, "WhileLoop")].index(W)
        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, i_D, (60, 60))
        g.drop_subvi(SCRATCH, BOOLVI, i_D, (60, 260))
        nsv = g.new_since(SCRATCH, "SubVI", sv0)
        if not gate("V1b two body nodes inside the loop body", len(nsv) == 2, f"{nsv}"):
            return 1
        wb = walk(SCRATCH, i_D)
        SRC = next((o["uid"] for o in nsv
                    if any(r["is_source"] and r["name"] == "error out" for r in wb[o["uid"]][2])), None)
        SNK = next((o["uid"] for o in nsv if o["uid"] != SRC), None)
        for u in (SRC, SNK):
            n_i, l, rows = wb[u]
            fact(f"body #{u} Nodes[{n_i}] {l!r}: "
                 f"outs {[(r['i'], r['name']) for r in rows if r['is_source']]}; "
                 f"bare ins {[(r['i'], r['name']) for r in rows if not r['is_source'] and r['wire'] == 0]}")

        # ---- V2: satisfy EVERY bare NAMED input of both body nodes (the peer's cause (iii))
        print("\n=== V2: literals on every bare NAMED input (OpCreateConstOnTerm_v0)", flush=True)
        placed, refused = [], []
        for u in (SRC, SNK):
            while True:
                wnow = walk(SCRATCH, i_D)
                n_i, _l, rows = wnow[u]
                nxt = next(((r["i"], r["name"]) for r in rows
                            if not r["is_source"] and r["wire"] == 0 and r["name"]
                            and r["name"] not in ("error in (no error)",)
                            and (u, r["i"]) not in [(a, b) for a, b, _c in placed + refused]), None)
                if nxt is None:
                    break
                t_i, t_nm = nxt
                res = create_const_on_term(SCRATCH, loop_i, n_i, t_i, clab, value=0)
                wnow = walk(SCRATCH, i_D)
                got = next((r["wire"] for r in wnow[u][2] if r["i"] == t_i), 0)
                (placed if got else refused).append((u, t_i, f"{t_nm!r} -> wire {got} "
                                                             f"{res.get('inv_err', '')[:50]}"))
                print(f"   #{u} t{t_i} {t_nm!r}: wire {got}", flush=True)
        fact(f"V2 literals placed {len(placed)}, refused {len(refused)}: "
             f"placed {[(a, b) for a, b, _c in placed]}; refused {refused}")

        # ---- V3: drive the loop's conditional terminal from the Boolean output (the peer's cause (ii))
        print("\n=== V3: the loop's conditional terminal, from the body Boolean (OpStopFromNode_v0)", flush=True)
        wnow = walk(SCRATCH, i_D)
        bool_u = next((u for u in (SRC, SNK)
                       if any(r["is_source"] and r["name"] and "?" in r["name"] for r in wnow[u][2])), None)
        if bool_u:
            n_b = wnow[bool_u][0]
            t_b = next(r["i"] for r in wnow[bool_u][2] if r["is_source"] and r["name"] and "?" in r["name"])
            vs = g.op(OP_STOP)
            vs.SetControlValue("vi path", SCRATCH)
            vs.SetControlValue("Class Name", "WhileLoop")
            vs.SetControlValue("index", int(loop_i))
            vs.SetControlValue(slab["index_node"], int(n_b))
            vs.SetControlValue(slab["index_term"], int(t_b))
            g._run(vs)
            fact(f"V3 OpStopFromNode_v0 on #{bool_u} Nodes[{n_b}] t{t_b}: "
                 f"error out {(g._err(vs, 'error out') or '')[:110]!r}")
        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)

        # ---- V4: THE PRECONDITION GATE
        es_pre = g.exec_state(SCRATCH)
        if not gate("V4 PRECONDITION: the scratch reads ExecState 1 BEFORE the op under test runs", es_pre == 1,
                    f"ExecState {es_pre} - if 0, one of the peer's three causes survived; the run stops here "
                    f"rather than scoring a gate it already knows is invalid"):
            wnow = walk(SCRATCH, i_D)
            bare = [(u, wnow[u][1], r["i"], r["name"]) for u in wnow for r in wnow[u][2]
                    if not r["is_source"] and r["wire"] == 0]
            fact(f"V4 BARE-TERMINAL CENSUS (the measured cause, not a guess): {bare}")
            return 1

        # ---- V5/V6: the one call, type-compatible, with the pre-call unwired assertion
        wnow = walk(SCRATCH, i_D)
        t_src = next(r["i"] for r in wnow[SRC][2] if r["is_source"] and r["name"] == "error out")
        cand = [r["i"] for r in wnow[SNK][2] if not r["is_source"] and r["wire"] == 0]
        t_sink = next((r["i"] for r in wnow[SNK][2]
                       if not r["is_source"] and r["wire"] == 0 and r["name"] == "error in (no error)"),
                      cand[0] if cand else None)
        if t_sink is None:
            gate("V5 an UNWIRED sink terminal exists on the body node", False, f"rows {wnow[SNK][2]}")
            return 1
        w_before = next(r["wire"] for r in wnow[SNK][2] if r["i"] == t_sink)
        gate("V5 PRE-CALL: the chosen sink terminal is UNWIRED (the assertion v0 lacked)", w_before == 0,
             f"#{SNK} t{t_sink} wire {w_before}")
        dw, es_post, err = connect_nested(SCRATCH, i_D, wnow[SNK][0], t_sink, wnow[SRC][0], t_src, lab)
        wafter = walk(SCRATCH, i_D)
        w_sink = next(r["wire"] for r in wafter[SNK][2] if r["i"] == t_sink)
        w_src = next(r["wire"] for r in wafter[SRC][2] if r["i"] == t_src)
        fact(f"V6 ONE call: sink #{SNK} t{t_sink} <- src #{SRC} t{t_src} 'error out' (error cluster -> error "
             f"cluster): op error {err[:110]!r}, wire delta {dw}, ExecState {es_pre} -> {es_post}")
        gate("V6a the sink and the source carry the SAME wire uid", bool(w_sink) and w_sink == w_src,
             f"sink w{w_sink} / source w{w_src}")
        gate("V6b the sink went UNWIRED -> WIRED", w_before == 0 and bool(w_sink), f"0 -> {w_sink}")
        gate("V6c THE DISCRIMINATOR: ExecState is STILL 1 - the op creates a COMPILABLE wire, not merely a "
             "present one", es_post == 1, f"ExecState {es_pre} -> {es_post}")

        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)
        fact(f"V7 junk Invokes purged: {junk}")
    except Exception as e:
        gate("Vx the test completed without an unhandled exception", False, f"EXC {str(e)[:220]}")
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
    print(f"\n=== test_opconnectnested_v1: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
