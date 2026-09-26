r"""stagekit - THE STAGE-SCRIPT SKELETON AS A LIBRARY (docs/cycle27-plan.md Pre-decided 103, USER-APPROVED
2026-09-22: "템플릿을 만들어두고 ... 아예 라이브러리 작성해서 인풋만 넣어주도록 ... 좋아").

WHY: cycle 63 wrote five 35-55 KB scripts whose ~80 % is one skeleton, and that authoring was 99 of its 181
minutes. This module holds THAT skeleton - lifted verbatim from the scripts that already passed, never
re-invented - so a stage file declares its INPUT, its ROWS and its CRITERIA and nothing else.

WHAT IT IS LIFTED FROM (read before a line was written, per CLAUDE.md "check what exists first"):
  * `tools/recipes/build_opfsinnertunnelconnect_v0.py`  - md5 pin + PINS + claudeDev listing phase (`:359`),
    `md5` `:227`, `del_wire` `:336`, `del_node` `:346`, `resolve_triple` `:730`, `purge_junk` `:288`,
    `private_bytes` `:270`, the `gate`/`fact`/`head`/`safe`/`dump`/`left_s` block `:200-245`.
  * `tools/bench/diag_c83_connect2x2_r2.py`            - the CELL loop on a dated scratch COPY (`:417`),
    the poisoned caller (`:169`), the hygiene phase (`:523`).
  * `tools/recipes/build_d1_m3a3b_d3.py`               - `bad_wire_count` `:265`, `fsit_call` `:279`,
    `fsit_read` `:342`, GATE S's owner-identity reading `:580-612`.
  * `tools/recipes/stage_d1_s1.py` / `stage_d1_s2_loops.py` - the STAGE shape: pins FATAL first, fresh
    instance, ORIGINAL Preloaded read-only, one save, cold re-read, `cond_read`'s third outcome UNREAD.
  * `tools/recipes/build_d1_m3a2.py` / `build_d1_m3a1.py`   - `node_census`/`new_nodes`/`node_view`/
    `delete_by_uid`/`print_walk`/`pd85_violations`/`loop_index_of` (imported, never re-typed).
  * `tools/gscript.py`                                  - every edit verb. NO NEW LabVIEW OP VI IS BUILT
    HERE; every mutator below is a thin wrapper over a verb that already exists on disk.

HARD RULES BAKED IN (they are not the stage file's to remember)
  1  An ORIGINAL is never opened for writing and never saved: `Stage` md5-pins the ORIGINAL
     (2a78e17c...) and its own INPUT before anything, FATALLY, and works only on a dated COPY under
     claudeDev (`g.save` itself refuses a path outside it).
  2  THE ARTEFACT IS NEVER RUN (34(f)). Nothing in this module calls `Run` on a stage target; the only
     VIs that execute are the built op VIs - that is what scripting is.
  3  Every uid is RE-READ immediately before use (34(h)); no index is carried across a mutation.
  4  `%`-format is not used to build any message - `.format()`/f-strings only (the 2026-09-22 TypeError).
  5  Gate rows print the DOCUMENTED tokens `  PASS  ` / `  FAIL  ` / `  FACT  ` - never `**FAIL**`
     (guard_peer.py:96 FAILURE_RE; docs/violation-decisions.md `device-failed` 2026-09-20).
  6  A mutating reader (Remove Bad Wires) refuses to run on the stage target unless the caller says
     `allow_mutation=True`, because it DELETES.
  7  Timeouts: the caller runs under `tools/bgrun.py --max-min N`; `Stage(deadline_min=)` keeps its own
     soft budget so the hygiene tail always lands inside the process deadline.

TYPICAL STAGE FILE
    import stagekit as K
    s = K.Stage(INPUT_VI, INPUT_MD5, "d1_m3a3_rowD", deadline_min=25)
    s.start()
    s.plan_rows(ROWS)                  # optional: one advisory JEV-ROWCHECK line per planned re-wiring row
    s.delete_wire(7506)
    r = s.fs_inner_tunnel_connect(7468, d_idx, 21, 1)
    s.junk_purge("rowD")
    s.gate("exactly one source and it is #23868", ...)
    s.save(broken_ok=True)
    sys.exit(s.close())
"""
import glob
import hashlib
import importlib
import json
import os
import shutil
import subprocess
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (HERE, os.path.join(HERE, "bench"), os.path.join(HERE, "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402

BENCH = os.path.join(HERE, "bench")
CLAUDEDEV = g.CLAUDEDEV

# THE ORIGINAL'S IDENTITY IS IMPORTED, NEVER RESTATED - `gscript` owns it (`gscript.py:62-70`).
# This module's FIRST run restated the path and restated it wrong, so the K2 pin pinned a file that is not
# there (`tools/bench/diag_c83_connect2x2_kit.log:10`); the review that followed
# (`archive/peer/2026-09-22-c87-stagekit-k2.md` §1) refuted "one wrong string" and named the real fault:
# a SECOND owner of one identity. Re-synchronising two copies was the shallow repair; this is the other one.
ORIGINAL = g.ORIGINAL
ORIG_MD5 = g.ORIG_MD5

# The five md5 pins every D1 stage carries (build_opfsinnertunnelconnect_v0.py:190-196). Resolved lazily so
# this module imports on a machine that has no claudeDev.
_PIN_SPEC = (("ORIGINAL", ORIGINAL, ORIG_MD5),
             ("S1 D1_s1_copy", os.path.join(CLAUDEDEV, "D1_s1_copy.vi"),
              "3e3d23cefd3a334001aa9d6156bf1aee"),
             ("S2 D1_s2_loops", os.path.join(CLAUDEDEV, "D1_s2_loops.vi"),
              "6ff19497f2309e007a214660bb64b911"),
             ("ROW2 bed", os.path.join(CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi"),
              "26c54ff784cb5cea21edbd214d2cc3a0"),
             ("M3a-2", os.path.join(CLAUDEDEV, "D1_s3b_m3a2_20260922_023029.vi"),
              "3842f5e6f128226235dc78353f26ef44"))
DEFAULT_PINS = _PIN_SPEC

CENSUS_CLASSES = ("Diagram", "WhileLoop", "SubVI", "Wire", "LoopTunnel", "Local", "ControlTerminal",
                  "Node")


class Stop(Exception):
    """A FATAL gate. The stage stops; `close()` still runs the hygiene tail."""


# C6 RESULT LINE (docs/session-protocol.md, user-approved 2026-09-24). `Stage.summary()` prints
# `RESULT {"schema":"result-line/1",...}` as its LAST line, from its own gate counts; bgrun / guard_peer / the
# runner / audit_cycle read ONLY that line (their body scans are gone). The two exit paths summary() cannot see are
# covered here: an UNCAUGHT exception (excepthook -> RESULT FAIL at exit, first_fail = the exception text) and gates
# recorded AFTER the last summary (re-printed at exit). A Stage that never reached summary() and no exception ->
# nothing printed, the exit code decides (a helper-only import must not invent a verdict).
import atexit                                                                      # noqa: E402
import protocol as _protocol                                                       # noqa: E402

_C6 = {"stage": None, "sig": None, "exc": None}


def _c6_line(stage, extra_fail=None):
    n_fail = len(stage.fails) if stage is not None else 0
    n_pass = len(stage.passes) if stage is not None else 0
    first = extra_fail or (getattr(stage, "exc_text", None) if stage is not None else None) \
        or (stage.fails[0] if stage is not None and stage.fails else None)
    if extra_fail:
        n_fail += 1
    arts = []
    if stage is not None:
        sv = stage.R.get("saves") or {}
        if sv.get("md5") and os.path.exists(stage.work):
            arts = [{"path": stage.work, "md5": sv["md5"]}]
    return _protocol.result_line(_protocol.make_result(n_pass, n_fail, first, arts))


def _c6_excepthook(etype, value, tb, _orig=sys.excepthook):
    if not issubclass(etype, (SystemExit, KeyboardInterrupt)):
        _C6["exc"] = "{0}: {1}".format(etype.__name__, str(value))[:200]
    elif issubclass(etype, KeyboardInterrupt):
        _C6["exc"] = "KeyboardInterrupt"
    _orig(etype, value, tb)


def _c6_atexit():
    st = _C6["stage"]
    try:
        if _C6["exc"]:
            line = _c6_line(st, extra_fail=_C6["exc"])
        elif st is not None and _C6["sig"] is not None and _C6["sig"] != (len(st.passes), len(st.fails)):
            line = _c6_line(st)
        else:
            return
        sys.stdout.write(line + "\n")
        sys.stdout.flush()
    except Exception:                                                              # noqa: BLE001
        pass


sys.excepthook = _c6_excepthook
atexit.register(_c6_atexit)


def md5(path):
    """build_opfsinnertunnelconnect_v0.py:227 verbatim."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def version_bytes(path, n=1 << 16):
    """`19 00 80 00` = LV2019, `26 00 80 00` = LV2026 (CLAUDE.md rule 1) - diag_s2_scaffold.py:133-140."""
    import re
    with open(path, "rb") as f:
        head = f.read(n)
    return sorted({m.group(0)[0] for m in re.finditer(rb"(?s).\x00\x80\x00", head)})


def private_bytes():
    """LabVIEW's private bytes - the COMPANION of the handle count, which is blind to VI Server refnums
    (docs/toolkit-capabilities.md:484-485). build_opfsinnertunnelconnect_v0.py:270 verbatim."""
    try:
        r = subprocess.run(["powershell", "-NoProfile", "-Command",
                            "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1)"
                            ".PrivateMemorySize64"], capture_output=True, text=True, timeout=60)
        return int((r.stdout or "").strip() or 0)
    except Exception:                                                              # noqa: BLE001
        return None


_MODS = {}


def mod(name):
    """Lazy import of a heavy fleet module, so a no-LabVIEW self-test can import stagekit."""
    if name not in _MODS:
        _MODS[name] = importlib.import_module(name)
    return _MODS[name]


def _a(text):
    return str(text).encode("ascii", "replace").decode("ascii")


class Stage(object):
    """One build/diagnostic stage: pin, copy, edit, gate, save, clean up, report."""

    # ------------------------------------------------------------------ construction
    def __init__(self, input_vi, input_md5, name, fresh=True, work_name=None, pins=DEFAULT_PINS,
                 deadline_min=45.0, reserve_s=300.0, out_json=None, preload=True, work_dir=CLAUDEDEV,
                 task=""):
        self.input_vi = input_vi
        self.input_md5 = input_md5
        self.name = name
        self.fresh = fresh
        self.pins = tuple(pins or ())
        self.preload_original = preload
        self.deadline_s = float(deadline_min) * 60.0
        self.reserve_s = float(reserve_s)
        self.t0 = time.time()
        self.stamp = time.strftime("%Y%m%d_%H%M%S")
        self.work_dir = work_dir
        self.work = os.path.join(work_dir, work_name or "{0}_{1}.vi".format(name, self.stamp))
        self.out_json = out_json or os.path.join(BENCH, "{0}.json".format(name))
        self.passes, self.fails, self.facts, self.rows = [], [], [], []
        self.scratches = []
        self.planned_rows = []            # `plan_rows()`; NOT `self.rows`, which is the non-gate ROW record
        self.sym = {}                     # from_decision symbols: "$name" -> what an earlier row created
        self._rowcheck_done = False
        self._nodes = None
        self._preload = None
        self.started = False
        self.R = {"script": name, "stamp": self.stamp, "input": input_vi, "input_md5_pin": input_md5,
                  "work": self.work, "task": task, "no_vi_was_run": True,
                  "verification_level": "STRUCTURAL unless a gate says otherwise",
                  "es_timeline": [], "ops": [], "saves": {}, "H": {}}

    # ------------------------------------------------------------------ reporting primitives
    def head(self, text):
        print("\n---------- {0}".format(_a(text)), flush=True)

    def gate(self, label, ok, detail="", fatal=False):
        ok = bool(ok)
        (self.passes if ok else self.fails).append(label)
        print(_a("  {0}  {1}{2}".format("PASS" if ok else "FAIL", label,
                                        ("  " + str(detail)) if detail else "")), flush=True)
        if not ok and fatal:
            raise Stop(label)
        return ok

    def fact(self, line):
        self.facts.append(str(line))
        print(_a("  FACT  {0}".format(line)), flush=True)
        return line

    def row(self, label, observed, expected=None):
        """A NON-GATE record. Deliberately NOT at the start of the line, so a row reporting an expected
        FAIL cannot arm `guard_peer.FAILURE_RE` - the gate belongs to the comparison, not to the row."""
        rec = {"label": label, "observed": observed, "expected": expected}
        self.rows.append(rec)
        print(_a("  ROW   {0} : observed={1} expected={2}".format(label, observed, expected)), flush=True)
        return rec

    def safe(self, label, fn, default=None):
        try:
            return fn(), ""
        except Exception as e:                                                     # noqa: BLE001
            msg = "{0}: {1}".format(type(e).__name__, str(e)[:250])
            self.fact("{0} raised {1}".format(label, msg))
            return default, msg

    def left_s(self):
        return self.deadline_s - (time.time() - self.t0) - self.reserve_s

    def dump(self):
        self.R["gates"] = {"pass": len(self.passes), "fail": len(self.fails), "failing": self.fails}
        self.R["facts"] = self.facts
        self.R["rows"] = self.rows
        self.R["elapsed_s"] = round(time.time() - self.t0, 1)
        with open(self.out_json, "w", encoding="utf-8") as f:
            json.dump(self.R, f, indent=1, default=str)

    def summary(self):
        print("\n" + "=" * 100, flush=True)
        print("=== GATES: {0} pass / {1} fail{2}".format(
            len(self.passes), len(self.fails),
            ("; failing: " + ", ".join(self.fails)) if self.fails else ""), flush=True)
        print("JSON: {0}   elapsed {1:.1f} s".format(self.out_json, time.time() - self.t0), flush=True)
        _C6["stage"], _C6["sig"] = self, (len(self.passes), len(self.fails))
        print(_c6_line(self), flush=True)                  # C6: the RESULT line is the LAST line
        return 0 if not self.fails else 1

    # ------------------------------------------------------------------ start
    def file_facts(self, tag, path):
        rec = {"path": path, "exists": os.path.exists(path)}
        if rec["exists"]:
            rec["md5"], rec["size"] = md5(path), os.path.getsize(path)
            rec["version_bytes"] = version_bytes(path)
            self.fact("{0}: {1} md5 {2} size {3} B; version bytes {4}".format(
                tag, os.path.basename(path), rec["md5"], rec["size"], rec["version_bytes"]))
        else:
            self.fact("{0}: {1} IS NOT ON DISK".format(tag, os.path.basename(path)))
        return rec

    def pin_check(self, when):
        """Every md5 pin, reported one per line. Returns True iff all hold."""
        allok, seen = True, {}
        for label, path, want in self.pins:
            have = md5(path) if os.path.exists(path) else "MISSING"
            seen[label] = have
            allok = allok and (have == want)
            self.fact("PIN {0:<6} {1:<16} {2}  (want {3}) {4}".format(
                when, label, have, want, "OK" if have == want else "DIFFERS"))
        self.R["pins_" + when.lower()] = seen
        return allok

    def restart(self):
        """Standing restart authority (CLAUDE.md 3). diag_s2_scaffold.fresh:155."""
        bp = mod("bench_prep")
        before, _ = self.safe("handles before restart", bp.labview_handles)
        self.R["H"]["handles_before_restart"] = before
        self.fact("LabVIEW handle count BEFORE the restart: {0!r}".format(before))
        self.safe("restart_labview", bp.restart_labview)
        g.reset()
        time.sleep(3.0)
        after, _ = self.safe("handles after restart", bp.labview_handles)
        self.R["H"]["handles_after_restart"] = after
        self.fact("LabVIEW handle count AFTER the restart: {0!r}".format(after))

    def start(self):
        """FILES ONLY -> restart -> Preload the ORIGINAL read-only -> the dated WORK copy -> open it."""
        self.head("[0] FILES ONLY - the input's md5, the pins, the claudeDev listing")
        # THE LISTING IS TAKEN FIRST, before any fatal gate: a start() that STOPS at a pin used to leave
        # `claudedev_before` unset, and close()'s H6 then read every file in claudeDev as "added".
        self.R["claudedev_before"] = sorted(os.path.basename(p)
                                            for p in glob.glob(os.path.join(CLAUDEDEV, "*.vi")))
        self.fact("claudeDev holds {0} .vi file(s) BEFORE the run".format(len(self.R["claudedev_before"])))
        got = md5(self.input_vi) if os.path.exists(self.input_vi) else "MISSING"
        self.R["input_md5_before"] = got
        self.gate("K1 input md5 == {0}".format(self.input_md5), got == self.input_md5,
                  "got {0}".format(got), fatal=True)
        self.pin_check("BEFORE")
        # The detail carries the HASH **and** the path: a gate that prints only the path cannot tell
        # "absent" from "present with the wrong bytes" (the c87 review's §2, accepted).
        orig = md5(ORIGINAL) if os.path.exists(ORIGINAL) else "MISSING - no such file"
        self.gate("K2 the ORIGINAL's md5 is {0}".format(ORIG_MD5), orig == ORIG_MD5,
                  "got {0} at {1}".format(orig, ORIGINAL), fatal=True)
        if self.fresh:
            self.head("[1] RESTART LabVIEW (standing authority; fresh ~31,500 handles)")
            self.restart()
        if self.preload_original:
            self._preload_enter()
        self.head("[2] THE DATED WORK COPY under claudeDev - the input is never opened for writing")
        shutil.copyfile(self.input_vi, self.work)
        time.sleep(0.4)
        self.gate("K3 the work copy is byte-identical to the input",
                  md5(self.work) == got, os.path.basename(self.work), fatal=True)
        self.safe("ensure_loaded(work)", lambda: g.ensure_loaded(self.work))
        self.es("after open")
        self.started = True
        self.dump()
        return self.work

    def _preload_enter(self):
        """The established trick: the ORIGINAL resident READ-ONLY so the copy's subVI links resolve
        without a relink pass. Nothing is opened, nothing is saved (diag_s2_scaffold.Preload:167)."""
        try:
            import pythoncom
            from win32com.client import dynamic
            pythoncom.CoInitialize()
            app = dynamic.Dispatch("LabVIEW.Application")
            vi = app.GetVIReference(ORIGINAL, "", False, 0)
            self._preload = (app, vi)
            self.fact("PRELOAD: the ORIGINAL is resident READ-ONLY (LabVIEW {0}), its own ExecState {1}; "
                      "nothing opened, nothing saved".format(app.Version, int(vi.ExecState)))
        except Exception as e:                                                     # noqa: BLE001
            self.fact("PRELOAD FAILED ({0}: {1}) - continuing without it".format(type(e).__name__,
                                                                                str(e)[:160]))

    def _preload_exit(self):
        if self._preload:
            self._preload = None
            self.fact("PRELOAD references released; refs {0!r}".format(g.ref_counts()))

    # ------------------------------------------------------------------ readings
    def es(self, tag, target=None):
        """One ExecState reading, appended to the timeline. RECORDED; a criterion only where a gate says
        so (the D1 beds are broken BY DESIGN - Pre-decided 89/97)."""
        t = target or self.work
        v, err = self.safe("exec_state({0})".format(tag), lambda: g.exec_state(t))
        self.R["es_timeline"].append({"tag": tag, "target": os.path.basename(t), "exec_state": v,
                                      "t": round(time.time() - self.t0, 1), "err": err})
        self.fact("ExecState [{0}] {1} = {2!r}".format(tag, os.path.basename(t), v))
        return v

    def count(self, cls, target=None):
        return g.count(target or self.work, cls)

    def census(self, classes=CENSUS_CLASSES, tag="", target=None):
        """A class census by NAME, never by index - the numbers a stage's counts gate on."""
        t = target or self.work
        out = {}
        for c in classes:
            v, _e = self.safe("count({0})".format(c), lambda cc=c: g.count(t, cc))
            out[c] = v
        self.fact("CENSUS {0} {1}: {2!r}".format(tag, os.path.basename(t), out))
        self.R.setdefault("censuses", []).append({"tag": tag, "target": os.path.basename(t),
                                                  "counts": out})
        return out

    def uid_index(self, cls, uid, target=None):
        """The traverse index of `uid` RE-READ at the call site - never cached across a mutation (34(h))."""
        order = [o["uid"] for o in g.report_all(target or self.work, cls)]
        return order.index(uid) if uid in order else None

    def wired_terminals(self, uid, hints=(), target=None, tag=""):
        """Every terminal row of node #uid with its wire - `build_d1_m3a1.node_view`:572, which finds the
        node by uid across diagrams and prints the full table. Returns (location, rows)."""
        M = mod("build_d1_m3a1")
        t = target or self.work
        loc, rows = M.node_view(t, uid, list(hints), tag or "#{0}".format(uid))
        wired = [r for r in (rows or []) if r.get("has_wire")]
        self.fact("#{0}: {1} terminal(s), {2} WIRED".format(uid, len(rows or []), len(wired)))
        return loc, (rows or [])

    def net_sources(self, wire_uid, n=8, target=None, tag=""):
        """THE OWNER-IDENTITY READING (build_d1_m3a3b_d3.py:589-600). `OpWireSource_v5` is WIRE-addressed -
        a terminal is named by the wire it carries - and every row carries its own error columns, so an
        unresolvable uid yields no owner instead of the previous call's answer."""
        M = mod("build_d1_m3a1")
        W = mod("build_opconnectfromwire_v0").wire_source_owner
        t = target or self.work
        tag = tag or "w{0}".format(wire_uid)
        walk, err = self.safe("{0} OpWireSource_v5".format(tag),
                              lambda: W(t, int(wire_uid), n=n) if wire_uid else [], [])
        M.print_walk(tag, wire_uid, walk, err)
        bad = M.pd85_violations(wire_uid, walk) if wire_uid else ["no wire"]
        owners = sorted({(str(x.get("owner_class")), int(x.get("owner_uid")))
                         for x in (walk or []) if x.get("owner_uid")})
        srcs = sorted({(str(x.get("owner_class")), int(x.get("owner_uid")))
                       for x in (walk or []) if x.get("is_source") and x.get("owner_uid")})
        out = {"wire": wire_uid, "walk": walk, "err": err, "source_owners": srcs, "all_owners": owners,
               "pd85_violations": len(bad), "pd85": bad}
        self.fact("NET w{0}: source-terminal owners {1!r} ; every owner {2!r} ; PD85 {3}".format(
            wire_uid, srcs, owners, len(bad)))
        self.R.setdefault("nets", []).append({k: out[k] for k in
                                              ("wire", "source_owners", "all_owners",
                                               "pd85_violations", "err")})
        return out

    def broken_wire_count(self, target=None, allow_mutation=False, tag=""):
        """THE DIAGRAM-WIDE BROKEN-WIRE COUNT (build_d1_m3a3b_d3.bad_wire_count:265). ⚠️ IT MUTATES -
        `remove_bad_wires_scripted` runs LabVIEW's own Remove Bad Wires (VI method 410) and DELETES - so it
        refuses the stage target unless the caller states `allow_mutation=True`; on a scratch about to be
        discarded it is free."""
        t = target or self.work
        if t == self.work and not allow_mutation:
            raise Stop("broken_wire_count on the STAGE TARGET deletes wires - pass allow_mutation=True or "
                       "a scratch (stagekit rule 6)")
        before = g.count(t, "Wire")
        after, es = g.remove_bad_wires_scripted(t)
        n = before - after
        self.fact("{0} BROKEN-WIRE COUNT: Wire {1} -> {2} after Remove Bad Wires = {3} bad wire(s); "
                  "ExecState after {4!r}".format(tag, before, after, n, es))
        return {"bad": n, "wires_before": before, "wires_after": after, "exec_state": es}

    # ------------------------------------------------------------------ scratch copies
    def scratch(self, suffix, source=None):
        """A dated scratch COPY (unique per run, deleted by `close()`) - the only surface a mutating
        measurement is allowed to touch."""
        src = source or self.input_vi
        p = os.path.join(CLAUDEDEV, "{0}_{1}_{2}.vi".format(self.name[:18], self.stamp, suffix))
        shutil.copyfile(src, p)
        time.sleep(0.4)
        self.scratches.append(p)
        self.gate("SC {0} is a byte-identical copy of {1}".format(os.path.basename(p),
                                                                  os.path.basename(src)),
                  md5(p) == md5(src), os.path.basename(p), fatal=True)
        self.safe("ensure_loaded({0})".format(suffix), lambda: g.ensure_loaded(p))
        return p

    def drop_scratch(self, path, tag="H4"):
        """Close and DELETE one scratch now (a diagnostic that runs several cells must not hold them all
        open). Retries, because LabVIEW can still hold the file for a moment."""
        self.safe("close_panel({0})".format(os.path.basename(path)), lambda: g.close_panel(path))
        for _a2 in range(6):
            if not os.path.exists(path):
                break
            try:
                os.remove(path)
            except Exception as e:                                                 # noqa: BLE001
                self.fact("delete {0} failed: {1}".format(os.path.basename(path), str(e)[:110]))
                time.sleep(3.0)
        ok = not os.path.exists(path)
        if path in self.scratches:
            self.scratches.remove(path)
        self.gate("{0} scratch deleted: {1}".format(tag, os.path.basename(path)), ok, path)
        return ok

    def discard_work(self):
        """THIS STAGE SAVES NOTHING: the dated work copy is treated as a scratch, so `close()` deletes it
        and the files-left-on-disk gate expects []. A diagnostic must leave no artefact behind."""
        if self.work not in self.scratches:
            self.scratches.append(self.work)
        self.fact("THE WORK COPY IS A SCRATCH: this stage saves nothing, so {0} is deleted at close".format(
            os.path.basename(self.work)))
        return self.work

    # ------------------------------------------------------------------ planned rows (Jev row check, #5)
    def plan_rows(self, rows, tag=""):
        """DECLARE this stage's planned re-wiring rows: (source uid/terminal) -> (sink uid/terminal).

        The rows are judged ONCE, by `tools/jev_rowcheck.py`, against this project's own measured terminal
        tables, and the verdicts print as `JEV-ROWCHECK | <stage> | <row> | <class> p=<p>` - one line per row
        here and in `tools/bench/jev_gate.log`. Two row schemas are accepted; `jev_rowcheck.normalise_row`'s
        docstring is the contract, and a row matching neither reads `unknown`, never `ok`.

        ADVISORY, BY CONSTRUCTION (docs/jev-integration-plan.md 2nd wave #5; measured 62.5 % on 40 labelled
        rows, which is a signal, not a verdict): nothing here refuses a row, changes a gate, or raises. No key,
        no network or a malformed row is a printed line and nothing else.

        THE CALL IS LAZY - it fires from `_op`, immediately BEFORE the stage's first mutating verb, wherever in
        the file the rows were declared. A stage that declares rows and then mutates nothing spends nothing."""
        try:
            self.planned_rows = list(rows or [])
        except TypeError:
            self.planned_rows = []
        self._rowcheck_done = False
        self.R["planned_rows"] = len(self.planned_rows)
        self.fact("PLANNED RE-WIRING ROWS declared: {0}{1}".format(
            len(self.planned_rows), ("  [" + str(tag) + "]") if tag else ""))
        return self.planned_rows

    def _rowcheck(self):
        """Fire the planned-row advisory once. EVERYTHING is caught: this may never affect a build."""
        if self._rowcheck_done or not self.planned_rows:
            return []
        self._rowcheck_done = True
        try:
            import jev_rowcheck
            lines = jev_rowcheck.stage_lines(self.planned_rows, self.name,
                                             budget_s=min(60.0, max(5.0, self.left_s())))
        except Exception as e:                                                     # noqa: BLE001
            print(_a("  JEV-ROWCHECK | {0} | - | unavailable ({1})".format(
                self.name, type(e).__name__)), flush=True)
            return []
        for ln in lines:
            print(_a("  " + ln), flush=True)
        self.R["jev_rowcheck"] = lines
        return lines

    # ------------------------------------------------------------------ edit verbs (thin wrappers)
    def _op(self, verb, fn, detail=""):
        """Run one mutator, record its error column, mark the node census for a later junk purge."""
        self._rowcheck()          # ADVISORY, once, before the first mutation (docs/jev-integration-plan.md #5)
        self.node_mark(verb)
        t0 = time.time()
        res, err = self.safe("{0} {1}".format(verb, detail), fn)
        rec = {"verb": verb, "detail": detail, "err": err, "result": res,
               "s": round(time.time() - t0, 1)}
        self.R["ops"].append(rec)
        self.fact("OP {0} {1} -> err {2!r} ({3:.1f} s)".format(verb, detail, err, rec["s"]))
        return rec

    def node_mark(self, tag=""):
        """The Node census BEFORE a mutation - `junk_purge()` diffs against the last mark."""
        M = mod("build_d1_m3a1")
        nodes, _e = self.safe("node_census({0})".format(tag), lambda: M.node_census(self.work, tag)[0], [])
        self._nodes = nodes
        return nodes

    def junk_purge(self, tag="", hints=()):
        """THE MEASURED PURGE (build_opfsinnertunnelconnect_v0.purge_junk:288): the OpConnect* family mints
        1.00 stray `Invoke` per call, and a node with ZERO wired terminals is the only shape deleted -
        anything else new is REPORTED VERBATIM and LEFT ALONE."""
        C82 = mod("build_opfsinnertunnelconnect_v0")
        if self._nodes is None:
            self.node_mark(tag)
            return {"skipped": "no census mark existed; one was taken now"}
        final, rec = C82.purge_junk(self.work, self._nodes, tag or self.name, list(hints))
        self._nodes = final
        self.R.setdefault("purges", []).append(rec)
        return rec

    def delete_wire(self, wire_uid, tag=""):
        """build_opfsinnertunnelconnect_v0.del_wire:336 - by uid, via the LIVE traverse order."""
        C82 = mod("build_opfsinnertunnelconnect_v0")
        return self._op("delete_wire", lambda: C82.del_wire(self.work, wire_uid, tag),
                        "w{0}".format(wire_uid))

    def delete_object(self, cls, uid, tag=""):
        """build_opfsinnertunnelconnect_v0.del_node:346 - uid -> live index -> `g.delete_object`."""
        C82 = mod("build_opfsinnertunnelconnect_v0")
        return self._op("delete_object", lambda: C82.del_node(self.work, cls, uid, tag),
                        "{0} #{1}".format(cls, uid))

    def move_in(self, uid, dest_diagram_index, position):
        """build_d1_v0.move_in:318 - move an object INTO a nested diagram by uid."""
        B = mod("build_d1_v0")
        return self._op("move_in", lambda: B.move_in(self.work, uid, dest_diagram_index, position),
                        "#{0} -> Diagram[{1}] at {2}".format(uid, dest_diagram_index, position))

    def connect(self, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels=None):
        """gscript.connect_nested_v2:2965 = `OpConnectNested_v2` - the nested-diagram writer."""
        return self._op("connect", lambda: g.connect_nested_v2(self.work, sink_diag, sink_node, sink_term,
                                                               src_diag, src_node, src_term, labels),
                        "sink D[{0}].N[{1}].t{2} <- src D[{3}].N[{4}].t{5}".format(
                            sink_diag, sink_node, sink_term, src_diag, src_node, src_term))

    def connect_from_wire(self, sink_diag, sink_node, sink_term, wire_uid, wire_term_index, labels=None):
        """`OpConnectFromWire_v0` - the only writer whose SOURCE need not be a node
        (docs/toolkit-capabilities.md:70). `build_opconnectfromwire_v0.connect_from_wire`:381, whose own
        argument order is (target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels); the
        label map defaults to the op's own `tools/bench/opconnectfromwire_v0_labels.json`."""
        F = mod("build_opconnectfromwire_v0")
        lab = labels or json.load(open(F.MAP_OUT, encoding="utf-8"))
        return self._op("connect_from_wire",
                        lambda: F.connect_from_wire(self.work, wire_uid, wire_term_index, sink_diag,
                                                    sink_node, sink_term, lab),
                        "sink D[{0}].N[{1}].t{2} <- w{3}[{4}]".format(sink_diag, sink_node, sink_term,
                                                                      wire_uid, wire_term_index))

    def fs_inner_tunnel_connect(self, fsit_uid, sink_diag, sink_node, sink_term, auto_route=None,
                                target=None, op=None):
        """`OpFsInnerTunnelConnect_v1` (build_d1_m3a3b_d3.fsit_call:279, the POISONED caller of Pre-decided
        125). Connects a source terminal addressed by INDEX TRIPLE to a `FlatSequenceInnerTunnel`'s
        terminal addressed by UID. Returns the op's full readout dict incl. every error column."""
        D3 = mod("build_d1_m3a3b_d3")
        t = target or self.work
        op_path = op or D3.OP1
        labels = json.load(open(D3.MAP_OUT, encoding="utf-8"))
        self.node_mark("fsit_connect")
        r, err = self.safe("fs_inner_tunnel_connect #{0}".format(fsit_uid),
                           lambda: D3.fsit_call(op_path, labels, t, fsit_uid, sink_diag, sink_node,
                                                sink_term, auto_route=auto_route), {})
        r = r or {}
        r["wrapper_err"] = err
        self.R["ops"].append({"verb": "fs_inner_tunnel_connect", "op": os.path.basename(op_path),
                              "fsit_uid": fsit_uid, "triple": [sink_diag, sink_node, sink_term],
                              "err": r.get("err"), "invoke_err": r.get("invoke_err"),
                              "term_uid": r.get("term_uid"), "uid_back": r.get("uid_back"),
                              "sink_wire_uid": r.get("sink_wire_uid"), "is_broken": r.get("is_broken"),
                              "wire_delta": r.get("wire_delta"), "wrapper_err": err})
        self.fact("OP fs_inner_tunnel_connect(#{0}) -> op_err={1!r} invoke_err={2!r} term_uid={3!r} "
                  "uid_back={4!r} UID2={5!r} wire_delta={6!r} is_broken={7!r}".format(
                      fsit_uid, r.get("err"), r.get("invoke_err"), r.get("term_uid"), r.get("uid_back"),
                      r.get("sink_wire_uid"), r.get("wire_delta"), r.get("is_broken")))
        return r

    def fs_inner_tunnel_read(self, fsit_uid, target=None, tag=""):
        """`OpFsInnerTunnelTerm_v0` - the FSIT's two faces, read-only (build_d1_m3a3b_d3.fsit_read:342)."""
        D3 = mod("build_d1_m3a3b_d3")
        r, _e = self.safe("fsit_read #{0}".format(fsit_uid),
                          lambda: D3.fsit_read(target or self.work, fsit_uid, tag or self.name))
        return r or {}

    def wire_indicators(self, node_index, src_terms, indicator_names, diagram_index=0,
                        node_class="SubVI"):
        """gscript.wire_indicators:1786 - branch a node's outputs onto front-panel indicators."""
        return self._op("wire_indicators",
                        lambda: g.wire_indicators(self.work, node_index, list(src_terms),
                                                  list(indicator_names), diagram_index=diagram_index,
                                                  node_class=node_class),
                        "N[{0}] {1} -> {2}".format(node_index, list(src_terms), list(indicator_names)))

    def add_shift_reg(self, loop_index, y_position=120, class_name="WhileLoop"):
        """gscript.add_shift_reg:687."""
        return self._op("add_shift_reg",
                        lambda: g.add_shift_reg(self.work, loop_index, y_position, class_name),
                        "loop[{0}] y={1}".format(loop_index, y_position))

    def wire_sr(self, variant, loop_index, reg_index, **kw):
        """gscript.wire_sr:737."""
        return self._op("wire_sr",
                        lambda: g.wire_sr(variant, self.work, loop_index, reg_index, **kw),
                        "{0} loop[{1}] reg[{2}] {3!r}".format(variant, loop_index, reg_index, kw))

    def create_local_read(self, label, panel_index=None, tag=""):
        """The BUILT local-variable creator. Its measured implementation lives in the diagnostics that
        proved it (`tools/bench/diag_s3b_l0_localname_v2.create_local`:964 - label + panel index); this is
        a thin binding to THAT function, never a re-implementation."""
        L = mod("diag_s3b_l0_localname_v2")
        return self._op("create_local_read",
                        lambda: L.create_local(self.work, label, panel_index, tag or self.name),
                        "{0!r} panel[{1}]".format(label, panel_index))

    # ------------------------------------------------------------------ the ordered second pass
    def expect_is_broken_false(self, label, reconnect, wire_uid=None):
        """42(b): THE ORDERED SECOND PASS. The acceptance is asserted on a SEPARATE, idempotent re-connect,
        never in the pass that made the connection (build_d1_m3a3.phase_second_pass:1374, Pre-decided 94):
        `wire_delta` must be 0 because the connection already exists, and the op's own `Wire.Is Broken?`
        6371004 readback must be False. `reconnect` is a callable that RE-RESOLVES its endpoints and
        re-issues the connect - nothing is carried across the mutation (the T2c2 lesson)."""
        w0 = self.count("Wire")
        r = reconnect() or {}
        w1 = self.count("Wire")
        delta = w1 - w0
        ib = r.get("is_broken")
        same = (wire_uid is None) or (r.get("sink_wire_uid") == wire_uid)
        self.fact("{0} ORDERED SECOND PASS: Wire {1} -> {2} (delta {3}); op err {4!r}; `UID 2` {5!r}; "
                  "`Is Broken?` {6!r}".format(label, w0, w1, delta, r.get("err"),
                                              r.get("sink_wire_uid"), ib))
        a = self.gate("{0} wire_delta 0 on the ordered idempotent second pass (Pre-decided 94)".format(
            label), delta == 0, "wire_delta {0!r}".format(delta))
        b = self.gate("{0} `Wire.Is Broken?` 6371004 reads False on the SEPARATE ORDERED pass "
                      "(42(b))".format(label), ib is False and same,
                      "Is Broken? {0!r} ; `UID 2` {1!r} vs wire {2!r} (same {3!r})".format(
                          ib, r.get("sink_wire_uid"), wire_uid, same))
        return {"wire_delta": delta, "is_broken": ib, "pass": bool(a and b), "readout": r}

    # ------------------------------------------------------------------ decision record -> edits (plan step 6)
    STRUCTS = ("CaseStructure", "WhileLoop", "ForLoop", "TimedLoop", "EventStructure", "FlatSequence",
               "StackedSequence")

    def address(self, end, is_source, objs=None):
        """A terminal named by (node uid, terminal name, frame diagram uid) -> the LIVE index triple
        (Diagram idx, Nodes[] idx, Terminals[] idx), every index read off the machine just before use and the
        node's uid ECHOED back. A Selector/Loop tunnel's OUTER terminal is addressed as a terminal of its
        STRUCTURE node, found by GEOMETRY (a structure on the same diagram at the tunnel's left x, or the nearest
        structure up-left of it) - a HEURISTIC, reported in the returned `how`, and made safe by requiring the
        name to resolve to exactly one terminal of the right direction on that structure."""
        t = self.work
        uid, how = int(end["uid"]), "node"
        diags = g.report_all(t, "Diagram")
        didx = next((d["i"] for d in diags if int(d["uid"]) == int(end["diagram"])), None)
        if didx is None:
            raise RuntimeError("diagram #{0} not in report_all('Diagram')".format(end["diagram"]))
        labels = g.node_labels(t, didx)
        uids = [r["uid"] for r in labels]
        if end["owner_class"] in ("SelectorTunnel", "Tunnel", "LoopTunnel") and end["term_class"] == "OuterTerminal":
            pos = dict((o["uid"], (o["pos"], o["class"])) for o in (objs or []))
            tp = pos[uid][0]
            cands = [u for u in uids if pos.get(u, (None, ""))[1] in self.STRUCTS]
            left = [u for u in cands if pos[u][0][0] == tp[0] and pos[u][0][1] <= tp[1]]
            upl = sorted((u for u in cands if pos[u][0][0] <= tp[0] and pos[u][0][1] <= tp[1]),
                         key=lambda u: (-pos[u][0][0], -pos[u][0][1]))
            pick = left or upl[:1]
            if not pick:
                raise RuntimeError("no structure found for tunnel #{0}".format(uid))
            uid, how = pick[0], "structure #{0} of tunnel #{1} (geometry: {2})".format(
                pick[0], end["uid"], "left edge x" if left else "nearest up-left")
        if uid not in uids:
            raise RuntimeError("#{0} not in Diagram[{1}].Nodes[]".format(uid, didx))
        nidx = uids.index(uid)
        echo, rows = g.node_terms_uid(t, didx, nidx)
        if echo != uid:
            raise RuntimeError("uid echo {0!r} != #{1}".format(echo, uid))
        # Pre-decided 173 + 174 (cycle 72 firefighter): ONLY the staged field `verify_term_uid` selects the uid path.
        # Candidate ends from jev_candidates carry `term_uid` at FIRST wiring, when the terminal is still unwired,
        # and r2 (stage_d1_l7_1b_r2.log:41-45) died because that field switched the branch. `term_uid` is ignored
        # here; the second pass / Is Broken? / gates set `verify_term_uid` after the wire has landed.
        if end.get("verify_term_uid"):
            ti, _a = match_term_uid(end["verify_term_uid"], mod("allterms").read_terms(t)[0], rows, is_source)
            return (didx, nidx, ti), "{0}; terminal by uid #{1} (wire {2})".format(how, end["verify_term_uid"], _a["wire_uid"])
        hits = [r for r in rows if r["name"] == end["term"] and bool(r["is_source"]) == bool(is_source)]
        if len(hits) > 1:
            hits = [r for r in hits if not r["wire"]]
        if len(hits) != 1:
            raise RuntimeError("terminal {0!r} ({1}) on #{2}: {3} matches".format(
                end["term"], "source" if is_source else "sink", uid, len(hits)))
        return (didx, nidx, int(hits[0]["i"])), how

    # ------------------------------------------------------------------ creator rows (cycle 68, M4a/M4b)
    def resolve(self, v):
        """`$name` / `$name.key` -> self.sym; `$wire_of:<uid>:<term i>` -> that terminal's LIVE wire uid (read now,
        never carried). Lists and dicts are resolved recursively; anything else is returned unchanged."""
        if isinstance(v, dict):
            return dict((k, self.resolve(x)) for k, x in v.items())
        if isinstance(v, list):
            return [self.resolve(x) for x in v]
        if not (isinstance(v, str) and v.startswith("$")):
            return v
        if v.startswith("$wire_of:"):
            _w, uid, ti = v.split(":")
            _loc, rows = self.wired_terminals(int(uid), tag="resolve {0}".format(v))
            return int([r for r in rows if int(r["i"]) == int(ti)][0]["wire"])
        name, _dot, key = v[1:].partition(".")
        x = self.sym[name]
        return x[key] if key else x

    def copy_in(self, cls, uid, dest_diagram_uid, position, tag=""):
        """COPY a primitive that already exists on the donor into Diagram #dest by `OpMoveByIndex_v0` (the op of
        `gscript.copy_by_index`, duplicate=True, UID guard) + `move_in` + junk purge. PRECONDITION (the op is
        hard-wired to the NI Moving-Objects pair): `self.work` IS `g.MOVE_DST` and `g.MOVE_SRC` holds the donor's
        bytes - the stage file arranges both. copy_by_index itself is not called because it saves and file-copies
        the Target, which a stage that has more rows to execute must not do. Returns the new node's uid."""
        if os.path.normcase(self.work) != os.path.normcase(g.MOVE_DST):
            raise Stop("copy_in needs work == gscript.MOVE_DST (got {0})".format(self.work))
        order = [int(o["uid"]) for o in g.report_all(g.MOVE_SRC, cls)]
        idx = order.index(int(uid))
        before = set(int(o["uid"]) for o in g.report_all(self.work, cls))

        def _copy():
            lab = json.load(open(os.path.join(BENCH, "opmovebyindex_labels.json"), encoding="utf-8"))
            vi = g.op(g.OP_MOVE_INDEX)
            vi.SetControlValue(lab["class_name"], cls)
            vi.SetControlValue(lab["index"], int(idx))
            vi.SetControlValue(lab["duplicate"], True)
            vi.SetControlValue(lab["traverse_target"], 1)
            g._run(vi)
            return int(vi.GetControlValue(lab["selected_uid"]))
        rec = self._op("copy_in", _copy, "{0}[{1}] #{2}".format(cls, idx, uid))
        if rec["result"] != int(uid):
            raise Stop("copy_in UID guard: selected {0!r} != #{1}".format(rec["result"], uid))
        new = sorted(set(int(o["uid"]) for o in g.report_all(self.work, cls)) - before)
        self.fact("COPY #{0} -> new {1} uid(s) {2!r}".format(uid, cls, new))
        if len(new) != 1:
            raise Stop("copy_in: {0} new {1} object(s), expected 1: {2!r}".format(len(new), cls, new))
        self.junk_purge("{0} after copy".format(tag))
        di = [int(o["uid"]) for o in g.report_all(self.work, "Diagram")].index(int(dest_diagram_uid))
        self.move_in(new[0], di, tuple(position))
        self.junk_purge("{0} after move_in".format(tag), hints=[di, 0])
        return new[0]

    def add_sr_row(self, ex, tag=""):
        """`add_shift_reg` on the loop named by uid, then the register PAIR read back by index: {right, left, k,
        right_uids, loop_index}."""
        cls = ex.get("loop_class", "WhileLoop")
        li = self.uid_index(cls, int(ex["loop_uid"]))
        rec = self.add_shift_reg(li, class_name=cls)
        right = rec["result"]
        rights = []
        for k in range(12):
            u = g.shift_reg(self.work, li, k, class_name=cls).get("uid")
            if u is None:
                break
            rights.append(int(u))
        k = rights.index(int(right))
        left = g.shift_reg_left(self.work, li, k, class_name=cls)["left"]["uid"]
        self.junk_purge("{0} after add_shift_reg".format(tag))
        out = {"right": int(right), "left": int(left), "k": k, "right_uids": rights, "loop_index": li}
        self.fact("SHIFT REGISTER on {0} #{1}: {2!r}".format(cls, ex["loop_uid"], out))
        return out

    def const_row(self, ex, tag=""):
        """`OpCreateConstOnTerm_v0` (`build_opcreateconstonterm_v0.create_const_on_term`:364): a constant TYPED BY
        THE SINK and already wired, on a node of a WhileLoop BODY. exec {loop_uid, body_diagram, node, term,
        value}. Returns the op's {err, inv_err, created_uid}."""
        C = mod("build_opcreateconstonterm_v0")
        lab = json.load(open(os.path.join(BENCH, "opcreateconstonterm_labels.json"), encoding="utf-8"))
        li = self.uid_index("WhileLoop", int(ex["loop_uid"]))
        (_d, n, t), _how = self.address({"uid": ex["node"], "term": ex["term"], "diagram": ex["body_diagram"],
                                         "owner_class": "", "term_class": ""}, False)
        rec = self._op("create_const_on_term",
                       lambda: C.create_const_on_term(self.work, li, n, t, lab, value=ex.get("value")),
                       "loop[{0}] N[{1}].t{2} value {3!r}".format(li, n, t, ex.get("value")))
        self.junk_purge("{0} after const".format(tag))
        return rec

    def cfw_second_pass(self, src_uid, dst):
        """42(b)'s ordered idempotent second pass through `OpConnectFromWire_v0`, usable for ANY new wire whose sink
        is a Nodes[] terminal: the source is src_uid's terminal on the sink's CURRENT wire (read live), so the
        re-connect must add no wire and read back `Wire.Is Broken?`. Feed it to `expect_is_broken_false`."""
        F = mod("build_opconnectfromwire_v0")
        (dd, dn, dt), _h = self.address(dst, False)       # dst["verify_term_uid"] set => by uid (Pre-decided 173/174)
        self.fact("2nd-pass sink addressed: {0}".format(_h))
        self.wired_terminals(dst["uid"], tag="2nd-pass sink")                     # the printed table, evidence only
        w = int([r for r in g.node_terms(self.work, dd, dn) if int(r["i"]) == dt][0]["wire"])
        hit = [x for x in F.wire_source_owner(self.work, w, n=8)
               if x.get("owner_uid") == int(src_uid) and x.get("is_source")]
        self.node_mark("2nd pass")
        dw, es, err, sub = F.connect_from_wire(self.work, w, int(hit[0]["i"]), dd, dn, dt,
                                               json.load(open(F.MAP_OUT, encoding="utf-8")))
        self.junk_purge("2nd pass purge", hints=[dd, 0])
        return {"is_broken": (sub or {}).get("Is Broken?"), "sink_wire_uid": (sub or {}).get("UID 2"), "err": err,
                "wire": w, "wire_delta_op": dw}

    def live_graph(self, path, retired_rights=(), extra_rights=None):
        """The step-4 graph of a LIVE file (stage_d1_m3a4.py:104-110's recipe): wiki_build.read_live + the bed's
        loop table with `retired_rights` dropped and `extra_rights` {loop_uid: [right uid, ...]} appended, flat-
        sequence faces reused from the rowD wiki (a wire edit never touches them)."""
        W, JC = mod("wiki_build"), mod("jev_candidates")
        Gr = JC.load(JC.BED_KEY)
        ex = extra_rights or {}
        loops = [dict(l, right_uids=[u for u in l["right_uids"] if u not in set(retired_rights)] +
                      list(ex.get(l["loop_uid"], [])))
                 for l in json.load(open(JC._newest("graph_loops_bed_*.json"), encoding="utf-8"))["loops"]]
        lv = W.read_live(path, fs_pairs=Gr["wiki"]["fs_tunnel_pairs"])
        self.fact("LIVE MAP {0}: {1}".format(os.path.basename(path), lv["secs"]))
        return JC.from_parts({"terminals": lv["terminals"], "graph_summary": Gr["wiki"]["graph_summary"]},
                             lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"],
                             os.path.basename(path))

    def rule_check(self, d):
        """PRE-DECIDED 143: the op the row names must be the op `jev_pairs.op_rule` names for its classes, unless
        the row carries `op_override` (a reason). Returns (rule_op, rule_variant, why)."""
        import jev_pairs
        ex = d["exec"]
        c = {"src": dict(ex["src"]), "dst": dict(ex["dst"])}
        op, var, why = jev_pairs.op_rule(c)
        if (op, var) != (d.get("op"), d.get("variant")) and not d.get("op_override"):
            raise RuntimeError("op_rule says {0}/{1} ({2}); row says {3}/{4}".format(op, var, why, d.get("op"),
                                                                                  d.get("variant")))
        return op, var, why

    def from_decision(self, record, tag="fd"):
        """PLAN STEP 6 / Pre-decided 142-143: execute a decision record (tools/jev_pairs.write_record shape).
        action 'wire'   -> the row's `op` (connect_nested | connect_terminals | wire_sr | connect_from_wire |
                           fs_inner_tunnel_connect) on the `exec` ends {uid, term, term_class, owner_class, diagram};
                           wire_sr also needs exec.sr {loop_uid, loop_class, right_uid, right_uids}. The op is
                           checked against `jev_pairs.op_rule` first (`rule_check`); `es_probe` reads ExecState
                           right after the connect, after 2 s, and after the purge (review c68-p6d §4).
        action 'delete' -> exec.wire_uid is deleted; 'retire' -> exec {class, uid} is deleted.
        action 'copy' -> `copy_in` (exec {cls, uid, dest_diagram, pos}); 'add_shift_reg' -> `add_sr_row`;
        'create_const_on_term' -> `const_row`. A row with `as` stores its result in self.sym for later `$` refs.
        'llm' / 'skip' / anything else -> REPORTED, never executed. Every mutation goes through `_op`, so the node
        census is marked and the measured junk `Invoke` is purged after it. Returns one dict per decision."""
        objs = [dict(o, pos=tuple(o["pos"])) for o in g.report_all(self.work, "GObject")]
        out = []
        for i, d0 in enumerate(record.get("decisions", [])):
            row = {"i": i, "row_key": d0.get("row_key"), "action": d0.get("action"), "op": d0.get("op"),
                   "variant": d0.get("variant"), "id": d0.get("id")}
            act = d0.get("action")
            try:
                d = self.resolve(d0) if act in ("wire", "delete", "retire", "copy", "add_shift_reg",
                                                "create_const_on_term") else d0
                ex = d.get("exec") or {}
                if act == "delete":
                    row["result"] = self.delete_wire(int(ex["wire_uid"]), tag)
                elif act == "retire":
                    row["result"] = self.delete_object(ex["class"], int(ex["uid"]), tag)
                elif act == "copy":
                    row["result"] = self.copy_in(ex["cls"], ex["uid"], ex["dest_diagram"], ex["pos"], d0.get("id"))
                elif act == "add_shift_reg":
                    row["result"] = self.add_sr_row(ex, d0.get("id") or tag)
                elif act == "create_const_on_term":
                    row["result"] = self.const_row(ex, d0.get("id") or tag)
                elif act == "wire":
                    row["op_rule"] = self.rule_check(d)
                    row.update(self._wire_row(d, objs))
                    if d.get("es_probe"):
                        row["es_probe"] = [self.es("{0} right after the connect".format(d0.get("id")))]
                        time.sleep(2.0)
                        row["es_probe"].append(self.es("{0} after 2 s".format(d0.get("id"))))
                    self.junk_purge("{0} row {1}".format(tag, i))
                    if d.get("es_probe"):
                        row["es_probe"].append(self.es("{0} after the purge".format(d0.get("id"))))
                        self.row("P6D-probe {0} ES now/2s/purged".format(d0.get("id")), row["es_probe"],
                                 "recorded")
                else:
                    row["result"] = "NOT EXECUTED (action {0!r})".format(act)
                if d0.get("as") and act in ("copy", "add_shift_reg", "create_const_on_term"):
                    self.sym[d0["as"]] = row["result"]
            except Exception as e:                                                 # noqa: BLE001
                row["error"] = "{0}: {1}".format(type(e).__name__, str(e)[:240])
            res = row.get("result") if isinstance(row.get("result"), dict) else {}
            row["failed_layer"] = "execution" if row.get("error") or res.get("err") \
                else (None if act in ("wire", "delete", "retire", "copy", "add_shift_reg", "create_const_on_term")
                      else (d0.get("evidence") or {}).get("failed_layer"))
            self.row("from_decision row {0} {1}".format(i, row.get("id")), {k: row.get(k) for k in
                     ("action", "op", "variant", "how", "result", "error", "failed_layer")})
            out.append(row)
        self.R["from_decision"] = out
        self.dump()
        return out

    def _wire_row(self, d, objs):
        ex, op = d["exec"], d["op"]
        s, t = ex["src"], ex["dst"]
        if op in ("connect_nested", "connect_terminals"):
            (sd, sn, st), hs = self.address(s, True, objs)
            (dd, dn, dt), hd = self.address(t, False, objs)
            N = mod("build_opconnectnested_v1")
            lab = json.load(open(N.MAP_OUT, encoding="utf-8"))
            if op == "connect_terminals" and sd == dd == 0:
                rec = self._op("connect_terminals", lambda: g.connect_terminals(self.work, dn, dt, sn, st),
                               "N[{0}].t{1} <- N[{2}].t{3}".format(dn, dt, sn, st))
            else:
                rec = self._op("connect_nested_v1", lambda: N.connect_nested_v1(self.work, dd, dn, dt, sd, sn, st, lab),
                               "D[{0}].N[{1}].t{2} <- D[{3}].N[{4}].t{5}".format(dd, dn, dt, sd, sn, st))
            return {"how": [hs, hd], "result": rec}
        if op == "wire_sr":
            sr, variant = ex["sr"], d["variant"]
            body, is_src = (t, False) if variant == "LeftIn" else (s, True)
            reg_end = s if variant == "LeftIn" else t
            if int(body["diagram"]) != int(reg_end["diagram"]):
                raise RuntimeError("body end on diagram {0}, register inside on {1}".format(body["diagram"],
                                                                                            reg_end["diagram"]))
            (bd, bn, bt), hb = self.address(body, is_src, objs)
            cls = sr.get("loop_class", "WhileLoop")
            li = next((r["i"] for r in g.report_all(self.work, cls) if int(r["uid"]) == int(sr["loop_uid"])), None)
            k = list(sr["right_uids"]).index(int(sr["right_uid"]))
            echo = g.shift_reg(self.work, li, k, class_name=cls).get("uid")
            if echo != int(sr["right_uid"]):
                raise RuntimeError("shift_reg[{0}][{1}] echo {2!r} != #{3}".format(li, k, echo, sr["right_uid"]))
            rec = self._op("wire_sr", lambda: g.wire_sr(variant, self.work, li, k, node_index=bn, term_index=bt,
                                                        class_name=cls),
                           "{0} loop[{1}] reg[{2}] node[{3}].t{4}".format(variant, li, k, bn, bt))
            return {"how": [hb, "loop #{0} idx {1}, reg {2} echo #{3}".format(sr["loop_uid"], li, k, echo)],
                    "result": rec}
        if op == "fs_inner_tunnel_connect":
            (sd, sn, st), hs = self.address(s, True, objs)
            return {"how": [hs], "result": self.fs_inner_tunnel_connect(int(t["uid"]), sd, sn, st)}
        if op == "connect_from_wire":
            return self._cfw_row(d, objs)
        raise RuntimeError("op {0!r} has no executor in from_decision".format(op))

    def _cfw_row(self, d, objs):
        """`OpConnectFromWire_v0` rows. variant None: the source terminal is on live wire exec.src.wire_uid.
        variant 'tunnel_outer' (PRE-DECIDED 146, docs/connectivity-map-plan.md; measured
        tools/bench/bench_map_w9635.log C1): the source is a Selector/Loop tunnel's INNER terminal that no writer
        can address; branch off the tunnel's OUTER feed wire, taking the terminal the tunnel itself owns on it
        (index read live by `OpWireSource_v5`, owner uid echoed) - LabVIEW mints a NEW tunnel - then delete the
        ORPHAN (the old tunnel, only when every inner wire reads 0 via `OpTunnels_v0`). ExecState is read before
        and after the delete and REPORTED; nothing else is cleaned up."""
        ex, variant = d["exec"], d.get("variant")
        s, t = ex["src"], ex["dst"]
        F = mod("build_opconnectfromwire_v0")
        w = int(s.get("outer_wire") or 0) if variant == "tunnel_outer" else int(s.get("wire_uid") or 0)
        want_src = variant != "tunnel_outer"
        walk = F.wire_source_owner(self.work, w, n=8) if w else []
        hit = [x for x in walk if x.get("owner_uid") == int(s["uid"]) and bool(x.get("is_source")) == want_src]
        if len(hit) != 1:
            raise RuntimeError("w{0}: {1} term(s) owned by #{2} (is_source {3})".format(w, len(hit), s["uid"], want_src))
        (dd, dn, dt), hd = self.address(t, False, objs)
        rec = self.connect_from_wire(dd, dn, dt, w, int(hit[0]["i"]))
        how = [hd, "w{0}[{1}] owned by #{2}".format(w, hit[0]["i"], s["uid"])]
        out = {"how": how, "result": rec}
        if variant == "tunnel_outer" and s.get("owner_class") == "LoopTunnel":
            self.junk_purge("cfw before orphan")      # the connect's stray Invoke, before delete re-marks the census
            cls, uid = "LoopTunnel", int(s["uid"])
            li = self.uid_index(cls, uid)
            tun = g.tunnels(self.work, li) if li is not None else {}
            # review 2026-09-23 bench-map-w9635-writers test 1: the NEW tunnel's IndexMode + outer net vs the old

            def _new_tunnel():
                res = rec.get("result")
                sw = (res[3] or {}).get("UID 2") if isinstance(res, (list, tuple)) and len(res) > 3 else None
                new = [x for x in (F.wire_source_owner(self.work, int(sw), n=4) if sw else []) if x.get("is_source")]
                nu = int(new[0]["owner_uid"]) if new else None
                ni = self.uid_index(cls, nu) if nu else None
                nt = g.tunnels(self.work, ni) if ni is not None else {}
                nnet = self.net_sources(nt.get("out_wire"), tag="new tunnel outer") if nt.get("out_wire") else {}
                return {"uid": nu, "index_mode": nt.get("index_mode"), "out_wire": nt.get("out_wire"),
                        "out_net_sources": nnet.get("source_owners"), "old_index_mode": tun.get("index_mode"),
                        "old_out_wire": tun.get("out_wire"), "feed_wire_alive": w in g.uids(self.work, "Wire")}
            out["new_tunnel"], _e = self.safe("PD146 new-tunnel read", _new_tunnel, {})
            self.fact("PD146 new tunnel vs old: {0}".format(out["new_tunnel"]))
            orphan = bool(tun) and tun.get("uid") == uid and not any(tun.get("in_wires") or [1])
            es0 = self.es("before orphan delete #{0}".format(uid))
            if orphan:
                out["orphan_delete"] = self.delete_object(cls, uid, "orphan")
            out["orphan"] = {"uid": uid, "in_wires": tun.get("in_wires"), "deleted": orphan, "es_before": es0,
                             "es_after": self.es("after orphan delete #{0}".format(uid))}
            self.fact("PD146 orphan #{0}: {1}".format(uid, out["orphan"]))
        return out

    # ------------------------------------------------------------------ save
    def save_route(self, exec_state, broken_ok):
        """WHICH SAVE ROUTE, as a pure function so it is self-testable without LabVIEW.
        1 -> the scripted `SaveInstrument`; 0 + broken_ok -> the APPROVED broken-intermediate `gui_save`
        (CLAUDE.md split-rule 6, evidence "user 2026-09-22 broken-intermediate save"); 0 without it ->
        REFUSE (`SaveInstrument` blocks forever on a broken VI - gscript.save:2147)."""
        if exec_state == 1:
            return "scripted"
        if exec_state == 0 and broken_ok:
            return "gui_save"
        return "refuse"

    def save(self, broken_ok=False, cold_check=True):
        """ONE save of the work copy, by the route `save_route` picks. Records md5, size and version bytes;
        the COLD re-open check runs only when ExecState was 1 (never cold-load a broken-saved VI - the
        recompile spin, skill "five laws")."""
        self.head("[SAVE] {0}".format(os.path.basename(self.work)))
        es = self.es("before the save")
        route = self.save_route(es, broken_ok)
        self.R["saves"]["exec_state_before"] = es
        self.R["saves"]["route"] = route
        if route == "refuse":
            self.gate("S1 a save route exists for ExecState {0!r}".format(es), False,
                      "ExecState 0 and broken_ok=False - NOTHING SAVED")
            return None
        if route == "gui_save":
            self.fact("SAVE ROUTE = gui_save, the APPROVED broken-intermediate route (CLAUDE.md "
                      "split-rule 6; evidence \"user 2026-09-22 broken-intermediate save\"). The artefact "
                      "is BROKEN BY DESIGN and is NEVER RUN (34(f)).")
        size, err = self.safe("g.save(allow_broken={0!r})".format(route == "gui_save"),
                              lambda: g.save(self.work, allow_broken=(route == "gui_save")))
        self.gate("S1 the save returned without raising ({0} route)".format(route), not err,
                  str(err)[:180])
        g.reset()
        time.sleep(1.5)
        ff = self.file_facts("SAVED ARTEFACT", self.work)
        self.R["saves"].update({"size": size, "md5": ff.get("md5"), "bytes": ff.get("size"),
                                "version_bytes": ff.get("version_bytes")})
        self.gate("S2 the artefact is on disk and non-empty", bool(ff.get("size")),
                  "{0} B".format(ff.get("size")))
        if route == "scripted" and cold_check:
            es2 = self.es("re-read AFTER the save")
            self.gate("S3 ExecState 1 re-read AFTER the save", es2 == 1,
                      "ExecState {0!r}".format(es2))
        else:
            self.fact("S3 COLD re-open check SKIPPED BY RULE: ExecState was {0!r}, and a broken-saved VI "
                      "is never cold-loaded headless (recompile spin).".format(es))
        self.dump()
        return ff.get("md5")

    # ------------------------------------------------------------------ close
    def close(self, expect_files=None):
        """HYGIENE: panels closed, refs opened == closed, scratches deleted, the input's md5 unchanged,
        every pin re-checked, the files-left-on-disk listing, handles, JSON. Returns the process rc."""
        self.head("[H] HYGIENE")
        for p in [self.work] + list(self.scratches):
            self.safe("close_panel({0})".format(os.path.basename(p)), lambda q=p: g.close_panel(q))
        self._preload_exit()
        self.R["H"]["ref_counts"] = g.ref_counts()
        self.fact("gscript ref_counts: {0!r}".format(self.R["H"]["ref_counts"]))
        self.gate("H5 VI-Server reference counter level (opened == closed)",
                  self.R["H"]["ref_counts"].get("live") == 0, repr(self.R["H"]["ref_counts"]))
        bp = mod("bench_prep")
        handles, _ = self.safe("handles after the work", bp.labview_handles)
        self.R["H"]["handles_after_work"] = handles
        self.fact("LabVIEW handle count AFTER the work: {0!r}".format(handles))
        if self.scratches:
            self.safe("restart before the deletes", bp.restart_labview)
            g.reset()
            time.sleep(2.0)
        for p in self.scratches:
            for _a2 in range(6):
                if not os.path.exists(p):
                    break
                try:
                    os.remove(p)
                except Exception as e:                                             # noqa: BLE001
                    self.fact("delete {0} failed: {1}".format(os.path.basename(p), str(e)[:110]))
                    time.sleep(4.0)
            self.gate("H4 scratch deleted: {0}".format(os.path.basename(p)), not os.path.exists(p), p)
        got = md5(self.input_vi) if os.path.exists(self.input_vi) else "MISSING"
        self.R["input_md5_after"] = got
        self.gate("H2 the INPUT's md5 is UNCHANGED after the run", got == self.R.get("input_md5_before"),
                  "before {0} / after {1}".format(self.R.get("input_md5_before"), got))
        self.gate("H3 every md5 pin still holds", self.pin_check("AFTER"))
        after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(CLAUDEDEV, "*.vi")))
        if self.R.get("claudedev_before") is None:
            self.fact("H6 NOT MEASURED: the run never took the BEFORE listing, so an 'added' set would be "
                      "the whole directory. Reported, not gated.")
            self.dump()
            return self.summary()
        added = sorted(set(after) - set(self.R["claudedev_before"]))
        gone = sorted(set(self.R["claudedev_before"]) - set(after))
        want = sorted(expect_files if expect_files is not None else
                      ([os.path.basename(self.work)] if os.path.exists(self.work) else []))
        self.fact("THE FILES THIS RUN LEFT ON DISK: {0!r}  (removed: {1!r})".format(added, gone))
        self.gate("H6 the files left on disk == {0!r} and nothing was removed".format(want),
                  added == want and not gone, "added {0!r} removed {1!r}".format(added, gone))
        handles2, _ = self.safe("handles final", bp.labview_handles)
        self.R["H"]["handles_final"] = handles2
        self.fact("LabVIEW handle count at exit: {0!r}".format(handles2))
        self.dump()
        return self.summary()


def fixtures_check(bad_md5s=(), before_listing=None):
    """REVIEW c68-h6 (archive/peer/2026-09-24-c68-h6-fixture-listing.md §1/§4, accepted): after a run that swapped
    bytes into the NI Moving-Objects pair, PROVE the restore - each live file == its `.ORIG.bak`, no `.bak` holds a
    run's bytes (`bad_md5s`, e.g. the bed), and the folder's *.vi listing is unchanged. Prints gate rows; returns ok."""
    ok = True
    for live in (g.MOVE_SRC, g.MOVE_DST):
        bak = live + ".ORIG.bak"
        a = md5(live) if os.path.exists(live) else "MISSING"
        b = md5(bak) if os.path.exists(bak) else "MISSING"
        good = a == b and b != "MISSING" and b not in set(bad_md5s)
        ok = ok and good
        print(_a("  {0}  FX {1} == its .ORIG.bak and the .bak is not a run's bytes  live {2} bak {3}".format(
            "PASS" if good else "FAIL", os.path.basename(live), a, b)), flush=True)
    now = sorted(os.path.basename(p) for p in glob.glob(os.path.join(os.path.dirname(g.MOVE_DST), "*.vi")))
    if before_listing is not None:
        same = now == sorted(before_listing)
        ok = ok and same
        print(_a("  {0}  FX the Moving-Objects *.vi listing is unchanged  {1}".format("PASS" if same else "FAIL",
                                                                                     now)), flush=True)
    return ok


def match_term_uid(term_uid, all_rows, node_rows, is_source):
    """Pre-decided 173 (cycle 71): a terminal addressed by its TERMINAL UID after its first resolution, because a
    terminal's NAME changes on move and on wiring (`stage_d1_l7_1b.log:274`: a new left SR's outer terminal read
    'total data array out' before its wire landed and '' after). Pure function, no LabVIEW.
    `all_rows` = `allterms.read_terms` rows (term_uid, wire_uid, is_source, ...); `node_rows` = `gscript.node_terms`
    rows of the node the connect op addresses (i, name, is_source, wire) - which may be the STRUCTURE carrying the
    terminal (a shift register's outer terminal sits in the loop's Terminals[]). The uid is found in the whole-VI
    table, and its WIRE uid (a unique object) picks the one node row of the same direction. An unwired terminal or
    anything other than exactly one hit RAISES - never a fallback to the name. Returns (terminal index, all-row)."""
    a = [r for r in all_rows if int(r["term_uid"]) == int(term_uid)]
    if len(a) != 1:
        raise RuntimeError("terminal uid #{0}: {1} row(s) in the whole-VI terminal table".format(term_uid, len(a)))
    w = int(a[0]["wire_uid"] or 0)
    if not w or bool(a[0]["is_source"]) != bool(is_source):
        raise RuntimeError("terminal uid #{0}: wire {1}, is_source {2} - uid addressing needs a wired terminal of "
                           "direction {3}".format(term_uid, w, a[0]["is_source"], bool(is_source)))
    hits = [r for r in node_rows if int(r.get("wire") or 0) == w and bool(r["is_source"]) == bool(is_source)]
    if len(hits) != 1:
        raise RuntimeError("terminal uid #{0} (wire {1}): {2} matching row(s) on the addressed node".format(
            term_uid, w, len(hits)))
    return int(hits[0]["i"]), a[0]


def uid_edges(G, kinds=("wire", "fs")):
    """A graph's edges keyed by TERMINAL UID, not by name (review archive/peer/2026-09-24-c68-m4a-p6b-rename.md §4,
    measured tools/bench/q_m4a_diffuid.log: a name-keyed diff reported 13/12 renamed-only edges on unchanged
    uids). `sr` is excluded by default: vigraph pairs registers by equal TOP, and a new register added at an
    occupied TOP makes the pairing ambiguous (same log, U3/U6) - report it, never gate on it."""
    V = mod("vigraph")
    out = set()
    for k, a, b, _i in G["edges"]:
        if k in kinds:
            out.add((k, V.key_parts(a)[0], int((G["rows"].get(a) or {}).get("term_uid") or 0),
                     V.key_parts(b)[0], int((G["rows"].get(b) or {}).get("term_uid") or 0)))
    return out


def fixture_listing():
    return sorted(os.path.basename(p) for p in glob.glob(os.path.join(os.path.dirname(g.MOVE_DST), "*.vi")))


def unload_donor(path=None):
    """Card 97-5 (judgement c97): after the copy_in calls, drop the donor (default `g.MOVE_SRC`) from LabVIEW's memory
    before the MEMSTOP-metered edits. An open front panel keeps a VI resident (gscript.close_panel), so its panel is
    closed; residency is READ before/after from `Application.ExportedVIs` (NI 'All VIs in Memory'), and private MB
    before/after. FACTS ONLY: returns a dict, never raises - a failed read is recorded, not gated."""
    path = path or g.MOVE_SRC
    name = os.path.basename(path).lower()

    def resident():
        try:
            return any(os.path.basename(str(n)).lower() == name for n in (g.lv().ExportedVIs or ()))
        except Exception as e:                                                     # noqa: BLE001
            return "unread: {0}".format(str(e)[:60])
    out = {"mb_before": round((private_bytes() or 0) / 1e6, 1), "resident_before": resident()}
    try:
        g.close_panel(path)
        out["close_panel"] = "ok"
    except Exception as e:                                                         # noqa: BLE001
        out["close_panel"] = "err: {0}".format(str(e)[:80])
    time.sleep(1.0)
    out["resident_after"] = resident()
    out["mb_after"] = round((private_bytes() or 0) / 1e6, 1)
    return out


def run(fn, stage):
    """The standard main(): run `fn(stage)`, never let an exception skip the hygiene tail."""
    try:
        fn(stage)
    except Stop as e:
        stage.gate("STOP at gate: {0}".format(e), False)
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        stage.exc_text = "{0}: {1}".format(type(e).__name__, str(e))[:200]      # C6 first_fail
        stage.R["fatal"] = traceback.format_exc()[-2500:]
        print("\nOBSERVED EXC {0}\n{1}".format(str(e)[:300], traceback.format_exc()[-2000:]), flush=True)
        stage.gate("the run completed without an unhandled exception", False, str(e)[:160])
    try:
        return stage.close()
    except Exception as e:                                                         # noqa: BLE001
        stage.gate("H-HYGIENE the hygiene phase completed", False, str(e)[:150])
        return stage.summary()
