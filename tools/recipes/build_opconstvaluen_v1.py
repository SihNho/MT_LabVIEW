r"""build_opconstvaluen_v1.py - OpConstValueN_v1.vi = OpConstValueN_v0 (numeric constant reader, run 2 functional:
Value carries data through the DigitalNumericConstant-typed node) + the constant's WIRE identity, so the four reseed
selector constants (docs/stage2-assembly-step-e.md: wires 10850 Less?.y, 10312 Or.y, 9806 And.y, 10142 Equal?.y) can be
found among the main VI's 180 numeric constants by the wire they feed:
  TMSC --branch--> Property(Constant).'Terminal' (634AC04; Constant is a GObject, not a Node - review
  ...-opconstvaluen-v1-recipe-wire-identity) -> Property(Terminal).'Connected Wire' (634A000) -> Property(GObject).'UID'
  (632A813) -> indicator (the wire uid; an unwired constant gives an invalid wire ref -> 1055 on the Wire or UID node -
  measured, not assumed). CAVEAT (same review): a constant OUTSIDE diagram 43 reports the tunnel's OUTER wire, not the
  inner uid the step-E census read; the scan therefore also lists every wire uid so a tunnel crossing can be added if the
  four inner uids do not appear.
Predictions = gates: +1 Property(Constant) with a 'Terminal' source; +1 Property(Terminal) with a 'Wire' source (the
short name of Connected Wire); +1 Property(GObject) with a 'UID' source; wires on both ends; ExecState 1.
TEST (read-only on the main VI): DigitalNumericConstant[0] and [1]: wire uid > 0 or the Terminal error 1055 (unwired);
identity per read; a StringConstant index must fail the cast (1055/1057); MAIN md5 in finally. Then --scan: read every
numeric constant whose reporter `owner` matches --owner=<uid|name> (default: all 180), print (index, uid, wire uid, value,
text, repr) and write tools/bench/opconstvaluen_scan.json; report which indices feed the four selector wires.

  py tools/bgrun.py --max-min 15 --log tools/bench/build_opconstvaluen_v1.log -- py -u tools/recipes/build_opconstvaluen_v1.py [--test-only] [--scan [--owner=X]]
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
from build_opconstvalue_v1 import MAIN, com_preflight, lv_pid, fresh  # noqa: E402
from build_opconstvalue_v1b import decode_flat, NUM_TD  # noqa: E402
from build_opconstvalue_v1c import normalize_u8  # noqa: E402
from build_opconstvaluen_v0 import OP as OP0, MAP_OUT as MAP0, parse_num  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpConstValueN_v1.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconstvaluen_v1_labels.json")
SCAN_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconstvaluen_scan.json")
CLS_N = "VI Server:DigitalNumericConstant"
SELECTOR_WIRES = {10850: "Less?.y (lost threshold)", 10312: "Or.y", 9806: "And.y", 10142: "Equal?.y (auto-reset period)"}
# NumericConstant.Representation enum (NI doc, via peer ...-opconstvaluen-run2-typed-node-carries-data) -> flattened TD code
REPR_TD = {1: 0x0A, 3: 0x03, 6: 0x07}   # DBL, I32, U32 (others are logged, not gated, until measured)
MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))


def new_labels(dst, before, ind):
    return [l for _i, l, i in g.fp_labels(dst) if i == ind and l not in before]


def prop_node(cls, pid, name, pos):
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in pn0]
    must(f"B exactly one new Property node ({cls.split(':')[1]}.{name})", len(new) == 1, str(new))
    w = walk(OP, 0)
    must(f"B the node has '{name}' as a SOURCE", term(w[new[0]][2], name, True) is not None, str([(r['name'], r['is_source']) for r in w[new[0]][2]]))
    return new[0]


def main():
    if "--test-only" in sys.argv or "--scan" in sys.argv:
        g.reset(); com_preflight()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpConstValueN_v1.vi and its labels exist from a passed build", os.path.exists(OP) and "wire" in labels, str(labels))
        return scan(labels) if "--scan" in sys.argv else test(labels)
    with open(MAP0, encoding="utf-8") as f:
        labels = json.load(f)
    must("S OpConstValueN_v0.vi (run 2) exists with its labels", os.path.exists(OP0) and "text" in labels)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    fresh()
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP0, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    w = walk(OP, 0)
    tm = next(u for u, v in w.items() if term(v[2], "specific class reference", True))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # review ...-opconstvaluen-v1-recipe-wire-identity: Constant is a GObject, not a Node - use Constant.Terminal 634AC04
    # (one terminal, no Index Array); the DigitalNumericConstant ref from the TMSC upcasts into a Constant-typed node
    pnTm = prop_node("VI Server:Constant", "634AC04", "Terminal", (1500, 1800))
    g.wire(OP, "Function", fi("Function", tm), "specific class reference", "Property", fi("Property", pnTm), "reference", branch=True)
    w = walk(OP, 0)
    a = term(w[tm][2], "specific class reference", True)["wire"]; b = term(w[pnTm][2], "reference", False)["wire"]
    must("C TMSC -> Terminal node 'reference' (branch) on both ends", a and a == b, f"{a}/{b}")
    # run 1 (05:44): the 634A000 output terminal is the SHORT name 'Wire' (NAMES.md short-name pattern), not 'Connected Wire'
    pnW = prop_node("VI Server:Terminal", "634A000", "Wire", (2300, 1800))
    g.wire(OP, "Property", fi("Property", pnTm), "Terminal", "Property", fi("Property", pnW), "reference")
    w = walk(OP, 0)
    a = term(w[pnTm][2], "Terminal", True)["wire"]; b = term(w[pnW][2], "reference", False)["wire"]
    must("C Constant.'Terminal' -> Terminal node 'reference' on both ends", a and a == b, f"{a}/{b}")
    pnU = prop_node("VI Server:GObject", "632A813", "UID", (2700, 1800))
    g.wire(OP, "Property", fi("Property", pnW), "Wire", "Property", fi("Property", pnU), "reference")
    w = walk(OP, 0)
    a = term(w[pnW][2], "Wire", True)["wire"]; b = term(w[pnU][2], "reference", False)["wire"]
    must("C 'Wire' (Connected Wire) -> GObject node 'reference' on both ends", a and a == b, f"{a}/{b}")
    for uid, name, key in ((pnU, "UID", "wire"), (pnW, "error out", "errW"), (pnU, "error out", "errU")):
        w = walk(OP, 0)
        i0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
        labs = new_labels(OP, i0, True)
        must(f"D indicator on '{name}'", len(labs) == 1, str(labs)); labels[key] = labs[0]
    es = g.exec_state(OP)
    must("E op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def read(vi, labels, cls, i, man):
    for lab in (labels["text"], labels["hex"]):
        vi.SetControlValue(lab, "POISON")
    vi.SetControlValue(labels["u8"], []); vi.SetControlValue(labels["wire"], -1); vi.SetControlValue("UID", 0); vi.SetControlValue(labels["size"], False)
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:80]}"
    errV = g._err(vi, labels["errV"]) or ""; errT = g._err(vi, labels["errT"]) or ""
    errW = (g._err(vi, labels["errW"]) or "") + (g._err(vi, labels["errU"]) or "")     # unwired: 1055 may surface on either node
    uid = int(vi.GetControlValue("UID")); txt = vi.GetControlValue(labels["text"]); rep = vi.GetControlValue(labels["repr"])
    wire = int(vi.GetControlValue(labels["wire"]))
    b = normalize_u8(vi.GetControlValue(labels["u8"]))
    code, val, note = decode_flat(b) if b else (None, None, "no bytes")
    ident = uid == man[i]["uid"]
    rep_ok = (rep not in REPR_TD) or (REPR_TD[rep] == code)      # independent oracle for the TD code
    if not rep_ok:
        print(f"   !! Representation {rep} expects TD {REPR_TD[rep]:#x} but the variant carries {code!r}", flush=True)
    print(f"   {cls}[{i}] uid={uid} ident={ident} wire={wire} text={txt!r:.16} repr={rep!r} TD={code!r} rep_ok={rep_ok} val={val!r:.24} {note[:40]} "
          f"err={err[:30]!r} errV={errV[:30]!r} errT={errT[:30]!r} errW={errW[:40]!r}", flush=True)
    return dict(i=i, uid=uid, ident=ident, wire=wire, err=err, errV=errV, errT=errT, errW=errW, txt=txt, rep=rep, code=code, val=val, rep_ok=rep_ok)


def finally_audit():
    same = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN)) == MAIN_BASE
    print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched since the script started", flush=True)
    B.PASS.append(("T(finally) main VI untouched", same))


def test(labels):
    vi = g.op(OP)
    try:
        man = g.report(MAIN, "DigitalNumericConstant")
        rows = [read(vi, labels, "DigitalNumericConstant", i, man) for i in range(2)]
        must("T1 identity OK, Value-node error clear, values decode, TD matches Representation, for both reads",
             all(r["ident"] and not r["errV"] and r["code"] in NUM_TD and r["val"] is not None and r["rep_ok"] for r in rows))
        must("T2 each read yields a wire uid > 0 or the Terminal node reports 1055 (unwired)", all((r["wire"] > 0 and not r["errW"]) or "1055" in r["errW"] for r in rows), str([(r["wire"], r["errW"][:30]) for r in rows]))
        man_s = g.report(MAIN, "StringConstant")
        r = read(vi, labels, "StringConstant", 7, man_s)
        must("T3 negative control: a StringConstant fails the numeric cast (1055/1057)", any(c in r["errV"] or c in r["err"] for c in ("1055", "1057")))
        n_ok = sum(1 for _n, p in B.PASS if p)
        print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
        return 0 if B.PASS and n_ok == len(B.PASS) else 1
    finally:
        finally_audit()


def scan(labels):
    vi = g.op(OP)
    owner = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--owner=")), None)
    try:
        man = g.report(MAIN, "DigitalNumericConstant")
        idx = [i for i, r in enumerate(man) if owner is None or str(r.get("owner")) == owner]
        print(f"   scanning {len(idx)}/{len(man)} numeric constants (owner filter {owner!r})", flush=True)
        out = []
        for i in idx:
            r = read(vi, labels, "DigitalNumericConstant", i, man)
            r["owner"] = man[i].get("owner"); r["pos"] = man[i].get("pos"); out.append(r)
            if r["wire"] in SELECTOR_WIRES:
                print(f"SELECTOR: wire {r['wire']} {SELECTOR_WIRES[r['wire']]} <- constant uid {r['uid']} index {i}: value {r['val']!r} (TD {r['code']}) text {r['txt']!r} repr {r['rep']!r}", flush=True)
        with open(SCAN_OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        found = {r["wire"]: r for r in out if r["wire"] in SELECTOR_WIRES}
        print(f"SUMMARY selector constants found {sorted(found)} of {sorted(SELECTOR_WIRES)}; identity failures {sum(1 for r in out if not r['ident'])}", flush=True)
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
