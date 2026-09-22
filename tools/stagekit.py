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

    # ------------------------------------------------------------------ edit verbs (thin wrappers)
    def _op(self, verb, fn, detail=""):
        """Run one mutator, record its error column, mark the node census for a later junk purge."""
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


def run(fn, stage):
    """The standard main(): run `fn(stage)`, never let an exception skip the hygiene tail."""
    try:
        fn(stage)
    except Stop as e:
        stage.gate("STOP at gate: {0}".format(e), False)
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        stage.R["fatal"] = traceback.format_exc()[-2500:]
        print("\nOBSERVED EXC {0}\n{1}".format(str(e)[:300], traceback.format_exc()[-2000:]), flush=True)
        stage.gate("the run completed without an unhandled exception", False, str(e)[:160])
    try:
        return stage.close()
    except Exception as e:                                                         # noqa: BLE001
        stage.gate("H-HYGIENE the hygiene phase completed", False, str(e)[:150])
        return stage.summary()
