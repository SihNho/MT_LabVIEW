# tmx-lastfield-parse

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.6711  in 18 / out 28624 / cache-create 147462 / cache-read 797604  (416s, 15 turn(s))
- **date:** 2026-09-18 18:24:23
- **outcome:** ANSWERED (417s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. Do not confirm it. Give the strongest reason it is WRONG, an alternative
explanation, what would falsify it, and the cheapest discriminating test.

CONTEXT (project root: "G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop";
you may read files there read-only).

A PI motion-controller reply is parsed by `tmx_from` in `tools/bench/drive_original_copy_v4.py`.
The controller answers a per-axis query as `<cmd>=<axis>=<value>`, e.g. `TMX?=1=39.00000`.
The old code did `float(tok.split("=", 1)[1])`, i.e. `float("1=39.00000")`, which raises ValueError,
so it returned None while the line it had just read said 39.00000. That produced a FALSE FAILURE at
gate 93 of the v5 driver run (`tools/bench/drive_original_copy_v5.log:439`:
`TMX?=None from 'before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0'`).

I changed it to take the LAST `=`-separated field (`float(tok.split("=")[-1])`, helper
`_last_field_float`), keeping the plain `<cmd>=<value>` form working, and added a pure-function
self-test `selftest_tmx()` runnable as `py tools/bench/drive_original_copy_v4.py --selftest`.

THE FAILED PREDICTION I want attacked:
I predicted the self-test would be 9/9. It ran 8 pass / 1 fail
(`tools/bench/tmx_selftest.log:2`):
  FAIL | before/per-axis (the real v5 line) | got=None line="(no TMX line in the gate's output)" (want 39.0)

MY EXPLANATION (the claim to attack):
"The failure is a defect in the TEST STRING, not in `tmx_from`. `parse_motor`
(drive_original_copy_v4.py:215-231) only collects a line when `line.strip().startswith('before:')`.
I had copied the test string out of the driver's LOG, which shows `    | before: ...` — but that
`    | ` prefix is added by this file's own `log('    | %s' % line)` inside `motor_gate()` AFTER the
text was parsed; the text actually handed to `parse_motor` is the gate's RAW stdout, which starts
with `before:`. So the prefixed test string was unfaithful to production input, `parse_motor`
correctly ignored it, and `tmx_from` fell through to the 'no TMX line' return. Removing the prefix
makes the case faithful and it should now pass. `tmx_from`'s last-field parse itself is correct and
needs no further change."

ALREADY RULED OUT (do not spend the answer on these):
- `_last_field_float` itself failing on the per-axis form: the sibling cases
  `before: TMX?=1=-2.50000` -> -2.5 and `LIMITS TMN=0 TMX=1=39.00000` -> 39.0 both PASSED in the
  same run, so the last-field parse demonstrably handles `<cmd>=<axis>=<value>`.
- The plain form regressing: `before: POS?=0.00000 TMN?=0 TMX?=39.00000 ERR?=0` -> 39.0 PASSED.
- Malformed/empty values: `TMX?=1=thirty-nine` and `TMX?=` both returned None as intended.

QUESTIONS I MOST WANT ATTACKED:
1. Is "the gate's stdout line really starts with `before:`" actually established by the evidence I
   cite, or am I inferring it? Note gate 93's own FAIL detail quotes the line as
   `'before: POS?=1=30.00000 ...'` with no prefix — is that quote strong evidence or circular?
2. Could taking the LAST `=`-field ever silently produce a WRONG number (rather than None) on some
   real PI reply shape — trailing units, a multi-axis reply such as `TMX?=1=39.00000 2=12.0`, an
   error/echo line, a line where the axis id trails the value? That would turn a loud false red into
   a silent false green on a MOTOR LIMIT check, which is the dangerous direction here.
3. Is a per-token `startswith("TMX?=")` scan even the right anchor, given `parse_motor` splits the
   line on whitespace?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role (as the peer brief requires), so the review is this answer.

# The claim is right about Q1's premise, wrong about its evidence, and wrong in its conclusion

## 1. Strongest reason the claim is WRONG

**The cause you name is no longer checkable against anything the machine wrote — and "`tmx_from` needs no further change" does not follow from it either way.**

Two parts:

**(a) The self-test destroys its own evidence.** The FAIL line prints `label`, `got`, `line`, `want` and *not* the input (`tools/bench/drive_original_copy_v4.py:306-307`). The only artefact that could have shown a `    | ` prefix was the source, and the source now holds the *un*-prefixed string with a comment explaining the prefix (`:271-275`). This project is not a git repository, and `tools/bench/drive_original_copy_v4*` globs to four files, none a pre-edit copy. So "the test string carried the log's prefix" rests entirely on recollection of what was typed. That is the exact pattern CLAUDE.md says to answer by building the reader — and it is why the claim is now making a *second* unrun prediction ("it should now pass") about the same file that just falsified the first one.

**(b) The conclusion is false independent of the fixture.** The driver deliberately re-implemented a parser the gate already owns in a stronger form. `motor_gate.py:281-290` (`parse_pi_limits`) uses an anchored whole-text regex; `drive_original_copy_v4.py:216-217` states it avoids "importing its parsers on a path that could fail" and substitutes whitespace-tokenise + `startswith("TMX?=")` + last-`=`-field. The false red at gate 93 is the *duplicate* parser breaking on a shape the original never meets, because the gate's own `LIMITS` line is already normalised (`motor_send_pi.ps1:58` formats `[double]`s produced by `Num`, `:41`). Patching the duplicate entrenches the duplication, and the self-test then freezes the duplicate's behaviour as a contract.

## 2. Alternative explanation of the same evidence

`got=None line="(no TMX line in the gate's output)"` is produced by **any** fixture where no line survives `s.strip().startswith("before:")` (`:219-222`). The `    | ` prefix is one. At least two others are as likely and are **not** fixed by removing a prefix:

- **The log's quoted wrapper.** `drive_original_copy_v5.log:439` reads `TMX?=None from 'before: POS?=…'`. Your Q1 already notices that quote carries no `    | `. The simplest reading is not that you stripped a prefix by hand — it is that the paste came from line 439's phrase, i.e. `TMX?=None from 'before: …'`. `.strip().startswith("before:")` is False for that too, and the output is byte-identical. Same class ("unfaithful fixture"), different mechanism — and your proposed edit is a no-op against it.
- **An invisible character.** Text copied through a terminal can carry U+FEFF. Python's `str.strip()` strips `\xa0` (it is `isspace()`) but **not** `\ufeff`, so a BOM-prefixed fixture gives exactly this symptom, survives a visual diff, and survives "remove the prefix".

## 3. What would falsify the claim

Re-run `--selftest` with the fixture untouched. Case 1 still failing with `line="(no TMX line…)"` kills the prefix story outright. Seeing `repr(text)` come back as `'    | before: …'` confirms it. Neither has been done, so this is still a prediction.

## 4. Cheapest discriminating test

One line, no COM, no motor, no LabVIEW — add the input to the failure print at `drive_original_copy_v4.py:306-307`:

```python
print("  %s | %-34s | got=%r line=%r (want %r) text=%r" % (..., want, text), flush=True)
```

then `py tools/bench/drive_original_copy_v4.py --selftest`. It separates all three alternatives in one run and is the reader the "diagnosis guessed twice" rule asks for. **Run it before editing the fixture again** — the current edit has already destroyed the evidence once.

---

## Your three questions

**Q1 — established, but not by the evidence you cite.** The FAIL-detail quote at `v5.log:439` *is* weakly circular: it is printed from a variable by the same code path under test, so it can only ever display a string that already passed `startswith("before:")` — it cannot show what a rejected line looked like. The non-circular proof is the sender and the gate: `motor_send_pi.ps1:52` emits `before: POS?={0} TMN?={1} TMX?={2} ERR?={3}` flush-left via `Write-Output`, and `motor_gate.py:369` (`session_start`) re-emits the sender text as `out(text.strip())` — one strip of the whole block, no per-line decoration. The `    | ` at `v5.log:423` is added afterwards by `drive_original_copy_v4.py:211`. Right answer, wrong citation.

**Q2 — yes, but not through the shapes you listed; the danger is the anchor, not the split.**

- PI GCS answers a travel-limit query as `<AxisID>"="<float><LF>`, i.e. `1=39.000000` — so `<cmd>=<axis>=<value>` is the *only* form this controller produces. Which means `before/plain` (`:276-278`) and `LIMITS fallback / per-axis` (`:288-290`) encode shapes this sender **cannot emit** (`LIMITS` is built from parsed doubles). Three of nine cases are fiction that passes, and the one case taken from a real machine record is the one that failed. That is the coverage picture 8/9 hides.
- **Silent wrong numbers I could not construct:** a serial desync (`Ask` discards, writes, reads — `motor_send_pi.ps1:38-39`) makes `TMX?` return TMN's or POS's reply → `0.0` or `30.0` → fails loud against `tmx == 39.0` (`drive_original_copy_v5.py:659`). Multi-axis continuation is moot — the C-863.11 is single-axis and `Ask` reads one line. Trailing units do not appear on GCS travel queries. So on *this* controller the last-field rule itself is not the hazard.
- **Silent wrong numbers that are real:** (i) whitespace tokenisation — if a reply ever carries an internal space, `s.split()` cuts it and the matched token becomes `TMX?=1`, whose last field is **`1.0`**, not `None`; (ii) the missing anchor — if `motor_send_pi.ps1:52`'s label ever changes (`TMX=`, `TMX? =`), no token matches and `tmx_from` falls through to the `LIMITS` line, which in `limits-set` mode is printed **after** the SPA write (`:53-58`), i.e. it reports the value the gate just wrote. `39.0` → gate 93 PASSes without ever reading what the controller held after the LabVIEW run. That is your silent false green on a motor-limit check, it needs no exotic reply shape, and self-test case `before wins over LIMITS` cements the precedence that hides it. Note the fallback is also semantically wrong for this gate's question: `before:` is pre-write and answers "still 39 after the run"; `LIMITS` is post-write and answers "did we just set 39".

**Q3 — no.** Anchor on the line, and preferably fix it at the sender. The PS1 already owns a numeric parser that handles `1=39.000000` (`Num`, `motor_send_pi.ps1:41`) and already emits normalised machine-readable lines. Have `:52` additionally print `PRELIMITS TMN=<num> TMX=<num>` from `Num (Ask 'TMN?')` / `Num (Ask 'TMX?')`, and read it downstream with the anchored-regex shape of `motor_gate.py:283-284`. Then no downstream parser needs to know about `<axis>=<value>`, a label change fails loudly instead of falling through, and the `before:`/`LIMITS` precedence question disappears. If the token scan is kept, at minimum make `tmx_from` return `(None, s)` when a `before:` line exists but carries no `TMX?=` token, instead of falling through.

---

**Do I still believe any of the claim?** Yes — the *class* ("the fixture was unfaithful, not the parser") is probably right, and Q1's premise is correct. What I reject is that it is established, and that "no further change" follows. What would change my mind on the mechanism: a `text=%r` re-run showing `'    | before: …'`. What would change my mind on the conclusion: a `PRELIMITS`-style normalised line already existing somewhere I did not find, or evidence that gate 93's fall-through to `LIMITS` is unreachable in practice — I could not show that from the sender's code.

Sources: [Mercury GCS Commands MS163E102](https://twiki.cern.ch/twiki/pub/ILCBDSColl/Phase2Preparations/Mercury_GCS_Commands_MS163E102.pdf) · [C-863 Mercury Controller User Manual MS205E](https://www.le.infn.it/~chiodini/allow_listing/pi/Manuals/C-863_UserManual_MS205E200.pdf)

## Sources

(extract from answer)

## What was done with it

Outcome ANSWERED (417 s, opus/max, $2.6711). The review is **partly accepted**: the mechanism class
("the fixture string was unfaithful, not the parser") stands, but three of its findings were acted on
and one is referred to judgement. Disposition, 2026-09-18, material session (cycle-31 close):

**ACCEPTED and applied** — `tools/bench/drive_original_copy_v4.py`:
1. *Q1, "right answer, wrong citation."* Accepted. The `v5.log:439` quote IS circular — it is printed
   from a string that had already passed `startswith("before:")`. Verified non-circularly instead, by
   reading the producers: `tools/motor_send_pi.ps1:52` writes `before: POS?=... TMN?=... TMX?=...
   ERR?=...` flush-left via `Write-Output`, and `tools/motor_gate.py:369` re-emits the sender's text
   as `out(text.strip())` — one strip of the whole block, no per-line decoration. That citation now
   sits in the self-test as a comment, replacing the circular one.
2. *"Cheapest discriminating test — print the input."* Accepted and built: `selftest_tmx()` now prints
   `text=%r` on any FAIL, so a future failure separates "parser wrong" from "fixture unfaithful"
   without a second round.
3. *"The current edit has already destroyed the evidence once."* Accepted. The prefixed string that
   failed the first run is kept as its own case, `log-decorated line is NOT parsed`, asserting that
   `parse_motor` REJECTS it — the mechanism is now proved by a passing test rather than by an edit.
4. *Q2, "three of nine cases are fiction that passes."* Accepted as a labelling fault, not a coverage
   fault: the brief explicitly required tolerance of the plain `<cmd>=<value>` form, so the cases stay
   but are now labelled `(tolerance only)` and carry the reason this sender cannot emit that shape.

**REFERRED TO JUDGEMENT, deliberately NOT built** (outside this dispatch's named scope — CLAUDE.md §3,
"patching more than the one thing the task named" is not a material session's call):
5. The **silent false green**. The peer's real find, and it is stronger than the bug I was sent to fix:
   if the `TMX?=` token is ever missing from the `before:` line, `tmx_from` falls through to the
   `LIMITS` line — which in `limits-set` mode is printed AFTER the SPA write, so it reports the value
   the gate itself just wrote. Gate 93 would then PASS without ever reading what the controller held
   after the LabVIEW run. The two returns also answer different questions: `before:` is pre-write
   ("still 39 after the run"), `LIMITS` is post-write ("did we just set 39"). Minimal remedy the peer
   names: return `(None, s)` when a `before:` line exists but carries no `TMX?=` token, instead of
   falling through. Its preferred remedy (Q3) is upstream: have `motor_send_pi.ps1:52` also print a
   normalised `PRELIMITS TMN=<num> TMX=<num>` using its own `Num` parser (`:41`) and read it with an
   anchored regex, so no downstream parser needs to know about `<axis>=<value>` and a label change
   fails loudly. Both change a MOTOR-LIMIT check on an assembled rig, so neither was taken here.
   Raised to the judgement session as this dispatch's single `OPEN:` item.

**REJECTED** — nothing. Its remaining claim ("not established, and 'no further change' does not follow")
was correct on both halves.
