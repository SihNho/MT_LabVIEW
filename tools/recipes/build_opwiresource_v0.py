r"""build_opwiresource_v0.py - OpWireSource_v0.vi: name the SOURCE object of a wire, by wire index. This replaces the
180-object constant scan for the three unresolved reseed selector feeders (peer
archive/peer/2026-09-15-opconstvaluen-scan-three-selectors-missing.md §4: walk the wire, do not re-scan the constants):

  Traverse('Wire') -> Index Array[index] -> To More Specific Class(Wire, target from a Wire-typed seed control)
    -> Property(VI Server:Wire).'Terms[]'   6371003   (NI: element 0 is the SOURCE terminal when one exists)
    -> Index Array[0]                                  (index left unwired = element 0)
    -> Property(VI Server:Generic).'Owner'  6327806
    -> Property(VI Server:Generic).'ClassName' 6327803  + Property(VI Server:GObject).'UID' 632A813
  indicators: owner class name, owner uid, and the error out of each new node.

Donor: OpConstValue_v1.vi (it already carries Open VI Reference -> Traverse -> Index Array -> TMSC and the
OpReport_v3 identity outputs). Its Constant.Value byte-route tail (Property.Value, Flatten To String, Unflatten From
String, Bytes to Lowercase Hex String.vi) is DELETED first: once the TMSC target becomes Wire-typed, a Constant-class
property node on that wire would break the VI. The freed indicators stay on the panel, unwired (legal), unused.

Gates = predictions: the four tail nodes are found and deleted, ExecState 1 after the deletion; the Wire-typed seed
control appears and survives unwired; each new property node carries its SHORT-named source terminal
('Terms[]', 'Owner', 'ClassName', 'UID'); wire uids equal on both ends; ExecState 1 before the single COM save.

TEST (read-only on the main VI, MAIN md5 in an outer finally) - a cross-check against a MEASURED fact:
  wire 10850's source must be the constant uid 10739 of class DigitalNumericConstant
  (tools/bench/opconstvaluen_scan.log index 70, value I32 0). Then the three unresolved selector wires
  10312 (Or.y), 9806 (And.y), 10142 (Equal?.y) are read and their owner class/uid printed.

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opwiresource_v0.log -- py -u tools/recipes/build_opwiresource_v0.py [--test-only]
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
from build_opconstvalue_v1 import OP as OP_BASE, MAIN, com_preflight, lv_pid, fresh  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpWireSource_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_selectors.json")
KNOWN = (10850, 10739, "DigitalNumericConstant")     # wire, source uid, source class - measured 2026-09-15 06:00
TARGETS = {10312: "Or.y", 9806: "And.y", 10142: "Equal?.y (auto-reset period)"}
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def new_labels(dst, before, ind):
    return [l for _i, l, i in g.fp_labels(dst) if i == ind and l not in before]


def prop_node(cls, pid, short, pos):
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"B exactly one new Property node ({cls.split(':')[1]}.{short})", len(new) == 1, str(new))
    w = walk(OP, 0)
    must(f"B the node has '{short}' as a SOURCE", term(w[new[0]][2], short, True) is not None,
         str([(r["name"], r["is_source"]) for r in w[new[0]][2]]))
    return new[0]


def drop_node(uid, cls, tag):
    ids = [o["uid"] for o in g.report_all(OP, cls)]
    must(f"A {tag} is present as {cls}[{ids.index(uid) if uid in ids else '?'}]", uid in ids, f"{uid} not in {cls}")
    g.delete_object(OP, cls, ids.index(uid), verify=False)


def main():
    if "--test-only" in sys.argv:
        # run 4 was killed mid-COM-call by the bgrun deadline; a surviving instance holds that client's references,
        # so the rerun starts on a fresh one (project rule: a killed client's handles stay inside LabVIEW).
        fresh()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpWireSource_v0.vi and its labels exist from a passed build", os.path.exists(OP) and "ownercls" in labels, str(labels))
        return test(labels)
    must("S OpConstValue_v1.vi (donor with Traverse -> IA -> TMSC) exists", os.path.exists(OP_BASE))
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_BASE, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    labels = {}
    w = walk(OP, 0)
    tm = next(u for u, v in w.items() if term(v[2], "specific class reference", True))
    pnC = next(u for u, v in w.items() if term(v[2], "Value", True) and any(r["name"] == "reference" for r in v[2]))
    fl = next(u for u, v in w.items() if any(r["name"] == "anything" for r in v[2]))
    uf = next(u for u, v in w.items() if any(r["name"] == "binary string" for r in v[2]))
    hv = next(u for u, v in w.items() if any(r["name"] == "bytes" for r in v[2]) and term(v[2], "hex string", True))
    # A: remove the Constant.Value byte-route tail (the TMSC is about to carry a Wire, not a Constant)
    drop_node(hv, "SubVI", "Bytes to Lowercase Hex String.vi")
    drop_node(uf, "FlattenUnflattenString", "Unflatten From String")
    drop_node(fl, "FlattenString", "Flatten To String")
    drop_node(pnC, "Property", "Constant.Value node")
    g.remove_bad_wires_scripted(OP)
    w = walk(OP, 0)
    must("A the TMSC survived the deletion", tm in w, str(sorted(w)[:8]))
    es = g.exec_state(OP)
    must("A op runnable after the tail deletion (unwired indicators are legal)", es == 1, str(es))
    # B: the Wire-typed chain
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    pnT = prop_node("VI Server:Wire", "6371003", "Terms[]", (1500, 1200))
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    wt = walk(OP, 0); g.create_control(OP, wt[pnT][0], term(wt[pnT][2], "reference", False)["i"])
    labs = new_labels(OP, c0, False)
    must("B exactly one new control (Wire-typed seed) on the Terms[] node's 'reference'", len(labs) == 1, str(labs)); labels["seedW"] = labs[0]
    pw = {r["label"]: r for r in g.panel_wiring(OP)}; ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(pw[labels["seedW"]]["wire"]), verify=False)
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("B the Wire-typed control survives, unwired", pw[labels["seedW"]]["wire"] == 0)
    # retype the TMSC target: drop the old Constant seed's wire, wire the new control
    old_seed = next((l for l in pw if pw[l]["wire"] and pw[l]["wire"] == term(walk(OP, 0)[tm][2], "target class", False)["wire"]), None)
    must("C the old (Constant) seed control feeds TMSC.'target class'", old_seed is not None, str(sorted(pw)[:10]))
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(pw[old_seed]["wire"]), verify=False)
    g.wire_control(OP, [labels["seedW"]], "Function", fi("Function", tm), ["target class"])
    w = walk(OP, 0); pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("C Wire-typed control -> TMSC.'target class' on both ends",
         pw[labels["seedW"]]["wire"] and pw[labels["seedW"]]["wire"] == term(w[tm][2], "target class", False)["wire"])
    g.wire(OP, "Function", fi("Function", tm), "specific class reference", "Property", fi("Property", pnT), "reference")
    w = walk(OP, 0)
    a = term(w[tm][2], "specific class reference", True)["wire"]; b = term(w[pnT][2], "reference", False)["wire"]
    must("C TMSC -> Wire.Terms[] node 'reference' on both ends", a and a == b, f"{a}/{b}")
    ia0 = g.uids(OP, "IndexArray"); g.build_index_array(OP, (1900, 1200))
    ia = [u for u in g.uids(OP, "IndexArray") if u not in ia0]
    must("C exactly one new Index Array", len(ia) == 1, str(ia)); ia = ia[0]
    g.wire(OP, "Property", fi("Property", pnT), "Terms[]", "IndexArray", fi("IndexArray", ia), "array")
    w = walk(OP, 0)
    a = term(w[pnT][2], "Terms[]", True)["wire"]; b = term(w[ia][2], "array", False)["wire"]
    must("C Terms[] -> IndexArray.'array' on both ends (index left unwired = element 0 = the SOURCE terminal)", a and a == b, f"{a}/{b}")
    pnO = prop_node("VI Server:Generic", "6327806", "Owner", (2300, 1200))
    g.wire(OP, "IndexArray", fi("IndexArray", ia), "element", "Property", fi("Property", pnO), "reference")
    w = walk(OP, 0)
    a = term(w[ia][2], "element", True)["wire"]; b = term(w[pnO][2], "reference", False)["wire"]
    must("C IndexArray.'element' -> Generic.Owner node 'reference' on both ends", a and a == b, f"{a}/{b}")
    pnN = prop_node("VI Server:Generic", "6327803", "ClassName", (2700, 1200))
    g.wire(OP, "Property", fi("Property", pnO), "Owner", "Property", fi("Property", pnN), "reference")
    w = walk(OP, 0)
    a = term(w[pnO][2], "Owner", True)["wire"]; b = term(w[pnN][2], "reference", False)["wire"]
    must("C Owner -> ClassName node 'reference' on both ends", a and a == b, f"{a}/{b}")
    # run 2 (06:13): Create Indicator on a GObject.UID node fed by Generic.Owner returned NOTHING (no panel row, no
    # ControlTerminal, no error). Diagnosis under review (...-opwiresource-fail2-generic-owner-into-gobject-node):
    # Generic -> GObject is a DOWNCAST, so that wire is broken and the node is unusable. MEASURE it, then drop the
    # node: the source is identified by its CLASS here, and by the fed-wire scan of that class afterwards.
    es_before = g.exec_state(OP)
    pnU = prop_node("VI Server:GObject", "632A813", "UID", (2700, 1400))
    g.wire(OP, "Property", fi("Property", pnO), "Owner", "Property", fi("Property", pnU), "reference", branch=True)
    w = walk(OP, 0)
    a = term(w[pnO][2], "Owner", True)["wire"]; b = term(w[pnU][2], "reference", False)["wire"]
    es_after = g.exec_state(OP)
    # A/B/C as the reviewer asked: isolate the WIRE's effect before removing the node (step D, inserting a
    # Generic->GObject cast, needs a second To More Specific Class and is deferred - the identity comes from the
    # cast-free Constant->Connected Wire->UID scan instead).
    # run 3 (06:20): deleting "that wire" also cut Owner -> ClassName - a BRANCH is ONE wire object shared by both
    # sinks, so step C of the reviewer's sequence is not separable here; the node is removed directly instead.
    es_wireless = -1
    drop_node(pnU, "Property", "GObject.UID node (Generic downcast)")
    g.remove_bad_wires_scripted(OP)
    es_clean = g.exec_state(OP)
    print(f"OBSERVED downcast test: ExecState A(before wire)={es_before} B(after Generic.Owner -> GObject node)={es_after} "
          f"C(skipped: branch = one wire)={es_wireless} D(node deleted)={es_clean}; broken-wire diagnosis "
          f"{'CONFIRMED' if es_before == 1 and es_after == 0 else 'NOT confirmed'}", flush=True)
    must("C the op is runnable again once the downcast node is gone", es_clean == 1, f"{es_before}/{es_after}/{es_wireless}/{es_clean}")
    n_nodes = g.count(OP, "Node")
    must("D the diagram fits the 80-node walker (the walk is the node-index source)", n_nodes < 80, str(n_nodes))
    for uid, name, key in ((pnN, "ClassName", "ownercls"),
                           (pnT, "error out", "errT"), (pnO, "error out", "errO"), (pnN, "error out", "errU")):
        w = walk(OP, 0)
        # run 1 (06:07): the UID indicator produced NO NEW LABEL in a set-difference. Per peer
        # ...-opwiresource-fail1-uid-indicator-not-created: duplicate panel labels are LEGAL, so a label SET is not a
        # creation oracle - diff the panel rows by UID (a multiset), and keep the op's own return value.
        rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
        ct0 = g.uids(OP, "ControlTerminal")
        ret = g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
        rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
        new = [r for u, r in rows1.items() if u not in rows0]
        ct1 = [u for u in g.uids(OP, "ControlTerminal") if u not in ct0]
        if len(new) != 1:
            print(f"   D diag [{key}]: ret={str(ret)[:160]} new panel rows={new} new ControlTerminals={ct1} "
                  f"panel {len(rows0)}->{len(rows1)}", flush=True)
        must(f"D exactly one new panel object for '{name}' ({key})", len(new) == 1, f"{new} / terms {ct1}")
        must(f"D it is an INDICATOR with a unique label ({key})",
             new[0]["indicator"] and sum(1 for r in rows1.values() if r["label"] == new[0]["label"]) == 1,
             f"{new[0]['label']!r} indicator={new[0]['indicator']}")
        labels[key] = new[0]["label"]
    es = g.exec_state(OP)
    must("E op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read_wire(vi, labels, wire_uid, wires):
    idx = next((i for i, u in enumerate(wires) if u == wire_uid), None)
    if idx is None:
        print(f"   wire {wire_uid}: NOT in report(MAIN,'Wire') ({len(wires)} wires)", flush=True)
        return None
    vi.SetControlValue(labels["ownercls"], "POISON")
    vi.SetControlValue("UID", 0); vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", "Wire"); vi.SetControlValue("index", idx)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errT", "errO", "errU")) if x)
    uid = int(vi.GetControlValue("UID")); cls = vi.GetControlValue(labels["ownercls"])
    r = dict(wire=wire_uid, index=idx, wire_uid_readback=uid, owner_class=cls, err=err, errs=errs)
    print(f"   wire {wire_uid} (index {idx}): traversed uid={uid} -> owner class {cls!r:.34} {err[:30]} {errs[:60]}", flush=True)
    return r


def test(labels):
    vi = g.op(OP)
    try:
        # run 4 (06:25) timed out here: g.report() runs the reporter op ONCE PER OBJECT and the main VI holds
        # thousands of wires. uids() is report_all-based - ONE op run.
        t0 = time.time(); wires = g.uids(MAIN, "Wire")
        print(f"   uids(MAIN,'Wire') -> {len(wires)} wires in {time.time() - t0:.1f}s", flush=True)
        r = read_wire(vi, labels, KNOWN[0], wires)
        must("T0 the cross-check wire is in the report and reads without error", r is not None and not r["err"] and not r["errs"], str(r))
        must("T1 wire 10850's SOURCE is of the measured class (DigitalNumericConstant - uid 10739 per the scan)",
             r["wire_uid_readback"] == KNOWN[0] and r["owner_class"] == KNOWN[2], str(r))
        out = [r]
        for wu, what in TARGETS.items():
            rr = read_wire(vi, labels, wu, wires)
            if rr:
                rr["role"] = what; out.append(rr)
                print(f"SELECTOR: wire {wu} ({what}) source class = {rr['owner_class']} {rr['errs'][:40]}", flush=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        must("T2 all three unresolved selector wires resolved to a source CLASS (the object itself follows from a "
             "class-specific fed-wire scan)",
             sum(1 for x in out[1:] if x.get("owner_class") and x["owner_class"] != "POISON") == len(TARGETS),
             str([(x["wire"], x.get("owner_class")) for x in out[1:]]))
        n_ok = sum(1 for _n, p in B.PASS if p)
        print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
        return 0 if B.PASS and n_ok == len(B.PASS) else 1
    finally:
        finally_audit()


def finally_audit():
    same = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN)) == MAIN_BASE
    print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched since the script started", flush=True)
    B.PASS.append(("T(finally) main VI untouched", same))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True); sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True); sys.exit(1)
