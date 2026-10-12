# ---
# labview: none
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/brief_166-a1-3.md
# ---
r"""elpredict - the ring-step PREDICTED step-end Error List (errorlist-expected/1) maker, ONCE (card 166-a1-3, docs/d1/ring-p5c.md PD403(d)(2)).

WHAT EXISTED (read first): `tools/bench/prep_c164_a2_3_lib.py:118-235` el(cfg) - the standing flow, called by prep_c164_a2_3_el.py,
prep_c164_a3_4_el.py, prep_c164_a3_6_el.py, prep_c165_a3_3_el.py; inline older copies at prep_c160_c3_1_el.py:50-176 (step 2, MERGE form) and
prep_c163_a1_3_el.py:42-150 (step 3). Those scripts are the record of what ran and stay untouched; NEW makers call `predict` here.
Why a new module and not tools/elrule.py: elrule.py is the FIXED rule for NEW items (L / C / SR / A) and its md5 is recorded inside every
predicted file (`elrule.module_md5`), so editing it would change every replay; this module is the flow around it (expected rows -> cleared /
stale / raised / unpredicted / standing), the topic the brief names.

predict(cfg) == prep_c164_a2_3_lib.el(cfg) (same keys, same output bytes when no new rule fires) plus two CLEARING rules (PD403(d)(2)):
  rule 1 (clears_by in plan): a row whose clears_by names an ACTION ('A70 w_k3f') that THIS plan contains is CLEARED by that action even when
         no action names the row's object uid (the old rule kept it STANDING: prep_c165_a3_3_el.py:10, errorlist_predicted_..._p5s02e_end.json
         items 4 / 49);
  rule 2 (tunnel-linked): when a row of class 'undirected' (object = a tunnel #T) is CLEARED, every 'nosource' / 'whilesubvi' row whose object
         wire carries, in the plan's BASE graph, an OuterTerminal of #T is CLEARED with it by the same action (the tunnel gets a source, its
         outer face flips to source; measured: #5204 t9631 / #10404 t24363, tools/bench/diag_c166_a1_1_facts.md:17-18).
  A row cleared by rule 1 that rule 2 also links carries both reasons ('how' + 'tunnel_link').
Self-test: `py tools/elpredict.py --selftest` (rule functions on literal rows + base graph 2a5fa0c4, then the step-5 REPLAY from its stored
inputs: total 47) and tools/bench/selftest_c166_eladv.py / tools/bench/diag_c166_a1_3_replay.py (steps 2..5 re-made, byte compare).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c166_a1_3_elpredict_selftest.log -- py -u tools/elpredict.py --selftest"""
import collections, copy, json, os, sys                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate / md5 / rel / J (shared)
md5, J = L.md5, L.J


def rel(p):
    """prep_c156_a1_1_lib.rel (repo-relative, '/' separators); a path on another drive (a %TEMP% copy) is returned absolute. Returns a str."""
    try:
        return L.rel(p)
    except ValueError:
        return os.path.abspath(p)
T = os.path.join(ROOT, "tools")
EL_KEYS = {"input": ["containsunwiredorbadterminal"], "sr": ["shiftregister", "unwiredfrominside"], "local": ["localvariable", "notconnected"],
           "cond": ["conditionalterminal", "notwired"]}                                    # elrule class -> norm_all (elrule.py:6-13) == prep_c164_a2_3_lib.EL_KEYS
TUNNEL_LINKED = ("nosource", "whilesubvi")                                                 # rule 2's row classes (PD403(d)(2))


def base_uids(a):
    """Base (int) uids a plan action names: loop / body / parent / diagram, a delete row's uid / wire_uid, and a dict end's uid / term_uid; returns a
    set. == prep_c164_a2_3_lib.base_uids. Self-test: --selftest A."""
    out = set(int(a[k]) for k in ("loop", "body", "parent", "diagram", "uid", "wire_uid") if isinstance(a.get(k), int))
    for k in ("src", "dst"):
        e = a.get(k)
        if isinstance(e, dict):
            out |= set(int(e[q]) for q in ("uid", "term_uid") if isinstance(e.get(q), int))
    return out


def is_stale(row, aids):
    """(stale, action name): a row whose clears_by names an ACTION ('A70 w_k3f') that is not in this plan's ids `aids`. == prep_c164_a2_3_lib.is_stale.
    Self-test: --selftest A."""
    cb = row.get("clears_by") or {}
    nm = str(cb.get("action") or "")
    return (cb.get("kind") == "action" and bool(nm) and nm.split()[-1] not in aids), nm


def clears_by_in_plan(row, aids):
    """Rule 1: the action id (last word of clears_by.action, e.g. 'w_k3f') when the row's clears_by is an ACTION that this plan's ids `aids`
    contain, else None. Self-test: --selftest A."""
    cb = row.get("clears_by") or {}
    nm = str(cb.get("action") or "")
    return nm.split()[-1] if (cb.get("kind") == "action" and nm and nm.split()[-1] in aids) else None


def attached_wires(state, uid):
    """Sorted wire uids on the terminal rows owned by object `uid` in a sim state. Self-test: --selftest B."""
    return sorted(set(int(t["wire_uid"]) for t in state["terminals"] if int(t.get("owner_uid") or 0) == int(uid) and t.get("wire_uid")))


def wires_of(s):
    """Set of wire uids on any terminal row of a sim state / graph. Self-test: --selftest B."""
    return set(int(t["wire_uid"]) for t in s["terminals"] if t.get("wire_uid"))


def tunnel_links(rows, cleared_items, base):
    """Rule 2: {row item: link} for every row of class nosource / whilesubvi whose object WIRE carries, in the base graph `base`, an OuterTerminal of
    a tunnel whose 'undirected' row is in `cleared_items` ({item: (action id, A)}); link = {tunnel, outer_term, with_item, action, A}. Self-test:
    --selftest C (base graph 2a5fa0c4: items 4 / 49 <- 7 / 8)."""
    outer = {}
    for r in rows:
        ob = r.get("object") or {}
        if r.get("class") == "undirected" and r.get("item") in cleared_items and ob.get("uid") is not None:
            for t in base["terminals"]:
                if int(t.get("owner_uid") or 0) == int(ob["uid"]) and t.get("term_class") == "OuterTerminal" and t.get("wire_uid"):
                    outer.setdefault(int(t["wire_uid"]), []).append((int(ob["uid"]), int(t["term_uid"]), r.get("item")))
    out = {}
    for r in rows:
        ob = r.get("object") or {}
        if r.get("class") in TUNNEL_LINKED and ob.get("kind") == "wire" and ob.get("uid") is not None and int(ob["uid"]) in outer:
            tu, term, it = outer[int(ob["uid"])][0]
            act, apos = cleared_items[it]
            out[r.get("item")] = {"tunnel": tu, "outer_term": term, "with_item": it, "action": act, "A": apos}
    return out


def predict(cfg, gate=None):
    """cfg: PLAN, SESS, EXPF, OUT (None = do not write), PINS, A0 (A number of action 1), N_REB, STEP_TXT, CARD, MAKER, UNPRED_WHY, ELR_SPAN.
    The predicted step-end Error List (entries in the form of EXPF) by prep_c164_a2_3_lib.el's flow + rules 1 and 2. Returns (gate rc, out dict,
    the JSON text written / that would be written). `gate` defaults to a fatal prep_c156_a1_1_lib.Gate(width=1000), as the lib. Self-test:
    --selftest D (step-5 replay, total 47) and tools/bench/diag_c166_a1_3_replay.py."""
    import elrule as ELR                                                                    # noqa: E402
    import errorlist_check as EC                                                            # noqa: E402
    import stagekit as K                                                                    # noqa: E402
    PLAN, SESS, EXPF, OUT, A0 = cfg["PLAN"], cfg["SESS"], cfg["EXPF"], cfg.get("OUT"), cfg["A0"]
    gate = gate or L.Gate(width=1000)
    ex, P, S = J(EXPF), J(PLAN), J(SESS)
    READF = os.path.join(ROOT, ex["measured_from"])
    gate("M0 pins {0}".format(dict((os.path.basename(p), w) for p, w in cfg["PINS"].items())), all(md5(p).startswith(w) for p, w in cfg["PINS"].items()),
         dict((os.path.basename(p), md5(p)[:8]) for p in cfg["PINS"]))
    gate("M1 read md5 == expected file's measured_md5 {0}".format(ex["measured_md5"][:8]), md5(READF) == ex["measured_md5"], md5(READF))
    RI = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in J(READF).get("items") or []]
    ROWS = ex["expected"]
    NROW = sum(int(r.get("count") or 1) for r in ROWS)
    xb, mb, _u = EC.compare(copy.deepcopy(RI), ROWS)
    gate("B compare(read {0} items, the {1} expected entries = {2} items) extra {3} missing {4} (baseline)".format(len(RI), len(ROWS), NROW, len(xb), len(mb)),
         len(RI) == NROW == int(ex["total"]) and not xb and not mb, (xb, mb))
    A = P["actions"]
    AID = set(a["id"] for a in A)
    APOS = dict((a["id"], A0 + n) for n, a in enumerate(A))
    base = J(P["finalized"]["base"]["path"])
    TOUCH = dict((u, a["id"]) for a in A for u in base_uids(a))
    print("FACT actions {0}; base uids named {1}".format([a["id"] for a in A], sorted(TOUCH.items())), flush=True)
    # pass 1 (per row index): uid named (the lib's rule) or rule 1; stale rows as before
    why = {}
    stale = []
    for n, r in enumerate(ROWS):
        ou = (r.get("object") or {}).get("uid")
        st_, nm = is_stale(r, AID)
        cbp = clears_by_in_plan(r, AID)
        if ou is not None and int(ou) in TOUCH:
            why[n] = (TOUCH[int(ou)], "action names #{0}".format(ou), None)
        elif st_:
            stale.append({"item": r.get("item"), "class": r.get("class"), "object_uid": ou, "was": nm, "in_plan": False,
                          "now": "STANDING (entry unchanged): {0} is not an action of {1}; it moves with the step that carries it".format(nm, os.path.basename(PLAN))})
        elif cbp and r.get("item") is not None:
            why[n] = (cbp, "clears_by '{0}' names action {1} of this plan (rule 1, PD403(d)(2); no action names #{2})".format(nm, cbp, ou), "1")
    # pass 2: rule 2 over the rows cleared so far (keyed by item; rows without an item are never linked)
    IDX = dict((r.get("item"), n) for n, r in enumerate(ROWS) if r.get("item") is not None)
    links = tunnel_links(ROWS, dict((ROWS[n].get("item"), (w[0], APOS[w[0]])) for n, w in why.items() if ROWS[n].get("item") is not None), base)
    for it, lk in sorted(links.items(), key=lambda kv: str(kv[0])):
        print("FACT TUNNEL-LINK item {0}: wire carries t{1} (OuterTerminal of #{2}, item {3} cleared by A{4} {5}){6}".format(
              it, lk["outer_term"], lk["tunnel"], lk["with_item"], lk["A"], lk["action"], " - also cleared by an earlier rule" if IDX[it] in why else ""), flush=True)
        if IDX[it] not in why:
            why[IDX[it]] = (lk["action"], "tunnel-linked: its wire carries t{0}, the OuterTerminal of #{1} whose undirected item {2} this action clears "
                                          "(rule 2, PD403(d)(2))".format(lk["outer_term"], lk["tunnel"], lk["with_item"]), "2")
    cleared = []
    for n, r in enumerate(ROWS):
        w = why.get(n)
        if not w:
            continue
        ou = (r.get("object") or {}).get("uid")
        e = {"item": r.get("item"), "class": r.get("class"), "object_uid": ou, "action": w[0], "A": APOS[w[0]], "how": w[1]}
        if w[2]:
            e["rule"] = "PD403(d)(2) rule " + w[2]
        if w[2] and r.get("item") in links:
            e["tunnel_link"] = dict((k, links[r.get("item")][k]) for k in ("tunnel", "outer_term", "with_item"))
        cleared.append(e)
    for e in cleared:
        print("FACT CLEARED item {item} {class} uid {object_uid} by A{A} {action} - {how}".format(**e), flush=True)
    for e in stale:
        print("FACT STALE item {item} {class} uid {object_uid}: clears_by '{was}' not in the plan -> STANDING".format(**e), flush=True)
    gate("CL {0} row(s) cleared by an action of this plan (items {1})".format(len(cleared), [e["item"] for e in cleared]), all(e["action"] in AID for e in cleared), cleared)
    gate("ST {0} stale row(s) (items {1}): none names an action of this plan".format(len(stale), [e["item"] for e in stale]), not any(e["in_plan"] for e in stale), stale)
    sf = P["finalized"]["step_files"]
    SFN = dict((int(x["n"]), x) for x in sf)
    st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
    sym0 = set(v for v in (st0.get("sym") or {}).values() if isinstance(v, int))
    SYMR = dict((int(u), s) for s, u in (last.get("sym") or {}).items() if isinstance(u, int))
    madeu = set(SYMR) - sym0
    ELP = ELR.predict(st0, last, NROW, madeu, carry=(), extra_owner_states=(base,), subvis=ELR.subvis_from_plan(P, st0, last))
    print("FACT ELRULE new {0} closed {1} uncertain base {2} uncertain subvi {3}".format(ELP["new_items"], ELP["closed_items"],
          ELP["uncertain_base_newly_unwired_inputs"], ELP["uncertain_subvi_terminals"]), flush=True)
    AS = dict((a["as"], a["id"]) for a in A if a.get("as"))
    raised = []
    for k, (c, u) in enumerate(ELP["new_items"]):
        s = (SYMR.get(int(u)) or "")[4:]
        who = next((AS[x] for x in sorted(AS, key=len, reverse=True) if s.startswith(x)), None) or TOUCH.get(int(u))
        raised.append({"item": "r{0}".format(k), "norm_all": EL_KEYS.get(c), "count": 1, "label": "elrule {0} item on #{1} [raised r{2}]".format(c, u, k),
                       "class": "elrule:" + c, "object": {"kind": "node", "uid": u, "evidence": "tools/elrule.py predict, " + cfg["ELR_SPAN"]}, "raised_by": who,
                       "A": APOS.get(who)})
    gate("R every elrule new item ({0}) attributed to an action and has a text key; closed {1}".format(len(raised), ELP["closed_items"]),
         all(x["raised_by"] and x["norm_all"] for x in raised), raised)
    unpred = []
    for kind, how, acts in (S.get("compile") or {}).get("ops") or []:
        if kind == "connect_term_uid" and how == "register_end_case_border":
            ids = [A[i - 1]["id"] for i in acts]
            unpred.append({"action": "UNPREDICTED:A{0} {1}".format(A0 + acts[0] - 1, ids[0]), "id": ids[0], "op_group": ids, "A": [A0 + i - 1 for i in acts],
                           "why": cfg["UNPRED_WHY"]["reb"]})
    for n, a in enumerate(A, 1):
        if a["op"] != "delete_object":
            continue
        pre, post = J(SFN[n - 1]["path"])["state"], J(SFN[n]["path"])["state"]
        aw = attached_wires(pre, a["uid"])
        left = sorted(w for w in aw if w in wires_of(post))
        print("FACT DELOBJ A{0} {1} #{2}: wires on it at step {3} {4}; still on other rows at step {5} {6}".format(APOS[a["id"]], a["id"], a["uid"], n - 1, aw, n, left), flush=True)
        if aw:
            unpred.append({"action": "UNPREDICTED:A{0} {1}".format(APOS[a["id"]], a["id"]), "id": a["id"], "op_group": [a["id"]], "A": [APOS[a["id"]]],
                           "wires_on_object": aw, "wires_left_in_sim": left, "why": cfg["UNPRED_WHY"]["delobj"]})
    gate("U unpredicted groups (session compile reb groups + delete_object rows with wires): {0}".format([(u["action"], u["op_group"]) for u in unpred]),
         len([u for u in unpred if len(u["op_group"]) > 1]) == cfg["N_REB"], unpred)
    CI = set(e["item"] for e in cleared)
    pred_rows = [copy.deepcopy(r) for r in ROWS if r.get("item") is None or r.get("item") not in CI] + [copy.deepcopy(x) for x in raised]
    c = copy.deepcopy(RI)
    _x, mc, _u = EC.compare(c, [r for r in ROWS if r.get("item") in CI])
    lic = [it for it in c if it.get("licensed_by") == "explicit"]
    rest = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in c if it.get("licensed_by") != "explicit"]
    xf, mf, _u = EC.compare(copy.deepcopy(rest), pred_rows)
    TT = sum(int(r.get("count") or 1) for r in pred_rows)
    gate("F compare(read minus the {0} cleared = {1} items, the {2} predicted entries = {3} items) extra {4} missing {5} (raised rows are synthetic: {6})".format(
         len(lic), len(rest), len(pred_rows), TT, len(xf), len(mf), len(raised)), not mc and len(lic) == len(CI) and not xf and (len(mf) == len(raised)), (mc, xf, mf))
    C0 = collections.Counter(K.el_class(x) for x in RI)
    CC = collections.Counter(K.el_class(x) for x in lic)
    RN = collections.Counter("elrule:" + k[0] for k in ELP["new_items"])
    RC = collections.Counter("elrule:" + k[0] for k in ELP["closed_items"])
    PC = dict((k, C0.get(k, 0) - CC.get(k, 0) + RN.get(k, 0) - RC.get(k, 0)) for k in sorted(set(C0) | set(RN)) if C0.get(k, 0) - CC.get(k, 0) + RN.get(k, 0) - RC.get(k, 0))
    gate("PC per-class predicted total {0} == item total {1} (start {2} - cleared {3} + raised {4} - elrule closed {5})".format(
         sum(PC.values()), TT, len(RI), len(CI), len(raised), len(ELP["closed_items"])), sum(PC.values()) == TT == len(RI) - len(CI) + len(raised) - len(ELP["closed_items"]), PC)
    cnt = {"cleared": len(cleared), "raised": len(raised), "unpredicted": len(unpred), "standing": NROW - len(cleared), "stale": len(stale), "total": TT,
           "total_if_every_unpredicted_raises_one": TT + len(unpred), "base_total": NROW}
    print("EL COUNTS cleared {cleared} raised {raised} unpredicted {unpredicted} standing {standing} stale {stale} total {total} (upper {total_if_every_unpredicted_raises_one})".format(**cnt), flush=True)
    out = {"schema": "errorlist-expected/1", "kind": "PREDICTED step end ({0}, {1}); not a read - the scratch reads it".format(cfg["STEP_TXT"], rel(PLAN)),
           "bed": None, "bed_note": "the step's in-between file does not exist yet; base bed " + str(ex.get("bed_md5") or "")[:8] + " (" + str(ex["bed"]) + ")",
           "decided_by": "card {0}: cleared AND raised items per action; written by {1}".format(cfg["CARD"], cfg["MAKER"]),
           "base_expected": {"path": rel(EXPF), "md5": md5(EXPF), "total": NROW}, "measured_from": ex["measured_from"], "measured_md5": ex["measured_md5"],
           "plan": {"path": rel(PLAN), "md5": md5(PLAN)}, "session": {"path": rel(SESS), "md5": md5(SESS)}, "total": TT, "counts": cnt,
           "cleared": cleared, "stale": stale, "raised": raised, "unpredicted": unpred,
           "elrule": {"module_md5": md5(os.path.join(T, "elrule.py")), "new_items": ELP["new_items"], "closed_items": ELP["closed_items"],
                      "uncertain_base_newly_unwired_inputs": ELP["uncertain_base_newly_unwired_inputs"], "uncertain_subvi_terminals": ELP["uncertain_subvi_terminals"],
                      "rule": ELP["rule"], "fixed": ELP},
           "per_class": {"start_read": {"path": ex["measured_from"], "md5": md5(READF), "items": len(RI), "classes": dict(sorted(C0.items()))},
                         "cleared": dict(CC), "rule_new": dict(RN), "rule_closed": dict(RC), "predicted": PC, "classifier": "stagekit.el_class"},
           "check": {"compare_baseline": [len(xb), len(mb)], "compare_predicted": [len(xf), len(mf)], "checker": "errorlist_check.compare"},
           "expected": pred_rows,
           "format_note": "same entry form as " + rel(EXPF) + " (norm_all / count / label / cite; checker errorlist_check.compare); cleared / raised / unpredicted / stale are extra keys"}
    text = json.dumps(out, indent=1)
    if OUT:
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(text)
    W = json.loads(text)
    xs, ms, _u = EC.compare(copy.deepcopy(rest), W["expected"])
    gate("W predicted file {0}, {1} items == total; compare(read minus cleared, the file's own entries) extra {2} missing {3} == raised".format(
         "written" if OUT else "built (not written)", sum(int(r.get("count") or 1) for r in W["expected"]), len(xs), len(ms)),
         sum(int(r.get("count") or 1) for r in W["expected"]) == TT and not xs and len(ms) == len(raised))
    if OUT:
        print("FACT md5 {0} {1}".format(md5(OUT), rel(OUT)), flush=True)
    return gate.result([{"path": rel(OUT), "md5": md5(OUT)}] if OUT else []), out, text


# step-5 inputs: the CFG of tools/bench/prep_c165_a3_3_el.py:17-40 (data, restated; that script runs on import)
B = os.path.join(ROOT, "tools", "bench")
STEP5_CFG = {"PLAN": os.path.join(B, "plan_ring_p5s02e.json"), "SESS": os.path.join(B, "prep_c165_a3_2_session.json"),
             "EXPF": os.path.join(B, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json"), "OUT": None,
             "PINS": {os.path.join(B, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json"): "c74200f2", os.path.join(B, "plan_ring_p5s02e.json"): "fd23974e",
                      os.path.join(B, "graph_ring_p5s02d_20261010_154830.json"): "2a5fa0c4"}, "A0": 72, "N_REB": 2,
             "STEP_TXT": "P5-2 step 5, groups K3f + K4 + K4f A72..A84", "CARD": "165-3-3 (docs/d1/ring-p5c.md PD400, PD401, PD402)",
             "MAKER": "tools/bench/prep_c165_a3_3_el.py", "ELR_SPAN": "step_00 -> step_13 of tools/bench/sim/ring_p5s02e",
             "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR SK4): step 2's same verb "
                                   "left +2 'Wire has loose ends.' items (diag_c162_a1_2_facts.md), step 3's left none (diag_c163_a2_2_facts.md:31); not "
                                   "decidable offline - the step-5 scratch measures it",
                            "delobj": "no delete_object row in this plan"}}


def selftest():
    """A rule functions on literal rows; B attached_wires / wires_of on a toy state; C tunnel_links on the real base graph 2a5fa0c4 (items 4 / 49
    linked to 7 / 8 via t9631 / t24363); D the step-5 prediction replayed from its stored inputs: total 47, items 4 and 49 cleared, compare with
    the stored 47-item read 0c0664d8 extra 0 missing 0; E rule 2 alone (a %TEMP% copy of the expected file with rule 1 disabled on items 4 / 49):
    total 47 again. Prints the RESULT line; returns 0 / 1."""
    import errorlist_check as EC                                                            # noqa: E402
    g = L.Gate(fatal_default=False)
    r1 = {"clears_by": {"kind": "action", "action": "A70 w_k3f", "step": 3}}
    r2 = {"clears_by": {"kind": "standing"}}
    g("A is_stale / clears_by_in_plan / base_uids", is_stale(r1, {"dw_cond"}) == (True, "A70 w_k3f") and is_stale(r1, {"w_k3f"})[0] is False and is_stale(r2, set())[0] is False
      and clears_by_in_plan(r1, {"w_k3f"}) == "w_k3f" and clears_by_in_plan(r1, {"dw_cond"}) is None and clears_by_in_plan(r2, {"w_k3f"}) is None
      and base_uids({"op": "delete_wire", "wire_uid": 7}) == {7} and base_uids({"src": {"uid": 3, "term_uid": 4}, "dst": "new:X", "loop": 9}) == {3, 4, 9})
    s = {"terminals": [{"owner_uid": 5, "wire_uid": 11}, {"owner_uid": 6, "wire_uid": 12}, {"owner_uid": 5, "wire_uid": None}]}
    g("B attached_wires / wires_of", attached_wires(s, 5) == [11] and attached_wires(s, 7) == [] and wires_of(s) == {11, 12})
    rows = J(STEP5_CFG["EXPF"])["expected"]
    base = J(os.path.join(B, "graph_ring_p5s02d_20261010_154830.json"))
    lk = tunnel_links(rows, {7: ("w_k3f", 73), 8: ("w_k4f", 84)}, base)
    g("C tunnel_links(base 2a5fa0c4, items 7 / 8 cleared) == {4: #5204 t9631, 49: #10404 t24363}",
      sorted(lk) == [4, 49] and (lk[4]["tunnel"], lk[4]["outer_term"], lk[4]["with_item"]) == (5204, 9631, 7)
      and (lk[49]["tunnel"], lk[49]["outer_term"], lk[49]["with_item"]) == (10404, 24363, 8) and tunnel_links(rows, {}, base) == {}, lk)
    rc, out, _t = predict(STEP5_CFG, L.Gate(width=1000, fatal_default=False))
    READ = os.path.join(B, "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")
    items = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in J(READ)["items"]]
    x, m, _u = EC.compare(items, out["expected"])
    g("D step-5 replay: predict rc {0}, total {1} == 47, cleared items {2} include 4 and 49; compare(read 0c0664d8 {3} items) extra {4} missing {5}".format(
      rc, out["total"], [e["item"] for e in out["cleared"]], len(items), len(x), len(m)),
      rc == 0 and out["total"] == 47 and {4, 49} <= set(e["item"] for e in out["cleared"]) and not x and not m and md5(READ).startswith("0c0664d8"), (x, m))
    import tempfile
    ex = J(STEP5_CFG["EXPF"])
    for r in ex["expected"]:
        if r.get("item") in (4, 49):
            r["clears_by"] = {"kind": "standing", "cause": "selftest E: rule 1 disabled for this row"}
    tmp = os.path.join(tempfile.gettempdir(), "elpredict_selftest_E_expected.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(ex, f, indent=1)
    cfg = dict(STEP5_CFG, EXPF=tmp, PINS={})
    rcE, outE, _t = predict(cfg, L.Gate(width=1000, fatal_default=False))
    os.remove(tmp)
    ce = dict((e["item"], e) for e in outE["cleared"])
    g("E rule 2 alone (items 4 / 49 clears_by -> standing in a temp copy): rc {0}, total {1} == 47, items 4 / 49 cleared by rule 2 via #5204 / #10404".format(rcE, outE["total"]),
      rcE == 0 and outE["total"] == 47 and ce.get(4, {}).get("rule") == "PD403(d)(2) rule 2" and ce.get(49, {}).get("rule") == "PD403(d)(2) rule 2"
      and ce[4]["action"] == "w_k3f" and ce[49]["action"] == "w_k4f", [(e["item"], e["action"], e.get("rule")) for e in outE["cleared"]])
    return g.result([])


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.exit(selftest())
