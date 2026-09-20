r"""build_opcaseframes_v0.py - OpCaseFrames_v0.vi: a case structure's FRAME NAMES and its frame diagrams, by UID.

The last unknown of Census B is polarity: Case #5540 has two frames (diagrams 5582 = forwards the left shift
registers, 5592 = forwards the loop's initialisers), and the rebuild must know WHICH of them is the TRUE case before
a `Select` can replace the structure. Semantics suggest 5592 is the reseed frame; polarity is measured, not assumed.

Derived from OpTunnelRead_v0 (24/24) by retargeting its cast from `Tunnel` to `CaseStructure` and replacing
`Tunnel.Inside Terminals[]` with `MultiFrameStructure.Frames[]` 6363801 (short name UNKNOWN - censused at build
time, never guessed), plus `CaseStructure.Frame Names` 6365002 -> `FrameNames` read straight into a string-array
indicator. The existing Index Array + `Terminal.Diagram`/`GObject.UID` chain is reused so `Frames[][i]` yields the
frame diagram's UID, which is matched against the diagrams the tunnel census already reported.

Order of edits follows the lessons banked in NAMES.md: keep the VI runnable at every save boundary, delete the
obsolete sink NODE before rewiring, expect the stub a deleted node leaves to make the next connection a BRANCH, and
run at most ONE Remove Bad Wires at the very end (never inside the window).

TEST (read-only, MAIN md5 in an outer finally): for case uid 5540, `FrameNames` must contain exactly two labels and
`Frames[][i]` must resolve to the two diagram uids 5582 and 5592 already measured - which pairs each label with its
frame and settles the polarity.

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opcaseframes_v0.log -- py -u tools/recipes/build_opcaseframes_v0.py [--test-only]
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import MAIN, lv_pid, fresh  # noqa: E402
from build_optunnelread_v0 import OP as OP_TUN, MAP_OUT as MAP_TUN  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpCaseFrames_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opcaseframes_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "case5540_polarity.json")
CASE_UID = 5540
KNOWN_FRAMES = {5582: "forwards the LEFT shift registers (previous state)",
                5592: "forwards the loop initialisers (reseed)"}
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def prop_node(cls, pid, label, pos):
    """Build a property node and CENSUS its data terminal - the short name is never guessed."""
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"exactly one new Property node ({cls.split(':')[1]}.{label} {pid})", len(new) == 1, str(new))
    w = walk(OP, 0)
    data = [r for r in w[new[0]][2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
    must(f"the new node has exactly one data SOURCE terminal ({label})", len(data) == 1,
         str([(r["name"], r["is_source"]) for r in w[new[0]][2]]))
    print(f"   CENSUS {cls} {pid} -> data terminal {data[0]['name']!r}", flush=True)
    return new[0], data[0]["name"]


def add_indicator(uid, name, key, labels):
    w = walk(OP, 0)
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new = [r for u, r in rows1.items() if u not in rows0]
    must(f"exactly one new panel object for '{name}' ({key})", len(new) == 1, str(new))
    must(f"it is an INDICATOR with a unique label ({key})",
         new[0]["indicator"] and sum(1 for r in rows1.values() if r["label"] == new[0]["label"]) == 1, str(new[0]))
    labels[key] = new[0]["label"]


def main():
    if "--test-only" in sys.argv:
        fresh()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpCaseFrames_v0.vi and its labels exist from a passed build", os.path.exists(OP) and "frame_names" in labels, str(labels))
        return test(labels)
    must("S the tunnel op exists", os.path.exists(OP_TUN))
    with open(MAP_TUN, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_TUN, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    es = [("copy of the tunnel op", g.exec_state(OP))]
    must("A the copied tunnel op is runnable", es[-1][1] == 1, str(es))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # A: the two readers, and the seed taken from the CASESTRUCTURE one. Runs 1-4 took the seed from the
    # MultiFrameStructure node, which made the cast emit MultiFrameStructure - and feeding that into the
    # CaseStructure-class Frame Names node is a DOWNCAST, the same break that bit the Generic->GObject chain earlier
    # (a broken wire still reports equal uids at both ends). CaseStructure is the child, so a CaseStructure-typed cast
    # drives BOTH nodes: child -> parent is an upcast.
    # run 5 (15:3x): build ONE node here. Two unwired property nodes leave the VI broken before the seed can feed
    # either of them, and this gate is meant to keep the VI runnable up to the deliberate (never-saved) window below.
    pnN, n_names = prop_node("VI Server:CaseStructure", "6365002", "Frame Names", (1100, 3100))
    w = walk(OP, 0)
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    g.create_control(OP, w[pnN][0], term(w[pnN][2], "reference", False)["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new_ctl = [r for u, r in rows1.items() if u not in rows0]
    must("A exactly one new control (MultiFrameStructure-typed seed)", len(new_ctl) == 1, str(new_ctl))
    labels["seedF"] = new_ctl[0]["label"]
    es.append(("Frames[] node + seed (wired)", g.exec_state(OP)))
    must("A runnable with the seed wired", es[-1][1] == 1, str(es))
    # B: retarget the lookup cast to MultiFrameStructure and feed the Index Array from Frames[]
    w = walk(OP, 0)
    ti = next(u for u, v in w.items() if term(v[2], "InsideTerms[]", True))
    w_inner = term(w[ti][2], "InsideTerms[]", True)["wire"]
    ia = next(u for u, v in w.items() if term(v[2], "array", False) and term(v[2], "array", False)["wire"] == w_inner)
    cast1 = next(u for u, v in w.items() if term(v[2], "specific class reference", True)
                 and term(v[2], "specific class reference", True)["wire"] == term(w[ti][2], "reference", False)["wire"])
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    for wid in (w_inner, pw[labels["seedT"]]["wire"], pw[labels["seedF"]]["wire"]):
        if wid in ws:
            g.delete_object(OP, "Wire", [o["uid"] for o in g.report_all(OP, "Wire")].index(wid), verify=False)
    g.delete_object(OP, "Property", fi("Property", ti), verify=False)      # the obsolete Inside Terminals[] node
    es.append(("old wiring + Inside Terminals[] node removed (broken window - never saved)", g.exec_state(OP)))
    g.wire_control(OP, [labels["seedF"]], "Function", fi("Function", cast1), ["target class"])
    g.wire(OP, "Function", fi("Function", cast1), "specific class reference", "Property", fi("Property", pnN), "reference", branch=True)
    # the Frames[] node is created only now, with the cast available to feed it immediately (upcast: the cast emits
    # CaseStructure, the node is declared on its parent MultiFrameStructure)
    pnF, n_frames = prop_node("VI Server:MultiFrameStructure", "6363801", "Frames[]", (1100, 2800))
    g.wire(OP, "Function", fi("Function", cast1), "specific class reference", "Property", fi("Property", pnF), "reference", branch=True)
    g.wire(OP, "Property", fi("Property", pnF), n_frames, "IndexArray", fi("IndexArray", ia), "array")
    w = walk(OP, 0); pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("B PROVENANCE seed -> cast 'target class'",
         pw[labels["seedF"]]["wire"] and pw[labels["seedF"]]["wire"] == term(w[cast1][2], "target class", False)["wire"])
    a = term(w[cast1][2], "specific class reference", True)["wire"]; b = term(w[pnF][2], "reference", False)["wire"]
    must("B PROVENANCE cast output -> Frames[] node", a and a == b, f"{a}/{b}")
    a = term(w[pnF][2], n_frames, True)["wire"]; b = term(w[ia][2], "array", False)["wire"]
    must("B PROVENANCE Frames[] -> Index Array 'array'", a and a == b, f"{a}/{b}")
    w = walk(OP, 0)
    must("C PROVENANCE cast output -> Frame Names node",
         term(w[pnN][2], "reference", False)["wire"] == term(w[cast1][2], "specific class reference", True)["wire"])
    # D: the element now carries DIAGRAM references, so every inherited TERMINAL reader is class-incompatible and must
    # be DELETED, not re-fed (peer ...-opcaseframes-terminal-chain-must-go: matching wire uids prove only that both
    # ends reference the same wire, never that the classes agree). Their indicators stay behind unwired, which is
    # harmless - an indicator is a data sink. Kept: Generic.Owner on the element, because a frame diagram's owner
    # should be the case structure itself (5540) - a free provenance check - and GObject.UID for the frame uid.
    w = walk(OP, 0)
    doomed = []
    for u, v in w.items():
        names = {r["name"] for r in v[2]}
        if names & {"IsSource", "Wire", "Diagram"} and term(v[2], "reference", False):
            doomed.append((u, sorted(names & {"IsSource", "Wire", "Diagram"})))
    # run 2 (14:4x): identify the frame-uid node BEFORE the deletions - a deleted node leaves its wire as a stub, so
    # afterwards that node's reference is NOT 0 and cannot be found by looking for unwired sinks.
    dia = next((u for u, v in w.items() if term(v[2], "Diagram", True)), None)
    must("D the inherited Terminal.Diagram node is present", dia is not None, str(sorted(w)[:8]))
    w_dia = term(w[dia][2], "Diagram", True)["wire"]
    frame_uid_node = next((u for u, v in w.items() if term(v[2], "UID", True) and term(v[2], "reference", False)
                           and term(v[2], "reference", False)["wire"] == w_dia), None)
    must("D exactly the UID node fed by Terminal.Diagram is identified as the frame-uid node", frame_uid_node is not None, str(w_dia))
    print(f"   DIAG deleting inherited TERMINAL readers: {doomed}; frame-uid node is {frame_uid_node} (fed by wire {w_dia})", flush=True)
    for u, _n in doomed:
        ids = [o["uid"] for o in g.report_all(OP, "Property")]
        if u in ids:
            g.delete_object(OP, "Property", ids.index(u), verify=False)
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    if w_dia in ws:
        g.delete_object(OP, "Wire", ws.index(w_dia), verify=False)      # the stub the deleted node left behind
    g.wire(OP, "IndexArray", fi("IndexArray", ia), "element", "Property", fi("Property", frame_uid_node), "reference", branch=True)
    uid_nodes = [frame_uid_node]
    g.remove_bad_wires_scripted(OP)          # the ONE cleanup, after the graph is whole again
    w = walk(OP, 0)
    must("D PROVENANCE Index Array element -> the frame-uid node",
         term(w[uid_nodes[0]][2], "reference", False)["wire"] == term(w[ia][2], "element", True)["wire"])
    es.append(("terminal readers deleted, frame-uid node re-fed (+ single cleanup)", g.exec_state(OP)))
    if es[-1][1] != 1:
        # run 3 (14:5x) left exactly one meaningful orphan: a Property node whose 'reference' lost its feed when the
        # terminal readers went. Report WHAT it reads (its data terminals) and re-feed it by kind: a class/uid reader
        # belongs on the owner cast's output, anything else on the Index Array element.
        w = walk(OP, 0)
        cast_owner = next((u for u, v in w.items() if term(v[2], "specific class reference", True)
                           and u != cast1), None)
        for u, v in list(w.items()):
            ref = term(v[2], "reference", False)
            if not ref or ref["wire"] != 0 or u in (pnF, pnN):
                continue
            data = [r["name"] for r in v[2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
            ids = [o["uid"] for o in g.report_all(OP, "Property")]
            if u not in ids:
                continue
            # peer ...-opcaseframes-last-orphan-node-1329: DELETE an inherited reader whose purpose is gone, rather
            # than re-feeding it to satisfy the compiler - that would keep semantically dead code alive.
            print(f"   DIAG orphan Property {u} reads {data} -> deleting (its diagnostic purpose belongs to the old chain)", flush=True)
            g.delete_object(OP, "Property", ids.index(u), verify=False)
        es.append(("remaining orphan readers deleted", g.exec_state(OP)))
        print(f"OBSERVED ExecState per step: {es}", flush=True)
    must("C runnable after the retarget", es[-1][1] == 1, str(es))
    add_indicator(pnN, n_names, "frame_names", labels)
    add_indicator(pnN, "error out", "errN", labels)
    add_indicator(pnF, "error out", "errF", labels)
    es.append(("indicators", g.exec_state(OP)))
    print(f"OBSERVED ExecState per step: {es}", flush=True)
    must("D op runnable before the save", es[-1][1] == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read_frame(vi, labels, case_uid, idx):
    vi.SetControlValue(labels["frame_names"], [])
    for lab in (labels["uid_back"], labels["frame_uid"]):
        vi.SetControlValue(lab, 0)
    vi.SetControlValue(labels["cls_back"], "POISON")
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue(labels["uid_in"], case_uid); vi.SetControlValue(labels["term_index"], idx)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errL", "errN", "errF", "errD")) if x)
    names = vi.GetControlValue(labels["frame_names"])
    r = dict(case=case_uid, index=idx, uid_back=int(vi.GetControlValue(labels["uid_back"])),
             case_class=vi.GetControlValue(labels["cls_back"]), frame_uid=int(vi.GetControlValue(labels["frame_uid"])),
             names=[str(x) for x in (names or [])], err=err, errs=errs)
    print(f"OBSERVED: case {case_uid} ({r['case_class']!r:.16}) Frames[{idx}] -> diagram {r['frame_uid']}; "
          f"FrameNames {r['names']} {err[:24]} {errs[:40]}", flush=True)
    return r


def test(labels):
    vi = g.op(OP)
    try:
        rows = []
        for i in range(4):
            r = read_frame(vi, labels, CASE_UID, i)
            if r["errs"] and r["frame_uid"] == 0:
                break
            rows.append(r)
        must("T0 the case resolved and reported frames", rows and rows[0]["uid_back"] == CASE_UID and not rows[0]["err"], str(rows[:1]))
        must("T1 exactly two frames, matching the diagrams the tunnel census measured",
             {r["frame_uid"] for r in rows} == set(KNOWN_FRAMES), str([(r["index"], r["frame_uid"]) for r in rows]))
        names = rows[0]["names"]
        must("T2 FrameNames has one label per frame", len(names) == len(rows), f"{names} vs {len(rows)} frames")
        pol = {r["frame_uid"]: names[r["index"]] for r in rows}
        for uid, what in KNOWN_FRAMES.items():
            print(f"POLARITY: diagram {uid} = case {pol.get(uid)!r} - {what}", flush=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump({"frames": rows, "polarity": {str(k): v for k, v in pol.items()}}, f, indent=1, default=str)
        n_ok = sum(1 for _n, p in B.PASS if p)
        print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
        return 0 if B.PASS and n_ok == len(B.PASS) else 1
    finally:
        same = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN)) == MAIN_BASE
        print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched", flush=True)
        B.PASS.append(("T(finally) main VI untouched", same))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True); sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True); sys.exit(1)
