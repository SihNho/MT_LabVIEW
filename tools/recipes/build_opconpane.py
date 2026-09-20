"""build_opconpane.py - OpConPane_v0.vi: READ a VI's connector pane by script.

Why: TRACK_kernel_v1's `backend` selector (control `index`) is not on the connector pane, so the main VI cannot drive it with
a wire; it can only be chosen by the control's saved default. Putting it on the pane needs two ops, and this is the reader
(the writer, OpConPaneAssign_v0, must know which terminal is FREE before it assigns anything).

API (labviewwiki via codex 2026-08-31, IDs now in docs/vi-server-ids.json):
  VI.Connector Pane:Reference = 23E  ->  ConnectorPane refnum
  ConnectorPane.Controls[]    = 239A8403 (one Control refnum per terminal, terminal-index order, NULL = unassigned)
  ConnectorPane.Number of Connection Terminals = 239A8401
Terminal indices are NOT geometric, so the map must be READ, never derived from the pane's picture.

Built from OpFPLabels_v0, which already is `VI -> <something>.Controls[] -> Index Array -> Control.Label -> Text.Text -> 'Text'`:
only its first two Property nodes change, from Front Panel (23D) + Panel.Controls[] (6348801) to Connector Pane:Reference (23E)
+ ConnectorPane.Controls[] / Number of Connection Terminals. Everything downstream is reused untouched.

Steps (prediction contract):
  1. copy OpFPLabels_v0 -> OpConPane_v0; delete the two head Property nodes (by position ~ (420,300) and (520,300))
     predict: Property count 4 -> 2, ExecState 0
  2. PN1 = VI.Connector Pane:Reference (23E) at (420,300) <- Open VI Reference 'vi reference'   predict: +1 Property
  3. PN2 = ConnectorPane [Controls[] 239A8403, Number of Connection Terminals 239A8401] at (520,300) <- PN1 output
     (PN1's output terminal name is the property's SHORT name - probed from a candidate list)
  4. PN2.'Controls[]' -> IA308.array (the surviving Index Array), indicator on the NumTerms terminal
     predict: ExecState 1
  5. save; then READ the pane of TRACK_kernel_v1 and print the terminal map (label per index, blank = FREE)
An unassigned terminal yields a NULL Control refnum, so Control.Label raises inside the op and LabVIEW shows its automatic
error dialog for ~8 s (OpFPLabels_v0's error out is unwired, same as its own index sweep) - expected, not a failure.
  py tools/bgrun.py --max-min 20 --log tools/bench/build_opconpane.log -- py -u tools/recipes/build_opconpane.py
"""
import os, shutil, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi"); OP = os.path.join(g.CLAUDEDEV, "OpConPane_v0.vi")
TRACK = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi")
CONPANE_OUT = ("ConPane", "Connector Pane", "Conn Pane", "ConnectorPane", "CPane", "Connector Pane:Reference", "Pane")
CTRLS_OUT = ("Controls[]", "Ctrls[]", "Controls")
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
    # NEVER touch the target through VI Server before overwriting it. close_panel() calls GetVIReference, which LOADS the VI;
    # the copyfile then changes it underneath LabVIEW and the next OpenFrontPanel raises the modal "The VI ... has changed on
    # disk since last saved or loaded by LabVIEW ... resulting in a corrupt VI" (Revert/Cancel), which blocks every COM call
    # until the process is killed (measured 2026-09-10: OpenFrontPanel hung the full 180 s watchdog).
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP); g.open_panel(OP); time.sleep(1.0)
    props = g.report(OP, "Property")
    print("copy of OpFPLabels_v0: nodes", g.count(OP, "Node"), "properties", [(o["uid"], o["pos"]) for o in props],
          "wires", g.count(OP, "Wire"), "ExecState", g.exec_state(OP), flush=True)
    print("fp:", [l for _, l, _ in g.fp_labels(OP)], flush=True)
    ovr = idx("Function", 43)

    def near(x, y):
        return min(g.report(OP, "Property"), key=lambda o: abs(o["pos"][0] - x) + abs(o["pos"][1] - y))
    head = [near(420, 300)["uid"], near(520, 300)["uid"]]
    print("   head Property nodes to replace:", head, flush=True)

    def drop_head():
        for uid in head:
            ids = [o["uid"] for o in g.report(OP, "Property")]
            if uid in ids:
                g.delete_object(OP, "Property", ids.index(uid))
        g.remove_bad_wires_scripted(OP)
        return g.count(OP, "Property"), g.count(OP, "Wire"), g.exec_state(OP)
    step("1 delete the Front Panel / Panel.Controls[] head", "Property 4 -> 2, ExecState 0", drop_head)

    pn1 = step("2 PN VI.Connector Pane:Reference (23E)", "+1 Property",
               lambda: g.build_property(OP, "VI Server:VI", [("23E", False)], (420, 300)))
    if not pn1:
        return 2
    u1 = pn1[0]["uid"]
    step("2b Open VI Reference.'vi reference' -> PN1.reference", "accepted",
         lambda: g.wire(OP, "Function", ovr, "vi reference", "Property", idx("Property", u1), "reference", branch=True))
    pn2 = step("3 PN ConnectorPane [Controls[], Number of Connection Terminals]", "+1 Property",
               lambda: g.build_property(OP, "VI Server:ConnectorPane",
                                        [("239A8403", False), ("239A8401", False)], (520, 300)))
    if not pn2:
        return 3
    u2 = pn2[0]["uid"]

    def pn1_out():
        for term in CONPANE_OUT:
            try:
                return term, g.wire(OP, "Property", idx("Property", u1), term, "Property", idx("Property", u2), "reference")
            except Exception as e:
                print(f"   {term!r}: {str(e)[:80]}", flush=True)
        return None
    if not step("3b PN1 output -> PN2.reference", "one candidate name accepted", pn1_out):
        return 3

    def ctrls_out():
        for term in CTRLS_OUT:
            try:
                return term, g.wire(OP, "Property", idx("Property", u2), term, "IndexArray", idx("IndexArray", 308), "array")
            except Exception as e:
                print(f"   {term!r}: {str(e)[:80]}", flush=True)
        return None
    if not step("4 PN2.'Controls[]' -> IA308.array", "accepted", ctrls_out):
        return 4
    g.remove_bad_wires_scripted(OP)
    print("   ExecState after the data wires:", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)
    # 4c. RE-WIRE THE INDEX ARRAY'S OUTPUT. Deleting the node that fed IA308's `array` leaves `element` with an undefined type,
    # which BREAKS the existing `element -> Control property node` wire downstream, and remove_bad_wires then deletes it. The
    # damage is invisible in the wire count (3 wires removed either way) and it is what kept ExecState at 0 through two
    # attempts; found by diffing net_map of the broken build against the intact source, where IA308 has nothing unwired.
    # Note also: in OpFPLabels_v0 every property node's error terminal is UNWIRED, so no error chain is added here.
    pn3 = near(700, 300)["uid"]
    step("4c IA308.'element' -> PN3 (Control).reference", "Wire +1",
         lambda: g.wire(OP, "IndexArray", idx("IndexArray", 308), "element", "Property", idx("Property", pn3), "reference"))
    g.remove_bad_wires_scripted(OP)
    print("   ExecState after re-wiring element:", g.exec_state(OP), "wires", g.count(OP, "Wire"), flush=True)

    n2 = g.count(OP, "Node") - 1                       # PN2 was created last -> last entry of Nodes[]
    lab = step("4b indicator on PN2's 'Number of Connection Terminals'", "a readable indicator",
               lambda: _ind(OP, n2, "Number"))
    g.remove_bad_wires_scripted(OP); es = g.exec_state(OP)
    print("\nassembled: nodes", g.count(OP, "Node"), "wires", g.count(OP, "Wire"), "ExecState", es,
          "\nfp:", [l for _, l, _ in g.fp_labels(OP)], "\nsteps failed:", [n for n, ok in STEPS if not ok], flush=True)
    if es != 1:
        print("STOP: broken - NOT saving. Net map of the BROKEN build follows, then the INTACT source for comparison:", flush=True)
        try:
            print("\n--- OpConPane_v0 (broken) ---", flush=True); g.print_net_map(*g.net_map(OP))
        except Exception as e:
            print("   net_map(OP) failed:", str(e)[:150], flush=True)
        try:
            print("\n--- OpFPLabels_v0 (intact source) ---", flush=True); g.print_net_map(*g.net_map(SRC))
        except Exception as e:
            print("   net_map(SRC) failed:", str(e)[:150], flush=True)
        return 5
    print("saved", g.save(OP), flush=True)
    g.close_panel(OP); time.sleep(0.5)

    # --- read TRACK_kernel_v1's pane -------------------------------------------------------------
    print("\n=== connector pane of TRACK_kernel_v1 ===", flush=True)
    vi = g.op(OP); vi.SetControlValue("vi path", TRACK)
    for l in ("Names", "Names 2", "Class Name", "Class Name 2"):
        try:
            vi.SetControlValue(l, [] if l.startswith("Names") else "")
        except Exception:
            pass
    n_terms = None
    for i in range(28):
        vi.SetControlValue("index", i)
        try:
            g._run(vi); text = vi.GetControlValue("Text")
        except Exception as e:
            text = f"(FREE / error: {str(e)[:60]})"
        if n_terms is None and lab:
            try:
                n_terms = int(vi.GetControlValue(lab)); print(f"   terminals on the pane: {n_terms}", flush=True)
            except Exception:
                pass
        print(f"   terminal[{i:2}] = {text!r}", flush=True)
        if n_terms and i >= n_terms - 1:
            break
    return 0


def _ind(OP, n, wanted, max_terms=10):
    for t in range(max_terms):
        fp0 = {l for _, l, _ in g.fp_labels(OP)}
        new = g.create_indicator(OP, n, t)
        labs = [l for _, l, _ in g.fp_labels(OP) if l not in fp0]
        if new and labs and labs[-1].lower().startswith(wanted.lower()):
            return labs[-1]
        if new:
            ct = [o["uid"] for o in g.report(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"])); ct = [x["uid"] for x in g.report(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
    return None


if __name__ == "__main__":
    sys.exit(main())
