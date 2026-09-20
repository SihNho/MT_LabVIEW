r"""build_strtopath.py - StrToPath.vi: one `String To Path` primitive with a string control and a path indicator on the
connector pane. Stage-2 step B (docs/stage2-assembly-step-b.md, revised route): Python precomputes every frame's
full path as a STRING; the replay loop auto-indexes a string-array control and converts each element with this
sub-VI into IMAQ ReadFile's `File Path`. It replaces FramePath.vi, whose copied `Format Into String` would keep the
donor's 5 argument terminals (NI error 83 at run time; a node's arity is not scriptable - peer
archive/peer/2026-09-14-stage2-step-b-revised-forloop-route.md).

Donor node: claudeDev/background VIs_COPY/save N xyz traces.vi, top-level n7 uid 194 'String To Path'
(terminals: 'string' sink, 'path' source - tools/bench/census_savetraces_terms.log). Harvested with
copy_into(prepare=set_node_label) - the donor file itself is never edited.

PREDICTION CONTRACT (first miss stops; nothing saved on a miss):
  C1 copy_into -> exactly one new node labelled 'STP' whose terminals are 'string'/'path'
  C2 create_control on 'string' -> a String control; create_indicator on 'path' -> a Path indicator (labels read back)
  C3 ExecState 1
  C4 FUNCTIONAL over COM: 'G:\x\img00007.tif', 'C:\a b\img11824.tif', '\\srv\share\f.tif' -> the Path indicator
     reads back equal to the input string (LabVIEW Path -> COM string), error out clear
  C5 conpane_assign(string -> 0, path -> 1); conpane() shows both; saved
  py tools/bgrun.py --max-min 8 --log tools/bench/build_strtopath.log -- py -u tools/recipes/build_strtopath.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

DONOR = os.path.join(g.CLAUDEDEV, "background VIs_COPY", "save N xyz traces.vi")
BASE = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "StrToPath.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "strtopath_labels.json")
DONOR_NODE_INDEX = 7
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def walk(target, diagram=0):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(40):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def term(rows, name, source):
    return next((r for r in rows if r["name"] == name and r["is_source"] == source), None)


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(BASE, OP); time.sleep(0.3)
    def prepare(src):
        # Run 1 (23:55, cycle3_toolkit.log): Error 1054 'object not found' in OpMoveByLabel - the label write had been
        # DECLINED SILENTLY because the substituted donor's panel was not open (the fleet rule for every edit; the
        # one prior prepare= success, tools/bench/copy_clfn2.py, opened the panel first). Verify by reading back.
        g.report(src, "SubVI"); g.open_panel(src); time.sleep(1.0)
        g.set_node_label(src, 0, DONOR_NODE_INDEX, "STP")
        labs = {r["uid"]: r["label"] for r in g.node_labels(src, 0)}
        print(f"   prepare: labels now {[(u, l) for u, l in labs.items() if l in ('STP', 'String To Path')]}", flush=True)
        # peer (…-move-by-label-1054): require the label on UID 194 specifically (the census's String To Path), which
        # separates 'edit declined' from 'wrong node index' in one readback
        if labs.get(194) != "STP":
            raise RuntimeError(f"prepare: 'STP' is not on uid 194 (uid 194 reads {labs.get(194)!r})")
    # Run 2 (23:58): the label 'STP' was verified on uid 194 and the Move op STILL raised 1054 (label not found).
    # Plan A (H7, the discriminating test): a built-in function's lookup NAME is its own name, not its label text ->
    # look it up as 'String To Path' with NO prepare. Plan B (declared): the former 'STP' + prepare route.
    # Runs 1-3: label/name lookup cannot find a built-in primitive (error 1054 x3). Plan C (reviewed, ...-fail3-...):
    # copy BY REFERENCE with OpMoveByIndex_v0 - Traverse class 'Function', index of uid 194 in report() order,
    # UID guard: the op's 'Selected UID' must read 194 or the target is rejected.
    # Run 4 (00:19): the copy landed (UID guard 194) but saving the BROKEN target by keystroke failed. Revised
    # protocol (peer ...-fail4-gui-save-of-broken-target): the copied primitive gets its required input and its
    # indicator INSIDE copy_by_index's `finish` hook, on the still-loaded Target, so the VI is runnable and is
    # COM-saved once - no broken intermediate is ever saved.
    labels = {}

    def finish(dst):
        w = walk(dst)
        print(f"   finish: nodes {[(u, v[0], v[1], [r['name'] for r in v[2]]) for u, v in w.items()]}", flush=True)
        stp = next((u for u, v in w.items() if term(v[2], "string", False) and term(v[2], "path", True)), None)
        check("C1 the copied node has 'string' (sink) / 'path' (source)", stp is not None)
        if stp is None:
            raise RuntimeError("finish: no String To Path node on the Target")
        n = w[stp][0]
        before = {l for _i, l, ind in g.fp_labels(dst) if not ind}
        g.create_control(dst, n, term(w[stp][2], "string", False)["i"])
        new = [l for _i, l, ind in g.fp_labels(dst) if not ind and l not in before]
        check("C2 String control", bool(new), str(new)); labels["string"] = new[-1] if new else None
        w = walk(dst)
        before = {l for _i, l, ind in g.fp_labels(dst) if ind}
        g.create_indicator(dst, n, term(w[stp][2], "path", True)["i"])
        new = [l for _i, l, ind in g.fp_labels(dst) if ind and l not in before]
        check("C2 Path indicator", bool(new), str(new)); labels["path"] = new[-1] if new else None
        print(f"   finish: ExecState {g.exec_state(dst)} (1 required before the COM save)", flush=True)

    added = None
    try:
        funcs = [o["uid"] for o in g.report(DONOR, "Function")]
        i_stp = funcs.index(194)
        print(f"   donor Function[] order: {funcs}; uid 194 at index {i_stp}", flush=True)
        added, sel = g.copy_by_index(DONOR, "Function", i_stp, OP, expect_uid=194, finish=finish)
        print(f"   copy_by_index -> added {added}, selected uid {sel}", flush=True)
    except Exception as e:
        print(f"   OBSERVED EXC {str(e)[:240]}", flush=True); added = None
    check("C1 one object copied and the Target saved runnable", bool(added), str(added))
    if not added:
        return 2
    g.open_panel(OP); time.sleep(0.8)
    es = g.exec_state(OP); check("C3 ExecState 1 (the copied file)", es == 1, str(es))
    if es != 1 or None in labels.values():
        g.close_panel(OP); return 3
    vi = g.op(OP)
    for s in (r"G:\x\img00007.tif", r"C:\a b\img11824.tif", r"\\srv\share\f.tif"):
        vi.SetControlValue(labels["string"], s)
        try:
            g._run(vi); out = str(vi.GetControlValue(labels["path"]))
        except Exception as e:
            out = f"EXC {str(e)[:100]}"
        check(f"C4 {s!r} -> path reads back equal", out == s, repr(out))
    for lab, k in ((labels["string"], 0), (labels["path"], 1)):
        try:
            g.conpane_assign(OP, lab, k)
        except Exception as e:
            print(f"   conpane_assign {lab!r}: EXC {str(e)[:120]}", flush=True)
    cp = g.conpane(OP); print(f"   conpane: {str(cp)[:300]}", flush=True)
    check("C5 both pane assignments visible", labels["string"] in str(cp) and labels["path"] in str(cp))
    n_ok = sum(1 for _n, ok in PASS if ok)
    if n_ok == len(PASS):
        g.set_auto_error_handling(OP, False); g.save(OP)
        with open(MAP_OUT, "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=2)
        print("   saved", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for nme, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {nme}", flush=True)
    return 0 if n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
