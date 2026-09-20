"""build_opmakedefault.py - OpMakeDefault_v0.vi: VI method `Default Values:Make Current Default` (ID 3F3, labviewwiki VI class,
no scripting licence) on the VI at `vi path`. Needed because the ActiveX VirtualInstrument interface has NO MakeCurValsDefault
(probed 2026-09-10: DISP_E_UNKNOWNNAME) and a SetControlValue on a loaded subVI does not reach its call (track_check.log: backend
1 ran the CPU frame). Flow for a script: SetControlValue(vi, ctl, v) -> OpMakeDefault_v0(vi) -> save(vi).

Built from OpWire_v1 exactly like OpFPLabels_v0 (build_opfplabels.py): strip to `vi path -> Open VI Reference`, then
  build_invoke("VI Server:VI", "3F3") <- OpenVIRef.'vi reference'; ExecState 1 -> save.
Test (scratch copy of TRACK_kernel_v1): SetControlValue('index', 1) -> op -> save -> revert -> GetControlValue('index') == 1.
  py tools/bgrun.py --max-min 10 --log tools/bench/build_opmakedefault.log -- py -u tools/recipes/build_opmakedefault.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi"); OP = os.path.join(g.CLAUDEDEV, "OpMakeDefault_v0.vi")
TRACK = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi"); T = os.path.join(g.CLAUDEDEV, "SCRATCH_mkdef.vi")
KEEP = {106}
g._run.__defaults__ = (6.0, 45.0)


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    if os.path.exists(OP):
        try:
            g.close_panel(OP)
        except Exception:
            pass
    shutil.copyfile(SRC, OP); g.open_panel(OP); time.sleep(1.0)

    def strip():
        for cls, uid in (("SubVI", 216), ("SubVI", 262), ("SubVI", 124), ("SubVI", 170),
                         ("Function", 683), ("Function", 788), ("Constant", 755), ("Constant", 834),
                         ("IndexArray", 327), ("IndexArray", 308)):
            try:
                g.delete_object(OP, cls, idx(cls, uid))
            except Exception as e:
                print(f"   delete {cls} {uid}: {str(e)[:80]}", flush=True)
        while True:
            ws = g.report(OP, "Wire")
            d = [i for i, o in enumerate(ws) if o["uid"] not in KEEP]
            if not d:
                break
            g.delete_object(OP, "Wire", d[0])
        return [(o["uid"], o["pos"]) for o in g.report(OP, "Wire")], g.count(OP, "Node"), g.exec_state(OP)
    step("1 strip to `vi path -> Open VI Reference`", "Wires [106]; nodes 1", strip)
    ovr = idx("Function", 43)
    inv = step("2 Invoke VI.Default Values:Make Current Default (3F3)", "+1 Invoke",
               lambda: g.build_invoke(OP, "VI Server:VI", "3F3", (420, 300)))
    if not inv:
        return 2
    ui = inv[0]["uid"]
    step("3 OpenVIRef.'vi reference' -> Invoke.'reference'", "Wire +1",
         lambda: g.wire(OP, "Function", ovr, "vi reference", "Invoke", idx("Invoke", ui), "reference"))
    g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("assembled nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es, flush=True)
    if es != 1:
        print("STOP: broken - NOT saving", flush=True); return 5
    step("4 save", "size > 0", lambda: g.save(OP))
    g.close_panel(OP)
    # test on a scratch copy of TRACK_kernel_v1
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(TRACK, T)
    vi = g.lv().GetVIReference(T, "", False, 0); vi.SetControlValue("index", 1)
    print("   scratch index set to", vi.GetControlValue("index"), flush=True)
    o = g.op(OP); o.SetControlValue("vi path", T)
    for lab in ("Names", "Names 2"):
        try:
            o.SetControlValue(lab, [])
        except Exception:
            pass
    try:
        g._run(o); print("   op ran (no dialog)", flush=True)
    except Exception as e:
        print("   op run:", str(e)[:160], flush=True)
    print("   saved scratch", g.save(T), flush=True)
    g.revert(T); time.sleep(0.5)
    v = g.lv().GetVIReference(T, "", False, 0).GetControlValue("index")
    print(f"TEST: index after save+revert = {v!r} (expect 1) -> {'PASS' if v == 1 else 'FAIL'}", flush=True)
    del vi
    try:
        g.close_panel(T)
    except Exception:
        pass
    os.remove(T); print("scratch removed", flush=True)
    return 0 if v == 1 else 6


if __name__ == "__main__":
    sys.exit(main())
