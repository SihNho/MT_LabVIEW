r"""retro_v2_compare_runner.py - ONE runner for the v1-vs-v2 retrospective comparison (user's decision,
2026-09-16: "MEASURE, before adopting"). No LabVIEW is touched: this is documents + peer dispatch only.

PRIOR ART CHECKED BEFORE WRITING THIS (CLAUDE.md, "Before creating any new op, tool, or recipe"):
  - `tools/retrospective.py` (now v2) and `tools/retrospective_v1.py` (the frozen v1) are the instruments; nothing
    new is built here.
  - `tools/bench/retro_cycle13_runner.py` is the previous runner of exactly this shape - one bgrun chaining
    audit + retrospective, with a prediction contract. This file is that pattern applied three times, and its
    cp949 lesson (retro_cycle12.log:33-36: rc=1 on a UnicodeEncodeError while PRINTING a completed child's
    stdout) is carried over verbatim: every child runs with encoding='utf-8' and stdout is a UTF-8 wrapper.
  - `tools/audit_cycle.py` already carries the window; v2 passes --from/--to, so nothing is recomputed here.
  - `tools/violations.py` already parses both VIOLATION forms; no counting happens in this file.
  Nothing existing does the three-cycle comparison, so this runner is new; the two tools it chains are not.

WHAT IT DOES. For cycles 11, 12 and 13 - whose v1 retrospectives each fired ALL NINE slugs - it runs v2 with slug
`retrospective-v2-cycle<N>` (so the archives do not collide with the v1 ones), SEQUENTIALLY, and records each
run's OUTCOME line, wall-clock, cost if any, and VIOLATION lines verbatim.

WHY IT WRITES A DISPOSITION BETWEEN RUNS, and why that is not an evasion. `tools/hooks/guard_peer.py`'s
`undisposed()` device refuses a new `retrospective` dispatch while the newest archived review of that kind has an
empty "What was done with it" section. That hook sees the OUTER command only, so a runner that shells out three
times would slip past it silently - which is the `rule-evaded` slug in its purest form. So the runner checks the
same condition itself and writes each archive's disposition before dispatching the next one. The disposition is
BOOKKEEPING, not judgement: it records what the run was (a measurement for tools/bench/retro_v2_comparison.md) and
where the findings are disposed. No verdict is accepted or rejected here.

PREDICTION CONTRACT (machine-checkable, evaluated at the end of this file):
  P1  each of the three `retrospective.py --cycle N --slug retrospective-v2-cycle<N>` runs exits 0 and archives
      EXACTLY ONE new archive/peer/*retrospective-v2-cycle<N>*.md that did not exist before.     -> gates A<N>
  P2  each new archive's frontmatter `outcome:` reads ANSWERED.                                   -> gates B<N>
  P3  each new archive carries at least one `VIOLATION:` line (`VIOLATION: none` counts).         -> gates C<N>
  P4  each archive's disposition section is written before the NEXT dispatch, so guard_peer's
      undisposed() condition is false at every dispatch.                                          -> gates D<N>
  P5  `py tools/violations.py` still parses every archive, old and new, and exits 0.              -> gate E

OBSERVATION, REPORTED AND NOT A PREDICTION (the same shape as retro_cycle13_runner's gate D): how many VIOLATION
lines each v2 archive carries. v2's output contract asks for one, at most two. Whether the reviewer obeys it IS
the thing this comparison measures, so a count above two is a RESULT to report to the judgement session, not a
failed prediction to grind against. It is printed as `OBSERVED:` and never as a gate.
"""
import glob
import io
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))          # tools/bench
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
PEER = os.path.join(ROOT, "archive", "peer")
CYCLES = [11, 12, 13]
DISPOSITION_H = "## What was done with it"

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace", line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace", line_buffering=True)


def say(*a):
    print(*a, flush=True)


gates = []


def gate(label, ok, detail=""):
    gates.append((label, ok, detail))
    say(("-> PASS  " if ok else "-> FAIL  ") + label + ("  " + detail if detail else ""))


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def undisposed_newest():
    """guard_peer.undisposed('retrospective'), reimplemented here so the runner is held to the same condition the
    hook would hold a single dispatch to. Returns (path, why) or None."""
    files = sorted(glob.glob(os.path.join(PEER, "*retrospective*.md")), key=os.path.getmtime)
    if not files:
        return None
    newest = files[-1]
    body = read(newest)
    if DISPOSITION_H not in body:
        return newest, "no disposition section at all"
    tail = re.sub(r"^\s*\(?\s*claude fills in\s*\)?\s*$", "", body.split(DISPOSITION_H, 1)[1],
                  flags=re.I | re.M).strip()
    if len(tail) < 80:
        return newest, "disposition is empty or still the placeholder"
    return None


def write_disposition(path, cycle, seconds, outcome, viols):
    """Bookkeeping only - what the run WAS, not what its findings mean."""
    body = read(path)
    note = (
        f"This is a **retroactive v2 comparison run**, not the cycle's live retrospective. Cycle {cycle}'s own\n"
        f"retrospective is `archive/peer/2026-09-16-retrospective-cycle{cycle}.md` (v1), and its findings were\n"
        f"disposed there. This archive exists because the user asked for v2 to be MEASURED against v1 before it is\n"
        f"adopted (2026-09-16): same cycle, same evidence, new question set and a cycle-boundary evidence window.\n\n"
        f"- dispatched by `tools/bench/retro_v2_compare_runner.py` under bgrun, run {seconds:.0f} s, outcome "
        f"{outcome}\n"
        f"- v1 fired 9 slugs on this cycle; this run's machine lines are reproduced verbatim below\n"
        + "".join(f"- `{v}`\n" for v in viols)
        + "\n**Disposition of the findings: `tools/bench/retro_v2_comparison.md`**, which is the artefact this run\n"
          "was bought for. No verdict is accepted or rejected in this file - whether v2 replaces v1, and what to do\n"
          "about `judgement-in-material`, are judgement calls and are left OPEN for the judgement session.\n")
    if DISPOSITION_H in body:
        head, tail = body.split(DISPOSITION_H, 1)
        tail = re.sub(r"^\s*\(?\s*claude fills in\s*\)?\s*$", "", tail, flags=re.I | re.M).strip()
        body = head + DISPOSITION_H + "\n\n" + note + (("\n" + tail + "\n") if tail else "")
    else:
        body = body.rstrip() + "\n\n" + DISPOSITION_H + "\n\n" + note
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)


say("=== retrospective v2 comparison runner: cycles 11, 12, 13 ===")
say(f"    root {ROOT}")
results = []

for n in CYCLES:
    slug = f"retrospective-v2-cycle{n}"
    say(f"\n================ cycle {n} ================")
    u = undisposed_newest()
    if u:
        say(f"    newest retrospective archive UNDISPOSED: {os.path.relpath(u[0], ROOT)} ({u[1]})")
    gate(f"D{n} guard_peer undisposed() is false before this dispatch", u is None,
         "" if u is None else f"{os.path.basename(u[0])}: {u[1]}")

    before = set(glob.glob(os.path.join(PEER, f"*{slug}*.md")))
    t0 = time.time()
    r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "retrospective.py"),
                        "--cycle", str(n), "--slug", slug],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1500)
    dt = time.time() - t0
    out = (r.stdout or "") + (("\nSTDERR:\n" + r.stderr) if (r.stderr or "").strip() else "")
    say(out)
    say(f"    retrospective.py rc={r.returncode} in {dt:.1f}s")

    new = sorted(set(glob.glob(os.path.join(PEER, f"*{slug}*.md"))) - before)
    gate(f"A{n} rc==0 and exactly one new archive", r.returncode == 0 and len(new) == 1,
         f"rc={r.returncode}, new={[os.path.basename(p) for p in new]}")
    if not new:
        results.append(dict(cycle=n, path=None, secs=dt, outcome="NO ARCHIVE", cost=None, viols=[], runner_out=out))
        continue

    path = new[0]
    body = read(path)
    m = re.search(r"^\-\s*\*\*outcome:\*\*\s*(\w+)\s*(?:\((\d+)s\))?", body, re.M)
    outcome, peer_s = (m.group(1) if m else "?"), (m.group(2) if m and m.group(2) else "?")
    gate(f"B{n} archive outcome is ANSWERED", outcome.upper() == "ANSWERED", f"outcome={outcome} ({peer_s}s)")

    answer = body.split(DISPOSITION_H)[0]
    viols = [ln.strip() for ln in answer.splitlines() if ln.strip().startswith("VIOLATION:")]
    gate(f"C{n} archive carries >=1 VIOLATION line", len(viols) >= 1, f"n={len(viols)}")
    say(f"OBSERVED: cycle {n} v2 emitted {len(viols)} VIOLATION line(s)  (v1 emitted "
        f"{9 if n in (11, 12) else 6}); contract asks for 1, at most 2")
    for v in viols:
        say("    " + v)

    cm = re.search(r"COST:\s*\$?([0-9]+\.[0-9]+)", out)
    cost = float(cm.group(1)) if cm else None
    say(f"    cost line in dispatcher output: {'$%.4f' % cost if cost is not None else 'NONE (codex prints no cost)'}")

    write_disposition(path, n, dt, outcome, viols)
    say(f"    disposition written into {os.path.relpath(path, ROOT)}")
    results.append(dict(cycle=n, path=path, secs=dt, peer_secs=peer_s, outcome=outcome, cost=cost,
                        viols=viols, runner_out=out))

# ---------------------------------------------------------------- E: violations.py still parses everything
say("\n--- E: py tools/violations.py (both VIOLATION forms) ---")
rv = subprocess.run([sys.executable, os.path.join(TOOLS, "violations.py")],
                    cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
say(rv.stdout.rstrip("\n"))
if (rv.stderr or "").strip():
    say("STDERR:\n" + rv.stderr)
gate("E violations.py exits 0 over old+new archives", rv.returncode == 0, f"rc={rv.returncode}")

say("\n--- E2: py tools/violations.py --due (VERBATIM) ---")
rd = subprocess.run([sys.executable, os.path.join(TOOLS, "violations.py"), "--due"],
                    cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=300)
say("<<<DUE-BEGIN>>>")
say(rd.stdout.rstrip("\n"))
say("<<<DUE-END>>>")
say(f"    violations --due rc={rd.returncode}")

# ---------------------------------------------------------------- summary block for the comparison document
say("\n=== SUMMARY (for tools/bench/retro_v2_comparison.md) ===")
for x in results:
    say(f"cycle {x['cycle']}: {x['secs']:.0f}s runner / peer {x.get('peer_secs', '?')}s, outcome {x['outcome']}, "
        f"cost {'$%.4f' % x['cost'] if x['cost'] is not None else '?'}, {len(x['viols'])} VIOLATION line(s)")
    for v in x["viols"]:
        say(f"    {v}")

npass = sum(1 for _, ok, _ in gates if ok)
nfail = len(gates) - npass
say(f"\n=== retro_v2_compare: {npass} pass, {nfail} fail ===")
sys.exit(0 if nfail == 0 else 1)
