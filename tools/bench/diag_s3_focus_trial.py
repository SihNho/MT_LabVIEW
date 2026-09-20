r"""diag_s3_focus_trial - CYCLE 54: does the 1.5 FOCUS set COMPILE once it is moved into loop a and re-wired?

A DIAGNOSTIC, never a recipe (it lives under `tools/bench/`, not `tools/recipes/`). That placement is the whole
point: `docs/cycle27-plan.md` Pre-decided 38(d) re-cut S3 as a 34(j)-pattern measurement whose READING is the
deliverable and whose saved file is a bonus, so the prior-art LAUNCH gate must not sit on a measurement.
It MEASURES and CHOOSES NOTHING. 🔴 **The branch on the `ExecState` reading is Pre-decided 38(f) and belongs to
the judgement session; this file does not resolve it, does not recommend a next step, and writes no stage.**

`tools/recipes/stage_d1_s3_focus.py` is WITHDRAWN (Pre-decided 38(a)); its STOP RECORD stays armed. Measurement
code is LIFTED from it below (`term_state`, `node_state`, `term_index`, the job tables); it is never launched,
never re-armed and never copied into `tools/recipes/`.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "check what exists first":
`grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`). NOTHING NEW IS
BUILT (Pre-decided 2; user 2026-09-18 08:53):
  * `build_d1_v0.move_in` `:318` / `owner_of` `:338` / `diag_index` `:357` - THE BUILT MOVER and the two
    uid-addressed readers. `move_in` is not in `tools/gscript.py` at all.
  * `build_opstopfromnode_v0.walk` `:129` - the BUILT per-diagram terminal census (`node_labels` +
    `gscript.node_terms_uid` `:925`, four per-property error columns). This is the WIRED-TERMINAL instrument
    37(e) requires; no Wire census is used as a gate anywhere in this file.
  * `build_opconnectnested_v1.connect_nested_v1` `:418` (`OpConnectNested_v1.vi`) - the BUILT writer for
    node -> node inside a nested diagram.
  * `build_opconnectfromwire_v0.connect_from_wire` `:381` + `wire_source_owner` `:423` (`OpConnectFromWire_v0.vi`,
    `docs/toolkit-capabilities.md:70`) - **the only built writer whose SOURCE need not be a node**, which the
    withdrawn recipe never imported. It is what the `from-tunnel` row `#10407` t1 needs.
  * `gscript.add_shift_reg` `:673` / `wire_sr` `:713` / `shift_reg` `:753` - the BUILT shift-register family; the
    verb `docs/d1-build-plan.md:402-403` names. SRs are **CREATED**, never moved.
  * `diag_s2_scaffold` `fresh` `:156` / `Preload` `:168` / `file_facts` `:143` / `read_state` `:344` /
    `try_save` `:352` - cycle 50's measured harness (in-instance ExecState under Preload, 34(l); `g.save()` with
    `allow_broken` False, `gui_save` NEVER called).
  * `diag_destidx_drift.py` (cycle 53, 15/0) is the pattern this file follows, including its gates-are-REPORTED
    discipline and the documented `  FAIL  ` emitter (37(i)).
  * `bench_prep.labview_handles`; `hash_probe.probe` (34(k), read-only md5/sha256/size).
  * `tools/bench/c53_row_class.json` - the MEASURED 17-row table this file's job list is taken from, and
    `tools/bench/d1_rewire_sources.json` - the rows themselves, re-read at run time.

THE SET AND THE DESTINATION (37(h) / 38(d), CITED, never re-derived - `docs/cycle27-plan.md:1126-1131`):
  five movable nodes, ALL on `Diagram #639` (the body of `WhileLoop #637`): `CaseStructure #10407`, `#48`,
  `#3529` (a **ControlReferenceConstant**), `#3560`, `#3447`  ->  body `Diagram #23058` of loop a `#23032`.

🔴 BANNED BY NAME (38(g)): this file NEVER closes 1.5's inputs by tunnelling out of `#637`, wiring on `#686` and
   tunnelling into `#23032`. That construction compiles green and CHANGES THE COMPUTATION (rule 1a) - autofocus
   would run once after acquisition instead of once per frame. A row that would need it is left BARE and reported.
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 No motor, no ASI, no camera, no GUI action. Every edit lands on a DATED SCRATCH copy unique to this run.

PREDICTION CONTRACT - every line is a printed GATE. Only the FILE-IDENTITY gates are FATAL; every gate about the
BUILD is REPORTED, because a required gate here would smuggle in the outcome 38(f) reserves for judgement.
 T1  the ORIGINAL exists, md5 2a78e17c449cacdaf5da389818526859.                                          FATAL
 T2  `claudeDev\D1_s2_loops.vi` md5 6ff19497f2309e007a214660bb64b911 / 475707 B BEFORE the copy.          FATAL
 T3  the dated scratch is byte-identical to it.                                                          FATAL
 T4  baseline census vs the verified S2 numbers (Diagram 173 / WhileLoop 6 / SubVI 97 / Comparison 17 /
     LoopTunnel 135 / Wire 1905).                                                                     REPORTED
 T5  loop identity by OWNERSHIP TRAVERSAL: #23058 -> #23032 -> #686 (37(b): never by array index).     REPORTED
 T6  the five set members' owner and WIRED-TERMINAL count BEFORE any edit.                            REPORTED
 T7a-e per move: the destination index is RE-RESOLVED by uid from a freshly-read traverse list and the
     resolved index is gated to still own #23058 (38(e) - cheap defence; drift was measured ABSENT).   REPORTED
 T8  after the five moves: each member's owner and wired-terminal count.                               REPORTED
 T9  two shift-register pairs CREATED on loop a (`add_shift_reg`) and read back (`shift_reg`).         REPORTED
 T10 each wiring job: the node-side terminal's state afterwards, and the machine's own error text.     REPORTED
 T11 `OpConnectFromWire_v0` on the from-tunnel row `#10407` t1 (wire 9635): accepted or refused.       REPORTED
 T12 the rows left BARE by instruction: `#10407` t0 (case selector), t2, t6.                           REPORTED
 T13 per moved node, WIRED TERMINALS before / after - REPORTED, and NOTHING is required of them:
     38(a) measured the "returns to its pre-move value" criterion UNSOUND (two rows are queue endpoints
     excluded by construction).                                                                        REPORTED
 T14 `ExecState` in-instance with the ORIGINAL preloaded (34(l)).                                      REPORTED
 T15 ONE `g.save()`, `allow_broken` False, `gui_save` NEVER called. A REFUSED save is a legitimate
     outcome, not a failure to work around.                                                            REPORTED
 T16 no live VI Server reference is left open.                                                        non-fatal
 T17 ORIGINAL, `D1_s1_copy.vi` and `D1_s2_loops.vi` md5s unchanged at the end.                           FATAL
`tools/bench/diag_s3_focus_trial.json` is written after EVERY phase and again in `finally`, so it exists on
EITHER branch - that is this run's only hard requirement.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_s3_focus_trial.log \
      -- py -u tools/bench/diag_s3_focus_trial.py
"""
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

# Several recipe modules set `g._run.__defaults__` at IMPORT time (build_opconnectfromwire_v0.py:136 sets
# (6.0, 120.0)). Capture gscript's own value and restore it after the imports so this run uses the timeouts
# cycles 50/52/53 measured, not whichever module happened to be imported last.
_RUN_DEFAULTS = g._run.__defaults__
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index                             # noqa: E402
from build_opstopfromnode_v0 import walk as WALK                                  # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402
from build_opconnectfromwire_v0 import connect_from_wire as CONNECT_FROM_WIRE     # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_SOURCE_OWNER     # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402
g._run.__defaults__ = _RUN_DEFAULTS

BENCH = os.path.join(ROOT, "tools", "bench")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S2_SIZE = 475707
STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_s3focus_%s.vi" % STAMP)     # NEVER named D1_s3_loop15.vi
OUT = os.path.join(BENCH, "diag_s3_focus_trial.json")
REWIRE_JSON = os.path.join(BENCH, "d1_rewire_sources.json")

FRAME_BODY_UID = 639             # WhileLoop #637's body - where the 1.5 set lives today (37(f))
SIBLING_DIAG_UID = 686           # the FlatSequenceFrame diagram that HOLDS WhileLoop #637
LOOP_A_UID = 23032               # 37(h), docs/cycle27-plan.md:1126-1131 - CITED, never re-derived
BODY_A_UID = 23058               # 37(h), same line
WALK_LIMIT = 200

# (uid, name, pre-move wired count on the record, drop position, evidence)
SET = [
    (3529, "- Inc (PgDn)", 1, (40, 60), "ControlReferenceConstant; docs/d1-build-plan.md:330"),
    (3560, "+ Inc (PgUp)", 1, (40, 170), "ControlReferenceConstant; docs/d1-build-plan.md:331"),
    (3447, "Focus Step (F1)", 1, (40, 280), "ControlReferenceConstant; docs/d1-build-plan.md:332"),
    (48, "ASI_adjust focus-subvi.vi", 7, (300, 170), "SubVI; docs/d1-build-plan.md:306"),
    (10407, "Case Structure", 7, (620, 60), "CaseStructure (autofocus); docs/d1-build-plan.md:305"),
]
SET_UIDS = [u for u, _n, _w, _p, _e in SET]

# The five wires INTERNAL to the set (c53_row_class.json rows with action same-loop / source-side).
INTERNAL_JOBS = [
    (48, "-Inc reference", 0, 3529, "- Inc (PgDn)", 0, "w4833; c53_row_class.json table rows :1919 / :2096"),
    (48, "+Inc reference", 1, 3560, "+ Inc (PgUp)", 0, "w2819; d1_rewire_sources.json:1946 / :2126"),
    (48, "Focus inc reference", 2, 3447, "Focus Step (F1)", 0, "w1893; d1_rewire_sources.json:1973 / :2156"),
    (10407, "Outgoing Handle", 3, 48, "Outgoing Handle", 6, "w11232; d1_rewire_sources.json:1820 / :2066"),
    (10407, "Out position", 5, 48, "Out position", 5, "w7388; d1_rewire_sources.json:1865 / :2036"),
]

# The two SR pairs of row 1.5 (docs/d1-build-plan.md:402-403 gives the verb; :359-360 names the registers).
# reg 0 = VISA (old pair #4334/#4344), reg 1 = POSITION (old pair #4256/#4274). The OLD pairs stay on #637:
# 38(d) names no deletion, and `delete_object` on a shift register is unverified here.
SR_SPECS = [
    {"tag": "VISA", "reg_index": 0, "y": 120, "old_pair": [4334, 4344],
     "sides": [("RightIn", 10407, "VISA out", 4, "d1_rewire_sources.json:1847 to-sr"),
               ("LeftIn", 48, "VISA resource name", 3, "d1_rewire_sources.json:2000 from-sr")]},
    {"tag": "POSITION", "reg_index": 1, "y": 220, "old_pair": [4256, 4274],
     # RightIn is DEFERRED BY INSTRUCTION: `#10407` t6 is the unnamed `to-sr` row d1_rewire_sources.json:1892,
     # which 38(b) records as a real and unclosed gap (S6 names no construction verb for it). Left BARE.
     "sides": [("LeftIn", 48, "In position", 4, "d1_rewire_sources.json:2018 from-sr")]},
]

# The from-tunnel row - the ONE row that needs OpConnectFromWire_v0 (docs/toolkit-capabilities.md:70).
TUNNEL_JOB = {"sink_uid": 10407, "sink_name": "# slices in stack", "sink_t": 1, "wire": 9635,
              "tunnel_uid": 9641, "outer_wire": 9649,
              "evidence": "d1_rewire_sources.json:1775-1792, action 'from-tunnel'"}

# Left BARE by instruction (38(d)): the two DEFERRED cross-loop rows and the unnamed to-sr row.
BARE_ROWS = [
    {"uid": 10407, "t": 0, "name": "", "wire": 10799, "json_line": 1748,
     "why": "the CASE SELECTOR, fed by #10686 'x .and. y?' - cross-loop:1.2->1.5, and loop 1.2 does not exist"},
    {"uid": 10407, "t": 2, "name": "Index of closest\ncal image slice, bead 2", "wire": 10990, "json_line": 1793,
     "why": "fed by #10757 'element' - cross-loop:1.2->1.5, far end planned for row 1.2, which does not exist"},
    {"uid": 10407, "t": 6, "name": "position [internal units]", "wire": 9113, "json_line": 1892,
     "why": "a SOURCE labelled to-sr whose far end #12589 t1 stays on row 1.1; 38(b): S6 names no verb for it"},
]

BASELINE = {"Diagram": 173, "WhileLoop": 6, "SubVI": 97, "Comparison": 17, "LoopTunnel": 135, "Wire": 1905}

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "measurement": "cycle 54 / Pre-decided 38(d): move the 1.5 FOCUS set into loop a, wire what can be wired, "
                    "read ExecState. THE BRANCH ON THE READING IS 38(f) AND IS NOT RESOLVED HERE.",
     "no_vi_was_run": True, "chooses_nothing": True, "banned_construction_38g_used": False,
     "loop_identity_cited": "docs/cycle27-plan.md:1126-1131 (Pre-decided 37(h)) - cited, never re-derived",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "scratch": {"path": SCRATCH},
     "node_states": [], "moves": [], "shift_regs": [], "wire_jobs": [], "bare_rows": [],
     "dest_index_resolutions": [], "handles": {}, "hash_probe": [], "censuses": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
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


def dump(phase=None):
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    if phase:
        R.setdefault("phases_done", []).append(phase)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


# ---------------------------------------------------------------- the diagram traverse array, and 38(e)
def diagram_list(target):
    """The WHOLE Diagram traverse array, in the exact order `diag_index` / `move_in` address it."""
    return [int(o["uid"]) for o in g.report_all(target, "Diagram")]


def resolve_dest(tag, target, want_uid=BODY_A_UID):
    """38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before every
    `move_in`, and gate that the resolved index still owns that diagram. Drift was MEASURED ABSENT for `move_in`
    (`tools/bench/diag_destidx_drift.json`, idx 22/22/22), so this is cheap defence, not a fix."""
    lst = diagram_list(target)
    idx = lst.index(want_uid) if want_uid in lst else None
    owns = (idx is not None and lst[idx] == want_uid)
    rec = {"tag": tag, "want_diagram_uid": want_uid, "resolved_index": idx, "traverse_len": len(lst),
           "index_still_owns_it": owns, "diagram_class_count": g.count(target, "Diagram")}
    R["dest_index_resolutions"].append(rec)
    fact("DESTINDEX %s: Diagram #%d resolves to traverse index %s (array length %d, Diagram class count %d)"
         % (tag, want_uid, idx, len(lst), rec["diagram_class_count"]))
    gate("T7 %s: the freshly resolved index %s still owns Diagram #%d (38(e))" % (tag, idx, want_uid),
         owns, "traverse_len %d" % len(lst), fatal=False)
    return idx


# ---------------------------------------------------------------- Pre-decided 14: UNREAD is a third outcome
def term_state(r):
    """WIRED / BARE / UNREAD for ONE `node_terms_uid` row. `tools/gscript.py:874` documents the ONE legitimate
    error pattern: a bare terminal returns wire 0 with conn_err/wire_err 1055 and name_err/src_err 0. Everything
    else beside a value is UNREAD (Pre-decided 14)."""
    ne, se = int(r.get("name_err") or 0), int(r.get("src_err") or 0)
    ce, we = int(r.get("conn_err") or 0), int(r.get("wire_err") or 0)
    w = int(r.get("wire") or 0)
    if w:
        return "UNREAD" if (ne or se or ce or we) else "WIRED"
    if ne or se:
        return "UNREAD"
    if (ce and ce != 1055) or (we and we != 1055):
        return "UNREAD"
    return "BARE"


_EPOCH = [0]
_WALK_CACHE = {}


def bump(why):
    """Every MUTATION invalidates every cached address (34(h)). Nothing is cached across one."""
    _EPOCH[0] += 1
    _WALK_CACHE.clear()
    return why


def walk_of(target, diagram_uid):
    key = (diagram_uid, _EPOCH[0])
    if key not in _WALK_CACHE:
        di = diag_index(target, diagram_uid)
        _WALK_CACHE[key] = (di, WALK(target, di, limit=WALK_LIMIT))
    return _WALK_CACHE[key]


def node_state(tag, target, uid, quiet=False):
    """The live state of ONE node, addressed BY uid and re-resolved at the call site (34(h) / 37(b)):
    owner -> Traverse Diagram index -> that diagram's `walk` -> Nodes[] index -> terminal rows.
    WIRED TERMINALS are counted, never Wire-class counts (37(e): a Wire census cannot see a cut)."""
    rec = {"tag": tag, "uid": uid, "owner_class": None, "owner_uid": None, "diagram_index": None,
           "node_index": None, "label": None, "rows": None, "wired": None, "bare": None, "unread": None,
           "error": None}
    try:
        cls, own = owner_of(target, uid)
        rec["owner_class"], rec["owner_uid"] = cls, own
        di, w = walk_of(target, own)
        rec["diagram_index"] = di
        if uid not in w:
            rec["error"] = ("#%d is NOT in AbstractDiagram.Nodes[] of its owner %s #%s (walk saw %d nodes)"
                            % (uid, cls, own, len(w)))
        else:
            ni, label, rows = w[uid]
            rec["node_index"], rec["label"] = ni, label
            rec["rows"] = [{"i": r["i"], "name": r["name"], "is_source": r["is_source"], "wire": r["wire"],
                            "state": term_state(r), "name_err": r["name_err"], "src_err": r["src_err"],
                            "conn_err": r["conn_err"], "wire_err": r["wire_err"]} for r in rows]
            rec["wired"] = sum(1 for r in rec["rows"] if r["state"] == "WIRED")
            rec["bare"] = sum(1 for r in rec["rows"] if r["state"] == "BARE")
            rec["unread"] = sum(1 for r in rec["rows"] if r["state"] == "UNREAD")
    except Exception as e:                                                        # noqa: BLE001
        rec["error"] = "%s: %s" % (type(e).__name__, e)
    R["node_states"].append(rec)
    if rec["rows"] is None:
        fact("NODE %s #%d: NOT READ - %s" % (tag, uid, rec["error"]))
    elif not quiet:
        fact("NODE %s #%d (owner %s #%s, Diagram index %s, Nodes[%s], label %r): %d terminals - "
             "%d WIRED / %d BARE / %d UNREAD"
             % (tag, uid, rec["owner_class"], rec["owner_uid"], rec["diagram_index"], rec["node_index"],
                rec["label"], len(rec["rows"]), rec["wired"], rec["bare"], rec["unread"]))
        for r in rec["rows"]:
            print(("        t%-2d %-32s src=%-5s wire=%-6s %-6s errs(n/s/c/w)=%d/%d/%d/%d"
                   % (r["i"], repr(r["name"] or "")[:32], r["is_source"], r["wire"], r["state"],
                      r["name_err"], r["src_err"], r["conn_err"], r["wire_err"]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
    return rec


def term_index(rec, name, want_i, is_source=None):
    """The LIVE terminal index for a (name, recorded index) pair. The NAME is the address; `want_i` is only the
    fallback, and only when the name is absent or not unique (34(h): names are stable, indices drift)."""
    rows = rec.get("rows") or []
    m = [r["i"] for r in rows if r["name"] == name and (is_source is None or r["is_source"] == is_source)]
    if len(m) == 1:
        return m[0], "by name %r" % name
    if any(r["i"] == want_i for r in rows):
        return want_i, "by recorded index %d (name %r matched %d rows)" % (want_i, name, len(m))
    return None, "UNRESOLVED (name %r matched %d rows; index %d absent)" % (name, len(m), want_i)


def census(tag, target):
    c = {k: g.count(target, k) for k in BASELINE}
    R["censuses"][tag] = c
    fact("class census %s: %r" % (tag, c))
    return c


# ============================================================================== PHASES
def phase_0_files():
    print("\n=== PHASE 0: files only, zero LabVIEW", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])
    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL exists and its md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"))
    s = probe("T2 the S2 artefact BEFORE the copy", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s and size == %d B" % (S2_MD5, S2_SIZE),
         s.get("md5") == S2_MD5 and s.get("size") == str(S2_SIZE),
         "md5 %s size %s" % (s.get("md5"), s.get("size")))
    probe("T2b D1_s1_copy.vi BEFORE", S1_ARTEFACT)
    D.fresh("T2c")
    fact("handles after the restart: %r" % labview_handles())
    shutil.copy2(S2_ARTEFACT, SCRATCH)
    t = probe("T3 the dated scratch", SCRATCH)
    gate("T3 the scratch is byte-identical to the S2 artefact", t.get("md5") == S2_MD5, t.get("md5", "?"))
    dump("0-files")


def phase_1_baseline():
    print("\n=== PHASE 1: baseline census, loop identity, and the five set members BEFORE any edit", flush=True)
    c0 = census("BEFORE any edit", SCRATCH)
    R["census_before"] = c0
    gate("T4 baseline census == the verified S2 numbers %r (REPORTED)" % BASELINE,
         all(c0[k] == v for k, v in BASELINE.items()), repr(c0), fatal=False)

    cls_body, own_body = owner_of(SCRATCH, BODY_A_UID)
    cls_loop, own_loop = owner_of(SCRATCH, LOOP_A_UID)
    R["loop_a"] = {"loop_uid": LOOP_A_UID, "body_uid": BODY_A_UID, "body_owner_class": cls_body,
                   "body_owner": own_body, "loop_owner_class": cls_loop, "loop_owner": own_loop}
    fact("loop a (37(h), CITED): Diagram #%d's owner reads %s #%s; WhileLoop #%d's owner reads %s #%s"
         % (BODY_A_UID, cls_body, own_body, LOOP_A_UID, cls_loop, own_loop))
    gate("T5 Diagram #%d -> WhileLoop #%d -> Diagram #%d by ownership traversal (REPORTED)"
         % (BODY_A_UID, LOOP_A_UID, SIBLING_DIAG_UID),
         own_body == LOOP_A_UID and own_loop == SIBLING_DIAG_UID,
         "body owner %s #%s; loop owner %s #%s" % (cls_body, own_body, cls_loop, own_loop), fatal=False)

    before = {}
    for uid, name, wired_on_record, _pos, why in SET:
        st = node_state("BEFORE", SCRATCH, uid)
        before[uid] = st
        fact("set member #%d %r - %s" % (uid, name, why))
        gate("T6 #%d BEFORE: owner Diagram #%s, %s WIRED terminals (on the record: %d) - REPORTED"
             % (uid, st["owner_uid"], st["wired"], wired_on_record), True,
             "bare %r unread %r" % (st["bare"], st["unread"]), fatal=False)
    R["before_states"] = {str(u): {k: before[u][k] for k in
                                   ("owner_uid", "node_index", "wired", "bare", "unread", "error")}
                          for u in before}
    dump("1-baseline")
    return before


def phase_2_move():
    print("\n=== PHASE 2: five `move_in` calls, ONE NODE PER CALL, destination RE-RESOLVED before each (38(e))",
          flush=True)
    fact("37(d): `move_in` takes ONE uid per call and SEVERS every wire on the moved node in EITHER order; the "
         "echoed uid is NOT the moved object (both cycle-52 calls echoed 23035).")
    for uid, name, _w, pos, _why in SET:
        bi = resolve_dest("before move #%d" % uid, SCRATCH)
        rec = {"uid": uid, "name": name, "dest_diagram_uid": BODY_A_UID, "dest_index_used": bi,
               "position": list(pos)}
        try:
            rec["echoed_uid"] = move_in(SCRATCH, uid, bi, pos)
            fact("MOVE #%d %r -> Diagram #%d [traverse index %s] at %r; the op echoed uid %r"
                 % (uid, name, BODY_A_UID, bi, pos, rec["echoed_uid"]))
        except Exception as e:                                                    # noqa: BLE001
            rec["error"] = "%s: %s" % (type(e).__name__, e)
            fact("MOVE #%d RAISED %s: %s" % (uid, type(e).__name__, e))
        bump("move #%d" % uid)
        st = node_state("AFTER move #%d" % uid, SCRATCH, uid, quiet=True)
        rec["after"] = {k: st[k] for k in ("owner_uid", "node_index", "wired", "bare", "unread", "error")}
        R["moves"].append(rec)
        gate("T7 move #%d: owner now Diagram #%s, wired %s (REPORTED - 37(d) predicts the wires are severed)"
             % (uid, st["owner_uid"], st["wired"]), True,
             "echoed %r error %r" % (rec.get("echoed_uid"), rec.get("error")), fatal=False)
        dump("2-move-%d" % uid)

    still = []
    for u in SET_UIDS:
        try:
            still.append((u, owner_of(SCRATCH, u)[1]))
        except Exception as e:                                                    # noqa: BLE001
            still.append((u, "ERR %s" % str(e)[:60]))
    R["owners_after_moves"] = still
    gate("T8 owners after the five moves: %r (REPORTED)" % (still,), True, "", fatal=False)
    R["census_after_moves"] = census("AFTER the five moves", SCRATCH)
    dump("2-move")


def phase_3_shift_regs():
    print("\n=== PHASE 3: the two shift-register pairs, CREATED on loop a (not moved)", flush=True)
    fact("docs/d1-build-plan.md:402-403 names `add_shift_reg` + `wire_sr`. The OLD pairs on #637 (#4334/#4344, "
         "#4256/#4274) are NOT deleted: 38(d) names no deletion and `delete_object` on an SR is unverified here.")
    for spec in SR_SPECS:
        li = [o["uid"] for o in g.report_all(SCRATCH, "WhileLoop")].index(LOOP_A_UID)   # re-read (34(h))
        rec = {"tag": spec["tag"], "reg_index": spec["reg_index"], "loop_index": li,
               "old_pair_left_on_637": spec["old_pair"]}
        try:
            rec["new_right_uid"] = g.add_shift_reg(SCRATCH, li, y_position=spec["y"])
            bump("add_shift_reg %s" % spec["tag"])
            fact("SR %s: add_shift_reg(loop index %d, y=%d) -> new RightShiftRegister #%s"
                 % (spec["tag"], li, spec["y"], rec["new_right_uid"]))
        except Exception as e:                                                    # noqa: BLE001
            rec["error"] = "%s: %s" % (type(e).__name__, e)
            fact("SR %s: add_shift_reg RAISED %s: %s" % (spec["tag"], type(e).__name__, e))
        try:
            rec["readback"] = g.shift_reg(SCRATCH, li, spec["reg_index"])
            fact("SR %s: shift_reg(loop %d, reg %d) reads uid %r class %r errors %r"
                 % (spec["tag"], li, spec["reg_index"], rec["readback"].get("uid"),
                    rec["readback"].get("class"), rec["readback"].get("errors")))
        except Exception as e:                                                    # noqa: BLE001
            rec["readback_error"] = "%s: %s" % (type(e).__name__, e)
            fact("SR %s: shift_reg readback RAISED %s: %s" % (spec["tag"], type(e).__name__, e))
        R["shift_regs"].append(rec)
        gate("T9 SR %s created on loop a and read back (REPORTED)" % spec["tag"], True,
             "created %r; readback uid %r; errors %r / %r"
             % (rec.get("new_right_uid"), (rec.get("readback") or {}).get("uid"), rec.get("error"),
                rec.get("readback_error")), fatal=False)
        dump("3-sr-%s" % spec["tag"])


# ------------------------------------------------------------------------------ the three writers
def _job_node(job):
    """node -> node inside one nested diagram, with `OpConnectNested_v1`."""
    sink = node_state("job %s sink" % job["tag"], SCRATCH, job["sink_uid"], quiet=True)
    si, why_s = term_index(sink, job["sink_name"], job["sink_t"], is_source=False)
    src = node_state("job %s src" % job["tag"], SCRATCH, job["src_uid"], quiet=True)
    ri, why_r = term_index(src, job["src_name"], job["src_t"], is_source=True)
    job["addr"] = {"sink_diag": sink["diagram_index"], "sink_node": sink["node_index"], "sink_term": si,
                   "sink_resolved": why_s, "src_diag": src["diagram_index"], "src_node": src["node_index"],
                   "src_term": ri, "src_resolved": why_r}
    if si is None or ri is None or sink["node_index"] is None or src["node_index"] is None:
        job["result"] = "NOT ADDRESSABLE"
        return
    try:
        dw, es, err = CONNECT_V1(SCRATCH, sink["diagram_index"], sink["node_index"], si,
                                 src["diagram_index"], src["node_index"], ri, V1_LABELS)
        job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200]}
    except Exception as e:                                                        # noqa: BLE001
        job["connect"] = {"exception": "%s: %s" % (type(e).__name__, e)}
    bump(job["tag"])
    after = node_state("job %s sink AFTER" % job["tag"], SCRATCH, job["sink_uid"], quiet=True)
    row = next((r for r in (after["rows"] or []) if r["i"] == si), None)
    job["sink_after"] = row
    src_after = node_state("job %s src AFTER" % job["tag"], SCRATCH, job["src_uid"], quiet=True)
    srow = next((r for r in (src_after["rows"] or []) if r["i"] == ri), None)
    job["src_after"] = srow
    job["result"] = ("sink t%s %s wire %s | source t%s %s wire %s | same wire uid: %s"
                     % (si, (row or {}).get("state"), (row or {}).get("wire"), ri,
                        (srow or {}).get("state"), (srow or {}).get("wire"),
                        bool(row and srow and row["wire"] and row["wire"] == srow["wire"])))


def _job_sr(job):
    """ONE side of a shift register, with `gscript.wire_sr`. `gscript.py:717-722`: RightIn takes the node's
    terminal as the SOURCE into the right register; LeftIn feeds the left register's inside terminal INTO the
    node's terminal."""
    node_is_source = (job["variant"] == "RightIn")
    st = node_state("job %s node" % job["tag"], SCRATCH, job["node_uid"], quiet=True)
    ti, why = term_index(st, job["term_name"], job["term_t"], is_source=node_is_source)
    li = [o["uid"] for o in g.report_all(SCRATCH, "WhileLoop")].index(LOOP_A_UID)      # re-read (34(h))
    job["addr"] = {"loop_index": li, "reg_index": job["reg_index"], "node_index": st["node_index"],
                   "term_index": ti, "resolved": why, "node_is_source": node_is_source}
    if ti is None or st["node_index"] is None:
        job["result"] = "NOT ADDRESSABLE"
        return
    try:
        g.wire_sr(job["variant"], SCRATCH, li, job["reg_index"],
                  node_index=st["node_index"], term_index=ti)
        job["connect"] = {"variant": job["variant"], "machine_error": ""}
    except Exception as e:                                                        # noqa: BLE001
        job["connect"] = {"variant": job["variant"], "exception": "%s: %s" % (type(e).__name__, e)}
    bump(job["tag"])
    after = node_state("job %s node AFTER" % job["tag"], SCRATCH, job["node_uid"], quiet=True)
    row = next((r for r in (after["rows"] or []) if r["i"] == ti), None)
    job["node_after"] = row
    try:
        job["sr_readback"] = g.shift_reg(SCRATCH, li, job["reg_index"])
    except Exception as e:                                                        # noqa: BLE001
        job["sr_readback_error"] = "%s: %s" % (type(e).__name__, e)
    job["result"] = ("node t%s %s wire %s" % (ti, (row or {}).get("state"), (row or {}).get("wire")))


def _job_tunnel(job):
    """The from-tunnel row, with `OpConnectFromWire_v0` - the ONLY built writer whose SOURCE need not be a node
    (`docs/toolkit-capabilities.md:70`). The wire OBJECT survives the cut (37(e)), so its SOURCE terminal is still
    the tunnel's inside terminal; the source terminal index is MEASURED with `OpWireSource_v5`, never assumed."""
    wire_uid = job["wire"]
    wires = None
    try:
        wires = [int(o["uid"]) for o in g.report_all(SCRATCH, "Wire")]
        job["wire_still_in_wire_list"] = wire_uid in wires
    except Exception as e:                                                        # noqa: BLE001
        job["wire_list_error"] = "%s: %s" % (type(e).__name__, e)
    try:
        terms = WIRE_SOURCE_OWNER(SCRATCH, wire_uid)
        job["wire_terms"] = terms
        srcs = [t for t in terms if t.get("is_source")]
        fact("TUNNEL ROW: wire %d reads %d terminal rows, %d with Is Source? TRUE: %r"
             % (wire_uid, len(terms), len(srcs), srcs))
    except Exception as e:                                                        # noqa: BLE001
        job["wire_source_error"] = "%s: %s" % (type(e).__name__, e)
        srcs = []
        fact("TUNNEL ROW: wire_source_owner(%d) RAISED %s: %s" % (wire_uid, type(e).__name__, e))
    if len(srcs) != 1:
        job["result"] = "SOURCE NOT UNIQUE (%d source terminals on wire %d)" % (len(srcs), wire_uid)
        return
    st = node_state("job %s sink" % job["tag"], SCRATCH, job["sink_uid"], quiet=True)
    ti, why = term_index(st, job["sink_name"], job["sink_t"], is_source=False)
    job["addr"] = {"sink_diag": st["diagram_index"], "sink_node": st["node_index"], "sink_term": ti,
                   "resolved": why, "wire_uid": wire_uid, "wire_term_index": srcs[0]["i"],
                   "wire_source_owner": "%s #%s" % (srcs[0].get("owner_class"), srcs[0].get("owner_uid"))}
    if ti is None or st["node_index"] is None:
        job["result"] = "SINK NOT ADDRESSABLE"
        return
    try:
        dw, es, err, sub = CONNECT_FROM_WIRE(SCRATCH, wire_uid, srcs[0]["i"], st["diagram_index"],
                                             st["node_index"], ti, CFW_LABELS)
        job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200],
                          "op_sub_outputs": {k: str(v)[:80] for k, v in (sub or {}).items()}}
    except Exception as e:                                                        # noqa: BLE001
        job["connect"] = {"exception": "%s: %s" % (type(e).__name__, e)}
    bump(job["tag"])
    after = node_state("job %s sink AFTER" % job["tag"], SCRATCH, job["sink_uid"], quiet=True)
    row = next((r for r in (after["rows"] or []) if r["i"] == ti), None)
    job["sink_after"] = row
    job["result"] = ("sink t%s %s wire %s; Is Broken? %r"
                     % (ti, (row or {}).get("state"), (row or {}).get("wire"),
                        (job.get("connect", {}).get("op_sub_outputs") or {}).get("Is Broken?")))


def phase_4_wire():
    print("\n=== PHASE 4: wire every row whose source exists NOW. Gates REPORTED, never required.", flush=True)
    jobs = []
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, ev in INTERNAL_JOBS:
        jobs.append({"tag": "int-%d.t%d" % (sink_uid, sink_t), "kind": "node", "writer": "OpConnectNested_v1",
                     "sink_uid": sink_uid, "sink_name": sink_name, "sink_t": sink_t, "src_uid": src_uid,
                     "src_name": src_name, "src_t": src_t, "evidence": ev})
    for spec in SR_SPECS:
        for variant, node_uid, term_name, term_t, ev in spec["sides"]:
            jobs.append({"tag": "sr-%s-%s" % (spec["tag"], variant), "kind": "sr", "writer": "gscript.wire_sr",
                         "variant": variant, "reg_index": spec["reg_index"], "node_uid": node_uid,
                         "term_name": term_name, "term_t": term_t, "evidence": ev})
    tj = dict(TUNNEL_JOB)
    tj.update({"tag": "tunnel-10407.t1", "kind": "tunnel", "writer": "OpConnectFromWire_v0"})
    jobs.append(tj)
    fact("%d wiring jobs: %d internal node->node, %d shift-register sides, 1 from-tunnel. %d rows are left BARE "
         "by instruction (38(d))." % (len(jobs), len(INTERNAL_JOBS),
                                      sum(len(s["sides"]) for s in SR_SPECS), len(BARE_ROWS)))
    for job in jobs:
        print("\n--- job %s (%s)" % (job["tag"], job["writer"]), flush=True)
        try:
            if job["kind"] == "node":
                _job_node(job)
            elif job["kind"] == "sr":
                _job_sr(job)
            else:
                _job_tunnel(job)
        except Exception as e:                                                    # noqa: BLE001
            job["result"] = "RAISED %s: %s" % (type(e).__name__, e)
        R["wire_jobs"].append(job)
        fact("JOB %s [%s]: %s   | connect %r   | %s"
             % (job["tag"], job["writer"], job.get("result"), job.get("connect"), job["evidence"]))
        gate("T10 job %s: %s (REPORTED)" % (job["tag"], job.get("result")), True, "", fatal=False)
        dump("4-job-%s" % job["tag"])
    tun = next((j for j in R["wire_jobs"] if j["kind"] == "tunnel"), {})
    gate("T11 OpConnectFromWire_v0 on the from-tunnel row #10407 t1: %s (REPORTED)" % tun.get("result"),
         True, "connect %r" % (tun.get("connect"),), fatal=False)

    for b in BARE_ROWS:
        st = node_state("BARE-check #%d" % b["uid"], SCRATCH, b["uid"], quiet=True)
        row = next((r for r in (st["rows"] or []) if r["i"] == b["t"]), None)
        rec = dict(b)
        rec["state_now"] = (row or {}).get("state")
        rec["wire_now"] = (row or {}).get("wire")
        R["bare_rows"].append(rec)
        fact("BARE row #%d t%d (%s): state %r wire %r - LEFT BARE BY INSTRUCTION. %s"
             % (b["uid"], b["t"], b["json_line"], rec["state_now"], rec["wire_now"], b["why"]))
        gate("T12 row #%d t%d is %s (REPORTED; 38(g)'s banned construction was NOT used to close it)"
             % (b["uid"], b["t"], rec["state_now"]), True, "", fatal=False)
    R["census_after_wiring"] = census("AFTER the wiring", SCRATCH)
    dump("4-wire")


def phase_5_readings(before):
    print("\n=== PHASE 5: wired terminals before/after, ExecState, and ONE save attempt", flush=True)
    table = []
    for uid, name, _w, _p, _e in SET:
        st = node_state("FINAL", SCRATCH, uid)
        b = before.get(uid) or {}
        table.append({"uid": uid, "name": name, "wired_before": b.get("wired"), "wired_after": st["wired"],
                      "bare_after": st["bare"], "unread_after": st["unread"],
                      "owner_before": b.get("owner_uid"), "owner_after": st["owner_uid"]})
        fact("WIRED TERMINALS #%d %r: before %r -> after %r (bare %r, unread %r); owner %r -> %r"
             % (uid, name, b.get("wired"), st["wired"], st["bare"], st["unread"],
                b.get("owner_uid"), st["owner_uid"]))
    R["wired_terminal_table"] = table
    gate("T13 per-node WIRED TERMINALS before/after are REPORTED and NOTHING is required of them - 38(a) "
         "measured that criterion unsound (two rows are queue endpoints excluded by construction)", True,
         repr([(t["uid"], t["wired_before"], t["wired_after"]) for t in table]), fatal=False)
    dump("5-terminals")

    es = D.read_state("T14_after_move_and_wire_in_instance_preloaded", SCRATCH)
    R["exec_state"] = es
    gate("T14 ExecState after the moves and the wiring = %r (1 = runnable, 0 = broken) - REPORTED; the BRANCH "
         "on this reading is Pre-decided 38(f) and is NOT resolved here" % es, True, "", fatal=False)
    dump("5-execstate")

    sv = D.try_save("s3focus", SCRATCH)
    R["save"] = sv
    R["save_reachable"] = sv["exception"] is None and bool(sv["returned_bytes"])
    gate("T15 g.save() reachable with allow_broken=False (gui_save NEVER called): %s - REPORTED; a REFUSED save "
         "is a legitimate outcome" % R["save_reachable"], True,
         "returned %r exception %r" % (sv["returned_bytes"], sv["exception"]), fatal=False)
    dump("5-save")


def main():
    print("=== diag_s3_focus_trial  %s   (DIAGNOSTIC, Pre-decided 38(d); NO VI IS RUN, 34(f); no new op)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    phase_0_files()
    with D.Preload("T"):
        g.open_panel(SCRATCH)                    # required before ANY scripting edit (skill rule)
        time.sleep(1.0)
        before = phase_1_baseline()
        phase_2_move()
        phase_3_shift_regs()
        phase_4_wire()
        phase_5_readings(before)
        try:
            g.close_panel(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    probe("T15b the scratch on disk, final", SCRATCH)
    dump("6-done")


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at the first FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
    finally:
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
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"].get("after"), R["handles"].get("before")))
        gate("T16 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            try:
                d = probe("T17 %s after the run" % tag, path)
            except Exception as e:                                                # noqa: BLE001
                d = {}
                fact("T17 %s probe RAISED %s: %s" % (tag, type(e).__name__, e))
            R.setdefault("untouched", {})[tag] = d.get("md5")
            ok = d.get("md5") == pin
            gate("T17 %s md5 unchanged" % tag, ok,
                 d.get("md5", "?") if ok else "%s != %s" % (d.get("md5"), pin), fatal=False)
            if not ok:
                rc = 1
        try:
            R["scratch"]["final"] = HASH(SCRATCH)
        except Exception:                                                         # noqa: BLE001
            pass
        dump("7-closeout")
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== ExecState reading: %r ; save reachable: %r" % (R.get("exec_state"), R.get("save_reachable")),
              flush=True)
        print("=== THE BRANCH ON THIS READING IS Pre-decided 38(f) AND IS NOT RESOLVED HERE.", flush=True)
        print("=== NO VI WAS RUN (34(f)); no new op; no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
