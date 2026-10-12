r"""m8b_replay_compare - card 78-3 R2/R3 (m8 plan PD13(d), PD17(b'), PD22(d)): join the S1-replay and S3-replay tra rows on
iteration index and test X/Y/Z bit-identity. No LabVIEW. FOUND FIRST: drive_m8.tra_rows (header end marker 'not in z!)',
binary f64 rows time,trans,rot + N x (x,y,z)); this adds the layout read (2 x I32 little-endian dims, then <f8 row-major,
m8_s1_p3.json:110-112 rem 8 = the dims prefix) and the join.
    py tools/bench/m8b_replay_compare.py <run_dir_s1> <run_dir_s3> [--out tools/bench/m8b_replay_78.json]
PREDICTION: G1 both tra parse (dims product == data length); G2 >= 1000 common rows; G3 zero rows with X/Y/Z not
bit-identical over the common prefix; cal files: FACT (md5 equal or first differing byte offset)."""
import hashlib, json, os, re, struct, sys                                               # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                    # noqa: E402


def tra(d):
    f = [x for x in sorted(os.listdir(d)) if x.lower().startswith("tra")][0]
    b = open(os.path.join(d, f), "rb").read(); k = b.find(b"not in z!)") + 10
    r, c = struct.unpack("<ii", b[k:k + 8]); a = np.frombuffer(b[k + 8:], dtype="<f8")   # LITTLE-endian (selftest78: '>' gave 0x0C000000)
    w = np.frombuffer(b[k + 8:k + 8 + 8 * (a.size)], dtype="u1").reshape(-1, 8); ex = lambda v: int(np.sum(((v >= 0x3F) & (v <= 0x41)) | ((v >= 0xBF) & (v <= 0xC1))))  # noqa: E731
    order = {"hdr_len_prefix_le": struct.unpack("<I", b[:4])[0], "hdr_len_expected": k - 4,        # review 78-3-selftest-endian (a)
             "exp_byte_pos0": ex(w[:, 0]), "exp_byte_pos7": ex(w[:, 7])}                           # (b): exponent byte position
    ok = r * c == a.size and order["hdr_len_prefix_le"] == k - 4 and order["exp_byte_pos7"] > order["exp_byte_pos0"]
    return {"file": os.path.join(d, f), "dims": [r, c], "byte_order": order, "parsed": ok}, (a.reshape(r, c) if ok else None)


def cal(d):
    f = [x for x in sorted(os.listdir(d)) if x.lower().startswith("cal")][0]
    return open(os.path.join(d, f), "rb").read()


def main(a1, a3, out):
    i1, t1 = tra(a1); i3, t3 = tra(a3); G = {}; R = {"s1": i1, "s3": i3}
    G["G1 both tra parse (dims, LE header length prefix, exponent byte at pos 7)"] =i1["parsed"] and i3["parsed"] and i1["dims"][1] == i3["dims"][1]
    if all(G.values()):
        n = min(len(t1), len(t3)); x1, x3 = t1[:n, 3:], t3[:n, 3:]
        neq = np.any(x1.view("u8") != x3.view("u8"), axis=1); bad = np.nonzero(neq)[0]
        pref = int(bad[0]) if bad.size else n
        R.update({"rows_s1": len(t1), "rows_s3": len(t3), "common": n, "identical_prefix": pref,
                  "rows_xyz_not_bit_identical": int(bad.size),
                  "first_diff": None if not bad.size else {"row": pref, "s1": t1[pref].tolist(), "s3": t3[pref].tolist()},
                  "max_abs_diff_xyz": float(np.nanmax(np.abs(x1 - x3))) if n else None,
                  "trans_rot_rows_differ": int(np.sum(np.any(t1[:n, 1:3] != t3[:n, 1:3], axis=1))),
                  "nan_rows_s1": int(np.sum(np.any(np.isnan(x1), axis=1))), "row0_s1": t1[0].tolist() if n else None})
        G["G2 >= 1000 common rows"] = n >= 1000
        G["G3 X/Y/Z bit-identical over the common rows"] = n > 0 and bad.size == 0
    c1, c3 = cal(a1), cal(a3)
    off = next((i for i, (p, q) in enumerate(zip(c1, c3)) if p != q), None if len(c1) == len(c3) else min(len(c1), len(c3)))
    R["cal"] = {"md5_s1": hashlib.md5(c1).hexdigest(), "md5_s3": hashlib.md5(c3).hexdigest(), "len": [len(c1), len(c3)],
                "first_diff_offset": off, "context_s1": c1[max(0, (off or 0) - 40):(off or 0) + 40].hex() if off is not None else None}
    R["gates"] = G; json.dump(R, open(out, "w"), indent=1, default=str)
    for k, v in G.items():
        print("GATE %-50s %s" % (k, "PASS" if v else "FAIL"))
    print("FACTS", json.dumps({k: R.get(k) for k in ("rows_s1", "rows_s3", "common", "identical_prefix",
                                                      "rows_xyz_not_bit_identical", "max_abs_diff_xyz", "trans_rot_rows_differ")}))
    print("CAL", json.dumps({k: v for k, v in R["cal"].items() if k != "context_s1"}))
    bad = [k for k, v in G.items() if not v]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                      [{"path": os.path.relpath(out, ROOT), "md5": hashlib.md5(open(out, "rb").read()).hexdigest()}])))
    return not bad


# ==== card 170-a2-4 (ring-p6.md PD409(b) :246-253, PD410(c) :301-309): the (b)/(c) compare. tra/cal/main above are unchanged
# and CALLED.  py tools/bench/m8b_replay_compare.py <run_dir_a> <run_dir_b> --slots D [--out f]   (no --slots = the old G1-G3 run)
#               py tools/bench/m8b_replay_compare.py --selftest --slots D   (stored 110-7 legs, PD409(f) :277-280)
# FOUND FIRST: NUM/SIZE, td_label, walk, run_dirs lived in tools/bench/diag_c170_a2_1_cal.py (old :32-35, :43-65, :79-113,
# :122-133); that file runs its whole decode at import and imports gscript (COM), so they are MOVED here unchanged, except
# walk's row 'type' (gscript._td_canon there) now comes from the caller's `canon` (None -> the TD's name). The cal type
# (parsed TD list of ClusterConstant #26159) is read from the stored f4 read, not re-parsed (no gscript in this file).
NUM = {0x01: ">b", 0x02: ">h", 0x03: ">i", 0x04: ">q", 0x05: ">B", 0x06: ">H", 0x07: ">I", 0x08: ">Q", 0x09: ">f", 0x0A: ">d",
       0x15: ">B", 0x16: ">H", 0x17: ">I", 0x21: ">B"}
SIZE = dict((k, struct.calcsize(v)) for k, v in NUM.items())
SIZE.update({0x0B: 16, 0x0C: 8, 0x0D: 16, 0x0E: 32})
CAL_TYPE = os.path.join(HERE, "diag_c170_a2_1_f4.json")    # types.cluster_const_out = t26156 of #26159 (p6_replay_facts.md F4)
DATE_LABEL = "Date and time"
ENVELOPE = ("NOT-EVALUATED: tools/motor_gate.py:14-17 says the script-level numeric envelope is DELETED (limits live in the "
            "controllers), :20-21/:32 the rotor has no envelope declared - no single envelope constant in motor_gate.py")


def td_label(td_hex):
    """Label of one TD (hex of its bytes incl. the I16 length + I16 code): flag 0x40 = labelled; the label is the Pascal string that
    ends the TD (one pad byte allowed) after the code-specific body. Returns the label or None."""
    b = bytes.fromhex(td_hex)
    code, flags = b[3], b[2]
    if not flags & 0x40:
        return None
    p = 4
    if code in (0x30, 0x32):
        p += 4
    elif code == 0x40:
        p += 2 + 4 * struct.unpack(">h", b[4:6])[0] + 2
    elif code == 0x50:
        p += 2 + 2 * struct.unpack(">h", b[4:6])[0]
    elif code in (0x15, 0x16, 0x17):
        n = struct.unpack(">h", b[4:6])[0]; p += 2                                           # noqa: E702
        for _ in range(n):
            p += 1 + b[p]
        p += (p % 2)                                                                         # items padded to even (checked below)
    for q in (p, p - (p % 2)):
        if q < len(b) and q + 1 + b[q] in (len(b), len(b) - 1):
            return b[q + 1:q + 1 + b[q]].decode("cp949", "replace")
    return None


assert td_label("0007400a026162") == "ab" and td_label("0008400a02616200") == "ab" and td_label("0004000a") is None


def walk(tds, i, b, p, path, out, canon=None):
    """Flattened LabVIEW DATA of TD tds[i] at b[p:] (big-endian; arrays: I32 per dim then elements; strings: I32 length + bytes;
    clusters: elements in order). Appends (path, code-name, offset, length, value-or-summary) for cluster elements; returns end offset.
    canon(tds, e) names an element's type (None -> the TD name). Self-test: the assert below + --selftest."""
    t = tds[i]
    c = t["code"]
    if c in SIZE:
        v = struct.unpack(NUM[c], b[p:p + SIZE[c]])[0] if c in NUM else None
        return p + SIZE[c], v
    if c in (0x30, 0x32):
        n = struct.unpack(">i", b[p:p + 4])[0]
        if n < 0 or p + 4 + n > len(b):
            raise ValueError("bad string length %d at %d (%s)" % (n, p, path))
        return p + 4 + n, b[p + 4:p + 4 + n]
    if c == 0x40:
        nd = t["ndims"]
        dims = list(struct.unpack(">%di" % nd, b[p:p + 4 * nd])); q = p + 4 * nd                # noqa: E702
        n = 1
        for d in dims:
            n *= d
        et = tds[t["elem_index"]]
        if et["code"] in SIZE:
            return q + n * SIZE[et["code"]], {"dims": dims, "elem": et["name"]}
        for k in range(n):
            q, _v = walk(tds, t["elem_index"], b, q, "%s[%d]" % (path, k), None, canon)
        return q, {"dims": dims, "elem": et["name"]}
    if c == 0x50:
        q = p
        for k, e in enumerate(t["elems"]):
            q0 = q
            q, v = walk(tds, e, b, q, "%s.%d" % (path, k), None, canon)
            if out is not None:
                out.append({"index": k, "label": td_label(tds[e]["hex"]), "type": canon(tds, e) if canon else tds[e]["name"],
                            "offset": q0, "length": q - q0, "value": v.decode("cp949", "replace") if isinstance(v, bytes) else v})
        return q, None
    raise ValueError("TD code 0x%02x (%s) not walkable at %s" % (c, t["name"], path))


_T = [{"code": 0x50, "elems": [1, 2], "name": "Cluster", "hex": "000850000002000100020000"},
      {"code": 0x0A, "name": "DBL", "hex": "0007400a026162"}, {"code": 0x30, "name": "String", "hex": "00084030ffffffff"}]
_o = []
assert walk(_T, 0, struct.pack(">di", 1.5, 3) + b"xyz", 0, "", _o)[0] == 15 and _o[1]["offset"] == 8 and _o[1]["value"] == "xyz"


def run_dirs(leg_json):
    """Sorted distinct 'run_dir' string values anywhere in a leg.json."""
    vals = set()

    def rec(x):
        if isinstance(x, dict):
            for k, v in x.items():
                vals.add(v) if k == "run_dir" and isinstance(v, str) else rec(v)            # noqa: expression-not-assigned
        elif isinstance(x, list):
            for v in x:
                rec(v)
    rec(json.load(open(leg_json, encoding="utf-8")))
    return sorted(vals)


def md5f(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def cal_type(path=CAL_TYPE):
    """(tds, top) of the cal write's cluster from the stored type read (types.cluster_const_out: parsed TD list + top index)."""
    t = json.load(open(path, encoding="utf-8"))["types"]["cluster_const_out"]
    return t["tds"], t["top"][0]


def cal_field(b, tds, top, label=DATE_LABEL):
    """Walk one cal file's bytes with the cluster type; returns {size, walk_end, consumed_exactly, n_label, field_offset, field_length,
    text_offset, text, text_hex} for the element labelled `label` (field = I32 length + text). Self-test: --selftest."""
    rows = []
    try:
        end, _v = walk(tds, top, b, 0, "cal", rows)
    except Exception as e:                                                                   # noqa: BLE001
        end = "EXC %s" % e
    f = [r for r in rows if r["label"] == label]
    r = {"size": len(b), "walk_end": end, "consumed_exactly": end == len(b), "n_label": len(f)}
    if len(f) == 1:
        o, n = f[0]["offset"], f[0]["length"]
        txt = b[o + 4:o + n]
        r.update(field_offset=o, field_length=n, text_offset=o + 4, text=txt.decode("cp949", "replace"), text_hex=txt.hex())
    return r


def cal_compare(ca, cb, tds, top):
    """(b) .cal: whole-file byte compare, the date/time field located by the WALK of each file, and the differing bytes split into
    inside / outside that field. Returns {md5, len, bytes_differing, field {A, B}, outside_field_differing, first_outside_offset}."""
    fa, fb = cal_field(ca, tds, top), cal_field(cb, tds, top)
    m = min(len(ca), len(cb))
    diffs = np.nonzero(np.frombuffer(ca[:m], "u1") != np.frombuffer(cb[:m], "u1"))[0].tolist() + list(range(m, max(len(ca), len(cb))))

    def inside(k, f):
        return "field_offset" in f and f["field_offset"] <= k < f["field_offset"] + f["field_length"]
    out = [k for k in diffs if not (inside(k, fa) and inside(k, fb))]
    return {"md5": [hashlib.md5(ca).hexdigest(), hashlib.md5(cb).hexdigest()], "len": [len(ca), len(cb)], "bytes_differing": len(diffs),
            "field": {"A": fa, "B": fb}, "outside_field_differing": len(out), "first_outside_offset": out[0] if out else None}


def xyz_match(ta, tb, slots):
    """(b)+(c) MATCH: X/Y/Z (columns 3..) bit-identical per common row by f64 bits (time column 0 excluded); NaN cells per side and
    FINITE cells compared (finite on both sides) per bead; on the first differing row i the drop signature = every d in 1..slots
    with B row i == A row i+d bitwise. Self-test: the assert below."""
    n = min(len(ta), len(tb))
    xa, xb = ta[:n, 3:], tb[:n, 3:]
    nb = xa.shape[1] // 3
    bad = np.nonzero(np.any(xa.view("u8") != xb.view("u8"), axis=1))[0]
    fa, fb = np.isfinite(xa), np.isfinite(xb)
    ua_all = np.ascontiguousarray(ta[:, 3:]).view("u8")
    sig = None
    if bad.size:
        i = int(bad[0])
        ub = np.ascontiguousarray(tb[i, 3:]).view("u8")
        sig = [d for d in range(1, slots + 1) if i + d < len(ta) and np.array_equal(ub, ua_all[i + d])]
    return {"common": n, "beads": nb, "cols_xyz": xa.shape[1], "rows_not_identical": int(bad.size),
            "first_diff_row": int(bad[0]) if bad.size else None, "drop_signature_d": sig,
            "finite_cells_per_bead": (fa & fb).reshape(n, nb, 3).sum(axis=(0, 2)).tolist(),
            "nan_cells_A": int((~fa).sum()), "nan_cells_B": int((~fb).sum()),
            "nan_cells_per_bead_A": (~fa).reshape(n, nb, 3).sum(axis=(0, 2)).tolist()}


_a = np.array([[0, 0, 0, 1, 1, 1], [0, 0, 0, 2, 2, 2], [0, 0, 0, 3, 3, 3]], float)
_b = np.array([[9, 0, 0, 1, 1, 1], [0, 0, 0, 3, 3, 3]], float)
_m = xyz_match(_a, _b, 2)
assert _m["rows_not_identical"] == 1 and _m["first_diff_row"] == 1 and _m["drop_signature_d"] == [1] and _m["finite_cells_per_bead"] == [6]


def distinct(ta, n, slots):
    """(c) DISTINCT on side A alone: row i (< n) passes when it differs bitwise in >= 1 X/Y/Z cell FINITE on both rows from EACH A
    row i+1..i+slots that exists. Returns {slots, rows, pass, fail, first_fail_row}. Self-test: the assert below."""
    x = ta[:, 3:]
    u, f = x.view("u8"), np.isfinite(x)
    ok = np.ones(n, bool)
    for d in range(1, slots + 1):
        m = max(0, min(n, len(ta) - d))
        ok[:m] &= np.any((u[:m] != u[d:d + m]) & f[:m] & f[d:d + m], axis=1)
    bad = np.nonzero(~ok)[0]
    return {"slots": slots, "rows": n, "pass": int(ok.sum()), "fail": int(bad.size), "first_fail_row": int(bad[0]) if bad.size else None}


_d = distinct(np.array([[0, 0, 0, 1, 1, 1], [0, 0, 0, 2, 2, 2], [0, 0, 0, 2, 2, 2], [0, 0, 0, np.nan, 2, 2]]), 4, 1)
assert _d["pass"] == 2 and _d["first_fail_row"] == 1


def trans_rot(ta, tb):
    """(b) trans/rot (columns 1, 2). Init boundary = the first row after A's LAST row whose trans or rot differs (bits) from the row
    before (0 if none). Stationary rows (boundary.. common end): A vs B bit-identical count; init rows of B: non-finite count,
    first and last values bit-equal to A's. Envelope: NOT-EVALUATED (ENVELOPE)."""
    n = min(len(ta), len(tb))
    ua, ub = np.ascontiguousarray(ta[:, 1:3]).view("u8"), np.ascontiguousarray(tb[:, 1:3]).view("u8")
    ch = np.nonzero(np.any(ua[1:] != ua[:-1], axis=1))[0] + 1
    last = int(ch[-1]) if ch.size else None
    bd = last + 1 if last is not None else 0
    st = np.any(ua[bd:n] != ub[bd:n], axis=1) if bd < n else np.zeros(0, bool)
    k = min(bd, len(tb))
    return {"last_change_row_A": last, "boundary": bd, "stationary_rows": max(0, n - bd), "stationary_rows_differ": int(st.sum()),
            "first_stationary_diff": int(np.nonzero(st)[0][0]) + bd if st.any() else None,
            "init_rows_B": k, "init_nonfinite_B": int((~np.isfinite(tb[:k, 1:3])).sum()),
            "init_first_equal": bool(k and np.array_equal(ua[0], ub[0])), "init_last_equal": bool(k and np.array_equal(ua[k - 1], ub[k - 1])),
            "init_first_A": ta[0, 1:3].tolist() if k else None, "init_last_A": ta[k - 1, 1:3].tolist() if k else None,
            "init_first_B": tb[0, 1:3].tolist() if k else None, "init_last_B": tb[k - 1, 1:3].tolist() if k else None, "envelope": ENVELOPE}


def dir_files(d):
    """{name: {size, md5}} of every entry of a run dir (a subdir = {dir: True})."""
    r = {}
    for x in sorted(os.listdir(d)):
        p = os.path.join(d, x)
        r[x] = {"dir": True} if os.path.isdir(p) else {"size": os.path.getsize(p), "md5": md5f(p)}
    return r


def files_compare(da, db):
    """(b) every file by name: 'equal' / 'differ' (md5) / 'only A' / 'only B'. Returns {name: {status, A, B}}."""
    fa, fb = dir_files(da), dir_files(db)
    return dict((k, {"status": "only B" if k not in fa else "only A" if k not in fb else "equal" if fa[k] == fb[k] else "differ",
                     "A": fa.get(k), "B": fb.get(k)}) for k in sorted(set(fa) | set(fb)))


def find_text(d, needle=b"lost frames"):
    """Counter search: {file: [offsets of the needle, case-insensitive]} over every file of a run dir (empty list = NOT FOUND)."""
    return dict((x, [m.start() for m in re.finditer(re.escape(needle), open(os.path.join(d, x), "rb").read(), re.I)])
                for x in sorted(os.listdir(d)) if os.path.isfile(os.path.join(d, x)))


def y_source(G, qr_uid):
    """Graph fact: the source terminal wired to 'y' of Quotient & Remainder #qr_uid and that owner's stored obj fields (the graph
    JSON keeps uid/class/pos/owner only - a constant's VALUE is reported as absent unless a field holds it)."""
    T = G["terminals"]
    y = [t for t in T if t["owner_uid"] == qr_uid and t["term_name"] == "y"]
    src = [t for t in T if y and t["wire_uid"] == y[0]["wire_uid"] and t["is_source"]]
    o = [x for x in G["objs"] if src and int(x["uid"]) == int(src[0]["owner_uid"])]
    return {"qr": qr_uid, "y_term": y[0]["term_uid"] if y else None, "wire": y[0]["wire_uid"] if y else None,
            "src_owner": src[0]["owner_uid"] if src else None, "src_class": src[0]["owner_class"] if src else None,
            "obj": o[0] if o else None, "value_stored": bool(o and set(o[0]) - {"uid", "class", "pos", "owner"})}


def fact(tag, x):
    print("FACT %s %s" % (tag, json.dumps(x, default=str, ensure_ascii=False)[:1500]), flush=True)


def compare_bc(da, db, slots, out):
    """The whole (b)/(c) report of two run dirs (A = S1 side) with D = slots: tra parse + rows, MATCH + drop signature, DISTINCT,
    trans/rot, cal field rule, every file, counters. Prints FACT/ITEM lines, writes `out`, returns (report, items {label: bool})."""
    ia, ta = tra(da)
    ib, tb = tra(db)
    R = {"A": da, "B": db, "slots": slots, "tra": {"A": ia, "B": ib}}
    I = {"T tra both parse": bool(ia["parsed"] and ib["parsed"] and ia["dims"][1] == ib["dims"][1])}
    fact("TRA dims ('actual data points' = rows) A/B", [ia["dims"], ib["dims"]])
    if I["T tra both parse"]:
        R["xyz"] = xyz_match(ta, tb, slots)
        R["distinct"] = distinct(ta, R["xyz"]["common"], slots)
        R["trans_rot"] = trans_rot(ta, tb)
        fact("XYZ", R["xyz"])
        fact("DISTINCT", R["distinct"])
        fact("TRANSROT", R["trans_rot"])
        I["B1 X/Y/Z MATCH all common rows"] = R["xyz"]["rows_not_identical"] == 0
        I["C1 DISTINCT all common rows"] = R["distinct"]["fail"] == 0
        I["B3 trans/rot stationary rows bit-identical"] = R["trans_rot"]["stationary_rows_differ"] == 0
        I["B4 init rows of B finite, first+last equal A"] = (R["trans_rot"]["init_nonfinite_B"] == 0 and R["trans_rot"]["init_first_equal"]
                                                             and R["trans_rot"]["init_last_equal"])
    tds, top = cal_type()
    R["cal"] = cal_compare(cal(da), cal(db), tds, top)
    fact("CAL", R["cal"])
    I["B2 cal walk exact both, field found, 0 bytes differ outside it"] = (R["cal"]["field"]["A"]["consumed_exactly"] and
                                                                         R["cal"]["field"]["B"]["consumed_exactly"] and
                                                                         "field_offset" in R["cal"]["field"]["A"] and
                                                                         "field_offset" in R["cal"]["field"]["B"] and
                                                                         R["cal"]["outside_field_differing"] == 0)
    R["files"] = files_compare(da, db)
    fact("FILES", R["files"])
    I["B5 every file present in both dirs"] = all(v["status"] in ("equal", "differ") for v in R["files"].values())
    R["counters"] = {"lost_frames_text": {"A": find_text(da), "B": find_text(db)}}
    fact("COUNTERS 'lost frames' text offsets per file (empty = NOT FOUND)", R["counters"])
    for k, v in I.items():
        print("ITEM %-55s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    R["items"] = I
    json.dump(R, open(out, "w", encoding="utf-8"), indent=1, default=str, ensure_ascii=False)
    return R, I


# ==== card 170-a3-3 (PD409(b) init envelope + every other leg file, PD411(d)): compare_bc above is unchanged and CALLED.
# FOUND FIRST: trans_rot's envelope was NOT-EVALUATED (ENVELOPE); files_compare covers the run dir only.
def init_range(tb, k, limits):
    """(b) init envelope on B's first k rows (k = trans_rot's init_rows_B): trans (col 1) finite and inside the PI range of
    tools/bench/motor_limits.json (the motor_gate session's lo_mm..hi_mm), rot (col 2) finite only (no rotor range declared,
    PD411(d)); the ASI range has no tra column (cols: time, trans, rot, beads) - reported, not evaluated. Self-test: the assert below."""
    lo, hi = float(limits["pi"]["lo_mm"]), float(limits["pi"]["hi_mm"])
    tr, ro = tb[:k, 1], tb[:k, 2]
    fin = np.isfinite(tr)
    out = int(np.sum(fin & ((tr < lo) | (tr > hi))))
    return {"rows": int(k), "pi_range_mm": [lo, hi], "trans_nonfinite": int((~fin).sum()), "trans_outside_pi": out,
            "trans_min": float(np.nanmin(tr)) if fin.any() else None, "trans_max": float(np.nanmax(tr)) if fin.any() else None,
            "rot_nonfinite": int((~np.isfinite(ro)).sum()),
            "asi": "NOT-EVALUATED: no ASI column in tra (time, trans, rot, then beads); range %s..%s" % (limits["asi"]["sl"], limits["asi"]["su"]),
            "ok": bool(k) and int((~fin).sum()) == 0 and out == 0 and int((~np.isfinite(ro)).sum()) == 0}


_ir = init_range(np.array([[0, 1.0, 5.0], [0, 40.0, 5.0], [0, 2.0, np.nan]]), 3, {"pi": {"lo_mm": 0, "hi_mm": 39}, "asi": {"sl": 0, "su": 0}})
assert _ir["trans_outside_pi"] == 1 and _ir["rot_nonfinite"] == 1 and not _ir["ok"]


def compare_p6(da, db, slots, out, oa, ob, limits):
    """compare_bc (unchanged) plus the two PD409(b) items it lacked: B6 init rows of B inside the session's PI range, rot finite
    (init_range); B7 every OTHER file the legs wrote (each leg's --out dir: leg.json, clicks.json, the kept m8 jsons) by name with
    files_compare. Rewrites `out`; returns (report, items). Self-test: selftest() S9/S10."""
    R, I = compare_bc(da, db, slots, out)
    if "trans_rot" in R:
        R["init_range"] = init_range(tra(db)[1], R["trans_rot"]["init_rows_B"], limits)
        fact("INITRANGE", R["init_range"])
        I["B6 init rows of B: trans inside PI range, rot finite"] = R["init_range"]["ok"]
    R["leg_files"] = files_compare(oa, ob)
    fact("LEGFILES", R["leg_files"])
    I["B7 every other leg file present in both leg dirs"] = bool(R["leg_files"]) and all(v["status"] in ("equal", "differ")
                                                                                         for v in R["leg_files"].values())
    for k in ("B6 init rows of B: trans inside PI range, rot finite", "B7 every other leg file present in both leg dirs"):
        if k in I:
            print("ITEM %-55s %s" % (k, "PASS" if I[k] else "FAIL"), flush=True)
    R["items"] = I
    json.dump(R, open(out, "w", encoding="utf-8"), indent=1, default=str, ensure_ascii=False)
    return R, I


SELF_LEGS = os.path.join(HERE, "t0_legs", "c110f_replay_20260927_184600")


def selftest(slots):
    """PD409(f) self-test on the stored 110-7 legs: A = m8_out/replay_s1_20260927_184651, B = the run_dir of B's leg.json; expects
    4443 common rows, 0 X/Y/Z rows differing, DISTINCT all rows, cal differing only inside the walked field (5 bytes), the old
    main() G1-G3 PASS, the moved walk reproducing diag_c170_a2_2_cal.log (offset 857264, length 40), run dirs unchanged by md5."""
    G = {}
    A = os.path.join(HERE, "m8_out", "replay_s1_20260927_184651")
    rb = run_dirs(os.path.join(SELF_LEGS, "B_dispreplay_a1", "leg.json"))
    ra = run_dirs(os.path.join(SELF_LEGS, "A_S1replay_a1", "leg.json"))
    fact("LEG run_dir values A/B", [ra, rb])
    G["S0 leg A run_dir == the stored A dir, leg B has one run_dir (replay_s1_20260927_185846)"] = (
        [os.path.normcase(x) for x in ra] == [os.path.normcase(A)] and len(rb) == 1 and os.path.basename(rb[0]) == "replay_s1_20260927_185846")
    B = rb[0]
    h0 = dict((d, dir_files(d)) for d in (A, B))
    ok_main = main(A, B, os.path.join(HERE, "m8b_replay_selftest_main.json"))
    G["S1 old CLI main() G1-G3 PASS (unchanged path)"] = bool(ok_main)
    import motor_gate                                                                   # card 170-a3-3: the session's limit file
    R, I = compare_p6(A, B, slots, os.path.join(HERE, "m8b_replay_selftest_170.json"), os.path.join(SELF_LEGS, "A_S1replay_a1"),
                      os.path.join(SELF_LEGS, "B_dispreplay_a1"), motor_gate.load_limits())
    G["S2 4443 common rows"] = R.get("xyz", {}).get("common") == 4443
    G["S3 0 X/Y/Z rows differ (MATCH all)"] = I.get("B1 X/Y/Z MATCH all common rows") is True
    G["S4 DISTINCT all common rows (slots %d)" % slots] = I.get("C1 DISTINCT all common rows") is True
    fa, fb = R["cal"]["field"]["A"], R["cal"]["field"]["B"]
    G["S5 cal: walk 857264/40 both (diag_c170_a2_2_cal.log:45,60), 0 outside, 5 bytes differ"] = (
        fa.get("field_offset") == 857264 == fb.get("field_offset") and fa.get("field_length") == 40 == fb.get("field_length")
        and R["cal"]["outside_field_differing"] == 0 and R["cal"]["bytes_differing"] == 5)
    g = json.load(open(os.path.join(HERE, "graph_ring_p6_20261012_212645.json"), encoding="utf-8"))
    ys = y_source(g, 27373)
    fact("GRAPH ring counter Q&R #27373 'y' source (graph_ring_p6_20261012_212645.json:1, md5 %s)" % g.get("md5"), ys)
    G["S6 graph: Q&R #27373 y <- DigitalNumericConstant #27433"] = ys["src_owner"] == 27433 and ys["src_class"] == "DigitalNumericConstant"
    fact("S7 REPLACED by a citation (ring-p6.md PD411(c)): D = 20 from U13 + docs/d1/ring-p4b.md:21 at uid #27433; graph "
         "stores the value", ys["value_stored"])
    G["S9 init range on 110-7 B: PI range applied, %d init rows, 0 outside, rot finite" % R["trans_rot"]["init_rows_B"]] = (
        R.get("init_range", {}).get("rows") == R["trans_rot"]["init_rows_B"] > 0 and I.get("B6 init rows of B: trans inside PI range, rot finite") is True)
    G["S10 leg dirs: clicks.json + leg.json listed and compared"] = (sorted(R["leg_files"]) == ["clicks.json", "leg.json"]
                                                                      and I.get("B7 every other leg file present in both leg dirs") is True)
    h1 = dict((d, dir_files(d)) for d in (A, B))
    G["S8 110-7 run dirs unchanged (name, size, md5)"] = h0 == h1
    fact("RUNDIR md5", h1)
    for k, v in G.items():
        print("GATE %-90s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    return G


if __name__ == "__main__":
    A = sys.argv[1:]
    if "--slots" in A or "--selftest" in A:
        if "--slots" not in A:
            print("REFUSED: --slots D (the ring's slot count, a graph fact quoted with its uid) is required"); sys.exit(4)
        D = int(A[A.index("--slots") + 1])
        if "--selftest" in A:
            G = selftest(D)
            arts = ["m8b_replay_selftest_170.json", "m8b_replay_selftest_main.json"]
        else:
            o = A[A.index("--out") + 1] if "--out" in A else os.path.join(HERE, "m8b_replay_bc.json")
            G = compare_bc(A[0], A[1], D, o)[1]
            arts = [os.path.relpath(o, HERE)]
        bad = [k for k, v in G.items() if not v]
        print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                          [{"path": "tools/bench/" + x.replace("\\", "/"), "md5": md5f(os.path.join(HERE, x))} for x in arts])))
        sys.exit(0 if not bad else 1)
    o = A[A.index("--out") + 1] if "--out" in A else os.path.join(HERE, "m8b_replay_78.json")
    sys.exit(0 if main(A[0], A[1], o) else 1)
# ---
# labview: none
# hardware: none
# ---
