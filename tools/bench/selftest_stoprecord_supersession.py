r"""selftest_stoprecord_supersession.py - the THREE acceptance cases of the `_check()` supersession rule.

WHY THIS EXISTS. `archive/peer/2026-09-19-stoprecord-release-deadlock-codex.md` (verdict `unverified`) proposes
that `_check()` SKIP an already-released record whose sha no longer matches WHEN a LATER record exists for the
same normalised path. Its own closing sentence names the test this file is:

    "The cheapest discriminating test is an isolated temporary-store unit case: old released record, later
     same-path record with valid dispositions, edited bytes - current code must refuse on the old record, while
     the supersession edit must evaluate and release through the later one."

Cases 2 and 3 are the OVER-RELEASE GUARDS added by the cycle-44 judgement session, not by the review: a patch
that releases case 1 and also releases 2 or 3 has broken the gate, which is what `device-failed` means.

PREDICTION CONTRACT (fixed in advance; each line is a gate, and the expectation DEPENDS on whether the loaded
`tools/stop_record.py` carries the patch - detected from `inspect.getsource(_check)`, never assumed):

  CASE 1  old RELEASED record (sha s1) + later same-path record, all findings disposed + bytes edited to s2
            -> UNPATCHED: REFUSED   (the deadlock, reproduced)
            -> PATCHED  : RELEASED, and the LATER record is stamped with s2 while the old record keeps s1
  CASE 2  old released record + later same-path record whose findings are NOT disposed
            -> UNPATCHED: REFUSED    -> PATCHED: STILL REFUSED  (over-release guard)
  CASE 3  old released record, NO later record for that path, bytes edited
            -> UNPATCHED: REFUSED    -> PATCHED: STILL REFUSED  (the original protection, intact)

It also re-runs `tools/bench/stop_record_selftest.py` (the six cycle-18 acceptance cases) as a subprocess and
reports its score, so the same log carries the before/after of the existing device.

WHAT ALREADY EXISTED (checked before writing this, CLAUDE.md "check what already exists"):
  * `ls tools/bench/selftest_* tools/bench/*selftest*` -> `stop_record_selftest.py` covers cycle 18's SIX cases
    (refusal, release, re-edit refusal, corrupt store, arming). NONE of them plants a SECOND record for the same
    path, so none of them can see the supersession rule. This file adds exactly that axis and reuses the other
    file rather than restating it.
  * The release-line validator is `guard_cycle.released_slugs`, imported by `stop_record`, never copied here.

ISOLATION. `stop_record.STORE` / `.MARKER` are pointed at a fresh temp directory PER CASE and restored in
`finally`; the real store is fingerprinted before and after and the comparison is a gate. The scratch recipe is a
real file under `tools/recipes/` (so the command strings and the path matching are the real shapes) and is
deleted in the same run; the scratch reviews live in the temp directory, deliberately NOT in `archive/peer/`.

    MATERIAL=1 py tools/bgrun.py --max-min 8 --log tools/bench/selftest_stoprecord_supersession.log \
        -- py -u tools/bench/selftest_stoprecord_supersession.py
"""
import hashlib
import inspect
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
import importlib  # noqa: E402
stop_record = importlib.import_module(os.environ.get("STOP_RECORD_UNDER_TEST", "stop_record"))  # override: a candidate copy

RESULTS = []


def gate(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))
    print(("  PASS  " if ok else "  -> FAIL  ") + name + (("   " + detail) if detail else ""), flush=True)
    return bool(ok)


def first_line(msg):
    return (msg or "").strip().splitlines()[0][:140] if msg else "(empty)"


def fingerprint(p):
    if not os.path.exists(p):
        return "absent"
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:16]


REVIEW = """# prior-art review - SCRATCH (supersession self-test)

- **agent:** claude
- **slug:** {slug}
- **date:** {date}
- **outcome:** ANSWERED

## Question

(scratch)

## Answer

PRIOR-ART: {slug_verdict}
"""

DISPOSED = """

## What was done with it

REFUTED: {slug_verdict} - tools/bench/selftest_stoprecord_supersession.py:1 says this case is a scratch fixture,
which does not cover the real build because no real build is involved.
"""

UNDISPOSED = """

## What was done with it

(Claude fills in)
"""


def patched():
    """Is the loaded stop_record carrying the supersession rule? Read from the source, never assumed."""
    try:
        return "later_same_path" in inspect.getsource(stop_record._check)
    except (OSError, TypeError):
        return False


def run_case(case, want_later, later_disposed, tag):
    """Returns (allow, msg, records). Builds a fresh isolated store, an old RELEASED record at sha s1, edits the
    recipe to s2, optionally plants a later same-path record, then asks the gate."""
    tmp = tempfile.mkdtemp(prefix="supersede_%d_" % case)
    stem = "scratch_supersede_%d_%d_%d" % (case, os.getpid(), int(time.time()))
    recipe_rel = "tools/recipes/%s.py" % stem
    recipe_abs = os.path.join(ROOT, "tools", "recipes", "%s.py" % stem)
    launch = ("MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/%s.log -- py -u %s"
              % (stem, recipe_rel))
    real_store, real_marker = stop_record.STORE, stop_record.MARKER
    out = {}
    try:
        stop_record.STORE = os.path.join(tmp, "stop_records.json")
        stop_record.MARKER = os.path.join(tmp, "stop_records.marker")
        with open(recipe_abs, "w", encoding="utf-8") as f:
            f.write("# scratch recipe for the supersession self-test (case %d). Deleted by the same run.\n"
                    "print('scratch')\n" % case)
        s1 = stop_record.sha256_of(recipe_abs)

        # --- the OLD record: reviewed at s1, fully disposed, and RELEASED by a real launch -------------------
        rev_a = os.path.join(tmp, "review-old.md")
        with open(rev_a, "w", encoding="utf-8") as f:
            f.write(REVIEW.format(slug="priorart-old-%d" % case, date=time.strftime("%Y-%m-%d"),
                                  slug_verdict="already-failed")
                    + DISPOSED.format(slug_verdict="already-failed"))
        stop_record.write_stop_record(recipe_rel, rev_a, ["already-failed"])
        allow0, msg0 = stop_record.check_command(launch)
        stamped = ((stop_record.load_records()[0] or {}).get("released") or {}).get("sha256")
        gate("C%d.0 precondition: the OLD record is RELEASED and stamped at s1 %s" % (case, (s1 or "")[:12]),
             allow0 and stamped == s1, first_line(msg0) if not allow0 else "")

        # --- the recipe is EDITED after that release (the bug fix judgement already released) ---------------
        with open(recipe_abs, "a", encoding="utf-8") as f:
            f.write("# the post-release bug fix\n")
        s2 = stop_record.sha256_of(recipe_abs)
        gate("C%d.1 the bytes changed (s1 != s2)" % case, s1 != s2, "%s -> %s" % (s1[:12], s2[:12]))

        # --- optionally, the LATER record over the edited bytes ---------------------------------------------
        if want_later:
            rev_b = os.path.join(tmp, "review-new.md")
            body = REVIEW.format(slug="priorart-new-%d" % case, date=time.strftime("%Y-%m-%d"),
                                 slug_verdict="contradicted")
            body += DISPOSED.format(slug_verdict="contradicted") if later_disposed else UNDISPOSED
            with open(rev_b, "w", encoding="utf-8") as f:
                f.write(body)
            stop_record.write_stop_record(recipe_rel, rev_b, ["contradicted"])
            recs = stop_record.load_records()
            gate("C%d.2 two records stand for the same path, the new one LAST" % case,
                 len(recs) == 2 and recs[1].get("reviewed_sha256") == s2
                 and stop_record._rel(recs[1].get("recipe_path")) == stop_record._rel(recs[0].get("recipe_path")),
                 "%d record(s)" % len(recs))
        else:
            gate("C%d.2 exactly ONE record stands for this path" % case,
                 len(stop_record.load_records()) == 1)

        allow, msg = stop_record.check_command(launch)
        out = {"allow": allow, "msg": msg, "s1": s1, "s2": s2,
               "records": stop_record.load_records()}
        print("  [case %d %s] gate says: %s" % (case, tag, "ALLOW" if allow else first_line(msg)), flush=True)
    finally:
        stop_record.STORE, stop_record.MARKER = real_store, real_marker
        try:
            os.remove(recipe_abs)
        except OSError:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
    out["recipe_gone"] = not os.path.exists(recipe_abs)
    return out


def exempt_patched():
    """Is the loaded stop_record carrying the COMMAND-POSITION EXEMPTION (cycle 46)? Read, never assumed."""
    return hasattr(stop_record, "exempt_program")


def run_exemption_case():
    """CASE 4 - the second half of the deadlock (cycle 46). A STANDING, UNDISPOSED record refuses everything that
    names its path; the two programs that can only ADD a record (`tools/stop_record.py`, `tools/prior_art_review.py`)
    must nevertheless be able to run, because the documented remedy IS `stop_record.py write` for that same path.
    The over-release guards are in the same case: a build launch naming the path, and a command that merely
    MENTIONS stop_record.py somewhere other than command position, must both still be refused."""
    tmp = tempfile.mkdtemp(prefix="exempt_")
    stem = "scratch_exempt_%d_%d" % (os.getpid(), int(time.time()))
    recipe_rel = "tools/recipes/%s.py" % stem
    recipe_abs = os.path.join(ROOT, "tools", "recipes", "%s.py" % stem)
    real_store, real_marker = stop_record.STORE, stop_record.MARKER
    out = {}
    try:
        stop_record.STORE = os.path.join(tmp, "stop_records.json")
        stop_record.MARKER = os.path.join(tmp, "stop_records.marker")
        with open(recipe_abs, "w", encoding="utf-8") as f:
            f.write("# scratch recipe for the exemption self-test. Deleted by the same run.\nprint('scratch')\n")
        rev = os.path.join(tmp, "review-undisposed.md")
        with open(rev, "w", encoding="utf-8") as f:
            f.write(REVIEW.format(slug="priorart-exempt", date=time.strftime("%Y-%m-%d"),
                                  slug_verdict="already-failed") + UNDISPOSED)
        stop_record.write_stop_record(recipe_rel, rev, ["already-failed"])
        out["cmds"] = {
            # the two EXEMPT programs, in command position, naming the stopped path
            "plant": "py tools/stop_record.py write --recipe %s --review %s --verdict contradicted"
                     % (recipe_rel, "archive/peer/2026-09-19-x.md"),
            "plant_flags": "py -u tools\\stop_record.py write --recipe %s --review r.md --verdict x" % recipe_rel,
            "priorart": "python -u tools/prior_art_review.py --recipe %s --slug x" % recipe_rel,
            # the shape EVERY real command arrives in: the Bash tool prefixes `cd "<project>" &&`
            "cd_plant": 'cd "%s" && py tools/stop_record.py write --recipe %s --review r.md --verdict x'
                        % (ROOT, recipe_rel),
            # the over-release guards - these must STILL be refused
            "build": "py tools/bgrun.py --material --max-min 5 --log tools/bench/%s.log -- py -u %s"
                     % (stem, recipe_rel),
            "mention": "py -u %s --helper tools/stop_record.py" % recipe_rel,
            # an exempt segment must not launder a build segment sitting beside it
            "chained": "py -u %s && py tools/stop_record.py write --recipe %s --review r.md --verdict x"
                       % (recipe_rel, recipe_rel),
        }
        out["res"] = {k: stop_record.check_command(v) for k, v in out["cmds"].items()}
    finally:
        stop_record.STORE, stop_record.MARKER = real_store, real_marker
        try:
            os.remove(recipe_abs)
        except OSError:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
    out["recipe_gone"] = not os.path.exists(recipe_abs)
    return out


def run_novel_case():
    """CASE 5 (cycle 72 firefighter). Old RELEASED record at s1; bytes edited to s2; a NOVEL review of s2 written
    through `write_novel_record` -> the launch is ALLOWED (5a). Bytes edited AGAIN to s3 -> REFUSED (5b, the
    original protection). The novel review file tampered to carry a blocking slug -> REFUSED (5c, no laundering).
    A novel record cannot be written from a review whose answer is not purely novel (5d)."""
    if not hasattr(stop_record, "write_novel_record"):
        return None
    tmp = tempfile.mkdtemp(prefix="novel_")
    stem = "scratch_novel_%d_%d" % (os.getpid(), int(time.time()))
    recipe_rel = "tools/recipes/%s.py" % stem
    recipe_abs = os.path.join(ROOT, "tools", "recipes", "%s.py" % stem)
    launch = "py tools/bgrun.py --material --max-min 5 --log tools/bench/%s.log -- py -u %s" % (stem, recipe_rel)
    real_store, real_marker = stop_record.STORE, stop_record.MARKER
    out = {}
    try:
        stop_record.STORE = os.path.join(tmp, "stop_records.json")
        stop_record.MARKER = os.path.join(tmp, "stop_records.marker")
        with open(recipe_abs, "w", encoding="utf-8") as f:
            f.write("# scratch recipe for the novel-record self-test. Deleted by the same run.\nprint('scratch')\n")
        rev_a = os.path.join(tmp, "review-old.md")
        with open(rev_a, "w", encoding="utf-8") as f:
            f.write(REVIEW.format(slug="priorart-old-5", date=time.strftime("%Y-%m-%d"), slug_verdict="already-failed")
                    + DISPOSED.format(slug_verdict="already-failed"))
        stop_record.write_stop_record(recipe_rel, rev_a, ["already-failed"])
        out["pre"] = stop_record.check_command(launch)[0]
        with open(recipe_abs, "a", encoding="utf-8") as f:
            f.write("# the post-release bug fix\n")
        out["edited_refused"] = not stop_record.check_command(launch)[0]
        rev_n = os.path.join(tmp, "review-novel.md")
        with open(rev_n, "w", encoding="utf-8") as f:
            f.write(REVIEW.format(slug="priorart-novel-5", date=time.strftime("%Y-%m-%d"), slug_verdict="novel"))
        stop_record.write_novel_record(recipe_rel, rev_n)
        out["a"] = stop_record.check_command(launch)
        with open(recipe_abs, "a", encoding="utf-8") as f:
            f.write("# a SECOND edit after the novel review\n")
        out["b"] = stop_record.check_command(launch)
        with open(recipe_abs, "r", encoding="utf-8") as f:
            body = f.read()
        with open(recipe_abs, "w", encoding="utf-8") as f:
            f.write(body.replace("# a SECOND edit after the novel review\n", ""))      # back to the reviewed bytes
        out["a2"] = stop_record.check_command(launch)[0]
        with open(rev_n, "a", encoding="utf-8") as f:
            f.write("\nPRIOR-ART: already-built\n")                                    # tampered after the record
        out["c"] = stop_record.check_command(launch)
        try:
            stop_record.write_novel_record(recipe_rel, rev_a)
            out["d"] = False
        except stop_record.StoreError:
            out["d"] = True
    finally:
        stop_record.STORE, stop_record.MARKER = real_store, real_marker
        try:
            os.remove(recipe_abs)
        except OSError:
            pass
        shutil.rmtree(tmp, ignore_errors=True)
    out["recipe_gone"] = not os.path.exists(recipe_abs)
    return out


def main():
    mode = "PATCHED" if patched() else "UNPATCHED"
    print("=== stop_record._check supersession self-test - loaded module is %s ===" % mode, flush=True)
    print("    (expectations differ by mode; both halves of the prediction contract are measured, "
          "one run before the patch and one after)", flush=True)
    real_store, real_marker = stop_record.STORE, stop_record.MARKER
    before = (fingerprint(real_store), fingerprint(real_marker))

    # ---- CASE 1 -------------------------------------------------------------------------------------------
    r1 = run_case(1, want_later=True, later_disposed=True, tag=mode)
    if mode == "PATCHED":
        gate("C1 PATCHED RELEASES (old released record superseded by the later disposed one)",
             r1["allow"], first_line(r1["msg"]))
        recs = r1["records"]
        gate("C1b the LATER record is stamped with the edited bytes s2",
             len(recs) == 2 and ((recs[1].get("released") or {}).get("sha256") == r1["s2"]),
             ((recs[1].get("released") or {}).get("sha256") or "none")[:12] if len(recs) == 2 else "?")
        gate("C1c the OLD record still carries its OWN release (s1) - no history was rewritten",
             len(recs) == 2 and ((recs[0].get("released") or {}).get("sha256") == r1["s1"]))
    else:
        gate("C1 UNPATCHED REFUSES (the deadlock, reproduced)", not r1["allow"], first_line(r1["msg"]))
        gate("C1b the refusal is the sha-mismatch one, naming both hashes",
             (not r1["allow"]) and r1["s1"][:12] in (r1["msg"] or "") and r1["s2"][:12] in (r1["msg"] or ""))
        gate("C1c the later record was NOT stamped (nothing was released)",
             all((r.get("released") or {}).get("sha256") != r1["s2"] for r in r1["records"]))

    # ---- CASE 2 -------------------------------------------------------------------------------------------
    r2 = run_case(2, want_later=True, later_disposed=False, tag=mode)
    gate("C2 %s MUST STILL REFUSE (later record's findings are NOT disposed)" % mode,
         not r2["allow"], first_line(r2["msg"]))
    gate("C2b the refusal is the UNDISPOSED-verdict one, not the sha-mismatch one",
         (not r2["allow"]) and "neither refuted nor fixed" in (r2["msg"] or "")
         if mode == "PATCHED" else (not r2["allow"]))
    gate("C2c nothing was stamped for the edited bytes",
         all((r.get("released") or {}).get("sha256") != r2["s2"] for r in r2["records"]))

    # ---- CASE 3 -------------------------------------------------------------------------------------------
    r3 = run_case(3, want_later=False, later_disposed=False, tag=mode)
    gate("C3 %s MUST STILL REFUSE (no later record; the original protection)" % mode,
         not r3["allow"], first_line(r3["msg"]))
    gate("C3b the refusal is the sha-mismatch one, naming both hashes",
         (not r3["allow"]) and r3["s1"][:12] in (r3["msg"] or "") and r3["s2"][:12] in (r3["msg"] or ""))
    gate("C3c the single record still carries its original release stamp (s1)",
         len(r3["records"]) == 1 and ((r3["records"][0].get("released") or {}).get("sha256") == r3["s1"]))

    # ---- CASE 4: the COMMAND-POSITION EXEMPTION (cycle 46) -------------------------------------------------
    emode = "EXEMPT-PATCHED" if exempt_patched() else "EXEMPT-UNPATCHED"
    print("--- case 4: command-position exemption, loaded module is %s ---" % emode, flush=True)
    r4 = run_exemption_case()
    res = r4["res"]
    for k in ("plant", "plant_flags", "priorart", "cd_plant", "build", "mention", "chained"):
        print("  [case 4 %s] %-11s -> %s" % (emode, k, "ALLOW" if res[k][0] else first_line(res[k][1])),
              flush=True)
    if exempt_patched():
        gate("C4 PATCHED: `py tools/stop_record.py write --recipe <stopped path>` PASSES", res["plant"][0],
             first_line(res["plant"][1]))
        gate("C4a PATCHED: the same with -u and backslashes PASSES", res["plant_flags"][0],
             first_line(res["plant_flags"][1]))
        gate("C4b PATCHED: `python -u tools/prior_art_review.py --recipe <stopped path>` PASSES",
             res["priorart"][0], first_line(res["priorart"][1]))
        gate("C4f PATCHED: the real shape `cd \"<project>\" && py tools/stop_record.py write …` PASSES",
             res["cd_plant"][0], first_line(res["cd_plant"][1]))
    else:
        gate("C4 UNPATCHED: the planting command is REFUSED (the deadlock, reproduced)", not res["plant"][0],
             first_line(res["plant"][1]))
        gate("C4a UNPATCHED: the -u/backslash form is REFUSED too", not res["plant_flags"][0])
        gate("C4b UNPATCHED: the prior-art command is REFUSED too", not res["priorart"][0])
        gate("C4f UNPATCHED: the `cd … && py tools/stop_record.py write …` form is REFUSED too",
             not res["cd_plant"][0])
    gate("C4c %s: a BUILD LAUNCH naming the same path is STILL REFUSED" % emode, not res["build"][0],
         first_line(res["build"][1]))
    gate("C4d %s: the refusal is the undisposed-verdict one" % emode,
         (not res["build"][0]) and "neither refuted nor fixed" in (res["build"][1] or ""))
    gate("C4e %s: stop_record.py mentioned OUTSIDE command position does NOT exempt" % emode,
         not res["mention"][0], first_line(res["mention"][1]))
    gate("C4g %s: an exempt segment does NOT launder a build segment chained beside it" % emode,
         not res["chained"][0], first_line(res["chained"][1]))

    # ---- CASE 5: a NOVEL review over edited bytes (cycle 72) -------------------------------------------------
    r5 = run_novel_case()
    if r5 is None:
        print("--- case 5: loaded module has no write_novel_record (pre-cycle-72) - skipped ---", flush=True)
        r5 = {"recipe_gone": True}
    else:
        gate("C5.0 precondition: old record released, edited bytes refused", r5["pre"] and r5["edited_refused"])
        gate("C5a a NOVEL review of the edited bytes RELEASES the launch", r5["a"][0], first_line(r5["a"][1]))
        gate("C5b a SECOND edit after the novel review is REFUSED (sha mismatch, no later record)",
             not r5["b"][0] and "different bytes" in (r5["b"][1] or ""), first_line(r5["b"][1]))
        gate("C5a2 restoring the reviewed bytes releases again", r5["a2"])
        gate("C5c a novel review file TAMPERED to carry a blocking slug no longer releases",
             not r5["c"][0], first_line(r5["c"][1]))
        gate("C5d write_novel_record REFUSES a review whose answer is not purely novel", r5["d"])

    # ---- hygiene ------------------------------------------------------------------------------------------
    gate("C0a every scratch recipe was deleted in the same run",
         all(r.get("recipe_gone") for r in (r1, r2, r3, r4, r5)))
    after = (fingerprint(real_store), fingerprint(real_marker))
    gate("C0b the REAL store was never touched", before == after, "%s -> %s" % (before, after))
    gate("C0c no scratch recipe survives under tools/recipes/",
         not [p for p in os.listdir(os.path.join(ROOT, "tools", "recipes"))
              if p.startswith(("scratch_supersede_", "scratch_exempt_", "scratch_novel_"))])

    # ---- the EXISTING device's own six cases, same run ------------------------------------------------------
    print("--- re-running tools/bench/stop_record_selftest.py (cycle-18 acceptance, %s) ---" % mode, flush=True)
    p = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "bench", "stop_record_selftest.py")],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    tail = (p.stdout or "") + (p.stderr or "")
    m = re.search(r"=== stop_record selftest: (\d+) pass, (\d+) fail ===", tail)
    for ln in tail.splitlines():
        if "FAIL" in ln or "selftest:" in ln:
            print("    | " + ln.strip(), flush=True)
    gate("C9 the existing stop_record self-test still scores 0 fail (%s)" % mode,
         bool(m) and m.group(2) == "0", (m.group(0) if m else "no score line, rc %s" % p.returncode))

    npass = sum(1 for _, ok, _ in RESULTS if ok)
    nfail = len(RESULTS) - npass
    print("=== supersession selftest (%s): %d pass, %d fail ===" % (mode, npass, nfail), flush=True)
    return 1 if nfail else 0


if __name__ == "__main__":
    sys.exit(main())
