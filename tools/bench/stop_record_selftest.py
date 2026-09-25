r"""stop_record_selftest.py - the SIX acceptance cases of the prior-art LAUNCH GATE (cycle 18).

WHY A SELF-TEST IS THE ACCEPTANCE (docs/cycle18-plan.md Pre-decided 4, and §D.4 of the motor plan it rehearses):
"Prove it on a deliberately blocked recipe before trusting it ... A gate that passes only its happy path is not
accepted." The device exists because `device-failed` reached its threshold - a device that let its own fault
through - so this file exercises the refusal, the release, the re-edit, and the unreadable store.

PREDICTION CONTRACT (each line is a gate; the run fails if any disagrees):
  CASE 1  a standing stop record, no release line anywhere in its review
            -> check_command(<launch of that recipe>) REFUSES, in all three command spellings
            -> an unrelated command is still ALLOWED (the refusal is narrow)
  CASE 2  a valid `FIXED: <slug> - <recipe>:<line> - ...` under "## What was done with it"
            -> the same launch PASSES, and the record is stamped with the recipe's CURRENT sha256
  CASE 3  one byte appended to the recipe after that release
            -> the launch REFUSES again, and the message names BOTH hashes
  CASE 4  tools/bench/stop_records.json replaced by garbage
            -> a command naming any tools/recipes/*.py REFUSES (fail closed)
            -> `ls -la docs` is ALLOWED (narrow: a broken store must not wedge the session)
  CASE 5  (2026-09-18) `prior_art_review.py` run with NEITHER --recipe NOR the opt-out
            -> it EXITS NON-ZERO, naming both flags; no peer is dispatched; no stop record is written
  CASE 6  (2026-09-18) the same run with `--no-recipe "<reason>"`
            -> it RUNS (the peer dispatch is attempted exactly once, stubbed here) and the reason appears
               verbatim in the archived review file, in a block no gate can mistake for a release

WHY 5 AND 6 EXIST (the judgement decision of 2026-09-18). Cases 1-4 prove the gate refuses what it was armed
against; they say nothing about whether it was ever ARMED. Before this change, omitting `--recipe` printed
`STOP RECORD: NOT ARMED` and carried on - so the device could be left inert by forgetting a flag, which is not a
decision anybody took. An omission is now a refusal and the opt-out is explicit and recorded, exactly as the GUI
gate distinguishes a slip from an authorised exception.

WHAT ALREADY EXISTED (checked before writing this):
  * `ls tools/bench/selftest_*` -> selftest_guard_cycle_fixed.py / _rerun.py cover `premature_build` condition
    (b); selftest_stamp_window.py covers `stamp()`. NONE covers a launch, and none existed for stop_record.
  * The FIXED:/REFUTED: validator is guard_cycle's and is IMPORTED by stop_record, never copied - so this file
    tests the gate, not a second copy of the rules.

ISOLATION (brief: "never test against the live store in place"). `stop_record.STORE` / `.MARKER` are pointed at a
temp directory for the whole run and restored in `finally`; the real store is fingerprinted before and after and
the comparison is a gate. The scratch recipe is a REAL file under tools/recipes/ (so the command strings and the
fail-closed path test are the real shapes) and is deleted in the same operation, and the scratch review lives in
the temp directory - deliberately NOT in archive/peer/, where a stray `*priorart*.md` would gate real builds.

    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/cycle18_stopgate.log \
        -- py -u tools/bench/stop_record_selftest.py
"""
import glob
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import prior_art_review as par  # noqa: E402  - cases 5 and 6 test its arming contract
import stop_record  # noqa: E402

RESULTS = []


def gate(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("  PASS  " if ok else "  -> FAIL  ") + name + (("   " + detail) if detail else ""), flush=True)
    return bool(ok)


def first_line(msg):
    return (msg or "").strip().splitlines()[0][:150] if msg else "(empty)"


def fingerprint(p):
    if not os.path.exists(p):
        return "absent"
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


REVIEW_HEAD = """# Prior-art review - SCRATCH (self-test)

- **agent:** claude
- **slug:** priorart-scratch-stopgate
- **date:** {date}
- **outcome:** ANSWERED

## Question

(scratch)

## Answer

A2 REFUTED ALREADY. This exact build was attempted and failed.

PRIOR-ART: already-failed
"""

DISPOSITION = """

## What was done with it

FIXED: already-failed - {recipe}:1 - the scratch recipe was rewritten to stop repeating the failed route.
"""


def main():
    print("=== stop_record launch gate: self-test (cycle 18, plan Pre-decided 4) ===", flush=True)
    real_store, real_marker = stop_record.STORE, stop_record.MARKER
    before = (fingerprint(real_store), fingerprint(real_marker))
    tmp = tempfile.mkdtemp(prefix="stopgate_")
    stem = "scratch_stopgate_%d_%d" % (os.getpid(), int(time.time()))
    recipe_rel = "tools/recipes/%s.py" % stem
    recipe_abs = os.path.join(ROOT, "tools", "recipes", "%s.py" % stem)
    review = os.path.join(tmp, "scratch-priorart-review.md")
    launches = ["MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/%s.log -- py -u %s"
                % (stem, recipe_rel),
                "py %s" % recipe_rel,
                "py %s" % recipe_rel.replace("/", "\\")]
    try:
        stop_record.STORE = os.path.join(tmp, "stop_records.json")
        stop_record.MARKER = os.path.join(tmp, "stop_records.marker")
        with open(recipe_abs, "w", encoding="utf-8") as f:
            f.write("# scratch recipe for the cycle-18 launch-gate self-test. Deleted by the same run.\n"
                    "print('scratch')\n")
        with open(review, "w", encoding="utf-8") as f:
            f.write(REVIEW_HEAD.format(date=time.strftime("%Y-%m-%d")))

        # ---- CASE 1: a standing record with no release anywhere -------------------------------------------
        rec = stop_record.write_stop_record(recipe_rel, review, ["already-failed"])
        gate("C1a record written, keyed to path+hash",
             rec["recipe_path"] == recipe_rel and len(rec["reviewed_sha256"] or "") == 64
             and rec["released"] is None, rec["reviewed_sha256"][:12])
        for i, cmd in enumerate(launches):
            allow, msg = stop_record.check_command(cmd)
            gate("C1b launch REFUSED (spelling %d)" % (i + 1), not allow, first_line(msg))
        allow, _ = stop_record.check_command("ls -la docs")
        gate("C1c an unrelated command is untouched", allow)
        allow, _ = stop_record.check_command("py tools/recipes/some_other_recipe.py")
        gate("C1d a DIFFERENT recipe is untouched (refusal is per record, not per directory)", allow)

        # ---- CASE 2: a valid FIXED: release ----------------------------------------------------------------
        with open(review, "a", encoding="utf-8") as f:
            f.write(DISPOSITION.format(recipe=recipe_rel))
        os.utime(recipe_abs, None)                         # the fix post-dates the review, as FIXED: requires
        sha_at_release = stop_record.sha256_of(recipe_abs)
        allow, msg = stop_record.check_command(launches[0])
        gate("C2a launch PASSES after a valid FIXED: line", allow, first_line(msg) if not allow else "")
        recs = stop_record.load_records()
        rel = (recs[0] or {}).get("released") or {}
        gate("C2b the release is stamped with the CURRENT sha256", rel.get("sha256") == sha_at_release,
             (rel.get("sha256") or "none")[:12])
        allow2, _ = stop_record.check_command(launches[1])
        gate("C2c a second launch of the same bytes still passes", allow2)

        # ---- CASE 3: the recipe's bytes change after the release -------------------------------------------
        with open(recipe_abs, "a", encoding="utf-8") as f:
            f.write("# edited after the release\n")
        sha_now = stop_record.sha256_of(recipe_abs)
        allow, msg = stop_record.check_command(launches[0])
        gate("C3a launch REFUSED again after the recipe changed", not allow, first_line(msg))
        gate("C3b the refusal names BOTH hashes",
             (not allow) and sha_at_release[:12] in msg and sha_now[:12] in msg)
        gate("C3c the record was NOT cleared by the re-save",
             (stop_record.load_records()[0].get("released") or {}).get("sha256") == sha_at_release)

        # ---- CASE 4: an unreadable store ------------------------------------------------------------------
        with open(stop_record.STORE, "w", encoding="utf-8") as f:
            f.write("{ this is not json, and never was")
        allow, msg = stop_record.check_command("py tools/bgrun.py --max-min 5 --log tools/bench/x.log "
                                               "-- py -u tools/recipes/anything_at_all.py")
        gate("C4a corrupt store REFUSES a tools/recipes launch (fail closed)", not allow, first_line(msg))
        allow, _ = stop_record.check_command("ls -la docs")
        gate("C4b corrupt store leaves an unrelated command alone", allow)
        os.remove(stop_record.STORE)
        allow, msg = stop_record.check_command("py tools/recipes/anything_at_all.py")
        gate("C4c a DELETED store is missing-but-expected, not a release", not allow, first_line(msg))
        allow, _ = stop_record.check_command("grep -n def tools/gscript.py")
        gate("C4d ... and still does not wedge a grep", allow)

        # ---- CASE 5: omission is a REFUSAL, not an un-armed gate (2026-09-18) -------------------------------
        # Run as a real SUBPROCESS, so what is tested is the command line an operator actually types. No peer is
        # dispatched: the refusal happens at argument-parse time, before the task file, before peer.ps1.
        peers_before = len(glob.glob(os.path.join(ROOT, "archive", "peer", "*.md")))
        store_before = (fingerprint(real_store), fingerprint(real_marker))
        p5 = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "prior_art_review.py"),
                             "--plan", "scratch plan, cycle-18 self-test case 5", "--slug",
                             "scratch-omission-%d" % os.getpid()],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        out5 = (p5.stdout or "") + (p5.stderr or "")
        gate("C5a --recipe omitted with no opt-out -> NON-ZERO exit", p5.returncode != 0, "rc %s" % p5.returncode)
        gate("C5b the refusal names both the required flag and the opt-out",
             "--recipe" in out5 and "--no-recipe" in out5, first_line(out5))
        gate("C5c the refusal prints the current command form",
             "prior_art_review.py --plan-file" in out5 and "tools/recipes/" in out5)
        gate("C5d no peer was dispatched (no new archive/peer file)",
             len(glob.glob(os.path.join(ROOT, "archive", "peer", "*.md"))) == peers_before)
        gate("C5e no stop record was written (the REAL store is untouched)",
             (fingerprint(real_store), fingerprint(real_marker)) == store_before)

        # ---- CASE 6: the explicit opt-out RUNS, and is recorded --------------------------------------------
        # The peer dispatch is STUBBED - a self-test must never spend a real review. `par.subprocess` is replaced
        # wholesale (not `subprocess.run` patched globally) so nothing else in this process is affected, and
        # `par.ROOT` is pointed at a fake project tree so the archived review this writes into is a scratch file,
        # never a real `archive/peer/*priorart*.md` (one of those would gate real builds).
        slug6 = "scratch-optout-%d" % os.getpid()
        reason6 = "this reviews a plan document; no recipe exists yet (self-test case 6)"
        fake_root = os.path.join(tmp, "fakeroot")
        os.makedirs(os.path.join(fake_root, "archive", "peer"))
        rev6 = os.path.join(fake_root, "archive", "peer",
                            "%s-priorart-%s.md" % (time.strftime("%Y-%m-%d"), slug6))
        with open(rev6, "w", encoding="utf-8") as f:
            f.write(REVIEW_HEAD.format(date=time.strftime("%Y-%m-%d")))
        calls = []

        class _FakeProc(object):
            returncode = 0

        def _fake_run(cmd, **kw):
            calls.append(cmd)
            return _FakeProc()

        old_root, old_sub, old_argv = par.ROOT, par.subprocess, sys.argv
        # card chat-L2: prior_art_review.main() writes a review/1 card through protocol.CARDS_DIR; without this the
        # self-test left scratch review cards in the REAL tools/bench/cards/ (chat-L1 removed 2 by hand).
        import protocol as _proto
        old_cards = _proto.CARDS_DIR
        _proto.CARDS_DIR = os.path.join(fake_root, "cards")
        try:
            par.ROOT = fake_root
            par.subprocess = types.SimpleNamespace(run=_fake_run)
            sys.argv = ["prior_art_review.py", "--plan", "scratch plan, case 6", "--slug", slug6,
                        "--no-recipe", reason6]
            rc6 = par.main()
        finally:
            par.ROOT, par.subprocess, sys.argv = old_root, old_sub, old_argv
            _proto.CARDS_DIR = old_cards
        with open(rev6, encoding="utf-8") as f:
            body6 = f.read()
        gate("C6a --no-recipe \"<reason>\" RUNS (rc 0)", rc6 == 0, "rc %s" % rc6)
        gate("C6b the peer dispatch was attempted exactly once (stubbed)", len(calls) == 1)
        gate("C6c the reason is in the archived review, verbatim", reason6 in body6,
             "%d chars appended" % (len(body6) - len(REVIEW_HEAD.format(date=time.strftime("%Y-%m-%d")))))
        gate("C6d the recorded block cannot be read as a release or a disposition",
             not re.search(r"^(FIXED|REFUTED|PRIOR-ART):", body6.split("## Launch gate", 1)[-1], re.M)
             and "## What was done with it" not in body6)
        gate("C6e the opt-out armed NOTHING (the REAL store is still untouched)",
             (fingerprint(real_store), fingerprint(real_marker)) == store_before)
        p6 = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "prior_art_review.py"),
                             "--plan", "x", "--slug", slug6, "--no-recipe", "   "],
                            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        gate("C6f a whitespace-only reason is NOT an opt-out", p6.returncode != 0,
             "rc %s" % p6.returncode)
    finally:
        stop_record.STORE, stop_record.MARKER = real_store, real_marker
        for p in (recipe_abs,):
            try:
                os.remove(p)
            except OSError:
                pass
        shutil.rmtree(tmp, ignore_errors=True)

    gate("C0 the scratch recipe was deleted in the same run", not os.path.exists(recipe_abs))
    after = (fingerprint(real_store), fingerprint(real_marker))
    gate("C0 the REAL store was never touched", before == after, "%s -> %s" % (before, after))

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    nfail = len(RESULTS) - npass
    print("=== stop_record selftest: %d pass, %d fail ===" % (npass, nfail), flush=True)
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
