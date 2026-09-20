r"""diag_ownerchain_hop.py - STATUS OPEN 1, one more hop. WHO OWNS the three objects the outer-wire read landed on,
and which DIRECTION the two PERIODIC LoopTunnels actually run.

WHAT ALREADY EXISTS (checked before writing a line - CLAUDE.md "before creating any new op, tool or recipe"):
  * `OpOwnerChain_v1.vi` - BUILT and FUNCTIONAL 2026-09-16 (`docs/toolkit-capabilities.md:49`, 20 gates pass,
    `tools/bench/build_opownerchain_v1.log`; B6 read the main VI read-only: 10407 -> Diagram#639, 639 ->
    WhileLoop#637). NO new op is built here. Its driver `read_owner(vi, labels, uid)` is imported VERBATIM from
    `tools/recipes/build_opownerchain_v1.py:246` - it already poisons the outputs before each run, so a property
    read that never happened cannot be mistaken for an answer.
  * `g.tunnels(target, index)` (`tools/gscript.py:747`) ALREADY REPORTS `Is Source?` on BOTH sides of a
    LoopTunnel: `out_is_source` for the outer terminal and `in_is_source` (a list, one per frame) for the INNER
    terminals. `node_terms()` also reports `is_source`, but it is addressed by (diagram index, node index) and the
    two tunnels' diagram/node indices are not recorded anywhere - `tunnels()` is addressed by the same access
    index `main_vi_tunnels.json` already stores. So: TUNNELS() is the reporter used, and no new reader is needed.
  * `tools/bench/main_vi_tunnels.json` - the 132-entry LoopTunnel census (10114 at index 62, 10177 at index 33).
  * `tools/bench/diag_reset_gate_outer.py` - the run this one continues; its `fresh()` preflight and md5 bracket
    are reused. Its four measured wires are NOT re-read.
  * `tools/bench/reset_gate_outer.json` - the four wire rows this hop starts from.
  READ-ONLY on the main VI (rule 1d): md5 asserted unchanged around the whole run.

THE FOUR OBJECTS TO RESOLVE. From `reset_gate_outer.json` / STATUS OPEN 1:
    686  - the `Diagram` that OWNS the terminal driving 10114's OUTER wire 9000. A Diagram is not a source of
           data by itself, so "owner = Diagram 686" means the source terminal belongs to diagram 686; the
           question is WHICH STRUCTURE that diagram belongs to, and what owns that structure.
    <hop> - the owner of 686's owner. One more level, so the nesting is read rather than assumed.
    8634 - the `GrowableFunction` that 10177's outer wire 10166 FEEDS. Which diagram is it on?
    8953 - the `GrowableFunction` that 10114's outer wire 9000 also feeds (the second sink). Which diagram?

PREDICTION CONTRACT (machine-checked below; a miss is a failed prediction and owes a peer review).
  P1  `read_owner(686)` returns a NON-ZERO owner uid with an empty error string, and `uid_back == 686`
      (the op's self-read echo), `cls_back == 'Diagram'` - i.e. 686 really is a Diagram.
  P2  686's owner class is a STRUCTURE or the VI: one of {WhileLoop, ForLoop, CaseStructure, SequenceStructure,
      FlatSequence, StackedSequence, EventStructure, DisableStructure, TimedLoop, VI, Application}. Precedent:
      639 -> WhileLoop#637 (B6). A `Diagram` owning a `Diagram` would be OFF-CONTRACT.
  P3  the second hop (owner of 686's owner) returns class `Diagram` when hop 1 was a structure - structures live
      on diagrams - or terminates (owner uid 0 / class 'VI') when hop 1 was already the VI.
  P4  8634 and 8953 each resolve to owner class `Diagram` with a non-zero uid (a node's owner is its diagram).
  P5  the census still holds: g.tunnels(62).uid == 10114 and g.tunnels(33).uid == 10177, with the out_wire/
      in_wires recorded in main_vi_tunnels.json.
  P6  DIRECTION, the measured part: for each tunnel, exactly one side is the source. `out_is_source` is False
      for both in the census, so the INNER terminals must report is_source TRUE for a tunnel that carries data
      INTO the loop (an input tunnel: the outer terminal consumes from the parent diagram, the inner terminal
      emits onto the subdiagram) and FALSE for one carrying data OUT. Any tunnel reporting the SAME is_source on
      both sides is off-contract and is reported as such.

This script REPORTS. What the chain MEANS for "is the PERIODIC auto-reset gated by `Auto-Reset`", and which wire
or node to read next, is judgement and is NOT written here (CLAUDE.md 3, result-dependent actions).

  MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/diag_ownerchain_hop.log -- py -u tools/bench/diag_ownerchain_hop.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402
from build_opownerchain_v1 import MAIN, OP, LABELS, read_owner  # noqa: E402

CENSUS = os.path.join(HERE, "main_vi_tunnels.json")
OUT = os.path.join(HERE, "ownerchain_hop.json")
STRUCTURAL = ("WhileLoop", "ForLoop", "CaseStructure", "SequenceStructure", "FlatSequence", "StackedSequence",
              "EventStructure", "DisableStructure", "ConditionalDisableStructure", "TimedLoop", "InPlaceStructure",
              "VI", "Application")
# (uid, why it is being read)
SEEDS = [(686, "the Diagram that owns the terminal driving 10114's OUTER wire 9000"),
         (8634, "GrowableFunction fed by 10177's outer wire 10166"),
         (8953, "GrowableFunction fed by 10114's outer wire 9000 (second sink)")]
TUNNELS = [(10114, 62, "the PERIODIC period crosses here (out_name '# FD points')"),
           (10177, 33, "the PERIODIC remainder crosses here")]

_gates = []


def gate(label, ok, detail=""):
    _gates.append((label, bool(ok)))
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}{('   ' + detail) if not ok and detail else ''}", flush=True)
    return bool(ok)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    print(f"MAIN md5 before: {md5}", flush=True)
    if not os.path.exists(OP):
        print("STOP: OpOwnerChain_v1.vi missing", flush=True)
        return 3
    with open(LABELS, encoding="utf-8") as f:
        labels = json.load(f)
    with open(CENSUS, encoding="utf-8") as f:
        census = {t["uid"]: t for t in json.load(f)["tunnels"]}
    g._lv = None
    fresh()
    out = {"owners": [], "tunnels": []}
    try:
        # ---- owner hops -------------------------------------------------------------------------------
        vi = g.op(OP)
        rows = {}
        for uid, why in SEEDS:
            r = read_owner(vi, labels, uid)
            r["why"] = why
            rows[uid] = r
            out["owners"].append(r)
        gate("P1a uid 686 resolved (non-zero owner, no error)",
             rows[686]["owner_uid"] != 0 and not rows[686]["err"] and not rows[686]["errs"],
             f"owner_uid {rows[686]['owner_uid']} err {rows[686]['err']!r} {rows[686]['errs']!r}")
        gate("P1b the op's self-read echoes 686 as class 'Diagram'",
             rows[686]["uid_back"] == 686 and rows[686]["cls_back"] == "Diagram",
             f"self {rows[686]['cls_back']!r}#{rows[686]['uid_back']}")
        gate("P2 686's owner is a structure or the VI", rows[686]["ownercls"] in STRUCTURAL,
             f"got {rows[686]['ownercls']!r}")
        # second hop - the uid comes from the first read, so it cannot be named up front
        hop2 = None
        h1 = rows[686]["owner_uid"]
        if h1:
            hop2 = read_owner(vi, labels, h1)
            hop2["why"] = f"one more hop: the owner of 686's owner ({rows[686]['ownercls']}#{h1})"
            out["owners"].append(hop2)
            gate("P3 the second hop returns class 'Diagram' (or terminates at the VI)",
                 hop2["ownercls"] in ("Diagram", "VI", "Application") or hop2["owner_uid"] == 0,
                 f"got {hop2['ownercls']!r}#{hop2['owner_uid']}")
        else:
            gate("P3 the second hop was reachable", False, "hop 1 returned owner uid 0")
        for uid in (8634, 8953):
            gate(f"P4 {uid} -> owner class 'Diagram', non-zero",
                 rows[uid]["ownercls"] == "Diagram" and rows[uid]["owner_uid"] != 0,
                 f"got {rows[uid]['ownercls']!r}#{rows[uid]['owner_uid']}")
        print("CHAIN (measured, no interpretation):", flush=True)
        for r in out["owners"]:
            print(f"  uid {r['uid']:>6} ({r['cls_back']}) -> owner {r['ownercls']}#{r['owner_uid']}", flush=True)

        # ---- tunnel direction -------------------------------------------------------------------------
        for uid, idx, what in TUNNELS:
            live = g.tunnels(MAIN, idx)
            rec = census.get(uid, {})
            agree = live["uid"] == uid and live["out_wire"] == rec.get("out_wire") \
                and list(live["in_wires"]) == list(rec.get("in_wires", []))
            gate(f"P5 census still true for LoopTunnel #{uid} ({what})", agree,
                 f"live uid {live['uid']} out_wire {live['out_wire']} in_wires {live['in_wires']}")
            ins = live["in_is_source"]
            one_sided = bool(ins) and all(bool(x) != bool(live["out_is_source"]) for x in ins)
            gate(f"P6 LoopTunnel #{uid}: exactly one side is the source", one_sided,
                 f"out_is_source {live['out_is_source']} in_is_source {ins}")
            direction = ("INTO the loop (outer consumes, inner emits)" if (ins and ins[0] and not live["out_is_source"])
                         else "OUT of the loop (inner consumes, outer emits)" if (ins and not ins[0] and live["out_is_source"])
                         else "OFF-CONTRACT (both sides report the same Is Source?)")
            print(f"  MEASURED LoopTunnel #{uid} idx {idx}: out_is_source {live['out_is_source']} "
                  f"(wire {live['out_wire']}, name {live['out_name']!r}) | in_is_source {ins} "
                  f"(wires {live['in_wires']}, names {live['in_names']}) | index_mode {live['index_mode']} "
                  f"=> data flows {direction}", flush=True)
            out["tunnels"].append({"uid": uid, "index": idx, "live": live, "census_agrees": agree,
                                   "direction": direction})
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"   wrote {OUT}", flush=True)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        gate("main VI md5 unchanged (rule 1d: read-only)", same)
        try:
            g.reset()          # release this client's cached VI references (CLAUDE.md reference hygiene)
        except Exception as e:
            print(f"   reset() raised {e}", flush=True)
    npass = sum(1 for _, ok in _gates if ok)
    nfail = len(_gates) - npass
    print(f"=== diag_ownerchain_hop: {npass} pass, {nfail} fail ===", flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
