r"""build_opconstwire_v0.py - OpConstWire_v0.vi: for ANY constant class, the wire it feeds. The numeric-typed reader
(OpConstValueN_v1) found only 1 of the 4 reseed selector feeders because it can cast only DigitalNumericConstant; the
remaining three wires (10312 Or.y, 9806 And.y - Boolean terminals - and 10142 Equal?.y) need a class-agnostic pass.

Built from OpConstValue_v1.vi (whose TMSC target class is the BASE Constant seed, so every constant subclass casts) by
adding the identity chain measured in OpConstValueN_v1:
  TMSC --branch--> Property(VI Server:Constant).'Terminal' (634AC04) -> Property(VI Server:Terminal).'Wire' (634A000,
  short name of Connected Wire) -> Property(VI Server:GObject).'UID' (632A813) -> indicator; error indicators on the
  Terminal/Wire/UID nodes (an unwired constant reports 1055 there, measured).
Gates = predictions: one new Property node per step with the short-named SOURCE terminal; wire uids equal on both ends;
ExecState 1 before the single COM save.
TEST (read-only on the main VI, identity per read, MAIN md5 in an outer finally): the constant already measured through
the numeric op - DigitalNumericConstant uid 10739 - must report wire 10850 through THIS base-typed op too (cross-check
of the two ops); a StringConstant must report a wire uid or 1055 without a cast error (the base cast accepts it).
--scan: report(MAIN, 'Constant') - if the Traverse filter is inclusive this enumerates EVERY constant class - and for
each index print (index, uid, class, wire); flag any that feeds 10850/10312/9806/10142; write tools/bench/opconstwire_scan.json.

  py tools/bgrun.py --max-min 60 --log tools/bench/build_opconstwire_v0.log -- py -u tools/recipes/build_opconstwire_v0.py [--test-only] [--scan] [--class=Constant]
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
OP = os.path.join(g.CLAUDEDEV, "OpConstWire_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconstwire_labels.json")
SCAN_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconstwire_scan.json")
SELECTOR_WIRES = {10850: "Less?.y (lost threshold, measured = I32 0)", 10312: "Or.y", 9806: "And.y", 10142: "Equal?.y"}
KNOWN = (10739, 10850)      # the cross-check pair measured by OpConstValueN_v1 (opconstvaluen_scan.log index 70)
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def new_labels(dst, before, ind):
    return [l for _i, l, i in g.fp_labels(dst) if i == ind and l not in before]


def prop_node(cls, pid, short, pos):
    """A property node gated on the SHORT name of its data terminal (peer …-v1-fail1-connected-wire-short-name:
    the menu long name is never the terminal name)."""
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"B exactly one new Property node ({cls.split(':')[1]}.{short})", len(new) == 1, str(new))
    w = walk(OP, 0)
    must(f"B the node has '{short}' as a SOURCE", term(w[new[0]][2], short, True) is not None,
         str([(r["name"], r["is_source"]) for r in w[new[0]][2]]))
    return new[0]


def main():
    if any(a in sys.argv for a in ("--test-only", "--scan")):
        g.reset(); com_preflight()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpConstWire_v0.vi and its labels exist from a passed build", os.path.exists(OP) and "wire" in labels, str(labels))
        return scan(labels) if "--scan" in sys.argv else test(labels)
    must("S OpConstValue_v1.vi (base-Constant byte route) exists", os.path.exists(OP_BASE))
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP_BASE, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    labels = {}
    w = walk(OP, 0)
    tm = next(u for u, v in w.items() if term(v[2], "specific class reference", True))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    pnT = prop_node("VI Server:Constant", "634AC04", "Terminal", (1500, 1800))
    g.wire(OP, "Function", fi("Function", tm), "specific class reference", "Property", fi("Property", pnT), "reference", branch=True)
    w = walk(OP, 0)
    a = term(w[tm][2], "specific class reference", True)["wire"]; b = term(w[pnT][2], "reference", False)["wire"]
    must("C TMSC -> Constant.Terminal node 'reference' (branch) on both ends", a and a == b, f"{a}/{b}")
    pnW = prop_node("VI Server:Terminal", "634A000", "Wire", (1900, 1800))
    g.wire(OP, "Property", fi("Property", pnT), "Terminal", "Property", fi("Property", pnW), "reference")
    w = walk(OP, 0)
    a = term(w[pnT][2], "Terminal", True)["wire"]; b = term(w[pnW][2], "reference", False)["wire"]
    must("C Constant.'Terminal' -> Terminal node 'reference' on both ends", a and a == b, f"{a}/{b}")
    pnU = prop_node("VI Server:GObject", "632A813", "UID", (2300, 1800))
    g.wire(OP, "Property", fi("Property", pnW), "Wire", "Property", fi("Property", pnU), "reference")
    w = walk(OP, 0)
    a = term(w[pnW][2], "Wire", True)["wire"]; b = term(w[pnU][2], "reference", False)["wire"]
    must("C Terminal.'Wire' -> GObject node 'reference' on both ends", a and a == b, f"{a}/{b}")
    for uid, name, key in ((pnU, "UID", "wire"), (pnT, "error out", "errT"), (pnW, "error out", "errW"), (pnU, "error out", "errU")):
        w = walk(OP, 0)
        i0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
        labs = new_labels(OP, i0, True)
        must(f"D indicator on '{name}' ({key})", len(labs) == 1, str(labs)); labels[key] = labs[0]
    es = g.exec_state(OP)
    must("E op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read(vi, labels, cls, i, man):
    vi.SetControlValue(labels["wire"], -1); vi.SetControlValue("UID", 0); vi.SetControlValue("Class Name 2", "POISON")
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errs = " ".join(x for x in (g._err(vi, labels[k]) or "" for k in ("errT", "errW", "errU")) if x)
    uid = int(vi.GetControlValue("UID")); cls2 = vi.GetControlValue("Class Name 2"); wire = int(vi.GetControlValue(labels["wire"]))
    ident = uid == man[i]["uid"]
    return dict(i=i, uid=uid, cls=cls2, ident=ident, wire=wire, err=err, errs=errs)


def finally_audit():
    same = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN)) == MAIN_BASE
    print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched since the script started", flush=True)
    B.PASS.append(("T(finally) main VI untouched", same))


def test(labels):
    vi = g.op(OP)
    try:
        man = g.report(MAIN, "DigitalNumericConstant")
        idx = next((i for i, r in enumerate(man) if r["uid"] == KNOWN[0]), None)
        must("T0 the cross-check constant uid 10739 is in the numeric report", idx is not None, str(KNOWN))
        r = read(vi, labels, "DigitalNumericConstant", idx, man)
        print(f"   cross-check {r}", flush=True)
        must("T1 the base-typed op reports the SAME wire for uid 10739 as the numeric-typed op (10850)",
             r["ident"] and r["wire"] == KNOWN[1] and not r["err"], f"{r['wire']} vs {KNOWN[1]}")
        man_s = g.report(MAIN, "StringConstant")
        r = read(vi, labels, "StringConstant", 7, man_s)
        print(f"   string read {r}", flush=True)
        must("T2 a StringConstant passes the BASE cast: identity OK and either a wire uid or 1055, no op error",
             r["ident"] and not r["err"] and (r["wire"] > 0 or "1055" in r["errs"]), f"{r['wire']} {r['errs'][:60]}")
        n_ok = sum(1 for _n, p in B.PASS if p)
        print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
        return 0 if B.PASS and n_ok == len(B.PASS) else 1
    finally:
        finally_audit()


def scan(labels):
    vi = g.op(OP)
    cls = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--class=")), "Constant")
    try:
        man = g.report(MAIN, cls)
        classes = sorted({r["class"] for r in man})
        print(f"   report(MAIN, {cls!r}) -> {len(man)} objects; actual classes {classes}", flush=True)
        out = []
        for i in range(len(man)):
            r = read(vi, labels, cls, i, man)
            r["pos"] = man[i].get("pos"); out.append(r)
            if r["wire"] in SELECTOR_WIRES:
                print(f"SELECTOR: wire {r['wire']} {SELECTOR_WIRES[r['wire']]} <- {r['cls']} uid {r['uid']} index {i}", flush=True)
            elif i % 25 == 0 or not r["ident"]:
                print(f"   [{i}/{len(man)}] uid={r['uid']} cls={r['cls']!r:.26} ident={r['ident']} wire={r['wire']} {r['errs'][:40]}", flush=True)
        with open(SCAN_OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        found = {r["wire"]: r for r in out if r["wire"] in SELECTOR_WIRES}
        print(f"SUMMARY classes {classes}; selector wires found {sorted(found)} of {sorted(SELECTOR_WIRES)}; "
              f"identity failures {sum(1 for r in out if not r['ident'])}; wired {sum(1 for r in out if r['wire'] > 0)}/{len(out)}", flush=True)
        for wr, r in sorted(found.items()):
            print(f"   {wr} <- {r['cls']} uid {r['uid']} index {r['i']}", flush=True)
        return 0 if len(found) == len(SELECTOR_WIRES) else 1
    finally:
        finally_audit()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True); sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True); sys.exit(1)
