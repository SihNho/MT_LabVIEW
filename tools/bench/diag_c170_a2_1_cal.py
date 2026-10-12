# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/brief_170-a2-1.md
# ---
r"""diag_c170_a2_1_cal - card 170-a2-1 brief steps 2 (decode) and 4 (check): OFFLINE in effect (gscript is imported for its pure TD parser
only, so the header declares read; no LabVIEW call is made). Decodes the type bytes read by diag_c170_a2_1_f4.py
(Terminal.Data Type of ClusterConstant #26159's output t26156, TD layout docs/NAMES.md:1167-1169) into the element list (order, type,
label), then walks the stored 110-7 cal001 of leg A and leg B with that type (Write to Binary File #26615 of the bundled cluster: big-endian,
flattened cluster; inner strings/arrays always size-prefixed I32) and reports the 'Date and time' field's offset, length and text per file,
and whether the bytes outside the field are identical. Facts only.

Found before writing (CALLED): gscript.parse_type_descriptors (tools/gscript.py:4591: TD list, cluster element indices, array ndims/elem
index; it does NOT decode labels or walk data - td_label / walk below are new, each with one assert). Leg run dirs: leg.json 'run_dir'
(t0_legs/c110f_replay_20260927_184600/{A_S1replay_a1,B_dispreplay_a1}/leg.json:460/491).

PREDICTION: D1 the f4 JSON holds a lossless cluster TD; D2 exactly one element labelled 'Date and time', a String; W per file the walk
consumes the file EXACTLY (857376 B); F per file the field's text is printable; X outside-field bytes identical A vs B: REPORTED (a fact,
not a gate - the brief asks facts only).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c170_a2_1_cal.log -- py -u tools/bench/diag_c170_a2_1_cal.py"""
import json, os, struct, sys                                                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (ROOT, os.path.join(ROOT, "tools"), HERE):
    _p in sys.path or sys.path.insert(0, _p)                                                 # noqa: E701
import gscript as g                                                                          # noqa: E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402

F4 = os.path.join(HERE, "diag_c170_a2_1_f4.json")
OUT = os.path.join(HERE, "diag_c170_a2_1_cal.json")
LEGS = {"A": os.path.join(HERE, "t0_legs", "c110f_replay_20260927_184600", "A_S1replay_a1", "leg.json"),
        "B": os.path.join(HERE, "t0_legs", "c110f_replay_20260927_184600", "B_dispreplay_a1", "leg.json")}
# card 170-a2-4: NUM/SIZE, td_label, walk, run_dirs MOVED to tools/bench/m8b_replay_compare.py (shared; self-tests there) and
# imported here; walk's element type keeps gscript._td_canon through its `canon` argument (call below).
from m8b_replay_compare import td_label, walk, run_dirs                                      # noqa: E402
gate = L.Gate(fatal_default=False)


def fact(x):
    print("FACT " + str(x)[:2500], flush=True)


def enum_items(td_hex):
    b = bytes.fromhex(td_hex)
    n, p, out = struct.unpack(">h", b[4:6])[0], 6, []
    for _ in range(n):
        out.append(b[p + 1:p + 1 + b[p]].decode("cp949", "replace")); p += 1 + b[p]          # noqa: E702
    return out


R = {}
f4 = json.load(open(F4, encoding="utf-8"))
ct = (f4.get("types") or {}).get("cluster_const_out") or {}
gate("D1 f4 JSON: t26156 type read lossless, top TD Cluster", ct.get("hex_ok") and ct.get("top_name") == "Cluster", (ct.get("hex_ok"), ct.get("top_name")))
ty = g.parse_type_descriptors(bytes.fromhex(ct["bytes_hex"]))
tds, top = ty["tds"], ty["top"][0]
for k, t in enumerate(tds):
    fact("TD %d: %s flags 0x%02x len %d label %r hex %s%s" % (k, t["name"], t["flags"], t["len"], td_label(t["hex"]), t["hex"],
         (" items %s" % enum_items(t["hex"])) if t["code"] in (0x15, 0x16, 0x17) else ""))
els = [{"index": k, "td": e, "label": td_label(tds[e]["hex"]), "type": g._td_canon(tds, e)} for k, e in enumerate(tds[top]["elems"])]
R["cluster"] = {"label": td_label(tds[top]["hex"]), "n": len(els), "elements": els, "canon": ty["canon"]}
for e in els:
    fact("ELEMENT %d %r: %s" % (e["index"], e["label"], e["type"]))
di = [e["index"] for e in els if e["label"] == "Date and time"]
gate("D2 exactly one element labelled 'Date and time', type String", len(di) == 1 and els[di[0]]["type"] == "String", di)
for tag in ("fixed_const_out", "enum_const_out", "bool_const_out", "bundler_date_in"):
    t2 = (f4.get("types") or {}).get(tag) or {}
    if t2.get("bytes_hex"):
        p2 = g.parse_type_descriptors(bytes.fromhex(t2["bytes_hex"]))
        fact("TERMTYPE %s t%s: canon %s labels %s items %s | data part %s" % (
            tag, t2.get("term"), p2.get("canon"), [td_label(x["hex"]) for x in p2.get("tds") or []],
            [enum_items(x["hex"]) for x in p2.get("tds") or [] if x["code"] in (0x15, 0x16, 0x17)], t2["bytes_hex"][-40:]))
for k, v in (f4.get("values") or {}).items():
    fact("VALUE %s: %s" % (k, json.dumps(dict((a, v.get(a)) for a in ("cls", "route", "value", "type", "hex", "repr", "echo", "err", "exc")),
                                          default=str)))

FILES = {}
for leg, lj in sorted(LEGS.items()):
    rd = run_dirs(lj)
    fact("LEG %s run_dir values in %s: %s" % (leg, os.path.relpath(lj, ROOT), rd))
    if len(rd) != 1:
        gate("LEG %s has one run_dir" % leg, False, rd)
        continue
    cal = os.path.join(rd[0], "cal001")
    b = open(cal, "rb").read()
    rows = []
    try:
        end, _v = walk(tds, top, b, 0, "cal", rows, g._td_canon)
    except Exception as e:                                                                   # noqa: BLE001
        end = "EXC %s" % e
    gate("W leg %s: walk of %s consumes the file exactly (%s of %d B)" % (leg, os.path.relpath(cal, ROOT), end, len(b)), end == len(b))
    for r in rows:
        fact("CAL %s el %d %r %s offset %d length %d value %s" % (leg, r["index"], r["label"], r["type"], r["offset"], r["length"],
                                                                  json.dumps(r["value"], default=str)[:160]))
    f = [r for r in rows if r["label"] == "Date and time"]
    if f:
        f = f[0]
        txt = b[f["offset"] + 4:f["offset"] + f["length"]]
        FILES[leg] = {"path": os.path.relpath(cal, ROOT), "md5": L.md5(cal), "size": len(b), "field_offset": f["offset"],
                      "field_length": f["length"], "text_offset": f["offset"] + 4, "text_len": len(txt), "text_hex": txt.hex(),
                      "text": txt.decode("cp949", "replace"), "bytes": b}
        fact("FIELD %s: offset %d (I32 length prefix) length %d (4 + %d text bytes); text %r hex %s" % (
            leg, f["offset"], f["length"], len(txt), FILES[leg]["text"], txt.hex()))
        gate("F leg %s: field text is printable (cp949 decode without replacement)" % leg, "�" not in FILES[leg]["text"] and len(txt) > 0,
             FILES[leg]["text"])
    R.setdefault("rows", {})[leg] = rows
if len(FILES) == 2:
    a, bb = FILES["A"], FILES["B"]
    A, B = a["bytes"], bb["bytes"]
    pre = A[:a["field_offset"]] == B[:bb["field_offset"]]
    post = A[a["field_offset"] + a["field_length"]:] == B[bb["field_offset"] + bb["field_length"]:]
    nd = sum(1 for x, y in zip(A, B) if x != y) if len(A) == len(B) else None
    R["outside_identical"] = {"before_field": pre, "after_field": post, "same_offset": a["field_offset"] == bb["field_offset"],
                              "same_length": a["field_length"] == bb["field_length"], "whole_file_bytes_differing": nd,
                              "md5": [a["md5"], bb["md5"]]}
    fact("OUTSIDE-FIELD A vs B: bytes before the field identical %s, after the field identical %s; field offset equal %s, length equal %s; "
         "whole-file differing bytes %s; md5 A %s B %s" % (pre, post, a["field_offset"] == bb["field_offset"],
                                                           a["field_length"] == bb["field_length"], nd, a["md5"], bb["md5"]))
    if not (pre and post):
        diffs = [k for k, (x, y) in enumerate(zip(A, B)) if x != y]
        fact("DIFFERING OFFSETS (first 20) %s" % diffs[:20])
        R["outside_identical"]["first_diffs"] = diffs[:200]
R["files"] = dict((k, dict((a, v) for a, v in f.items() if a != "bytes")) for k, f in FILES.items())
json.dump(R, open(OUT, "w", encoding="utf-8"), default=str, indent=1, ensure_ascii=False)
sys.exit(gate.result([{"path": os.path.relpath(OUT, ROOT).replace("\\", "/"), "md5": L.md5(OUT)}]))
