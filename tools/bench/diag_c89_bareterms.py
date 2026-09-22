r"""diag_c89_bareterms - THE POSITIVE CONTROL FOR THE `ExecState` READER + FOUR CENSUS READS. READ-ONLY.

PREDICTION CONTRACT (the brief's). ONLY C1 IS A GATE; C2-C5 ARE CENSUS READS REPORTED AS VALUES.
  C1  POSITIVE CONTROL - the only pass/fail gate in this file. On a dated scratch COPY of
      `claudeDev\OpFsInnerTunnelConnect_v1.vi` (md5 5b4e5f0f...): `ExecState` reads 1; ONE scripted
      wire delete that bares a required input is then made; `ExecState` re-read IN THE SAME RUN
      THROUGH `gscript.exec_state` - the same code path diag_c89_execstate_factorial used - must read 0.
      1 -> 0 = the reader responds to a scripted mutation. Anything else means the factorial's four
      zeros are UNINFORMATIVE, and that is reported plainly, not repaired.
  C2  every `WhileLoop` on the bed: its conditional terminal uid and whether it carries a wire (VALUES).
  C3  `WhileLoop #23032`'s body diagram: every node, every terminal (index/name/is_source/wire); the
      BARE non-source terminals named (VALUES).
  C4  the same for `#10407` and `Global #7202`, and for every node on that body diagram (VALUES).
  C5  the owner of `Diagram #639`, with a uid echo (VALUE).

NOTHING IS BUILT, NOTHING IS SAVED, NO OP IS CREATED. The bed is NEVER mutated - C2-C5 are property
reads on the dated work COPY; the ONLY mutation in this file is C1's single wire delete on a scratch
copy of an OP VI, which is deleted in the same run. `THE FILES THIS RUN LEFT ON DISK: []` is gated by
stagekit's H6; the bed's md5 and all five pins are asserted at both ends. NO motor, NO ASI, NO camera.

WHAT ALREADY EXISTS (CLAUDE.md "check what exists first" - grep of tools/, docs/toolkit-capabilities.md)
  * `tools/stagekit.py` - pins, restart+handle counts, preload, scratch, `es`, `wired_terminals`, hygiene.
  * `tools/recipes/build_d1_v0.py` - `loop_end_ref` (:820, OpLoopEndRef_v0, THE conditional-terminal
    reader, 16/16 on the main VI per docs/toolkit-capabilities.md:62), `owner_of` (:338, strict uid
    echo), `diag_index` (:357), `wmap` (:364), `bare_named_sinks` (:482). NOTHING NEW IS WRITTEN.
  * `tools/recipes/build_opfsinnertunnelconnect_v0.del_wire` (:336) - the uid-addressed wire delete.
  * `tools/recipes/build_d1_m3a1.node_view` (:572) - uid -> node across diagrams, with `uid_echo`.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

BED = os.path.join(K.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_MD5 = "0b84595245dd650c0e8fd3f57104782c"
PC_VI = os.path.join(K.CLAUDEDEV, "OpFsInnerTunnelConnect_v1.vi")
PC_MD5 = "5b4e5f0fb3baae96361c33ce81bcd7b1"
LOOPS = (23041, 10170, 23032, 25380, 637, 15173)
BODY, NEWLOOP, D639 = 23058, 23032, 639
ASK_NODES = (10407, 7202)


def terms_table(s, p, di, tag):
    """Every node on diagram index `di` with every terminal. Returns the BARE non-source rows."""
    V = K.mod("build_d1_v0")
    wm, _e = s.safe("{0} wmap(diagram_index={1})".format(tag, di), lambda: V.wmap(p, di, fresh=True), {})
    bare = []
    for uid, rec in sorted((wm or {}).items()):
        n_i, label, rows = rec
        s.fact("{0} NODE #{1} (Nodes[{2}]) label {3!r}: {4} terminal(s)".format(tag, uid, n_i, label, len(rows)))
        for r in rows:
            s.fact("{0}   #{1} t{2:<3} name={3!r} is_source={4} wire={5}".format(
                tag, uid, r["i"], r["name"], r["is_source"], r["wire"]))
            if not r["is_source"] and not r["wire"]:
                bare.append((uid, r["i"], r["name"], label))
    s.fact("{0} BARE INPUT TERMINALS ({1}): {2!r}".format(tag, len(bare), bare))
    return bare


def c1_positive_control(s):
    s.head("[C1] POSITIVE CONTROL - does `ExecState` respond to a scripted mutation IN THE SAME RUN?")
    C82 = K.mod("build_opfsinnertunnelconnect_v0")
    s.file_facts("C1 source", PC_VI)
    s.gate("C1a the positive-control source's md5 is {0}".format(PC_MD5), K.md5(PC_VI) == PC_MD5,
           K.md5(PC_VI))
    pc = s.scratch("pc", source=PC_VI)
    before = s.es("C1 before any mutation", target=pc)
    s.gate("C1b the untouched positive-control scratch reads ExecState 1", before == 1,
           "observed {0!r}".format(before))
    V = K.mod("build_d1_v0")
    wm, _e = s.safe("C1 wmap(diagram 0)", lambda: V.wmap(pc, 0, fresh=True), {})
    cands = [(u, r["i"], r["name"], r["wire"]) for u, rec in sorted((wm or {}).items())
             for r in rec[2] if (not r["is_source"]) and r["wire"]]
    s.fact("C1 wired INPUT terminals on diagram 0 of the scratch: {0} ; first 8 {1!r}".format(
        len(cands), cands[:8]))
    after, t_gap, second = None, None, None
    for uid, ti, name, w in cands[:8]:
        s.fact("C1 DELETING the wire feeding #{0} t{1} ({2!r}): wire {3}".format(uid, ti, name, w))
        _r, err = s.safe("C1 del_wire w{0}".format(w), lambda ww=w: C82.del_wire(pc, ww, "C1 "))
        t_mut = time.time()
        after = s.es("C1 after deleting w{0}".format(w), target=pc)
        t_gap = time.time() - t_mut
        s.fact("C1 the ExecState read happened {0:.2f} s after the mutation returned (err {1!r})".format(
            t_gap, err))
        if after == 0:
            break
    time.sleep(6.0)
    second = s.es("C1 SECOND read, ~6 s later", target=pc)
    s.row("C1 ExecState before / after / 6 s later", [before, after, second], [1, 0, 0])
    s.gate("C1c ExecState went 1 -> 0 on a scripted wire delete, read through the SAME code path the "
           "factorial used (if this FAILS the four zeros of diag_c89_execstate_factorial are UNINFORMATIVE)",
           before == 1 and after == 0, "before {0!r} after {1!r} second {2!r}".format(before, after, second))
    s.gate("C1d the second read agrees with the first (no lazy recompile between them)", after == second,
           "{0!r} vs {1!r}".format(after, second))
    s.drop_scratch(pc, "H4 C1")


def main(s):
    s.start()
    s.discard_work()
    V = K.mod("build_d1_v0")
    p = s.work
    c1_positive_control(s)

    s.head("[C2] CONDITIONAL-TERMINAL CENSUS - every WhileLoop on the bed (VALUES, not gates)")
    loops = g.report_all(p, "WhileLoop")
    s.fact("C2 WhileLoop census from the machine ({0}): {1!r}".format(
        len(loops), [(L["i"], L["uid"]) for L in loops]))
    s.fact("C2 the briefed list {0!r} vs the machine's: missing {1!r}, extra {2!r}".format(
        list(LOOPS), sorted(set(LOOPS) - {L["uid"] for L in loops}),
        sorted({L["uid"] for L in loops} - set(LOOPS))))
    for L in loops:
        r, e = s.safe("C2 loop_end_ref(index {0})".format(L["i"]), lambda i=L["i"]: V.loop_end_ref(p, i), {})
        r = r or {}
        s.fact("C2 WhileLoop #{0} (index {1}): uid echo {2!r} ({3}) ; COND TERM #{4} ; is_source {5} ; "
               "COND WIRE {6} -> {7} ; err {8!r} errs {9!r} {10}".format(
                   L["uid"], L["i"], r.get("loop_uid"), "ECHO OK" if r.get("loop_uid") == L["uid"] else "ECHO MISMATCH",
                   r.get("cond_term_uid"), r.get("is_source"), r.get("cond_wire_uid"),
                   "WIRED" if r.get("cond_wire_uid") else "BARE - nothing stops this loop",
                   r.get("err"), r.get("errs"), e))

    s.head("[C5] WHO OWNS `Diagram #{0}`? (one read, uid-echoed)".format(D639))
    for u in (D639, BODY):
        (oc, ou), e = s.safe("C5 owner_of(#{0})".format(u), lambda uu=u: V.owner_of(p, uu), (None, None))
        s.fact("C5 Diagram #{0} owner -> {1!r} #{2!r} ; err {3!r}".format(u, oc, ou, e))
    diags = [o["uid"] for o in g.report_all(p, "Diagram")]
    s.fact("C5 Diagram #{0} in the Diagram census: {1} ; #{2}: {3} ; {4} diagram(s) total".format(
        D639, D639 in diags, BODY, BODY in diags, len(diags)))

    if s.left_s() > 150:
        s.head("[C3] BARE-INPUT CENSUS on `WhileLoop #{0}`'s body `Diagram #{1}`".format(NEWLOOP, BODY))
        di, e = s.safe("C3 diag_index(#{0})".format(BODY), lambda: V.diag_index(p, BODY))
        s.fact("C3 Diagram #{0} is Traverse index {1!r} {2}".format(BODY, di, e))
        if di is not None:
            terms_table(s, p, di, "C3")
    else:
        s.fact("C3 SKIPPED - {0:.0f} s left inside the deadline".format(s.left_s()))

    s.head("[C4] THE NAMED NODES - #10407 and Global #7202, wherever they live")
    for u in ASK_NODES:
        if s.left_s() < 90:
            s.fact("C4 #{0} SKIPPED - {1:.0f} s left".format(u, s.left_s()))
            continue
        loc, rows = s.wired_terminals(u, hints=(), tag="C4 #{0}".format(u))
        f = (loc or {}).get("found") or {}
        s.fact("C4 #{0}: uid echo {1!r} ; diagram_uid {2!r} ; Nodes[{3!r}]".format(
            u, (loc or {}).get("uid_echo"), f.get("diagram_uid"), f.get("nodes_index")))
        bare = [(r["i"], r["name"]) for r in rows if not r.get("is_source") and not r.get("wire")]
        for r in rows:
            s.fact("C4   #{0} t{1:<3} name={2!r} is_source={3} wire={4}".format(
                u, r["i"], r.get("name"), r.get("is_source"), r.get("wire")))
        s.fact("C4 #{0} BARE INPUT TERMINALS ({1}): {2!r}".format(u, len(bare), bare))


S = K.Stage(BED, BED_MD5, "diag_c89_bareterms", deadline_min=16.0, reserve_s=210.0,
            out_json=os.path.join(K.BENCH, "diag_c89_bareterms.json"),
            task="positive control for the ExecState reader + conditional-terminal and bare-input census")
sys.exit(K.run(main, S))
