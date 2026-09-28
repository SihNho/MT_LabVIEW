r"""diag_c118_p0 - card 118-1 P0, READ-ONLY on a byte copy of the SAVED R2 (D1_l2_r2_20260928_110756.vi): the R2 graph dump
(prior art diag_c116b_props.py A3: wiki_build.read_live + k_contract_79.mloops + build_d1_v0.owner_of) -> tools/bench/graph_l2r2_saved_20260928.json,
then #13938 (IMAQ Create, PD234(b)) located by class + callee: its frame diagram, its inputs (Image Name source + value, Image Type source
+ value, Border Size, error in), its callee path (gscript.subvis on that frame), and every OTHER IMAQ Create's name source + value (#20436).
Readers: OpConstValue_v1 (string bytes, Constant cast), OpConstValueN_v1 (numeric/ring text + Representation, DigitalNumericConstant cast;
RingConstant measured, not assumed). Nothing is wired, deleted or saved; the copy is deleted; LabVIEW killed.
PREDICTION: G1 dump == R1 saved minus the 13 tunnels' rows (5827 - 26 = 5801 rows), every Diagram owner resolved; G2 exactly 2 IMAQ Create
SubVIs (#13938 in frame diagram 13236, #20436); G3 #13938 Image Name <- StringConstant #23583, Image Type <- RingConstant #13245, Border Size
and error in unwired; G4 #23583 value read with uid echo; G5 #13245 value read (class route reported); G6 #20436 name source read; LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c118_p0.log -- py -u tools/bench/diag_c118_p0.py"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K, vigraph as V                                                 # noqa: E401,E402
g = K.g
R2, R2M = os.path.join(g.CLAUDEDEV, "D1_l2_r2_20260928_110756.vi"), "7dac9f04ff4b65fa517e8e12f4bef5f3"
OUTG, OUTJ = os.path.join(HERE, "graph_l2r2_saved_20260928.json"), os.path.join(HERE, "diag_c118_p0.json")
G1 = json.load(open(os.path.join(HERE, "graph_l2r1_saved_20260928.json"), encoding="utf-8"))
LAB = json.load(open(os.path.join(HERE, "opconstvalue_labels.json"), encoding="utf-8"))
LABN = json.load(open(os.path.join(HERE, "opconstvaluen_v1_labels.json"), encoding="utf-8"))
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(R2, R2M, "scratch_c118_p0", preload=False, deadline_min=25, reserve_s=180, out_json=OUTJ, task="card 118-1 P0") if __name__ == "__main__" else None


def u8(v):
    try:
        return bytes(v) if v is not None and not isinstance(v, str) else b""
    except (TypeError, ValueError):
        return bytes(int(x) & 0xFF for x in v)


def read_str(t, uid):
    order = [int(o["uid"]) for o in g.report_all(t, "Constant")]
    if uid not in order:
        return {"err": "not in Constant traverse"}
    vi = g.op(os.path.join(g.CLAUDEDEV, "OpConstValue_v1.vi"))
    vi.SetControlValue(LAB["hex"], "POISON"); vi.SetControlValue("UID", 0); vi.SetControlValue(LAB["size"], False)   # noqa: E702
    vi.SetControlValue("vi path", t); vi.SetControlValue("Class Name", "Constant"); vi.SetControlValue("index", order.index(uid))   # noqa: E702
    g._run(vi)
    b = u8(vi.GetControlValue(LAB["u8"]))
    return {"uid": int(vi.GetControlValue("UID")), "hex": b.hex(), "text": b.decode("latin-1"), "err": str(g._err(vi, "error out") or "")[:120]}


def read_num(t, uid):
    out = {}
    for cls in ("DigitalNumericConstant", "RingConstant", "Constant"):
        order = [int(o["uid"]) for o in g.report_all(t, cls)]
        if uid not in order:
            out[cls] = "not in traverse"
            continue
        vi = g.op(os.path.join(g.CLAUDEDEV, "OpConstValueN_v1.vi"))
        vi.SetControlValue(LABN["text"], "POISON"); vi.SetControlValue(LABN["hex"], "POISON"); vi.SetControlValue(LABN["u8"], [])   # noqa: E702
        vi.SetControlValue(LABN["wire"], -1); vi.SetControlValue("UID", 0); vi.SetControlValue(LABN["size"], False)   # noqa: E702
        vi.SetControlValue("vi path", t); vi.SetControlValue("Class Name", cls); vi.SetControlValue("index", order.index(uid))   # noqa: E702
        try:                                           # plain try (no Stage): diag_c118_p1 imports these readers
            g._run(vi); err = g._err(vi, "error out") or ""                          # noqa: E702
        except Exception as e:                                                     # noqa: BLE001
            err = "EXC {0}".format(str(e)[:120])
        out[cls] = {"uid": int(vi.GetControlValue("UID")), "text": vi.GetControlValue(LABN["text"]), "repr": vi.GetControlValue(LABN["repr"]),
                    "hex": u8(vi.GetControlValue(LABN["u8"])).hex(), "wire": int(vi.GetControlValue(LABN["wire"])), "err": str(err)[:160]}
    return out


def body(_):
    s.start(); s.scratches.append(s.work)                                          # noqa: E702  read-only: the work copy is a scratch
    if os.path.exists(OUTG):                   # rerun: the dump of run 1 (same R2 md5, diag_c118_p0.log G1 PASS) is reused, not re-read
        gr = json.load(open(OUTG, encoding="utf-8")); s.fact("REUSED {0} md5 {1}".format(OUTG, K.md5(OUTG)))   # noqa: E702
        return probe(gr["terminals"])
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=G1["fs_tunnel_pairs"])
    loops, BD = K.mod("k_contract_79").mloops(s, s.work), K.mod("build_d1_v0")
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo = {}, list(diags)
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        v = s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(s.work, u, strict=False), ("?", 0))[0] or ("?", 0)
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    gr = {"vi": R2, "md5": R2M, "source": "tools/bench/diag_c118_p0.py (read_live + mloops + owner_of on a byte copy of the SAVED R2)", "terminals": lv["terminals"],
          "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": G1["fs_tunnel_pairs"], "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}
    DRY or (json.dump(gr, open(OUTG, "w", encoding="utf-8")), s.fact("WROTE {0} md5 {1}".format(OUTG, K.md5(OUTG))))
    T = lv["terminals"]
    s.gate("G1 dump: {0} rows (R1 saved 5827 - 26 = 5801), {1} objs, every Diagram owner resolved".format(len(T), len(lv["objs"])),
           len(T) == 5801 and all(O[d][0] != "?" for d in diags), (len(T), len(lv["objs"]), [d for d in diags if O[d][0] == "?"][:10]))
    probe(T)


def probe(T):
    byw = {}
    for r in T:
        r["wire_uid"] and byw.setdefault(int(r["wire_uid"]), []).append(r)
    src = lambda w: [x for x in byw.get(int(w or 0), []) if x["is_source"]]           # noqa: E731
    subs, DL = {}, [int(o["uid"]) for o in g.report_all(s.work, "Diagram")]
    for fd in sorted(set(int(r["frame_diagram"] or 0) for r in T if r["owner_class"] == "SubVI")):
        di = DL.index(fd) if fd in DL else 0
        for row in s.safe("subvis #{0}".format(fd), lambda: g.subvis(s.work, di, strict=False)[0], [])[0] or []:
            subs[int(row["uid"])] = (row.get("path"), fd)
    ic = sorted(u for u, (p, _fd) in subs.items() if str(p or "").lower().endswith("imaq create.vi"))
    s.fact("IMAQ CREATE callers {0}".format([(u, subs[u]) for u in ic]))
    s.gate("G2 exactly 2 IMAQ Create SubVIs: #13938 in frame diagram 13236 and #20436", ic == [13938, 20436] and subs[13938][1] == 13236, ic)
    inp = dict((r["term_name"], (int(r["term_uid"]), int(r["wire_uid"] or 0), [(x["owner_uid"], x["owner_class"]) for x in src(r["wire_uid"])]))
               for r in T if int(r["owner_uid"]) == 13938)
    s.fact("#13938 TERMS {0}".format(inp))
    s.gate("G3 #13938: Image Name <- StringConstant #23583, Image Type <- RingConstant #13245, Border Size + error in unwired",
           inp["Image Name"][2] == [(23583, "StringConstant")] and inp["Image Type"][2] == [(13245, "RingConstant")]
           and not inp["Border Size"][1] and not inp["error in (no error)"][1], inp)
    nm = read_str(s.work, 23583); s.fact("#23583 NAME {0}".format(nm))           # noqa: E702
    s.gate("G4 #23583 string read, uid echo, no error", nm.get("uid") == 23583 and not nm.get("err"), nm)
    rg = read_num(s.work, 13245); s.fact("#13245 RING {0}".format(json.dumps(rg, default=str)))   # noqa: E702
    s.gate("G5 #13245 value read by some class route with uid echo and no error", any(isinstance(v, dict) and v["uid"] == 13245 and not v["err"] for v in rg.values()), rg)
    other = [(r["term_name"], src(r["wire_uid"])) for r in T if int(r["owner_uid"]) == 20436 and r["term_name"] == "Image Name"]
    ou = [int(x["owner_uid"]) for _n, xs in other for x in xs]
    on = [dict(read_str(s.work, u), src=u) for u in ou if any(x["owner_class"] == "StringConstant" for _n, xs in other for x in xs)]
    s.fact("#20436 NAME SOURCE {0} -> {1}".format(other, on))
    s.gate("G6 #20436 Image Name source read", bool(on) and all(not x.get("err") for x in on), on)
    tv = dict((c, sorted(set([23583, 13245]) & set(int(o["uid"]) for o in g.report_all(s.work, c)))) for c in ("Node", "Constant", "DigitalNumericConstant"))
    s.fact("TRAVERSE membership of #23583/#13245: {0}".format(tv))
    s.R["p0"] = {"imaq_create": ic, "subs": dict((str(u), subs[u]) for u in ic), "t13938": inp, "name13938": nm, "ring13245": rg, "name20436": on}
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
