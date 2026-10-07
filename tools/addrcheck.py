r"""addrcheck - ONE module for "does this plan address name that real terminal?" (card chat-S5, the user's "S1", 2026-10-03:
"좋아. 지금 수정 내용을 S1이라고 할게"; decision PD337 in docs/d1/tooling.md). Imported by stagesim (writes the position triple),
stage_prerun (--rebase / --prerun tier (a)), gateclass/guard_peer (an address-only failure owes no hypothesis review).

WHY. Cycles 142-143: ~44 of ~175 min went to our own checkers refusing good work. 143-4: the s03 plan addressed Local #-20 by
the simulator's alias 'value' (stagesim.py resolve_addr, card 100-3) while the real graph names that terminal by its
variable 'StopAll'; rebase's name lookup found 0 rows and refused, although the terminal was the only source of that node.

THE THREE TIERS (user approved the design, brief_chat-S5.md section 2)
  (a) CODE, automatic: resolve every plan address against a terminal table. Selector order = stagesim's own:
        name exact -> '<name>#k' (k-th same-named row) -> 'inner'/'outer' face -> 'value' alias (the node's one terminal
        of the wanted direction) -> the POSITION TRIPLE (owner uid, terminal index, terminal class [, direction]) that
        stagesim recorded when it resolved the address (plan finalized.addr_pos).
      Never guess: a selector that does not give EXACTLY one row is unresolved; the output lists the candidates.
  (b) JEV, advisory only: one typed noul question per unresolved item with a short candidate list ("same terminal?").
      Switched on only after measure() on the labelled set (tools/bench/addrcheck_labelled.json) and only LOGGED -
      the result never binds anything (standing Jev rule, CLAUDE.md section 3 exception 2026-09-22).
  (c) LLM only for the low-confidence items: the item is printed as `ADDRESS-LLM-OWED` (no whole-card re-review);
      the judgement session reads those lines.

Self-test: tools/bench/selftest_s5.py (the name selftest_addrcheck_s5.py never existed); face/cond: selftest_t4.py.
"""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
LABELLED = os.path.join(BENCH, "addrcheck_labelled.json")
MEASURE = os.path.join(BENCH, "addrcheck_jev_measure.json")
JEV_MIN_ACC = 0.85            # advisory switch-on threshold on the labelled set (measured, MEASURE file)
LOCAL_CLASSES = ("Local", "LocalVariable", "GlobalVariable")


def _node_of(r):
    try:
        import vigraph as V
        return V.node_of(r)
    except Exception:                                                              # noqa: BLE001
        return r.get("owner_uid")


def addr_key(a):
    """The canonical text of one plan address (dict or '<uid>.<term>' string) - the key stagesim's addr_pos records use."""
    if isinstance(a, dict):
        return json.dumps(a, sort_keys=True, separators=(",", ":"))
    return str(a)


def owner_rows(rows, owner):
    """The owner's terminal rows in READ order, one per term uid (a multi-frame tunnel lists a uid once)."""
    out, seen = [], set()
    for r in rows or []:
        if _node_of(r) == owner and r["term_uid"] not in seen:
            seen.add(r["term_uid"])
            out.append(r)
    return out


def triple(rows, term_uid):
    """{owner, index, class, source, name} of one terminal row, index = position among its owner's rows (read order)."""
    r = next((x for x in rows or [] if x["term_uid"] == term_uid), None)
    if r is None:
        return None
    own = owner_rows(rows, _node_of(r))
    idx = next(i for i, x in enumerate(own) if x["term_uid"] == term_uid)
    return {"owner": _node_of(r), "index": idx, "class": r.get("term_class", ""), "source": bool(r.get("is_source")),
            "name": r.get("term_name", "")}


def _short(r):
    return {"term_uid": r["term_uid"], "name": r.get("term_name", ""), "class": r.get("term_class", ""),
            "source": bool(r.get("is_source"))}


def resolve(rows, owner, name, want_source=None, pos=None, owner_class=None):
    """(row | None, how, candidates). Tier (a) on ONE address against ONE terminal table. `pos` = the recorded triple
    ({index, class[, source]}) or None. how in name | name#k | side | value-alias | triple | unique-dir | (None)."""
    own = owner_rows(rows, owner)
    if want_source is not None:
        dirrows = [r for r in own if bool(r.get("is_source")) == bool(want_source)]
    else:
        dirrows = list(own)
    cands = [_short(r) for r in dirrows][:8]
    if not own:
        return None, None, []
    nm = "" if name is None else str(name)
    hit = [r for r in dirrows if r.get("term_name", "") == nm]
    if len(hit) == 1:
        return hit[0], "name", cands
    mk = re.match(r"^(.*)#([0-9]+)$", nm)
    if mk and not hit:
        same = [r for r in own if r.get("term_name", "") == mk.group(1)]
        k = int(mk.group(2))
        if k < len(same) and (want_source is None or bool(same[k].get("is_source")) == bool(want_source)):
            return same[k], "name#k", cands
    if not hit and nm in ("inner", "outer"):
        side = [r for r in dirrows if r.get("term_class") == ("InnerTerminal" if nm == "inner" else "OuterTerminal")]
        if len(side) == 1:
            return side[0], "side", cands
    if not hit and nm == "value" and len(dirrows) == 1:
        # stagesim.py resolve_addr (card 100-3): '.value' = the node's one terminal of the wanted direction (a Local)
        return dirrows[0], "value-alias", cands
    if isinstance(pos, dict) and isinstance(pos.get("index"), int):
        k = pos["index"]
        if 0 <= k < len(own):
            r = own[k]
            ok = r.get("term_class", "") == pos.get("class", r.get("term_class", ""))
            if "source" in pos:
                ok = ok and bool(r.get("is_source")) == bool(pos["source"])
            if want_source is not None:
                ok = ok and bool(r.get("is_source")) == bool(want_source)
            if ok:
                return r, "triple", cands
    return None, None, cands


def real_match(sim_rows, st, real_rows, rt, rn_owner):
    """Tier (a) on the REAL side of a rebind: does real row `rt` on real owner `rn_owner` sit at the SAME position as
    sim row `st` on its owner? Returns (ok, how). Accepted only when unique by construction:
      'unique-dir'  - the (term class, direction) pair occurs exactly once on the sim owner AND on the real owner, and
                      rt is that row (index irrelevant);
      'index'       - same index, same class, same direction on both owners (the recorded triple and rebind's positional
                      pairing agree - the caller passes rt = rebind's binding)."""
    ts = triple(sim_rows, st)
    tr = triple(real_rows, rt)
    if not ts or not tr or tr["owner"] != rn_owner:
        return False, None
    if (ts["class"], ts["source"]) != (tr["class"], tr["source"]):
        return False, None
    so = [r for r in owner_rows(sim_rows, ts["owner"]) if (r.get("term_class", ""), bool(r.get("is_source"))) == (ts["class"], ts["source"])]
    ro = [r for r in owner_rows(real_rows, rn_owner) if (r.get("term_class", ""), bool(r.get("is_source"))) == (tr["class"], tr["source"])]
    if len(so) == 1 and len(ro) == 1 and ro[0]["term_uid"] == rt:
        return True, "unique-dir"
    if ts["index"] == tr["index"]:
        return True, "index"
    return False, None


# card chat-T4 (PD348), ported from bench arm A13K card 145-a3-1 (PD346(c) there; A13K tools/addrcheck.py:141-208, md5
# 96502aaa): the SAME face / 'cond' selectors as the sim side, on the REAL side of a rebind. ADDED helpers - resolve /
# real_match above are unchanged for every existing caller. One translation, no loosening: A13K's terminal mode 'record'
# (a terminal paired by position inside a node seeded from the bind log) is main's 'map-pos' (paired by position inside a
# node bound by the creation map, stage_prerun.rebind, card chat-T3); main's 'map' (the terminal itself recorded) is as
# strong as 'conn' there (STRONG_MODES).
FACE_CLASS = {"inner": "InnerTerminal", "outer": "OuterTerminal"}
BOUND_MODES = ("conn", "map", "map-pos")


def real_face(sim_rows, st, real_rows, rn_owner, face, want_source, rt, mode):
    """(ok, why). A plan address named 'inner'/'outer' binds on the real side only when ALL hold: the sim row `st` is of
    that face class; rebind bound it by connectivity or by the creation map (`mode` in BOUND_MODES); the real owner has
    EXACTLY ONE row of that face class and of the wanted direction; and that row IS the bound one (`rt` = M[st]).
    The caller keeps the name."""
    cls = FACE_CLASS.get(face)
    if cls is None:
        return False, "face: {0!r} is not 'inner'/'outer'".format(face)
    srow = next((r for r in sim_rows or [] if r["term_uid"] == st), None)
    if srow is None or srow.get("term_class") != cls:
        return False, "face: sim row #{0} is {1}, not {2}".format(st, (srow or {}).get("term_class"), cls)
    if mode not in BOUND_MODES:
        return False, "face: sim row #{0} bound by {1}, not {2}".format(st, mode, "/".join(BOUND_MODES))
    side = [r for r in owner_rows(real_rows, rn_owner)
            if r.get("term_class") == cls and bool(r.get("is_source")) == bool(want_source)]
    if len(side) != 1:
        return False, "face: real owner #{0} has {1} {2} row(s) of that direction {3}".format(
            rn_owner, len(side), cls, [r["term_uid"] for r in side][:6])
    if side[0]["term_uid"] != rt:
        return False, "face: the real {0} row #{1} != the bound row #{2}".format(cls, side[0]["term_uid"], rt)
    return True, "face"


def obj_class(doc, uid):
    """The class of object `uid` in a graph doc's `objs` (None when absent)."""
    return next((o.get("class") for o in (doc or {}).get("objs") or [] if isinstance(o, dict) and o.get("uid") == uid), None)


def cond_sinks(doc, rows, loop):
    """(body diagrams, sink rows) of While `loop`: stagesim.cond_row's filter (body Diagram = `owners` entry owned by the
    loop; row owner_class Diagram, term_class Terminal, sink), one row per term uid."""
    body = [int(b) for b, cu in ((doc or {}).get("owners") or {}).items()
            if isinstance(cu, (list, tuple)) and len(cu) == 2 and str(cu[1]).lstrip("-").isdigit() and int(cu[1]) == loop]
    out, seen = [], set()
    for r in rows or []:
        if (_node_of(r) in body and r.get("owner_class") == "Diagram" and r.get("term_class") == "Terminal"
                and not r.get("is_source") and r["term_uid"] not in seen):
            seen.add(r["term_uid"])
            out.append(r)
    return body, out


def cond_bind(addr, sim_doc, sim_rows, sim_loop, real_doc, real_rows, real_loop, M):
    """(real sink uid | None, why). The PD316 base-loop form {'uid': <While>, 'term': 'cond'} (stagexec.base_cond: exactly
    those two keys) rebinds to {'uid': real_loop, 'term': 'cond'} only when: the sim owner AND the real owner are WhileLoops
    (stagesim.cond_target); each body has EXACTLY ONE cond_row sink and the real one is unnamed; and when rebind bound the
    sim sink, it bound it to that real sink."""
    if not (isinstance(addr, dict) and addr.get("term") == "cond" and not set(addr) - {"uid", "term"}):
        return None, "cond: not the PD316 form {'uid': <loop>, 'term': 'cond'}"
    sc, rc = obj_class(sim_doc, sim_loop), obj_class(real_doc, real_loop)
    if sc != "WhileLoop" or rc != "WhileLoop":
        return None, "cond: sim #{0} is {1}, real #{2} is {3} (a While loop is required)".format(sim_loop, sc, real_loop, rc)
    sb, ss = cond_sinks(sim_doc, sim_rows, sim_loop)
    rb, rs = cond_sinks(real_doc, real_rows, real_loop)
    if len(ss) != 1 or len(rs) != 1:
        return None, "cond: body sink row(s) sim {0} on {1}, real {2} on {3} (exactly one each)".format(
            [r["term_uid"] for r in ss][:6], sb, [r["term_uid"] for r in rs][:6], rb)
    if rs[0].get("term_name", "") != "":
        return None, "cond: real body sink #{0} is named {1!r}".format(rs[0]["term_uid"], rs[0].get("term_name"))
    if ss[0]["term_uid"] in (M or {}) and M[ss[0]["term_uid"]] != rs[0]["term_uid"]:
        return None, "cond: sim sink #{0} is bound to #{1}, not the real sink #{2}".format(
            ss[0]["term_uid"], M[ss[0]["term_uid"]], rs[0]["term_uid"])
    return rs[0]["term_uid"], "cond: body {0} sink #{1}".format(rb, rs[0]["term_uid"])


# ------------------------------------------------------------------------------------------------ tier (b) Jev, advisory
SAME_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW block-diagram build plan addresses ONE terminal of a node. A simulator and the real LabVIEW graph may "
        "LABEL the same terminal differently (a Local variable's terminal is called 'value' by the simulator and by the "
        "variable's name in LabVIEW; a new tunnel face can be unnamed '' in one and 'error out' in the other). `planned` "
        "is the plan's address (node class, terminal name, direction, terminal class, index among the node's terminals); "
        "`candidate` is one terminal of the real node the plan's node was bound to. Answer YES only if the candidate is "
        "the SAME terminal: same direction, same terminal class, consistent position, and a label difference that is only "
        "a naming convention. Two different inputs/outputs of one node (x vs y, status vs code, i vs the loop condition) "
        "are NOT the same even if both are unnamed."),
    "criteria": {"same_terminal": "the candidate is the planned terminal under another label"},
}


def jev_same(planned, candidate, n=1, timeout=25):
    """(p, verdict, err) - one typed question. Never raises; no key -> (None, 'unknown', 'no key')."""
    try:
        import jev
    except Exception as e:                                                         # noqa: BLE001
        return None, "unknown", "jev import: {0}".format(e)
    state = {"planned": json.dumps(planned, sort_keys=True), "candidate": json.dumps(candidate, sort_keys=True)}
    mean, _sp, err = jev.ask_n(state, {"same": SAME_Q}, n=n, purpose="addrcheck-same", timeout=timeout, retries=1)
    if err:
        return None, "unknown", err
    return mean, jev.verdict(mean), None


def measure(path=LABELLED, out=MEASURE, n=1, log=print):
    """Run tier (b) on the labelled set; write {accuracy, n, rows, switched_on} to MEASURE. Accuracy counts an 'unknown'
    answer as wrong (it cannot advise)."""
    d = json.load(open(path, encoding="utf-8"))
    rows, right, unk = [], 0, 0
    for it in d["items"]:
        p, v, err = jev_same(it["planned"], it["candidate"], n=n)
        want = "yes" if it["same"] else "no"
        ok = v == want
        right += ok
        unk += v == "unknown"
        rows.append({"id": it["id"], "p": p, "verdict": v, "label": want, "ok": ok, "err": err})
        log("JEV-ADDR-MEASURE {0} p={1} verdict={2} label={3} {4}".format(it["id"], None if p is None else round(p, 3), v,
                                                                       want, "OK" if ok else "WRONG"))
    acc = right / float(len(rows) or 1)
    rec = {"schema": "addrcheck-jev-measure/1", "labelled": os.path.relpath(path, ROOT).replace("\\", "/"),
           "n_items": len(rows), "samples_per_item": n, "accuracy": round(acc, 3), "unknown": unk,
           "threshold": JEV_MIN_ACC, "switched_on": acc >= JEV_MIN_ACC, "mode": "advisory (logged, never binds)",
           "rows": rows, "at": __import__("time").strftime("%Y-%m-%d %H:%M:%S")}
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    return rec


def jev_switched_on(path=MEASURE):
    if os.environ.get("ADDR_JEV") == "0":
        return False
    try:
        return bool(json.load(open(path, encoding="utf-8")).get("switched_on"))
    except (OSError, ValueError):
        return False


def advise(items, log=print, n=1):
    """Tiers (b) and (c) over unresolved items [{planned, candidates:[...]}]: Jev advisory per candidate when switched on
    (logged JEV-ADDR lines, nothing acts on them); an item without a confident single YES -> ADDRESS-LLM-OWED line.
    Returns the per-item advice list (for the caller's log / result)."""
    on = jev_switched_on()
    out = []
    for it in items:
        adv = {"item": it.get("id"), "jev": [], "llm_owed": True}
        if on:
            for c in (it.get("candidates") or [])[:4]:
                p, v, err = jev_same(it["planned"], c, n=n)
                adv["jev"].append({"candidate": c.get("term_uid"), "p": p, "verdict": v, "err": err})
                log("JEV-ADDR advisory {0} candidate #{1} {2!r}: p={3} {4} (advisory only - binds nothing)".format(
                    it.get("id"), c.get("term_uid"), c.get("name"), None if p is None else round(p, 3), v))
            yes = [a for a in adv["jev"] if a["verdict"] == "yes"]
            adv["llm_owed"] = len(yes) != 1
        if adv["llm_owed"]:
            log("ADDRESS-LLM-OWED {0}: planned {1}; candidates {2} (judgement session decides; no card re-review)".format(
                it.get("id"), json.dumps(it.get("planned"), sort_keys=True)[:200],
                [(c.get("term_uid"), c.get("name")) for c in (it.get("candidates") or [])][:6]))
        out.append(adv)
    return out


# ------------------------------------------------------------------------------------------------ tier (a) over a plan
ADDR_FIELDS = ("at", "src", "dst", "born_on", "on")
SRC_FIELDS = ("src", "born_on")


def plan_ends(plan):
    """[(action n, action id, field, address)] for every address field of every action."""
    out = []
    for n, a in enumerate(plan.get("actions") or [], 1):
        for f in ADDR_FIELDS:
            if f in a and a[f] is not None:
                out.append((n, a.get("id"), f, a[f]))
    return out


def split_addr(v):
    """(owner uid int | None, term name | None, term_uid | None) - None owner for a symbolic new:... address."""
    if isinstance(v, dict):
        u = v.get("uid")
        return (u if isinstance(u, int) and not isinstance(u, bool) else None), v.get("term"), v.get("term_uid")
    if isinstance(v, str):
        m = re.match(r"^(-?\d+)\.(.*)$", v)
        if m:
            return int(m.group(1)), m.group(2), None
    return None, None, None


def check_plan(plan, rows, addr_pos=None):
    """Tier (a) over every NUMERIC-owner address of a plan against ONE terminal table (the plan's base graph). Symbolic
    'new:' addresses belong to the simulator (they do not exist before the plan runs) and are skipped, as are owners the
    table does not hold (created by an earlier stage - rebase binds those). Returns {resolved, unresolved, skipped}."""
    pos = dict(((r["n"], r["addr"]), r) for r in (addr_pos or []) if isinstance(r, dict))
    have = set(_node_of(r) for r in rows or [])
    res, unres, skip = [], [], []
    for n, aid, f, v in plan_ends(plan):
        if f == "at":
            skip.append((n, f, "at"))
            continue
        owner, name, tu = split_addr(v)
        if owner is None or owner not in have:
            skip.append((n, f, addr_key(v)[:60]))
            continue
        if tu is not None:
            ok = any(r["term_uid"] == tu and _node_of(r) == owner for r in rows)
            (res if ok else unres).append({"id": "{0}:{1}".format(aid or n, f), "addr": v, "how": "term_uid" if ok else None})
            continue
        r, how, cands = resolve(rows, owner, name, want_source=(f in SRC_FIELDS), pos=pos.get((n, addr_key(v))))
        if r is not None:
            res.append({"id": "{0}:{1}".format(aid or n, f), "addr": v, "how": how, "term_uid": r["term_uid"]})
        else:
            unres.append({"id": "{0}:{1}".format(aid or n, f), "addr": v,
                          "planned": {"owner": owner, "name": name, "source": f in SRC_FIELDS},
                          "candidates": cands})
    return {"resolved": res, "unresolved": unres, "skipped": skip}
# ---
# labview: none
# hardware: none
# ---
