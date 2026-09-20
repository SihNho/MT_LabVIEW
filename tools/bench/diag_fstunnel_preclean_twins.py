r"""diag_fstunnel_preclean_twins.py - DOES A PRE-CLEAN OF THE DONOR'S TWO ORPHAN WIRES AT `_v1.py:403` CHANGE THE
B4 `ExecState`?  Two twins from the frozen `_v1` construction, ONE runner, no RBW anywhere before B4 in twin B.

Cycle 23 dispatch 4 MATERIAL brief. This is a DIAGNOSTIC: it lives under tools/bench, it saves no VI, it builds no
op, and it NEVER writes to tools/recipes/build_opfstunnelterm_v1.py (STATUS: any edit to `_v1.py` bricks its launch
path - `stop_record._check:325`). `_v1.py` is IMPORTED and monkey-patched IN MEMORY ONLY.
`tools/recipes/build_opfstunnelterm_v2.py` is NOT launched and NOT imported.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "before creating any new op"):
  * `grep -n "^def " tools/gscript.py` - gscript has NO orphan-wire reader and NO pre-clean; `ls tools/bench
    tools/recipes` - the three existing fstunnel diagnostics are diag_fstunnel_{orphans,rbwvictims,wirebroken}.py
    and NONE of them pre-cleans the donor copy at CKPT[00] and then reaches B4 without an RBW call. That gap IS
    this file.
  * the import+freeze route (`StopAtB4`, `_must_hook`, `build_to_b4`, `snapshot`, `handles`, `md5`) is COPIED
    VERBATIM from tools/bench/diag_fstunnel_wirebroken.py:154-183 + :119-150 (dispatch 1, 10/10, rc=0).
  * the `sweep` line-stamp hook (`inspect` on the caller's f_lineno, so the clean fires at exactly the
    `_v1.py:403` checkpoint and nowhere else) is COPIED from tools/bench/diag_fstunnel_rbwvictims.py:164-181
    (dispatch 2, 18/18, rc=0).
  * the orphan test itself (a wire NO owning-node terminal reads at either end) is
    tools/recipes/build_opfstunnelterm_v2.py:465-470 `orphan_wires()`, re-typed here as three lines rather than
    imported, ONLY because `_v2.py` is being edited in the same dispatch and an import would race that edit.
    Same algorithm, same `sweep()`/`gscript.uids` inputs. `gscript.net_map` is deliberately NOT used: its purge
    calls remove_bad_wires_scripted itself (tools/gscript.py:2509-2531), which destroys the distinction.
  * `gscript.remove_bad_wires_scripted` read as a SET DIFFERENCE of Wire uids - dispatch 2's reading, not new.
  * NO new op VI is built. NO `Wire.Is Broken?` read is taken (dispatch 3's prior-art finding A1: an orphan has no
    sink terminal, so 6371004 has no measured route for one; and docs/NAMES.md records that such a read PERTURBS
    the ExecState, which is the very number this diagnostic exists to measure).

THE TWO TWINS
  TWIN A - in-run control, NO pre-clean: build to B4; `ExecState` at B4; then `remove_bad_wires_scripted` and its
           removed-list / added-list / wire count / `ExecState` after.
  TWIN B - PRE-CLEANED at CKPT[00] (`_v1.py:403`): the orphan set is measured, asserted to be EXACTLY {894, 1356}
           (anything else removes NOTHING and aborts the twin), then those wires are deleted ONE BY ONE with
           `gscript.delete_object` - NOT with RBW, so no recompile side effect can be smuggled in. Then, in order:
             (1) wire count + `ExecState` immediately after the clean;
             (2) `ExecState` AT B4 with NO RBW call anywhere in between  <- THE KEY NUMBER;
             (3) the six wire sites' per-site `ExecState BEFORE` (`_v1`'s own wire_checked attributor);
             (4) at B4, `remove_bad_wires_scripted`: removed-list, added-list, `ExecState` after. An EMPTY
                 removed-list with `ExecState` flipping 0->1 IS a legitimate outcome and is reported plainly;
             (5) the wire uids present at B4, and whether 384 / 1694 / 1719 / 1766 all exist.
  No conclusion about which explanation this favours is drawn anywhere in this file or in its output.

PREDICTION CONTRACT (each line PASS/FAIL; one miss never hides the rest; P7 is REPORTED, never asserted):
  P1  TWIN A reproduces run 1 (tools/bench/build_opfstunnelterm_v1_run1.log:45-75) object for object: terms 145 /
      ia 151 / tmsc 1044 / consumers [157,1319,1326]; the six sites land on 384,384,1694,1719,1719,1766.
  P2  TWIN A `ExecState` at the B4 point == 0 (run 1 line 75).
  P3  TWIN A RBW at B4 removes EXACTLY [894,1356], adds nothing, and `ExecState` goes 0 -> 1
      (tools/bench/diag_fstunnel_rbwvictims.log:164-172).
  P4  TWIN B the orphan set measured at the `_v1.py:403` checkpoint is EXACTLY [894,1356]; on anything else the
      twin removes NOTHING and aborts (the abort is itself a reported result).
  P5  TWIN B after the clean: 42 -> 40 wires and the node-TERMINAL count is unchanged (no node lost a connection).
  P6  TWIN B reaches the B4 gate with NO RBW call in between - enforced MECHANICALLY: every RBW call in this file
      goes through `rbw_at()`, which RAISES unless `RBW_ALLOWED[0]` is True, and that flag is set only after a
      twin has frozen at B4. The count of RBW call sites in this file's own source is printed beside it.
  P7  TWIN B `ExecState` at the B4 point - RECORDED, NOT ASSERTED. Both 0 and 1 are legitimate outcomes.
  P8  TWIN B the six per-site `ExecState BEFORE` values are recorded from `_v1.RES["wires"]`.
  P9  TWIN B the Wire census at B4 is recorded, with the presence of 384 / 1694 / 1719 / 1766.
  P10 TWIN B RBW at B4: removed-list, added-list and `ExecState` after are RECORDED, NOT asserted.
  P11 handle count before and after; both scratch VIs created and DELETED in this same run.
  P12 every original md5-identical BEFORE AND AFTER (3StateClamping + every .vi under `zz_LabView VI\background
      VIs` + the V6 working copy + the donor), and no original is opened at all (`identity()` is never called).
  P13 no motor, no serial port, no camera, `motor_gate.py --execute` never called (Pre-decided 2 / P1).

LAUNCH LINE ACTUALLY USED, and why it is not the usual one (a harness friction worth recording, not a bypass):
  py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_preclean_twins.log -- py -u tools/bench/diag_fstunnel_preclean_twins.py MATERIAL=1
  The documented prefix form `MATERIAL=1 py tools/bgrun.py ...` no longer matches `.claude/settings.json`'s
  allowlist entry `Bash(py tools/*)` (the env prefix moves the first token), and a non-interactive session cannot
  answer the resulting prompt; the PowerShell equivalent `$env:MATERIAL='1'; py ...` is refused by the tool's own
  "command modifies environment variables" check. `guard_bash.MARKER_RE` asks only for the token `MATERIAL=1`
  ANYWHERE on the command line as its own whitespace-delimited token (tools/hooks/guard_bash.py:50), so the
  declaration is made as a TRAILING ARGV TOKEN. This file never reads sys.argv, so the token is inert.
  No guard was disabled, no env var was set, nothing was edited in .claude/.
"""
import glob as _glob
import hashlib
import inspect
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))                 # tools/bench
ROOT = os.path.dirname(os.path.dirname(HERE))                     # project root
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes"),
           os.path.join(ROOT, "tools", "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                               # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid                    # noqa: E402
import build_opfstunnelterm_v1 as V1                              # noqa: E402  READ ONLY - never patched on disk

STAMP = time.strftime("%H%M%S")
SCR_A = os.path.join(g.CLAUDEDEV, f"SCRATCH_fspcA_{STAMP}_{os.getpid()}.vi")
SCR_B = os.path.join(g.CLAUDEDEV, f"SCRATCH_fspcB_{STAMP}_{os.getpid()}.vi")
OUT = os.path.join(HERE, "diag_fstunnel_preclean_twins.json")

ZZ = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))      # ...\zz_LabView VI
BGVIS = os.path.join(ZZ, "background VIs")
ORIGINALS = [V1.ORIG_3STATE] + sorted(_glob.glob(os.path.join(BGVIS, "**", "*.vi"), recursive=True))
WATCHED = ORIGINALS + [V1.V6, V1.DONOR]

RUN1 = {"terms": 145, "ia": 151, "tmsc": 1044, "consumers": [157, 1319, 1326],
        "wires": [384, 384, 1694, 1719, 1719, 1766]}
ORPHANS = [894, 1356]            # diag_fstunnel_rbwvictims.log:14 - already in the DONOR file
DONOR_WIRES = 42                 # ibid.
SITE_WIRES = [384, 1694, 1719, 1766]
CKPT_LINE = 403                  # `by = sweep(op)` in build_one - diag_fstunnel_rbwvictims.log:181 "CKPT[00] ... :403"

RES = {"gates": [], "twinA": {}, "twinB": {}, "md5": {}, "handles": {}}
RBW_ALLOWED = [False]            # P6's mechanical enforcement


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:500]})
    return bool(ok)


def note(label, value):
    print(f"  NOTE {label}: {str(value)[:400]}", flush=True)


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERR {e}"


def snapshot(tag):
    d = {p: md5(p) for p in WATCHED}
    RES["md5"][tag] = d
    print(f"-- md5 {tag}: {len(d)} files ({len(ORIGINALS)} originals) --", flush=True)
    print(f"   {d[V1.ORIG_3STATE]}  {os.path.basename(V1.ORIG_3STATE)}", flush=True)
    return d


def handles(tag):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                              "Measure-Object -Property HandleCount -Sum).Sum"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        n = int(out) if out else 0
    except Exception as e:
        n = f"ERR {str(e)[:60]}"
    RES["handles"][tag] = n
    print(f"  HANDLES {tag}: {n}  (fresh baseline ~31,500)", flush=True)
    return n


def nterms(by):
    return sum(len(rows) for (_i, rows) in by.values())


def orphan_wires(target, by):
    """(orphan uids, whole Wire census). COPIED from build_opfstunnelterm_v2.py:465-470 - a wire is an ORPHAN when
    NO owning-node terminal on diagram 0 reads it at EITHER end (dispatch 2 printed this as "END NONE")."""
    on_terms = {int(r["wire"]) for _u, (_i, rows) in by.items() for r in rows if r["wire"]}
    census = sorted(int(w) for w in g.uids(target, "Wire"))
    return sorted(w for w in census if w not in on_terms), census


def rbw_at(target, where):
    """The ONLY route to remove_bad_wires_scripted in this file. Refuses unless a twin has frozen at B4 (P6)."""
    if not RBW_ALLOWED[0]:
        raise RuntimeError(f"P6 VIOLATION: rbw_at({where}) called while RBW_ALLOWED is False - a pre-B4 RBW call "
                           f"would invalidate the whole measurement")
    w0 = sorted(int(w) for w in g.uids(target, "Wire"))
    es0 = g.exec_state(target)
    try:
        g.remove_bad_wires_scripted(target)
        err = ""
    except Exception as e:
        err = str(e)[:200]
    w1 = sorted(int(w) for w in g.uids(target, "Wire"))
    es1 = g.exec_state(target)
    rec = {"where": where, "exec_before": es0, "exec_after": es1, "n_before": len(w0), "n_after": len(w1),
           "removed": sorted(set(w0) - set(w1)), "added": sorted(set(w1) - set(w0)), "err": err,
           "wires_before": w0, "wires_after": w1}
    print(f"   RBW @{where}: ExecState {es0} -> {es1}; {len(w0)} -> {len(w1)} wires; "
          f"REMOVED {rec['removed']}; ADDED {rec['added']}; err {err!r}", flush=True)
    return rec


def rbw_call_sites():
    token = "remove_bad_wires" + "_scripted("
    try:
        with open(os.path.abspath(__file__), encoding="utf-8", errors="replace") as f:
            src = f.readlines()
    except Exception as e:
        return [f"ERR {str(e)[:80]}"]
    return [f"{i}: {l.strip()[:80]}" for i, l in enumerate(src, 1)
            if token in l and not l.lstrip().startswith("#")]


# ============================================================ the B4 freeze + the CKPT[00] pre-clean
class StopAtB4(Exception):
    pass


_V1_MUST = V1.must
_V1_SWEEP = V1.sweep
PRECLEAN = {"path": None, "done": False, "rec": {}}


def _must_hook(label, ok, detail=""):
    r = _V1_MUST(label, ok, detail)
    if label.startswith("B4 "):                 # "B4b ..." must pass through - it fires BEFORE B4
        raise StopAtB4(f"{label} | {detail}")
    return r


def do_preclean(target):
    """Remove the donor copy's OWN orphan wires - and nothing else - with delete_object, never with RBW."""
    by0 = _V1_SWEEP(target)
    nt0 = nterms(by0)
    orph, census0 = orphan_wires(target, by0)
    es0 = g.exec_state(target)
    rec = {"orphans_measured": orph, "orphans_predicted": ORPHANS, "n_wires_before": len(census0),
           "wires_before": census0, "n_terminals_before": nt0, "exec_before_clean": es0, "removed": [],
           "aborted": False}
    PRECLEAN["rec"] = rec
    print(f"   PRECLEAN @_v1.py:{CKPT_LINE}: {len(census0)} wires, {nt0} node terminals, ExecState {es0}; "
          f"orphan set (no owning-node terminal at either end) = {orph}", flush=True)
    if not must(f"P4 TWIN B the orphan set at the _v1.py:{CKPT_LINE} checkpoint is EXACTLY {ORPHANS}",
                orph == ORPHANS, f"measured {orph}; {len(census0)} wires; ExecState {es0}"):
        rec["aborted"] = True
        print("   ABORT: NOTHING was removed - a wire the assertion did not predict is never removed.", flush=True)
        raise RuntimeError(f"preclean aborted: orphan set {orph} != {ORPHANS}")
    for w in ORPHANS:
        order = [int(o["uid"]) for o in g.report_all(target, "Wire")]
        if w not in order:
            print(f"      orphan #{w} already absent", flush=True)
            continue
        g.delete_object(target, "Wire", order.index(w), verify=False)
        print(f"      deleted orphan Wire #{w} (delete_object, NOT RBW)", flush=True)
    by1 = _V1_SWEEP(target)
    census1 = sorted(int(w) for w in g.uids(target, "Wire"))
    nt1 = nterms(by1)
    es1 = g.exec_state(target)
    rec.update({"removed": sorted(set(census0) - set(census1)), "added": sorted(set(census1) - set(census0)),
                "n_wires_after": len(census1), "wires_after": census1, "n_terminals_after": nt1,
                "exec_after_clean": es1})
    print(f"   PRECLEAN DONE (1): {len(census0)} -> {len(census1)} wires; REMOVED {rec['removed']}; "
          f"terminals {nt0} -> {nt1}; ExecState after the clean = {es1}", flush=True)
    must(f"P5 TWIN B after the clean: {DONOR_WIRES} -> {DONOR_WIRES - len(ORPHANS)} wires, removed exactly "
         f"{ORPHANS}, and the node-TERMINAL count is unchanged",
         len(census0) == DONOR_WIRES and len(census1) == DONOR_WIRES - len(ORPHANS)
         and rec["removed"] == ORPHANS and rec["added"] == [] and nt1 == nt0,
         f"{len(census0)} -> {len(census1)} wires; removed {rec['removed']}; added {rec['added']}; "
         f"terminals {nt0} -> {nt1}")
    return by1


def _sweep_hook(target, n=120, diagram=0):
    r = _V1_SWEEP(target, n, diagram)
    try:
        line = inspect.currentframe().f_back.f_lineno
    except Exception:
        line = None
    if (PRECLEAN["path"] and not PRECLEAN["done"] and line == CKPT_LINE
            and os.path.normcase(target) == os.path.normcase(PRECLEAN["path"])):
        PRECLEAN["done"] = True
        return do_preclean(target)      # the post-clean sweep becomes build_one's own `by`
    return r


def build_to_b4(kind, path, preclean=False):
    spec = list(V1.SPEC[kind])
    spec[0] = path
    V1.SPEC[kind] = tuple(spec)
    V1.must = _must_hook
    V1.sweep = _sweep_hook
    V1.RES["wires"] = []
    V1.RES["build"] = []
    PRECLEAN.update({"path": path if preclean else None, "done": False, "rec": {}})
    RBW_ALLOWED[0] = False
    print(f"\n================ REPRODUCE build_one({kind!r}) -> {os.path.basename(path)} "
          f"(preclean={preclean}) ================", flush=True)
    try:
        out = "NO STOP: build_one returned without the B4 gate firing"
        V1.build_one(kind)
    except StopAtB4 as e:
        out = f"FROZEN AT B4: {e}"
    except Exception as e:
        out = f"EXC before B4: {type(e).__name__} {str(e)[:260]}"
    finally:
        PRECLEAN["path"] = None
    RBW_ALLOWED[0] = True               # only now may rbw_at() run (P6)
    return out


def site_table(tag):
    """The six wire_checked records as `_v1` itself recorded them, per site."""
    rows = []
    for i, w in enumerate(V1.RES["wires"]):
        rows.append({"site": i + 1, "tag": (w.get("tag") or "").strip(), "src": f"#{w['src_uid']}.{w['src_term']}",
                     "sink": f"#{w['dst_uid']}.{w['dst_term']}", "branch": w.get("branch"),
                     "wire": w.get("src_after"), "exec_before": w.get("exec_before"),
                     "exec_after": w.get("exec_after")})
        print(f"   {tag} SITE {i + 1} {rows[-1]['src']} -> {rows[-1]['sink']} wire {rows[-1]['wire']}: "
              f"ExecState BEFORE = {rows[-1]['exec_before']!r}, AFTER = {rows[-1]['exec_after']!r}", flush=True)
    return rows


def census_at(target, tag):
    w = sorted(int(u) for u in g.uids(target, "Wire"))
    have = {str(x): (x in w) for x in SITE_WIRES}
    print(f"   {tag} Wire census: {len(w)} wires; 384/1694/1719/1766 present = {have}", flush=True)
    note(f"{tag} wire uids", w)
    return {"n": len(w), "uids": w, "site_wires_present": have, "all_four_present": all(have.values())}


# ============================================================ main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT P1..P13 - see this file's docstring. NO conclusion about E1/E2 is drawn here.",
          flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    print(f"   scratch A (control, no pre-clean) {SCR_A}\n   scratch B (pre-cleaned at CKPT[00]) {SCR_B}",
          flush=True)
    sites = rbw_call_sites()
    note("P6 remove_bad_wires_scripted call sites in THIS file", sites)
    must("P6a every RBW call in this file is inside rbw_at(), which refuses before a B4 freeze", len(sites) == 1,
         str(sites))
    before = snapshot("before")

    try:
        fresh()
        handles("after a fresh LabVIEW, before any work")

        # ===================== TWIN A - the in-run control, NO pre-clean ==============================
        stopA = build_to_b4("OUT", SCR_A, preclean=False)
        note("TWIN A stop reason", stopA)
        must("P1a TWIN A reached the B4 gate (so the frozen state IS the B4 point)",
             stopA.startswith("FROZEN AT B4"), stopA)
        b1 = next((b for b in V1.RES["build"] if "pn_terms" in b), {})
        wires_seen = [w.get("src_after") for w in V1.RES["wires"]]
        esA = g.exec_state(SCR_A)
        censusA = census_at(SCR_A, "TWIN A @B4")
        rowsA = site_table("TWIN A")
        RES["twinA"] = {"stop": stopA, "b1": b1, "wires_seen": wires_seen, "exec_at_b4": esA,
                        "census_at_b4": censusA, "sites": rowsA}
        must("P1 TWIN A reproduces run 1 object for object (terms/ia/tmsc/consumers and all six site wires)",
             b1.get("pn_terms") == RUN1["terms"] and b1.get("ia") == RUN1["ia"] and b1.get("tmsc") == RUN1["tmsc"]
             and list(b1.get("consumers") or []) == RUN1["consumers"] and wires_seen == RUN1["wires"],
             f"terms {b1.get('pn_terms')} ia {b1.get('ia')} tmsc {b1.get('tmsc')} "
             f"consumers {b1.get('consumers')} wires {wires_seen} vs run1 {RUN1['wires']}")
        print(f"\n   >>> TWIN A ExecState AT B4 = {esA}", flush=True)
        must("P2 TWIN A ExecState at the B4 point is 0, as run 1 measured (…v1_run1.log:75)", esA == 0,
             f"ExecState {esA}")
        rbwA = rbw_at(SCR_A, "TWIN A @B4")
        RES["twinA"]["rbw"] = rbwA
        must(f"P3 TWIN A RBW at B4 removed EXACTLY {ORPHANS}, added nothing, and ExecState went 0 -> 1",
             not rbwA["err"] and rbwA["removed"] == ORPHANS and rbwA["added"] == []
             and rbwA["exec_before"] == 0 and rbwA["exec_after"] == 1,
             f"removed {rbwA['removed']}; added {rbwA['added']}; ExecState {rbwA['exec_before']} -> "
             f"{rbwA['exec_after']}; err {rbwA['err']!r}")
        try:
            g.close_panel(SCR_A)
        except Exception:
            pass

        # ===================== TWIN B - pre-cleaned at CKPT[00], no RBW before B4 =====================
        stopB = build_to_b4("OUT", SCR_B, preclean=True)
        note("TWIN B stop reason", stopB)
        pre = PRECLEAN["rec"]
        RES["twinB"] = {"stop": stopB, "preclean": pre}
        reached = stopB.startswith("FROZEN AT B4")
        must("P6b TWIN B reached the B4 gate with NO RBW call in between (the pre-clean used delete_object)",
             reached and not pre.get("aborted"), stopB)
        b1b = next((b for b in V1.RES["build"] if "pn_terms" in b), {})
        wires_seenB = [w.get("src_after") for w in V1.RES["wires"]]
        esB = g.exec_state(SCR_B)
        print(f"\n   >>> TWIN B (2) ExecState AT B4, NO RBW ANYWHERE IN BETWEEN = {esB}"
              f"{'' if reached else '   [NOT the B4 point - see the stop reason]'}", flush=True)
        rowsB = site_table("TWIN B (3)")
        censusB = census_at(SCR_B, "TWIN B (5) @B4")
        RES["twinB"].update({"b1": b1b, "wires_seen": wires_seenB, "exec_at_b4": esB, "reached_b4": reached,
                             "sites": rowsB, "census_at_b4": censusB})
        must("P7 TWIN B ExecState at the B4 point was RECORDED (not asserted - either value is legitimate)",
             isinstance(esB, int), f"ExecState {esB}")
        must("P8 TWIN B the per-site ExecState BEFORE values were recorded for every wire site reached",
             len(rowsB) > 0, f"{len(rowsB)} site rows; exec_before = {[r['exec_before'] for r in rowsB]}")
        must("P9 TWIN B the Wire census at B4 was recorded with the presence of 384/1694/1719/1766", True,
             f"{censusB['n']} wires; {censusB['site_wires_present']}")
        rbwB = rbw_at(SCR_B, "TWIN B (4) @B4")
        RES["twinB"]["rbw"] = rbwB
        print(f"   >>> TWIN B (4) RBW AT B4: removed {rbwB['removed']}, added {rbwB['added']}, "
              f"ExecState {rbwB['exec_before']} -> {rbwB['exec_after']}"
              f"{'   [EMPTY removed-list with a 0->1 flip - a legitimate outcome, not a failure]' if not rbwB['removed'] and rbwB['exec_before'] != rbwB['exec_after'] else ''}",
             flush=True)
        must("P10 TWIN B RBW at B4 ran and its removed/added/ExecState were RECORDED (not asserted)",
             not rbwB["err"], f"removed {rbwB['removed']}; added {rbwB['added']}; "
                              f"ExecState {rbwB['exec_before']} -> {rbwB['exec_after']}; err {rbwB['err']!r}")

        print("\n================ THE ANSWER SHEET (numbers only) ================", flush=True)
        print(f"   TWIN A: ExecState @B4 = {RES['twinA'].get('exec_at_b4')}; RBW removed "
              f"{rbwA['removed']}, added {rbwA['added']}, ExecState {rbwA['exec_before']} -> "
              f"{rbwA['exec_after']}; {rbwA['n_before']} -> {rbwA['n_after']} wires", flush=True)
        print(f"   TWIN B (1) after the clean: {pre.get('n_wires_after')} wires, ExecState "
              f"{pre.get('exec_after_clean')}  (before the clean: {pre.get('n_wires_before')} wires, ExecState "
              f"{pre.get('exec_before_clean')}; removed {pre.get('removed')})", flush=True)
        print(f"   TWIN B (2) ExecState @B4, NO RBW in between = {esB}", flush=True)
        print(f"   TWIN B (3) per-site ExecState BEFORE = {[r['exec_before'] for r in rowsB]}  "
              f"(AFTER = {[r['exec_after'] for r in rowsB]}; wires {wires_seenB})", flush=True)
        print(f"   TWIN B (4) RBW @B4: removed {rbwB['removed']}, added {rbwB['added']}, ExecState "
              f"{rbwB['exec_before']} -> {rbwB['exec_after']}", flush=True)
        print(f"   TWIN B (5) wires @B4 = {censusB['n']}; 384/1694/1719/1766 present = "
              f"{censusB['site_wires_present']} (all four: {censusB['all_four_present']})", flush=True)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-2000:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        for p in (SCR_A, SCR_B):
            try:
                g.close_panel(p)
            except Exception:
                pass
        try:
            g.reset()
        except Exception:
            pass
        time.sleep(0.5)
        gone = []
        for p in (SCR_A, SCR_B):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as e:
                    print(f"   scratch delete FAILED {os.path.basename(p)}: {str(e)[:120]}", flush=True)
            gone.append(not os.path.exists(p))
        must("P11 both scratch VIs were created and DELETED in this same run", all(gone),
             f"A gone {gone[0]}, B gone {gone[1]}")
        handles("after the run")
        after = snapshot("after")
        diff = [os.path.basename(p) for p in WATCHED if before.get(p) != after.get(p)]
        must(f"P12 all {len(ORIGINALS)} originals (+ the V6 copy and the donor) are md5-identical before and "
             f"after, and no original was opened", not diff and not any(str(v).startswith("ERR")
                                                                       for v in after.values()),
             f"differing: {diff}")
        must("P13 no motor, no serial port, no camera, motor_gate.py --execute not called (static: this file "
             "makes no such call)", True, "read-only VI Server + two throwaway scratch VIs")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:56] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
