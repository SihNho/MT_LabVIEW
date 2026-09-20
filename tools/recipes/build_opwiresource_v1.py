r"""build_opwiresource_v1.py - OpWireSource_v1.vi: the source object of a wire addressed BY UID, not by traverse index.

Why: run 5 of OpWireSource_v0 proved that an index from one reporter op does not select the same object in another
(uid 10850 sat at index 742 of `uids()` but the op's own Traverse returned uid 3512 there). Traverse order has no
documented contract (peer archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md), so the index is
removed from the addressing path entirely, as both reviews recommended:

  Open VI Reference('vi path') --branch--> `vi.lib\VIServer\UID to GObject Reference.vi`(UID control) -> GObject ref
     -> Property(VI Server:GObject).'UID'      632A813  -> indicator  (readback: must equal the requested UID)
     -> Property(VI Server:Generic).'ClassName' 6327803 -> indicator  (must be 'Wire' before anything is believed)
     -> To More Specific Class(Wire) -> Property(VI Server:Wire).'Terms[]' 6371003 -> Index Array[0]
        -> Property(VI Server:Generic).'Owner' 6327806 -> Property(VI Server:Generic).'ClassName' -> indicator

Donor: OpWireSource_v0.vi (Wire-typed seed, Terms[] -> IA -> Owner -> ClassName already built and saved). The old
Traverse -> Index Array -> TMSC input wire is replaced by the lookup output.

Reference hygiene (settled by peer ...-v1-lookup-terminal-census): `dup Owning VI` is a FLOW-THROUGH output, not a
new reference, and the `GObject` result is a child reference of the VI that is released when the VI reference the op
already closes is closed - so nothing extra needs closing here. The test still prints LabVIEW's handle-count delta
around the reads, because "nothing leaks" is a claim worth measuring.
The reviewer's crash caveat is respected: NO deliberately nonexistent UID is ever submitted.

Gates = predictions: the lookup VI drops and its terminals are censused (names printed, not guessed); a numeric UID
control is created from its UID input; the TMSC input comes from the lookup; ExecState 1 before the single save.
TEST: the measured cross-check first - UID 10850 must read back as 10850, class Wire, and its SOURCE owner must be
DigitalNumericConstant (the constant uid 10739 = I32 0 found by the value scan). Only then are 10312, 9806 and 10142
resolved. MAIN md5/mtime audited in an outer finally.

  py tools/bgrun.py --max-min 20 --log tools/bench/build_opwiresource_v1.log -- py -u tools/recipes/build_opwiresource_v1.py [--test-only]
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import MAIN, EX, com_preflight, lv_pid, fresh  # noqa: E402
from build_opwiresource_v0 import OP as OP_V0, KNOWN, TARGETS  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpWireSource_v1.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_v1_labels.json")
MAP_V0 = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_labels.json")
OUT_JSON = os.path.join(os.path.dirname(HERE), "bench", "opwiresource_selectors.json")
LOOKUP = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def handles():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return int(out) if out.isdigit() else -1


def prop_node(cls, pid, short, pos):
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"B exactly one new Property node ({cls.split(':')[1]}.{short})", len(new) == 1, str(new))
    w = walk(OP, 0)
    must(f"B the node has '{short}' as a SOURCE", term(w[new[0]][2], short, True) is not None,
         str([(r["name"], r["is_source"]) for r in w[new[0]][2]]))
    return new[0]


def add_indicator(uid, name, key, labels):
    w = walk(OP, 0)
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new = [r for u, r in rows1.items() if u not in rows0]
    must(f"D exactly one new panel object for '{name}' ({key})", len(new) == 1, str(new))
    must(f"D it is an INDICATOR with a unique label ({key})",
         new[0]["indicator"] and sum(1 for r in rows1.values() if r["label"] == new[0]["label"]) == 1, str(new[0]))
    labels[key] = new[0]["label"]


def main():
    if "--test-only" in sys.argv:
        fresh()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpWireSource_v1.vi and its labels exist from a passed build", os.path.exists(OP) and "uid_in" in labels, str(labels))
        return test(labels)
    must("S the v0 op and the lookup VI exist", os.path.exists(OP_V0) and os.path.exists(LOOKUP))
    with open(MAP_V0, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_V0, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    # the NI example's To More Specific Class (the donor for the fresh cast node), as in build_opconstvalue_v1
    ex_labels = {r["uid"]: r["label"] for r in g.node_labels(EX, 3)}
    ex_tmsc = next(u for u, l in ex_labels.items() if l == "To More Specific Class")
    i_tmsc = [o["uid"] for o in g.report_all(EX, "Function")].index(ex_tmsc)
    print(f"   example TMSC uid {ex_tmsc} = Function[{i_tmsc}]", flush=True)
    w = walk(OP, 0)
    tm = next(u for u, v in w.items() if term(v[2], "specific class reference", True))
    ovr = next(u for u, v in w.items() if term(v[2], "vi reference", True) or term(v[2], "VI Reference", True))
    print(f"   Open VI Reference node {ovr} terminals {[(r['i'], r['name'], 'src' if r['is_source'] else 'sink') for r in w[ovr][2]]}", flush=True)
    vr_name = "vi reference" if term(w[ovr][2], "vi reference", True) else "VI Reference"
    # A: drop the lookup VI and CENSUS its terminals (names are measured, never guessed)
    sub0 = g.uids(OP, "SubVI"); g.drop_subvi(OP, LOOKUP, 0, (900, 1600))
    lk = [u for u in g.uids(OP, "SubVI") if u not in sub0]
    must("A exactly one new SubVI (UID to GObject Reference.vi)", len(lk) == 1, str(lk)); lk = lk[0]
    w = walk(OP, 0)
    rows = [(r["i"], r["name"], "src" if r["is_source"] else "sink") for r in w[lk][2]]
    print(f"OBSERVED lookup VI terminals: {rows}", flush=True)
    # MEASURED run 1 (11:52): the VI's terminals are 'Owning VI' (sink), 'UID' (sink), 'GObject' (src),
    # 'dup Owning VI' (src), error in/out, plus unconnected connector-pane slots with EMPTY names.
    ref_in = term(w[lk][2], "Owning VI", False)
    uid_in = term(w[lk][2], "UID", False)
    out_t = term(w[lk][2], "GObject", True)
    # review ...-v1-lookup-terminal-census: match name AND direction, require exactly one of each, ignore the unnamed
    # connector-pane slots and the 'dup Owning VI' flow-through source (which is NOT a separate reference to close).
    def one(name, is_src):
        return sum(1 for r in w[lk][2] if r["name"] == name and r["is_source"] == is_src)
    must("A the lookup VI exposes exactly one 'Owning VI' sink, one 'UID' sink and one 'GObject' source",
         ref_in is not None and uid_in is not None and out_t is not None
         and one("Owning VI", False) == 1 and one("UID", False) == 1 and one("GObject", True) == 1, str(rows))
    srcs = [out_t]
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    g.wire(OP, "Function", fi("Function", ovr), vr_name, "SubVI", fi("SubVI", lk), ref_in["name"], branch=True)
    w = walk(OP, 0)
    a = term(w[ovr][2], vr_name, True)["wire"]; b = term(w[lk][2], ref_in["name"], False)["wire"]
    must("B Open VI Reference -> lookup's VI-reference input (branch) on both ends", a and a == b, f"{a}/{b}")
    rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
    w = walk(OP, 0); g.create_control(OP, w[lk][0], uid_in["i"])
    rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
    new = [r for u, r in rows1.items() if u not in rows0]
    must("B exactly one new control on the lookup's UID input", len(new) == 1, str(new))
    must("B it is a CONTROL with a unique label", (not new[0]["indicator"]) and sum(1 for r in rows1.values() if r["label"] == new[0]["label"]) == 1, str(new[0]))
    labels["uid_in"] = new[0]["label"]
    # C: replace the TMSC's input (Index Array element) with the lookup output
    w = walk(OP, 0)
    # run 2 (11:56) broke the VI here and the review (...-v1-fail2-execstate-zero-after-readbacks) named the cause:
    # that wire is a BRANCH - the Index Array element also feeds OpReport_v3's identity property nodes (UID,
    # Class Name 2, Position), so deleting it left THEIR required reference inputs unwired. The wire is therefore left
    # alone; the TMSC NODE is deleted instead (a wire survives losing one sink) and a fresh TMSC is copied in from the
    # NI example, fed by the lookup.
    es_log = [("lookup dropped, VI ref branched, UID control made", g.exec_state(OP))]
    must("C the op is still runnable with the lookup wired in", es_log[-1][1] == 1, str(es_log))
    w = walk(OP, 0)
    tw = next(u for u, v in w.items() if term(v[2], "Terms[]", True))
    tm_old = tm

    # The fresh cast node is copied in BEFORE anything is deleted: a broken VI cannot be saved, and copy_by_index
    # loads the target from disk. Its output is left unwired (legal) so the VI stays runnable across that save.
    def F(dst):
        wd = walk(dst, 0)
        new_fn = [u for u, v in wd.items() if u not in fn_before and term(v[2], "specific class reference", True)]
        must("C exactly one new To More Specific Class (by added uid)", len(new_fn) == 1, str(new_fn))
        tm2 = new_fn[0]
        fid = lambda cls, u: [o["uid"] for o in g.report_all(dst, cls)].index(u)
        # run 3 (12:04): the Wire-typed seed already feeds the OLD cast node, so this is a BRANCH, not a new wire
        # (the helper's own error said so). No new hypothesis here - the documented branch mechanism.
        g.wire_control(dst, [labels["seedW"]], "Function", fid("Function", tm2), ["target class"], branch=True)
        g.wire(dst, "SubVI", fid("SubVI", lk), out_t["name"], "Function", fid("Function", tm2), "reference")
        wd = walk(dst, 0); pw = {r["label"]: r for r in g.panel_wiring(dst)}
        must("C Wire-typed seed -> new TMSC.'target class'",
             pw[labels["seedW"]]["wire"] and pw[labels["seedW"]]["wire"] == term(wd[tm2][2], "target class", False)["wire"])
        a2 = term(wd[lk][2], out_t["name"], True)["wire"]; b2 = term(wd[tm2][2], "reference", False)["wire"]
        must("C lookup 'GObject' -> new TMSC.'reference' on both ends", a2 and a2 == b2, f"{a2}/{b2}")
        must("C the target is runnable with the new TMSC in place (its output still free)", g.exec_state(dst) == 1)
    fn_before = set(walk(OP, 0).keys())
    g.save(OP); g.close_panel(OP)          # runnable at this point; copy_by_index loads the target itself
    g.copy_by_index(EX, "Function", i_tmsc, OP, expect_uid=ex_tmsc, finish=F)
    g.open_panel(OP); time.sleep(0.8)
    es_log.append(("fresh TMSC copied, seed + lookup wired", g.exec_state(OP)))
    w = walk(OP, 0)
    tm = next(u for u, v in w.items() if u != tm_old and term(v[2], "specific class reference", True))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # now retire the OLD cast: delete the NODE (never its input wire - that wire also feeds OpReport_v3's identity
    # property nodes, and deleting it was exactly what broke run 2)
    g.delete_object(OP, "Function", fi("Function", tm_old), verify=False); g.remove_bad_wires_scripted(OP)
    es_log.append(("old TMSC node deleted (input wire kept for the report chain)", g.exec_state(OP)))
    g.wire(OP, "Function", fi("Function", tm), "specific class reference", "Property", fi("Property", tw), "reference")
    w = walk(OP, 0)
    a = term(w[tm][2], "specific class reference", True)["wire"]; b = term(w[tw][2], "reference", False)["wire"]
    must("C new TMSC -> Wire.'Terms[]' node 'reference' on both ends", a and a == b, f"{a}/{b}")
    es_log.append(("new TMSC -> Terms[] node", g.exec_state(OP)))
    must("C the op is runnable again after the cast swap", es_log[-1][1] == 1, str(es_log))
    # D: readback identity on the looked-up object (GObject -> Generic is an upcast; both are legal here)
    pnU = prop_node("VI Server:GObject", "632A813", "UID", (1500, 1600))
    es_log.append(("GObject.UID node placed (unwired)", g.exec_state(OP)))
    g.wire(OP, "SubVI", fi("SubVI", lk), srcs[0]["name"], "Property", fi("Property", pnU), "reference", branch=True)
    es_log.append(("lookup -> GObject.UID.reference", g.exec_state(OP)))
    pnC = prop_node("VI Server:Generic", "6327803", "ClassName", (1500, 1800))
    g.wire(OP, "SubVI", fi("SubVI", lk), srcs[0]["name"], "Property", fi("Property", pnC), "reference", branch=True)
    es_log.append(("lookup -> Generic.ClassName.reference", g.exec_state(OP)))
    w = walk(OP, 0)
    src_w = term(w[lk][2], srcs[0]["name"], True)["wire"]
    must("D both readback nodes share the lookup's output wire",
         term(w[pnU][2], "reference", False)["wire"] == src_w and term(w[pnC][2], "reference", False)["wire"] == src_w, str(src_w))
    print(f"OBSERVED ExecState per step: {es_log}", flush=True)
    es = es_log[-1][1]
    must("D the op is runnable with the readback nodes wired (no downcast)", es == 1,
         f"first drop to 0 at: {next((n for n, v in es_log if v != 1), 'none')}")
    add_indicator(pnU, "UID", "uid_back", labels)
    add_indicator(pnC, "ClassName", "cls_back", labels)
    add_indicator(lk, "error out", "errL", labels)
    es = g.exec_state(OP)
    must("E op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read_uid(vi, labels, wire_uid):
    for lab in (labels["ownercls"], labels["cls_back"]):
        vi.SetControlValue(lab, "POISON")
    vi.SetControlValue(labels["uid_back"], 0)
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue(labels["uid_in"], wire_uid)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errL", "errT", "errO", "errU")) if x)
    back = int(vi.GetControlValue(labels["uid_back"])); cls = vi.GetControlValue(labels["cls_back"])
    owner = vi.GetControlValue(labels["ownercls"])
    r = dict(wire=wire_uid, uid_back=back, wire_class=cls, owner_class=owner, err=err, errs=errs)
    print(f"   UID {wire_uid}: readback {back} class {cls!r:.18} -> SOURCE owner class {owner!r:.30} {err[:30]} {errs[:60]}", flush=True)
    return r


def test(labels):
    vi = g.op(OP)
    h0 = handles()
    try:
        r = read_uid(vi, labels, KNOWN[0])
        must("T0 the lookup resolves the requested UID (readback equal, class Wire, no error)",
             r["uid_back"] == KNOWN[0] and r["wire_class"] == "Wire" and not r["err"] and not r["errs"], str(r))
        must(f"T1 wire {KNOWN[0]}'s SOURCE is a {KNOWN[2]} (the measured constant uid {KNOWN[1]} = I32 0)",
             r["owner_class"] == KNOWN[2], str(r))
        out = [r]
        for wu, what in TARGETS.items():
            rr = read_uid(vi, labels, wu)
            rr["role"] = what; out.append(rr)
            print(f"SELECTOR: wire {wu} ({what}) source class = {rr['owner_class']}", flush=True)
        with open(OUT_JSON, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        must("T2 every target UID resolved to itself, class Wire, with a named source class",
             all(x["uid_back"] == x["wire"] and x["wire_class"] == "Wire" and x["owner_class"] not in ("", "POISON") for x in out[1:]),
             str([(x["wire"], x["uid_back"], x["wire_class"], x["owner_class"]) for x in out[1:]]))
        n_ok = sum(1 for _n, p in B.PASS if p)
        print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
        return 0 if B.PASS and n_ok == len(B.PASS) else 1
    finally:
        h1 = handles()
        print(f"   handle count {h0} -> {h1} (delta {h1 - h0}; the lookup's duplicate reference is not closed by this op)", flush=True)
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
