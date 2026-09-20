---
type: archive
status: archived
date: 2026-09-18
tags: [status, open-items, cycle20]
---

# STATUS OPEN items 42 / 43 / 46 / 47 — relocated VERBATIM (rule 4, STATUS was at 119 lines)

Relocated 2026-09-18 03:2x by the cycle-20 step-2 material session. Nothing is rewritten; STATUS keeps one
pointer line. Numbering is STATUS's.

42. ⚠️ 39 archived reviews undisposed (`doc_lint` L6 FAIL standalone, pre-2026-09-15 legacy; under `audit_cycle` L6 defers to **A4**, which sees 14 of 80 in its 24 h window). ⚠️ **`audit_cycle` A2/A3 are SELF-REFERENTIAL** — they failed cycle 19 naming only `c19_audit*.log`, the audit's own rc=1 output; same family as "review logs are evidence, never the thing under test" (CLAUDE.md:487-489). Not yet fixed.

43. ✅ **FIXED 2026-09-18 02:47 (cycle 20 step 1).** `guard_cycle.fixed_claim()` (new) reads the newest review's claim on the recipe BEFORE the mtime rule: valid `FIXED:` → allow, claim that fails 449(a/b/c) → **REFUSE**, no claim → unchanged. **T1–T6 PASS + B1 REFUSED / B2 ALLOWED** (verbatim gate text) → `tools/bench/selftest_guard_cycle_fixed.log`; no regression: `selftest_guard_cycle_rerun` 4/4 incl. C4.

46. ⚠️ **USER-FACING FACT, not a build task: `SetCommand_signed.vi` DOES NOT EXIST ANYWHERE ON DISK.** Glob `**/SetCommand*.vi`
   under `G:\…\MinLab` → **0 hits**; `…\LabVIEW 2026\instr.lib\Autonics Motor\` holds only `Close.vi`, `Configure.vi`, `SetCommand.vi`. CLAUDE.md rule 1b says the new VI uses it.

47. 🔴 **JUDGEMENT — cycle-19's audit `c19_audit2.log` A1/A2/A3: the remedy is NOT a `logclass` entry.** Dual review both ANSWERED (`archive/peer/2026-09-18-c20-audit-a1-motorgate-{codex,opus}.md`, disposed). MEASURED: `tools/bgrun.py` has **no `BGRUN_LOG`** (0 hits) while `audit_cycle.py:186-197` reads it ⇒ the own-log exemption is **unreachable code**; `motor_gate.log` carries live `SENT rc=` records, so excluding it by filename would **hide execution evidence**. opus reads this as `device-failed` (threshold 1).
