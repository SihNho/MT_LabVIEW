r"""build_opwiresource_v2.py - OpWireSource_v2.vi = v1 plus the SOURCE OBJECT'S UID.

v1 names the class of a wire's source (`Generic.Owner` → `Generic.ClassName`) but not the object: `Generic` exposes no
UID, and wiring a Generic-typed reference straight into a GObject-class node is a downcast that breaks the VI
(measured 2026-09-15 06:2x). The fix is the documented one: put a To More Specific Class(GObject) in between.

  lookup(UID) → TMSC(Wire) → Wire.'Terms[]' → Index Array[0] → Generic.'Owner' ─┬→ Generic.'ClassName'  (v1)
                                                                               └→ TMSC2(GObject) → GObject.'UID'  (new)

Needed because Census B of the reseed work (archive/peer/2026-09-15-reseed-vi-design-cycle7.md) starts from the two
output wires of Case #5540 (5975, 5637) and must name the TUNNEL objects behind them by UID before their inner
terminals can be read per frame.

Build steps, each gated (and ExecState recorded after every mutation, the lesson of the v1 runs):
  A  a GObject-typed seed control: build a spare `GObject.UID` node, `create_control` on its `reference`, cut the wire
  B  copy a fresh To More Specific Class from the NI example (`copy_by_index`), wire seed → 'target class' (a BRANCH:
     the Wire-typed seed already feeds TMSC #1) and `Generic.Owner` → its 'reference'
  C  TMSC2 → the spare UID node's 'reference'; indicator on its 'UID'; error indicator too
TEST (read-only, MAIN md5 in an outer finally): the measured cross-check - wire 10850's source must still be class
`DigitalNumericConstant` AND now uid 10739 (the constant carrying I32 0, from opconstvaluen_scan.log). Then the two
Case #5540 output wires 5975 and 5637 are resolved to (class, uid), which is what Census B needs.

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opwiresource_v2.log -- py -u tools/recipes/build_opwiresource_v2.py [--test-only]
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
from build_opconstvalue_v1 import MAIN, EX, com_preflight, lv_pid, fresh  # noqa: E402
from build_opwiresource_v1 import OP as OP_V1, MAP_OUT as MAP_V1  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpWireSource_v2.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_v2_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "case5540_output_tunnels.json")
KNOWN = (10850, 10739, "DigitalNumericConstant")
CASE_OUT = {5975: "#5540 output tunnel -> x,y,z array (right shift register)",
            5637: "#5540 output tunnel -> Bead is good? array in (right shift register)"}
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def prop_node(cls, pid, short, pos):
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"exactly one new Property node ({cls.split(':')[1]}.{short})", len(new) == 1, str(new))
    w = walk(OP, 0)
    must(f"the node has '{short}' as a SOURCE", term(w[new[0]][2], short, True) is not None,
         str([(r["name"], r["is_source"]) for r in w[new[0]][2]]))
    return new[0]


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
        must("S OpWireSource_v2.vi and its labels exist from a passed build", os.path.exists(OP) and "owner_uid" in labels, str(labels))
        return test(labels)
    must("S the v1 op exists", os.path.exists(OP_V1))
    with open(MAP_V1, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_V1, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    es_log = [("copy of v1", g.exec_state(OP))]
    must("A the copied v1 op is runnable", es_log[-1][1] == 1, str(es_log))
    w = walk(OP, 0)
    pnO = next(u for u, v in w.items() if term(v[2], "Owner", True))
    ex_labels = {r["uid"]: r["label"] for r in g.node_labels(EX, 3)}
    ex_tmsc = next(u for u, l in ex_labels.items() if l == "To More Specific Class")
    i_tmsc = [o["uid"] for o in g.report_all(EX, "Function")].index(ex_tmsc)
    # A: the spare UID node + a GObject-typed seed control taken from its 'reference'
    pnU2 = prop_node("VI Server:GObject", "632A813", "UID", (2300, 1600))
    es_log.append(("spare GObject.UID node placed (unwired -> broken is expected)", g.exec_state(OP)))
    w = walk(OP, 0)
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    g.create_control(OP, w[pnU2][0], term(w[pnU2][2], "reference", False)["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new = [r for u, r in rows1.items() if u not in rows0]
    must("A exactly one new control (GObject-typed seed)", len(new) == 1, str(new))
    must("A it is a CONTROL with a unique label", (not new[0]["indicator"])
         and sum(1 for r in rows1.values() if r["label"] == new[0]["label"]) == 1, str(new[0]))
    labels["seedG"] = new[0]["label"]
    # run 1 (12:2x): the wire is NOT cut here. create_control leaves the control wired to the node, which keeps the VI
    # RUNNABLE - and it must be runnable to be saved, because copy_by_index loads the target FROM DISK and unsaved
    # edits are simply lost. The cut happens inside the copy's finish hook, where the VI ends runnable anyway.
    es_log.append(("spare node + GObject seed (still wired)", g.exec_state(OP)))
    must("A the op is runnable with the seed left wired", es_log[-1][1] == 1, str(es_log))
    pnU2_uid, seed_label = pnU2, labels["seedG"]
    # B: a second cast, copied from the NI example while the spare node is still unwired (the VI is broken here, so
    #    the copy's own finish hook must make it runnable again before its single save)
    def F(dst, added=None):
        # identity comes from copy_by_index's OWN before/after delta (`added`), taken in the same loaded universe -
        # never from a set captured before a reload (peer ...-opwiresource-v2-fail1-and-tunnelread-plan).
        wd = walk(dst, 0)
        add_uids = {o["uid"] for o in (added or [])}
        new_fn = [u for u, v in wd.items() if u in add_uids and term(v[2], "specific class reference", True)]
        must("B exactly one new To More Specific Class (from copy_by_index's own `added`)", len(new_fn) == 1,
             f"{new_fn} of added {sorted(add_uids)[:8]}")
        tm2 = new_fn[0]
        fid = lambda cls, u: [o["uid"] for o in g.report_all(dst, cls)].index(u)
        # cut the seed's auto-wire now (the VI ends runnable below, so this broken window never reaches a save)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        wsd = [o["uid"] for o in g.report_all(dst, "Wire")]
        if pwd[seed_label]["wire"] in wsd:
            g.delete_object(dst, "Wire", wsd.index(pwd[seed_label]["wire"]), verify=False)
        g.remove_bad_wires_scripted(dst)
        g.wire_control(dst, [labels["seedG"]], "Function", fid("Function", tm2), ["target class"], branch=True)
        g.wire(dst, "Property", fid("Property", pnO), "Owner", "Function", fid("Function", tm2), "reference", branch=True)
        g.wire(dst, "Function", fid("Function", tm2), "specific class reference", "Property", fid("Property", pnU2_uid), "reference")
        wd = walk(dst, 0); pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        must("B GObject seed -> TMSC2.'target class'",
             pwd[labels["seedG"]]["wire"] and pwd[labels["seedG"]]["wire"] == term(wd[tm2][2], "target class", False)["wire"])
        a = term(wd[pnO][2], "Owner", True)["wire"]; b = term(wd[tm2][2], "reference", False)["wire"]
        must("B Generic.'Owner' -> TMSC2.'reference' (branch) on both ends", a and a == b, f"{a}/{b}")
        a = term(wd[tm2][2], "specific class reference", True)["wire"]; b = term(wd[pnU2_uid][2], "reference", False)["wire"]
        must("B TMSC2 -> spare GObject.UID node 'reference' on both ends", a and a == b, f"{a}/{b}")
        must("B the target is runnable again (the downcast is now legal through the cast)", g.exec_state(dst) == 1)
    g.save(OP); g.close_panel(OP)          # RUNNABLE here - the edits must be on disk before copy_by_index loads it
    g.copy_by_index(EX, "Function", i_tmsc, OP, expect_uid=ex_tmsc, finish=F)
    g.open_panel(OP); time.sleep(0.8)
    es_log.append(("TMSC2 copied and wired", g.exec_state(OP)))
    add_indicator(pnU2_uid, "UID", "owner_uid", labels)
    add_indicator(pnU2_uid, "error out", "errG", labels)
    es_log.append(("indicators added", g.exec_state(OP)))
    print(f"OBSERVED ExecState per step: {es_log}", flush=True)
    must("C op runnable before the save", es_log[-1][1] == 1, str(es_log))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read_uid(vi, labels, wire_uid):
    for lab in (labels["ownercls"], labels["cls_back"]):
        vi.SetControlValue(lab, "POISON")
    vi.SetControlValue(labels["uid_back"], 0); vi.SetControlValue(labels["owner_uid"], 0)
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue(labels["uid_in"], wire_uid)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errL", "errT", "errO", "errU", "errG")) if x)
    r = dict(wire=wire_uid, uid_back=int(vi.GetControlValue(labels["uid_back"])),
             wire_class=vi.GetControlValue(labels["cls_back"]), owner_class=vi.GetControlValue(labels["ownercls"]),
             owner_uid=int(vi.GetControlValue(labels["owner_uid"])), err=err, errs=errs)
    print(f"   UID {wire_uid}: readback {r['uid_back']} class {r['wire_class']!r:.14} -> SOURCE "
          f"{r['owner_class']!r:.26} uid {r['owner_uid']} {err[:30]} {errs[:50]}", flush=True)
    return r


def test(labels):
    vi = g.op(OP)
    try:
        r = read_uid(vi, labels, KNOWN[0])
        must("T0 the lookup still resolves the cross-check wire (readback, class Wire, no error)",
             r["uid_back"] == KNOWN[0] and r["wire_class"] == "Wire" and not r["err"] and not r["errs"], str(r))
        must(f"T1 wire {KNOWN[0]}'s source is {KNOWN[2]} uid {KNOWN[1]} - class AND uid now match the value scan",
             r["owner_class"] == KNOWN[2] and r["owner_uid"] == KNOWN[1], str(r))
        out = [r]
        for wu, what in CASE_OUT.items():
            rr = read_uid(vi, labels, wu); rr["role"] = what; out.append(rr)
            print(f"CASE-OUT: wire {wu} ({what}) source = {rr['owner_class']} uid {rr['owner_uid']}", flush=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        must("T2 both #5540 output wires resolved to a named source object with a uid",
             all(x["uid_back"] == x["wire"] and x["owner_uid"] and x["owner_class"] not in ("", "POISON") for x in out[1:]),
             str([(x["wire"], x["owner_class"], x["owner_uid"]) for x in out[1:]]))
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
