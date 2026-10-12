# ---
# labview: read
# hardware: none
# evidence: tools/bench/cards/brief_170-a2-1.md
# ---
r"""diag_c170_a2_1_f4 - card 170-a2-1 brief step 2: ONE read-only LabVIEW session on a NEVER-SAVED byte copy of claudeDev\D1_s1_copy.vi
(3e3d23ce): the TYPE of ClusterConstant #26159 'input cluster', the values of #26136 / #26126 / #26145, the type the NamedBundler #26446
carries. Nothing is saved, no VI of the target is run, the ORIGINAL is not opened.

Found before writing (CALLED): gscript.read_term_type (tools/gscript.py:4646, OpTermDataType_v0: Terminal.Data Type -> TD bytes incl.
labels) - the cluster-type reader; gscript.read_const_value (:4417) for the BooleanConstant #26126; prep_c156_a1_1_lib.Gate/md5;
bench_prep.labview_handles; stagexec.kill_labview_at_exit. Form = diag_c153_a2_6_orig_read.py (plain gscript on a byte copy): the stagekit
form (discard_work) is refused by guard_bash as VI-modifying - gate-fp fp-63, deduped by this card. NOT covered by a verb: #26136 is a
FixedConstant and #26145 an EnumConstant (docs/wiki/subvi/D1_s1_copy.json:66600,66610), neither in gscript.CONST_VALUE_CLASSES (:4412):
const_value_op() drives the EXISTING ops OpConstValue_v1 (base Constant cast) and OpConstValueRing_v0 (RingConstant cast) with those class
names; its body follows read_const_value's StringConstant / c118 branches (:4448-4474) - reported as a duplicate. Terminal uids:
D1_s1_copy.json:66336-66423 / 66585-66692. TD bytes are DECODED OFFLINE (diag_c170_a2_1_cal.py): a decoding error needs no second session.

PREDICTION CONTRACT: K0 no LabVIEW at start; C1 copy md5 == 3e3d23ce; RQ verbs/ops found; T1 #26156 (ClusterConstant out) type read,
echo, no error, lossless hex, top TD Cluster; T2 #26448 (bundler out) canon+sig == T1; T3 #26470 ('Date and time' sink) top TD String;
V1 #26126 Boolean value read; V2 #26136 value read as a string (TD 0x30) through OpConstValue_v1; #26145 value READ or NOT-READ is
reported (no verb exists; both ops tried once) - informational; types of #26133 / #26142 / #26123 read; H handles flat +-100 and gscript
refs live 0; G LabVIEW gone; D copy deleted; X D1_s1_copy.vi md5 unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c170_a2_1_f4.log -- py -u tools/bench/diag_c170_a2_1_f4.py"""
import json, os, shutil, subprocess, sys, time                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (ROOT, os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    _p in sys.path or sys.path.insert(0, _p)                                                 # noqa: E701
import gscript as g                                                                          # noqa: E402
import bench_prep as BP                                                                      # noqa: E402
import protocol as PR                                                                        # noqa: E402
import stagexec as SX                                                                        # noqa: E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi")
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
COPY = os.path.join(g.CLAUDEDEV, "scratch_c170_a2_1_f4_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
OUT = os.path.join(HERE, "diag_c170_a2_1_f4.json")
TERMS = {"cluster_const_out": 26156, "bundler_out": 26448, "bundler_date_in": 26470, "fixed_const_out": 26133,
         "enum_const_out": 26142, "bool_const_out": 26123}
_G = L.Gate(fatal_default=False)
R = {"copy": COPY}


def gate(label, ok, d=""):
    """prep_c156_a1_1_lib.Gate (returns None) plus the verdict, so a failed precondition can stop the body."""
    _G(label, ok, d)
    return bool(ok)


def fact(x):
    print("FACT " + str(x)[:3000], flush=True)


def lv_running():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()


def const_value_op(W, cls, uid, route):
    """Value of constant #uid of class `cls` through op `route` (OpConstValue_v1 base cast, or OpConstValueRing_v0). Read-only.
    Returns {route, cls, index, value, type, hex?, echo, err}."""
    i = g._uid_index(W, cls, uid)
    if route == "OpConstValue_v1":
        g._c97_paths()
        from build_opconstvalue_v1b import decode_flat
        lab = json.load(open(os.path.join(HERE, "opconstvalue_labels.json"), encoding="utf-8"))
        vi = g.op(os.path.join(g.CLAUDEDEV, "OpConstValue_v1.vi"))
        vi.SetControlValue(lab["hex"], "POISON"); vi.SetControlValue("UID", 0); vi.SetControlValue(lab["size"], False)   # noqa: E702
        vi.SetControlValue("vi path", W); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", i)   # noqa: E702
        g._run(vi)
        raw = vi.GetControlValue(lab["u8"])
        b = bytes(raw) if raw is not None and not isinstance(raw, str) else b""
        code, val, note = decode_flat(b) if b else (None, None, "no bytes")
        return {"route": route, "cls": cls, "index": i, "value": val, "type": "TD 0x%02x" % code if code is not None else None,
                "hex": b.hex(), "note": note, "echo": int(vi.GetControlValue("UID")), "err": str(g._err(vi, "error out") or "")}
    lab = json.load(open(g.C118_LABELS, encoding="utf-8"))[route]
    vi = g.op(os.path.join(g.CLAUDEDEV, route + ".vi"))
    g._set_common(vi, W, lab, cls, i)
    vi.SetControlValue(lab["UID"], 0)
    g._run(vi)
    v = vi.GetControlValue(lab["Value"])
    return {"route": route, "cls": cls, "index": i, "value": v, "type": type(v).__name__,
            "repr": int(vi.GetControlValue(lab["Repr"])) if lab.get("Repr") else None,
            "echo": int(vi.GetControlValue(lab["UID"])), "err": str(g._err(vi, lab["Err"]) or "")}


def safe(label, fn):
    try:
        return fn()
    except Exception as e:                                                                   # noqa: BLE001
        fact("%s raised %s: %s" % (label, type(e).__name__, str(e)[:300]))
        return {"exc": "%s: %s" % (type(e).__name__, str(e)[:300])}


def body():
    R["s1_md5_before"] = L.md5(S1)
    gate("X0 D1_s1_copy.vi md5 == 3e3d23ce", R["s1_md5_before"] == S1_MD5, R["s1_md5_before"])
    req = PR.check_requires({"requires": [{"kind": "verb", "name": "read_term_type"}, {"kind": "verb", "name": "read_const_value"},
                                          {"kind": "op", "name": "OpTermDataType_v0"}, {"kind": "op", "name": "OpConstValue_v1"},
                                          {"kind": "op", "name": "OpConstValueB_v0"}, {"kind": "op", "name": "OpConstValueRing_v0"}]})
    fact("RQ found %s" % [(x["name"], x["cite"]) for x in req["found"]])
    if not gate("RQ existing verbs + ops found (protocol.check_requires)", req["ok"], req["missing"]):
        return
    if not gate("K0 no LabVIEW running at start", not lv_running()) or not gate("K1 no stale copy", not os.path.exists(COPY), COPY):
        return
    shutil.copyfile(S1, COPY)
    if not gate("C1 ONE byte copy %s: md5 == 3e3d23ce" % os.path.basename(COPY), L.md5(COPY) == S1_MD5, L.md5(COPY)):
        return
    t0 = time.time()
    g.ensure_loaded(COPY)
    h0 = BP.labview_handles()
    fact("loaded copy in %.1f s; ExecState %s; handles %s; refs %s" % (time.time() - t0, g.exec_state(COPY), h0, g.ref_counts()))
    T = {}
    for key, tu in sorted(TERMS.items()):
        r = safe("read_term_type t%d" % tu, lambda u=tu: g.read_term_type(COPY, u))
        ty = r.get("types") or {}
        T[key] = {"term": tu, "echo": r.get("echo"), "err": r.get("err") or r.get("exc"), "hex_ok": r.get("hex_ok"),
                  "bytes_hex": r.get("bytes_hex"), "top_name": ty.get("top_name"), "canon": ty.get("canon"), "sig": ty.get("sig"),
                  "parse_err": ty.get("err"), "tds": ty.get("tds"), "top": ty.get("top")}
        fact("TYPE %s t%d: echo %s err %r hex_ok %s top %s canon %s | bytes %s" % (
            key, tu, r.get("echo"), T[key]["err"], r.get("hex_ok"), ty.get("top_name"), ty.get("canon"), r.get("bytes_hex")))
    R["types"] = T
    c, b, d = T["cluster_const_out"], T["bundler_out"], T["bundler_date_in"]
    gate("T1 #26159 out t26156 type read: echo, no error, lossless hex, top TD Cluster",
         c["echo"] == 26156 and not c["err"] and c["hex_ok"] and c["top_name"] == "Cluster", (c["echo"], c["err"], c["top_name"]))
    gate("T2 #26446 'output cluster' t26448 type == #26159 type (canon + label-exact sig)",
         bool(b["canon"]) and b["canon"] == c["canon"] and b["sig"] == c["sig"], (b["canon"] == c["canon"], b["sig"] == c["sig"]))
    gate("T3 #26446 'Date and time' t26470 type is String", d["echo"] == 26470 and not d["err"] and d["top_name"] == "String",
         (d["echo"], d["err"], d["top_name"]))
    V = {"26126": safe("read_const_value #26126", lambda: g.read_const_value(COPY, 26126))}
    fact("VALUE #26126 BooleanConstant: %s" % json.dumps(V["26126"], default=str))
    gate("V1 #26126 BooleanConstant value read (echo, no error, a bool)",
         V["26126"].get("echo") == 26126 and not V["26126"].get("err") and isinstance(V["26126"].get("value"), bool), V["26126"])
    V["26136"] = safe("OpConstValue_v1 FixedConstant #26136", lambda: const_value_op(COPY, "FixedConstant", 26136, "OpConstValue_v1"))
    fact("VALUE #26136 FixedConstant (OpConstValue_v1): %s" % json.dumps(V["26136"], default=str))
    gate("V2 #26136 FixedConstant value read as a string (echo, no error, TD 0x30)",
         V["26136"].get("echo") == 26136 and not V["26136"].get("err") and V["26136"].get("type") == "TD 0x30"
         and isinstance(V["26136"].get("value"), str), V["26136"])
    for rt in ("OpConstValue_v1", "OpConstValueRing_v0"):
        k = "26145 " + rt
        V[k] = safe("%s EnumConstant #26145" % rt, lambda r=rt: const_value_op(COPY, "EnumConstant", 26145, r))
        fact("VALUE #26145 EnumConstant via %s: %s" % (rt, json.dumps(V[k], default=str)))
    R["values"] = V
    h1 = BP.labview_handles()
    R["handles"], R["refs"] = [h0, h1], g.ref_counts()
    fact("HANDLES before/after the reads: %s -> %s; gscript refs %s" % (h0, h1, R["refs"]))
    gate("H handles flat +-100 over the reads, gscript refs live 0", h0 is not None and h1 is not None and abs(h1 - h0) <= 100
         and R["refs"].get("live") == 0, (h0, h1, R["refs"]))


if __name__ == "__main__":
    try:
        body()
    except Exception as e:                                                                   # noqa: BLE001
        import traceback
        traceback.print_exc()
        gate("no exception", False, "%s: %s" % (type(e).__name__, str(e)[:300]))
    finally:
        json.dump(R, open(OUT, "w", encoding="utf-8"), default=str, indent=1)
        R["gone"] = SX.kill_labview_at_exit()
        gate("G LabVIEW gone", R["gone"] and not lv_running())
        for _ in range(5):
            if not os.path.exists(COPY):
                break
            try:
                os.remove(COPY)
            except OSError as e:
                fact("copy delete failed: %s" % e)
                time.sleep(2)
        gate("D copy deleted (nothing saved)", not os.path.exists(COPY), os.path.basename(COPY))
        gate("X D1_s1_copy.vi md5 unchanged (3e3d23ce)", L.md5(S1) == S1_MD5, L.md5(S1))
        sys.exit(_G.result([{"path": os.path.relpath(OUT, ROOT).replace("\\", "/"), "md5": L.md5(OUT)}]))
