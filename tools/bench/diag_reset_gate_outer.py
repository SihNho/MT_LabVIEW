r"""diag_reset_gate_outer.py - STATUS OPEN 1, the cheap route: who drives the OUTER wires of LoopTunnels
#10114 and #10177, the pair that carries the PERIODIC auto-reset across the frame-loop border.

WHAT ALREADY EXISTS (checked before writing a line of this, CLAUDE.md "before creating any new op, tool or
recipe"):
  * `tools/bench/main_vi_tunnels.json` - the LoopTunnel census of the main VI is ALREADY MEASURED, 132 entries:
        uid 10114 (index 62) out_name '# FD points', out_wire 9000, in_wires [10103], out_is_source False
        uid 10177 (index 33) out_name ''           , out_wire 10187, in_wires [10166], out_is_source False
    So `tunnels()` does not have to be re-run to learn the outer wire uids; this script re-reads the two entries
    anyway (one op run each) ONLY to confirm the census still matches the file on disk before acting on it.
  * `tools/bench/diag_reset_arm.py` / `.log` - already resolved wires 10103 and 10187 (and 9868, 3457). It did
    NOT read 9000 or 10166, which is exactly the hop OPEN 1 is missing.
  * `OpWireSource_v5` - the reader (12/12 verified). `read_terminal()` from `build_opwiresource_v5.py` and the
    `fresh()` preflight from `build_opconstvalue_v1.py` are reused verbatim, as `diag_case5540_inputs.py` does.
  * No new op VI is built. READ-ONLY on the main VI (rule 1d): md5 asserted unchanged around the run.

THE FOUR WIRES. 9000 = 10114's outer side; 10103 = 10114's inner side (re-read, previously ('LoopTunnel',10114)
-> ('Function',10068)); 10187 = 10177's other side (previously ('Function',10068) -> ('LoopTunnel',10177));
10166 = 10177's remaining side, never read. Reading all four in one client makes the direction of both tunnels
readable from the data instead of from the census's out/in labels.

PREDICTION CONTRACT - what "gated" and "not gated" look like in the wire sources.
The known gate shape in this VI is the lost-bead arm: an `And`, uid 9647, class `Function`, combining the arming
boolean with the switch (`diag_reset_arm.log:14-17`, wire 9868 -> ('Function', 9647)). So, for the PERIODIC arm:

  GATED      the source of 10114's outer wire 9000 is a COMBINER, not a control: owner_class `Function`
             (LabVIEW's `And` / `Select` primitives report as `Function`) or `CompoundArithmetic`, or a
             `CaseStructure` output tunnel - i.e. the value entering the loop is computed, and one of that
             node's inputs is where `Auto-Reset` would enter. Same signature on 10177's outer wire: a sink of
             class `Function` / `CompoundArithmetic` downstream of the remainder.
  NOT GATED  the source of 9000 is a front-panel control terminal (owner_class `Terminal` / `ControlTerminal`)
             or a `Constant`, with no combiner between it and the tunnel; and the remainder's outer wire reaches
             only comparison / indicator / structure objects, no boolean combiner.
  NEITHER    the source is another `LoopTunnel` / `Tunnel` / `SubVI` - the decision is assembled one diagram
             further out, this run does not answer OPEN 1, and the next wire to read is named in the output.

This script REPORTS; it does not conclude. Which of the three the numbers mean, and what follows for OPEN 1, is
a judgement call and stays under OPEN.

  MATERIAL=1 py tools/bgrun.py --max-min 12 --log tools/bench/diag_reset_gate_outer.log -- py -u tools/bench/diag_reset_gate_outer.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import MAIN, fresh  # noqa: E402
from build_opwiresource_v5 import OP, MAP_OUT, read_terminal  # noqa: E402

CENSUS = os.path.join(HERE, "main_vi_tunnels.json")
OUT = os.path.join(HERE, "reset_gate_outer.json")
# (tunnel uid, access index recorded in main_vi_tunnels.json, what STATUS says it carries)
TUNNELS = [(10114, 62, "the PERIODIC period enters the frame loop here (out_name '# FD points')"),
           (10177, 33, "the PERIODIC remainder crosses the frame-loop border here")]
# wire uid -> role. 9000 and 10166 are the NEW reads; 10103 and 10187 are re-reads of diag_reset_arm's result.
WIRES = [(9000, "10114 OUTER (never read) - the period's source outside the loop"),
         (10103, "10114 INNER (re-read; diag_reset_arm: ('LoopTunnel',10114) -> ('Function',10068))"),
         (10187, "10177 side A (re-read; diag_reset_arm: ('Function',10068) -> ('LoopTunnel',10177))"),
         (10166, "10177 side B (never read) - the remaining side of the remainder tunnel")]
COMBINER = ("Function", "CompoundArithmetic")
CONTROLISH = ("Terminal", "ControlTerminal", "Constant")


def resolve(vi, labels, wire, role):
    rows = []
    for i in range(8):
        r = read_terminal(vi, labels, wire, i)
        if r["errs"] and r["owner_uid"] == 0:
            break
        rows.append(r)
    srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire]
    sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"] and r["owner_uid"]]
    src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if srcs else None
    print(f"RESULT wire {wire} [{role}]: source {src}; sinks {sinks}", flush=True)
    return dict(wire=wire, role=role, source=src, sinks=sinks, n_terms=len(rows))


def classify(src):
    if not src:
        return "NEITHER (no source terminal resolved)"
    cls = src[0]
    if cls in COMBINER:
        return f"matches the GATED signature (combiner class {cls!r})"
    if cls in CONTROLISH:
        return f"matches the NOT-GATED signature (control/constant class {cls!r})"
    return f"NEITHER signature - class {cls!r}, the decision is assembled further out"


def main():
    md5 = hashlib.md5(open(MAIN, "rb").read()).hexdigest()
    print(f"MAIN md5 before: {md5}", flush=True)
    with open(MAP_OUT, encoding="utf-8") as f:
        labels = json.load(f)
    with open(CENSUS, encoding="utf-8") as f:
        census = {t["uid"]: t for t in json.load(f)["tunnels"]}
    fresh()
    out = {"tunnels": [], "wires": []}
    ok = True
    try:
        for uid, idx, what in TUNNELS:
            live = g.tunnels(MAIN, idx)
            rec = census.get(uid, {})
            agree = live["uid"] == uid and live["out_wire"] == rec.get("out_wire") \
                and list(live["in_wires"]) == list(rec.get("in_wires", []))
            print(f"{'PASS' if agree else 'FAIL'}  census still true for LoopTunnel #{uid} ({what}): live "
                  f"uid {live['uid']} out_wire {live['out_wire']} in_wires {live['in_wires']} "
                  f"out_is_source {live['out_is_source']} vs recorded out_wire {rec.get('out_wire')} "
                  f"in_wires {rec.get('in_wires')}", flush=True)
            ok = ok and agree
            out["tunnels"].append({"uid": uid, "live": live, "recorded": rec, "agree": agree})
        vi = g.op(OP)
        for wire, role in WIRES:
            row = resolve(vi, labels, wire, role)
            out["wires"].append(row)
        for uid, _idx, _what in TUNNELS:
            w = out["tunnels"][[t["uid"] for t in out["tunnels"]].index(uid)]["live"]["out_wire"]
            row = [r for r in out["wires"] if r["wire"] == w]
            if row:
                print(f"OBSERVED signature: LoopTunnel #{uid} outer wire {w} source {row[0]['source']} -> "
                      f"{classify(row[0]['source'])}", flush=True)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"   wrote {OUT}", flush=True)
    finally:
        same = hashlib.md5(open(MAIN, "rb").read()).hexdigest() == md5
        print(f"   {'PASS' if same else 'FAIL'} main VI unchanged (rule 1d: read-only)", flush=True)
        ok = ok and same
        try:
            g.reset()          # release this client's cached VI references (CLAUDE.md reference hygiene)
        except Exception as e:
            print(f"   reset() raised {e}", flush=True)
    print(f"=== SUMMARY {len(out['wires'])}/{len(WIRES)} wires resolved, census agreement "
          f"{sum(1 for t in out['tunnels'] if t['agree'])}/{len(TUNNELS)} ===", flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
