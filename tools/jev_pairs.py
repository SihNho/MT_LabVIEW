r"""jev_pairs.py - connectivity-map plan STEP 5, layer 2: Jev DECIDES per item, code takes the best, LLM gets the rest.

Pre-decided 135: a Jev answer here DRIVES `action` in the decision record - it is not an advisory line. Three
menus, each a small exclusive question over ONE item and its wiki lines (user 2026-09-23: "개별 아이템들 검증"):

  PAIR   noul, per candidate pair from tools/jev_candidates.py: "does this source -> sink realise the intent?"
         Code takes the best p. ACT only when best p >= PAIR_ACT and no second pair >= jev.UNKNOWN_HI (0.70);
         two "yes" answers above 0.70 or a best below PAIR_ACT -> "llm" (asymmetry: a wrong wire is the
         dangerous direction, so ambiguity is never resolved by code).
  OP     choice, <= 3 options, per chosen row: which writer op makes this connection. The options offered are the
         ops whose MEASURED applicability matches the row's classes (OP_MENU below, docs/toolkit-capabilities.md).
  RISK   noul, per chosen row: does wiring it change the ORIGINAL's computation (rule 1a)? state = the row + the
         vigraph effective-source sets. Dangerous direction = "no risk" when there is one, so the row PROCEEDS
         only when p_risk <= RISK_ACT; otherwise "llm".

The thresholds are SET FROM THE MEASURED CURVES (tools/bench/jev_menus_step5.py -> tools/bench/jev_menu_*_result.json)
and are read from tools/bench/jev_menu_thresholds.json at import; a menu whose measured accuracy is below 80 %
carries "acts": false there and every one of its answers becomes "llm" (flag only).

DECISION RECORD (tools/bench/decision_<stage>.json):
  {stage, bed_md5, intent:[...], candidates:[...], decisions:[{row_key:{src_uid,src_term,dst_uid,dst_term},
   pair_p, op, op_p, risk_p, action:"wire"|"llm"|"skip", decided_by, evidence:{...}}], created, jev_calls, cost}

PRIOR ART CHECKED (2026-09-23): tools/jev.py (ask_n consensus = the transport, used unchanged),
tools/jev_rowcheck.py (a consistency noul over a PLANNED row - the question style copied, its tables not used:
this menu works on the live wiki graph), tools/jev_candidates.py (part A). OP_MENU capability sentences are
restated from docs/toolkit-capabilities.md rows 25/67/70, tools/stagekit.py:544-627 and docs/NAMES.md:278-280.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402
import vigraph as V  # noqa: E402

THRESH_FILE = os.path.join(BENCH, "jev_menu_thresholds.json")
COST_PER_CALL = 0.00008      # docs/jev-integration-plan.md:13 - 40 calls $0.0032 (the only measured figure)


def thresholds():
    try:
        return json.load(open(THRESH_FILE, encoding="utf-8"))
    except (OSError, ValueError):
        return {"pair": {"act": 0.90, "acts": False}, "op": {"act": 0.90, "acts": False},
                "risk": {"act": 0.10, "acts": False}, "chain": {"act": 0.90, "acts": False},
                "note": "defaults before measurement - nothing acts"}


# ------------------------------------------------------------------------------------------------ wiki lines
_WIKI_IDX = None


def _wiki_index():
    global _WIKI_IDX
    if _WIKI_IDX is None:
        try:
            _WIKI_IDX = json.load(open(os.path.join(ROOT, "docs", "wiki", "index.json"), encoding="utf-8"))["vis"]
        except (OSError, ValueError, KeyError):
            _WIKI_IDX = {}
    return _WIKI_IDX


def subvi_record(name):
    """The wiki JSON of a subVI by its call-node name ('X.vi'), or None when it is not in the wiki."""
    if not name:
        return None
    base = name[:-3] if name.lower().endswith(".vi") else name
    ent = _wiki_index().get(base)
    if not ent:
        return None
    try:
        return json.load(open(os.path.join(ROOT, ent["json"]), encoding="utf-8"))
    except (OSError, ValueError):
        return None


def wiki_line(t):
    """ONE line for one terminal row (jev_candidates.term_row): node, class, subVI name + the matching
    connector-pane row (label/direction/type) and the one-sentence summary when the wiki has them."""
    head = "node #{0} {1} terminal {2!r} ({3}) on diagram {4}".format(
        t["uid"], t["owner_class"], t["term"], t["term_class"], t["diagram"])
    if not t.get("subvi"):
        return head
    rec = subvi_record(t["subvi"])
    if not rec:
        return head + "; subVI {0!r} (not in the wiki)".format(t["subvi"])
    pane = [p for p in rec.get("connector_pane", []) if p.get("label", "").strip().lower() == t["term"].strip().lower()]
    pl = "; pane row: {0!r} {1} type {2!r}".format(pane[0]["label"], pane[0]["direction"], pane[0].get("type") or "?") \
        if pane else "; no pane row with that label"
    summ = rec.get("summary") or ""
    return head + "; subVI {0!r}{1}{2}".format(t["subvi"], pl, ("; summary: " + summ) if summ else "")


# ------------------------------------------------------------------------------------------------ PAIR menu
PAIR_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW block diagram is being re-wired from a written INTENT. `intent` says which node's output must "
        "feed which node's input, sometimes with terminal-name hints. `candidate` is ONE legal pair: a SOURCE "
        "terminal and a SINK terminal, each with its node uid, node class, terminal name, terminal class and the "
        "diagram it sits on, plus facts computed by code (whether the sink is free, a severed half-wire or already "
        "wired; how many structure borders the wire would cross). `src_wiki` and `dst_wiki` are the project's own "
        "wiki lines for the two terminals. Decide whether THIS pair is the connection the intent asks for. Judge "
        "the terminal identities against the intent and its hints; a terminal may have been renamed by an earlier "
        "edit (a shift register or tunnel takes the name of the wire it carries), so a different name on the SAME "
        "node and the same terminal class can still be the intended terminal."),
    "criteria": {
        "true": "This source terminal and this sink terminal are exactly the ends the intent describes.",
        "false": ("At least one end is not the intended terminal: a different input or output of the node, "
                  "the wrong side of a tunnel or register, or a terminal the hints do not describe."),
    },
}


def pair_state(intent_line, c):
    s, d = c["src"], c["dst"]
    cand = ("SOURCE node #{0} {1} terminal {2!r} ({3}, diagram {4})  ->  SINK node #{5} {6} terminal {7!r} "
            "({8}, diagram {9}); sink is {10}; scope {11}, borders {12}".format(
                s["uid"], s["owner_class"], s["term"], s["term_class"], s["diagram"], d["uid"], d["owner_class"],
                d["term"], d["term_class"], d["diagram"], c["sink_state"], c["scope"], c["borders"]))
    return {"intent": intent_line, "candidate": cand, "src_wiki": wiki_line(s), "dst_wiki": wiki_line(d)}


def ask_pair(intent_line, c, n=None):
    p, spread, err = jev.ask_n(pair_state(intent_line, c), {"pair": PAIR_Q}, n=n, purpose="step5-pair")
    return p, spread, err


# ------------------------------------------------------------------------------------------------ OP menu
OP_MENU = {
    "connect_nested": ("OpConnectNested_v1/v2 (stagekit .connect): Terminal.Connect Wire with BOTH ends addressed "
                       "as Diagram[i].Nodes[j].Terminals[k]; the two ends may be on different diagrams. "
                       "Diagram.Nodes[] enumerates functions, subVIs, Locals, constants and structures (a "
                       "structure's border tunnels appear as the STRUCTURE node's terminals); it cannot address a "
                       "tunnel's or shift register's own terminal object, a front-panel control terminal or a "
                       "severed half-wire."),
    "connect_from_wire": ("OpConnectFromWire_v0 (stagekit .connect_from_wire): SINK addressed as "
                          "Diagram/Nodes/Terminals; SOURCE = a terminal already on an EXISTING wire, addressed by "
                          "that wire's uid and terminal index. The only writer whose source need not be a node - "
                          "used when the source is a loop tunnel's inner terminal, a shift-register terminal or a "
                          "live net; it branches onto that wire."),
    "wire_sr": ("OpWireSR_* (stagekit .wire_sr, variants RightIn / LeftIn / LeftOutNode / LeftOutCtl): wires ONE "
                "side of a shift register on a loop addressed by loop index + register index: RightIn = a body "
                "node's output INTO the right register; LeftIn = the left register's inside value into a body "
                "node's input; LeftOut* = the register's initial value from outside the loop."),
    "fs_inner_tunnel_connect": ("OpFsInnerTunnelConnect_v1 (stagekit .fs_inner_tunnel_connect): connects a "
                                "source terminal addressed by index triple to a FlatSequenceInnerTunnel's terminal "
                                "addressed by the tunnel's UID."),
    "wire_indicators": ("gscript.wire_indicators (stagekit .wire_indicators): branches a node's named OUTPUT onto "
                        "a front-panel INDICATOR's diagram terminal (ControlTerminal), addressed by the "
                        "indicator's label. connect_ctl does the same on the TOP-LEVEL diagram only."),
}
SR_CLS = ("LeftShiftRegister", "RightShiftRegister")
FS_CLS = ("FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel")


def op_options(c):
    """<= 3 exclusive options, chosen by the row's CLASSES only (a hard fact, not a ranking)."""
    s, d = c["src"], c["dst"]
    classes = {s["owner_class"], d["owner_class"]}
    base = ["connect_nested", "connect_from_wire"]
    if d["owner_class"] == "ControlTerminal" or d["term_class"] == "ControlTerminal":
        return ["wire_indicators"] + base
    if d["owner_class"] == "FlatSequenceInnerTunnel":          # the op addresses an FSIT SINK by uid
        return ["fs_inner_tunnel_connect"] + base
    if classes & set(SR_CLS):
        return ["wire_sr"] + base
    return base


TUNNEL_BORDER = ("SelectorTunnel", "Tunnel", "LoopTunnel")
NOT_A_NODE = TUNNEL_BORDER + SR_CLS + FS_CLS + ("ControlTerminal", "Diagram", "TopLevelDiagram")


def op_rule(c, top_diagram=None):
    """PRE-DECIDED 143 as code: the writer op chosen by the row's CLASSES; (op, variant, why) or (None, None, why)
    when the rule has no entry (then, and only then, Jev's OP menu is asked). Order = the Pre-decided sentence:
      ControlTerminal end            -> connect_ctl
      source already on a live wire  -> connect_from_wire
      FlatSequenceInnerTunnel sink   -> fs_inner_tunnel_connect
      shift-register INSIDE terminal -> wire_sr (LeftIn: left inner source; RightIn: right inner sink)
      node <-> node                  -> connect_terminals on the TOP-LEVEL diagram (it addresses VI.Block Diagram
                                        Nodes[] only, gscript.py:2528), connect_nested on any nested diagram. A
                                        Selector/Loop tunnel's OUTER terminal counts as a node end: it is addressed
                                        as a terminal of its STRUCTURE node (OP_MENU connect_nested).
    """
    s, d = c["src"], c["dst"]
    if "ControlTerminal" in (s["owner_class"], d["owner_class"], s["term_class"], d["term_class"]):
        return "connect_ctl", None, "a ControlTerminal end"
    if s.get("wire_uid"):
        return "connect_from_wire", None, "source terminal is on live wire w{0}".format(s["wire_uid"])
    if d["owner_class"] == "FlatSequenceInnerTunnel":
        return "fs_inner_tunnel_connect", None, "FSIT sink"
    if s["owner_class"] == "LeftShiftRegister" and s["term_class"] == "InnerTerminal":
        return "wire_sr", "LeftIn", "left register inside -> body node"
    if d["owner_class"] == "RightShiftRegister" and d["term_class"] == "InnerTerminal":
        return "wire_sr", "RightIn", "body node -> right register inside"

    def node_end(e):
        return e["owner_class"] not in NOT_A_NODE or \
            (e["owner_class"] in TUNNEL_BORDER and e["term_class"] == "OuterTerminal")
    if node_end(s) and node_end(d):
        top = top_diagram is not None and s["diagram"] == d["diagram"] == top_diagram
        return ("connect_terminals" if top else "connect_nested"), None, "node <-> node ({0})".format(
            "top-level" if top else "nested diagram {0}/{1}".format(s["diagram"], d["diagram"]))
    return None, None, "no rule entry: {0} {1} -> {2} {3}".format(s["owner_class"], s["term_class"],
                                                                  d["owner_class"], d["term_class"])


def op_question(opts):
    return {"type": "choice",
            "instructions": (
                "A LabVIEW scripting project has a small set of MEASURED writer operations. `row` is ONE connection "
                "to make: source and sink terminal with their node class, terminal class and diagram. Choose the "
                "ONE writer operation whose measured addressing can reach BOTH ends of this row as they are. Judge "
                "by what each op can address (the option descriptions), not by which op is most general."),
            "criteria": dict((o, OP_MENU[o]) for o in opts)}


def op_state(c):
    s, d = c["src"], c["dst"]
    return {"row": ("SOURCE #{0} {1} terminal {2!r} ({3}, diagram {4}) -> SINK #{5} {6} terminal {7!r} ({8}, "
                    "diagram {9}); scope {10}".format(s["uid"], s["owner_class"], s["term"], s["term_class"],
                                                      s["diagram"], d["uid"], d["owner_class"], d["term"],
                                                      d["term_class"], d["diagram"], c.get("scope")))}


def ask_op(c, n=None):
    opts = op_options(c)
    probs, spread, err = jev.ask_n(op_state(c), {"op": op_question(opts)}, n=n, purpose="step5-op")
    if not probs:
        return None, None, opts, err
    best = max(probs, key=probs.get)
    return best, probs, opts, err


# ------------------------------------------------------------------------------------------------ RISK menu
RISK_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW VI is being restructured under ONE hard rule: only SCHEDULING may change (tunnels, shift "
        "registers, loop structure, Local relays, Wait/timing); the per-item COMPUTATION of the original - which "
        "computation node feeds which computation input - must stay identical. `change` is ONE edit (a wire, or a "
        "node added). `evidence` is computed by code from the original's graph and the edited graph: the "
        "COMPUTATION sources that reach the affected input once scheduling relays are walked through, before and "
        "after, and whether a node is new. Decide whether this edit CHANGES the original's computation."),
    "criteria": {
        "true": ("The edit changes computation: a computation node that the original does not have, or an input "
                 "whose effective computation source differs from the original's."),
        "false": ("The edit is scheduling only: the effective computation sources are identical before and after, "
                  "and no computation node is added."),
    },
}


def ask_risk(change_line, evidence, n=None):
    p, spread, err = jev.ask_n({"change": change_line, "evidence": evidence}, {"risk": RISK_Q}, n=n,
                               purpose="step5-risk")
    return p, spread, err


def risk_evidence(G_orig, G_new, c, orig_sink_key=None):
    """Code-computed rule-1a evidence for wiring candidate c in G_new: the effective computation sources of the
    sink in the ORIGINAL vs what the candidate source would bring (vigraph ASSUMPTION A)."""
    sk = c["src"]["key"]
    new_src = {sk} if not V.transparent(G_new, sk) else set(V.effective_sources(G_new, sk))
    orig = set(V.effective_sources(G_orig, orig_sink_key)) if orig_sink_key and orig_sink_key in G_orig["rows"] \
        else None
    return {"original_effective_sources": sorted(V.show(x) for x in orig) if orig is not None else "sink not in original",
            "candidate_brings": sorted(V.show(x) for x in new_src),
            "identical": (orig is not None and set(V.show(x) for x in orig) == set(V.show(x) for x in new_src)),
            "assumption": "A (vigraph.SCHED_OWNER) - awaiting the user, plan OPEN A"}


# ------------------------------------------------------------------------------------------------ one intent
def decide(intent_line, cand, G_orig=None, G_new=None, orig_sink_key=None, n=None, th=None, by_rule=False,
           risk_gates=True, top_diagram=None):
    """Run PAIR over every candidate, then OP and RISK on the chosen one. Returns one decision dict.
    by_rule=True  -> Pre-decided 143: `op_rule` first, Jev's OP menu only when the rule has no entry.
    risk_gates=False -> Pre-decided 144: RISK is asked and RECORDED, never changes `action`."""
    th = th or thresholds()
    pairs = cand["pairs"]
    calls = 0
    rk = {"src_uid": None, "src_term": None, "dst_uid": None, "dst_term": None}
    if not pairs:
        return {"row_key": rk, "pair_p": None, "op": None, "op_p": None, "risk_p": None, "action": "llm",
                "decided_by": "python", "evidence": {"reason": "no legal candidate", "excluded": cand["excluded"],
                                                     "failed_layer": "candidate"},
                "jev_calls": 0}
    scored = []
    for c in pairs:
        p, spread, err = ask_pair(intent_line, c, n=n)
        calls += (spread or {}).get("n", 0) if spread else jev.samples()
        scored.append({"row_key": c["row_key"], "p": p, "spread": (spread or {}).get("spread"), "err": err})
    ok = [s for s in scored if s["p"] is not None]
    if not ok:
        return {"row_key": rk, "pair_p": None, "op": None, "op_p": None, "risk_p": None, "action": "llm",
                "decided_by": "python", "evidence": {"reason": "jev gave no answer", "pairs": scored, "failed_layer": "verdict"},
                "jev_calls": calls}
    ok.sort(key=lambda s: -s["p"])
    best = ok[0]
    c = pairs[scored.index(best)]
    many = [s for s in ok if s["p"] >= jev.UNKNOWN_HI]
    ev = {"pairs": scored, "n_yes_above_0.70": len(many)}
    action, by = "wire", "jev"
    if not th["pair"].get("acts"):
        action, ev["reason"] = "llm", "pair menu does not act (measured < 80 % or unmeasured)"
    elif best["p"] < th["pair"]["act"]:
        action, ev["reason"] = "llm", "best p {0:.3f} < act threshold {1}".format(best["p"], th["pair"]["act"])
    elif len(many) >= 2:
        action, ev["reason"] = "llm", "{0} candidates >= 0.70 (asymmetry)".format(len(many))
    variant, op_by = None, "jev"
    op = None
    if by_rule:
        op, variant, ev["op_rule"] = op_rule(c, top_diagram)
        op_by = "python-rule" if op else "jev"
    if op:
        op_p, probs, opts = None, None, None
    else:
        op, probs, opts, _e = ask_op(c, n=n)
        calls += jev.samples() if n is None else n
        op_p = probs.get(op) if probs else None
        if action == "wire" and (not th["op"].get("acts") or op_p is None or op_p < th["op"]["act"]):
            action, ev["reason"] = "llm", "op menu does not act or op_p below threshold"
            ev["failed_layer"] = "op"
    ev["op_options"], ev["op_probs"], ev["op_decided_by"] = opts, probs, op_by
    risk_p = None
    if G_orig is not None and G_new is not None:
        rev = risk_evidence(G_orig, G_new, c, orig_sink_key)
        line = "wire {0} -> {1}".format(V.show(c["src"]["key"]), V.show(c["dst"]["key"]))
        risk_p, _sp, _e = ask_risk(line, rev, n=n)
        calls += jev.samples() if n is None else n
        ev["risk_evidence"] = rev
        if risk_gates and action == "wire" and (not th["risk"].get("acts") or risk_p is None or
                                                 risk_p > th["risk"]["act"]):
            action, ev["reason"] = "llm", "risk menu does not act or p_risk above threshold"
            ev["failed_layer"] = "risk"
    if action == "llm" and "failed_layer" not in ev:
        ev["failed_layer"] = "verdict"
    return {"row_key": {"src_uid": c["row_key"]["src_uid"], "src_term": c["row_key"]["src_term"],
                        "dst_uid": c["row_key"]["dst_uid"], "dst_term": c["row_key"]["dst_term"]},
            "pair_p": best["p"], "op": op, "variant": variant, "op_p": op_p, "risk_p": risk_p, "action": action,
            "decided_by": by, "evidence": ev, "jev_calls": calls,
            "exec": {"src": dict((k, c["src"][k]) for k in ("uid", "term", "term_uid", "term_class", "owner_class",
                                                             "diagram", "wire_uid")),
                     "dst": dict((k, c["dst"][k]) for k in ("uid", "term", "term_uid", "term_class", "owner_class",
                                                             "diagram", "wire_uid"))}}


def write_record(stage, bed_md5, intents, cands, decisions, t0, extra=None):
    calls = sum(d.get("jev_calls", 0) for d in decisions)
    rec = {"stage": stage, "bed_md5": bed_md5, "intent": intents,
           "candidates": [{"intent": c["intent"], "resolved": c["resolved"], "excluded": c["excluded"],
                           "pairs": [{"row_key": p["row_key"], "sink_state": p["sink_state"], "scope": p["scope"],
                                      "borders": p["borders"], "cycle_overapprox": p["cycle_overapprox"]}
                                     for p in c["pairs"]]} for c in cands],
           "decisions": decisions, "created": time.strftime("%Y-%m-%d %H:%M:%S"), "jev_calls": calls,
           "cost": {"usd_est": round(calls * COST_PER_CALL, 5), "basis": "docs/jev-integration-plan.md:13",
                    "seconds": round(time.time() - t0, 1)},
           "thresholds": thresholds()}
    if extra:
        rec.update(extra)
    p = os.path.join(BENCH, "decision_{0}.json".format(stage))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rec, f, indent=1)
    return p, rec
