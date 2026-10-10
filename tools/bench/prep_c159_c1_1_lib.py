# ---
# labview: none
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/brief_159-c1-1.md
# ---
r"""prep_c159_c1_1_lib - card 159-c1-1 (OFFLINE, json only): the "next step of a split plan on the REAL graph of the previous step's adopted
file" mapping, ONCE. Until now it lived as inline copies in module-level makers (prep_c154_a4_1_mk.py:95-172, prep_c155_a2_1_mk.py:95-181):
  made_symbols(acts)                      -> the 'new:' symbols the rows themselves create (aliases + SR L/R)
  used_symbols(acts, made)                -> the earlier-step symbols the rows reference ('new:X' or 'new:X.f<k>')
  map_symbols(used, sym, bound, graph)    -> (REAL {symbol: real uid}, bad, lines): symbol -> sim uid (previous step's sim end state.sym) ->
                                             real uid (`bound` {sim uid: real uid}: a creation map or STEPX lines); a frame symbol must be
                                             an owners entry under the mapped case, any other uid must own rows or an obj in the real graph
  map_frames(acts, all_acts, sym, bound, owners) -> (FMAP, bad, lines): a `frame` NAME on an end whose tunnel sits on an earlier-step case
                                             -> '#<real frame diagram uid>' checked == stagesim.base_case_frames(owners, real case)[k] (PD378)
  apply_map(acts, REAL, FMAP)             -> the rows with every earlier-step symbol replaced (string address 'new:X.t' -> {'uid', 'term'}),
                                             frame names replaced by '#<uid>'; every other field (why included) kept
  bound_from_cmap(path)                   -> {sim uid: real uid} over obj/diag/term of ONE creation map (stage_prerun.read_creation_map)
Self-test (--selftest): replays card 155-a2-1's recorded case - P5-1b rows 21..32 of plan_ring_p5s01_in.json mapped with the P5-1a sim end
sym + the STEPX `bound` lines of diag_c154_p5s01a_scratch.log on graph bd67a511 == the actions of plan_ring_p5s01b.json 75a77a00. PREDICTION 3/0.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c159_c1_1_lib.log -- py -u tools/bench/prep_c159_c1_1_lib.py --selftest"""
import copy, hashlib, json, os, re, sys                                                      # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
FRAME_SYM = re.compile(r"\.f[0-9]+$")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731


def made_symbols(acts):
    """The 'new:' symbols the rows create: every `as` alias, plus <as>L / <as>R of an add_shift_reg. Self-test: --selftest."""
    return set("new:" + a["as"] for a in acts if a.get("as")) | set("new:" + a["as"] + s for a in acts if a.get("op") == "add_shift_reg" for s in "LR")


def _head(x):
    return x if FRAME_SYM.search(x) else x.split(".", 1)[0]


def used_symbols(acts, made):
    """Sorted earlier-step symbols the rows reference: 'new:X' (address heads) or 'new:X.f<k>' (frame diagrams), minus `made`. Self-test: --selftest."""
    acc = set()

    def walk(x):
        if isinstance(x, str) and x.startswith("new:"):
            acc.add(_head(x))
        elif isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    walk(acts)
    return sorted(s for s in acc if s not in made)


def map_symbols(used, sym, bound, graph):
    """(REAL, bad, lines): each used symbol -> sim uid (sym) -> real uid (bound); a frame symbol's real uid must be an owners entry
    ['CaseStructure', <the mapped case>], any other must own terminal rows or an obj in `graph`. Self-test: --selftest."""
    own = graph.get("owners") or {}
    objs = set(int(o["uid"]) for o in graph.get("objs") or [])
    REAL, bad, lines = {}, [], []
    for s in used:
        su = sym.get(s)
        ru = bound.get(su) if su is not None else None
        if ru is None:
            bad.append((s, su, "no sim uid / no bound entry"))
            continue
        if FRAME_SYM.search(s):
            ow = own.get(str(ru))
            cs = s.rsplit(".", 1)[0]
            ok = bool(ow) and ow[0] == "CaseStructure" and int(ow[1]) == REAL.get(cs, bound.get(sym.get(cs)))
            lines.append("MAP {0} -> sim {1} -> real diagram #{2}; owners entry {3}".format(s, su, ru, ow))
        else:
            rr = [r for r in graph["terminals"] if int(r["owner_uid"]) == int(ru) or int(r["term_uid"]) == int(ru)]
            ok = bool(rr) or int(ru) in objs
            lines.append("MAP {0} -> sim {1} -> real #{2} ({3} rows; obj {4})".format(s, su, ru, len(rr), int(ru) in objs))
        REAL[s] = ru
        if not ok:
            bad.append((s, su, ru))
    return REAL, bad, lines


def map_frames(acts, all_acts, sym, bound, owners, default_frames=("False", "True")):
    """(FMAP {(action id, end uid): {...,'addr': '#<uid>'}}, bad, lines): a `frame` name on an end whose tunnel (`tunnel` action in all_acts)
    sits on a case created in all_acts -> index in that case's `frames` -> '<case>.f<k>' -> sim -> real diagram, checked against
    stagesim.base_case_frames(owners, real case)[k]. A tunnel made by the rows on a case they also make is not mapped (left as written).
    Self-test: --selftest."""
    import stagesim as SS
    tun_case = dict(("new:" + a["as"], a.get("loop")) for a in all_acts if a.get("op") == "tunnel" and a.get("as"))
    case_fr = dict(("new:" + a["as"], list(a.get("frames") or default_frames)) for a in all_acts
                   if a.get("op") == "create" and a.get("class") == "CaseStructure" and a.get("as"))
    made = made_symbols(acts)
    FMAP, bad, lines = {}, [], []
    for a in acts:
        for e in (a.get("src"), a.get("dst")):
            if not (isinstance(e, dict) and e.get("frame") is not None):
                continue
            cs = tun_case.get(e.get("uid"))
            if cs in made:
                continue
            fl = case_fr.get(cs) or []
            if cs is None or e["frame"] not in fl:
                bad.append((a["id"], e))
                continue
            k = fl.index(e["frame"])
            fs = "{0}.f{1}".format(cs, k)
            ru, rc = bound.get(sym.get(fs)), bound.get(sym.get(cs))
            gfr = SS.base_case_frames(owners, rc) if rc is not None else []
            ok = ru is not None and len(gfr) > k and gfr[k] == ru
            FMAP[(a["id"], e["uid"])] = {"case_sym": cs, "frame_name": e["frame"], "index": k, "frame_sym": fs, "sim": sym.get(fs),
                                         "real_frame": ru, "real_case": rc, "graph_frames": gfr, "ok": ok, "addr": "#{0}".format(ru)}
            lines.append("FRM {0} end {1}: frame {2!r} = index {3} of {4} -> {5} -> sim {6} -> real #{7}; graph frames of #{8} {9}: {10}".format(
                a["id"], e["uid"], e["frame"], k, cs, fs, sym.get(fs), ru, rc, gfr, ok))
            if not ok:
                bad.append((a["id"], e, ru, gfr))
    return FMAP, bad, lines


def apply_map(acts, REAL, FMAP):
    """The rows with earlier-step symbols -> real uids (string address 'new:X.t' in src/dst -> {'uid': real, 'term': 't'}) and mapped frame
    names -> '#<uid>'. Self-test: --selftest."""
    def sub(x, key=None):
        if isinstance(x, str) and x.startswith("new:"):
            h = _head(x)
            if h in REAL:
                if key in ("src", "dst") and "." in x:
                    return {"uid": REAL[h], "term": x.split(".", 1)[1]}
                return REAL[h]
            return x
        if isinstance(x, dict):
            return dict((k, sub(v, k)) for k, v in x.items())
        if isinstance(x, list):
            return [sub(v) for v in x]
        return x
    out = []
    for r in acts:
        a = sub(copy.deepcopy(r))
        for k_ in ("src", "dst"):
            if isinstance(r.get(k_), dict) and r[k_].get("frame") is not None and (r["id"], r[k_]["uid"]) in FMAP:
                a[k_] = dict(a[k_], frame=FMAP[(r["id"], r[k_]["uid"])]["addr"])
        out.append(a)
    return out


def bound_from_cmap(path):
    """{sim uid: real uid} over the obj / diag / term entries of ONE creation-map/1 file, read by stage_prerun.read_creation_map; a sim id in
    two kinds with different real uids raises ValueError. Self-test: the maker's MAP gate (needs a live map)."""
    import stage_prerun as SPR
    _h, ent, _s = SPR.read_creation_map(path)
    out = {}
    for k in ("obj", "diag", "term"):
        for s, e in ent[k].items():
            if s in out and out[s] != int(e["real"]):
                raise ValueError("creation map {0}: sim {1} -> {2} and {3}".format(path, s, out[s], e["real"]))
            out[s] = int(e["real"])
    return _h, out


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
    import prep_c156_a1_1_lib as L                                                            # Gate (one copy)
    import stagexec as SX                                                                     # noqa: F401
    g = L.Gate(fatal_default=False)
    B = os.path.join(ROOT, "tools", "bench")
    SIN, PA, PB = J(os.path.join(B, "plan_ring_p5s01_in.json")), J(os.path.join(B, "plan_ring_p5s01a.json")), os.path.join(B, "plan_ring_p5s01b.json")
    GR = J(os.path.join(B, "graph_ring_p5s01a_20261009_103621.json"))
    last = max((PA.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
    SYM = J(last["path"])["state"]["sym"]
    BOUND = {}
    for ln in open(os.path.join(B, "diag_c154_p5s01a_scratch.log"), encoding="utf-8", errors="replace"):   # 155-a2-1's source (test only)
        m = re.search(r"STEPX\s+\d+\s+.*bound (\{[^}]*\})", ln)
        if m:
            BOUND.update(dict((int(k), int(v)) for k, v in re.findall(r"(-?\d+):\s*(-?\d+)", m.group(1))))
    RAW = copy.deepcopy(SIN["actions"][20:])
    used = used_symbols(RAW, made_symbols(RAW))
    REAL, bad, _l = map_symbols(used, SYM, BOUND, GR)
    g("T1 155-a2-1 symbols {0} all map (bad {1})".format(used, bad), not bad and len(REAL) == len(used))
    FMAP, fbad, _l2 = map_frames(RAW, SIN["actions"], SYM, BOUND, GR.get("owners") or {})
    g("T2 155-a2-1 frame map {0} (bad {1})".format(sorted(set(v["addr"] for v in FMAP.values())), fbad), FMAP and not fbad)
    ACTS = apply_map(RAW, REAL, FMAP)
    PBJ = J(PB)
    g("T3 apply_map(155-a2-1 rows) == plan_ring_p5s01b.json actions ({0}; md5 {1})".format(len(ACTS), md5(PB)[:8]),
      ACTS == PBJ["actions"][:len(ACTS)] and len(ACTS) == len(PBJ["actions"]),
      [a["id"] for a, b in zip(ACTS, PBJ["actions"]) if a != b])
    sys.exit(g.result())
