r"""diag_flatseq_diagrams_attach.py - the cheapest discriminating test for the cycle-13 FAILED PREDICTION.

WHY. `tools/bench/diag_hierarchy_a3.log` gate B2 failed: no route we own reached a flat sequence's frame DIAGRAM
uids (traverse `Tunnel` = 468 objects with ZERO FlatSequence owners; `Structure` = 63 = 84-21;
`MultiFrameStructure` = 43 = 37+4+2; `SequenceTunnel`/`FlatSequenceTunnel` = error 1092; and
`Frames[]` 6363801 on `VI Server:FlatSequence` = error 1077). The mandatory peer review
(`archive/peer/2026-09-16-flatseq-frame-unreachable.md`, codex, ANSWERED 125 s) REFUTED the conclusion with a
specific, checkable claim:

    FlatSequence (class id 16459) has its OWN accessors, parallel to MultiFrameStructure's:
        FlatSequence.Diagrams[]  = 0x3578BC00     <- the frame DIAGRAM references, directly
        FlatSequence.Frames[]    = 0x3578BC07
    and 6363801 was refused simply because it belongs to the WRONG CLASS.

CLAUDE.md: "A peer answer is a HYPOTHESIS - confirm against the machine." This script does exactly that and
nothing else. It builds no op VI and reads nothing from the main VI.

WHAT ALREADY EXISTS (checked first): `g.build_property` (gscript.py:1989) + `g.node_terms_uid` (:731) are the
attach-census pair `build_opcaseframes_v0.py:49-58` uses, and `docs/toolkit-capabilities.md:232` now records WHY
the census - not the absence of error 1077 - is the verdict. `EMPTY_v0.vi` is the scratch donor. Nothing new.

PREDICTION CONTRACT (the peer's claim IS the prediction; a miss is the peer being wrong, not the tool):
  P1  `VI Server:FlatSequence` + `3578BC00` ATTACHES: the creator raises no error AND the new Property node has
      exactly ONE data source terminal (name reported, never guessed).
  P2  `VI Server:FlatSequence` + `3578BC07` likewise attaches.
  P3  CONTROL, re-measuring today's refusal so the comparison is same-session: `VI Server:FlatSequence` +
      `6363801` is REFUSED (error 1077).
  P4  CONTROL, the known-good pair: `VI Server:MultiFrameStructure` + `6363801` attaches with data terminal
      `Frames[]` (build_opcaseframes_v0.log:9-11, five runs).
  Z   the scratch VI is deleted in this same run; the main VI is never opened.

NOT DONE HERE, deliberately: building a reader op that walks `Diagrams[]` and returns the 57 uids. That is a NEW
OP and a judgement call (docs/cycle13-plan.md's STOP condition). This run only says whether the route EXISTS.

  MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/diag_flatseq_diagrams_attach.log -- py -u tools/bench/diag_flatseq_diagrams_attach.py
"""
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402

EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
OUT = os.path.join(HERE, "flatseq_diagrams_attach.json")
# (class, property id, what the peer/our records predict)
CASES = [("VI Server:FlatSequence", "3578BC00", "peer: FlatSequence.Diagrams[] - the frame DIAGRAM refs", True),
         ("VI Server:FlatSequence", "3578BC07", "peer: FlatSequence.Frames[]", True),
         ("VI Server:FlatSequence", "6363801", "CONTROL: MultiFrameStructure.Frames[] on the WRONG class", False),
         ("VI Server:MultiFrameStructure", "6363801", "CONTROL: the known-good pair, 5 recorded runs", True)]

_gates = []


def gate(label, ok, detail=""):
    _gates.append((label, bool(ok)))
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}{('   ' + detail) if detail else ''}", flush=True)
    return bool(ok)


def census(scratch, cls, pid, n_done):
    """Create the Property node and CENSUS its data terminal - the verdict, per toolkit-capabilities.md:232."""
    row = {"class": cls, "pid": pid, "creator_error": "", "all_terminals": None, "data_terminals": None}
    try:
        before = g.uids(scratch, "Property")
        g.build_property(scratch, cls, [(pid, False)], (80 + 70 * n_done, 60))
        new = [u for u in g.uids(scratch, "Property") if u not in before]
        row["new_property_uids"] = new
        terms = []
        for n in range(60):
            uid, rows = g.node_terms_uid(scratch, 0, n)
            if not uid:
                break
            if new and uid == new[0]:
                terms = rows
                break
        row["all_terminals"] = [(r["name"], r["is_source"]) for r in terms]
        data = [r for r in terms if r["is_source"] and r["name"] not in ("reference out", "error out")]
        row["data_terminals"] = [r["name"] for r in data]
        row["attached"] = (len(data) == 1)
        row["verdict"] = (f"ATTACHED - data terminal {data[0]['name']!r}" if len(data) == 1
                          else f"DID NOT ATTACH - {len(data)} data source terminal(s)")
    except Exception as e:
        row["creator_error"] = str(e)[:200]
        row["attached"] = False
        row["verdict"] = f"CREATOR REFUSED - {str(e)[:120]}"
    return row


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    if not os.path.exists(EMPTY):
        print("STOP: EMPTY_v0.vi missing", flush=True)
        return 3
    g._lv = None
    fresh()
    scratch = os.path.join(g.CLAUDEDEV, f"ScratchFS_{os.getpid()}.vi")
    out = {"cases": []}
    try:
        shutil.copy2(EMPTY, scratch)
        print(f"scratch {os.path.basename(scratch)} from EMPTY_v0.vi, ExecState {g.exec_state(scratch)}", flush=True)
        for i, (cls, pid, why, expect) in enumerate(CASES):
            r = census(scratch, cls, pid, i)
            r["why"] = why
            r["expected_to_attach"] = expect
            out["cases"].append(r)
            print(f"  {cls} + {pid}  ({why})\n      {r['verdict']}\n      terminals {r['all_terminals']}",
                  flush=True)
            gate(f"{'P' + str(i + 1)} {cls} + {pid} "
                 f"{'ATTACHES' if expect else 'is REFUSED'}", r["attached"] == expect, r["verdict"])
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        print(f"   wrote {OUT}", flush=True)
    finally:
        try:
            g.close_panel(scratch)
        except Exception:
            pass
        if os.path.exists(scratch):
            os.remove(scratch)
        gate("Z the scratch VI is deleted in the same run", not os.path.exists(scratch))
        try:
            g.reset()          # release this client's cached VI references (CLAUDE.md reference hygiene)
        except Exception as e:
            print(f"   reset() raised {e}", flush=True)
    npass = sum(1 for _, ok in _gates if ok)
    nfail = len(_gates) - npass
    names = [f"{c['class'].split(':')[1]}.{c['pid']}={c['verdict'].split(' -')[0]}" for c in out["cases"]]
    print(f"   RESULT: {' | '.join(names)}", flush=True)
    print(f"=== diag_flatseq_diagrams_attach: {npass} pass, {nfail} fail ===", flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
