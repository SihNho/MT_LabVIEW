r"""test_run_poison.py - does a hard-timed-out COM call still block the NEXT call? (OPEN 35, the defect
codex named in archive/peer/2026-09-17-connectnested-stall.md.)

    MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/test_run_poison.log \
        -- py -u tools/bench/test_run_poison.py

WHAT WAS ALREADY THERE (checked before writing a line of this):
  * `gscript._run` / `_invoke` already had the watchdog + hard cap; what they did NOT have is any handling
    of the call they abandon. `tools/gscript.py.guarded_attempt_20260905` shows the route this project
    already TRIED and ROLLED BACK - putting GetVIReference/SetControlValue on the watchdog thread, which
    itself blocked in cross-apartment marshalling (CLAUDE.md records it). So this fix is the OTHER option
    in the brief: a module POISON flag checked by every COM entry point.
  * `tools/bench/bench_prep.py:labview_handles` reads the handle count - reused, not rebuilt.
  * `tools/lv_restart.py` holds the restart-and-wait sequence - `_recover_poison()` follows it (including
    its "never dismiss the startup window, just wait 45 s" finding).

PREDICTION CONTRACT. Two arms; arm A needs no LabVIEW at all.

  ARM A - fake blocking callable, ZERO COM:
   A1  `_deadline_call(lambda: sleep(30), 0.5, "FAKE")` returns False (it timed out).
   A2  `poisoned()` is a dict naming "FAKE", with the 0.5 s cap recorded.
   A3  the next `op(<any path>)` raises **COMPoisoned** in < 1.0 s and NEVER reaches COM. (This is the
       whole fix: before it, `op()` on a cache miss went straight into `GetVIReference`.)
   A3b the same for `lv()`, `_err(<dummy>)`.
   A4  after `clear_poison()`: not poisoned, and a callable that FINISHES leaves it unpoisoned.
   A5  AUTO-HEAL: poison on a 1.0 s callable capped at 0.2 s; once that callable has finished,
       `_check_poison()` returns WITHOUT raising and `poisoned()` is None again (the apartment is drained -
       measured with `thread.is_alive()`, never assumed).

  ARM B - ONE REAL sub-millisecond timeout on a SCRATCH op (unique name, deleted in the same run):
   B0  LabVIEW answers COM; handles recorded.
   B1  `_run(scratch_op, hard_timeout_s=0.001)` raises RuntimeError AND leaves the module poisoned.
       The abandoned Run is a harmless READ (OpReport_v3 census of OpWire_v1) that finishes on its own.
   B2  while that worker is still alive, `op(<another op>)` raises COMPoisoned in < 2 s.
       ⚠️ If the abandoned Run happens to finish first, B2 is reported N/A with that fact (it cannot be
       forced); B3 then carries the evidence. It is NOT scored as a pass.
   B3  once the worker has finished, the next call SUCCEEDS: `_check_poison()` self-clears and a normal
       `_run(scratch_op)` (default cap) returns a census - i.e. the fix does not wedge normal operation.
   B5  the same scenario made DETERMINISTIC (added after run 1 reported B2 as N/A): `_invoke` has no
       screenshot on its expiry path, so a 1 ms cap on `OpenFrontPanel` hands control back while the COM
       call is CERTAINLY still outstanding. The next `op()` must then raise COMPoisoned in < 2 s.
   B4  scratch deleted; md5 of OpReport_v3.vi, OpWire_v1.vi and the ORIGINAL unchanged; handles after.

Nothing is saved. No original is opened (only file-hashed). Nothing outside user.lib\claudeDev is written.
"""
import hashlib
import os
import shutil
import sys
import threading
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g                        # noqa: E402

STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCHPOISON_{STAMP}.vi")
READ_TARGET = os.path.join(g.CLAUDEDEV, "OpWire_v1.vi")
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    try:
        return hashlib.md5(open(p, "rb").read()).hexdigest()
    except OSError as e:
        return f"(unreadable: {e})"


# ================= ARM A - no LabVIEW, fake blocking callables =================
print("\n=== ARM A: the poison mechanism, with a FAKE blocking callable (no COM at all)", flush=True)
g.clear_poison()

t0 = time.time()
okA1 = g._deadline_call(lambda: time.sleep(30), 0.5, "FAKE blocking call")
gate("A1 _deadline_call returns False on expiry", okA1 is False, f"returned {okA1!r} after {time.time()-t0:.2f}s")

p = g.poisoned()
gate("A2 the module is POISONED and the record names the call",
     bool(p) and "FAKE" in p["what"] and abs(p["timeout_s"] - 0.5) < 1e-9, str(p and p["what"]))

t0 = time.time()
try:
    g.op(os.path.join(g.CLAUDEDEV, "OpReport_v3.vi"))
    gate("A3 op() raises COMPoisoned instead of reaching COM", False, "it returned a reference!")
except g.COMPoisoned as e:
    dt = time.time() - t0
    gate("A3 op() raises COMPoisoned instead of reaching COM", dt < 1.0, f"{dt*1000:.1f} ms: {str(e)[:70]}")
except Exception as e:                      # noqa: BLE001
    gate("A3 op() raises COMPoisoned instead of reaching COM", False, f"wrong exception: {type(e).__name__}: {e}")

sub = []
for label, fn in (("lv()", g.lv), ("_err()", lambda: g._err(object()))):
    try:
        fn()
        sub.append(f"{label}=NO-RAISE")
    except g.COMPoisoned:
        sub.append(f"{label}=COMPoisoned")
    except Exception as e:                  # noqa: BLE001
        sub.append(f"{label}={type(e).__name__}")
gate("A3b lv() and _err() are guarded too", all(s.endswith("COMPoisoned") for s in sub), ", ".join(sub))

g.clear_poison()
okA4a = g.poisoned() is None
okA4b = g._deadline_call(lambda: None, 5.0, "fast call") is True and g.poisoned() is None
gate("A4 clear_poison() clears, and a call that FINISHES never poisons", okA4a and okA4b,
     f"cleared={okA4a}, fast-call-clean={okA4b}")

g._deadline_call(lambda: time.sleep(1.0), 0.2, "SHORT fake call")
was = bool(g.poisoned())
th = g.poisoned()["thread"]
for _ in range(40):
    if not th.is_alive():
        break
    time.sleep(0.2)
try:
    g._check_poison()
    healed = g.poisoned() is None
except Exception as e:                      # noqa: BLE001
    healed = False
    fact(f"A5 _check_poison raised after the worker finished: {type(e).__name__}")
gate("A5 AUTO-HEAL once the abandoned callable has finished", was and healed and not th.is_alive(),
     f"poisoned={was}, worker_alive={th.is_alive()}, healed={healed}")
g.clear_poison()

# ================= ARM B - one REAL timeout against LabVIEW =================
print("\n=== ARM B: one REAL sub-millisecond timeout on a scratch op", flush=True)
handles_before = handles_after = None
try:
    from bench_prep import labview_handles
    handles_before = labview_handles()
except Exception as e:                      # noqa: BLE001
    fact(f"handle read unavailable: {type(e).__name__}: {e}")

md5_report_0, md5_target_0, md5_orig_0 = (md5(g.OP_REPORT), md5(READ_TARGET), md5(ORIGINAL))
fact(f"LabVIEW handles before: {handles_before}")
fact(f"md5 before: OpReport_v3={md5_report_0}  OpWire_v1={md5_target_0}  ORIGINAL={md5_orig_0}")

try:
    ver = g.lv().Version
    gate("B0 LabVIEW answers COM", True, f"version {ver}")
except Exception as e:                      # noqa: BLE001
    gate("B0 LabVIEW answers COM", False, f"{type(e).__name__}: {e}")
    ver = None

if ver:
    shutil.copy2(g.OP_REPORT, SCRATCH)
    fact(f"scratch op: {SCRATCH} (copy of OpReport_v3.vi)")
    try:
        vi = g.op(SCRATCH)
        vi.SetControlValue("vi path", READ_TARGET)
        vi.SetControlValue("Class Name", "Node")
        vi.SetControlValue("index", 0)

        # B1 - the real abandoned call
        raised, poisoned_now = None, None
        t0 = time.time()
        try:
            g._run(vi, poll_s=6.0, hard_timeout_s=0.001)
        except g.COMPoisoned as e:           # noqa: BLE001
            raised = f"COMPoisoned: {e}"
        except RuntimeError as e:
            raised = f"RuntimeError: {str(e)[:90]}"
        dt_b1 = time.time() - t0
        poisoned_now = g.poisoned()
        gate("B1 a real 1 ms cap raises AND poisons the module",
             raised is not None and bool(poisoned_now),
             f"{dt_b1:.2f}s, poisoned={bool(poisoned_now)}, {str(raised)[:80]}")

        worker = poisoned_now["thread"] if poisoned_now else None
        alive_at_b2 = worker.is_alive() if worker else False

        # B2 - the defect under test: the NEXT call must not block
        t0 = time.time()
        b2_kind, b2_dt = None, None
        try:
            g.op(os.path.join(g.CLAUDEDEV, "OpSubVI_v1.vi"))
            b2_kind = "returned (no raise)"
        except g.COMPoisoned:
            b2_kind = "COMPoisoned"
        except Exception as e:               # noqa: BLE001
            b2_kind = f"{type(e).__name__}"
        b2_dt = time.time() - t0
        if alive_at_b2:
            gate("B2 while the abandoned Run is alive, the next op() raises COMPoisoned in < 2 s",
                 b2_kind == "COMPoisoned" and b2_dt < 2.0, f"{b2_kind} after {b2_dt*1000:.0f} ms")
        else:
            fact(f"B2 N/A - the abandoned Run had already finished before the next call "
                 f"(next call: {b2_kind} after {b2_dt*1000:.0f} ms); see B3")

        # B3 - the abandoned call drains, work continues
        t0 = time.time()
        while worker is not None and worker.is_alive() and time.time() - t0 < 180:
            time.sleep(0.5)
        drained = time.time() - t0
        fact(f"the abandoned COM Run finished on its own after ~{drained:.1f}s "
             f"(alive={worker.is_alive() if worker else None})")
        try:
            dt = g._run(vi, poll_s=6.0, hard_timeout_s=120.0)
            nrefs = int(vi.GetControlValue("# of Refs"))
            gate("B3 after the drain the next call SUCCEEDS (self-cleared poison)",
                 g.poisoned() is None and nrefs > 0, f"# of Refs={nrefs} in {dt:.2f}s")
        except Exception as e:               # noqa: BLE001
            gate("B3 after the drain the next call SUCCEEDS (self-cleared poison)", False,
                 f"{type(e).__name__}: {str(e)[:90]}")

        # B5 - the SAME scenario, made DETERMINISTIC. B2 could not be forced because `_run`'s expiry path
        # takes a screenshot (~0.5 s), which is longer than the census Run it abandoned. `_invoke` has no
        # screenshot, so it hands control back in ~1 ms with the COM call certainly still outstanding.
        # OpenFrontPanel on the scratch op is the slow-but-harmless call; the finally block closes it.
        ref = g.lv().GetVIReference(SCRATCH, "", False, 0)
        raised5 = None
        try:
            g._invoke(ref, "OpenFrontPanel", False, 1, hard_timeout_s=0.001)
        except g.COMPoisoned as e:           # noqa: BLE001
            raised5 = f"COMPoisoned: {e}"
        except RuntimeError as e:
            raised5 = f"RuntimeError: {str(e)[:60]}"
        p5 = g.poisoned()
        alive5 = bool(p5) and p5["thread"].is_alive()
        t0 = time.time()
        kind5 = None
        try:
            g.op(os.path.join(g.CLAUDEDEV, "OpSubVI_v1.vi"))
            kind5 = "returned (no raise)"
        except g.COMPoisoned:
            kind5 = "COMPoisoned"
        except Exception as e:               # noqa: BLE001
            kind5 = type(e).__name__
        dt5 = time.time() - t0
        if alive5:
            gate("B5 with a REAL outstanding COM call, the next op() raises COMPoisoned in < 2 s",
                 kind5 == "COMPoisoned" and dt5 < 2.0,
                 f"{kind5} after {dt5*1000:.0f} ms (abandoned: OpenFrontPanel, {str(raised5)[:40]})")
        else:
            fact(f"B5 N/A - OpenFrontPanel also finished before the next call ({kind5} after {dt5*1000:.0f} ms)")
        t0 = time.time()
        while p5 is not None and p5["thread"].is_alive() and time.time() - t0 < 180:
            time.sleep(0.5)
        fact(f"B5 the abandoned OpenFrontPanel drained after ~{time.time()-t0:.1f}s")
    finally:
        g.clear_poison()
        g._cache.pop(SCRATCH, None)
        try:
            g._invoke(g.lv().GetVIReference(SCRATCH, "", False, 0), "CloseFrontPanel")
        except Exception:                    # noqa: BLE001
            pass
        for _ in range(6):
            try:
                os.remove(SCRATCH)
                break
            except OSError:
                time.sleep(2)

gone = not os.path.exists(SCRATCH)
try:
    from bench_prep import labview_handles
    handles_after = labview_handles()
except Exception:                            # noqa: BLE001
    pass
md5_report_1, md5_target_1, md5_orig_1 = (md5(g.OP_REPORT), md5(READ_TARGET), md5(ORIGINAL))
gate("B4 scratch deleted; op VIs and the ORIGINAL unchanged",
     gone and md5_report_1 == md5_report_0 and md5_target_1 == md5_target_0 and md5_orig_1 == md5_orig_0,
     f"scratch_gone={gone}, ORIGINAL={md5_orig_1}")
fact(f"LabVIEW handles after: {handles_after} (before {handles_before})")

print("\n--- FACTS ---", flush=True)
for f in facts:
    print("  " + f, flush=True)
print(f"\n=== test_run_poison: {len(passes)} pass, {len(fails)} fail"
      + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
sys.exit(1 if fails else 0)
