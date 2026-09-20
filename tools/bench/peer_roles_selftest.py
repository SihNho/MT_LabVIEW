r"""peer_roles_selftest.py - self-test for the 2026-09-18 role routing (user's TRIAL: codex's roles move to
claude sub-sessions, "우선은 지금 말한 방법으로 몇 번 돌려보자").

PREDICTION CONTRACT (checked mechanically below; any row that disagrees prints FAIL and the run exits 1):

  A. guard_peer.review_quality() - IN MEMORY, no file is written anywhere near archive/peer/, because a
     synthetic archive file dropped there would lift a real failed-prediction gate.
     A1 claude + role hypothesis + ANSWERED                      -> ACCEPTED      (D3 amended today)
     A2 claude + role audit      + ANSWERED                      -> REJECTED
     A3 claude + NO role line + model 'opus (effort max; ...)'   -> ACCEPTED      (pre-today archives)
     A4 claude + NO role line + model 'sonnet (...)'             -> REJECTED
     A5 codex   + ANSWERED                                       -> ACCEPTED      (unchanged)
     A6 gemini  + ANSWERED                                       -> ACCEPTED      (unchanged)
     A7 claude + role hypothesis + TIMEOUT                       -> REJECTED      (outcome rule unchanged)
     A8 no outcome line at all (pre-2026-09-15 archive)          -> ACCEPTED      (not retro-invalidated)

  B. peer.ps1 -DryRun - resolution only, NO dispatch, NO archive file, NO cost:
     B1 -Kind fact,  no -Agent                  -> agent claude · role fact       · fable/low    · thin YES
     B2 -Kind prose, no -Agent                  -> agent claude · role prose      · fable/low    · thin YES
     B3 -Agent claude -Role hypothesis          -> agent claude · role hypothesis · opus/max     · thin no
     B4 -Agent codex -Kind fact                 -> agent codex  · gpt-5.6-sol/medium            · thin no
     B5 -Agent claude -Role priorart -Kind fact -> agent claude · role priorart   · opus/high    · thin no
     B6 py tools/outcome_review.py --dry-run    -> agent claude · role outcome    · fable/medium · thin YES

  C. ONE REAL CALL, the cheapest that exercises the new default route end to end:
     peer.ps1 -Agent claude -Role fact -Kind fact -Slug selftest-fact-role
     Expect OUTCOME: ANSWERED and a COST line. The cost line is the POINT of the run: the comparison number is
     the 2026-09-17 opus/max arm, $1.8621 with cache-create 158,866 (CLAUDE.md section 5). -Kind fact, not the
     brief's bare default -Kind review: `review` appends the four-part adversarial instruction set, which is
     not what this route is for and would inflate the very cost being measured.

WHAT ALREADY EXISTED (checked before writing this, CLAUDE.md "check what already exists"):
  tools/bench/peer_dual_selftest.log (2026-09-17) is the -Dual self-test - a REAL dual dispatch, no dry mode
  and no unit test; tools/bench/selftest_cycle_runner_ff.py and tools/bench/selftest_motor_gate2.py are the
  pattern this file copies (in-process asserts + a printed PASS/FAIL table). peer.ps1 had NO dry mode before
  today; -DryRun was added in the same patch as these roles.

Run it the only way it may be run:
  MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/peer_roles_selftest.log -- py -u tools/bench/peer_roles_selftest.py
"""
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PEER_PS1 = os.path.join(ROOT, "tools", "peer.ps1")
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import guard_peer  # noqa: E402

PASS = []
FAIL = []


def check(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print(("  PASS  " if ok else "  FAIL  ") + label + (("   " + detail) if detail else ""), flush=True)


def archive(agent, outcome="ANSWERED", role=None, model="sonnet (peer.ps1 default for role audit)",
            with_outcome=True):
    """A synthetic archive BODY - a string, never a file. Same shape peer.ps1 writes."""
    lines = ["# slug", "", f"- **agent:** {agent}"]
    if role is not None:
        lines.append(f"- **role:** {role}")
    lines += [f"- **model:** {model}", "- **kind:** review", "- **cost:** $0.0001"]
    if with_outcome:
        lines.append(f"- **outcome:** {outcome} (12s)")
    lines += ["", "## Answer", "", "text", ""]
    return "\n".join(lines)


def section_a():
    print("\n=== A. guard_peer.review_quality() - who may discharge a failed prediction ===", flush=True)
    rows = [
        ("A1 claude/hypothesis ANSWERED", archive("claude", role="hypothesis",
                                                  model="opus (effort max; peer.ps1 default for role hypothesis)"),
         True),
        ("A2 claude/audit ANSWERED", archive("claude", role="audit"), False),
        ("A3 claude, no role line, opus effort max", archive("claude",
                                                             model="opus (effort max; peer.ps1 default for role hypothesis)"),
         True),
        ("A4 claude, no role line, sonnet", archive("claude"), False),
        ("A5 codex ANSWERED", archive("codex", model="gpt-5.6-sol (effort medium; peer.ps1 default)"), True),
        ("A6 gemini ANSWERED", archive("gemini", model="(agy default, not readable)"), True),
        ("A7 claude/hypothesis TIMEOUT", archive("claude", outcome="TIMEOUT", role="hypothesis",
                                                 model="opus (effort max; ...)"), False),
        ("A8 pre-2026-09-15 archive, no outcome line", archive("claude", with_outcome=False), True),
    ]
    for label, body, expected in rows:
        ok, why = guard_peer.review_quality(body)
        check(label + f" -> {'ACCEPTED' if ok else 'REJECTED'}", ok == expected, why)


def dry(args):
    """Run peer.ps1 -DryRun and return the parsed DRYRUN lines as a dict."""
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& '%s' %s -DryRun" % (PEER_PS1, args)]
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=180,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    d = dict(re.findall(r"^DRYRUN (\w+)\s*:\s*(.*)$", out, re.M))
    if not d:
        print("    (no DRYRUN lines) rc=%s\n%s" % (r.returncode, out[:600]), flush=True)
    return d


def expect(label, d, **fields):
    bad = []
    for k, want in fields.items():
        got = d.get(k, "<missing>")
        if want.lower() not in got.lower():
            bad.append("%s=%r (wanted %r)" % (k, got, want))
    check(label, not bad, "; ".join(bad))
    if d:
        print("        model=%s | args=%s" % (d.get("model", "?"), d.get("args", "?")[:150]), flush=True)


def section_b():
    print("\n=== B. peer.ps1 -DryRun - routing, no dispatch ===", flush=True)
    expect("B1 -Kind fact, no -Agent", dry('-Kind fact -Slug dryfact -Task "x"'),
           agent="claude", role="fact", model="fable (effort low", thin="YES")
    expect("B2 -Kind prose, no -Agent", dry('-Kind prose -Slug dryprose -Task "x"'),
           agent="claude", role="prose", model="fable (effort low", thin="YES")
    expect("B3 -Agent claude -Role hypothesis", dry('-Agent claude -Role hypothesis -Slug dryhyp -Task "x"'),
           agent="claude", role="hypothesis", model="opus (effort max", thin="no")
    expect("B4 -Agent codex -Kind fact", dry('-Agent codex -Kind fact -Slug drycodex -Task "x"'),
           agent="codex", model="gpt-5.6-sol (effort medium", thin="no")
    expect("B5 -Agent claude -Role priorart", dry('-Agent claude -Role priorart -Kind fact -Slug drypa -Task "x"'),
           agent="claude", role="priorart", model="opus (effort high", thin="no")

    # B6: the real caller, resolved by the real caller. --dry-run prints the question set first; only the
    # DRYRUN lines are parsed.
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "outcome_review.py"), "--dry-run"],
                       cwd=ROOT, text=True, capture_output=True, timeout=300,
                       encoding="utf-8", errors="replace")
    d = dict(re.findall(r"^DRYRUN (\w+)\s*:\s*(.*)$", (r.stdout or "") + (r.stderr or ""), re.M))
    expect("B6 outcome_review.py --dry-run", d,
           agent="claude", role="outcome", model="fable (effort medium", thin="YES")


def section_c():
    print("\n=== C. ONE REAL CALL on the new default fact route (fable / low / thin) ===", flush=True)
    cmd = ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command",
           "& '%s' -Agent claude -Role fact -Kind fact -Slug selftest-fact-role -TimeoutSec 180 "
           "-Task \"Reply with the single word OK and cite nothing.\"" % PEER_PS1]
    r = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, timeout=420,
                       encoding="utf-8", errors="replace")
    out = (r.stdout or "") + (r.stderr or "")
    for ln in out.splitlines():
        if ln.startswith(("OUTCOME:", "COST:", "NOTE:")) or ln.strip() == "OK":
            print("    " + ln.strip(), flush=True)
    check("C1 real fact call ANSWERED", "OUTCOME: ANSWERED" in out, "rc=%s" % r.returncode)
    m = re.search(r"^COST: (.+)$", out, re.M)
    check("C2 cost line present", bool(m), (m.group(1) if m else out[-300:]))
    if m:
        print("    MEASURED fable/low/thin fact call: " + m.group(1), flush=True)
        print("    COMPARE opus/max full-context arm (2026-09-17): $1.8621, cache-create 158,866, 70s", flush=True)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("peer_roles_selftest - role routing trial, 2026-09-18", flush=True)
    section_a()
    section_b()
    section_c()
    print("\n=== RESULT: %d PASS / %d FAIL ===" % (len(PASS), len(FAIL)), flush=True)
    if FAIL:
        print("FAILING: " + ", ".join(FAIL), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
