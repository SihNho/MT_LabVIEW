r"""build_opconstvaluen_v0.py - OpConstValueN_v0.vi: the NUMERIC-constant reader (discriminators 2 + 3 of
archive/peer/2026-09-15-opconstvalue-numeric-void-variant.md). OpConstValue_v1 (Constant-typed node) returns a void
variant for every DigitalNumericConstant. This op is a COPY of OpConstValue_v1 whose reference chain is retyped:
  1. build_property('VI Server:DigitalNumericConstant', [Value 634AC00, Numeric Text 634D004, Representation 5DCFC00])
     -> pnN; create_control on its `reference` -> a DigitalNumericConstant-typed control; cut that wire
  2. delete the wire Constant-seed -> TMSC.'target class'; wire the new control -> TMSC.'target class'
     (the TMSC output now carries DigitalNumericConstant; it still feeds the old Constant PN by upcast)
  3. TMSC.'specific class reference' --branch--> pnN.'reference'
  4. delete the wire ConstantPN.'Value' -> Flatten.'anything'; wire pnN.'Value' -> Flatten.'anything'
     (so the byte route now carries the DigitalNumericConstant-typed node's variant = discriminator 2)
  5. build_property('VI Server:Text', [Text 632D800]) -> pnT; pnN.'Numeric Text' -> pnT.'reference';
     indicators on pnT.'Text' and pnN.'Representation' (= discriminator 3, textual fallback)
  6. ExecState 1 -> save -> labels json (tools/bench/opconstvaluen_labels.json)
Gates are the predictions (counts by added uid, wire uids on both ends). The op becomes numeric-only (the cast to
DigitalNumericConstant errors on a StringConstant) - OpConstValue_v1 stays the string reader.
TEST (read-only on the main VI, identity per read, MAIN md5 in finally): DigitalNumericConstant[0..5] ->
  T1 Text.Text is a non-empty numeric text for all 6 (parsable as int/float after stripping);
  T2 report whether the DigitalNumericConstant-typed node's Value variant is void (TD 0) or carries data - and if it
     carries data, the decoded value must equal the parsed text;
  T3 a StringConstant index must ERROR (cast 1057) - the negative control.

  py tools/bgrun.py --max-min 15 --log tools/bench/build_opconstvaluen_v0.log -- py -u tools/recipes/build_opconstvaluen_v0.py [--test-only]
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
from build_opconstvalue_v1 import OP as OP1, MAIN, MAP_OUT as MAP1, com_preflight, lv_pid, fresh  # noqa: E402
from build_opconstvalue_v1b import decode_flat, NUM_TD  # noqa: E402
from build_opconstvalue_v1c import normalize_u8  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP = os.path.join(g.CLAUDEDEV, "OpConstValueN_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opconstvaluen_labels.json")
CLS_N = "VI Server:DigitalNumericConstant"


def new_labels(dst, before, ind):
    return [l for _i, l, i in g.fp_labels(dst) if i == ind and l not in before]


def main():
    with open(MAP1, encoding="utf-8") as f:
        labels = json.load(f)
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    if "--test-only" in sys.argv:
        g.reset(); com_preflight()
        with open(MAP_OUT, encoding="utf-8") as f:
            labels = json.load(f)
        must("S OpConstValueN_v0.vi and its labels exist from a passed build", os.path.exists(OP) and "text" in labels, str(labels))
        return test(labels)
    fresh()     # run 1 (05:26) stopped mid-edit: the dirty OpConstValueN_v0 must not survive in memory into the next build
    must("S OpConstValue_v1.vi (v1c, byte route) exists with its labels", os.path.exists(OP1) and all(k in labels for k in ("seed", "value", "hex", "u8", "size")))
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(OP1, OP); time.sleep(0.3)
    g.open_panel(OP); time.sleep(0.8)
    w = walk(OP, 0)
    tm = next(u for u, v in w.items() if term(v[2], "specific class reference", True))
    pnC = next(u for u, v in w.items() if term(v[2], "Value", True) and any(r["name"] == "reference" for r in v[2]))
    fl = next(u for u, v in w.items() if any(r["name"] == "anything" for r in v[2]))
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    w_seed = pw[labels["seed"]]["wire"]
    must("A the Constant seed feeds TMSC.'target class'", w_seed and w_seed == term(w[tm][2], "target class", False)["wire"], str(w_seed))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # 1. THREE DigitalNumericConstant-typed nodes (review ...-opconstvaluen-v0-recipe: a multi-property node stops at
    #    the first failing element, so Value / Numeric Text / Representation must not share an error chain) + the
    #    typed control from the first one's `reference`
    def prop_node(pid, name, pos):
        pn0 = g.uids(OP, "Property")
        g.build_property(OP, CLS_N, [(pid, False)], pos)
        new = [u for u in g.uids(OP, "Property") if u not in pn0]
        must(f"B exactly one new Property node ({name})", len(new) == 1, str(new))
        w = walk(OP, 0)
        must(f"B the node has '{name}' as a SOURCE", term(w[new[0]][2], name, True) is not None, str([(r['name'], r['is_source']) for r in w[new[0]][2]]))
        return new[0]
    pnN = prop_node("634AC00", "Value", (1500, 1200))
    # census tools/bench/census_dnc_property_ids.log (05:34): 634D007 -> terminal 'NumText' (the wiki's 634D004 is RadixVis)
    pnX = prop_node("634D007", "NumText", (1500, 1400))
    pnR = prop_node("5DCFC00", "Representation", (1500, 1600))
    w = walk(OP, 0)
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    g.create_control(OP, w[pnN][0], term(w[pnN][2], "reference", False)["i"])
    labs = new_labels(OP, c0, False)
    must("B exactly one new control (DigitalNumericConstant-typed) on pnN.'reference'", len(labs) == 1, str(labs)); labels["seedN"] = labs[0]
    pw = {r["label"]: r for r in g.panel_wiring(OP)}; ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(pw[labels["seedN"]]["wire"]), verify=False)
    # 2. retype the TMSC target
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(w_seed), verify=False)
    g.wire_control(OP, [labels["seedN"]], "Function", fi("Function", tm), ["target class"])
    w = walk(OP, 0); pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("C new control -> TMSC.'target class' on both ends", pw[labels["seedN"]]["wire"] and pw[labels["seedN"]]["wire"] == term(w[tm][2], "target class", False)["wire"])
    must("C the old Constant seed is now free", pw[labels["seed"]]["wire"] == 0)
    # 3. TMSC -> the three nodes' reference (branches: it already feeds the Constant PN)
    for pn, nm in ((pnN, "Value"), (pnX, "NumText"), (pnR, "Representation")):
        g.wire(OP, "Function", fi("Function", tm), "specific class reference", "Property", fi("Property", pn), "reference", branch=True)
        w = walk(OP, 0)
        a = term(w[tm][2], "specific class reference", True)["wire"]; b = term(w[pn][2], "reference", False)["wire"]; c = term(w[pnC][2], "reference", False)["wire"]
        must(f"C TMSC -> {nm} node 'reference' (branch) shares the uid with TMSC -> ConstantPN.'reference'", a and a == b == c, f"{a}/{b}/{c}")
    # 4. the byte route now carries pnN.Value
    w_val = term(w[pnC][2], "Value", True)["wire"]
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(w_val), verify=False); g.remove_bad_wires_scripted(OP)
    w = walk(OP, 0)
    must("D ConstantPN.'Value' -> Flatten/indicator wire removed", term(w[fl][2], "anything", False)["wire"] == 0)
    g.wire(OP, "Property", fi("Property", pnN), "Value", "FlattenString", fi("FlattenString", fl), "anything")
    w = walk(OP, 0)
    a = term(w[pnN][2], "Value", True)["wire"]; b = term(w[fl][2], "anything", False)["wire"]
    must("D pnN.'Value' -> Flatten.'anything' on both ends", a and a == b, f"{a}/{b}")
    # 5. Numeric Text -> Text.Text; indicators
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, "VI Server:Text", [("632D800", False)], (2000, 1200))
    pnT = [u for u in g.uids(OP, "Property") if u not in pn0]
    must("E exactly one new Property node (Text)", len(pnT) == 1, str(pnT)); pnT = pnT[0]
    g.wire(OP, "Property", fi("Property", pnX), "NumText", "Property", fi("Property", pnT), "reference")
    w = walk(OP, 0)
    a = term(w[pnX][2], "NumText", True)["wire"]; b = term(w[pnT][2], "reference", False)["wire"]
    must("E pnX.'NumText' -> pnT.'reference' on both ends", a and a == b, f"{a}/{b}")
    for uid, name, key in ((pnT, "Text", "text"), (pnR, "Representation", "repr"), (pnT, "error out", "errT"), (pnN, "error out", "errV")):
        w = walk(OP, 0)
        i0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, w[uid][0], term(w[uid][2], name, True)["i"])
        labs = new_labels(OP, i0, True)
        must(f"E indicator on '{name}'", len(labs) == 1, str(labs)); labels[key] = labs[0]
    es = g.exec_state(OP)
    must("F op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def parse_num(s):
    t = s.strip().replace(",", "")
    try:
        return int(t)
    except ValueError:
        return float(t)


MAIN_BASE = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN))   # baseline at import = before anything


def test(labels):
    vi = g.op(OP)
    try:
        return _test(vi, labels)
    finally:
        same = (hashlib.md5(open(MAIN, "rb").read()).hexdigest(), os.path.getmtime(MAIN)) == MAIN_BASE
        print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched since the script started", flush=True)
        B.PASS.append(("T(finally) main VI untouched", same))


def _test(vi, labels):
    def read(cls, i, man):
        for lab in (labels["text"], labels["hex"]):
            vi.SetControlValue(lab, "POISON")
        vi.SetControlValue(labels["u8"], [])
        try:
            vi.SetControlValue(labels["repr"], 0)     # enum indicator: reset to item 0 (the read must change it or the log shows it)
        except Exception as e:
            print(f"   (repr reset declined: {str(e)[:60]})", flush=True)
        vi.SetControlValue("UID", 0); vi.SetControlValue(labels["size"], False)
        vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
        try:
            g._run(vi); err = g._err(vi, "error out") or ""
        except Exception as e:
            err = f"EXC {str(e)[:80]}"
        errV = g._err(vi, labels["errV"]) or ""; errT = g._err(vi, labels["errT"]) or ""
        uid = int(vi.GetControlValue("UID")); txt = vi.GetControlValue(labels["text"]); rep = vi.GetControlValue(labels["repr"])
        b = normalize_u8(vi.GetControlValue(labels["u8"]))
        code, val, note = decode_flat(b) if b else (None, None, "no bytes")
        ident = uid == man[i]["uid"]
        print(f"   {cls}[{i}] uid={uid} ident={ident} text={txt!r:.24} repr={rep!r} bytes={len(b) if b else None} TD={code!r} val={val!r:.24} {note[:50]} "
              f"err={err[:40]!r} errV={errV[:40]!r} errT={errT[:40]!r}", flush=True)
        return dict(ident=ident, err=err, errV=errV, errT=errT, txt=txt, rep=rep, code=code, val=val)
    man = g.report(MAIN, "DigitalNumericConstant")
    classes = sorted({r["class"] for r in man})
    must("T0 the reporter's actual classes under 'DigitalNumericConstant' are exactly that class", classes == ["DigitalNumericConstant"], str(classes))
    rows = [read("DigitalNumericConstant", i, man) for i in range(6)]
    must("T1 all 6 numeric reads: identity OK, op error out clear, Value-node error clear", all(r["ident"] and not r["err"] and not r["errV"] for r in rows))
    must("T1 all 6 'Numeric Text' -> Text.Text are non-empty strings (display text, grammar logged, not asserted)",
         all(isinstance(r["txt"], str) and r["txt"] not in ("", "POISON") for r in rows), str([r["txt"] for r in rows]))
    texts = []
    for r in rows:
        try:
            texts.append(parse_num(r["txt"]))
        except Exception:
            texts.append(None)
    print(f"OBSERVED: texts {[r['txt'] for r in rows]} parsed {texts} repr {[r['rep'] for r in rows]}", flush=True)
    void = [r["code"] == 0 for r in rows]; data = [r["code"] in NUM_TD and r["val"] is not None for r in rows]
    print(f"OBSERVED: DigitalNumericConstant-typed Value variant: void={void} data={data}", flush=True)
    if any(data):
        must("T2 every numeric Value that carries data equals its parsed text", all((not d) or (t is not None and r["val"] == t) for d, r, t in zip(data, rows, texts)), str([(r["val"], t) for r, t in zip(rows, texts)]))
    else:
        print("   T2: the DigitalNumericConstant-typed node's Value is void too (discriminator 2 -> read-side, not static typing)", flush=True)
    man_s = g.report(MAIN, "StringConstant")
    r = read("StringConstant", 7, man_s)
    # run 2 (05:41): the failed cast surfaces as error 1055 (invalid reference) on the typed property nodes, whose error
    # outs are separate indicators (errV/errT); the op's own error out stays clear. Either code on either node = the cast failed.
    must("T3 negative control: a StringConstant through the numeric cast fails (1055/1057 on the typed nodes)",
         any(c in r["errV"] or c in r["errT"] or c in r["err"] for c in ("1055", "1057")), f"{r['errV'][:60]!r} {r['err'][:40]!r}")
    n_ok = sum(1 for _n, p in B.PASS if p)
    print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
    return 0 if B.PASS and n_ok == len(B.PASS) else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True); sys.exit(1)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True); sys.exit(1)
