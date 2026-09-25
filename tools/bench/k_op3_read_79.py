r"""k_op3_read_79 - card 79-7 M1 (Pre-decided 178(h)): the HEADLESS READ the hypothesis review
archive/peer/2026-09-25-c79-6-k_e1op3.md asks for. FRESH LabVIEW (Stage.start restarts it - standing authority; this also
retires the stale pid 23284 left by 79-6) -> dated scratch copy of the S4 bed claudeDev\D1_s4_loop17.vi -> replay the FIRST
THREE compiled ops of plan_k_split.json with the SAME stagexec Executor + LVBackend stage_d1_k.py uses (op 3 = move_in #5058
is expected to raise the E1 step-diff exactly as in stage_d1_k.log:97 - caught, not a failure here) -> one live read ->
dump every real terminal row to k_op3_read_79.json (the M2 fixture) and print the rows of 2789/2792/5910/6253/2811/5124 and
every row on wires 505/3472/2924. NOTHING IS SAVED; the scratch is deleted at close. No VI run, no motor/ASI/camera.
PRIOR ART: tools/recipes/stage_d1_k.py (Executor/LVBackend wiring), stagekit.Stage/discard_work (scratch diagnostic
shape), stagexec.compare/edges (the E1 diff). No new op.
PREDICTION CONTRACT (the review's discriminator, section 3):
  R1 read OK and all 5 named terminals present in the real rows;
  tunnel-flip  <=> wire_uid(2789)=3472, wire_uid(2792)=2924 (non-zero) AND is_source False on 2789 and 2792;
  whole-wire loss <=> wire_uid 0 on 2789/2792/5910/6253; renumbering <=> non-zero but different uids on each pair's ends.
  Which of the three holds is RECORDED as a FACT, not gated (the read is the truth, M2 fits the model to it).
    MATERIAL=1 py tools/bgrun.py --material --max-min 25 --log tools/bench/k_op3_read_79.log -- py -u tools/bench/k_op3_read_79.py"""
import json, os, sys                                                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K, stagesim as SS, stagexec as SX                               # noqa: E401,E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
PLAN = os.path.join(K.BENCH, "plan_k_split.json")
P = J(PLAN); BASE = J(K.ROOT, P["finalized"]["base"]["path"]); WIKI = J(K.ROOT, P["context"]["fs_pairs_wiki"]["path"])  # noqa: E702
TERMS = (2789, 2792, 5910, 6253, 2811, 5124)
WIRES = (505, 3472, 2924)
OUT = os.path.join(K.BENCH, "k_op3_read_79.json")
N_OPS = 3


def row_s(r):
    return "term {0} owner #{1} {2}/{3} {4!r} is_source={5} wire={6}".format(
        r.get("term_uid"), r.get("owner_uid"), r.get("owner_class"), r.get("term_class"), r.get("term_name"),
        r.get("is_source"), r.get("wire_uid"))


def body(s):
    print(__doc__, flush=True)
    s.start(); s.discard_work(); bp = K.mod("bench_prep")                          # noqa: E702
    s.fact("HANDLES after open {0!r}".format(bp.labview_handles()))
    be = SX.LVBackend(s, WIKI["fs_tunnel_pairs"])
    ex = SX.Executor(PLAN, be, log=lambda m: print(m, flush=True))
    s.fact("COMPILED first {0} of {1} ops: {2}".format(N_OPS, len(ex.ops), [(o["kind"], o["acts"]) for o in ex.ops[:N_OPS]]))
    ex.ops = ex.ops[:N_OPS]
    stop = None
    try:
        ex.run()
    except SX.ExecStop as e:
        stop = str(e)
    s.fact("REPLAY ops 1-{0} ended: {1}".format(N_OPS, stop[:600] if stop else "no step-diff"))
    real = SX.dedupe(be.read())
    k3 = ex.ops[N_OPS - 1]["acts"][-1]
    sim = ex.step(k3)["state"]["terminals"]
    d = SX.compare(sim, real, ex.bind, ex.allow)
    s.fact("COMPARE sim step {0} vs real: {1}".format(k3, json.dumps({x: y for x, y in d.items() if y}, default=str)[:1500]))
    by = dict((r["term_uid"], r) for r in real)
    for t in TERMS:
        s.fact("READ " + (row_s(by[t]) if t in by else "term {0} ABSENT".format(t)))
    for w in WIRES:
        rows = [r for r in real if r.get("wire_uid") == w]
        s.fact("WIRE {0}: {1} row(s) (sources {2}, sinks {3})".format(w, len(rows), sum(1 for r in rows if r["is_source"]),
                                                                        sum(1 for r in rows if not r["is_source"])))
        for r in rows:
            s.fact("    " + row_s(r))
    for u in (2765, 5058):
        for r in [x for x in real if x.get("owner_uid") == u]:
            s.fact("OWNER #{0} ".format(u) + row_s(r))
    s.gate("R1 live read after op {0} holds all {1} named terminals".format(N_OPS, len(TERMS)), all(t in by for t in TERMS),
           [t for t in TERMS if t not in by])
    w = lambda t: (by.get(t) or {}).get("wire_uid")                               # noqa: E731
    src = lambda t: (by.get(t) or {}).get("is_source")                             # noqa: E731
    flip = w(2789) == 3472 and w(2792) == 2924 and src(2789) is False and src(2792) is False
    loss = all(not w(t) for t in (2789, 2792, 5910, 6253))
    renum = not loss and (w(2789) != w(6253) or w(2792) != w(5910))
    s.fact("VERDICT tunnel-flip={0} whole-wire-loss={1} renumbered={2} (pairs 2789/6253 {3}/{4}, 2792/5910 {5}/{6})".format(
        flip, loss, renum, w(2789), w(6253), w(2792), w(5910)))
    json.dump({"schema": "k_op3_read/1", "plan": os.path.relpath(PLAN, K.ROOT), "plan_md5": K.md5(PLAN), "sim_step": k3,
               "bed_md5": s.input_md5, "stop": stop, "compare": d, "terminals": real,
               "verdict": {"tunnel_flip": flip, "whole_wire_loss": loss, "renumbered": renum}},
              open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    s.gate("R2 fixture written {0}".format(os.path.basename(OUT)), os.path.isfile(OUT), K.md5(OUT))
    s.fact("HANDLES at end of work {0!r}".format(bp.labview_handles()))


if __name__ == "__main__":
    st = K.Stage(BASE["vi"], BASE["md5"], "D1_k_read79", preload=False, deadline_min=22,
                 out_json=os.path.join(K.BENCH, "k_op3_read_79_stage.json"))
    sys.exit(K.run(body, st))
