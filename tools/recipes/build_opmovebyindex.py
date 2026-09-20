r"""build_opmovebyindex.py - OpMoveByIndex_v0.vi: copy ANY GObject from the (byte-substituted) Move-example Source
into the Target BY TRAVERSE INDEX, not by label. Replaces the failed name lookup: OpMoveByLabel_v0's
'Open VI Object Reference' cannot resolve a built-in primitive by label OR by its own name (error 1054 x3,
tools/bench/build_strtopath.log; peers ...-strtopath-fail1/2/3-...). Plan + gates: archive/peer/
2026-09-15-strtopath-fail3-move-by-index-plan.md.

DONOR TOPOLOGY (tools/bench/diag_opmovebylabel.log, uids): Source static ref 65 -> Invoke 100 'Revert VI'
('reference out' 946) -> PN 430 VI[Diagram] (data 530) -> Open VI Object Reference 503 ('owner refnum' 530,
'name/order' 612 <- control 'Add Label', 'vi object class' 559 <- constant, 'object refnum' 712) -> Invoke 265 Move
('reference' 712, 'owner' 738 <- PN 332 VI[Diagram] of the Target static ref 87, 'position' 528 <- constant,
'duplicate' unwired). Error chain: PN430.error out 447 -> 503 -> 459 -> PN332 -> 539 -> Move -> 597 -> SEH.

SURGERY (prediction each; first miss = stop, nothing saved):
  S1 delete Function[0] (= 503) + Remove Bad Wires        -> Function 0; wires 712/559/612/530/447/459 gone
  S2 PN430.'error out' -> PN332.'error in (no error)'      -> same wire uid both ends (the chain re-closed)
  S3 drop vi.lib\Utility\traverseref.llb\Traverse for GObjects.vi; 'VI Refnum' <- Invoke100.'reference out' (branch)
  S4 create_control on Traverse.'Class Name'  (label read back)
  S5 build_index_array; Traverse.'References' -> IA.'array'; create_control on IA.'index'
  S6 IA.'element' -> Move.'reference'  (the previously orphaned sink)
  S7 PN GObject[UID 632A813] <- IA.'element' (branch); create_indicator on its 'UID' -> 'Selected UID'
  S8 create_control on Move.'duplicate' (Boolean; the caller sets TRUE)
  S9 auto error handling OFF; ExecState 1 -> save; labels -> tools/bench/opmovebyindex_labels.json
The functional test is build_strtopath.py (copy of uid 194 with the UID guard).
  py tools/bgrun.py --max-min 12 --log tools/bench/build_opmovebyindex.log -- py -u tools/recipes/build_opmovebyindex.py
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

SRC = g.OP_MOVE_LABEL
OP = os.path.join(g.CLAUDEDEV, "OpMoveByIndex_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opmovebyindex_labels.json")
TRAV = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\traverseref.llb\Traverse for GObjects.vi"
P_UID = "632A813"
g._run.__defaults__ = (6.0, 120.0)
PASS = []


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def walk():
    labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
    out = {}
    for n in range(60):
        u, rows = g.node_terms_uid(OP, 0, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def term(rows, name, source):
    return next((r for r in rows if r["name"] == name and r["is_source"] == source), None)


def cls_of(uid, w):
    lab = w[uid][1] or ""
    if lab == "Property Node":
        return "Property"
    if lab == "Invoke Node":
        return "Invoke"
    if lab == "Index Array":
        return "IndexArray"
    return "SubVI" if lab.endswith(".vi") else "Function"


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def connect(su, sname, du, dname, branch=False, tag=""):
    w = walk()
    g.wire(OP, cls_of(su, w), idx(cls_of(su, w), su), sname, cls_of(du, w), idx(cls_of(du, w), du), dname, branch=branch)
    w = walk()
    a = term(w[su][2], sname, True)["wire"]; b = term(w[du][2], dname, False)["wire"]
    check(f"{tag}{sname!r} -> {dname!r} on both ends", a and a == b, f"{a}/{b}")
    return a == b and bool(a)


def make_ctl(uid, name, key, labels, indicator=False):
    w = walk(); n = w[uid][0]; t = term(w[uid][2], name, indicator)["i"]
    before = {l for _i, l, ind in g.fp_labels(OP) if ind == indicator}
    (g.create_indicator if indicator else g.create_control)(OP, n, t)
    new = [l for _i, l, ind in g.fp_labels(OP) if ind == indicator and l not in before]
    check(f"{'indicator' if indicator else 'control'} on {name!r}", bool(new), str(new))
    if new:
        labels[key] = new[-1]


def main():
    g._lv = None
    if os.path.exists(OP):
        os.remove(OP)
    md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.report_all(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
    print(f"copy: ExecState {g.exec_state(OP)} Function {len(g.report_all(OP, 'Function'))} Wire {len(g.report_all(OP, 'Wire'))}", flush=True)
    w = walk()
    by = {v[1]: u for u, v in w.items()}
    ovor = by.get("Open VI Object Reference")
    inv_rev = next(u for u, v in w.items() if term(v[2], "Revert VI", False))
    move = next(u for u, v in w.items() if term(v[2], "Move", False))
    pns = [u for u, v in w.items() if v[1] == "Property Node"]
    w_owner = term(w[move][2], "owner", False)["wire"]
    pn_tgt = next(u for u in pns if term(w[u][2], "Diagram", True)["wire"] == w_owner)
    pn_src = next(u for u in pns if u != pn_tgt)
    print(f"   OVOR {ovor}, Revert {inv_rev}, Move {move}, PN_src {pn_src}, PN_tgt {pn_tgt} (owner wire {w_owner})", flush=True)
    # S1
    w0 = len(g.report_all(OP, "Wire"))
    g.delete_object(OP, "Function", idx("Function", ovor), verify=False); g.remove_bad_wires_scripted(OP)
    w = walk()
    check("S1 OVOR deleted, Move.reference now unwired, owner wire intact",
          ovor not in w and term(w[move][2], "reference", False)["wire"] == 0 and term(w[move][2], "owner", False)["wire"] == w_owner,
          f"wires {w0} -> {len(g.report_all(OP, 'Wire'))}")
    # S2 error chain
    connect(pn_src, "error out", pn_tgt, "error in (no error)", tag="S2 ")
    # S3 Traverse
    sub0 = g.uids(OP, "SubVI"); g.drop_subvi(OP, TRAV, 0, (700, 900))
    trav = [u for u in g.uids(OP, "SubVI") if u not in sub0]
    check("S3 Traverse dropped", len(trav) == 1, str(trav))
    if len(trav) != 1:
        return 2
    trav = trav[0]
    connect(inv_rev, "reference out", trav, "VI Refnum", branch=True, tag="S3 ")
    labels = {}
    make_ctl(trav, "Class Name", "class_name", labels)
    # Run 1 (00:08): ExecState 0 with every wire on both ends. Review (...-movebyindex-fail1-execstate0): 'Traverse
    # Target' is a REQUIRED ring (0 = FP, 1 = BD) that was left unwired -> a control; the caller sets it to 1 (BD).
    make_ctl(trav, "Traverse Target", "traverse_target", labels)
    # S5 IA
    ia = g.build_index_array(OP, (950, 900))[-1]["uid"]
    connect(trav, "References", ia, "array", tag="S5 ")
    make_ctl(ia, "index", "index", labels)
    # S6 -> Move.reference
    connect(ia, "element", move, "reference", tag="S6 ")
    # S7 UID guard
    pn_uid = g.build_property(OP, "VI Server:GObject", [(P_UID, False)], (1200, 1050))[-1]["uid"]
    connect(ia, "element", pn_uid, "reference", branch=True, tag="S7 ")
    make_ctl(pn_uid, "UID", "selected_uid", labels, indicator=True)
    # S8 duplicate control
    make_ctl(move, "duplicate", "duplicate", labels)
    g.set_auto_error_handling(OP, False)
    es = g.exec_state(OP)
    try:
        bw = len(g.report_all(OP, "BrokenWire"))
    except Exception as e:
        bw = f"n/a ({str(e)[:60]})"
    print(f"   after (a): ExecState {es}, BrokenWire objects {bw}", flush=True)
    if es != 1:
        # declared plan B (review): the donor's Move invoke may retain a SUBCLASS reference type from the old OVOR
        # output -> a GObject wire is a class conflict. Recreate the invoke as GObject.Move (632A400) and rewire.
        print("   plan B: recreate the Move invoke as a GObject-class invoke", flush=True)
        w = walk()
        rows_m = w[move][2]
        w_pos = term(rows_m, "position", False)["wire"]; w_own = term(rows_m, "owner", False)["wire"]
        w_ein = term(rows_m, "error in (no error)", False)["wire"]; w_eout = term(rows_m, "error out", True)["wire"]
        src_of = lambda wid: next(((uu, r["name"]) for uu, (nn, ll, rr) in w.items() for r in rr if r["is_source"] and r["wire"] == wid and wid), None)
        sink_of = lambda wid: next(((uu, r["name"]) for uu, (nn, ll, rr) in w.items() for r in rr if not r["is_source"] and r["wire"] == wid and wid and uu != move), None)
        s_pos, s_own, s_ein, k_eout = src_of(w_pos), src_of(w_own), src_of(w_ein), sink_of(w_eout)
        print(f"   Move feeds: position<-{s_pos} owner<-{s_own} error in<-{s_ein}; error out->{k_eout}", flush=True)
        g.delete_object(OP, "Invoke", idx("Invoke", move), verify=False); g.remove_bad_wires_scripted(OP)
        move = g.build_invoke(OP, "VI Server:GObject", "632A400", (1400, 850))[-1]["uid"]
        w = walk(); names = [r["name"] for r in w[move][2]]
        print(f"   new Move invoke {move}: {names}", flush=True)
        connect(ia, "element", move, "reference", branch=True, tag="B ")
        if s_own:
            connect(s_own[0], s_own[1], move, "owner", tag="B ")
        if s_pos:
            connect(s_pos[0], s_pos[1], move, "position", tag="B ")
        if s_ein:
            connect(s_ein[0], s_ein[1], move, "error in (no error)", tag="B ")
        if k_eout:
            connect(move, "error out", k_eout[0], k_eout[1], tag="B ")
        labels.pop("duplicate", None); make_ctl(move, "duplicate", "duplicate", labels)
        es = g.exec_state(OP)
    check("S9 ExecState 1", es == 1, str(es))
    n_ok = sum(1 for _n, ok in PASS if ok)
    if n_ok == len(PASS) and len(labels) == 5:
        g.save(OP)
        with open(MAP_OUT, "w", encoding="utf-8") as f:
            json.dump(labels, f, indent=2)
        print(f"   saved; labels {labels}", flush=True)
    else:
        print(f"   NOT saved (labels {labels})", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == md5}", flush=True)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for k, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {k}", flush=True)
    return 0 if n_ok == len(PASS) and len(labels) == 5 else 1


if __name__ == "__main__":
    sys.exit(main())
