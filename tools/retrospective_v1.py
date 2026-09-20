r"""retrospective_v1.py - FROZEN COPY of the v1 retrospective, kept runnable ONLY for the v1-vs-v2 comparison.

DO NOT USE THIS FOR A LIVE CYCLE. `tools/retrospective.py` is v2 (2026-09-16, user's decision: proposals 1, 2 and 4
adopted). This file is the exact text that produced the retrospectives of cycles 7-13, preserved so the comparison
in `tools/bench/retro_v2_comparison.md` is against the real instrument rather than a reconstruction of it.

WHY v1 WAS REPLACED, in its own numbers: seven retrospectives ran; five slugs fired in 7 of 7, and cycles 11, 12
and 13 each fired ALL NINE. The cause is in the text below - one question produces one slug, every question is
phrased "name one if any", there is no size estimate, no finding/violation distinction, the evidence window is
`--since-hours` (a time window, never a cycle boundary) and nothing ever asks whether the devices already built
worked. The counts saturated, so "3 occurrences -> build a device" became "a device every cycle".

Original docstring follows.

retrospective.py - end-of-cycle review of HOW the cycle was run, not of any single hypothesis.

WHY THIS EXISTS. The peer loop can only attack what Claude chooses to send it: a framing Claude wrote, evidence
Claude picked. So it criticises hypotheses well and criticises JUDGEMENT AND EXECUTION not at all (user,
2026-09-15: "피어 리뷰를 통해 판단 및 실행 구조에 대한 비평은 할 수 없는 것 같아"). Nobody ever asked whether a
question was worth asking, whether twenty failures were the same failure, or whether a tool should have been built
first. On 2026-09-15 that gap cost a night: three consecutive ExecState-0 diagnoses by inference, and five rebuilds
of one op, because no reviewer ever saw the TRAJECTORY.

WHAT IS DIFFERENT HERE. The material is not a summary Claude wrote. It is the machine's own record: the compliance
audit (tools/audit_cycle.py) plus the cycle's build logs, handed to the peer with CLAUDE.md so the rules are in
front of it. The questions are fixed, so Claude cannot steer them.

The peer must answer in prose AND end with machine-readable lines:

    VIOLATION: <slug>            one per repeated/structural fault, slug from CLAUDE.md's known list
    VIOLATION: none              if there are none

`tools/violations.py` counts those slugs across retrospectives; at three of the same slug the cycle gate demands a
mechanical device for it, the same way guard_peer demands an archived review. Claude does not do the counting.

  py tools/retrospective.py --cycle 7 [--since-hours 20] [--dry-run]
"""
import argparse
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
QUESTIONS = """Attack HOW this cycle was run. You are not being asked about any single hypothesis - those were
reviewed one at a time already, and every one of those reviews passed. You are being asked about the trajectory.

Answer these, in order, and be concrete about which log or file shows it:

1. REPEATED FAILURE. Did the same class of failure recur? On which attempt should the approach have changed, and to
   what? Name the attempt number.
2. MISSING TOOL. Is there a reader or op that was NOT built and whose absence made the cycle more expensive? Say
   which failures it would have answered.
3. UNMEASURED STEPS. Was anything decided by inference where a measurement was available and cheap?
4. RULE COMPLIANCE. Read the attached CLAUDE.md. Which of its rules were broken, evaded, or satisfied only
   formally? The compliance audit output is attached - say also what the audit does NOT cover.
5. ORDERING. Was the cycle's order of work defensible, or should some later step have come first?
6. WHAT WAS NOT REPORTED. From the raw logs, is there anything the session's own summary would have hidden or
   understated?
7. JUDGEMENT INSIDE A MATERIAL SESSION. Was any decision taken inside a MATERIAL sub-session (agent `material`,
   `log-reader`, `reporter`, or any `claude -p` cell) that belonged to the judgement session: a design change, a
   choice between explanations, accepting/rejecting a review finding, a change of plan direction, or an action
   pre-scripted in the brief as "if X then do Y"? Cite the log or archive file and line. If yes, emit
   `VIOLATION: judgement-in-material`.

Then END YOUR ANSWER with machine-readable lines, one per structural fault, using a slug from this list:
  repeated-failure-class · tool-not-built · inference-over-measurement · rule-evaded · wrong-ordering ·
  unreported-fact · scope-creep · premature-build · judgement-in-material
Format exactly:
  VIOLATION: <slug>
Use `VIOLATION: none` if there are none. Do not invent new slugs; map to the closest one and explain in the prose."""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cycle", required=True)
    ap.add_argument("--since-hours", type=float, default=20.0)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    # ENCODING IS NOT COSMETIC HERE - this text becomes the peer's EVIDENCE (lint, 2026-09-16). `text=True` with no
    # `encoding=` decodes the child's stdout with the console code page (cp949 on this box), and audit_cycle writes
    # `…` and Korean; the audit block reached the reviewer as mojibake, e.g. `md5 2a78e17c449c<?>`. This is the same
    # defect that voided prior-art run 3 ($2.53, `tools/bench/priorart_scores.md`) - a review fed corrupted evidence
    # is a review that told you nothing, and nothing in the transcript says so. Force UTF-8 on both ends.
    audit = subprocess.run([sys.executable, os.path.join(HERE, "audit_cycle.py"),
                            "--since-hours", str(a.since_hours)],
                           capture_output=True, text=True, encoding="utf-8", errors="replace",
                           timeout=300).stdout
    logs = []
    for p in sorted(os.listdir(os.path.join(HERE, "bench")), key=lambda n: n):
        fp = os.path.join(HERE, "bench", p)
        if p.endswith(".log") and not p.startswith("peer_") and os.path.getmtime(fp) >= time.time() - a.since_hours * 3600:
            logs.append(p)
    task = (f"RETROSPECTIVE of cycle {a.cycle} (read-only; you may open any file in the project).\n\n"
            f"{QUESTIONS}\n\n"
            f"=== COMPLIANCE AUDIT (tools/audit_cycle.py, machine-generated) ===\n{audit}\n"
            f"=== BUILD LOGS OF THIS CYCLE (read them directly, they are the primary record) ===\n"
            + "\n".join(f"tools/bench/{n}" for n in logs)
            + "\n\nThe rules are in CLAUDE.md at the project root; the cycle's own documents are STATUS.md and "
              "docs/stage2-assembly-step-e.md; every hypothesis-level review of this cycle is in archive/peer/.")
    slug = f"retrospective-cycle{a.cycle}"
    scratch = os.path.join(os.environ.get("TEMP", "."), f"retro_task_{a.cycle}.txt")
    with open(scratch, "w", encoding="utf-8") as f:
        f.write(task)
    print(f"   task written to {scratch} ({len(task)} chars, {len(logs)} logs listed)", flush=True)
    if a.dry_run:
        print(task[:1500]); return 0
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           # -TimeoutSec 600: peer.ps1's 180 s default is far too short for this question. A retrospective
           # attaches the audit, every build log of the cycle and CLAUDE.md, and the peer reads them; measured
           # siblings take 244-395 s, and cycle 8's attempt TIMED OUT at 180 s on 2026-09-15 with nothing
           # learned. -Kind fact because this prompt carries its own instruction set and has no claim to refute.
           f"& '{os.path.join(HERE, 'peer.ps1')}' -Agent codex -Kind fact -TimeoutSec 600 "
           f"-Slug {slug} -Task (Get-Content -Raw '{scratch}')"]
    r = subprocess.run(cmd, cwd=ROOT, text=True, timeout=900)
    print(f"   peer.ps1 rc {r.returncode}; archived as archive/peer/<date>-{slug}.md", flush=True)
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())
