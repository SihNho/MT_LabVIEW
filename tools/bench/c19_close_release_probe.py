r"""c19_close_release_probe.py - cycle-19 close-out C1 + C2. READ-ONLY on the real files.

PRIOR ART CHECKED (CLAUDE.md "check what already exists"):
  * `tools/stop_record.py` IS the launch gate (check_command / _released / load_records) and
    `tools/hooks/guard_cycle.py` IS the release validator (released_slugs / fixed_citations /
    review_time). Both are IMPORTED here; nothing is reimplemented.
  * `ls tools/bench | grep -i release` -> no existing release/stop-record probe. `tools/op_selftest.py`
    is the op self-test harness, unrelated.
  * The negative cases (a)(b)(c) below are the three the CLAUDE.md `FIXED:` table names; cycle 16 tested
    them at build time but left no runnable fixture, so this file is the fixture.

PREDICTION CONTRACT (machine-checked below; any line printed as MISS is a failed prediction):
  C1a  load_records() returns exactly 1 record whose recipe_path == tools/motor_wiring_check.py
       and whose `released` field is null BEFORE and AFTER this probe.
  C1b  guard_cycle.released_slugs(review) releases all four slugs
       {unread-evidence, contradicted, helper-exists, already-measured} with 0 rejected lines.
  C1c  stop_record._released(record) -> (True, <line>, "")   i.e. the RELEASE ITSELF IS VALID.
  C1d  stop_record.check_command("py tools/motor_wiring_check.py") -> (False, ...) anyway, because the
       cited recipe does not exist on disk, so the release cannot be stamped to any bytes.
  C1e  review_time() basis is the frontmatter date+TIME (01:12), not midnight; the plan's mtime is after it.
  C2a  a FIXED: line citing a nonexistent path releases nothing.
  C2b  a FIXED: line citing a path older than the review releases nothing.
  C2c  a FIXED: line placed ABOVE '## What was done with it' releases nothing.
  C2 uses a THROWAWAY review file in a temp dir, deleted in the same run. The real store is never written.
"""
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))

import stop_record            # noqa: E402
import guard_cycle            # noqa: E402

REVIEW = "archive/peer/2026-09-18-priorart-check-a-wiring.md"
RECIPE = "tools/" + "motor_wiring_check.py"      # split so this file's own text cannot trip the launch gate
PLAN = "docs/motor-limit-assurance-plan.md"
WANT = {"unread-evidence", "contradicted", "helper-exists", "already-measured"}

results = []


def check(label, ok, detail=""):
    results.append((label, bool(ok)))
    print("%-6s %-5s %s" % (label, "HIT" if ok else "MISS", detail))


def snapshot():
    with open(stop_record.STORE, "r", encoding="utf-8") as f:
        return f.read()


print("=" * 100)
print("C1 - DOES THE RELEASE ACTUALLY RELEASE?")
print("=" * 100)

before = snapshot()
recs = stop_record.load_records()
mine = [r for r in recs if stop_record._rel(r.get("recipe_path")) == RECIPE.lower()]
print("records in store            : %d" % len(recs))
print("records for the check-A path: %d" % len(mine))
for r in mine:
    print(json.dumps(r, indent=2, sort_keys=True))
check("C1a", len(mine) == 1 and mine[0].get("released") is None,
      "released field BEFORE = %r" % (mine[0].get("released") if mine else "NO RECORD"))

rev_abs = os.path.join(ROOT, REVIEW.replace("/", os.sep))
body = open(rev_abs, "r", encoding="utf-8", errors="replace").read()
rel_slugs, bad = guard_cycle.released_slugs(rev_abs, body)
print("\nguard_cycle.released_slugs(review) -> released=%s" % sorted(rel_slugs))
for s, w in bad:
    print("   REJECTED FIXED: %s - %s" % (s, w))
check("C1b", rel_slugs >= WANT and not bad,
      "all four verdict slugs released, %d rejected line(s)" % len(bad))

rt, basis = guard_cycle.review_time(rev_abs, body)
plan_abs = os.path.join(ROOT, PLAN.replace("/", os.sep))
pm = os.path.getmtime(plan_abs)
print("\nreview_time basis           : %s" % basis)
print("review instant              : %s" % time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(rt)))
print("%s mtime : %s" % (PLAN, time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(pm))))
print("comparison the code performs: `if fm <= rt: reject`  (guard_cycle.py:147)")
print("SAME-DAY ACCEPTED?          : %s" % ("YES - fm(%.0f) > rt(%.0f)" % (pm, rt) if pm > rt else
                                            "NO - fm(%.0f) <= rt(%.0f)" % (pm, rt)))
check("C1e", pm > rt and "date+time" in basis, "basis carries a TIME, so midnight is not used")

ok, line, why = stop_record._released(mine[0]) if mine else (False, "", "no record")
print("\nstop_record._released(record) -> ok=%s" % ok)
print("   line: %s" % (line[:150] if line else "(none)"))
print("   why : %s" % (why or "(no reason - the release is valid)"))
check("C1c", ok is True, "the four FIXED: lines DO constitute a valid release")

cmd = "py %s --all" % RECIPE
allow, msg = stop_record.check_command(cmd)
print("\nstop_record.check_command(%r) -> allow=%s" % (cmd, allow))
print("--- VERBATIM GATE MESSAGE ---")
print(msg if msg else "ALLOW (no message)")
print("--- END VERBATIM ---")
check("C1d", allow is False, "gate verdict = %s" % ("ALLOW" if allow else "REFUSE"))

after = snapshot()
check("C1a2", before == after, "stop_records.json byte-identical before/after this probe")
recs2 = stop_record.load_records()
mine2 = [r for r in recs2 if stop_record._rel(r.get("recipe_path")) == RECIPE.lower()]
print("released field AFTER        : %r" % (mine2[0].get("released") if mine2 else "NO RECORD"))

print("\n" + "=" * 100)
print("C2 - NEGATIVE PROOF OF THE RELEASE PATH (throwaway fixture, deleted in this run)")
print("=" * 100)

tmp = tempfile.mkdtemp(prefix="c19_relneg_")
try:
    HDR = ("# throwaway-fixture\n\n- **agent:** claude\n- **kind:** fact\n"
           "- **date:** 2026-09-18 01:12:34\n- **outcome:** ANSWERED\n\n## Question\n\nq\n\n## Answer\n\na\n\n")
    DISP = "## What was done with it\n\n"
    # An OLD real file: CLAUDE.md-era doc that predates 2026-09-18 01:12. Verified below, not assumed.
    OLD = "AGENTS.md"
    old_m = os.path.getmtime(os.path.join(ROOT, OLD))
    print("fixture old-path %s mtime = %s (review instant %s)"
          % (OLD, time.strftime("%Y-%m-%d %H:%M", time.localtime(old_m)),
             time.strftime("%Y-%m-%d %H:%M", time.localtime(rt))))

    cases = [
        ("C2a", "FIXED line citing a path that DOES NOT EXIST",
         HDR + DISP + "FIXED: contradicted - docs/no-such-file-at-all.md:12 - claims a fix.\n"),
        ("C2b", "FIXED line citing a path OLDER than the review",
         HDR + DISP + "FIXED: contradicted - %s:3 - claims a fix.\n" % OLD),
        ("C2c", "FIXED line placed OUTSIDE '## What was done with it'",
         HDR + "FIXED: contradicted - %s:3 - claims a fix.\n\n" % PLAN + DISP + "nothing here.\n"),
    ]
    for label, desc, text in cases:
        fp = os.path.join(tmp, label + ".md")
        with open(fp, "w", encoding="utf-8") as f:
            f.write(text)
        rec = {"recipe_path": RECIPE, "review_file": fp, "verdict": ["contradicted"],
               "reviewed_sha256": None, "released": None}
        o, l, w = stop_record._released(rec)
        rs, rb = guard_cycle.released_slugs(fp, text)
        print("\n%s  %s" % (label, desc))
        print("    released_slugs -> %s ; rejected -> %s" % (sorted(rs), [b[1][:110] for b in rb]))
        print("    _released      -> ok=%s why=%s" % (o, (w or "(none)").replace("\n", " ")[:200]))
        check(label, o is False and "contradicted" not in rs, "REFUSED as required" if o is False else
              "*** RELEASED - the gate accepted an invalid FIXED line ***")
    # C2c control: the same line INSIDE the section must release, or C2c proves nothing.
    ctrl = HDR + DISP + "FIXED: contradicted - %s:3 - claims a fix.\n" % PLAN
    fp = os.path.join(tmp, "C2c_control.md")
    open(fp, "w", encoding="utf-8").write(ctrl)
    rec = {"recipe_path": RECIPE, "review_file": fp, "verdict": ["contradicted"],
           "reviewed_sha256": None, "released": None}
    o, l, w = stop_record._released(rec)
    print("\nC2ctl CONTROL: the SAME line inside the section -> ok=%s (must be True, else C2c is vacuous)" % o)
    check("C2ctl", o is True, "control releases, so C2c's refusal is about PLACEMENT")
finally:
    shutil.rmtree(tmp, ignore_errors=True)
    print("\nthrowaway fixture deleted: %s exists=%s" % (tmp, os.path.exists(tmp)))

print("\n" + "=" * 100)
miss = [l for l, ok in results if not ok]
print("PREDICTION CONTRACT: %d/%d HIT" % (len(results) - len(miss), len(results)))
print("MISSES: %s" % (", ".join(miss) if miss else "none"))
sys.exit(1 if miss else 0)
