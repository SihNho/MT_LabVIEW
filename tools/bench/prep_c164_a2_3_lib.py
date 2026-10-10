# ---
# labview: none
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
r"""prep_c164_a2_3_lib - card 164-a2-3 (OFFLINE, json only): the ring-step PRED / LICENCE / predicted-ERROR-LIST makers as FUNCTIONS of one config
dict, so a ring step's makers are inputs + one call (docs/script-writing.md rules 1-2). The step-3 makers prep_c163_a1_3_{pred,licence,el}.py
(and their step-2 parents prep_c160_c3_1_*) are top-level scripts - importing one runs it - so their flow is written here ONCE, generalised:
  licence(cfg) == prep_c163_a1_3_licence.py (X11 log, base_sink_renames, licence_renames read-back, X11-after);
  el(cfg)      == prep_c163_a1_3_el.py + (i) base uids of delete rows (uid / wire_uid) count as named, (ii) STALE = any clears_by ACTION
                  not in this plan (the 163 test was clears_by.step == 3; the rows carried step 3 after the I-alone split), (iii) a
                  delete_object whose sim pre-state carries wires on the deleted object is UNPREDICTED (elrule has no loose-end class);
  pred(cfg)    == prep_c163_a1_3_pred.py + the DW / DO delete rows of prep_c160_c3_1_pred.py:100-133 (present at n-1, gone at n), the
                  route rows of the session's realsim route_check per action, session start read from `start_mb` or `start[0]`.
Shared calls only: Gate / main_of / sg_census (prep_c156_a1_1_lib), stagexec, stage_prerun, stage_shared.checkpoint_step_table,
stagekit.cen2_wire_ends / sim_census_snapshot / el_class / licence_renames, census_predict, elrule, errorlist_check.compare.
Self-test (--selftest): A is_stale / base_uids on literal rows; B attached_wires on a 2-row toy state. PREDICTION: 2/0.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c164_a2_3_lib.log -- py -u tools/bench/prep_c164_a2_3_lib.py --selftest"""
import collections, copy, json, os, sys                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import prep_c156_a1_1_lib as L                                                              # noqa: E402  Gate / main_of / sg_census (shared)
md5, rel, J = L.md5, L.rel, L.J
B, T = os.path.join(ROOT, "tools", "bench"), os.path.join(ROOT, "tools")
EL_KEYS = {"input": ["containsunwiredorbadterminal"], "sr": ["shiftregister", "unwiredfrominside"], "local": ["localvariable", "notconnected"],
           "cond": ["conditionalterminal", "notwired"]}                                    # elrule class -> norm_all (elrule.py:6-13), = prep_c163_a1_3_el.py:39


def base_uids(a):
    """Base (int) uids a plan action names: loop / body / parent / diagram, a delete row's uid / wire_uid, and a dict end's uid / term_uid."""
    out = set(int(a[k]) for k in ("loop", "body", "parent", "diagram", "uid", "wire_uid") if isinstance(a.get(k), int))
    for k in ("src", "dst"):
        e = a.get(k)
        if isinstance(e, dict):
            out |= set(int(e[q]) for q in ("uid", "term_uid") if isinstance(e.get(q), int))
    return out


def is_stale(row, aids):
    """(stale, action name): a row whose clears_by names an ACTION ('A70 w_k3f') that is not in this plan's ids `aids`."""
    cb = row.get("clears_by") or {}
    nm = str(cb.get("action") or "")
    return (cb.get("kind") == "action" and bool(nm) and nm.split()[-1] not in aids), nm


def attached_wires(state, uid):
    """Wire uids on the terminal rows owned by object `uid` in a sim state."""
    return sorted(set(int(t["wire_uid"]) for t in state["terminals"] if int(t.get("owner_uid") or 0) == int(uid) and t.get("wire_uid")))


def wires_of(s):
    return set(int(t["wire_uid"]) for t in s["terminals"] if t.get("wire_uid"))


def objs_of(s):
    return set(int(o["uid"]) for o in s.get("objs") or [])


def _pins_gate(gate, pins):
    gate("M0 pins {0}".format(dict((os.path.basename(p), w) for p, w in pins.items())), all(md5(p).startswith(w) for p, w in pins.items()),
         dict((os.path.basename(p), md5(p)[:8]) for p in pins))


# ------------------------------------------------------------------------------------------------------------------------------ LICENCE
def licence(cfg):
    """cfg: PLAN, LIC, X11LOG, SESS, STAGE, CARD, STEP_TXT, PD, PRECEDENT, MAKER. Writes the pb-licence/1 file; returns the gate rc."""
    import stage_prerun as SPR                                                              # noqa: E402
    import stagekit as K                                                                    # noqa: E402
    import stage_shared as SH                                                               # noqa: E402
    PLAN, LIC, SESS = cfg["PLAN"], cfg["LIC"], cfg["SESS"]
    gate = L.Gate(width=1200)
    gate("L0 plan md5 == session table's {0}".format(J(SESS)["plan"]["md5"][:8]), md5(PLAN) == J(SESS)["plan"]["md5"], md5(PLAN))
    X11L = open(cfg["X11LOG"], encoding="utf-8", errors="replace").read().splitlines()
    X11FLAGS = [ln for ln in X11L if ln.startswith("FLAG ")]
    X11CLEAN = any(ln.startswith("CLEAN ") for ln in X11L)
    print("FACT X11 log {0} md5 {1}: CLEAN {2}, FLAG lines {3}".format(rel(cfg["X11LOG"]), md5(cfg["X11LOG"]), X11CLEAN, X11FLAGS), flush=True)
    P = J(PLAN)
    BASE = J(P["finalized"]["base"]["path"])
    bt = dict((int(r["term_uid"]), r) for r in BASE["terminals"])
    x11 = SPR.buildarray_open_sibling(P, licences={})
    print("FACT X11 (licences ignored) flags {0}".format(x11), flush=True)
    nodes = sorted(set(int(f["node"]) for f in x11))
    gate("X11 flags node(s) {0} == the --buildarray-check log ({1} FLAG line(s), CLEAN {2})".format(nodes, len(X11FLAGS), X11CLEAN),
         len(x11) == len(X11FLAGS) and (X11CLEAN == (not x11)), x11)
    A = P["actions"]
    rbu = []
    for n in nodes:
        rows = [f["row"] for f in x11 if int(f["node"]) == n]
        tus = sorted(set(int(a["dst"]["term_uid"]) for a in A if a.get("id") in rows and isinstance(a.get("dst"), dict) and a["dst"].get("term_uid") is not None))
        rbu.append({"node": n, "term_uids": tus, "require": "every listed uid is an input of #{0} in the real end read with the same uid".format(n),
                    "why": "X11 flags row(s) {0} on #{1} (PD365(d)); read from the plan, not typed".format(rows, n)})
    ren, own, wr = SH.base_sink_renames(A, bt, "PD365(d) (chat-T6 rule, applied to " + cfg["STEP_TXT"] + " by card " + cfg["CARD"] +
                                        "): BASE sink terminal(s) of #{0} wired by row(s) {1}; from/to unset")
    print("FACT renames {0} entr(y/ies), {1} term uid(s), owners {2}".format(len(ren), sum(len(e["term_uids"]) for e in ren), sorted(own)), flush=True)
    for e in ren:
        print("FACT  rename node #{0} term_uids {1} rows {2} names {3}".format(e["node"], e["term_uids"], wr[e["node"]], [bt[u]["term_name"] for u in e["term_uids"]]), flush=True)
    gate("R renames ({0}; ZERO ALLOWED); every term uid a base SINK of its owner".format(len(ren)),
         all(not bt[u].get("is_source") and (int(bt[u]["owner_uid"]) == e["node"]) for e in ren for u in e["term_uids"]), ren)
    lic = {"schema": "pb-licence/1", "stage": cfg["STAGE"], "plan": rel(PLAN),
           "decided_by": "docs/d1/ring-p4c.md PD365(d) and PD366(g), applied to {0} ({1}) by card {2}: rename_by_uid where X11 flags a row; renames = "
                         "every BASE sink terminal a row wires BY TERM UID, from/to unset; written by {3}, never typed".format(cfg["STEP_TXT"], cfg["PD"], cfg["CARD"], cfg["MAKER"]),
           "why_a_file": "decision 8 / stage_prerun X6: a recipe never re-types a uid; the licence cannot be a field of the plan (form of " + cfg["PRECEDENT"] + ")",
           "precedent": cfg["PRECEDENT"], "source_plan_md5": md5(PLAN), "rename_by_uid": rbu, "renames": ren}
    json.dump(lic, open(cfg["LIC"], "w", encoding="utf-8"), indent=1)
    back = K.licence_renames(J(LIC))
    want = dict(((u, e["node"]), (None, None)) for e in ren for u in e["term_uids"])
    gate("W licence_renames reads back {0} keys == script's".format(len(back or {})), back == want, back)
    x11b = SPR.buildarray_open_sibling(P, licences=SPR.pb_licences(PLAN))
    gate("X11 after: every flag ({0}) licensed".format(len(x11b)), len(x11b) == len(x11) and all(f["licensed"] for f in x11b), x11b)
    print("FACT md5 {0} {1}".format(md5(LIC), rel(LIC)), flush=True)
    return gate.result([{"path": rel(LIC), "md5": md5(LIC)}])


# ------------------------------------------------------------------------------------------------------------------- PREDICTED ERROR LIST
def el(cfg):
    """cfg: PLAN, SESS, EXPF, OUT, PINS, A0 (A number of action 1), STEP_TXT, CARD, MAKER, UNPRED_WHY, ELR_SPAN. Writes the predicted
    step-end Error List (errorlist-expected/1, entries in the form of EXPF); returns the gate rc."""
    import elrule as ELR                                                                    # noqa: E402
    import errorlist_check as EC                                                            # noqa: E402
    import stagekit as K                                                                    # noqa: E402
    PLAN, SESS, EXPF, OUT, A0 = cfg["PLAN"], cfg["SESS"], cfg["EXPF"], cfg["OUT"], cfg["A0"]
    gate = L.Gate(width=1000)
    ex, P, S = J(EXPF), J(PLAN), J(SESS)
    READF = os.path.join(ROOT, ex["measured_from"])
    _pins_gate(gate, cfg["PINS"])
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
    cleared, stale = [], []
    for r in ROWS:
        ou = (r.get("object") or {}).get("uid")
        st_, nm = is_stale(r, AID)
        if ou is not None and int(ou) in TOUCH:
            cleared.append({"item": r.get("item"), "class": r.get("class"), "object_uid": ou, "action": TOUCH[int(ou)], "A": APOS[TOUCH[int(ou)]],
                            "how": "action names #{0}".format(ou)})
        elif st_:
            stale.append({"item": r.get("item"), "class": r.get("class"), "object_uid": ou, "was": nm, "in_plan": False,
                          "now": "STANDING (entry unchanged): {0} is not an action of {1}; it moves with the step that carries it".format(nm, os.path.basename(PLAN))})
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
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
    W = J(OUT)
    xs, ms, _u = EC.compare(copy.deepcopy(rest), W["expected"])
    gate("W predicted file written, {0} items == total; compare(read minus cleared, the file's own entries) extra {1} missing {2} == raised".format(
         sum(int(r.get("count") or 1) for r in W["expected"]), len(xs), len(ms)), sum(int(r.get("count") or 1) for r in W["expected"]) == TT and not xs and len(ms) == len(raised))
    print("FACT md5 {0} {1}".format(md5(OUT), rel(OUT)), flush=True)
    return gate.result([{"path": rel(OUT), "md5": md5(OUT)}])


# ---------------------------------------------------------------------------------------------------------------------------------- PRED
def pred(cfg):
    """cfg: RRP, PP, SESS, SGF, ELF, LIC, GRAPH, PINS, BEDVI_MD5_PREFIX, A0, LIMIT, MAIN_SRC_READS, CARD, STEP_TXT, NOTE, N_DW, N_DO. Writes the
    pred and the sink-gate census file; returns the gate rc."""
    import stagexec as SX, stage_prerun as SPR, census_predict as CPR                    # noqa: E401
    import stage_shared as SH                                                               # noqa: E402
    import stagekit as K                                                                    # noqa: E402
    RRP, PP, SESS, SGF, ELF, LIC, A0, LIMIT = cfg["RRP"], cfg["PP"], cfg["SESS"], cfg["SGF"], cfg["ELF"], cfg["LIC"], cfg["A0"], cfg["LIMIT"]
    gate = L.Gate()
    ARTS = gate.ARTS
    _pins_gate(gate, cfg["PINS"])
    p, S = J(RRP), J(SESS)
    fz = p.get("finalized") or {}
    bp = fz.get("base") or p.get("base") or {}
    neg = SPR.negative_uids_left(p)
    gate("RB plan FINAL, open_rows_match, {0} actions == session {1}; no negative uid; base not provisional".format(len(p["actions"]), len(S["actions"])),
         p.get("final") is True and fz.get("open_rows_match") is True and [a["id"] for a in p["actions"]] == S["actions"] and not neg
         and not (p.get("base") or {}).get("provisional"), {"base": p.get("base"), "neg": neg[:6]})
    base = J(bp["path"])
    gate("RB2 base IS the real {0} graph {1}; its vi md5 {2}".format(cfg["BEDVI_MD5_PREFIX"], md5(cfg["GRAPH"])[:8], str(base.get("md5"))[:8]),
         md5(os.path.join(ROOT, bp["path"])) == md5(cfg["GRAPH"]) == bp.get("md5") and str(base.get("md5") or "").startswith(cfg["BEDVI_MD5_PREFIX"]),
         (bp, base.get("vi"), base.get("md5")))
    A = p["actions"]
    APOS = dict((a["id"], A0 + n) for n, a in enumerate(A))
    ops = SX.compile_plan(p)
    SC = S["compile"]
    gate("C compile: {0} actions -> {1} ops == session compile (kind, how, acts), each action once".format(len(A), len(ops)),
         [[o["kind"], list(o["acts"])] for o in ops] == [[k, list(a)] for k, _h, a in SC["ops"]] and sorted(n for o in ops for n in o["acts"]) == list(range(1, len(A) + 1)),
         [[o["kind"], o["acts"]] for o in ops])
    cps = list(SX.checkpoint_ops(ops))
    bind = sorted(k for k, o in enumerate(ops, 1) if o["kind"] in SX.BIND_KINDS)
    SFN = dict((int(x["n"]), x) for x in fz.get("step_files") or [])
    cpe = SH.checkpoint_step_table(ops, cps, SFN, A)
    print("FACT E1 checkpoints {0}: {1}".format(cps, [(e["op"], e["kind"], e["action"], e["step_file"]) for e in cpe]), flush=True)
    DWK = sorted(k for k, o in enumerate(ops, 1) if o["kind"] == "delete_wire")
    gate("E1 checkpoints {0} == stagexec.checkpoint_ops == session {1} | delete_wire ops {2}; each has its simulated step file, md5 == recorded".format(cps, SC["checkpoints"], DWK),
         cps == sorted(set(SC["checkpoints"]) | set(DWK)) and all(e["step_file"] and md5(os.path.join(ROOT, e["step_file"])) == e["md5"] for e in cpe), cpe)
    MODEL = SPR.load_memory_model()
    XS0 = SPR.x10_start(base.get("md5"), MODEL)
    START, START_CITE = XS0 if XS0 else (None, None)
    xs = SPR.x10_plan_start(RRP, MODEL)
    SA = S.get("start_mb", (S.get("start") or [None])[0])
    gate("X1 ONE measured start: x10_plan_start(plan) {0} == x10_start({1}) {2} == session start {3}".format(xs and xs[0], cfg["BEDVI_MD5_PREFIX"], START, SA),
         xs is not None and START is not None and xs[0] == START == SA, (xs, XS0))
    KINDS = [o["kind"] for o in ops]
    MAIN, mp, _c = L.main_of(len(ops), KINDS, SX, SPR, MODEL, START, cfg["MAIN_SRC_READS"])
    SXR = S["x10"]
    print("FACT X10 at start {0}: N {1} R {2} Executor peak {3} MAIN {4}; session x10 {5}; card limit {6}; fail_above {7}; MEMSTOP {8}".format(
          START, mp["N"], mp["R"], mp["peak_mb"], MAIN, SXR, LIMIT, mp["fail_above_mb"], SX.MEM_STOP_MB), flush=True)
    gate("X10 MAIN {0} (start {1}) <= {2}; Executor peak {3} == session {4}; MAIN == session {5}".format(MAIN, START, LIMIT, mp["peak_mb"], SXR["exec_peak"], SXR["main"]),
         mp["ok"] and MAIN <= LIMIT and mp["peak_mb"] == SXR["exec_peak"] and MAIN == SXR["main"], mp)
    ok17, det17 = SPR.x17_gate([p])
    gate("X17 over " + cfg["STEP_TXT"], ok17, det17)
    st = lambda n: J(SFN[n]["path"])["state"]                                               # noqa: E731
    last, st0 = st(len(A)), st(0)
    SYM = last.get("sym") or {}
    trows = lambda u: [t for t in last["terminals"] if int(t.get("owner_uid") or 0) == int(u)]   # noqa: E731
    RT = dict((i, r) for r in ((S.get("realsim") or {}).get("route_check") or {}).get("rows") or [] for i in r["ids"])
    ent, objs, DW, DO = [], [], [], []
    for n, a in enumerate(A, 1):
        rt = RT.get(a["id"]) or {}
        e = {"n": n, "A": APOS[a["id"]], "id": a["id"], "op": a["op"], "verdict": "PLAN", "route": rt.get("route"), "route_how": rt.get("how"), "op_k": rt.get("k")}
        if a["op"] == "delete_wire":
            u = int(a["wire_uid"])
            pre, post = st(n - 1), st(n)
            # gone = off every terminal row; the sim's delete_wire opmodel keeps the Wire entry in `objs` (step_01 of ring_p5s02d) - recorded only
            e.update(verdict="DELETE", wire_uid=u, present_before=u in wires_of(pre), gone_after=u not in wires_of(post), objs_entry_after=u in objs_of(post))
            DW.append(e)
        elif a["op"] == "delete_object":
            u = int(a["uid"])
            pre, post = st(n - 1), st(n)
            e.update(verdict="DELETE-OBJECT", uid=u, present_before=u in objs_of(pre) or bool([t for t in pre["terminals"] if int(t.get("owner_uid") or 0) == u]),
                     gone_after=u not in objs_of(post) and not [t for t in post["terminals"] if int(t.get("owner_uid") or 0) == u],
                     wires_on_object_before=attached_wires(pre, u))
            DO.append(e)
        elif a.get("as"):
            syms = sorted(k for k in SYM if k == "new:" + a["as"] or (a["op"] == "add_shift_reg" and k in ("new:" + a["as"] + "L", "new:" + a["as"] + "R")))
            e.update(verdict="NEW", symbols=dict((k, SYM[k]) for k in syms), cls=a.get("class") or a["op"], prim=a.get("prim"),
                     terminals_at_end=dict((k, len(trows(SYM[k]))) for k in syms if isinstance(SYM[k], int)))
            objs.append(e)
        ent.append(e)
    gate("DW delete_wire rows {0}: each present at step n-1 and gone at step n".format([(e["id"], e["wire_uid"]) for e in DW]),
         len(DW) == cfg["N_DW"] and all(e["present_before"] and e["gone_after"] for e in DW), DW)
    gate("DO delete_object rows {0}: each present at step n-1 and gone at step n".format([(e["id"], e["uid"], e["wires_on_object_before"]) for e in DO]),
         len(DO) == cfg["N_DO"] and all(e["present_before"] and e["gone_after"] for e in DO), DO)
    gate("OBJ every created / shift-register / tunnel symbol bound at the sim end: {0}".format([(e["id"], e["symbols"]) for e in objs]),
         len(objs) == sum(1 for a in A if a.get("as")) and all(e["symbols"] and all(isinstance(v, int) for v in e["symbols"].values()) for e in objs)
         and all(len(e["symbols"]) == 2 for e in objs if e["op"] == "add_shift_reg"), objs)
    FM = S.get("frame_map") or {}
    FR = []
    for kk, v in FM.items():
        aid = kk.split("|")[0]
        n = [a["id"] for a in A].index(aid) + 1
        eff = J(SFN[n]["path"]).get("effect") or {}
        wu = eff.get("wire")
        rs = [t for t in last["terminals"] if wu is not None and t.get("wire_uid") == wu]
        e = ent[n - 1]
        e.update(frame_resolved=v.get("real_frame"), frame_addr=v.get("addr"), wire_sim=wu,
                 frame_checks={"frame_map ok": v.get("ok") is True, "sourced": any(t.get("is_source") for t in rs), "has_sink": any(not t.get("is_source") for t in rs)})
        FR.append(e)
    gate("FM frame-addressed rows ({0}) resolved by the session frame_map; the sim-end wire sourced and sunk: {1}".format(
         len(FR), [(e["id"], e["frame_addr"], e["frame_checks"]) for e in FR]), all(all(e["frame_checks"].values()) for e in FR), FR)
    WS = []
    for n, a in enumerate(A, 1):
        if a["op"] != "wire":
            continue
        eff = J(SFN[n]["path"]).get("effect") or {}
        du = eff.get("dst_term_uid")
        row = next((t for t in last["terminals"] if du is not None and t["term_uid"] == du), None)
        WS.append((a["id"], du, bool(row and row.get("wire_uid"))))
    gate("WS every wire row's sink terminal wired at the sim end ({0} rows)".format(len(WS)), WS and all(x[2] for x in WS), WS)
    gate("RT every action has its session route_check row; route_check PASS, 0 unroutable", all(e["route"] for e in ent)
         and ((S.get("realsim") or {}).get("route_check") or {}).get("status") == "PASS" and not any(r.get("unroutable") for r in RT.values()),
         [(e["id"], e["route"]) for e in ent])
    c2 = K.cen2_wire_ends(base["terminals"], last["terminals"], last["terminals"], (base.get("owners") or {}).keys())
    print("FACT CEN2 by ends on the sim end: new pairs {0} (key {1}); stubs {2}".format(c2["new_sim"], c2["key"], c2["stubs"]), flush=True)
    rep = CPR.predict(p, {}, J(os.path.join(B, "census_samples.json")))
    print("FACT CENSUS derived {0}; overall {1}; unpredicted rows {2}".format(rep["derived"], rep["overall"], [A[k - 1]["id"] for k in rep["unpredicted"]]), flush=True)
    csim = collections.Counter(K.sim_census_snapshot(last).values()) - collections.Counter(K.sim_census_snapshot(st0).values())
    print("FACT CENSUS sim end - step 0 by class (information only, NOT a census verdict, PD387(e)) {0}".format(dict(csim)), flush=True)
    EL = J(ELF)
    gate("EL item file {0} keyed to this plan md5; total {1} (cleared {2}, raised {3}, unpredicted {4})".format(rel(ELF), EL["total"], EL["counts"]["cleared"],
         EL["counts"]["raised"], EL["counts"]["unpredicted"]), EL["plan"]["md5"] == md5(RRP) and sum(EL["per_class"]["predicted"].values()) == EL["total"], EL["counts"])
    SGC = L.sg_census(p, SX)
    sgf = {"schema": "ring-session-census/1", "card": cfg["CARD"], "plan": {"path": rel(RRP), "md5": md5(RRP)}, "from_session": {"path": rel(SESS), "md5": md5(SESS)},
           "sink_gate_census": SGC, "actions": len(A), "ops": len(ops), "checkpoints": cps, "start_mb": START, "main_peak_mb": MAIN,
           "note": "stagekit.RingSession reads `sink_gate_census`; computed by prep_c156_a1_1_lib.sg_census (via prep_c164_a2_3_lib.pred)"}
    json.dump(sgf, open(SGF, "w", encoding="utf-8"), indent=1)
    gate("SG census file written: {0} wire row(s) onto a ControlTerminal, {1} need a sink gate".format(len(SGC), sum(1 for e in SGC if e["needs_sink_gate"])),
         J(SGF)["plan"]["md5"] == md5(RRP), SGC)
    el_ = EL["per_class"]
    out = {"schema": "ring-p3b-pred/1", "card": cfg["CARD"], "note": cfg["NOTE"] + "; Error List item-wise (cleared / raised / UNPREDICTED) in " + rel(ELF),
           "plan": {"path": rel(RRP), "md5": md5(RRP)}, "graph": {"path": bp["path"], "md5": md5(os.path.join(ROOT, bp["path"]))}, "bed": base.get("vi"), "bed_md5": base.get("md5"),
           "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": [A[k - 1]["id"] for k in rep["unpredicted"]],
           "census_sim_info": {"by_class": dict(csim), "note": "sim end - step 0 (stagekit.sim_census_snapshot); information only - census_predict has no sample "
                                                               "for these rows, so the census is UNPREDICTED (PD387(e)); the scratch measures it"},
           "ops": KINDS, "cdiff_rows": sorted(fz.get("end_cdiff_rows") or []), "cross_session_refs": "none: planned on the real graph (no rebase)",
           "actions": ent, "new_objects": objs, "frame_rows": FR, "wire_sinks": WS,
           "deletes": [dict((k, e[k]) for k in ("id", "A", "wire_uid", "present_before", "gone_after")) for e in DW],
           "delete_objects": [dict((k, e[k]) for k in ("id", "A", "uid", "present_before", "gone_after", "wires_on_object_before")) for e in DO],
           "cen2": {"judged_by": "Wire class by wire ENDS (source key, sink key, frame) - stagekit.gate_cen2 / cen2_wire_ends (PD389(b)); other classes uid census",
                    "new_pairs_sim": c2["new_sim"], "key": c2["key"], "stubs_sim": c2["stubs"]},
           "e1": {"rule": "PD374(f): graph == sim at every executor checkpoint (stagexec.checkpoint_ops)", "checkpoints": cpe, "move_in_checks": []},
           "keys": {"d_td_pb": "position key (chat-T6, PD366, PD370(b))", "vigraph": {"path": "tools/vigraph.py", "md5": md5(os.path.join(T, "vigraph.py"))}},
           "errorlist": {"bed_total": EL["base_expected"]["total"], "new_items_predicted": EL["counts"]["raised"] - EL["counts"]["cleared"], "predicted_total": EL["total"],
                         "alternative_total": EL["counts"]["total_if_every_unpredicted_raises_one"], "fixed": EL["elrule"]["fixed"],
                         "item_file": {"path": rel(ELF), "md5": md5(ELF)}, "counts": EL["counts"], "cleared": EL["cleared"], "unpredicted": EL["unpredicted"],
                         "stale": EL["stale"],
                         "rule": "PD396(d): item-wise from the expected file (cleared by action) + tools/elrule.py new items (raised); alternative = every "
                                 "UNPREDICTED group raises one item",
                         "rule_source": {"module": "tools/elrule.py", "module_md5": EL["elrule"]["module_md5"], "pd": "PD396(d); PD389(d); PD354(a)"},
                         "base_file": EL["base_expected"]["path"], "checked": False,
                         "per_class": {"start_read": el_["start_read"], "cleared": el_["cleared"], "rule_new": el_["rule_new"], "rule_closed": el_["rule_closed"],
                                       "predicted": el_["predicted"], "classifier": el_["classifier"],
                                       "advisory": "PD354(a): non-zero only for a class in neither start_read.classes nor predicted, or |total diff| > 3"}},
           "memory_pred": {"card": cfg["CARD"], "checkpoints": cps, "R": mp["R"], "N": mp["N"], "bind_ops": bind, "op_kinds": KINDS,
                           "start_mb": START, "start_cite": START_CITE, "start_rule": "stage_prerun.x10_start (PD352(b), PD396(c))", "peak_mb": mp["peak_mb"], "main_peak_mb": MAIN,
                           "card_limit_mb": LIMIT, "fail_above_mb": mp["fail_above_mb"], "below_fail": mp["ok"], "memstop_mb": SX.MEM_STOP_MB, "prerun_start": xs,
                           "model": {"path": rel(SPR.MEMORY_MODEL), "md5": md5(SPR.MEMORY_MODEL)}},
           "licence": {"path": rel(LIC), "md5": md5(LIC)}, "sg_census_file": {"path": rel(SGF), "md5": md5(SGF)},
           "summary": fz.get("summary")}
    json.dump(out, open(PP, "w", encoding="utf-8"), indent=1)
    print("FACT ops", dict(collections.Counter(KINDS)), "census", out["census"], out["census_overall"], "unpredicted", len(out["census_unpredicted"]),
          "| EL", out["errorlist"]["predicted_total"], "alt", out["errorlist"]["alternative_total"], "| end rows", len(out["cdiff_rows"]), "open pairs", len(p.get("open_rows") or []), flush=True)
    for e in ent:
        print("FACT PRED A{0} {1} {2} {3} route {4} {5}".format(e["A"], e["id"], e["op"], e["verdict"], e["route"],
              e.get("symbols") or e.get("wire_uid") or e.get("uid") or e.get("frame_addr") or ""), flush=True)
    ARTS.extend({"path": rel(x), "md5": md5(x)} for x in (PP, SGF))
    gate("SP pred written, keyed to the plan md5", J(PP)["plan"]["md5"] == md5(RRP))
    return gate.result()


# ---------------------------------------------------------------------------------------------------------------------------------- MD5
def unchanged(pins, outs):
    """U: every pinned file's md5 starts with its pin; prints the md5 of every output. Returns the gate rc."""
    gate = L.Gate(fatal_default=False)
    got = dict((p, md5(p)) for p in pins)
    for p in pins:
        print("FACT PIN {0} {1} (pin {2})".format(os.path.basename(p), got[p], pins[p]), flush=True)
    gate("U {0} pinned files unchanged".format(len(pins)), all(got[p].startswith(w) for p, w in pins.items()),
         [os.path.basename(p) for p, w in pins.items() if not got[p].startswith(w)])
    for p in outs:
        print("FACT OUT {0} {1}".format(rel(p), md5(p)), flush=True)
    return gate.result([{"path": rel(p), "md5": md5(p)} for p in outs])


if __name__ == "__main__" and "--selftest" in sys.argv:
    g = L.Gate(fatal_default=False)
    r1 = {"clears_by": {"kind": "action", "action": "A70 w_k3f", "step": 3}}
    r2 = {"clears_by": {"kind": "standing"}}
    g("A is_stale / base_uids", is_stale(r1, {"dw_cond"}) == (True, "A70 w_k3f") and is_stale(r1, {"w_k3f"})[0] is False and is_stale(r2, set())[0] is False
      and base_uids({"op": "delete_wire", "wire_uid": 7}) == {7} and base_uids({"src": {"uid": 3, "term_uid": 4}, "dst": "new:X", "loop": 9}) == {3, 4, 9})
    s = {"terminals": [{"owner_uid": 5, "wire_uid": 11}, {"owner_uid": 6, "wire_uid": 12}, {"owner_uid": 5, "wire_uid": None}]}
    g("B attached_wires", attached_wires(s, 5) == [11] and attached_wires(s, 7) == [] and wires_of(s) == {11, 12})
    sys.exit(g.result())
