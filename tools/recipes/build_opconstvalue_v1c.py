r"""build_opconstvalue_v1c.py - lossless byte readback for OpConstValue_v1.vi. The v1b `data string` BSTR arrives
code-page (cp949) decoded and a string route can never be proven lossless (peer archive/peer/2026-09-15-opconstvalue-v1b-bstr-codepage.md);
the fix is bytes: Flatten.data string -> Unflatten From String (type = U8[], `data includes array or string size?` = F,
i.e. String To Byte Array, for which the Erdos Miller library has no creator) -> U8[] indicator (SAFEARRAY VT_UI1) and,
through the stock vi.lib `Bit Manipulation\Bytes to Lowercase Hex String.vi`, an ASCII hex indicator - two independent
lossless readbacks that must agree.
Census facts (tools/bench/census_hexstring_vi.log, census_unflatten_terms.log): hex VI terminals `bytes` (sink, U8[]:
a string wire breaks it) / `hex string` (src); Unflatten (creator OpBuildUnflatten_v0, class FlattenUnflattenString)
sinks `binary string`, `type`, `data includes array or string size? (T)`, `byte order (0:big-endian, network order)`,
`error in (no error)`; sources `value`, `rest of the binary string`, `error out`.

Build (in place on the saved op, panel open, one COM save; gates = predictions):
  A  +1 SubVI (hex VI); create_control on its `bytes` -> U8[] control; cut that wire (control stays, wire 0)
  B  +1 FlattenUnflattenString; Flatten.'data string' --branch--> 'binary string' (same wire uid both ends)
  C  U8[] control -> 'type' (wire_control); create_control on 'data includes array or string size? (T)' -> Boolean control
  D  Unflatten.'value' -> hexVI.'bytes' (wire uid both ends); indicators on hexVI.'hex string' and Unflatten.'value'
  E  ExecState 1 -> save -> labels json
TEST (typed, read-only on the main VI; size control set FALSE per run; result indicators poisoned; identity per read):
  StringConstant[7]: hex == u8 bytes, contains b'img%05d.tif', HYPOTHESIS-A framing decodes it (TD 0x30);
  DigitalNumericConstant[0..5]: hex == u8 bytes, each decodes from a numeric TD (consumed exactly), not all identical;
  MAIN md5/mtime unchanged.

  py tools/bgrun.py --max-min 15 --log tools/bench/build_opconstvalue_v1c.log -- py -u tools/recipes/build_opconstvalue_v1c.py [--test-only]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import OP, MAIN, MAP_OUT, com_preflight, lv_pid  # noqa: E402
from build_opconstvalue_v1b import decode_flat, NUM_TD  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP_UNFLAT = os.path.join(g.CLAUDEDEV, "OpBuildUnflatten_v0.vi")
HEXVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Bit Manipulation\Bytes to Lowercase Hex String.vi"
SIZE_TERM = "data includes array or string size? (T)"


def new_labels(dst, before, ind):
    return [l for _i, l, i in g.fp_labels(dst) if i == ind and l not in before]


def main():
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    must("S the v1b op (Flatten labels) and the creator/donor VIs exist",
         os.path.exists(OP) and "data" in labels and os.path.exists(OP_UNFLAT) and os.path.exists(HEXVI))
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    g.reset(); com_preflight()
    if "--test-only" in sys.argv:
        must("S the byte-route labels exist from a passed build", all(k in labels for k in ("hex", "u8", "rest", "size", "u8type")), str(labels))
        return test(labels)
    g.open_panel(OP); time.sleep(0.8)
    w = walk(OP, 0)
    fl = next(u for u, v in w.items() if any(r["name"] == "anything" for r in v[2]))
    w_data = term(w[fl][2], "data string", True)["wire"]
    must("A Flatten.'data string' is wired (v1b indicator)", w_data != 0, str(w_data))
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    # A: the hex VI + a U8[] control seeded from its `bytes` input
    sub0 = g.uids(OP, "SubVI"); g.drop_subvi(OP, HEXVI, 0, (2500, 700))
    hv = [u for u in g.uids(OP, "SubVI") if u not in sub0]
    must("A exactly one new SubVI (hex VI)", len(hv) == 1, str(hv)); hv = hv[0]
    w = walk(OP, 0); n_hv = w[hv][0]; t_bytes = term(w[hv][2], "bytes", False)["i"]
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}; g.create_control(OP, n_hv, t_bytes)
    labs = new_labels(OP, c0, False)
    must("A exactly one new control (U8[] seed) on hexVI.'bytes'", len(labs) == 1, str(labs)); labels["u8type"] = labs[0]
    pw = {r["label"]: r for r in g.panel_wiring(OP)}; ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(pw[labels["u8type"]]["wire"]), verify=False)
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("A the U8[] control survives, unwired", labels["u8type"] in pw and pw[labels["u8type"]]["wire"] == 0)
    # B: Unflatten via the creator (junk Invoke removed as build_opclfn does)
    inv0 = g.uids(OP, "Invoke"); uf0 = g.uids(OP, "FlattenUnflattenString")
    vi = g.op(OP_UNFLAT); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0)
    vi.SetControlValue("location (0, 0)", [2200, 900]); g._run(vi)
    for o in [u for u in g.uids(OP, "Invoke") if u not in inv0]:
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o in ids:
            g.delete_object(OP, "Invoke", ids.index(o))
    uf = [u for u in g.uids(OP, "FlattenUnflattenString") if u not in uf0]
    must("B exactly one new Unflatten From String", len(uf) == 1, str(uf)); uf = uf[0]
    g.wire(OP, "FlattenString", fi("FlattenString", fl), "data string", "FlattenUnflattenString", fi("FlattenUnflattenString", uf), "binary string", branch=True)
    w = walk(OP, 0)
    a = term(w[fl][2], "data string", True)["wire"]; b = term(w[uf][2], "binary string", False)["wire"]
    must("B Flatten.'data string' -> Unflatten.'binary string' (branch) shares the wire uid on both ends", a and a == b == w_data, f"{a}/{b}/{w_data}")
    # C: type <- U8[] control; size? <- Boolean control
    g.wire_control(OP, [labels["u8type"]], "FlattenUnflattenString", fi("FlattenUnflattenString", uf), ["type"])
    w = walk(OP, 0); pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("C U8[] control -> Unflatten.'type' on both ends", pw[labels["u8type"]]["wire"] and pw[labels["u8type"]]["wire"] == term(w[uf][2], "type", False)["wire"])
    n_uf = w[uf][0]; t_size = term(w[uf][2], SIZE_TERM, False)["i"]
    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}; g.create_control(OP, n_uf, t_size)
    labs = new_labels(OP, c0, False)
    must("C exactly one new Boolean control on 'data includes array or string size?'", len(labs) == 1, str(labs)); labels["size"] = labs[0]
    # D: value -> bytes; indicators
    g.wire(OP, "FlattenUnflattenString", fi("FlattenUnflattenString", uf), "value", "SubVI", fi("SubVI", hv), "bytes")
    w = walk(OP, 0)
    a = term(w[uf][2], "value", True)["wire"]; b = term(w[hv][2], "bytes", False)["wire"]
    must("D Unflatten.'value' -> hexVI.'bytes' on both ends", a and a == b, f"{a}/{b}")
    for uid, name, key in ((hv, "hex string", "hex"), (uf, "value", "u8"), (uf, "rest of the binary string", "rest")):
        w = walk(OP, 0); n = w[uid][0]; t = term(w[uid][2], name, True)["i"]
        i0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, n, t)
        labs = new_labels(OP, i0, True)
        must(f"D indicator on '{name}'", len(labs) == 1, str(labs)); labels[key] = labs[0]
    es = g.exec_state(OP)
    must("E op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def normalize_u8(v):
    """pywin32 maps SAFEARRAY(VT_UI1) to a buffer-like value (bytes/memoryview), older builds to a tuple of ints
    (review ...-v1c-recipe-byte-route §4): accept both, reject strings/None/out-of-range."""
    if v is None or isinstance(v, str):
        return None
    try:
        return bytes(v)
    except (TypeError, ValueError):
        try:
            return bytes(int(x) for x in v)
        except (TypeError, ValueError, OverflowError):
            return None


def test(labels):
    vi = g.op(OP)
    main_md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest(); main_mtime = os.path.getmtime(MAIN)
    POISON = "POISON"
    try:
        return _test(vi, labels, POISON)
    finally:
        # review §6: the integrity audit must run even when a gate stops the test
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == main_md5 and os.path.getmtime(MAIN) == main_mtime
        print(f"   {'PASS' if same else 'FAIL'} T(finally) the main VI file is byte-identical and untouched after the reads", flush=True)
        B.PASS.append(("T(finally) main VI untouched", same))


def _test(vi, labels, POISON):
    def read(cls, i, manifest):
        must(f"T index {i} in range for {cls}", 0 <= i < len(manifest), str(len(manifest)))
        for lab in (labels["value"], labels["data"], labels["hex"], labels["rest"]):
            vi.SetControlValue(lab, POISON)
        vi.SetControlValue(labels["u8"], []); vi.SetControlValue("UID", 0); vi.SetControlValue("Class Name 2", POISON); vi.SetControlValue("# of Refs", -1)
        vi.SetControlValue(labels["size"], False)
        must("T size control reads back False before the run", vi.GetControlValue(labels["size"]) is False)
        vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
        g._run(vi); err = g._err(vi, "error out") or ""
        uid = int(vi.GetControlValue("UID")); cls2 = vi.GetControlValue("Class Name 2"); nrefs = int(vi.GetControlValue("# of Refs"))
        hx = vi.GetControlValue(labels["hex"]); u8 = vi.GetControlValue(labels["u8"]); rest = vi.GetControlValue(labels["rest"])
        b_u8 = normalize_u8(u8)
        hex_ok = isinstance(hx, str) and hx != POISON and b_u8 is not None and len(hx) == 2 * len(b_u8) and hx == hx.lower() \
            and all(c in "0123456789abcdef" for c in hx)
        try:
            b_hex = bytes.fromhex(hx) if hex_ok else None
        except ValueError:
            b_hex = None
        code, val, note = decode_flat(b_u8) if b_u8 else (None, None, f"u8={u8!r:.30}")
        ident = uid == manifest[i]["uid"] and cls2 == cls and nrefs == len(manifest)
        print(f"   {cls}[{i}] uid={uid}{'' if ident else '!=' + str(manifest[i]['uid'])} cls2={cls2!r:.24} n={nrefs} hex={hx!r:.44} "
              f"u8={len(b_u8) if b_u8 else None}B rest={rest!r:.12} same={b_hex == b_u8 and b_u8 is not None} -> code={code} val={val!r:.30} {note} {err[:40]}", flush=True)
        return dict(ident=ident, err=err, b_hex=b_hex, b_u8=b_u8, code=code, val=val, rest=rest, uid=uid, nrefs=nrefs)

    def good(r):
        return r["ident"] and not r["err"] and r["b_u8"] is not None and r["b_hex"] == r["b_u8"] and r["rest"] == ""
    man_s = g.report(MAIN, "StringConstant")
    r = read("StringConstant", 7, man_s)
    must("T StringConstant[7] identity (UID, class, # of Refs) matches the reporter, no error", r["ident"] and not r["err"])
    must("T strict lowercase hex == U8 SAFEARRAY bytes, remainder empty", good(r))
    must("T the bytes contain b'img%05d.tif' (framing-independent)", b"img%05d.tif" in r["b_u8"], r["b_u8"][:40].hex())
    must("T HYPOTHESIS-A framing decodes StringConstant[7] exactly (TD 0x30)", r["code"] == 0x30 and r["val"] == "img%05d.tif", f"{r['code']} {r['val']!r}")
    man_n = g.report(MAIN, "DigitalNumericConstant")
    nums = []
    for i in range(6):
        r = read("DigitalNumericConstant", i, man_n)
        must(f"T DigitalNumericConstant[{i}] identity, no error, hex == u8 bytes, remainder empty", good(r))
        if r["code"] in NUM_TD and r["val"] is not None:
            nums.append(r["val"])
    must("T all 6 numeric constants decode from a numeric TD (consumed exactly, finite), not all identical", len(nums) == 6 and len(set(nums)) >= 2, str(nums))
    # negative control (review §5): an out-of-range index must error or leave the outputs unmistakably poisoned
    for lab in (labels["hex"], labels["rest"]):
        vi.SetControlValue(lab, POISON)
    vi.SetControlValue("UID", 0); vi.SetControlValue(labels["size"], False)
    vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", "DigitalNumericConstant"); vi.SetControlValue("index", len(man_n) + 5)
    try:
        g._run(vi); err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:60]}"
    hx = vi.GetControlValue(labels["hex"]); uid = int(vi.GetControlValue("UID"))
    print(f"   negative control index {len(man_n) + 5}: err={err[:60]!r} hex={hx!r:.20} uid={uid}", flush=True)
    must("T out-of-range index errors or leaves the outputs poisoned (no silent stale read)", bool(err) or hx == POISON or uid == 0)
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
