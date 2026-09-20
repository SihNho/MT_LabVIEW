r"""build_s0_closeref_v3.py - D1 stage S0, RUN 2 (the LAST S0 attempt of cycle 43).

CUT FROM `build_s0_closeref_v2.py`'s BYTES, with the three cycle-43 JUDGEMENT DECISIONS of 2026-09-19 applied.
v2 was never launched: the census `tools/bench/s0_body_census.log` (7/7, rc=0) and the failed-prediction review
`archive/peer/2026-09-19-s0run1-closeorder.md` (ANSWERED, claude/hypothesis opus max, REFUTED) together showed
that v1/v2's stage-3 design rested on a measured-false premise. What the judgement session decided, verbatim in
substance, and what each decision changed here:

  D1. **The per-iteration `Owner` reference minted by Property node #114 IS in S0's scope.** CLAUDE.md's
      reference-hygiene rule covers every reference the op CREATES, so that one gets its own `Close Reference`.
      This is not scope growth. => `OpReportAll_v1` now carries **TWO** `Close Reference` nodes in the loop body:
      one for the traversed element, one for the `Owner` reference.
  D2. **Both closes use the same pattern**: the refnum input is a BRANCH of the wire that ALREADY CARRIES that
      refnum - the `Owner` output wire (w548 on these bytes) for #114's minted reference, the auto-indexed
      `References` element wire (w421) for the traversed one. Provenance, never lowest-uid (the review's §1(c)
      hazard: every Property node has a `reference out` terminal, so v2's `next(... ref_out is not None)` picked
      by numbering and was right only by accident). Execution ORDER comes from the ERROR CHAIN - the close's
      `error in` is fed from the `error out` of the LAST consumer (#115) - so nothing is ordered by an artificial
      data dependency, and **nothing is hand-wired into the bare scalar refnum input** (the `archive/WORKLOG.md:
      84-86` hazard: "`Close Reference` DEFEATED FOUR WIRING ATTEMPTS").
      One branch wire each. The second close takes its `error in` from the FIRST close's `error out`, so both are
      downstream of #115; that is the error chain, written down here because it is an interpretation of D2 and a
      reviewer must be able to attack it rather than guess it.
  D3. **Before the no-loop stages, RUN the review's §2 discriminating arm on a SCRATCH copy** (`ARM` below): does
      the `References` branch into a fresh For Loop land as a VALID wire - sink read back per Pre-decided 18
      SEGMENTED semantics and `Is Broken?` FALSE - or as the BAD wire `tools/gscript.py:1293-1295` records for a
      branch into a Property node's `reference` ("uid 467, ExecState 0, remove_bad_wires does not clear it")?
      Run 1 printed `ExecState=0` at that point and its VI no longer exists, so the question is open on measurement,
      not on argument. The arm SAVES NO OP: it works on `SCRATCH_s0arm_*.vi`, which is deleted at the end.

WHY A NEW FILE NAME (stated plainly so it is not mistaken for laundering, same reason v2 was cut from v1):
`tools/stop_record.py:313-331` refuses any launch of a PATH whose release was stamped for other bytes, and v2's
record was stamped at sha `c3c78f2801dc` on 2026-09-19T09:22:44Z. Editing v2 in place therefore cannot be
launched at all, while `tools/hooks/guard_cycle.py:485-496` has the "REVIEW -> FIX -> RUN" exemption that expressly
ALLOWS the edited file - the two gates disagree, and the project's own precedent is one file per run
(`build_d1_routeb_v0` ... `_v7`, and `build_s0_closeref_v0` -> `_v1` -> `_v2`, a stop record each). v3 carries its
OWN stop record, armed with the SAME seven prior-art slugs and released by the SAME disposition lines in
`archive/peer/2026-09-19-priorart-s0-closeref.md`. No finding is re-opened and none is bypassed. The gate
asymmetry stays an OPEN item for judgement, not a repair (the user's 2026-09-18 08:53 "no more devices" order).

  py tools/bgrun.py --material --max-min 40 --log tools/bench/build_s0_closeref_v3.log -- py -u tools/recipes/build_s0_closeref_v3.py

TARGETS - NEW FILES under `claudeDev`; the old ops and every original are untouched (rule 1):
  OpReport_v3.vi     -> OpReport_v4.vi       (the op behind gscript.count / gscript.report)
  OpWireSource_v5.vi -> OpWireSource_v6.vi   (the UID-addressed wire-source reader)
  OpReportAll_v0.vi  -> OpReportAll_v1.vi    (the op behind gscript.report_all)

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "check what already exists"):
  * `docs/toolkit-capabilities.md:438-443` - THE BUILT AND MEASURED ROUTE FOR CONSUMING THE `References` ARRAY:
    a For Loop auto-indexing it into a node in its body ("LoopTunnel 0->1, ExecState 0->1 <- the array supplies N").
    `OpReportAll_v0.vi` already HAS that shape; the two no-loop ops get one built the same way.
  * `tools/recipes/build_opconnectfromwire_v0.py:381 connect_from_wire()` - the BUILT writer that BRANCHES an
    existing wire into `Diagram[d].Nodes[n].Terminals[t]`, with its own ORDERED `Wire.Is Broken?` readback
    (`docs/NAMES.md:902-911`); `:423 wire_source_owner()` names the wire's single SOURCE terminal and its owner.
  * `tools/recipes/build_opconnectnested_v1.py:418 connect_nested_v1()` - the BUILT writer for a wire between two
    UNWIRED terminals on ANY diagram, the loop body included. Used ONLY for the two error-chain wires, where there
    is no existing wire to branch (#115's `error out` ships unwired - `tools/bench/s0_body_census.log:52`).
  * `tools/recipes/build_d1_v0.py:318 move_in()` - the BUILT reparent-by-UID; `gscript.for_loop` / `find_at` /
    `tunnels` / `set_index_mode` / `set_auto_error_handling` / `copy_by_index` are all built.
    NO NEW OP IS BUILT HERE (`docs/cycle27-plan.md` Pre-decided 2; user, 2026-09-18 08:53).
  * `tools/bench/s0_body_census.log` - the MEASURED body of `OpReportAll_v0`: `#114 'Owner'` (source, w548) drives
    `#115 'reference'` (`:47`,`:49`,`:60`); w421's source is LoopTunnel **#511**, the `References` tunnel,
    IndexMode 1 (`:58`,`:68`). This recipe RE-MEASURES all of it on the copy and gates it - no uid is hard-coded.
  * `tools/bench/s0_terminal_names.log` (6/6) - the EXACT terminal bytes: Traverse source `References` (index 2);
    `Close Reference` sinks `error in (no error)` and `reference`.

THE SEVEN DISPOSED PRIOR-ART FINDINGS are unchanged from v1/v2 and are NOT re-opened
(`archive/peer/2026-09-19-priorart-s0-closeref.md` "What was done with it"): A3(i) Pre-decided 21(b) withdrawn, so
**this recipe does not predict that it closes `error 2`** - it is a rule-compliance repair, and `error 2` in the
20-call test is THE FINDING, reported, not worked around; A3(ii) `References` is the measured terminal name;
A2/B2 the four archived failures were at the SCALAR refnum input, which no wire here ever targets; B3 the For-Loop
route is adopted, and boundary crossings are gated SEGMENTED-style, never by uid equality; B4 the blind +-100
kernel-handle criterion is replaced by G-A/G-B/G-C; A4 the three documents are cited here and in
`docs/REFERENCES.md` 4a; B1 S1/S2 lift `build_d1_routeb_v7.py`'s bodies and are OUT OF SCOPE - this recipe stops
at S0 and starts no S1.

WHAT IS AND IS NOT CLOSED:
  * CLOSED: every element of the `References` array the op's own `Traverse for GObjects.vi` returns, and (D1) the
    `Owner` reference `OpReportAll_v0`'s first body Property node mints on every iteration.
  * NOT CLOSED: the VI refnum from `Open VI Reference` (1 per call). Closing it can let the target VI LEAVE MEMORY
    and this project has already lost a chain build that way (`tools/gscript.py:1293-1295`); chained ops want the
    target in memory (`archive/WORKLOG.md:84-86`). Unchanged, and confirmed by the cycle-43 judgement.
  * MEASURED, NOT REPAIRED: `refmint_census()` prints every Property node's SOURCE terminals in each repaired op
    and flags the names that are known to RETURN A REFERENCE. Whether S0's scope covers those too is a judgement
    call (D1 named #114 only), so this run reports them and changes nothing. The no-loop ops' own chains are read
    here for the first time.
  * REPORTED, NOT DECIDED: the review's point that `#115` is the node documented to raise **error 1055** on the
    top-level diagram's `Owner` (`fix_opreportall_errors.py:1-15`), so the error chain D2 mandates carries a known
    error into `Close Reference.error in`, and no vendor statement was found for whether `Close Reference` still
    closes on an incoming error. Auto error handling is OFF on this op, so nothing opens a dialog either way.

PREDICTION CONTRACT - every line below is a gate, printed PASS/FAIL; the first fatal FAIL stops that stage only.
  ARM  on a scratch copy of OpReport_v3: the `References` branch into a fresh For Loop reads back a NON-ZERO sink
       wire (EXACT or SEGMENTED, never BARE) with `Is Broken?` not True, and the created LoopTunnel's IndexMode is
       read BEFORE it is written. ExecState immediately after each write is printed, never inferred.
  G0   the route-B original is the pinned md5 (before) and unchanged (after).
  G1   each new file starts byte-identical to its source and reads ExecState 1 before anything changes.
  G2   each copy adds exactly ONE node to diagram 0 and it carries `reference` + `error in (no error)`.
  G3   (no-loop ops) a For Loop is created, `Close Reference` is reparented INTO its body, and the `References`
       wire is BRANCHED into the body node: sink non-zero, a new LoopTunnel appears, its IndexMode settles to 1.
       (OpReportAll_v1) the body is MEASURED to be a CHAIN - exactly one Property node fed by a LoopTunnel
       (`pn_first`), the other fed by `pn_first`'s `Owner` output (`pn_last`) - and the two closes take BRANCHES of
       those two wires: close A <- the traversed element wire, close B <- the `Owner` wire. Same diagram, so the
       sink must read back the branched wire's own uid (EXACT) or another non-zero uid (SEGMENTED).
  G4   ordering. (no-loop ops) the panel `error out` net is branched into `error in (no error)` inside the loop,
       new tunnel IndexMode 0, the error-chain node identified FROM THE MACHINE. (OpReportAll_v1) close A's
       `error in` <- `pn_last`'s `error out`; close B's `error in` <- close A's `error out`.
  G5   ExecState is 1 after each stage's wiring - the repaired op compiles.
  G6   the saved file exists, its md5 is printed, the SOURCE op's md5 is unchanged, the new md5 differs.
  G7   EQUIVALENCE on a scratch copy of the route-B original: v4's counts + report row0 == v3's; v6's ws_call row
       == v5's; v1's report_all(Diagram) uid list == v0's.
  G-A  20 consecutive calls of EACH repaired op complete with NO `error 2` (and no other exception).
  G-B  kernel handles flat within +-100 from CALL 1 to CALL 20 (call 0, the VI load, is excluded and printed).
  G-C  private bytes |drift| <= 5 MB from call 1 to call 20.
Nothing branches on a result; every stage runs and every number is printed.

RUN 1 (`tools/bench/build_s0_closeref_v1.log`, `BGRUN END rc=1 after 566s`, 41 PASS / 2 FAIL, NOTHING SAVED) and
what changed since, so run 2 is not the same run twice:
  * BUG 1, fixed in v2 and kept here: `gscript.uids()` returns a SET, so `.index()` raised (`:47-49`). LoopTunnel
    access indices come from `tun_uids()` = `report_all` ORDER.
  * BUG 2's FIX IS WITHDRAWN: v2 answered run 1's stage-3 crash with "the body's Property nodes are PARALLEL".
    That was an inference from "both `reference out` = 0" and the machine says otherwise (census `:47`,`:49`,`:60`).
    The body is a CHAIN; D1/D2 above replace the whole of `_finish_loop_exists`.
  * The original's md5 was verified unchanged after run 1 (`:139`) and is gated again here, before and after.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconnectfromwire_v0 import connect_from_wire, wire_source_owner  # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1  # noqa: E402
from build_d1_v0 import move_in  # noqa: E402

must, walk, term = B.must, B.walk, B.term

ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")
CD = g.CLAUDEDEV
OP_V3 = os.path.join(CD, "OpReport_v3.vi")
OP_V4 = os.path.join(CD, "OpReport_v4.vi")
WS_V5 = os.path.join(CD, "OpWireSource_v5.vi")
WS_V6 = os.path.join(CD, "OpWireSource_v6.vi")
RA_V0 = os.path.join(CD, "OpReportAll_v0.vi")
RA_V1 = os.path.join(CD, "OpReportAll_v1.vi")
WS_MAP = os.path.join(BENCH, "opwiresource_v5_labels.json")
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))
CN_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
DONOR = os.path.join(CD, "KernelBuilder_v1.vi")
CLOSEREF_UID = 157                      # measured, tools/bench/s0_hygiene_probe.log run 1
TRAVERSE_LABEL = "Traverse for GObjects.vi"
REF_TERM = "reference"                  # measured, tools/bench/s0_terminal_names.log:26
ERRIN_TERM = "error in (no error)"      # measured, tools/bench/s0_terminal_names.log:25
ERROUT_TERM = "error out"
OWNER_TERM = "Owner"                    # measured, tools/bench/s0_body_census.log:47
REFS_TERM = "References"                # measured, :8 (docs/NAMES.md:230 corrected from `GObject Refs`)
# Property SOURCE terminals whose value IS a reference (so reading one MINTS a reference the op must close).
# Reported only - D1 named #114's `Owner`; anything else found here is a judgement call, not this run's repair.
REFMINT = {"owner", "owning vi", "reference out", "wire", "terminals[]", "block diagram", "front panel",
           "label", "diagram", "outside terminal", "inside terminals[]", "vi reference", "panel"}
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(CD, f"SCRATCH_s0_{STAMP}.vi")
ARM_SCRATCH = os.path.join(CD, f"SCRATCH_s0arm_{STAMP}.vi")

g._run.__defaults__ = (6.0, 120.0)
STATE = {}
RESULT = {}
PROOF = {}
BRANCH = {}          # tag -> the branch readbacks, so the ARM can gate what FINISH measured


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(s):
    print(f"   . {s}", flush=True)


def lv_pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return out or None


def mem():
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$p=Get-Process LabVIEW -ErrorAction SilentlyContinue|Select-Object -First 1;"
         "if($p){\"{0} {1}\" -f $p.HandleCount,$p.PrivateMemorySize64}else{'0 0'}"],
        capture_output=True, text=True)
    try:
        a, b = r.stdout.strip().split()
        return int(a), int(b)
    except Exception:
        return 0, 0


def com_preflight(tries=12, gap=4.0):
    """Two spaced round-trips agreeing against an unchanged pid (build_opconstvalue_v1.py:57-76)."""
    probe = os.path.join(CD, "OpWhileCast_v0.vi")
    last = None
    for k in range(tries):
        try:
            p0 = lv_pid()
            n = g.count(probe, "Wire")
            time.sleep(gap)
            n2 = g.count(probe, "Wire")
            p1 = lv_pid()
            if n == n2 and p0 and p0 == p1:
                print(f"   COM preflight OK (pid {p0}, two round-trips agree: {n} wires)", flush=True)
                return True
            last = f"pid {p0}->{p1}, wires {n}->{n2}"
        except Exception as e:
            last = str(e)[:160]
        print(f"   COM preflight attempt {k + 1}/{tries}: {last}", flush=True)
        time.sleep(gap)
    raise B.Stop(f"COM preflight FAILED after {tries} attempts: {last}")


def fresh():
    print(f"   fresh(): killing LabVIEW pid {lv_pid()}", flush=True)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) "
                    "{ Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{LV_EXE}'"],
                   capture_output=True, text=True, timeout=60)
    time.sleep(35)
    g.OP_REPORT = OP_V3          # preflight must use KNOWN-GOOD readers
    g.OP_REPORT_ALL = RA_V0
    g.reset()
    com_preflight()
    print(f"   fresh(): new LabVIEW pid {lv_pid()}", flush=True)


def pick(rows, want, source):
    """The terminal whose name matches `want` (exact, then substring) among sources or sinks. Names are exact
    bytes (CLAUDE.md), so what matched is printed and gated, never assumed."""
    w = want.strip().lower()
    for r in rows:
        if r["is_source"] == source and r["name"].strip().lower() == w:
            return r
    for r in rows:
        if r["is_source"] == source and w in r["name"].strip().lower():
            return r
    return None


def tun_uids(dst):
    """LoopTunnel uids in TRAVERSE ORDER - which is the access index `gscript.tunnels` / `set_index_mode` take.
    `gscript.uids()` returns a SET and must never be used for this (run 1 of this recipe died on `.index`)."""
    return [o["uid"] for o in g.report_all(dst, "LoopTunnel")]


def tun_index(dst, uid):
    """Traverse index of a LoopTunnel uid - the access index gscript.tunnels/set_index_mode take."""
    return tun_uids(dst).index(uid)


def wire_src(dst, wire_uid):
    """(source row, all rows) for `wire_uid` via OpWireSource_v5, read-only. The row names the SOURCE terminal's
    index on the wire and its OWNER - which is the provenance D2 requires and v2 did not have."""
    rows = wire_source_owner(dst, wire_uid, n=8)
    for r in rows:
        if r.get("is_source"):
            return r, rows
    return None, rows


def source_term_index(dst, wire_uid, owner_uid=None):
    """Which terminal of `wire_uid` is its SOURCE. Returns (index, row-or-rows)."""
    rows = wire_source_owner(dst, wire_uid, n=8)
    for r in rows:
        if r.get("is_source") and (owner_uid is None or r.get("owner_uid") == owner_uid):
            return r["i"], r
    return None, rows


def classify(claimed, got):
    """docs/cycle27-plan.md Pre-decided 18: EXACT reads the claimed uid, SEGMENTED reads a DIFFERENT non-zero uid
    (survival, because a crossing is several segments), BARE reads nothing (the only genuine loss)."""
    if not got:
        return "BARE"
    return "EXACT" if got == claimed else "SEGMENTED"


def settle_tunnel(dst, tag, new_tuns, want_mode, label):
    """Read each NEW LoopTunnel's IndexMode and write `want_mode` only where the machine disagrees."""
    for u in new_tuns:
        i = tun_index(dst, u)
        t = g.tunnels(dst, i)
        note(f"[{tag}] new LoopTunnel #{u} (index {i}) IndexMode AS READ {t['index_mode']} "
             f"outer wire {t['out_wire']} inner {t['in_wires']} ({label})")
        BRANCH.setdefault(tag, {}).setdefault("tunnel_mode_as_read", []).append((u, t["index_mode"]))
        if t["index_mode"] != want_mode:
            g.set_index_mode(dst, i, want_mode)
            t = g.tunnels(dst, tun_index(dst, u))
            note(f"[{tag}] set IndexMode -> {want_mode}; read back {t['index_mode']}")
        must(f"G3t {tag}: {label} tunnel IndexMode == {want_mode}", t["index_mode"] == want_mode,
             f"#{u} mode {t['index_mode']}")


def refmint_census(dst, tag, diagram_indices):
    """READ-ONLY. Print every Property node's SOURCE terminals on the given diagrams and flag the names that
    RETURN A REFERENCE. Reported, never repaired: D1 put #114's `Owner` in scope and said nothing about the rest,
    and deciding scope is a judgement act (CLAUDE.md 3)."""
    props = set(o["uid"] for o in g.report_all(dst, "Property"))
    flagged = []
    for d in diagram_indices:
        try:
            w = walk(dst, d)
        except Exception as e:
            note(f"[{tag}] refmint census: Diagram[{d}] UNREAD ({str(e)[:100]})")
            continue
        for u, (_n, _lab, rows) in sorted(w.items()):
            if u not in props:
                continue
            srcs = [r["name"] for r in rows if r["is_source"]]
            hits = [s for s in srcs if s.strip().lower() in REFMINT]
            print(f"   [{tag}] REFMINT D[{d}] Property #{u} sources {srcs} -> reference-returning {hits}",
                  flush=True)
            for h in hits:
                flagged.append((d, u, h))
    print(f"   [{tag}] REFMINT SUMMARY: {len(flagged)} reference-returning property read(s): {flagged}",
          flush=True)
    return flagged


# ---------------------------------------------------------------- the finish hook (runs on MOVE_DST)
def FINISH(dst, added_gobj=None):
    tag, kind, which = STATE["tag"], STATE["kind"], STATE["pass"]
    w = walk(dst, 0)
    added = [u for u in w if u not in STATE["before"]]
    print(f"   [{tag}/{which}] FINISH: new nodes on diagram 0 = {added} (copy_by_index reported {added_gobj})",
          flush=True)
    must(f"G2 {tag}/{which}: exactly ONE node added by the copy", len(added) == 1, str(added))
    cr = added[0]
    rows = w[cr][2]
    print(f"   [{tag}/{which}] Close Reference #{cr} terminals: "
          f"{[(r['i'], r['name'], r['is_source']) for r in rows]}", flush=True)
    ref_t = pick(rows, REF_TERM, False)
    ein_t = pick(rows, ERRIN_TERM, False)
    must(f"G2b {tag}/{which}: Close Reference carries '{REF_TERM}' and '{ERRIN_TERM}' sinks",
         ref_t is not None and ein_t is not None, f"{ref_t}/{ein_t}")

    if kind == "loop":
        _finish_loop(dst, tag, which, cr)
    else:
        _finish_new_loop(dst, tag, cr, w, ref_t, ein_t)

    try:
        g.set_auto_error_handling(dst, False)
        note(f"[{tag}/{which}] auto error handling OFF (Close Reference's `error out` is deliberately unwired, so "
             f"a runtime close error must never open a modal in an unattended run)")
    except Exception as e:
        note(f"[{tag}/{which}] set_auto_error_handling failed (non-fatal): {str(e)[:120]}")

    es = g.exec_state(dst)
    print(f"   [{tag}/{which}] FINISH ExecState {es}", flush=True)
    must(f"G5 {tag}/{which}: the repaired op is RUNNABLE (ExecState 1)", es == 1, f"ExecState {es}")
    STATE[f"closeref_{which}"] = cr


def _body_index(dst, tag):
    """The index of the ForLoop-owned Diagram - report() order, which is what move_in/connect_from_wire take."""
    dias = [d for d in g.report(dst, "Diagram") if d["owner"] == "ForLoop"]
    must(f"G3d {tag}: exactly one ForLoop-owned Diagram", len(dias) == 1,
         str([(d["i"], d["uid"], d["owner"]) for d in dias]))
    note(f"[{tag}] loop body Diagram[{dias[0]['i']}] uid {dias[0]['uid']}")
    return dias[0]["i"]


def _provenance(dst, tag, wb):
    """MEASURE the body's shape instead of assuming it (the review's §1(c): v2 chose by lowest uid).
    Returns (pn_first, pn_last, w_traverse, w_owner) where
      pn_first = the Property node whose `reference` comes from a LOOP TUNNEL (the auto-indexed element),
      pn_last  = the Property node whose `reference` comes from pn_first's `Owner` output (the minted reference)."""
    props = set(o["uid"] for o in g.report_all(dst, "Property"))
    body_pns = sorted(u for u in wb if u in props)
    must(f"G3b {tag}: the body holds EXACTLY TWO Property nodes", len(body_pns) == 2, str(body_pns))
    info = {}
    for u in body_pns:
        r = pick(wb[u][2], REF_TERM, False)
        wire = (r or {}).get("wire", 0)
        src, rows = (wire_src(dst, wire) if wire else (None, []))
        info[u] = {"wire": wire, "src": src}
        note(f"[{tag}]   PN #{u}: {REF_TERM} <- w{wire}, source {src}")
    first = [u for u in body_pns if (info[u]["src"] or {}).get("owner_class") == "LoopTunnel"]
    must(f"G3p1 {tag}: exactly ONE body Property node is fed by a LoopTunnel (the traversed element)",
         len(first) == 1, str(info))
    pn_first = first[0]
    pn_last = next(u for u in body_pns if u != pn_first)
    must(f"G3p2 {tag}: the OTHER Property node is fed by #{pn_first} - the body is a CHAIN, as measured in "
         f"tools/bench/s0_body_census.log:47,:49,:60",
         (info[pn_last]["src"] or {}).get("owner_uid") == pn_first, str(info[pn_last]))
    owner_t = pick(wb[pn_first][2], OWNER_TERM, True)
    must(f"G3p3 {tag}: #{pn_first} exposes the '{OWNER_TERM}' SOURCE terminal that MINTS the second reference",
         owner_t is not None, str([(r["i"], r["name"], r["is_source"]) for r in wb[pn_first][2]]))
    must(f"G3p4 {tag}: #{pn_first}.'{OWNER_TERM}' drives exactly the wire #{pn_last} reads (provenance, not uid "
         f"order)", owner_t["wire"] and owner_t["wire"] == info[pn_last]["wire"],
         f"owner wire {owner_t['wire']} vs pn_last reference wire {info[pn_last]['wire']}")
    note(f"[{tag}] PROVENANCE: traversed element w{info[pn_first]['wire']} -> PN #{pn_first} "
         f"--{OWNER_TERM}--> w{owner_t['wire']} -> PN #{pn_last}")
    return pn_first, pn_last, info[pn_first]["wire"], owner_t["wire"]


def _branch_into(dst, tag, which, what, wire_uid, owner_uid, body_i, node_i, term_i, sink_getter):
    """D2: the refnum input is a BRANCH of the wire that already carries that refnum. One branch wire, made by the
    wire-anchored writer - nothing is hand-wired into the bare scalar input (archive/WORKLOG.md:84-86)."""
    si, srow = source_term_index(dst, wire_uid, owner_uid)
    must(f"G3s {tag}/{which}: w{wire_uid} ({what}) has a SOURCE terminal owned by #{owner_uid}",
         si is not None, str(srow))
    dw, es, err, sub = connect_from_wire(dst, wire_uid, si, body_i, node_i, term_i, CFW_LABELS)
    note(f"[{tag}/{which}] connect_from_wire({what}, branch of w{wire_uid}) dw={dw} ExecState={es} "
         f"err={err!r} sub={sub}")
    got = sink_getter()
    kind = classify(wire_uid, got)
    broken = sub.get("Is Broken?")
    BRANCH.setdefault(tag, {})[which] = {"what": what, "claimed": wire_uid, "got": got, "class": kind,
                                         "is_broken": broken, "exec_state_after": es, "dw": dw}
    print(f"   [{tag}/{which}] BRANCH {what}: claimed w{wire_uid} -> sink w{got} = {kind}, "
          f"Is Broken? {broken!r}, ExecState after {es}", flush=True)
    must(f"G3 {tag}/{which}: {what} branched into the body - sink is not BARE", kind != "BARE",
         f"sink wire {got}")
    must(f"G3k {tag}/{which}: {what} is not reported BROKEN by the op's own ordered `Wire.Is Broken?` reader",
         broken is not True, f"Is Broken? {broken!r}")
    return got, kind, broken


def _finish_loop(dst, tag, which, cr):
    """OpReportAll_v0 -> v1. The For Loop that auto-indexes `References` ALREADY EXISTS, and the body is a CHAIN
    (measured: tools/bench/s0_body_census.log). D1: BOTH references are closed - pass A closes the traversed
    element, pass B closes the `Owner` reference PN #114 mints on every iteration. D2: each close takes a BRANCH
    of the wire that already carries its refnum, and the ERROR CHAIN orders it after the last consumer."""
    body_i = _body_index(dst, tag)
    pos = (24, 24) if which == "A" else (24, 120)
    move_in(dst, cr, body_i, pos)
    wb = walk(dst, body_i)
    must(f"G3a {tag}/{which}: Close Reference #{cr} is now on the loop body diagram", cr in wb, str(sorted(wb)))
    ref_t = pick(wb[cr][2], REF_TERM, False)        # RE-READ after the reparent, never carried across it
    ein_t = pick(wb[cr][2], ERRIN_TERM, False)
    must(f"G3f {tag}/{which}: the reparented Close Reference still exposes '{REF_TERM}' and '{ERRIN_TERM}'",
         ref_t is not None and ein_t is not None,
         str([(r["i"], r["name"], r["is_source"]) for r in wb[cr][2]]))
    pn_first, pn_last, w_trav, w_owner = _provenance(dst, tag, wb)

    if which == "A":
        wire_uid, owner_uid, what = w_trav, None, "the TRAVERSED element reference"
        # the traversed element's wire is sourced by the LoopTunnel's inner terminal; owner_uid stays None so the
        # single SOURCE terminal is taken whatever its owner, and the owner is printed in the note above.
    else:
        wire_uid, owner_uid, what = w_owner, pn_first, f"the `{OWNER_TERM}` reference MINTED by #{pn_first}"

    _branch_into(dst, tag, which, what, wire_uid, owner_uid, body_i, wb[cr][0], ref_t["i"],
                 lambda: (pick(walk(dst, body_i)[cr][2], REF_TERM, False) or {}).get("wire", 0))

    # ---- ordering, by the ERROR CHAIN (D2). Pass A hangs off the LAST consumer #pn_last; pass B hangs off
    #      pass A's close, so both are downstream of every property read and of each other.
    if which == "A":
        src_uid, src_name = pn_last, ERROUT_TERM
    else:
        src_uid, src_name = STATE["closeref_A"], ERROUT_TERM
        must(f"G4p {tag}/B: pass A's Close Reference #{src_uid} is on the body diagram", src_uid in wb,
             str(sorted(wb)))
    src_t = pick(wb[src_uid][2], src_name, True)
    must(f"G4s {tag}/{which}: #{src_uid} exposes '{src_name}'", src_t is not None,
         str([(r["i"], r["name"], r["is_source"]) for r in wb[src_uid][2]]))
    if src_t["wire"]:
        si, srow = source_term_index(dst, src_t["wire"], src_uid)
        must(f"G4e {tag}/{which}: the error wire has a SOURCE terminal owned by #{src_uid}", si is not None,
             str(srow))
        dw, es, err, sub = connect_from_wire(dst, src_t["wire"], si, body_i, wb[cr][0], ein_t["i"], CFW_LABELS)
        note(f"[{tag}/{which}] connect_from_wire(error chain, branch of w{src_t['wire']}) dw={dw} "
             f"ExecState={es} err={err!r} sub={sub}")
    else:
        # NO existing wire to branch (#115's `error out` ships unwired - s0_body_census.log:52), so this is the
        # built two-unwired-terminals writer, on the SAME (body) diagram.
        dw, es, err = connect_nested_v1(dst, body_i, wb[cr][0], ein_t["i"], body_i, wb[src_uid][0], src_t["i"],
                                        CN_LABELS)
        note(f"[{tag}/{which}] connect_nested_v1(D[{body_i}].N[{wb[src_uid][0]}].T[{src_t['i']}] -> "
             f"D[{body_i}].N[{wb[cr][0]}].T[{ein_t['i']}]) dw={dw} ExecState={es} err={err!r}")
    wb = walk(dst, body_i)
    c = (pick(wb[src_uid][2], src_name, True) or {}).get("wire", 0)
    d = (pick(wb[cr][2], ERRIN_TERM, False) or {}).get("wire", 0)
    print(f"   [{tag}/{which}] ERROR CHAIN: #{src_uid}.{src_name} w{c} -> #{cr}.{ERRIN_TERM} w{d} "
          f"({classify(c, d)})", flush=True)
    must(f"G4 {tag}/{which}: #{src_uid}.'{src_name}' -> #{cr}.'{ERRIN_TERM}' - the close runs after every read",
         bool(c) and bool(d), f"{c}/{d}")


def _finish_new_loop(dst, tag, cr, w, ref_t, ein_t):
    """OpReport_v3/OpWireSource_v5 -> v4/v6 (and the ARM): no loop exists, so build the measured one
    (docs/toolkit-capabilities.md:438-443) and branch `References` into it. The ARRAY never touches the scalar
    refnum input - the tunnel delivers one refnum per iteration (review A2/B2: that input defeated four attempts)."""
    which = STATE["pass"]
    tv = next((u for u in w if w[u][1] == TRAVERSE_LABEL), None)
    must(f"G3v {tag}: the Traverse node is present on diagram 0", tv is not None,
         str([(u, w[u][1]) for u in w]))
    refs = term(w[tv][2], REFS_TERM, True)
    must(f"G3r {tag}: the Traverse has the '{REFS_TERM}' SOURCE terminal (NAMES.md:230, measured)",
         refs is not None, str([r["name"] for r in w[tv][2] if r["is_source"]]))
    wref = refs["wire"]
    must(f"G3w {tag}: '{REFS_TERM}' already drives a wire (the branch needs one)", bool(wref), str(wref))
    note(f"[{tag}] References wire = {wref}")

    pos = g.report_all(dst, "Node")
    loc = (max(p["pos"][0] for p in pos) + 220, min(p["pos"][1] for p in pos) + 40)
    g.for_loop(dst, loc)
    loop = g.find_at(dst, "ForLoop", loc, tol=80)
    note(f"[{tag}] For Loop #{loop['uid']} created at {loc} (found at {loop['pos']})")
    body_i = _body_index(dst, tag)
    move_in(dst, cr, body_i, (24, 24))
    wb = walk(dst, body_i)
    must(f"G3a {tag}: Close Reference #{cr} is now on the loop body diagram", cr in wb, str(sorted(wb)))
    cr_n = wb[cr][0]
    ref_t = pick(wb[cr][2], REF_TERM, False)        # RE-READ after the reparent, never carried across it
    ein_t = pick(wb[cr][2], ERRIN_TERM, False)
    must(f"G3f {tag}: the reparented Close Reference still exposes '{REF_TERM}' and '{ERRIN_TERM}'",
         ref_t is not None and ein_t is not None,
         str([(r["i"], r["name"], r["is_source"]) for r in wb[cr][2]]))

    # ---- the refnum: BRANCH the References net into the body node, tunnel auto-indexing.
    tun0 = set(tun_uids(dst))
    got, kind, broken = _branch_into(
        dst, tag, which, f"the `{REFS_TERM}` array", wref, tv, body_i, cr_n, ref_t["i"],
        lambda: (pick(walk(dst, body_i)[cr][2], REF_TERM, False) or {}).get("wire", 0))
    new_tuns = [u for u in tun_uids(dst) if u not in tun0]
    # A BOUNDARY CROSSING IS TWO SEGMENTS PLUS A TUNNEL (docs/toolkit-capabilities.md:447-449), so the gate is
    # "sink reads back non-zero AND a tunnel appeared", never "equal uid on both ends".
    must(f"G3x {tag}: a LoopTunnel appeared for the crossing", len(new_tuns) >= 1, f"new tunnels {new_tuns}")
    BRANCH.setdefault(tag, {})["new_tunnels"] = new_tuns
    settle_tunnel(dst, tag, new_tuns, 1, "References (auto-index: the array supplies N)")
    note(f"[{tag}] ExecState after the refnum branch and the IndexMode settle: {g.exec_state(dst)}")

    # ---- the ordering: the close must run AFTER every property read on diagram 0.
    pw = g.panel_wiring(dst)
    cand = [r for r in pw if str(r.get("label", "")).strip().lower() == "error out" and r.get("wire")]
    note(f"[{tag}] panel error-out indicators: "
         f"{[(r.get('label'), r.get('wire')) for r in pw if 'error' in str(r.get('label', '')).lower()]}")
    must(f"G4a {tag}: exactly one panel indicator labelled 'error out' carrying a wire", len(cand) == 1, str(cand))
    ewire = cand[0]["wire"]
    owner = [u for u in w if (pick(w[u][2], ERROUT_TERM, True) or {}).get("wire") == ewire]
    must(f"G4b {tag}: the node driving the panel's error-out net was identified FROM THE MACHINE",
         len(owner) == 1, f"ewire {ewire} owners {owner}")
    last = owner[0]
    note(f"[{tag}] last error-chain node #{last} ('{w[last][1]}') drives panel error out on wire {ewire}")
    esi, esrow = source_term_index(dst, ewire, last)
    must(f"G4c {tag}: the error net has a SOURCE terminal owned by #{last}", esi is not None, str(esrow))
    tun1 = set(tun_uids(dst))
    dw, es, err, sub = connect_from_wire(dst, ewire, esi, body_i, cr_n, ein_t["i"], CFW_LABELS)
    note(f"[{tag}] connect_from_wire(error chain) dw={dw} ExecState={es} err={err!r} sub={sub}")
    wb = walk(dst, body_i)
    goterr = pick(wb[cr][2], ERRIN_TERM, False)["wire"]
    new_tuns = [u for u in tun_uids(dst) if u not in tun1]
    must(f"G4 {tag}: the error net branched INTO the loop - sink non-zero and a LoopTunnel appeared",
         bool(goterr) and len(new_tuns) >= 1, f"sink wire {goterr}, new tunnels {new_tuns}")
    settle_tunnel(dst, tag, new_tuns, 0, "error chain (scalar: NOT auto-indexed)")


def donor_index():
    fn_uids = [o["uid"] for o in g.report_all(DONOR, "Function")]
    must(f"G2c the donor holds Close Reference #{CLOSEREF_UID}", CLOSEREF_UID in fn_uids, str(fn_uids))
    return fn_uids.index(CLOSEREF_UID)


def one_copy(dst_path, tag, which, i_cr):
    STATE["tag"], STATE["pass"] = tag, which
    STATE["before"] = set(walk(dst_path, 0).keys())
    print(f"  [{tag}/{which}] donor Function index of #{CLOSEREF_UID} = {i_cr}; nodes on diagram 0 before = "
          f"{len(STATE['before'])}", flush=True)
    g.copy_by_index(DONOR, "Function", i_cr, dst_path, expect_uid=CLOSEREF_UID, finish=FINISH)


def repair(src, dst_path, tag, kind):
    """One stage: fresh instance -> byte copy -> copy Close Reference(s) in and wire them -> SAVED file + md5."""
    print(f"\n=== STAGE {tag}: {os.path.basename(src)} -> {os.path.basename(dst_path)} ({kind}) ===", flush=True)
    m_src = md5(src)
    print(f"  source md5 BEFORE {m_src}", flush=True)
    fresh()
    shutil.copy2(src, dst_path)
    must(f"G1a {tag}: the copy is byte-identical", md5(dst_path) == m_src, md5(dst_path))
    es = g.exec_state(dst_path)
    must(f"G1 {tag}: the copy is RUNNABLE before anything is changed", es == 1, f"ExecState {es}")
    STATE["kind"] = kind
    i_cr = donor_index()
    refmint_census(dst_path, tag, [0] if kind != "loop" else [0, 1])

    one_copy(dst_path, tag, "A", i_cr)
    if kind == "loop":
        # D1: the second Close Reference, for the `Owner` reference minted per iteration. A separate copy because
        # copy_by_index requires the Target to be RUNNABLE at the end of each finish (gscript.py:1548-1551).
        one_copy(dst_path, tag, "B", i_cr)

    es = g.exec_state(dst_path)
    must(f"G6a {tag}: the SAVED file is runnable", es == 1, f"ExecState {es}")
    m_new = md5(dst_path)
    print(f"  SAVED {dst_path}", flush=True)
    print(f"  md5   {m_new}   ({os.path.getsize(dst_path)} B)", flush=True)
    must(f"G6b {tag}: the SOURCE op is UNTOUCHED", md5(src) == m_src, md5(src))
    must(f"G6c {tag}: the new file differs from its source", m_new != m_src, m_new)
    RESULT[tag] = {"path": dst_path, "md5": m_new, "bytes": os.path.getsize(dst_path)}
    return m_new


def stage(src, dst_path, tag, kind):
    try:
        repair(src, dst_path, tag, kind)
    except B.Stop as e:
        print(f"  STAGE {tag} STOPPED at gate: {e}", flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  STAGE {tag} RAISED: {str(e)[:200]}", flush=True)
    if tag not in RESULT and os.path.exists(dst_path):
        # copy_by_index writes the target only at the END of its protocol, so a FINISH that raised leaves an
        # UNREPAIRED byte copy behind. Remove it, or the proof section would measure the old op and report it
        # as the repaired one.
        try:
            os.remove(dst_path)
            print(f"  removed the unrepaired {os.path.basename(dst_path)} stub", flush=True)
        except Exception as ex:
            print(f"  could not remove the stub: {ex}", flush=True)


def arm():
    """D3 / the review's §2 second arm. On a SCRATCH copy of OpReport_v3, run exactly the stage-1 write and read
    the three things run 1 never read: the sink wire (classified), the op's own ordered `Is Broken?`, and the new
    LoopTunnel's IndexMode AS READ. Saves no op; the scratch is deleted. Nothing branches on the result."""
    print("\n=== ARM (review 2026-09-19-s0run1-closeorder.md section 2): is the References branch a VALID wire? ===",
          flush=True)
    tag = "ARM"
    try:
        fresh()
        shutil.copy2(OP_V3, ARM_SCRATCH)
        must(f"A1 {tag}: the scratch is a byte copy of OpReport_v3", md5(ARM_SCRATCH) == md5(OP_V3),
             md5(ARM_SCRATCH))
        es = g.exec_state(ARM_SCRATCH)
        must(f"A2 {tag}: the scratch is RUNNABLE before anything is changed", es == 1, f"ExecState {es}")
        STATE["kind"] = "new"
        one_copy(ARM_SCRATCH, tag, "A", donor_index())
        b = BRANCH.get(tag, {}).get("A", {})
        must(f"A3 {tag}: the `{REFS_TERM}` branch is NOT a bare sink (Pre-decided 18: EXACT or SEGMENTED)",
             b.get("class") in ("EXACT", "SEGMENTED"), str(b))
        must(f"A4 {tag}: the op's ordered `Wire.Is Broken?` does not report the branch BROKEN "
             f"(tools/gscript.py:1293-1295 records the opposite result for a Property-node `reference` branch)",
             b.get("is_broken") is not True, str(b))
        print(f"   [{tag}] VERDICT: sink {b.get('class')}, Is Broken? {b.get('is_broken')!r}, ExecState right "
              f"after the write {b.get('exec_state_after')}, tunnel IndexMode as read "
              f"{BRANCH.get(tag, {}).get('tunnel_mode_as_read')}", flush=True)
    except B.Stop as e:
        print(f"  ARM STOPPED at gate: {e}", flush=True)
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"  ARM RAISED: {str(e)[:200]}", flush=True)
    finally:
        try:
            if os.path.exists(ARM_SCRATCH):
                os.remove(ARM_SCRATCH)
                print(f"  deleted {os.path.basename(ARM_SCRATCH)} (the arm saves no op)", flush=True)
        except Exception as e:
            print(f"  could not delete the arm scratch: {e}", flush=True)


# ---------------------------------------------------------------- callers used for equivalence + the proof
def ws_call(op_path, target, wire_uid, idx=0):
    """`build_opconnectfromwire_v0.py:423 wire_source_owner()` with the op PATH as a parameter, so v5 and v6 can
    be compared. UID-addressed: `uid_in` MUST be set (docs/toolkit-capabilities.md:48,:51)."""
    with open(WS_MAP, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(op_path)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(lab["uid_in"], int(wire_uid))
    vi.SetControlValue(lab["term_index"], int(idx))
    g._run(vi)
    return dict(is_source=bool(vi.GetControlValue(lab["is_source"])),
                owner_class=vi.GetControlValue(lab["ownercls"]),
                owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                recip=int(vi.GetControlValue(lab["recip_wire"])),
                err=g._err(vi, "error out") or "")


def twenty(label, call):
    """21 consecutive calls. CALL 0 IS THE VI LOAD and is excluded from the gates by the cycle-43 judgement
    decision: measured (`tools/bench/s0_hygiene_probe_run2.log:75,:95`), call 0 alone is +202 of a +215 handle
    window on a 473 KB target, i.e. the load of the VI and its dependency tree, not a per-call cost. Both the
    raw window and the gated (call 1 -> call 20) window are printed; the gates read the second."""
    rows, err = [], None
    h_raw, p_raw = mem()
    for i in range(21):
        try:
            v = call()
        except Exception as e:
            err = (i, str(e)[:220])
            print(f"   {label} call {i:2d}: RAISED {str(e)[:200]}", flush=True)
            break
        h, pb = mem()
        rows.append((i, h, pb))
        print(f"   {label} call {i:2d}: {str(v)[:56]} handles={h} private={pb/1e6:.1f} MB", flush=True)
    r = {"label": label, "n": len(rows), "err": err, "rows": rows,
         "h_raw": h_raw, "p_raw": p_raw, "h0": None, "h1": None, "p0": None, "p1": None}
    if len(rows) >= 2:
        r["h0"], r["p0"] = rows[1][1], rows[1][2]
        r["h1"], r["p1"] = rows[-1][1], rows[-1][2]
        print(f"   {label}: call 0 (THE LOAD) handles {h_raw} -> {rows[0][1]} ({rows[0][1]-h_raw:+d}), "
              f"private {p_raw/1e6:.1f} -> {rows[0][2]/1e6:.1f} MB   [excluded]", flush=True)
        print(f"   {label}: GATED WINDOW call 1 -> call {rows[-1][0]}: handles {r['h0']} -> {r['h1']} "
              f"({r['h1']-r['h0']:+d}), private {r['p0']/1e6:.1f} -> {r['p1']/1e6:.1f} MB "
              f"({(r['p1']-r['p0'])/1e6:+.1f} MB)", flush=True)
    return r


def err2(r):
    """Did this series hit LabVIEW `error 2` (memory/reference allocation)? - the cycle's named blocker."""
    return bool(r["err"]) and "error 2" in r["err"][1].lower()


def main():
    t0 = time.time()
    print(f"=== D1 STAGE S0 v3 - Close Reference restored, BOTH references, For-Loop design  "
          f"{time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    must("G0 the route-B original is the pinned one", md5(ORIGINAL) == ORIG_MD5, md5(ORIGINAL))
    for p in (OP_V3, WS_V5, RA_V0, DONOR):
        must(f"G0b source on disk: {os.path.basename(p)}", os.path.exists(p), p)

    arm()                                    # D3: before the no-loop stages, as decided

    stage(OP_V3, OP_V4, "OpReport_v4", "new")
    stage(WS_V5, WS_V6, "OpWireSource_v6", "new")
    stage(RA_V0, RA_V1, "OpReportAll_v1", "loop")

    print("\n=== PROOF: equivalence, then 20 consecutive calls of each repaired op ===", flush=True)
    fresh()
    shutil.copy2(ORIGINAL, SCRATCH)
    must("G7a scratch is byte-identical to the original", md5(SCRATCH) == ORIG_MD5, os.path.basename(SCRATCH))

    eq = {}
    for path, tg in ((OP_V3, "v3"), (OP_V4, "v4")):
        if not os.path.exists(path):
            note(f"{tg}: {os.path.basename(path)} not on disk - equivalence skipped")
            continue
        g.OP_REPORT = path
        g._cache.pop(path, None)                 # the cache key is the raw path string (gscript.py:210-215)
        eq[tg] = {c: g.count(SCRATCH, c) for c in ("Diagram", "Node", "Wire")}
        eq[tg + "_row0"] = g.report(SCRATCH, "Diagram")[0]
        print(f"   {tg}: {eq[tg]}   row0 {eq[tg + '_row0']}", flush=True)
    g.OP_REPORT = OP_V3
    if "v3" in eq and "v4" in eq:
        must("G7 OpReport_v4 counts EQUAL OpReport_v3 counts", eq["v3"] == eq["v4"], f"{eq['v3']} vs {eq['v4']}")
        must("G7b OpReport_v4 report() row 0 equals v3's", eq["v3_row0"] == eq["v4_row0"],
             f"{eq['v3_row0']} vs {eq['v4_row0']}")

    ra = {}
    for path, tg in ((RA_V0, "ra0"), (RA_V1, "ra1")):
        if not os.path.exists(path):
            note(f"{tg}: {os.path.basename(path)} not on disk - equivalence skipped")
            continue
        g.OP_REPORT_ALL = path
        g._cache.pop(path, None)
        ra[tg] = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")]
        print(f"   {tg}: report_all(Diagram) -> {len(ra[tg])} uids, first 6 {ra[tg][:6]}", flush=True)
    g.OP_REPORT_ALL = RA_V0
    if "ra0" in ra and "ra1" in ra:
        must("G7d OpReportAll_v1 returns the SAME Diagram uid list as v0", ra["ra0"] == ra["ra1"],
             f"{len(ra['ra0'])} vs {len(ra['ra1'])} uids")

    wire_uid = g.report_all(SCRATCH, "Wire")[0]["uid"]
    print(f"   equivalence wire uid for OpWireSource = {wire_uid}", flush=True)
    ws_eq = {}
    for path, tg in ((WS_V5, "v5"), (WS_V6, "v6")):
        if not os.path.exists(path):
            note(f"{tg}: {os.path.basename(path)} not on disk - equivalence skipped")
            continue
        g._cache.pop(path, None)
        try:
            ws_eq[tg] = ws_call(path, SCRATCH, wire_uid, 0)
        except Exception as e:
            ws_eq[tg] = {"exc": str(e)[:160]}
        print(f"   {tg}: {ws_eq[tg]}", flush=True)
    if "v5" in ws_eq and "v6" in ws_eq:
        must("G7c OpWireSource_v6 returns the SAME row as v5", ws_eq["v5"] == ws_eq["v6"],
             f"{ws_eq['v5']} vs {ws_eq['v6']}")

    # ---- the 20-call proof, repaired ops only (the UNREPAIRED baseline is already measured:
    #      tools/bench/s0_hygiene_probe_run2.log, review B4)
    if "OpReport_v4" in RESULT:
        g.OP_REPORT = OP_V4
        g._cache.pop(OP_V4, None)
        PROOF["v4"] = twenty("NEW OpReport_v4", lambda: g.count(SCRATCH, "Node"))
        g.OP_REPORT = OP_V3
    if "OpWireSource_v6" in RESULT:
        g._cache.pop(WS_V6, None)
        PROOF["ws6"] = twenty("NEW OpWireSource_v6", lambda: ws_call(WS_V6, SCRATCH, wire_uid, 0))
    if "OpReportAll_v1" in RESULT:
        g.OP_REPORT_ALL = RA_V1
        g._cache.pop(RA_V1, None)
        PROOF["ra1"] = twenty("NEW OpReportAll_v1", lambda: len(g.report_all(SCRATCH, "Diagram")))
        g.OP_REPORT_ALL = RA_V0

    # ---- verdict ---------------------------------------------------------------
    print("\n=== VERDICT ===", flush=True)
    print(f"  BRANCH readbacks: {json.dumps(BRANCH, default=str)}", flush=True)
    for k, r in PROOF.items():
        if r["h0"] is None:
            print(f"  {r['label']:<24} {r['n']} calls - NO GATED WINDOW   error2={err2(r)}   err={r['err']}",
                  flush=True)
            continue
        print(f"  {r['label']:<24} {r['n']:2d} calls  handles {r['h0']} -> {r['h1']} "
              f"({r['h1'] - r['h0']:+d})   private {(r['p1'] - r['p0']) / 1e6:+.1f} MB   "
              f"error2={err2(r)}   err={r['err']}", flush=True)
    for tg, r in RESULT.items():
        print(f"  SAVED {tg}: {r['path']}  md5 {r['md5']}  {r['bytes']} B", flush=True)

    for k, r in PROOF.items():
        dh = None if r["h0"] is None else r["h1"] - r["h0"]
        dp = None if r["p0"] is None else (r["p1"] - r["p0"]) / 1e6
        must(f"G-A {r['label']}: 21 calls, NO `error 2`", not err2(r), str(r["err"]))
        must(f"G-A2 {r['label']}: all 21 calls completed", r["err"] is None and r["n"] == 21,
             f"n={r['n']} err={r['err']}")
        must(f"G-B {r['label']}: handles flat +-100 from call 1 to call 20",
             dh is not None and abs(dh) <= 100, f"delta {dh}")
        must(f"G-C {r['label']}: private bytes |drift| <= 5 MB from call 1 to call 20",
             dp is not None and abs(dp) <= 5.0, f"delta {dp} MB")
    must("G-A0 all three ops were repaired and saved", len(RESULT) == 3, str(sorted(RESULT)))
    must("G-A3 every repaired op was proved", len(PROOF) == 3, str(sorted(PROOF)))

    try:
        os.remove(SCRATCH)
        print(f"  deleted {os.path.basename(SCRATCH)}", flush=True)
    except Exception as e:
        print(f"  could not delete scratch: {e}", flush=True)
    must("G9 the route-B original md5 is unchanged", md5(ORIGINAL) == ORIG_MD5, md5(ORIGINAL))
    print(f"\n({time.time()-t0:.0f}s)", flush=True)
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main()
    except B.Stop as e:
        print(f"\nSTOPPED at gate: {e}", flush=True)
    except Exception:
        import traceback
        traceback.print_exc()
    finally:
        try:
            print(f"ORIGINAL md5 AFTER: {md5(ORIGINAL)} (pinned {ORIG_MD5})", flush=True)
        except Exception:
            pass
        for p in (SCRATCH, ARM_SCRATCH):
            try:
                if os.path.exists(p):
                    os.remove(p)
                    print(f"cleanup: deleted {os.path.basename(p)}", flush=True)
            except Exception:
                pass
        npass = sum(1 for _n, ok in B.PASS if ok)
        nfail = sum(1 for _n, ok in B.PASS if not ok)
        print(f"\nGATES: {npass} PASS / {nfail} FAIL", flush=True)
        if nfail:
            print("failing: " + ", ".join(n for n, ok in B.PASS if not ok), flush=True)
        for tg, r in RESULT.items():
            print(f"ARTEFACT {tg}: {r['path']}  md5 {r['md5']}", flush=True)
    sys.exit(0 if (rc == 0 and not any(not ok for _n, ok in B.PASS)) else 1)
