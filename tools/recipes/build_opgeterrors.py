"""build_opgeterrors.py - OpGetErrors_v0.vi: read a VI's ERROR LIST by script (VI method `Get Errors`, ID 0x452, private scope;
labviewwiki + NI forum 2263216, archive/peer/2026-09-08-vi-error-list-by-script.md).  Until now a broken VI (ExecState 0) could
only be bisected blind; this op returns the same items the Ctrl+L window shows.
Built from OpBuildIA_v0 (Open VI Reference -> typed VI wire): delete the creator SubVI, build_invoke("VI Server:VI", "452"),
branch 'vi reference' -> Invoke.reference, indicators on every Invoke output (labels probed), save if ExecState 1.
Test: a scratch VI with a 2-record scripted CLFN (known broken) -> op -> print the outputs.
  py tools/bgrun.py --max-min 15 --log tools/bench/build_opgeterrors.log -- py -u tools/recipes/build_opgeterrors.py
"""
import json, os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpBuildIA_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpGetErrors_v0.vi")
g._run.__defaults__ = (6.0, 60.0)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    inv0 = set(g.uids(OP, "Invoke"))

    def purge():
        for o in g.new_since(OP, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(OP, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(OP, "Invoke", ids.index(o["uid"]))

    subs = g.report(OP, "SubVI"); fns = g.report(OP, "Function")
    ci = next(i for i, o in enumerate(subs) if o["pos"] == (900, 640)); g.delete_object(OP, "SubVI", ci); g.remove_bad_wires_scripted(OP)
    print("creator deleted: ExecState", g.exec_state(OP), flush=True)
    ovr = min(fns, key=lambda o: o["pos"][0])                              # Open VI Reference = leftmost Function
    inv = g.build_invoke(OP, "VI Server:VI", "452", (900, 500))
    if not inv:
        print("STOP: Get Errors invoke not created (private method rejected?)", flush=True); return 3
    ui = inv[0]["uid"]; inv0.add(ui); purge()
    n_inv = g.count(OP, "Node") - 1                                        # created last (junk purged)
    fi = [o["uid"] for o in g.report(OP, "Function")].index(ovr["uid"]); ii = [o["uid"] for o in g.report(OP, "Invoke")].index(ui)
    ok = False
    for term in ("vi reference", "VI reference", "reference"):
        try:
            g.wire(OP, "Function", fi, term, "Invoke", ii, "reference", branch=True); ok = True; print("wired", term, "-> Invoke.reference", flush=True); break
        except Exception as e:
            print("   wire", term, ":", str(e)[:100], flush=True)
    purge(); g.remove_bad_wires_scripted(OP)
    print("after reference wire: ExecState", g.exec_state(OP), flush=True)
    outs = []
    for t in range(0, 8):
        fp0 = {l for _, l, _ in g.fp_labels(OP)}; w0 = g.count(OP, "Wire")
        new = g.create_indicator(OP, n_inv, t); purge(); labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
        if new and labs and g.count(OP, "Wire") > w0:
            outs.append(labs[-1]); print(f"   t{t}: indicator {labs[-1]!r}", flush=True)
        elif new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
    purge(); g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("assembled: ExecState", es, "outputs", outs, flush=True)
    if es != 1 or not outs:
        print("STOP: not saved", flush=True); return 5
    print("saved", g.save(OP), flush=True)
    json.dump({"outputs": outs}, open(os.path.join(os.path.dirname(HERE), "bench", "opgeterrors_labels.json"), "w"), indent=1)
    # test on a known-broken scratch: 2-record scripted CLFN
    import clfn_params as cp
    T = os.path.join(g.CLAUDEDEV, "SCRATCH_geterr.vi")
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(os.path.join(g.CLAUDEDEV, "FPTARGET_v0.vi"), T); g.report(T, "SubVI"); g.open_panel(T); time.sleep(0.8)
    while g.count(T, "Node"):
        try:
            g.delete_object(T, "Node", 0)
        except RuntimeError as e:
            if "expected 1 object gone" not in str(e):
                raise
            break
    g.remove_bad_wires_scripted(T)
    while g.count(T, "ControlTerminal"):
        g.delete_object(T, "ControlTerminal", 0)
    g.remove_bad_wires_scripted(T); tinv0 = g.uids(T, "Invoke")
    g.build_clfn(T, (400, 300), os.path.join(g.CLAUDEDEV, "Debug", "mt_track.dll"), "mt2_track_simple", cp.compose(cp.PARAMS[:2]).hex())
    for o in g.new_since(T, "Invoke", tinv0):
        ids = [x["uid"] for x in g.report(T, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(T, "Invoke", ids.index(o["uid"]))
    g.remove_bad_wires_scripted(T); print("scratch: ExecState", g.exec_state(T), flush=True)
    vi = g.op(OP); vi.SetControlValue("vi path", T); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0)
    try:
        g._run(vi)
    except Exception as e:
        print("op run:", str(e)[:200], flush=True)
    for name in outs + ["error out"]:
        try:
            print(f"{name} = {repr(vi.GetControlValue(name))[:3000]}", flush=True)
        except Exception as e:
            print(name, "EXC", str(e)[:120], flush=True)
    try:
        g.close_panel(T); os.remove(T)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
