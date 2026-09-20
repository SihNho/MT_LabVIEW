r"""diag_owner_semantics.py - A2 (pre-rig-master-plan.md:69): does the OWNER fact hold for every structure class,
or only for CaseStructure? Read-only on the main VI. No op is built, modified or saved.

WHAT ALREADY EXISTS (checked before writing a line - CLAUDE.md "before creating any new op, tool or recipe"):
  * `OpOwnerChain_v1.vi` - BUILT and FUNCTIONAL 2026-09-16 (20 gates, `tools/bench/build_opownerchain_v1.log`).
    Its driver `read_owner(vi, labels, uid)` is imported VERBATIM from `tools/recipes/build_opownerchain_v1.py:246`
    - it poisons the outputs before every run, so a property read that never ran cannot be mistaken for an answer.
    NOTHING about the op is changed here.
  * `g.report_all(target, cls)` (`tools/gscript.py:294`) - pos/uid/class/OWNER-CLASS for every object of a class in
    ONE op run. This is where the 170 diagram UIDs come from.
  * `tools/bench/diagram_hierarchy.json` - `diagram_uid` + `diagram_index` + `owner_class` + a POSITION-MATCHED
    `owner_uid` (it carries a `distance` field: that uid was matched by geometry, which the project's own notes
    call invalid on a Clean-Up'd diagram - which is exactly why A3 exists).
  * `tools/bench/diagram_tree_main.json` - the 170-entry owner-CLASS array and a `structures` uid map for five of
    the six classes.
  * `docs/diagram-hierarchy.md:14-22` - the already-MEASURED structure census (3 WhileLoop, 17 ForLoop,
    37 CaseStructure, 21 FlatSequence, 4 Sequence, 2 EventStructure).
  No new op and no new reader is built. This script only drives ones that exist.

WHAT THE PRIOR-ART REVIEW CHANGED IN THIS SCRIPT (`archive/peer/2026-09-16-priorart-priorart-cycle12-a2.md`,
opus, ANSWERED 481 s - four of its eight verdicts land here and all four were taken):
  B3 `helper-exists`  : the node->Diagram hop is GONE. An earlier draft justified it with "diagram_tree_main.json
                        stores indices, never uids" - true of that file, false of `report_all(MAIN,'Diagram')`,
                        which returns the uid and the owner class for all 170 in one run. 18 op runs removed.
  A3-ii `contradicted`: "five of six classes have never been checked" was FALSE at the class level - the owner
                        CLASS is measured for every diagram in all six (`diagram_hierarchy.json`,
                        `build_diagram_hierarchy_run3.log:2-9`). What is genuinely unmeasured is the owner **UID**
                        read from the machine (`report()` never returns it) and the structure->parent hop, which
                        has never returned for any class. The script is narrowed to those two; the class checks
                        stay only as tripwires and are LABELLED as tripwires.
  B4 `already-measured`: the per-class census is a tripwire on `docs/diagram-hierarchy.md:16-24`, not A2 content.
  B2 `already-failed` : the FlatSequence arm reproduces a KNOWN failure, so it runs ONCE, not three times - and it
                        now reads `errCO` ("error out 10", `opwiresource_v5_labels.json`), the CAST NODE'S OWN
                        ERROR, which `read_owner` never reads. STATUS OPEN 1 and codex both say "the cast failed"
                        is IMPLIED, NEVER MEASURED. Reading one more EXISTING indicator of an existing op is not
                        an op change.

THE MEASUREMENT. `docs/NAMES.md:916-917` states the owner fact for ONE class: a node's `Generic.Owner` is its frame
`Diagram`, and that Diagram's `Owner` is the `CaseStructure`. A3's 170-diagram hierarchy is built on that fact for
all six classes, and on position matching for the uid. So, per class, up to 3 diagrams:

    (A) diagram uid -> its owner: CLASS (a tripwire, already known) and UID (NEW - never read for any class).
    (B) that structure uid -> its owner, expected a `Diagram`: the parent hop, which has NEVER returned.
    (C) cross-checks that cost nothing: the uid against `structures[<class>]`, and against the POSITION-MATCHED
        `owner_uid` in `diagram_hierarchy.json` - i.e. does geometry agree with the machine?

PREDICTION CONTRACT (machine-checked; a miss is a failed prediction and owes a peer review).
  T0  TRIPWIRE, not a finding: `report_all(MAIN,'Diagram')` returns 170 rows and its owner-class histogram equals
      `diagram_tree_main.json`'s (CaseStructure 76, FlatSequenceFrame 57, ForLoop 17, Sequence 11,
      EventStructure 5, WhileLoop 3, '' 1).
  T1  TRIPWIRE: the class census still reads {WhileLoop 3, ForLoop 17, CaseStructure 37, FlatSequence 21,
      Sequence 4, EventStructure 2} (`docs/diagram-hierarchy.md:16-24`).
  S2  "SAME SEMANTICS AS CaseStructure", per class: the diagram's owner class equals the recorded one AND the
      owner UID is NON-ZERO with no error. Predicted TRUE for WhileLoop, ForLoop, CaseStructure, Sequence,
      EventStructure. THE UID HALF IS THE NEW FACT.
  S3  the structure's own owner is a `Diagram` with a non-zero uid. Precedent: `10407 -> Diagram#639`,
      `639 -> WhileLoop#637` (build_opownerchain_v1.log B6). Never yet measured from a diagram-derived structure.
  S4  the structure uid is a member of `diagram_tree_main.json`'s `structures[<class>]` where that list exists.
      FlatSequence has no list - that absence IS the round trip the plan names.
  X   REPORTED, NOT GATED: agreement between the measured owner uid and `diagram_hierarchy.json`'s POSITION-MATCHED
      one. Disagreement is a finding about A3, not a failure of this run, so it is counted and printed, never
      gated - the position match is the thing under suspicion, not the reference.
  FS  FLATSEQUENCE IS PREDICTED TO DIFFER, from a MEASUREMENT not from taste: `diag_ownerchain_hop.log:7` measured
      `Diagram#686 -> FlatSequenceFrame`, owner uid 0, `error 1055`, empty cast echo. One instance, and `errCO` is
      read. `OpOwnerChain_v1` is NOT modified to chase it: codex's uncast `Generic.Class Name`/`Class ID`/`Owner`
      test (`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`) is a separate BUILD and a judgement call
      (CLAUDE.md 3 - a brief states the measurement, never the result-dependent action).
  O   STATUS OPEN 1's three outstanding reads, on the same op in the same run: the owners of `Function` 10068,
      `LoopTunnel` 10114 and `LoopTunnel` 10177. Predicted: each resolves with NO error and a NON-ZERO owner uid.
      The CLASS is deliberately not predicted for the two tunnels (a tunnel may belong to its loop or to a
      diagram; that is what the read is for), and what it means for "is the PERIODIC auto-reset gated by
      `Auto-Reset`" is judgement and is NOT written here.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_owner_semantics.log -- py -u tools/bench/diag_owner_semantics.py
"""
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402
from build_opownerchain_v1 import MAIN, OP, LABELS, read_owner  # noqa: E402

TREE = os.path.join(HERE, "diagram_tree_main.json")
HIER = os.path.join(HERE, "diagram_hierarchy.json")
OUT = os.path.join(HERE, "owner_semantics.json")

# (structure class, the OWNER STRING a diagram owned by it reports, expected census count, how many instances).
# FlatSequence is the one whose diagrams report a FRAME object, and it runs ONCE (prior-art B2).
CLASSES = [("WhileLoop", "WhileLoop", 3, 3),
           ("ForLoop", "ForLoop", 17, 3),
           ("CaseStructure", "CaseStructure", 37, 3),
           ("FlatSequence", "FlatSequenceFrame", 21, 1),
           ("Sequence", "Sequence", 4, 3),
           ("EventStructure", "EventStructure", 2, 2)]
OPEN1 = [(10068, "Function - the PERIODIC modulo; does it sit inside diagram 43?"),
         (10114, "LoopTunnel - the period ENTERS the frame loop here"),
         (10177, "LoopTunnel - the remainder crosses here")]

_gates = []


def gate(label, ok, detail=""):
    _gates.append((label, bool(ok)))
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}{('   ' + detail) if detail else ''}", flush=True)
    return bool(ok)


def read_owner_plus(vi, labels, uid):
    """`read_owner` VERBATIM, plus the ONE indicator it never reads: `errCO`, the cast node's own error.

    STATUS OPEN 1 and `archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md` both record the same gap in our
    own code - `read_owner` collects ("errL","errT","errO","errU","errG") and omits `errCO` although the labels
    file defines it - so "the cast to GObject failed" has been IMPLIED and never MEASURED. This reads an existing
    indicator of an existing op after the same run; it changes no VI.
    """
    r = read_owner(vi, labels, uid)
    lab = labels.get("errCO")
    try:
        r["errCO"] = (g._err(vi, lab) or "") if lab else "(no errCO label in the labels file)"
    except Exception as e:
        r["errCO"] = f"EXC {str(e)[:80]}"
    print(f"        errCO (the cast node's own error): {r['errCO'][:110]!r}", flush=True)
    return r


def clean(r):
    """The measured row, with nothing inferred."""
    return dict(uid=r["uid"], self_cls=r["cls_back"], self_uid=r["uid_back"], owner_cls=r["ownercls"],
                owner_uid=r["owner_uid"], cast_class=r["cast_class"], err=r["err"], errs=r["errs"],
                errCO=r.get("errCO"))


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
    with open(TREE, encoding="utf-8") as f:
        tree = json.load(f)
    with open(HIER, encoding="utf-8") as f:
        hier = json.load(f)
    structures = tree["structures"]
    tree_hist = collections.Counter(tree["owners"])
    # diagram uid -> the POSITION-MATCHED owner uid A3 must replace. Reported, never gated.
    posmatch = {int(r["diagram_uid"]): (r.get("owner_class"), r.get("owner_uid"), r.get("distance"))
                for r in hier.get("resolved", [])}

    g._lv = None
    fresh()
    out = {"diagram_census": {}, "class_census": {}, "classes": {}, "open1": [], "posmatch_disagreements": []}
    try:
        vi = g.op(OP)
        # ---- T0: every diagram uid + its owner CLASS, in ONE op run (prior-art B3) ---------------------
        rows = g.report_all(MAIN, "Diagram")
        hist = collections.Counter(r["owner"] for r in rows)
        out["diagram_census"] = {"n": len(rows), "histogram": dict(hist)}
        print(f"T0 report_all('Diagram'): {len(rows)} rows, owner-class histogram {dict(hist)}", flush=True)
        gate("T0 TRIPWIRE 170 diagrams and the owner-class histogram matches diagram_tree_main.json",
             len(rows) == 170 and hist == tree_hist, f"n={len(rows)} hist={dict(hist)} vs tree {dict(tree_hist)}")

        # ---- T1: the structure census (tripwire on docs/diagram-hierarchy.md:16-24) ---------------------
        print("T1 TRIPWIRE structure census:", flush=True)
        for cls, _owner_str, expect, _n in CLASSES:
            try:
                got = sorted(g.uids(MAIN, cls))
                out["class_census"][cls] = {"count": len(got), "expected": expect, "uids": got}
                gate(f"T1 TRIPWIRE {cls} census == {expect}", len(got) == expect, f"got {len(got)}")
            except Exception as e:
                out["class_census"][cls] = {"count": None, "expected": expect, "error": f"EXC {str(e)[:120]}"}
                gate(f"T1 TRIPWIRE {cls} census == {expect}", False, f"EXC {str(e)[:120]}")

        # ---- the A2 reads: diagram -> structure (uid!) -> parent diagram --------------------------------
        for cls, owner_str, _expect, n_inst in CLASSES:
            picks = [r for r in rows if r["owner"] == owner_str]
            picks.sort(key=lambda r: r["uid"])
            picks = picks[:n_inst]
            inst = []
            print(f"\nCLASS {cls} (diagrams reporting owner {owner_str!r}): "
                  f"{len(picks)} of {sum(1 for r in rows if r['owner'] == owner_str)} read", flush=True)
            for p in picks:
                dg = int(p["uid"])
                r2 = read_owner_plus(vi, labels, dg)
                row = {"diagram_uid": dg, "tree_owner_string": owner_str, "step_diagram_to_structure": clean(r2)}
                if cls == "FlatSequence":
                    gate(f"FS diagram {dg} -> {owner_str}, owner uid 0, error 1055 "
                         f"(reproducing diag_ownerchain_hop.log:7)",
                         r2["ownercls"] == owner_str and r2["owner_uid"] == 0
                         and ("1055" in (r2["err"] + r2["errs"])),
                         f"got {r2['ownercls']!r}#{r2['owner_uid']} err {r2['err'][:50]!r} "
                         f"errs {r2['errs'][:50]!r} cast {r2['cast_class']!r} errCO {str(r2['errCO'])[:60]!r}")
                else:
                    gate(f"S2 {cls} diagram {dg} -> {owner_str} with a NON-ZERO uid and no error",
                         r2["ownercls"] == owner_str and r2["owner_uid"] != 0 and not r2["err"] and not r2["errs"],
                         f"got {r2['ownercls']!r}#{r2['owner_uid']} err {r2['err'][:50]!r} {r2['errs'][:50]!r}")
                st = r2["owner_uid"]
                if st:
                    if cls in structures:
                        gate(f"S4 {cls} structure {st} is in diagram_tree_main.json structures[{cls}]",
                             st in structures[cls], f"uid {st} not in the {len(structures[cls])}-uid list")
                    pm = posmatch.get(dg)
                    if pm:
                        agrees = (pm[1] == st)
                        row["position_match"] = {"owner_class": pm[0], "owner_uid": pm[1], "distance": pm[2],
                                                 "agrees_with_measurement": agrees}
                        print(f"        X position-matched owner for diagram {dg}: {pm[0]}#{pm[1]} "
                              f"(distance {pm[2]}) -> {'AGREES' if agrees else 'DISAGREES'} with the read uid {st}",
                              flush=True)
                        if not agrees:
                            out["posmatch_disagreements"].append({"diagram_uid": dg, "read_uid": st,
                                                                  "position_uid": pm[1], "class": cls})
                    r3 = read_owner_plus(vi, labels, st)
                    row["structure_uid"] = st
                    row["step_structure_to_parent"] = clean(r3)
                    gate(f"S3 {cls} structure {st} -> Diagram, non-zero, no error",
                         r3["ownercls"] == "Diagram" and r3["owner_uid"] != 0 and not r3["err"] and not r3["errs"],
                         f"got {r3['ownercls']!r}#{r3['owner_uid']}")
                else:
                    row["step_structure_to_parent"] = None
                    print(f"        step 'structure -> parent' UNREACHABLE for diagram {dg}: owner uid 0",
                          flush=True)
                inst.append(row)
            out["classes"][cls] = {"tree_owner_string": owner_str, "instances": inst}

        # ---- STATUS OPEN 1's three reads ---------------------------------------------------------------
        print("\nSTATUS OPEN 1 - three owners:", flush=True)
        for uid, why in OPEN1:
            r = read_owner_plus(vi, labels, uid)
            row = clean(r)
            row["why"] = why
            out["open1"].append(row)
            gate(f"O {uid} resolves (non-zero owner, no error)",
                 r["owner_uid"] != 0 and not r["err"] and not r["errs"],
                 f"got {r['ownercls']!r}#{r['owner_uid']} err {r['err'][:50]!r} {r['errs'][:50]!r}")

        # ---- the table, measured, no interpretation ----------------------------------------------------
        print("\nPER-CLASS TABLE (measured; interpretation is NOT written here):", flush=True)
        print("  class | diagram uid -> owner (class#uid) | structure -> parent | position match | error", flush=True)
        for cls, _os, _e, _n in CLASSES:
            for row in out["classes"].get(cls, {}).get("instances", []):
                s2 = row.get("step_diagram_to_structure", {})
                s3 = row.get("step_structure_to_parent") or {}
                pm = row.get("position_match") or {}
                print(f"  {cls} | {row['diagram_uid']} -> {s2.get('owner_cls')}#{s2.get('owner_uid')} | "
                      f"{s3.get('owner_cls')}#{s3.get('owner_uid')} | "
                      f"{pm.get('owner_class')}#{pm.get('owner_uid')}"
                      f"{'' if not pm else (' AGREES' if pm.get('agrees_with_measurement') else ' DISAGREES')} | "
                      f"{(s2.get('err') or '')}{(s2.get('errs') or '')} errCO={str(s2.get('errCO'))[:40]}"[:240],
                      flush=True)
        print(f"\n  X position-match disagreements: {len(out['posmatch_disagreements'])} "
              f"{out['posmatch_disagreements'][:6]}", flush=True)
        print("  OPEN 1: " + " ; ".join(f"{r['uid']} ({r['self_cls']}) -> {r['owner_cls']}#{r['owner_uid']}"
                                        + (f" ERR {r['err'][:30]}" if r["err"] else "")
                                        for r in out["open1"]), flush=True)
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
    print(f"=== diag_owner_semantics: {npass} pass, {nfail} fail ===", flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
