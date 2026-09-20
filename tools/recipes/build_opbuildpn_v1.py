"""build_opbuildpn_v1.py - OpBuildPN_v1: the property-node builder that can no longer fail silently.

THE DEFECT, read from a file copy of OpBuildPN_v0 on 2026-09-14 (tools/bench/read_opbuildpn_panel.log): the
erdosmiller creator subVI (uid 297) has its `error out` and `Outputs` terminals UNWIRED. The op's panel `error out`
comes from elsewhere. So when a property ID is not supported for the class, the creator's error (1077 per peer
review) is dropped and the op returns a Property node with ZERO rows that is indistinguishable from success by
every count-based check. That is the mechanism behind three "did it attach?" probes that could not decide, and
behind `Control.Value` (2026-09-12) and `VI:Get Errors` (09-09, 09-14) being recorded as mysteries.

THE CHANGE (v1 is built from a COPY; v0 stays as-is and in use until v1 is verified):
    creator.'error out'  ->  new indicator  (label read back, expected 'error out N' or similar)
    creator.'Outputs'    ->  new indicator  (the new node's output terminal refnums; if refnum arrays read badly
                                             over ActiveX the fallback is Array Size -> integer indicator)
Both via Terminal.Create Indicator on the creator's terminals - the ONLY front-panel creation this fleet can do,
and it lets LabVIEW pick the datatype.

VERIFICATION, in this file, with a CONTROL and a KNOWN-BAD case on one scratch target:
    GObject.Position 632A800    -> creator error none, Outputs length 1          (must pass or the run is INVALID)
    bogus ID 'FFFFFFF'          -> creator error non-zero, Outputs length 0      (must FAIL LOUDLY, that is the point)
    Control.Terminal 6332006    -> classified by the same two readings
    AbstractDiagram.SubVIs[] 6375802 -> classified by the same two readings
Peer review of this plan: archive/peer/2026-09-14-opbuildpn-v1-plan.md - the recipe is not run until it lands.

  py tools/bgrun.py --max-min 15 --log tools/bench/build_opbuildpn_v1.log -- py -u tools/recipes/build_opbuildpn_v1.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpBuildPN_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpBuildPN_v1.vi")
TGT_SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
TGT = os.path.join(g.CLAUDEDEV, "SCRATCH_buildpn_v1_target.vi")
CREATOR_UID = 297
g._run.__defaults__ = (6.0, 120.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   OBSERVED: {obs}", flush=True)
        return obs
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:240]}", flush=True)
        return None


def node_index(uid):
    """The creator's index in AbstractDiagram.Nodes[] - the space create_indicator addresses.

    Run 1 passed its index within a class-filtered 'SubVI' traversal (0) instead; Nodes[] index 0 is the Open VI
    Reference node, so terminals 10 and 8 were out of range and nothing was created (build_opbuildpn_v1.log,
    2026-09-14). net_map iterates Nodes[] by index and reports the uid at each index, so its key IS that index.
    """
    nodes, _w = g.net_map(OP, 0, max_nodes=40, max_terms=30)
    for i, (u, _l, _terms) in nodes.items():
        if u == uid:
            return i
    raise RuntimeError(f"uid {uid} not found in Nodes[] walk")


def terminal_index(uid, name):
    nodes, _w = g.net_map(OP, 0, max_nodes=40, max_terms=30)
    for _i, (u, _l, terms) in nodes.items():
        if u == uid:
            for ti, t, _w2 in terms:
                if t == name:
                    return ti
    return None


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def main():
    g._lv = None
    for p in (OP, TGT):
        try:
            g.close_panel(p)
            time.sleep(0.3)
        except Exception:
            pass
        if os.path.exists(p):
            os.remove(p)
    shutil.copyfile(SRC, OP)
    g.open_panel(OP)
    time.sleep(1.0)
    print(f"start: ExecState {g.exec_state(OP)}, indicators {inds()}", flush=True)
    ci = node_index(CREATOR_UID)
    t_err = terminal_index(CREATOR_UID, "error out")
    t_out = terminal_index(CREATOR_UID, "Outputs")
    print(f"creator SubVI index {ci}; terminal indices: error out={t_err}, Outputs={t_out}", flush=True)
    if t_err is None or t_out is None:
        print("STOP: creator terminals not found by name. Nothing saved.", flush=True)
        return 2
    # Peer (archive/peer/2026-09-14-opbuildpn-v1-fail1.md): assert the address BEFORE invoking - run 1 addressed
    # Nodes[0] (Open VI Reference, 8 terminals) with terminal indices 10 and 8, which are out of range there.
    nodes, _w = g.net_map(OP, 0, max_nodes=40, max_terms=30)
    n_terms = len([t for _ti, t, _w2 in nodes[ci][2]])
    print(f"Nodes[{ci}] is uid {nodes[ci][0]} with {n_terms} terminals; need indices {t_err}, {t_out} < {n_terms}",
          flush=True)
    if nodes[ci][0] != CREATOR_UID or max(t_err, t_out) >= n_terms:
        print("STOP: address check failed - refusing to invoke Create Indicator on the wrong node/terminal.", flush=True)
        return 2

    # Run 2 (build_opbuildpn_v1b.log): both indicators were created and wired, yet ExecState went 1 -> 0.
    # So this run records ExecState and the Wire count after EACH creation, to see which of the two breaks
    # the VI, and - if broken at the end - runs Remove Bad Wires as a discriminator on the UNSAVED copy: if
    # ExecState returns to 1 and the wire count drops, the created wire itself was illegal (type/terminal),
    # not a side effect. Peer review of the anomaly: archive/peer/2026-09-14-opbuildpn-v1-fail2.md.
    w0 = g.count(OP, "Wire")
    before = set(inds())
    new_err = step("1 Create Indicator on creator.'error out'", "ControlTerminal +1, Wire +1, ExecState stays 1",
                   lambda: g.create_indicator(OP, ci, t_err))
    err_lab = [l for l in inds() if l not in before]
    es1, w1 = g.exec_state(OP), g.count(OP, "Wire")
    print(f"   new indicator label(s): {err_lab}; ExecState {es1}; Wire {w0}->{w1}", flush=True)
    before = set(inds())
    new_out = step("2 Create Indicator on creator.'Outputs'", "ControlTerminal +1, Wire +1, ExecState stays 1",
                   lambda: g.create_indicator(OP, ci, t_out))
    out_lab = [l for l in inds() if l not in before]
    es2, w2 = g.exec_state(OP), g.count(OP, "Wire")
    print(f"   new indicator label(s): {out_lab}; ExecState {es2}; Wire {w1}->{w2}", flush=True)

    es = g.exec_state(OP)
    print(f"\nassembled: ExecState {es}, indicators now {inds()}", flush=True)
    if es != 1:
        g.remove_bad_wires_scripted(OP)
        es_r, w_r = g.exec_state(OP), g.count(OP, "Wire")
        print(f"   DIAGNOSTIC Remove Bad Wires on the unsaved copy: ExecState {es}->{es_r}, Wire {w2}->{w_r} "
              f"({'a created wire was ILLEGAL' if (es_r == 1 and w_r < w2) else 'not a bad-wire problem'})",
              flush=True)
    # PHASE B (peer, opbuildpn-v1-fail2): the creator has TWO terminals named 'error out' (indices 10 and 12);
    # one may be a SINK, and an indicator on a sink breaks the caller. If phase A (index 10) broke the VI,
    # retry on a FRESH copy with index 12 - a measurement of which terminal is the real source, not a guess.
    if es != 1 and es1 != 1:
        t_err2 = None
        nodes, _w = g.net_map(OP, 0, max_nodes=40, max_terms=30)
        for ti, t, _w2 in nodes[ci][2]:
            if t == "error out" and ti != t_err:
                t_err2 = ti
        print(f"\n== PHASE B: index {t_err} broke the VI; retry on a fresh copy with the other 'error out' "
              f"(index {t_err2})", flush=True)
        if t_err2 is not None:
            g.close_panel(OP)
            time.sleep(0.4)
            os.remove(OP)
            shutil.copyfile(SRC, OP)
            g.open_panel(OP)
            time.sleep(1.0)
            w0 = g.count(OP, "Wire")
            before = set(inds())
            new_err = step(f"B1 Create Indicator on creator terminal {t_err2} ('error out' #2)",
                           "ExecState stays 1 if THIS is the real source", lambda: g.create_indicator(OP, ci, t_err2))
            err_lab = [l for l in inds() if l not in before]
            es1, w1 = g.exec_state(OP), g.count(OP, "Wire")
            print(f"   label(s) {err_lab}; ExecState {es1}; Wire {w0}->{w1}", flush=True)
            before = set(inds())
            new_out = step("B2 Create Indicator on creator.'Outputs'", "ExecState stays 1",
                           lambda: g.create_indicator(OP, ci, t_out))
            out_lab = [l for l in inds() if l not in before]
            es2, w2 = g.exec_state(OP), g.count(OP, "Wire")
            print(f"   label(s) {out_lab}; ExecState {es2}; Wire {w1}->{w2}", flush=True)
            es = g.exec_state(OP)
            print(f"   phase B assembled: ExecState {es}", flush=True)

    if es != 1 or not new_err or not new_out or not err_lab or not out_lab:
        print("VERDICT: not clean - NOT SAVING (v0 untouched).", flush=True)
        return 3
    g.save(OP)
    print("saved OpBuildPN_v1", flush=True)
    ERR_LABEL, OUT_LABEL = err_lab[-1], out_lab[-1]

    # ---- verification on a scratch target through the NEW op --------------------------------
    shutil.copyfile(TGT_SRC, TGT)
    g.open_panel(TGT)
    time.sleep(0.9)
    vi = g.op(OP)
    cases = [("CONTROL GObject.Position 632A800", "VI Server:GObject", "632A800", "pass"),
             ("KNOWN-BAD bogus id FFFFFFF", "VI Server:GObject", "FFFFFFF", "fail"),
             ("Control.Terminal 6332006", "VI Server:Control", "6332006", "?"),
             ("AbstractDiagram.SubVIs[] 6375802", "VI Server:AbstractDiagram", "6375802", "?")]
    rows = []
    y = 400
    for label, cls, pid, expect in cases:
        # Peer change 5: a FRESH scratch target per case, so a failed/default node from one case cannot
        # contaminate the next reading.
        try:
            g.close_panel(TGT)
            time.sleep(0.3)
            os.remove(TGT)
        except Exception:
            pass
        shutil.copyfile(TGT_SRC, TGT)
        g.open_panel(TGT)
        time.sleep(0.8)
        vi.SetControlValue("vi path", TGT)
        vi.SetControlValue("Class Name", "Diagram")
        vi.SetControlValue("index", 0)
        vi.SetControlValue("location (0, 0)", [1300, y])
        y += 110
        vi.SetControlValue("Class Name 3", cls)
        vi.SetControlValue("Properties", g.cluster_array([(pid, False)]))
        try:
            g._run(vi)
        except RuntimeError as e:
            if "modal dialog" not in str(e):
                raise
        try:
            err = tuple(vi.GetControlValue(ERR_LABEL))
        except Exception as e:
            err = ("<unreadable>", str(e)[:40], "")
        try:
            outs = vi.GetControlValue(OUT_LABEL)
            n_out = len(outs) if isinstance(outs, (tuple, list)) else f"<{type(outs).__name__}>"
        except Exception as e:
            n_out = f"<unreadable {str(e)[:40]}>"
        print(f"   {label:40} creator error={err}  Outputs len={n_out}   (expected: {expect})", flush=True)
        rows.append((label, err, n_out, expect))

    # Peer contract (archive/peer/2026-09-14-opbuildpn-v1-plan.md): the creator's error STATUS is the primary
    # verdict; the output count only corroborates a clean error; the bad case must show status TRUE but its
    # code is RECORDED, not asserted (1077 is plausible, not guaranteed); count may be 1 even on failure.
    ctl_ok = (rows[0][1][0] is False) and rows[0][2] == 1
    bad_ok = (rows[1][1][0] is True)
    print(f"\nknown-bad creator error code/source recorded: {rows[1][1][1:]}", flush=True)
    print("VERDICT:", flush=True)
    if ctl_ok and bad_ok:
        print("  v1 DISCRIMINATES: control clean with count 1, known-bad raises. Rows 3-4 are real readings.", flush=True)
        for label, err, n_out, _e in rows[2:]:
            if err[0] is True:
                v = f"REJECTED by creator (error {err[1]}: {str(err[2])[:60]})"
            elif n_out == 1:
                v = "ATTACHED (clean error, count 1)"
            else:
                v = f"INCONSISTENT (clean error, count {n_out}) - raise, do not trust"
            print(f"    {label:40} -> {v}", flush=True)
    else:
        print("  INVALID as a discriminator (control or known-bad did not behave) - rows 3-4 mean nothing.", flush=True)
    try:
        g.close_panel(TGT)
        time.sleep(0.3)
        os.remove(TGT)
        print("scratch target deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if (ctl_ok and bad_ok) else 4


if __name__ == "__main__":
    sys.exit(main())
