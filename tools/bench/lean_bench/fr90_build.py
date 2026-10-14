r"""fr90_build - lean task fr90 step 1 (2026-10-15): three leg copies whose ONLY change is the panel DEFAULT of the `Auto-Reset`
control (uid 17472 in the original) = False. ALL saves under claudeDev\bench\lean. Nothing inside a big VI's diagram is edited.
Per copy (A90r <- claudeDev\D1_s1_copy.vi 3e3d23ce, B90r <- bench\lean\D1_ring_p6latest_20261014_010104.vi 15c664e3,
BOBS90r <- bench\lean\D1_ring_p64Bobs_20261014_114246.vi 257fb852):
  fresh LabVIEW -> byte copy (md5 == source) -> load the COPY: panel rows (panel_wiring), every top-level panel value, callee
  census, wire edges, VI props, ExecState -> find `Auto-Reset` by label (exactly one CONTROL) + uid 17472 -> make_default
  {Auto-Reset: False} (set, Make Current Values Default, save, read back) -> fresh LabVIEW -> COLD: the same reads on the saved
  copy -> diff: panel values differ in exactly {Auto-Reset: True -> False}, panel rows equal, census equal, edges equal, props
  equal, ExecState 1 -> md5 pinned; source md5 unchanged.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/lean_bench/fr90_build.log -- py -u tools/bench/lean_bench/fr90_build.py"""
import hashlib, json, os, shutil, sys, time                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
import latest_build as LB                                                                # noqa: E402 (helpers only)
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = LB.LEAN
STATE = os.path.join(HERE, "fr90_state.json")
ST = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
TS = ST.get("ts") or time.strftime("%Y%m%d_%H%M%S")
EMPTY, EMPTY_MD5 = L.EMPTY, "6544be40470e80763764089fd2767f2a"
SRC = {"A90r": (L.S1, L.S1_MD5, "D1_s1_fr90A_%s.vi"),
       "B90r": (os.path.join(LEAN, "D1_ring_p6latest_20261014_010104.vi"), "15c664e3eed1c580e05b13e42c86566f", "D1_ring_fr90B_%s.vi"),
       "BOBS90r": (os.path.join(LEAN, "D1_ring_p64Bobs_20261014_114246.vi"), "257fb8522d557305ab6fe2aa11a04b61", "D1_ring_fr90Bobs_%s.vi")}
AR, AR_UID = "Auto-Reset", 17472
PROPS = ("ReentrancyType", "IsReentrant", "ExecPriority", "PreferredExecSystem", "AllowDebugging")
INV = os.path.join(os.path.dirname(HERE), "d0_inventory.json")


def save_state():
    ST["ts"] = TS
    json.dump(ST, open(STATE, "w", encoding="utf-8"), indent=1, default=str)


def live(p):
    return WB.read_live(p, fs_pairs=[])


def props(t):
    out = {}
    with g.vi_ref(t) as vi:
        for p in PROPS:
            try:
                v = getattr(vi, p); out[p] = v if isinstance(v, (int, float, str, bool)) else str(v)    # noqa: E702
            except Exception as e:                                                     # noqa: BLE001
                out[p] = "ERR %s" % str(e)[:60]
    return out


def vkey(v):
    """a comparable, short form of a panel value (md5 of its repr when long)"""
    r = repr(v)
    return r if len(r) <= 120 else "md5:%s len %d" % (hashlib.md5(r.encode("utf-8", "replace")).hexdigest(), len(r))


def snapshot(t):
    """panel rows + every top-level panel value (labels from panel_wiring, plus the d0 inventory's control labels)"""
    rows = g.panel_wiring(t)
    labels = [r["label"] for r in rows]
    try:
        inv = [r["label"] for r in json.load(open(INV, encoding="utf-8")).get("panel_rows") or [] if r.get("label")]
    except Exception:                                                                  # noqa: BLE001
        inv = []
    labs = []
    for lab in labels + inv:
        if lab and lab not in labs:
            labs.append(lab)
    vals = {}
    with g.vi_ref(t) as vi:
        for lab in labs:
            try:
                vals[lab] = vkey(vi.GetControlValue(lab))
            except Exception as e:                                                     # noqa: BLE001
                vals[lab] = "ERR %s" % str(e)[:80]
    prow = sorted((r["label"], r["indicator"], r["uid"], r["is_source"], r["wire"]) for r in rows)
    return {"rows": prow, "values": vals, "ar_rows": [r for r in rows if r["label"] == AR]}


def build(s, tag):
    src, smd5, pat = SRC[tag]
    dst = os.path.join(LEAN, pat % TS)
    s.head("[%s] %s -> %s" % (tag, os.path.basename(src), os.path.basename(dst)))
    s.gate("%s.0 source md5 == pin %s" % (tag, smd5[:8]), K.md5(src) == smd5, fatal=True)
    shutil.copyfile(src, dst)
    s.gate("%s.1 byte copy md5 == source" % tag, K.md5(dst) == smd5, dst, fatal=True)
    g.ensure_loaded(dst)
    s.gate("%s.2 ExecState 1 before" % tag, s.es("%s before" % tag, dst) == 1, fatal=True)
    S0 = snapshot(dst)
    ar = S0["ar_rows"]
    s.fact("%s Auto-Reset rows %r; value %r" % (tag, ar, S0["values"].get(AR)))
    s.gate("%s.3 exactly one panel object labelled %r, a CONTROL, uid %d" % (tag, AR, AR_UID),
           len(ar) == 1 and ar[0]["indicator"] is False and int(ar[0]["uid"]) == AR_UID, ar, fatal=True)
    s.gate("%s.4 its current (= saved default) value is True" % tag, S0["values"].get(AR) == "True", S0["values"].get(AR), fatal=True)
    c0 = L.census(dst); E0 = L.edges(live(dst), {}); P0 = props(dst)                     # noqa: E702
    s.fact("%s before: %d panel rows, %d values (%d ERR), %d callees, %d edges, props %r"
           % (tag, len(S0["rows"]), len(S0["values"]), sum(1 for v in S0["values"].values() if v.startswith("ERR")), len(c0), len(E0), P0))
    r = g.make_default(dst, {AR: False})
    s.fact("%s make_default -> %r" % (tag, r))
    g.reset()
    m = K.md5(dst)
    s.fact("SAVED %s md5 %s" % (dst, m))
    s.gate("%s.5 source md5 unchanged" % tag, K.md5(src) == smd5, fatal=True)
    return {"path": dst, "md5": m, "src": src, "src_md5": smd5, "S0": S0, "census": dict((str(k), v) for k, v in c0.items()),
            "edges_set": sorted(E0), "props": P0}


def cold(s, tag, rec):
    p = rec["path"]
    s.head("[%s COLD] %s" % (tag, os.path.basename(p)))
    s.gate("%s.C0 md5 as saved" % tag, K.md5(p) == rec["md5"], fatal=True)
    s.gate("%s.C1 ExecState 1 COLD" % tag, g.exec_state(p) == 1)
    S1 = snapshot(p)
    S0 = rec["S0"]
    dv = dict((k, (S0["values"].get(k), S1["values"].get(k))) for k in set(S0["values"]) | set(S1["values"])
              if S0["values"].get(k) != S1["values"].get(k))
    s.fact("%s COLD value diff %r" % (tag, dv))
    s.gate("%s.C2 COLD panel values differ in exactly {Auto-Reset: True -> False}" % tag, dv == {AR: ("True", "False")}, dv)
    s.gate("%s.C3 COLD panel rows (label, ind, uid, is_source, wire) == before (%d)" % (tag, len(S0["rows"])),
           [list(x) for x in S1["rows"]] == [list(x) for x in S0["rows"]])
    c1 = dict((str(k), v) for k, v in L.census(p).items())
    s.gate("%s.C4 COLD callee census == before (%d)" % (tag, len(c1)), c1 == rec["census"],
           sorted(set(c1.items()) ^ set(rec["census"].items()))[:6])
    E1 = L.edges(live(p), {})
    E0 = set(tuple(e) for e in rec["edges_set"])
    s.gate("%s.C5 COLD wire edges == before (%d)" % (tag, len(E0)), E1 == E0, (sorted(E1 - E0)[:6], sorted(E0 - E1)[:6]))
    P1 = props(p)
    s.gate("%s.C6 COLD VI props == before" % tag, P1 == rec["props"], (P1, rec["props"]))
    g.reset()
    s.gate("%s.C7 md5 unchanged by the cold reads" % tag, K.md5(p) == rec["md5"])
    s.gate("%s.C8 source md5 unchanged" % tag, K.md5(rec["src"]) == rec["src_md5"])
    return {"value_diff": dv, "rows": len(S1["rows"]), "values": len(S1["values"]),
            "values_err": sum(1 for v in S1["values"].values() if v.startswith("ERR")), "callees": len(c1), "edges": len(E1)}


def body(s):
    s.start(); R = s.R
    ST.setdefault("copies", {})
    for tag in ("A90r", "B90r", "BOBS90r"):
        if tag in ST["copies"]:
            continue
        s.restart()
        ST["copies"][tag] = build(s, tag); save_state(); s.dump()                        # noqa: E702
    ST.setdefault("cold", {})
    for tag in ("A90r", "B90r", "BOBS90r"):
        s.restart()
        ST["cold"][tag] = cold(s, tag, ST["copies"][tag]); save_state(); s.dump()        # noqa: E702
    R["copies"] = dict((k, {"path": v["path"], "md5": v["md5"], "src_md5": v["src_md5"]}) for k, v in ST["copies"].items())
    R["cold"] = ST["cold"]
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + tuple(("src " + k, p, m) for k, (p, m, _n) in SRC.items()) + (("EMPTY_v0", EMPTY, EMPTY_MD5),)
    work = os.path.join(LEAN, "scratch_fr90_work_%s.vi" % time.strftime("%H%M%S"))
    st = St(EMPTY, EMPTY_MD5, "fr90_build", preload=False, deadline_min=58, work_dir=LEAN, work_name=os.path.basename(work), pins=pins,
            task="lean-fr90", out_json=os.path.join(HERE, "fr90_build.json"))
    st.scratches.append(st.work)
    sys.exit(K.run(body, st))
