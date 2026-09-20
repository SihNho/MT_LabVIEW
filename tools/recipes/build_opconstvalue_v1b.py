r"""build_opconstvalue_v1b.py - augment the saved OpConstValue_v1.vi (run 4 build, run 6 functional for strings) so a
NUMERIC constant's value survives the Variant -> COM boundary: run 6 read every DigitalNumericConstant as Python None
with no error, while the StringConstants came back typed (peer archive/peer/2026-09-15-opconstvalue-run6-numeric-reads-none.md:
export the variant through Flatten To String - lossless, type-preserving; %g and Variant-To-Data(DBL) rejected).

Change (in place on the op, panel open, one COM save):
  +1 FlattenString via the proven creator OpBuildFlatten_v0 (build_opclfnparams; NAMES.md: inputs `anything`, outputs
     `data string`, `type string (7.x only)`), PN.Value --branch--> Flatten.anything, indicators on both outputs.
Gates (predictions): +1 FlattenString; the branch wire shares the uid of PN.Value's existing wire on both ends; 2 new
indicators; ExecState 1 before the save.
TEST (typed, on the main VI, read-only): StringConstant[7] = 'img%05d.tif' (docs/fixture-recording.md) must decode from
the flattened variant (TD 0x30 string, I32 length + bytes) AND still read from 'Value'; DigitalNumericConstant[0..5]:
at least 3 decode to numbers from a numeric TD (0x01-0x0B) and are not all identical.

  py tools/bgrun.py --max-min 15 --log tools/bench/build_opconstvalue_v1b.log -- py -u tools/recipes/build_opconstvalue_v1b.py
"""
import hashlib
import json
import math
import os
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import OP, MAIN, MAP_OUT, com_preflight, lv_pid  # noqa: E402

must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)
OP_FLAT = os.path.join(g.CLAUDEDEV, "OpBuildFlatten_v0.vi")
NUM_TD = {0x01: ">b", 0x02: ">h", 0x03: ">i", 0x04: ">q", 0x05: ">B", 0x06: ">H", 0x07: ">I", 0x08: ">Q", 0x09: ">f", 0x0A: ">d"}


def decode_flat(data):
    """Flattened LabVIEW variant as emitted by Flatten To String on a variant (NI 'Understanding Flattened Variant
    Data': version, type descriptor(s), data, attribute count; big-endian). The framing after the version is NOT
    documented precisely (peer ...-opconstvalue-v1b-recipe-flatten), so this parser is HYPOTHESIS A (U32 version, I32
    #TDs, TDs of I16 length/I16 code) and every failure returns the raw bytes; it is validated empirically on the
    documented StringConstant[7] BEFORE any numeric result is trusted. Bounds-checked; requires the data to be consumed
    exactly and the attribute count to be 0. Returns (code, value|None, note)."""
    # build run (04:54): the BSTR arrives code-page DECODED (chars > U+00FF) - LabVIEW's ActiveX string marshalling goes
    # through the ANSI code page (cp949 here). 'mbcs' strict is the candidate inverse; a failure or a structural
    # mismatch below means the path is LOSSY and the U8-array route must be built instead.
    try:
        b = data.encode("mbcs", errors="strict") if isinstance(data, str) else bytes(data)
    except UnicodeEncodeError as e:
        return None, None, f"mbcs re-encode LOSSY: {str(e)[:80]}"
    raw = b[:32].hex()
    if len(b) < 12:
        return None, None, f"short len={len(b)} raw={raw}"
    ver, ntd = struct.unpack(">Ii", b[:8]); p = 8; codes = []
    if not 0 < ntd <= 64:
        return None, None, f"bad #TDs {ntd} raw={raw}"
    for _ in range(ntd):
        if p + 4 > len(b) - 4:
            return None, None, f"TD overrun p={p} raw={raw}"
        ln, code = struct.unpack(">hh", b[p:p + 4])
        # OpConstValueN run 2 (05:41): labelled scalar TDs have ODD lengths (7, 11, 17, 21, 23) and NO pad byte -
        # 8 + ln + 4 + data + 4 == len(b) exactly - so odd is legal; only the bounds are gated
        if ln < 4 or p + ln > len(b) - 4:
            return None, None, f"bad TD length {ln} at {p} raw={raw}"
        codes.append(code & 0xFF); p += ln
    # MEASURED (v1c run 1, 05:06, StringConstant[7], 53 B): after the TD list come an I16 count of top-level type
    # indices (1) and that many I16 indices into the TD list, THEN the data, THEN the I32 attribute count. Hypothesis A
    # (data directly after the TDs) left 4 unexplained bytes; the TD code carries flag 0x40 (labelled) in its high byte.
    if p + 2 > len(b) - 4:
        return None, None, f"index-count overrun raw={raw}"
    nidx = struct.unpack(">h", b[p:p + 2])[0]; p += 2
    if not 1 <= nidx <= 8 or p + 2 * nidx > len(b) - 4:
        return None, None, f"bad index count {nidx} raw={raw}"
    idx = struct.unpack(f">{nidx}h", b[p:p + 2 * nidx]); p += 2 * nidx
    if not 0 <= idx[0] < len(codes):
        return None, None, f"bad top-level index {idx} raw={raw}"
    code = codes[idx[0]]
    nattr = struct.unpack(">i", b[-4:])[0]
    body = b[p:-4]
    try:
        if code in NUM_TD:
            size = struct.calcsize(NUM_TD[code])
            val = struct.unpack(NUM_TD[code], body[:size])[0]
            ok = len(body) == size and nattr == 0 and (not isinstance(val, float) or math.isfinite(val))
            return code, (val if ok else None), f"v{ver:#x} tds={codes} body={len(body)}B/{size} attrs={nattr}"
        if code == 0x30:
            n = struct.unpack(">i", body[:4])[0]
            ok = 0 <= n and len(body) == 4 + n and nattr == 0
            return code, (body[4:4 + n].decode("latin-1") if ok else None), f"v{ver:#x} tds={codes} body={len(body)}B/{4 + n} attrs={nattr}"
    except Exception as e:
        return code, None, f"decode EXC {e} raw={raw}"
    return code, None, f"v{ver:#x} tds={codes} unhandled body={body[:24].hex()} attrs={nattr}"


def main():
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    must("S OpConstValue_v1.vi (run 4) and OpBuildFlatten_v0.vi exist", os.path.exists(OP) and os.path.exists(OP_FLAT))
    print(f"   LabVIEW pid before: {lv_pid()}", flush=True)
    g.reset(); com_preflight()
    if "--test-only" in sys.argv:
        # the 04:54 build PASSED and saved (Flatten + 2 indicators); rerunning main() would add a second Flatten node
        must("S the Flatten labels exist from the passed build", "data" in labels and "type" in labels, str(labels))
        return test(labels)
    g.open_panel(OP); time.sleep(0.8)
    w = walk(OP, 0)
    pn = [u for u, v in w.items() if term(v[2], "Value", True) and any(r["name"] == "reference" for r in v[2])]
    must("A exactly one Property node with a 'Value' source", len(pn) == 1, str(pn)); pn = pn[0]
    w_val = term(w[pn][2], "Value", True)["wire"]
    must("A PN.Value already wired (to the run-4 indicator)", w_val != 0, str(w_val))
    # +1 FlattenString via the creator (its junk Invoke node on OP is removed, as build_opclfn does)
    inv0 = g.uids(OP, "Invoke"); fl0 = g.uids(OP, "FlattenString")
    vi = g.op(OP_FLAT); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0)
    vi.SetControlValue("location (0, 0)", [1900, 700]); g._run(vi)
    for o in g.new_since(OP, "Invoke", inv0):
        ids = [x["uid"] for x in g.report(OP, "Invoke")]
        if o["uid"] in ids:
            g.delete_object(OP, "Invoke", ids.index(o["uid"]))
    new = g.new_since(OP, "FlattenString", fl0)
    must("B exactly one new FlattenString", len(new) == 1, str(new)); fl = new[0]["uid"]
    fi = lambda cls, u: [o["uid"] for o in g.report_all(OP, cls)].index(u)
    g.wire(OP, "Property", fi("Property", pn), "Value", "FlattenString", fi("FlattenString", fl), "anything", branch=True)
    w = walk(OP, 0)
    a = term(w[pn][2], "Value", True)["wire"]; b = term(w[fl][2], "anything", False)["wire"]
    must("B PN.Value -> Flatten.anything (branch) shares the wire uid on both ends", a and a == b == w_val, f"{a}/{b}/{w_val}")
    n = w[fl][0]
    for name, key in (("data string", "data"), ("type string", "type")):
        t = next(r for r in w[fl][2] if r["is_source"] and r["name"].startswith(name))["i"]
        b0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, n, t)
        labs = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in b0]
        must(f"B indicator on Flatten.'{name}'", len(labs) == 1, str(labs)); labels[key] = labs[0]
    es = g.exec_state(OP)
    must("B op runnable before the save", es == 1, str(es))
    g.save(OP); g.close_panel(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   labels {labels}", flush=True)
    return test(labels)


def test(labels):
    vi = g.op(OP)
    main_md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest(); main_mtime = os.path.getmtime(MAIN)
    POISON = "POISON"

    def read(cls, i, manifest):
        # identity (review ...-v1b-recipe-flatten §4): the op still carries OpReport_v3's UID / Class Name 2 outputs -
        # every read must name the reporter's object for that index, and the result indicators are poisoned first so a
        # stale output from a failed run cannot pass.
        for lab in (labels["value"], labels["data"], labels["type"]):
            vi.SetControlValue(lab, POISON)
        vi.SetControlValue("UID", 0); vi.SetControlValue("Class Name 2", POISON)
        vi.SetControlValue("vi path", MAIN); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)
        g._run(vi); err = g._err(vi, "error out") or ""
        uid = int(vi.GetControlValue("UID")); cls2 = vi.GetControlValue("Class Name 2")
        v = vi.GetControlValue(labels["value"]); d = vi.GetControlValue(labels["data"]); t = vi.GetControlValue(labels["type"])
        code, val, note = decode_flat(d) if isinstance(d, str) and d != POISON else (None, None, f"data={d!r:.20}")
        ident = uid == manifest[i]["uid"] and cls2 == cls
        print(f"   {cls}[{i}] uid={uid}{'' if ident else '!=' + str(manifest[i]['uid'])} cls2={cls2!r:.24} Value={v!r:.30} "
              f"data={len(d) if isinstance(d, str) else d!r}B type={t!r:.20} -> code={code} val={val!r:.30} {note} {err[:40]}", flush=True)
        return v, val, code, err, ident, d
    man_s = g.report(MAIN, "StringConstant")
    v, val, code, err, ident, d = read("StringConstant", 7, man_s)
    must("T StringConstant[7] identity (UID and class) matches the reporter", ident and not err)
    must("T the op's '# of Refs' equals the reporter's StringConstant count", int(vi.GetControlValue("# of Refs")) == len(man_s), str(len(man_s)))
    must("T StringConstant[7] 'Value' still reads 'img%05d.tif'", v == "img%05d.tif", repr(v))
    must("T the flattened blob contains the literal bytes 'img%05d.tif' (framing-independent)", isinstance(d, str) and "img%05d.tif" in d, repr(d)[:80])
    must("T HYPOTHESIS A framing decodes StringConstant[7] exactly (TD 0x30, consumed exactly, 0 attrs)", code == 0x30 and val == "img%05d.tif", f"{code} {val!r}")
    man_n = g.report(MAIN, "DigitalNumericConstant")
    nums = []; lens = []
    for i in range(6):
        v, val, code, err, ident, d = read("DigitalNumericConstant", i, man_n)
        must(f"T DigitalNumericConstant[{i}] identity matches the reporter, no error", ident and not err)
        lens.append(len(d) if isinstance(d, str) else -1)
        if code in NUM_TD and val is not None:
            nums.append(val)
    must("T numeric blobs are structurally complete (>= 12 B each: NULs survived the BSTR path)", all(n >= 12 for n in lens), str(lens))
    must("T all 6 numeric constants decode from a numeric TD (consumed exactly, finite), not all identical", len(nums) == 6 and len(set(nums)) >= 2, str(nums))
    must("T the main VI file is byte-identical and untouched after the reads",
         hashlib.md5(open(MAIN, "rb").read()).hexdigest() == main_md5 and os.path.getmtime(MAIN) == main_mtime)
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
