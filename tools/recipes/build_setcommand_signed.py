"""build_setcommand_signed.py - SetCommand_signed.vi: the lab's Autonics rotor driver with a SIGNED position read.
User decision 2026-09-14 18:3x ("읽기부호 수정하도록 하자"). The instr.lib original is copied, never touched; the copy
is for the NEW main VI only. Plan review: archive/peer/2026-09-14-setcommand-signed-copy-plan.md.

Read frame (diagram 1, measured in probe_setcommand.log): VISA Write 795 -> VISA Read 926 -(1251)-> String Subset
979 -(1183)-> Hexadecimal String To Number 1013 (U32) -(2939)-> Multiply 2841.x ; Type Cast 622 (x <- 1183) -> Multiply
784 -> debug indicator. Fix = parse U32 as now, then Type Cast the NUMBER to the signed type, then scale:
  1  copy -> SetCommand_signed.vi, open_panel                                            ExecState 1
  2  delete wire 2939 and wire 1183 (by uid)                                            ExecState 0
  3  connect substring(979 t0) -> Hex.string(1013 t4); Hex.number(1013 t0) -> TypeCast.x(622 t0);
     TypeCast.out(622 t2) -> Multiply 2841.x(t2) [branch]; substring -> 'read buffer 2' (connect_ctl)   ExecState 1
  4  save (deliverable)
  5  TEST copy SetCommand_signed_TEST.vi: delete wire 1251; create_control on String Subset.string -> 'string';
     auto error handling OFF; save. Functional test: tools/bench/test_setcommand_signed.py (no hardware).
  py tools/bgrun.py --max-min 15 --log tools/bench/build_setcommand_signed.log -- py -u tools/recipes/build_setcommand_signed.py
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

SRC = r"C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Autonics Motor\SetCommand.vi"
OP = os.path.join(g.CLAUDEDEV, "SetCommand_signed.vi")
OPT = os.path.join(g.CLAUDEDEV, "SetCommand_signed_TEST.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "setcommand_signed_labels.json")
READ_DIAGRAM = 1
g._run.__defaults__ = (6.0, 120.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def main():
    g._lv = None
    # Runs 3-4 (19:39, 19:46): close_panel() on a file about to be overwritten LOADS it (GetVIReference), and the
    # following copyfile + OpenFrontPanel then hits LabVIEW's untitled "changed on disk - Revert/Cancel" modal
    # (tools/bench/dialog_1949_crop.png). Never touch the output files over COM before writing them; require a
    # clean instance (nothing of this name loaded) instead - the caller restarts LabVIEW if a previous run failed.
    for p in (OP, OPT, os.path.join(g.CLAUDEDEV, "SetCommand_orig_TEST.vi")):
        if os.path.exists(p):
            os.remove(p)
    src_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3)
    t0 = time.time(); n_sub = len(g.report_all(OP, "SubVI"))          # load through an op first (skill rule), timed
    print(f"   preload via report_all: {n_sub} subVIs in {time.time() - t0:.1f} s", flush=True)
    t0 = time.time(); g.open_panel(OP); time.sleep(1.0)
    print(f"   open_panel: {time.time() - t0:.1f} s", flush=True)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(OP)

    def snap(tag=""):
        return f"{tag} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}"

    def nodes(diagram):
        out = {}
        for cand in range(40):
            nu, rows = g.node_terms_uid(OP, diagram, cand)
            if not nu:
                break
            out[nu] = (cand, {r["name"]: r for r in rows}, rows)
        return out

    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: copy not runnable.", flush=True); return 2
    labels = {r["uid"]: r["label"] for r in g.node_labels(OP, READ_DIAGRAM)}
    nd = nodes(READ_DIAGRAM)
    by_label = {}
    for u, (n, tm, rows) in nd.items():
        by_label.setdefault(labels.get(u), []).append(u)
    print(f"   read frame nodes: {[(u, labels.get(u)) for u in nd]}", flush=True)
    u_sub = by_label["String Subset"][0]; u_hex = by_label["Hexadecimal String To Number"][0]; u_tc = by_label["Type Cast"][0]
    n_sub, t_sub, _ = nd[u_sub]; n_hex, t_hex, _ = nd[u_hex]; n_tc, t_tc, _ = nd[u_tc]
    w_sub = t_sub["substring"]["wire"]; w_num = t_hex["number"]["wire"]
    # the scale Multiply = the Multiply whose x is fed by the Hex 'number' wire
    u_mul = next(u for u, (n, tm, rows) in nd.items() if labels.get(u) == "Multiply" and tm.get("x", {}).get("wire") == w_num)
    n_mul, t_mul, _ = nd[u_mul]
    print(f"   String Subset {u_sub} (Nodes[] {n_sub}, substring wire {w_sub}); Hex {u_hex} (Nodes[] {n_hex}, number wire {w_num}); "
          f"Type Cast {u_tc} (Nodes[] {n_tc}, x wire {t_tc['x']['wire']}); scale Multiply {u_mul} (Nodes[] {n_mul})", flush=True)
    if t_tc["x"]["wire"] != w_sub:
        print("STOP: Type Cast is not fed by the substring - the frame differs from the probe. Nothing saved.", flush=True); return 3

    wires = [o["uid"] for o in g.report_all(OP, "Wire")]
    step("2a delete wire number->Multiply.x", "Wire -1", lambda: (g.delete_object(OP, "Wire", wires.index(w_num)), snap("after"))[1])
    wires = [o["uid"] for o in g.report_all(OP, "Wire")]
    step("2b delete the substring wire (Hex.string / TypeCast.x / 'read buffer 2')", "Wire -1, ExecState 0",
         lambda: (g.delete_object(OP, "Wire", wires.index(w_sub)), snap("after"))[1])
    # Run 1 (19:35): connect_terminals / connect_ctl address the TOP-LEVEL Nodes[] only; these nodes live inside the
    # case frame -> out-of-range dialogs, nothing wired. Inside a frame, wire by Traverse class + index + terminal NAME
    # (gscript.wire, erdosmiller Wire Inputs / Wire Indicators - proven inside loop bodies).
    def fi(uid):
        return [o["uid"] for o in g.report_all(OP, "Function")].index(uid)
    step("3a substring -> Hex.string (wire by name)", "Wire +1", lambda: (g.wire(OP, "Function", fi(u_sub), "substring", "Function", fi(u_hex), "string"), snap("after"))[1])
    step("3b Hex.number -> TypeCast.x", "Wire +1", lambda: (g.wire(OP, "Function", fi(u_hex), "number", "Function", fi(u_tc), "x"), snap("after"))[1])
    step("3c TypeCast.out -> Multiply.x (branch)", "ExecState 1", lambda: (g.wire(OP, "Function", fi(u_tc), "*(type *) &x", "Function", fi(u_mul), "x", branch=True), snap("after"))[1])
    step("3d substring -> 'read buffer 2' indicator (Wire Indicators by name, branch)", "no exception",
         lambda: g.wire_indicators(OP, fi(u_sub), ["substring"], ["read buffer 2"], diagram_index=READ_DIAGRAM, node_class="Function"))
    purge()
    nd = nodes(READ_DIAGRAM)
    print(f"   after: Hex {[(r['name'], r['wire']) for r in nd[u_hex][2]]}; TypeCast {[(r['name'], r['wire']) for r in nd[u_tc][2]]}; "
          f"Multiply {[(r['name'], r['wire']) for r in nd[u_mul][2]]}", flush=True)
    es = g.exec_state(OP)
    ok = (nd[u_tc][1]["x"]["wire"] == nd[u_hex][1]["number"]["wire"] != 0 and
          nd[u_mul][1]["x"]["wire"] == nd[u_tc][1]["*(type *) &x"]["wire"] != 0 and nd[u_hex][1]["string"]["wire"] != 0)
    print(f"   wiring check {ok}, ExecState {es}", flush=True)
    if es != 1 or not ok or any(k == "exc" for _, k in STEPS):
        print("\nVERDICT: BROKEN / wiring mismatch - NOT SAVING.", flush=True); return 4
    step("4 save SetCommand_signed.vi", "written", lambda: g.save(OP))
    # 5 TEST copies (peer: regression against the untouched ORIGINAL with identical injection): the signed copy and
    # a copy of the instr.lib original, each with the VISA Read -> String Subset wire replaced by a 'string' control.
    g.close_panel(OP); time.sleep(0.3)
    labels_out = {"read_diagram": READ_DIAGRAM}

    DONOR = os.path.join(g.CLAUDEDEV, "OpSetLabel_v0.vi")     # has a string control labelled 'Text'

    def make_test(src, dst, tag):
        # run 2 (19:37): create_control resolves top-level Nodes[] only (String Subset is inside the case frame) ->
        # inject through an EXISTING string control moved in by copy_into, wired by name (wire_control auto-creates
        # the case tunnel). Reviewed: archive/peer/2026-09-14-setcommand-signed-fail2-test-injection.md
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copyfile(src, dst); time.sleep(0.3)
        step(f"5a {tag}: copy_into donor 'Text' string control", "one new GObject", lambda: g.copy_into(DONOR, "Text", dst))
        g.open_panel(dst); time.sleep(0.8)
        invT = g.uids(dst, "Invoke")
        ctl = [l for _i, l, ind in g.fp_labels(dst) if not ind and l == "Text"]
        print(f"   {tag} panel has 'Text' control: {bool(ctl)}", flush=True)
        if not ctl:
            return None
        ndT = {}
        for cand in range(40):
            nu, rows = g.node_terms_uid(dst, READ_DIAGRAM, cand)
            if not nu:
                break
            ndT[nu] = (cand, {r["name"]: r for r in rows})
        w_in = ndT[u_sub][1]["string"]["wire"]
        wiresT = [o["uid"] for o in g.report_all(dst, "Wire")]
        step(f"5b {tag}: delete VISA Read -> String Subset.string wire", "Wire -1", lambda: g.delete_object(dst, "Wire", wiresT.index(w_in), verify=False))
        fiT = [o["uid"] for o in g.report_all(dst, "Function")].index(u_sub)
        step(f"5c {tag}: wire_control 'Text' -> String Subset.string (into the frame)", "ExecState 1",
             lambda: g.wire_control(dst, ["Text"], "Function", fiT, ["string"]))
        junk = [u for u in g.uids(dst, "Invoke") if u not in invT]
        if junk:
            order = [o["uid"] for o in g.report_all(dst, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(dst, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(dst)
        ndT2 = {}
        for cand in range(40):
            nu, rows = g.node_terms_uid(dst, READ_DIAGRAM, cand)
            if not nu:
                break
            ndT2[nu] = {r["name"]: r for r in rows}
        wired = ndT2[u_sub]["string"]["wire"]
        es = g.exec_state(dst)
        new_c = ["Text"] if wired and es == 1 else []
        print(f"   {tag} String Subset.string wire {wired}; ExecState {es}", flush=True)
        if len(new_c) != 1:
            return None
        g.set_auto_error_handling(dst, False); g.save(dst)
        try:
            g.close_panel(dst)
        except Exception:
            pass
        return new_c[0]

    # run 3 (19:39): a TEST copy left OPEN by a failed run 2 was deleted/overwritten on disk -> OpenFrontPanel blocked
    # 180 s (NAMES: never overwrite a loaded VI). Every exit path now closes the panels (finally) and the failure
    # path removes the unsaved copy AFTER closing it.
    OPO = os.path.join(g.CLAUDEDEV, "SetCommand_orig_TEST.vi")
    try:
        inj = make_test(OP, OPT, "TEST-signed")
        if not inj:
            print("STOP: signed TEST copy not runnable - the deliverable IS saved; test copies not saved.", flush=True); return 5
        labels_out["inject"] = inj
        inj_o = make_test(SRC, OPO, "TEST-original")
        if not inj_o:
            print("STOP: original TEST copy not runnable.", flush=True); return 5
    finally:
        for p in (OPT, OPO):
            try:
                g.close_panel(p)
            except Exception:
                pass
    labels_out["inject_orig"] = inj_o
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels_out, f, indent=2)
    print(f"instr.lib original md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == src_md5}", flush=True)
    print("\nVERDICT: SetCommand_signed.vi + _TEST built (structural) - run tools/bench/test_setcommand_signed.py next", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
