"""build_opconpaneassign.py - OpConPaneAssign_v0.vi: put a front-panel control ON the connector pane, by script.

Companion to OpConPane_v0 (the reader). Reading TRACK_kernel_v1's pane gave: 16 terminals, 13 assigned, **5, 6 and 10 FREE**.
Assigning into a free terminal leaves the pattern and the other 13 assignments untouched, which matters because a pattern
change is destructive and would break every caller (docs/NAMES.md).

  ConnectorPane.Assign Control To Terminal = 239A8000 (Control refnum, Terminal Index)

Built from OpFPLabels_v0, which ALREADY produces exactly the input this method needs: `VI -> Front Panel (23D) ->
Panel.Controls[] (6348801) -> Index Array[`index`] -> element` is a Control refnum for the front-panel object at tabbing
position `index`. Only the label-reading tail is replaced by the Invoke node.

Steps (prediction contract):
  1. copy OpFPLabels_v0 -> OpConPaneAssign_v0 (os.remove first: never load a VI you are about to overwrite)
  2. delete the two tail Property nodes (Control Label/Indicator at ~(700,300), Text.Text at ~(850,300))
     predict: Property 4 -> 2, ExecState 0, IA308.element left unwired
  3. PN_cp = VI.Connector Pane:Reference (23E) at (420,430) <- Open VI Reference 'vi reference' (branch)
  4. INV = Invoke ConnectorPane.'Assign Control To Terminal' (239A8000) at (700,380)
  5. PN_cp.'ConPane' -> INV.'reference'; IA308.'element' -> INV.<control input>; a control on INV's terminal-index input
     predict: ExecState 1
  6. save, then TEST on a SCRATCH COPY of TRACK_kernel_v1: assign its `index` control to free terminal 5, read the pane back
     with OpConPane_v0 and require terminal[5] == 'index'. The real TRACK_kernel_v1 is only touched by a later, separate run.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opconpaneassign.log -- py -u tools/recipes/build_opconpaneassign.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpConPaneAssign_v0.vi")
READER = os.path.join(g.CLAUDEDEV, "OpConPane_v0.vi")
TRACK = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi"); T = os.path.join(g.CLAUDEDEV, "SCRATCH_conpane.vi")
CONPANE_OUT = ("ConPane", "Connector Pane", "ConnectorPane", "Pane")
CTRL_IN = ("Control", "Control Reference", "control", "Control In", "Ctrl")
FREE_TERMINAL = 5
g._run.__defaults__ = (6.0, 45.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn(); print(f"   observed: {obs}", flush=True); STEPS.append((name, True)); return obs
    except Exception as e:
        print(f"   observed: EXC {str(e)[:220]}", flush=True); STEPS.append((name, False)); return None


def idx(cls, uid):
    return [o["uid"] for o in g.report(OP, cls)].index(uid)


def main():
    g._lv = None
    if "--test-only" in sys.argv and os.path.exists(OP):
        print("--test-only: reusing the saved OpConPaneAssign_v0", flush=True)
        return test("Terminal Index")
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.open_panel(OP); time.sleep(1.0)
    print("copy of OpFPLabels_v0: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"),
          "ExecState", g.exec_state(OP), flush=True)
    print("fp:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
    ovr = idx("Function", 43)

    def near(x, y):
        return min(g.report(OP, "Property"), key=lambda o: abs(o["pos"][0] - x) + abs(o["pos"][1] - y))

    def drop_tail():
        for uid in [near(700, 300)["uid"], near(850, 300)["uid"]]:
            ids = [o["uid"] for o in g.report(OP, "Property")]
            if uid in ids:
                g.delete_object(OP, "Property", ids.index(uid))
        g.remove_bad_wires_scripted(OP)
        return g.count(OP, "Property"), g.count(OP, "Wire"), g.exec_state(OP)
    step("2 delete the label-reading tail", "Property 4 -> 2, ExecState 0", drop_tail)

    pncp = step("3 PN VI.Connector Pane:Reference (23E)", "+1 Property",
                lambda: g.build_property(OP, "VI Server:VI", [("23E", False)], (420, 430)))
    if not pncp:
        return 3
    ucp = pncp[0]["uid"]
    step("3b OpenVIRef.'vi reference' -> PN_cp.reference", "accepted",
         lambda: g.wire(OP, "Function", ovr, "vi reference", "Property", idx("Property", ucp), "reference", branch=True))
    inv = step("4 Invoke ConnectorPane.'Assign Control To Terminal' (239A8000)", "+1 Invoke",
               lambda: g.build_invoke(OP, "VI Server:ConnectorPane", "239A8000", (700, 380)))
    if not inv:
        return 4
    uin = inv[0]["uid"]

    def inv_i():
        return [o["uid"] for o in g.report(OP, "Invoke")].index(uin)

    def cp_to_inv():
        for term in CONPANE_OUT:
            try:
                return term, g.wire(OP, "Property", idx("Property", ucp), term, "Invoke", inv_i(), "reference")
            except Exception as e:
                print(f"   {term!r}: {str(e)[:80]}", flush=True)
        return None
    if not step("5 PN_cp output -> INV.reference", "one candidate accepted", cp_to_inv):
        return 5

    def elem_to_inv():
        for term in CTRL_IN:
            try:
                return term, g.wire(OP, "IndexArray", idx("IndexArray", 308), "element", "Invoke", inv_i(), term)
            except Exception as e:
                print(f"   {term!r}: {str(e)[:80]}", flush=True)
        return None
    if not step("5b IA308.'element' -> INV control input", "one candidate accepted", elem_to_inv):
        return 5
    g.remove_bad_wires_scripted(OP)
    print("   ExecState before the terminal-index control:", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)

    n_inv = g.count(OP, "Node") - 1                    # the Invoke was created last
    lab = step("6 control on INV's terminal-index input", "a label naming the terminal index",
               lambda: _ctl(OP, n_inv, ("Terminal Index", "Terminal", "Index")))
    g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es,
          "\nfp:", [l for _, l, _ in g.fp_labels(OP)], "\nterminal-index control:", lab,
          "\nsteps failed:", [n for n, ok in STEPS if not ok], flush=True)
    if es != 1 or not lab:
        print("STOP: broken or no terminal-index control - NOT saving", flush=True)
        try:
            print("--- net map of the broken build ---", flush=True); g.print_net_map(*g.net_map(OP))
        except Exception as e:
            print("   net_map failed:", str(e)[:120], flush=True)
        return 5
    print("saved", g.save(OP), flush=True)
    g.close_panel(OP); time.sleep(0.5)
    return test(lab)


def test(lab):
    """Assign TRACK's `index` control to free terminal 5 on a SCRATCH COPY, and read the pane back to prove it landed."""
    print(f"\n=== TEST on a scratch copy: assign 'index' to terminal {FREE_TERMINAL} ===", flush=True)
    if os.path.exists(T):
        os.remove(T)
    shutil.copyfile(TRACK, T)
    # REQUIRED: a target loaded only through GetVIReference declines every edit SILENTLY (no error, no dialog) - the standing
    # rule in the skill. The first test run assigned nothing, reported a clean error cluster and left the file byte-identical
    # purely because this call was missing (2026-09-10).
    g.open_panel(T); time.sleep(0.8)
    labels = [l for _, l, _ in g.fp_labels(T)]
    print("   scratch fp:", labels, flush=True)
    if "index" not in labels:
        print("STOP: no 'index' control on the scratch", flush=True); return 6
    fp_i = labels.index("index")
    print(f"   'index' is front-panel object {fp_i}", flush=True)
    vi = g.op(OP)
    vi.SetControlValue("vi path", T); vi.SetControlValue("index", fp_i); vi.SetControlValue(lab, FREE_TERMINAL)
    for l in ("Names", "Names 2"):
        try:
            vi.SetControlValue(l, [])
        except Exception:
            pass
    for l in ("Class Name", "Class Name 2"):
        try:
            vi.SetControlValue(l, "")
        except Exception:
            pass
    try:
        g._run(vi); print("   assign ran, error out:", vi.GetControlValue("error out"), flush=True)
    except Exception as e:
        print("   assign EXC:", str(e)[:200], flush=True); return 6
    print("   saved scratch", g.save(T), "bytes (was", os.path.getsize(TRACK), "before the assignment)", flush=True)
    rd = g.op(READER); rd.SetControlValue("vi path", T)
    for l in ("Names", "Names 2"):
        try:
            rd.SetControlValue(l, [])
        except Exception:
            pass
    got = {}
    for i in range(16):
        rd.SetControlValue("index", i)
        try:
            g._run(rd); got[i] = rd.GetControlValue("Text")
        except Exception:
            got[i] = "(FREE)"
        print(f"   terminal[{i:2}] = {got[i]!r}", flush=True)
    ok = got.get(FREE_TERMINAL) == "index" and sum(1 for v in got.values() if v == "(FREE)") == 2
    print("\nTEST:", "PASS" if ok else "FAIL", f"- terminal[{FREE_TERMINAL}] = {got.get(FREE_TERMINAL)!r}", flush=True)
    try:
        g.close_panel(T)
    except Exception:
        pass
    os.remove(T); print("scratch removed", flush=True)
    return 0 if ok else 6


def _ctl(OP, n, wanted, max_terms=10):
    for t in range(max_terms):
        w0 = g.count(OP, "Wire"); new, lab = g.create_control(OP, n, t)
        if new and lab and any(lab.lower().startswith(w.lower()) for w in wanted) and g.count(OP, "Wire") > w0:
            return lab
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
    return None


if __name__ == "__main__":
    sys.exit(main())
