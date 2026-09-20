r"""diag_typectl_v2 - Pre-decided 40(c)+(d), SECOND ATTEMPT: VALIDATE `Wire.Is Broken?` BEFORE IT IS EVER A GATE.

🔴 A DIAGNOSTIC under `tools/bench/`, NEVER a recipe and never to be moved under `tools/recipes/`.
🔴 IT REPORTS FACTS AND INTERPRETS NOTHING. Whether a mismatched wire reads broken decides the queue path's
   future, and that decision is the judgement session's (Pre-decided 40, STATUS "NEXT"). Nothing here is a
   recommendation; nothing here chooses a donor, a sink, or a next stage.
🔴 **NO QUEUES IN THIS RUN** (40(d), which overrides STATUS's NEXT bullet on this point): the untested
   INSTRUMENT and the untested SUBJECT must not go into one experiment. `gscript.queue_node` is NOT imported
   and NOT called.
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 NO NEW OP IS BUILT (Pre-decided 2; user 2026-09-18 08:53). No motor, no ASI, no camera, no GUI action.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are never opened for writing; their
   md5s are probed before and after. Every edit happens on a DATED SCRATCH copy of the S2 artefact.

WHY THERE IS A SECOND ATTEMPT, AND WHAT CHANGED. Attempt 1
(`tools/bench/diag_queue_typetest_control.{py,log,json}`) never reached the control pair: its FIXED sink rule -
"the first bare NAMED input terminal on one of five numeric-arithmetic nodes" - found ZERO candidates, because
those nodes' inputs are all live and wired on a working VI. Judgement has accepted the reason: **"no bare
REQUIRED input" is ENTAILED by `ExecState == 1`**, so that rule could not succeed on any non-broken VI. The rule
is WITHDRAWN. Attempt 1's own census supplies the fix and is NOT repeated here.

**THE SINKS ARE NOW GIVEN, NOT RESOLVED BY A RULE** (from `tools/bench/diag_queue_typetest_control.json`
["diagram_686_terminal_census"]): `#2048 'Array Subset'` (Nodes[7] there) exposes t4 `'index'` and t5 `'length'`
- both bare (`wire == 0`), both NAMED, both type-constrained numerics. They are bare because they are OPTIONAL,
which is precisely why they survive on a compiling VI.

THE CONTROL PAIR - one variable only, the donor's TYPE, and the SAME sink terminal on both legs:
  Leg M (matched)     `#8486` t0 `'x+1'`             (numeric) -> `#2048` t4
  Leg X (mismatched)  `#250`  t1 `'IMAQdx Session'`  (refnum)  -> `#2048` t4
Each leg runs on ITS OWN dated scratch copy of `claudeDev\D1_s2_loops.vi`, so neither leg can contaminate the
other's `ExecState`. All three nodes are on `Diagram #686`; `owner_of` is re-read live on every scratch, never
inherited from attempt 1.

THE t5 SUBSTITUTION RULE, mechanical and declared in advance (the brief's contingency): if `#2048` t4 refuses
for a reason unrelated to type, use t5 for BOTH legs and report the substitution. "Refuses" is defined
MECHANICALLY as: the MATCHED leg - the leg whose types agree - ends with NO wire on t4 (`wire` falsy) or with a
non-empty op error column. In that case both legs are re-run at t5 on two FRESH scratch copies and every reading
from the t4 attempt is kept verbatim alongside. The rule is not applied on the mismatched leg's outcome, which
is the thing being measured.

THE TWO DISCRIMINATORS, READ IN THIS ORDER (a peer flags that `Is Broken?` PERTURBS its target,
`docs/NAMES.md:912-921` - so the unperturbed reading is taken first):
  1. `ExecState` BEFORE the connection, and AGAIN immediately after it.
  2. THEN `Wire.Is Broken?` **6371004**. ⚠️ Its verified location is `docs/NAMES.md:902-911`; the plan's
     `:888-897` citation is WRONG (that range is the case-structure property-ID block) and is not used.
⚠️ THE ORDERING TRAP (`docs/NAMES.md:905-911`): the `Is Broken?` readout inside `OpConnectNested_v1` ships with
its `error in (no error)` UNWIRED, so on the WRITING pass it may execute BEFORE the `Connect Wire` and describe
the OLD (absent) wire. The measured route to an ORDERED reading (`docs/NAMES.md:912-918`) is an IDEMPOTENT
re-connect of the SAME source->sink pair (0 new Wire objects), after which the readout necessarily describes the
wire that already exists. So both passes are recorded per leg - `pass1` (write, readback possibly stale) and
`pass2` (idempotent, THE READING) - and every `ExecState` taken after a pass2 is marked SUSPECT.

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (`grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `build_opconnectnested_v1.connect_nested_v1` `:418` (`OpConnectNested_v1.vi`) - the BUILT writer named by
    the brief, 5 for 5 on same-diagram rows in cycle 54 (`tools/bench/diag_s3_focus_trial.log`).
    `docs/toolkit-capabilities.md:68` describes it as "two DIFFERENT nested diagrams", but its two Traverse
    ladders are INDEPENDENT and cycle 54 drove all five of its wires with `src_diag == sink_diag`
    (`diag_s3_focus_trial.py:485-486`), so the SAME-diagram case is the measured case. The plain same-diagram
    ops `docs/toolkit-capabilities.md` names - `connect_terminals` `:2407` and `connect2` `:2633` - are REJECTED
    here because both require a TOP-LEVEL end and `Diagram #686` is not the top-level block diagram. This is the
    brief's "say which you used and why".
  * `gscript.report_all` `:488`, `node_terms_uid` `:925`, `count` `:1005`, `exec_state` `:1977`, `save` `:2062`,
    `open_panel`/`close_panel` `:1241`/`:1257`, `ref_counts` `:233`, `reset` `:262`.
    `gscript.queue_node` `:1122` is DELIBERATELY NOT USED (40(d)).
  * `diag_queue_typetest_control` - the template for this script (its structure is reused verbatim where it was
    sound) and the source of the GIVEN sink pair.
  * `diag_s2_scaffold.fresh` `:156` / `Preload` `:168` / `file_facts` `:143`; `build_d1_v0.diag_index` `:357` /
    `owner_of` `:338`; `build_opstopfromnode_v0.walk` `:129` / `cls_of` `:147`; `hash_probe.probe` (34(k));
    `bench_prep.labview_handles`.
Nothing new is built. Traverse class is resolved BY MEMBERSHIP in the walk, never by `cls_of` (STATUS NEXT).

PREDICTION CONTRACT - every line below is a printed GATE, and **gates are REPORTED, not required** (the
34(j)/37(e) pattern): the READING is the deliverable and the run's rc must not depend on either `Is Broken?`
value or on either `ExecState`. Only the file-safety gates are FATAL. A leg that refuses is a READING, not a
failure. No gate below is expected to retain a FAIL (41(c)).
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859.                                          FATAL
  T2  `claudeDev\D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911.                              FATAL
  T3  each leg's dated scratch is byte-identical to it at creation.                                    FATAL
  G0  on each leg's OWN live walk, `#2048` t4 and t5 are bare (wire 0), named, non-source.          REPORTED
  G1  each leg's source terminal is resolved on that leg's own live walk.                           REPORTED
  G2  `owner_of` reads ('Diagram', 686) for #8486, #250 and #2048 on every scratch.                 REPORTED
  G3  each leg was ATTEMPTED and the op's machine error column recorded VERBATIM.                   REPORTED
  G4  a wire uid was read back from each leg's sink terminal (0 is a legitimate reading).           REPORTED
  G5  `ExecState` recorded BEFORE and immediately AFTER the connection, before any `Is Broken?`.     REPORTED
  G6  an ORDERED `Is Broken?` reading was taken per leg via an IDEMPOTENT re-connect.                REPORTED
  G7  each leg's save attempt is recorded; `allow_broken` stays False, `gui_save` never called.      REPORTED
  G8  no live VI Server reference is left open.                                                      REPORTED
  T14 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are byte-unchanged at the end.                     FATAL

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_typectl_v2.log \
      -- py -u tools/bench/diag_typectl_v2.py
"""
import contextlib
import io
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import diag_index, owner_of                                      # noqa: E402
from build_opstopfromnode_v0 import walk as WALK                                  # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402
import build_opconnectnested_v1 as CN1                                            # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_typectl_v2.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

DIAG_UID = 686
SINK_UID = 2048                       # 'Array Subset'
SINK_TERMS = (4, 5)                   # t4 'index', t5 'length' - both bare, named, type-constrained numerics
LEGS = (("M-matched", 8486, "x+1"),           # numeric  -> the SAME sink terminal
        ("X-mismatched", 250, "IMAQdx Session"))   # refnum -> the SAME sink terminal

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "Pre-decided 40(c)+(d), attempt 2: validate `Wire.Is Broken?` 6371004 on a MATCHED/MISMATCHED "
                 "control pair whose SINK IS GIVEN (#2048 t4), one scratch per leg",
     "withdrawn_rule": "attempt 1's FIXED sink rule ('first bare named input on a numeric-arithmetic node') is "
                       "withdrawn: 'no bare required input' is ENTAILED by ExecState == 1",
     "no_vi_was_run": True, "interprets_nothing": True, "no_new_op": True,
     "no_queue_node_called": True, "queue_node_ban_source": "Pre-decided 40(d)",
     "writer_op": "OpConnectNested_v1 (same-diagram; connect_terminals/connect2 need a TOP-LEVEL end and "
                  "Diagram #686 is not top level)",
     "is_broken_citation": "docs/NAMES.md:902-911 (the plan's :888-897 is WRONG - that range is the "
                           "case-structure property-ID block)",
     "sink_given": {"node_uid": SINK_UID, "terminals": list(SINK_TERMS),
                    "source": "tools/bench/diag_queue_typetest_control.json[diagram_686_terminal_census]"},
     "legs_spec": [{"leg": n, "src_uid": u, "src_term_name": t} for n, u, t in LEGS],
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "legs": [], "handles": {}, "hash_probe": [], "substitution": None}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` - the documented emitter (37(i)); the bold form is invisible to guard_peer.
    line = "  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else "")
    print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def probe(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def census(rec, tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire", "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                    # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    rec.setdefault("censuses", {})[tag] = c
    fact("class census [%s] %r" % (tag, c))
    return c


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                        # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def owner(rec, target, uid):
    try:
        ow = owner_of(target, uid, strict=False)
    except Exception as e:                                                        # noqa: BLE001
        ow = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("owner_of", {})[str(uid)] = ow
    fact("owner_of(#%d) = %r" % (uid, ow))
    return ow


def op_indicators():
    """Re-read `OpConnectNested_v1.vi`'s own indicators AFTER a run. `g.op` caches the VI reference, so these are
    the same values the wrapper printed - captured here as data rather than as console text."""
    rd = {}
    try:
        vi = g.op(CN1.OP)
        for k in ("UID", "Name", "UID 2", "Is Broken?"):
            try:
                rd[k] = vi.GetControlValue(k)
            except Exception as e:                                                # noqa: BLE001
                rd[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:60])
    except Exception as e:                                                        # noqa: BLE001
        rd["_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    return rd


def connect(target, diag, sink_node_i, sink_term_i, src_node_i, src_term_i, tag):
    """One `OpConnectNested_v1` call with stdout captured and re-emitted, plus the op's own indicators."""
    buf = io.StringIO()
    rec = {"tag": tag}
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, diag, sink_node_i, sink_term_i,
                                     diag, src_node_i, src_term_i, V1_LABELS)
        rec.update({"wire_delta": dw, "exec_state_returned_by_wrapper": es, "error_verbatim": err})
    except Exception as e:                                                        # noqa: BLE001
        rec.update({"wire_delta": None, "exec_state_returned_by_wrapper": None,
                    "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    txt = buf.getvalue()
    if txt.strip():
        for ln in txt.rstrip().splitlines():
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    rec["op_stdout"] = txt.strip()
    rec["op_indicators"] = op_indicators()
    fact("%s: wire_delta=%r  op error column VERBATIM %r  op indicators %r"
         % (tag, rec.get("wire_delta"), rec.get("error_verbatim"), rec["op_indicators"]))
    return rec


def sink_wire(target, diag, node_i, term_i):
    try:
        u, rows = g.node_terms_uid(target, diag, node_i)
        r = rows[term_i] if rows and term_i < len(rows) else None
        return {"node_uid_readback": u, "term": (dict(r) if r else None),
                "wire": (r["wire"] if r else None)}
    except Exception as e:                                                        # noqa: BLE001
        return {"error": "%s: %s" % (type(e).__name__, str(e)[:160])}


def run_leg(leg_name, src_uid, src_term_name, sink_term_i, seq):
    """ONE leg on ITS OWN dated scratch copy. Returns the leg record."""
    rec = {"leg": leg_name, "sink_terminal_index": sink_term_i, "seq": seq,
           "source_spec": {"node_uid": src_uid, "term_name": src_term_name},
           "sink_spec": {"node_uid": SINK_UID}}
    target = os.path.join(g.CLAUDEDEV, "DIAG_typectl_v2_%s_%s_t%d.vi" % (STAMP, seq, sink_term_i))
    rec["scratch"] = target
    print("\n=================== LEG %s  (sink #%d t%d)  scratch %s"
          % (leg_name, SINK_UID, sink_term_i, os.path.basename(target)), flush=True)
    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(S2_ARTEFACT, target)
    p = probe("T3 the %s scratch at creation" % leg_name, target)
    rec["scratch_at_creation"] = p
    gate("T3 the %s scratch is byte-identical to the S2 artefact" % leg_name, p.get("md5") == S2_MD5,
         p.get("md5", "?"), fatal=True)

    with D.Preload("P-%s" % leg_name):
        g.open_panel(target)
        time.sleep(1.0)
        census(rec, "before", target)

        # ------------------------------------------------ the LIVE walk (34(h): re-read, never cached)
        diag = diag_index(target, DIAG_UID)
        rec["diagram_index"] = diag
        fact("Diagram #%d reads Traverse index %d on this scratch" % (DIAG_UID, diag))
        w = WALK(target, diag, limit=200)
        rec["walk_n_nodes"] = len(w)
        fact("the walk of Diagram #%d returned %d nodes" % (DIAG_UID, len(w)))
        # class resolved BY MEMBERSHIP in this walk, never by cls_of (STATUS NEXT / cycle 54)
        rec["membership"] = {str(u): (u in w) for u in (src_uid, SINK_UID)}

        # ------------------------------------------------ owners, read live on THIS scratch
        for uid in sorted({src_uid, SINK_UID, 8486, 250}):
            if uid in w:
                owner(rec, target, uid)
            else:
                fact("owner_of(#%d) NOT taken: the node is not in this walk of Diagram #%d" % (uid, DIAG_UID))
        gate("G2 [%s] owner_of reads ('Diagram', %d) for every node in this leg" % (leg_name, DIAG_UID),
             all(tuple(v) == ("Diagram", DIAG_UID) for v in rec.get("owner_of", {}).values()
                 if isinstance(v, (tuple, list))),
             repr(rec.get("owner_of")))

        # ------------------------------------------------ the GIVEN sink, re-verified live
        sink = None
        if SINK_UID in w:
            sni, slab, srows = w[SINK_UID]
            rec["sink_spec"].update({"node_index": sni, "label": slab})
            rec["sink_terms_live"] = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                                       "wire": r["wire"]} for r in srows if r["i"] in SINK_TERMS]
            fact("GIVEN sink #%d %r Nodes[%d]; its t4/t5 read live: %r"
                 % (SINK_UID, slab, sni, rec["sink_terms_live"]))
            row = next((r for r in srows if r["i"] == sink_term_i), None)
            if row is not None:
                sink = {"node_uid": SINK_UID, "node_index": sni, "label": slab, "term_index": row["i"],
                        "term_name": row["name"], "term_wire_before": row["wire"],
                        "is_source": bool(row["is_source"])}
            gate("G0 [%s] #%d t4 and t5 are bare (wire 0), NAMED and non-source on this scratch"
                 % (leg_name, SINK_UID),
                 len(rec["sink_terms_live"]) == 2
                 and all((not t["is_source"]) and (t["name"] or "").strip() and not t["wire"]
                         for t in rec["sink_terms_live"]),
                 repr(rec["sink_terms_live"]))
        else:
            gate("G0 [%s] #%d is on this walk of Diagram #%d" % (leg_name, SINK_UID, DIAG_UID), False,
                 "the GIVEN sink node is not in the walk")
        rec["sink"] = sink

        # ------------------------------------------------ the source, re-resolved live
        src = None
        if src_uid in w:
            ni, lab, rows = w[src_uid]
            for r in rows:
                if r["is_source"] and (r["name"] or "") == src_term_name:
                    src = {"node_uid": src_uid, "node_index": ni, "label": lab, "term_index": r["i"],
                           "term_name": r["name"], "term_wire": r["wire"]}
                    break
        rec["source"] = src
        fact("%s source resolved: %r" % (leg_name, src))
        gate("G1 [%s] the source terminal #%d %r is resolved on this leg's own live walk"
             % (leg_name, src_uid, src_term_name), bool(src), repr(src))

        if not (src and sink):
            fact("%s: an end could not be resolved - the connection is NOT attempted. That is the reading, "
                 "reported as one." % leg_name)
        else:
            # -------------------------------------------- DISCRIMINATOR 1a: ExecState BEFORE (unperturbed)
            rec["exec_state_before"] = read_exec_state(rec, "%s BEFORE the connection" % leg_name, target)

            # -------------------------------------------- pass 1: the write
            print("\n--- %s PASS 1: the write. OpConnectNested_v1, same-diagram (src_diag == sink_diag)."
                  % leg_name, flush=True)
            diag_now = diag_index(target, DIAG_UID)          # 38(e): re-resolve before every call
            rec["diagram_index_reresolved"] = diag_now
            rec["pass1"] = connect(target, diag_now, sink["node_index"], sink["term_index"],
                                   src["node_index"], src["term_index"], "%s pass1 (write)" % leg_name)
            rec["sink_after_write"] = sink_wire(target, diag_now, sink["node_index"], sink["term_index"])
            rec["wire_uid"] = (rec["sink_after_write"] or {}).get("wire")
            fact("%s: sink #%d t%d now carries wire %r (read from node_terms, NOT from the op) - %r"
                 % (leg_name, SINK_UID, sink["term_index"], rec["wire_uid"], rec["sink_after_write"]))

            # -------------------------------------------- DISCRIMINATOR 1b: ExecState immediately AFTER
            rec["exec_state_after"] = read_exec_state(
                rec, "%s IMMEDIATELY AFTER the connection (before any Is Broken? read)" % leg_name, target)

            # -------------------------------------------- DISCRIMINATOR 2: the ORDERED `Is Broken?`
            print("\n--- %s PASS 2: the ORDERED `Is Broken?` reading - an IDEMPOTENT re-connect of the SAME "
                  "pair (docs/NAMES.md:912-918). Expect wire_delta 0. Every ExecState after this is SUSPECT."
                  % leg_name, flush=True)
            diag_now = diag_index(target, DIAG_UID)
            rec["pass2"] = connect(target, diag_now, sink["node_index"], sink["term_index"],
                                   src["node_index"], src["term_index"],
                                   "%s pass2 (idempotent, THE READING)" % leg_name)
            rec["sink_after_pass2"] = sink_wire(target, diag_now, sink["node_index"], sink["term_index"])
            rec["is_broken_pass1_MAYBE_STALE"] = (rec["pass1"].get("op_indicators") or {}).get("Is Broken?")
            rec["is_broken_ordered"] = (rec["pass2"].get("op_indicators") or {}).get("Is Broken?")
            rec["wire_uid_2_ordered"] = (rec["pass2"].get("op_indicators") or {}).get("UID 2")
            rec["exec_state_after_is_broken_SUSPECT"] = read_exec_state(
                rec, "%s after the Is Broken? read (SUSPECT per NAMES.md:917-921)" % leg_name, target)

            fact("%s LEG READING: source #%d t%d %r -> sink #%d t%d %r | wire uid %r | op error column "
                 "pass1 %r / pass2 %r | `Is Broken?` pass1 %r (MAYBE STALE) / ORDERED pass2 %r | wire_delta "
                 "pass1 %r / pass2 %r | ExecState before %r -> after %r"
                 % (leg_name, src["node_uid"], src["term_index"], src["term_name"], SINK_UID,
                    sink["term_index"], sink["term_name"], rec["wire_uid"],
                    rec["pass1"].get("error_verbatim"), rec["pass2"].get("error_verbatim"),
                    rec["is_broken_pass1_MAYBE_STALE"], rec["is_broken_ordered"],
                    rec["pass1"].get("wire_delta"), rec["pass2"].get("wire_delta"),
                    rec["exec_state_before"], rec["exec_state_after"]))

        # ------------------------------------------------ census, save
        census(rec, "after", target)
        es_final = read_exec_state(rec, "%s immediately before the save attempt (SUSPECT)" % leg_name, target)
        size, serr = None, None
        if isinstance(es_final, int) and es_final != 0:
            try:
                size = g.save(target)        # allow_broken stays False; gui_save is NEVER called
            except Exception as e:                                                # noqa: BLE001
                serr = "%s: %s" % (type(e).__name__, str(e)[:250])
        else:
            serr = ("NOT ATTEMPTED: ExecState is %r and the brief permits a save only at ExecState != 0. "
                    "A leg that ends at 0 is an expected and legitimate outcome." % (es_final,))
        rec["save"] = {"returned_bytes": size, "exception_or_reason_verbatim": serr,
                       "allow_broken": False, "gui_save": False, "exec_state_before_save": es_final}
        fact("%s g.save(scratch) returned %r; exception/reason VERBATIM %r (allow_broken False, gui_save "
             "never called)" % (leg_name, size, serr))
        rec["save"]["file_after"] = D.file_facts("%s scratch after the save attempt" % leg_name, target)
        try:
            g.close_panel(target)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    return rec


def main():
    print("=== diag_typectl_v2  %s   (Pre-decided 40(c)+(d) ATTEMPT 2; SINKS GIVEN, no sink rule; NO QUEUE "
          "NODE, 40(d); NO VI IS RUN, 34(f); no new op; INTERPRETS NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (attempt 1 left ~63,400; fresh-instance baseline ~31,500): %r"
         % R["handles"]["before"])
    fact("THE INSTRUMENT UNDER TEST is `Wire.Is Broken?` 6371004, carried by OpConnectNested_v1's own readout "
         "(docs/NAMES.md:902-911 - the plan's :888-897 citation is WRONG and is not used). THE ORDERING TRAP "
         "(NAMES.md:905-911): that readout's `error in (no error)` ships UNWIRED, so on the WRITING pass it may "
         "run BEFORE the Connect Wire and describe the OLD wire; the ORDERED reading is pass2, an IDEMPOTENT "
         "re-connect (NAMES.md:912-918). Any ExecState taken after a pass2 is SUSPECT (NAMES.md:917-921), so "
         "both ExecState readings are taken BEFORE the Is Broken? read on every leg.")

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---------------------------------------------------------------- the restart the brief orders
    D.fresh("T2b RESTART (attempt 1 left ~63,400 handles against a ~31,500 baseline; standing restart "
            "permission, CLAUDE.md 3)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    # ---------------------------------------------------------------- the two legs, at t4
    term = SINK_TERMS[0]
    for name, uid, tname in LEGS:
        R["legs"].append(run_leg(name, uid, tname, term, "A"))
        dump()

    # ---------------------------------------------------------------- the declared t5 substitution rule
    m = R["legs"][0]
    refused = (not m.get("wire_uid")) or bool((m.get("pass1") or {}).get("error_verbatim"))
    R["substitution"] = {"rule": "if the MATCHED leg ends with NO wire on t4 or a non-empty op error column, "
                                "t4 refuses for a reason that is not type; both legs are then re-run at t5",
                         "matched_leg_wire_uid": m.get("wire_uid"),
                         "matched_leg_error_verbatim": (m.get("pass1") or {}).get("error_verbatim"),
                         "triggered": bool(refused), "substituted_terminal": None}
    fact("t5 SUBSTITUTION RULE: matched-leg wire uid %r, matched-leg op error column %r -> triggered=%r"
         % (m.get("wire_uid"), (m.get("pass1") or {}).get("error_verbatim"), bool(refused)))
    if refused:
        term = SINK_TERMS[1]
        R["substitution"]["substituted_terminal"] = term
        fact("SUBSTITUTION APPLIED: #%d t4 refused on the MATCHED leg for a reason unrelated to type (the "
             "types agree there), so BOTH legs are re-run at t%d on two FRESH scratch copies. Every t4 "
             "reading above is kept verbatim." % (SINK_UID, term))
        for name, uid, tname in LEGS:
            R["legs"].append(run_leg(name, uid, tname, term, "B"))
            dump()

    # ---------------------------------------------------------------- the reported gates
    print("\n--- the REPORTED gates over both legs", flush=True)
    attempted = [l for l in R["legs"] if l.get("pass1")]
    gate("G3 each attempted leg's machine error column is recorded VERBATIM",
         bool(attempted) and all("error_verbatim" in l["pass1"] for l in attempted),
         repr([(l["leg"], l["seq"], l["pass1"].get("error_verbatim")) for l in attempted]))
    gate("G4 a wire uid was read back from each attempted leg's sink terminal (0 is a legitimate reading)",
         bool(attempted) and all(l.get("sink_after_write") is not None for l in attempted),
         repr([(l["leg"], l["seq"], l.get("wire_uid")) for l in attempted]))
    gate("G5 ExecState recorded BEFORE and immediately AFTER the connection on each attempted leg",
         bool(attempted) and all(("exec_state_before" in l and "exec_state_after" in l) for l in attempted),
         repr([(l["leg"], l["seq"], l.get("exec_state_before"), l.get("exec_state_after"))
               for l in attempted]))
    gate("G6 an ORDERED `Is Broken?` reading was taken per attempted leg via an IDEMPOTENT re-connect",
         bool(attempted) and all("pass2" in l for l in attempted),
         repr([(l["leg"], l["seq"], l.get("is_broken_ordered"),
                "wire_delta %r" % (l.get("pass2") or {}).get("wire_delta")) for l in attempted]))
    gate("G7 each leg's save attempt is recorded; allow_broken False, gui_save never called",
         all("save" in l for l in R["legs"]),
         repr([(l["leg"], l["seq"], (l.get("save") or {}).get("returned_bytes"),
                (l.get("save") or {}).get("exception_or_reason_verbatim")) for l in R["legs"]]))

    fact("🔴 THE CONTROL PAIR, SIDE BY SIDE, INTERPRETED BY NOBODY HERE: %r"
         % [{"leg": l["leg"], "seq": l["seq"],
             "source": (l.get("source") or {}).get("node_uid"),
             "source_term": (l.get("source") or {}).get("term_name"),
             "sink": (SINK_UID, l.get("sink_terminal_index")),
             "wire": l.get("wire_uid"),
             "op_error": (l.get("pass1") or {}).get("error_verbatim"),
             "ExecState before -> after": (l.get("exec_state_before"), l.get("exec_state_after")),
             "Is Broken? (ordered)": l.get("is_broken_ordered")} for l in R["legs"]])
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at a FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
    finally:
        try:
            dump()
        except Exception:                                                         # noqa: BLE001
            pass
        try:
            g.reset()
        except Exception:                                                         # noqa: BLE001
            pass
        refs = None
        try:
            refs = g.ref_counts()
        except Exception:                                                         # noqa: BLE001
            pass
        R["ref_counts_end"] = refs
        try:
            R["handles"]["after"] = labview_handles()
        except Exception:                                                         # noqa: BLE001
            R["handles"]["after"] = None
        print("\n--- close-out", flush=True)
        fact("refs at end: %r" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r, after the restart %r). Attempt 1 measured ~32,700 added "
             "per 78-second run while ref_counts read 6/6/0 live."
             % (R["handles"].get("after"), R["handles"].get("before"), R["handles"].get("after_restart")))
        gate("G8 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            try:
                dd = probe("T14 %s after the run" % tag, path)
            except Exception as e:                                                # noqa: BLE001
                print("  FAIL  T14 %s could not be re-probed: %s: %s" % (tag, type(e).__name__, e), flush=True)
                fails.append("T14 %s re-probe raised" % tag)
                rc = 1
                continue
            R.setdefault("untouched", {})[tag] = dd.get("md5")
            if not gate("T14 %s md5 unchanged" % tag, dd.get("md5") == pin, dd.get("md5", "?")):
                rc = 1
        try:
            dump()
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  the readings JSON could not be written: %s: %s" % (type(e).__name__, e), flush=True)
            rc = 1
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== GATES ARE REPORTED, NOT REQUIRED - the READING is the deliverable (34(j)/37(e) pattern). "
              "The rc does NOT depend on either `Is Broken?` value or on either `ExecState`; a leg that "
              "refuses is a reading, not a failure.", flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== NOTHING IS INTERPRETED HERE. The branch after this measurement is the judgement session's "
              "(Pre-decided 40). NO QUEUE NODE WAS CREATED (40(d)); NO VI WAS RUN (34(f)); no new op; "
              "no motor, no ASI, no camera, no GUI.", flush=True)
        sys.exit(rc)
