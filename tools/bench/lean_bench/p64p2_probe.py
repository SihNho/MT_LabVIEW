r"""p64p2_probe - lean task p64p2, READ-ONLY LabVIEW probe (nothing is saved; no camera, no motor).
  [A] `IMAQdx Configure Grab.vi` (vi.lib original, read only): connector pane (slot -> label, direction), execution properties,
      pane terminal types.
  [B] the three sources (A = D1_s1_copy 3e3d23ce, B = 15c664e3, BOBS90 257fb852), each COLD: every call whose callee basename is
      `IMAQdx Configure Grab.vi` (uid, owner), what feeds its `Session In` / `Number of Buffers` (+ the constant's value), the
      same for `IMAQdx Open Camera.vi` and `IMAQ Create.vi`; the wire-edge count (the cold reference for the build).
  [C] NI IMAQdx attribute examples (read only): every Property-node owner with its terminal names (the donor for the attribute
      write / read), plus owners whose terminals name `code` / `millisecond timer value` / `appended array` (logger donors).
    py tools/bgrun.py --material --max-min 25 --log tools/bench/lean_bench/p64p2_probe.log -- py -u tools/bench/lean_bench/p64p2_probe.py"""
import json, os, sys, time                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
CG = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Configure Grab.vi"
CG_MD5 = "306a6f92c10e66ff419b3e74a315c20e"
SRC = {"A": (L.S1, L.S1_MD5), "B": (os.path.join(LEAN, "D1_ring_p6latest_20261014_010104.vi"), "15c664e3eed1c580e05b13e42c86566f"),
       "BOBS90": (os.path.join(LEAN, "D1_ring_p64Bobs_20261014_114246.vi"), "257fb8522d557305ab6fe2aa11a04b61")}
EXD = r"C:\Program Files\NI\LVAddons\niimaqdx\1\examples\Vision Acquisition\NI-IMAQdx"
EX = [os.path.join(EXD, "Camera Attributes", f) for f in ("Getting Started with Attributes.vi", "Change Configuration Attributes While Acquiring.vi",
                                                           "Advanced Functionality with Attributes.vi")] + \
     [os.path.join(EXD, "Basic Acquisition", "Acquire Every Image.vi")]
WATCH = ("IMAQdx Configure Grab.vi", "IMAQdx Open Camera.vi", "IMAQ Create.vi")


def live(p):
    return WB.read_live(p, fs_pairs=[])


def feeders(lv, u):
    """{input terminal name: [(src owner uid, src owner class, src term name)]} of node #u"""
    by = {}
    for r in lv["terminals"]:
        if r["wire_uid"]:
            by.setdefault(r["wire_uid"], []).append(r)
    out = {}
    for r in lv["terminals"]:
        if int(r["owner_uid"]) == int(u) and not r["is_source"]:
            srcs = [(int(a["owner_uid"]), a["owner_class"], a["term_name"]) for a in by.get(r["wire_uid"], []) if a["is_source"]] if r["wire_uid"] else []
            out[r["term_name"]] = srcs
    return out


def body(s):
    s.start(); R = s.R
    s.head("[A] IMAQdx Configure Grab.vi (read only)")
    s.gate("A0 Configure Grab md5 == start record", K.md5(CG) == CG_MD5, K.md5(CG), fatal=True)
    pane = L.pane_dirs(CG); R["cg_pane"] = pane; s.fact("CG PANE %r" % pane)                 # noqa: E702
    props = {}
    with g.vi_ref(CG) as vi:
        for p in ("ReentrancyType", "IsReentrant", "ExecPriority", "PreferredExecSystem", "AllowDebugging", "ExecState"):
            try:
                v = getattr(vi, p); props[p] = v if isinstance(v, (int, float, str, bool)) else str(v)   # noqa: E702
            except Exception as e:                                                     # noqa: BLE001
                props[p] = "ERR %s" % str(e)[:80]
    R["cg_props"] = props; s.fact("CG PROPS %r" % props)                                  # noqa: E702
    try:
        lv = live(CG)
        R["cg_owners"] = sorted(set((int(r["owner_uid"]), r["owner_class"]) for r in lv["terminals"]))
        s.fact("CG body owners %r" % R["cg_owners"][:40])
        types = {}
        for r in lv["terminals"]:
            if "Terminal" in str(r.get("term_class")) or r["owner_class"] in ("TopLevelDiagram",):
                try:
                    types[r["term_name"]] = str(g.read_term_type(CG, int(r["term_uid"])))[:160]
                except Exception as e:                                                 # noqa: BLE001
                    types[r["term_name"]] = "ERR %s" % str(e)[:60]
        R["cg_types"] = types; s.fact("CG TYPES %r" % types)                              # noqa: E702
    except Exception as e:                                                             # noqa: BLE001
        s.fact("CG live read failed (locked diagram?): %s" % str(e)[:200])
    g.reset()
    s.gate("A1 Configure Grab md5 unchanged", K.md5(CG) == CG_MD5)
    s.dump()
    R["src"] = {}
    for tag, (p, m) in SRC.items():
        s.restart()
        s.head("[B %s] COLD read-only %s" % (tag, os.path.basename(p)))
        s.gate("B%s.0 md5 == %s" % (tag, m[:8]), K.md5(p) == m, fatal=True)
        s.gate("B%s.1 ExecState 1 cold" % tag, g.exec_state(p) == 1)
        c = L.census(p)
        lv = live(p)
        E = L.edges(lv, {})
        rec = {"edges": len(E), "census_n": len(c), "calls": {}}
        for w in WATCH:
            us = sorted(u for u, q in c.items() if os.path.basename(str(q)).lower() == w.lower())
            rec["calls"][w] = []
            for u in us:
                fd = feeders(lv, u)
                vals = {}
                for tn, srcs in fd.items():
                    for (su, scl, stn) in srcs:
                        if "Constant" in str(scl):
                            try:
                                vals[tn] = g.read_const_value(p, su)
                            except Exception as e:                                     # noqa: BLE001
                                vals[tn] = "ERR %s" % str(e)[:80]
                rec["calls"][w].append({"uid": u, "path": str(c[u]), "feeders": fd, "const_values": vals})
            s.fact("%s %s calls %r" % (tag, w, rec["calls"][w]))
        R["src"][tag] = rec
        s.fact("%s: %d edges, %d subVI calls" % (tag, len(E), len(c)))
        g.reset()
        s.gate("B%s.2 md5 unchanged after the read" % tag, K.md5(p) == m)
        s.dump()
    R["ex"] = {}
    for p in EX:
        s.restart()
        s.head("[C] example %s (read only)" % os.path.basename(p))
        m0 = K.md5(p)
        try:
            lv = live(p)
        except Exception as e:                                                         # noqa: BLE001
            s.fact("EX %s read failed %s" % (os.path.basename(p), str(e)[:150]))
            continue
        own = {}
        for r in lv["terminals"]:
            own.setdefault(int(r["owner_uid"]), []).append(r)
        hits = []
        for u, rs in own.items():
            names = [str(r["term_name"]) for r in rs]
            cls = rs[0]["owner_class"]
            if "Property" in str(cls) or any(n in ("code", "millisecond timer value") or "appended" in n or "Attribute" in n for n in names):
                h = {"uid": u, "class": cls, "terms": [(r["term_name"], bool(r["is_source"]), int(r["wire_uid"] or 0)) for r in rs]}
                hits.append(h)
                s.fact("EX %s #%d %s %r" % (os.path.basename(p), u, cls, h["terms"]))
        R["ex"][p] = {"md5": m0, "hits": hits, "census": dict((str(k), str(v)) for k, v in L.census(p).items())}
        s.fact("EX %s census %r" % (os.path.basename(p), R["ex"][p]["census"]))
        g.reset()
        s.gate("C %s md5 unchanged" % os.path.basename(p), K.md5(p) == m0)
        s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + tuple((k, p, m) for k, (p, m) in SRC.items()) + (("Configure Grab", CG, CG_MD5),)
    st = St(L.EMPTY, "6544be40470e80763764089fd2767f2a", "p64p2_probe", preload=False, deadline_min=24, work_dir=LEAN,
            work_name="scratch_p64p2_probe_%s.vi" % time.strftime("%Y%m%d_%H%M%S"), pins=pins, task="lean-p64p2",
            out_json=os.path.join(HERE, "p64p2_probe.json"))
    st.scratches.append(st.work)
    sys.exit(K.run(body, st))
