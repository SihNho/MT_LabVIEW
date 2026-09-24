r"""m8b_replay_compare - card 78-3 R2/R3 (m8 plan PD13(d), PD17(b'), PD22(d)): join the S1-replay and S3-replay tra rows on
iteration index and test X/Y/Z bit-identity. No LabVIEW. FOUND FIRST: drive_m8.tra_rows (header end marker 'not in z!)',
binary f64 rows time,trans,rot + N x (x,y,z)); this adds the layout read (2 x I32 little-endian dims, then <f8 row-major,
m8_s1_p3.json:110-112 rem 8 = the dims prefix) and the join.
    py tools/bench/m8b_replay_compare.py <run_dir_s1> <run_dir_s3> [--out tools/bench/m8b_replay_78.json]
PREDICTION: G1 both tra parse (dims product == data length); G2 >= 1000 common rows; G3 zero rows with X/Y/Z not
bit-identical over the common prefix; cal files: FACT (md5 equal or first differing byte offset)."""
import hashlib, json, os, struct, sys                                                   # noqa: E401
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


if __name__ == "__main__":
    A = sys.argv[1:]
    o = A[A.index("--out") + 1] if "--out" in A else os.path.join(HERE, "m8b_replay_78.json")
    sys.exit(0 if main(A[0], A[1], o) else 1)
