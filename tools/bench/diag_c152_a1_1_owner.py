# ---
# labview: read
# hardware: none
# ---
r"""diag_c152_a1_1_owner - card 152-a1-1 (PD368(c)): ONE read-only owner read on a fresh load of P4 s08 (f99e8414; the stagekit
dated work copy is a never-saved byte copy, deleted at close - the same skeleton as diag_c151_a1_1_graph.py, which wrote graph 44858dbf).
Existing pieces, grepped first: OpOwnerChain_v1 driven by build_opownerchain_v1.read_owner (OBSERVED line, identity echo uid_back),
build_d1_v0.owner_of(strict=True) = the strict-echo owner_of gscript uses; stagesim.fs_measured_state.fs_parent = face-derived diagram.
Reads: (a) FS #29721, (b) its frame #29869, (c) CONTROL: the lowest-uid FS other than 29721 that has a face-derived parent.
PREDICTION: (a) class 'Diagram', owner uid != 0, echo 29721, strict owner_of agrees; (b) as graph owners: ('FlatSequenceFrame', 0) (fact
only); (c) class 'Diagram', owner uid == fs_parent, echo == control uid; handles flat +-100 over the reads; input md5 unchanged.
Derived graph file written ONLY if (a) holds: graph text byte-for-byte + top-level keys fs_owner_read / fs_owner_read_cite; it loads
through stagesim.base_state / fs_measured_state and vigraph.reach; graph 44858dbf unchanged.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c152_a1_1_owner.log -- py -u tools/bench/diag_c152_a1_1_owner.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, vigraph as V, stagesim as SS                                           # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c152_a1_1_owner_plan.json"), encoding="utf-8"))
BED, BEDM = PL["input"]["vi"], PL["input"]["md5"]
GRP, GRM, OUT = os.path.join(ROOT, PL["graph"]["path"]), PL["graph"]["md5"], os.path.join(ROOT, PL["graph"]["derived"])
LOG, FS, FR = PL["read_log"], int(PL["fs"]), int(PL["frame"])
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c152_a1_1_owner_p4s08", preload=False, deadline_min=10, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c152_a1_1_owner.json"), task="card 152-a1-1 owner read")
GR = json.load(open(GRP, encoding="utf-8"))
M = SS.fs_measured_state(GR)
CTL = min(int(f) for f in M["fs_parent"] if int(f) != FS)


def read(W, uid):
    OB, BD = K.mod("build_opownerchain_v1"), K.mod("build_d1_v0")
    labels = json.load(open(BD.LABELS, encoding="utf-8"))
    saved = OB.MAIN
    try:
        OB.MAIN = W
        return OB.read_owner(g.op(BD.OP_OWNER), labels, uid)
    finally:
        OB.MAIN = saved


def line_of(marker):
    try:
        for i, ln in enumerate(open(os.path.join(ROOT, LOG), encoding="utf-8", errors="replace"), 1):
            if marker in ln:
                return i
    except Exception:                                                                      # noqa: BLE001
        return None


def body(_):
    s.fact("input md5 before: {0}; graph md5 {1}; control FS #{2} face-derived diagram #{3} (borders {4})".format(
        K.md5(BED), K.md5(GRP), CTL, M["fs_parent"][CTL], sorted(u for u, b in M["borders"].items() if b.get("fs") == CTL)))
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    bp = K.mod("bench_prep"); h0 = bp.labview_handles()                                      # noqa: E702
    s.fact("MEM after load: {0} MB private; handles {1}".format(round((K.private_bytes() or 0) / 1e6, 1), h0))
    ra, rb, rc = read(W, FS), read(W, FR), read(W, CTL)
    st = s.safe("strict owner_of #{0}".format(FS), lambda: K.mod("build_d1_v0").owner_of(W, FS, strict=True), None)
    h1 = bp.labview_handles()
    s.R["reads"] = {"fs": ra, "frame": rb, "control": rc, "strict": [list(st[0]) if st[0] else None, st[1]], "handles": [h0, h1]}
    for tag, r in (("FS", ra), ("FRAME", rb), ("CONTROL", rc)):
        s.fact("READ {0} uid {1}: class {2!r} owner uid {3} echo {4!r}#{5} errs {6!r} err {7!r}".format(
            tag, r["uid"], r["ownercls"], r["owner_uid"], r["cls_back"], r["uid_back"], r["errs"][:80], r["err"][:60]))
    okA = ra["ownercls"] == "Diagram" and ra["owner_uid"] != 0 and ra["uid_back"] == FS
    s.gate("A FS #{0} read: class Diagram, owner uid != 0, echo == {0}".format(FS), okA,
           (ra["ownercls"], ra["owner_uid"], ra["uid_back"], ra["errs"][:80]))
    s.gate("A2 strict owner_of #{0} agrees with the read".format(FS), st[0] is not None and tuple(st[0]) == (ra["ownercls"], ra["owner_uid"]), st)
    s.fact("B frame #{0} read ({1!r}, {2}) vs graph owners {3}".format(FR, rb["ownercls"], rb["owner_uid"], GR["owners"].get(str(FR))))
    s.gate("C control FS #{0} read == face-derived diagram #{1}, echo == {0}".format(CTL, M["fs_parent"][CTL]),
           rc["ownercls"] == "Diagram" and rc["owner_uid"] == M["fs_parent"][CTL] and rc["uid_back"] == CTL,
           (rc["ownercls"], rc["owner_uid"], rc["uid_back"]))
    s.gate("H handles flat +-100 over the reads", h0 is not None and h1 is not None and abs(h1 - h0) <= 100, (h0, h1))
    s.gate("X input md5 unchanged", K.md5(BED) == BEDM, K.md5(BED))
    if not okA:
        s.fact("NO derived file written: read A is UNMEASURED (PD368(c))")
        return s.dump()
    ln = line_of("OBSERVED uid {0} ->".format(FS))
    cite = {"read_log": "{0}:{1}".format(LOG, ln) if ln else "{0} (marker 'OBSERVED uid {1} ->')".format(LOG, FS),
            "op": "OpOwnerChain_v1 via build_opownerchain_v1.read_owner + build_d1_v0.owner_of(strict=True)",
            "vi_md5": BEDM, "graph_md5": GRM, "echo": [ra["cls_back"], ra["uid_back"]], "card": "152-a1-1"}
    src = open(GRP, encoding="utf-8").read()
    s.gate("D0 graph text ends with '}'", src.rstrip().endswith("}"), src[-20:])
    txt = src.rstrip()[:-1] + ', "fs_owner_read": ' + json.dumps({str(FS): ["Diagram", int(ra["owner_uid"])]}) + \
        ', "fs_owner_read_cite": ' + json.dumps(cite) + "}"
    open(OUT, "w", encoding="utf-8").write(txt)
    d = json.load(open(OUT, encoding="utf-8"))
    base = dict((k, v) for k, v in d.items() if k not in ("fs_owner_read", "fs_owner_read_cite"))
    s.gate("D1 derived file == graph + 2 keys (prefix byte-identical)", base == GR and txt.startswith(src.rstrip()[:-1]), sorted(set(d) - set(GR)))
    bs = s.safe("stagesim.base_state", lambda: SS.base_state(d), None)
    fm = s.safe("stagesim.fs_measured_state", lambda: SS.fs_measured_state(d), None)
    rv = s.safe("vigraph.reach", lambda: V.reach(d, []), None)
    s.gate("D2 derived file loads (base_state, fs_measured_state, vigraph.reach)", bs[0] is not None and fm[0] is not None and not rv[1],
           (bs[1], fm[1], rv[1]))
    s.fact("D2 base_state fs_unmeasured {0} (stagesim not yet extended, PD368(c)); owners[{1}] {2}".format(
        (bs[0] or {}).get("fs_unmeasured"), FS, (bs[0] or {}).get("owners", {}).get(str(FS))))
    s.gate("D3 graph 44858dbf unchanged", K.md5(GRP) == GRM, K.md5(GRP))
    s.R["derived"] = {"path": os.path.relpath(OUT, ROOT), "md5": K.md5(OUT), "cite": cite}
    s.fact("WROTE {0} md5 {1}".format(OUT, K.md5(OUT)))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
