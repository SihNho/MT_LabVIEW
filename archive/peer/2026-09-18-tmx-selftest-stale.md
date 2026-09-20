# tmx-selftest-stale

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.8386  in 22 / out 28768 / cache-create 156116 / cache-read 1061975  (405s, 20 turn(s))
- **date:** 2026-09-18 19:04:23
- **outcome:** ANSWERED (406s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. It is the explanation formed for a failed prediction, and it is about to let a
motor-limit parser on an ASSEMBLED magnetic-tweezers rig be treated as correct. Find the strongest
reason it is WRONG.

THE FAILED PREDICTION
`tools/bench/drive_original_copy_v4.py --selftest` (pure function, no serial, no LabVIEW) declares in
its docstring `PREDICTION CONTRACT: 16 pass / 0 fail`. The recorded run in `tools/bench/tmx_selftest.log`
(BGRUN START 2026-09-18 18:45:48) ended:

    FAIL | no TMX anywhere | got=None line='before: POS?=1=0.00000 ERR?=0' (want None)  text='before: POS?=1=0.00000 ERR?=0'
    SELFTEST tmx_from: 14 pass / 1 fail
    BGRUN END rc=1 after 0s

THE CLAIM TO ATTACK
"That FAIL is not a defect in `tmx_from`. It is a STALE TEST EXPECTATION recorded against a source file
that has since changed. The case asserted the REPORTED LINE contains the substring 'no TMX line'; the
2026-09-18 fall-through fix makes `tmx_from` return the `before:` line it actually read and rejected
instead of the placeholder '(no TMX line in the gate's output)'. The returned VALUE was and remains
None, which is what the motor-limit gate consumes. The case on disk now reads
'no TMX anywhere (reports the before: line it read)' and expects the substring
'before: POS?=1=0.00000'; the file now carries 16 cases, the log's run carried 15. Therefore the
correct next action is to RE-RUN the self-test, not to change `tmx_from`."

EVIDENCE YOU CAN OPEN (read-only, all inside the project directory)
* `tools/bench/tmx_selftest.log` — three runs: 18:16 (8/1), 18:25 (10/0), 18:45 (14/1).
* `tools/bench/drive_original_copy_v4.py` — `_last_field_float` (~:243), `prelimits_from` (~:258),
  `tmx_from` (~:280) with its 4-step precedence, and `selftest_tmx`'s case table (~:327 onward).
* `STATUS.md` OPEN 55 — the fault being fixed: a `before:` line without a `TMX?=` token used to fall
  through to the POST-WRITE `LIMITS` line, so the gate read back the value it had just written and
  PASSED without ever learning what the controller held after the run (a silent false green).
* `archive/peer/2026-09-18-tmx-lastfield-parse.md` — the earlier review of this parser.

ALREADY RULED OUT — do not spend your answer on these three
1. A value defect on the failing case: the assertion `got=None` vs `want=None` matches; only the
   line-text assertion differs.
2. A regression introduced by the fall-through patch: the dedicated cases
   "FALL-THROUGH: before: without TMX?= never reads LIMITS" and "PRELIMITS beats a post-write LIMITS"
   both PASS in that same 18:45 run.
3. "The test was never run": it was, three times; the question is only whether the 18:45 run is stale
   with respect to the file now on disk.

WHAT I WANT FROM YOU
a) The strongest reason the claim is wrong — in particular, any way in which the changed EXPECTED
   SUBSTRING weakens the test rather than corrects it, or hides a real behaviour change in `tmx_from`.
b) Whether returning the rejected `before:` line (instead of a placeholder) can mislead any CALLER of
   `tmx_from`, not just this self-test — e.g. a gate that logs or pattern-matches the returned line.
c) Whether step 4 of `tmx_from`'s precedence (the `LIMITS` fallback when NO `PRELIMITS` and NO
   `before:` line exists) still admits a post-write value, and under what concrete transcript.
d) The cheapest DISCRIMINATING test that separates "stale expectation" from "real defect", runnable
   with no motor and no LabVIEW.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The single strongest reason the claim is wrong: the one case whose expectation changed is the one case that cannot tell the patched parser from the unpatched one — so the re-run it recommends is guaranteed to be green and carries no information about the fix, while the same patch introduced an untested behaviour change that nothing in the suite covers.**

---

## 1. Why the claim is wrong

The claim's arithmetic checks out — I verified it, and that is the problem. The file does hold 16 cases; the 18:45 run printed 15 (`tmx_selftest.log:27-41`); the added one is `no TMX and no before: line at all` (`drive_original_copy_v4.py:376-378`). Comparing every reported `line` in that run against every `want_line` now on disk, the log is consistent with exactly one changed expectation plus one added case. **The staleness story is true. The conclusion drawn from it is not.**

Look at what case 10 actually tests (`:373-375`):

```
fixture: "before: POS?=1=0.00000 ERR?=0"      # a before: line, no TMX?=, AND NO LIMITS LINE
```

There is no `LIMITS` line in that fixture. So the **unpatched** parser walked past the `before:` line, found nothing in the `LIMITS` loop, and returned the sentinel at `:315`; the **patched** parser stops at `:308-310`. Both return `None`. The two implementations differ on this fixture *only in the string*. That is confirmed by the machine, not inferred: the unpatched probe only ever produced a wrong number on fixtures that **did** contain a `LIMITS` line (`tmx_fallthrough_before.log:4` fixture A, `:10` fixture D — both have one; `:5`, `:11`).

So: case 10 is not a fall-through test. Its expectation change is cosmetic, and 16/0 on the re-run proves the edit was typed.

Meanwhile the three cases that *do* discriminate — `FALL-THROUGH: before: without TMX?= never reads LIMITS`, `PRELIMITS beats a post-write LIMITS`, `PRELIMITS with an empty field is NOT read` — **already passed at 18:45** (`tmx_selftest.log:37,38,41`). The evidence that OPEN 55's fault is fixed is already in the log. The re-run adds a number and nothing else.

And there is a second-order problem the claim inherits: `PREDICTION CONTRACT: 16 pass / 0 fail` (`:323`) was written **after** a 15-case 14/1 run, in the same edit that changed the code and the expectation. Under CLAUDE.md §3 ("Recipes must state their prediction contracts … before execution so 'failed prediction' is machine-checkable"), that is a postdiction. A contract fitted to observed output cannot fail informatively.

## (a) How the changed expected substring weakens the test

Two concrete ways.

**It moved from a code-owned constant to an echo of the input.** Old: `"no TMX line"` — a literal that exists in exactly one place in the source (`:315`). New: `"before: POS?=1=0.00000"` — a substring of the test's own fixture (`:374`). The assertion is `(got == want) and (want_line in line)` (`:416`), and with `want=None` the value half is satisfied by any `None`. So *all* of these pass case 10 identically:

- `return None, before[-1]` (what the code does)
- `return None, before[0]`
- `return None, text` (the whole transcript)

**And the fixture is degenerate: it has exactly one `before:` line.** So the case named *"reports the before: line it read"* cannot show *which* `before:` line is reported. **No case among the 16 contains two `before:` lines**, yet `before[-1]` (`:310`) is a real last-wins choice the code makes, on a transcript that `motor_gate.py` assembles from two senders (`motor_gate.py:375-376` PI, `:386-387` ASI). It is safe today only by accident: `motor_asi_io.ps1:61` prints `before SL: …`, which `startswith("before:")` rejects. One label change at the ASI sender and step 3 answers a PI limit question with an ASI line, with no test to catch it.

**Cheap repair that keeps the new information without the weakness:** return `(None, "no TMX?= token in: " + s)`. Then the case asserts a code-owned constant *and* the echoed line, and a two-`before:`-line fixture becomes meaningful.

## (b) Can the returned line mislead a caller?

**No machine caller changes its verdict — I checked all three.** `drive_original_copy_v4.py:1006,1012`, `v5.py:656,659` and `diag_d0_pickloop_liveness.py:433-435` all gate on `tmx == 39.0`; `line` only reaches a detail string and a JSON field (`diag_…:434`). `guard_peer.py`'s `FAILURE_RE` (`:73`) matches none of these strings.

**The human/agent reader is misled, and in the exact way that already cost this project once.** The detail string is built as `"TMX?=%r from %r; gate exit=%d; %s; …"` with the *post-write* `LIMITS` line appended right after (`v4.py:1013-1015`). A failure now renders as:

```
TMX?=None from 'before: POS?=1=30.00000 TMN?=1=0.00000 ERR?=0'; gate exit=0; LIMITS TMN=0 TMX=39 …
```

The old sentinel said *"I found nothing"*. The new one presents a plausible-looking controller line with no `TMX?=` in it, adjacent to a plausible-looking `TMX=39`. That is precisely the reading trap that produced the false-red mis-diagnosis at `drive_original_copy_v5.log:439`, and this project's log-reader sub-agent and retrospective are real consumers of that text. Replacing a self-describing sentinel with a line the reader must interpret runs against "when a diagnosis is GUESSED twice, build the reader".

## (c) Step 4 — the ⚠️ RESIDUAL is a phantom; the real hazard is the opposite one

The docstring (`:295-299`) says step 4 fires "only when the sender produced NO `PRELIMITS` and NO `before:` line at all — **a `--mode send` transcript, where `LIMITS` is printed before any transmit**", and flags a residual post-write risk for judgement.

**Read the sender. Send mode prints a `before:` line.** `motor_send_pi.ps1:111`:

```powershell
Write-Output ("before: POS?={0}  SVO?={1}  FRF?={2}  VEL?={3}  ERR?={4}" -f …)
```

No `TMX?=` token — POS?, SVO?, FRF?, VEL?, ERR?. And the genuinely **pre-transmit** `LIMITS` line sits at `:105`, above it.

So the patch inverted the behaviour on the one transcript step 4 was written for: `tmx_from` now stops at `:310` and returns `(None, <that before: line>)`, **never reaching the valid pre-write `LIMITS` at :105** — a new false RED, undocumented and untested.

And step 4 is now **unreachable for every transcript this sender can emit**:

| mode | `before:` printed? | reaches step 4? |
|---|---|---|
| `limits-set` / `limits-release` | yes, unconditional (`:58`), plus `PRELIMITS` (`:67`) | no — step 1 or step 3 |
| `send` | yes (`:111`) | no — step 3 |
| port open throws (`:52`) | no output at all | no — no `LIMITS` either |

Its only green comes from cases 6 and 7 (`:354-361`), whose fixtures are a bare `LIMITS` line with no `before:` — a shape no branch of `motor_send_pi.ps1` produces. **The residual escalated to the judgement session does not exist in production, and the behaviour change that does exist was not reported.** That is the `unreported-fact` shape, not a stale test.

Two smaller accuracy faults in the same neighbourhood: the parser's producer citations are stale — `:284` and `:126` cite `motor_send_pi.ps1:52` for the `before:`/`PRELIMITS` lines (that line is `$sp.Open()`); actual producers are `:58`, `:67`, and `LIMITS` at `:73`/`:93`, not `:58/:78` as `:288` claims.

## 2. Alternative explanation of the same evidence

**The second element of `tmx_from`'s tuple has no specification, so both the code and the test are guesses, and 14/1 is the first place they disagreed.** Nothing states what the reported line *means* when the value is `None` — "the line I parsed", "the line I rejected", or "why I have no answer". The old sentinel answered the third; the patch silently switched case 10 to the second, and the expectation was rewritten to match the output rather than to a contract. This explains the identical evidence (value matches, line differs, one case changed) and predicts more of the same wherever `None` can arise. Under it, the right action is to *specify* that element and test it against a non-degenerate fixture.

**A second, cheaper alternative I cannot rule out from the log:** the 18:45 run executed a half-finished edit (15 cases) rather than an older complete one. "Stale expectation" and "ran a mid-edit file" produce byte-identical logs, because the self-test never prints its own case count, mtime or md5. The evidence does not distinguish these two.

## 3. What would falsify the claim

A re-run that returns anything other than 16/0 kills it outright. But the decisive observation is cheaper and independent of the count: **feed `tmx_from` a send-mode transcript** (`LIMITS` at `:105` + the `before:` line at `:111`). If it returns `None`, "no change to `tmx_from` is needed" is refuted regardless of how the re-run scores — the patch broke a transcript shape the docstring names as step 4's legitimate case.

Conversely, what would restore the claim for me: a written contract for the second tuple element, plus a case with two `before:` lines and a case with the send-mode shape, all predicted before running.

## 4. Cheapest discriminating test

Pure function, no motor, no LabVIEW, under a second. **Write the three predictions down first, then run once:**

```python
# 1. SEND MODE - the shape motor_send_pi.ps1:105 + :111 actually emits.
("send-mode transcript: before: carries no TMX?=, LIMITS is PRE-transmit",
 "LIMITS TMN=0 TMX=39 SPA15=39 SPA30=0\n"
 "before: POS?=1=30.00000  SVO?=1  FRF?=1  VEL?=1.000000  ERR?=0",
 ???, ???),            # predict 39.0 or None IN WRITING before running

# 2. TWO before: LINES - separates "the line it read" from "the last before: line".
("two before: lines - which one is named?",
 "before: POS?=1=30.00000 TMX?=1=39.00000 ERR?=0\nbefore: POS?=1=0.00000 ERR?=0",
 39.0, "TMX?=1=39.00000"),

# 3. ECHO-PROOF - does the assertion survive an implementation that returns the whole text?
#    (temporarily return (None, text) at :310 and confirm cases 10/12/16 FAIL)
```

Plus one line at the top of `selftest_tmx()`: print `len(cases)` and the file's own md5, so a future log can be checked against the file that produced it — that alone separates "stale expectation" from "ran a mid-edit file" permanently.

Case 1 is the whole argument. If it returns `None`, the next action is not a re-run.

---

**Do I still believe any of the claim?** The narrow factual half, yes — the expectation *is* stale and the file *did* change after the run; I confirmed both. What I reject is the conclusion. Re-running produces a green that certifies nothing, the case at the centre of the argument has zero discriminating power, and the same patch made `tmx_from` return `None` on a send-mode transcript whose `LIMITS` line is legitimately pre-write — on a parser that gates motor limits on an assembled rig. **What would change my mind: case 1 above returning 39.0, or a stated contract saying `None` is the intended answer for send-mode transcripts — in which case `:295-299` must be rewritten, because it says the opposite.**

One honest gap: the external record did not settle the GCS reply-format question. The only reply sample I could source is `PI GCS read: 1 0X40=125` (axis-prefixed `<axis>=<value>`), consistent with `_last_field_float`'s assumption but not proof of it; neither search surfaced a C-863 GCS reply-format specification. That question is unchanged by this review either way — none of the findings above depend on it.

Sources: [CSS spec help — pi_gcs](https://certif.com/spec_help/pi_gcs.html) · [PIPython (PI GCS command library)](https://github.com/PI-PhysikInstrumente/PIPython) · [C-863 Mercury user manual listing](https://www.manualslib.com/manual/1623159/Physik-Instrumente.html)

## Sources

(extract from answer)

## What was done with it

Outcome **ANSWERED** (`tools/bench/peer_tmx-selftest-stale.log`, `BGRUN END rc=0 after 406s`), dispatched by
**cycle-34 material dispatch A**, whose actual task is the N1 VI-level fixture comparison. It was dispatched
because `guard_peer.py` blocked that measurement on `tools/bench/tmx_selftest.log` (18:45:48, `FAIL | no TMX
anywhere`), a failure belonging to a **different** dispatch (the OPEN-55 `tmx_from` work).

**Accepted as fact, both halves confirmed by the peer against the files:** the 18:45 expectation IS stale and
`drive_original_copy_v4.py` DID change after that run (15 cases then, 16 on disk now, and the failing case was
relabelled `no TMX anywhere (reports the before: line it read)`). The failing assertion is the line-text one; the
value assertion `got=None` / `want=None` matched.

**REJECTED by the peer — the conclusion "so just re-run it":** the peer's position is that a re-run produces a
green that certifies nothing, that the relabelled case now has zero discriminating power, and that the same patch
made `tmx_from` return `None` for a **send-mode** transcript whose `LIMITS` line is legitimately *pre*-write —
against `tmx_from`'s own docstring at `:295-299`, which says such a transcript may be answered from `LIMITS`. The
peer's stated falsifier: that case returning `39.0`, or a written contract declaring `None` the intended answer
for send-mode transcripts. One gap the peer flagged honestly: it could not source a C-863 GCS reply-format
specification, so `_last_field_float`'s axis-prefixed assumption remains unconfirmed externally (and nothing here
depends on it).

**NOT ACTED ON in this dispatch, deliberately.** Changing what a motor-limit parser accepts on an **assembled**
rig is a rule-1b/judgement call, and the parser is another dispatch's scope; this session neither patched
`tmx_from` nor re-ran the self-test (both re-run attempts were themselves blocked by the same gate before the
review landed). Handed to judgement as the live question: **is `None` the intended answer for a send-mode
transcript, or must step 4 of `tmx_from`'s precedence keep answering from `LIMITS`?** — because `:295-299`
currently documents the opposite of what the code now does. Recorded in `STATUS.md` OPEN 55.

The measurement this review unblocked ran immediately afterwards: `tools/bench/n1_gpuk_vi_fixture.py` →
`tools/bench/n1_gpuk_vi_fixture.log`.
