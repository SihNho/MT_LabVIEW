# Task — write the user-facing STOP message for cycle 66

Write **in Korean**, plain language, for a researcher who runs the rig but does not read LabVIEW scripting code.
Two or three short paragraphs. No headings, no bullet list, no code fences. End with the two decisions we need
from them, stated as questions. Do not invent numbers. Do not soften: the work has stopped and they need to know why.

Avoid jargon where a plain word exists. "Local variable" may stay as 로컬 변수; "data type" as 데이터 타입.

## FACT LIST

**Why the work stopped.** The project rule (`docs/cycle27-plan.md` Pre-decided 56(j)) says that if three
independent reviewers raise the same rule-1a concern, the work stops and the question goes to the user. That
happened on 2026-09-21. It is now three: `archive/peer/2026-09-21-c64-row1-wirecount-k2.md`,
`archive/peer/2026-09-21-c65-row2-wireind.md`, and today `archive/peer/2026-09-21-c66-m3-movelocals.md`.

**QUESTION 1 — execution order (already asked once, now sharpened).** In the original VI one wire carried a
value straight from a node into a Case structure input, and LabVIEW's dataflow guaranteed the Case structure
only ran after the value arrived. To prepare the loop split we replaced that one wire with two pieces: the node
writes to a front-panel indicator, and a local variable reads it back into the Case structure. There is no data
dependency between the two pieces, so LabVIEW guarantees no order, and the Case structure may legally read the
previous iteration's value, or on the first iteration the control's default. This Case structure drives the ASI
focus axis. The NEW point today's reviewer added: the next step moves those local variables into a DIFFERENT
loop, and it argues that this changes the sampling rate, what the read races against, and the first-iteration
value — i.e. it is a change of computation, not merely of scheduling.

**QUESTION 2 — silent number conversion (new this cycle).** Every automatic check we own reads existence,
counts, which wire touches which terminal, and whether a wire is broken. **None of them reads a data type.** The
broken-wire check catches an ILLEGAL connection; it does not catch a LEGAL conversion (for example 64-bit float
to 32-bit float, or float to integer). A legal conversion leaves every check passing while quietly changing the
numbers that come out. Row 2's indicator was originally derived from one terminal and is now fed from a
different one, so this is a live possibility, not a theoretical one.

This cycle found the two LabVIEW properties that can answer it — `Terminal.Coerce Dot?` (634A006) and
`Terminal.Data Type` (634A008) — and verified that both resolve on this machine. But READING THEIR VALUES needs
one small new helper VI, and the user's standing instruction of 2026-09-18 08:53 ("장치는 더 만들지 말고 계속
진행") blocks building new helpers. So the answer is currently **not measured** — which is different from
"measured and fine". Nothing has been run, so no wrong numbers have been produced.

**State of the work, so they know what is and is not at risk.** The two S3b files (rows 1 and 2) are built and
saved and pass every structural check; neither has ever been executed. Row 1 `D1_s3b_row1_20260921_135932.vi`,
row 2 `D1_s3b_row2_20260921_160311.vi`. The next stage, M3 (moving the loop-1.5 nodes into the loop body), was
attempted and did not produce a file: all seven moves and seven re-wirings landed, but the VI stayed in a broken
state, so nothing was saved — this is the second time that same stage has failed at the same point, so the next
cycle will break it into smaller pieces instead of retrying it whole. A reviewer also measured that no subset of
those seven moves is self-contained, which means the "every step leaves a file you can open" rule cannot be met
the way that stage is currently cut.

## THE TWO DECISIONS TO ASK FOR, at the end

1. In the final VI, is it acceptable for this focus signal to lose its guaranteed execution order — given that
   the seven-loop design they already approved passes data between loops asynchronously anyway — or must this
   particular signal keep a guaranteed order, in which case the transport is redesigned and both S3b files are
   rebuilt?
2. Do they want us to build the one small helper VI that reads the data type and the conversion mark, so the
   silent-conversion question can be answered by measurement instead of left open? This is the one exception
   being requested to their "no more new helpers" instruction.
