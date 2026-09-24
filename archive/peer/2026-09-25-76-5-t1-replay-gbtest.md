# 76-5-t1-replay-gbtest

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4932  in 24 / out 15806 / cache-create 98429 / cache-read 1188330  (201s, 19 turn(s))
- **date:** 2026-09-25 05:08:24
- **outcome:** ANSWERED (205s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about failed gates T1/T2/T3 in tools/bench/replay_vis_76d_test.log (script tools/bench/diag_replay_gbtest.py;
the stand-ins were built by tools/bench/diag_replay_standins.py, log tools/bench/replay_vis_76d.log run 2 = 35/0; card 76-5).

OBSERVED (test run 2): harness = IMAQ Create -> VUT -> IMAQ ImageToArray, all error outs on indicators. Get-buff copy
(replay_get_buff_image.vi, only #529 -> replay_imaqdx_get_image_buf.vi) with b = 8217, 8218, and b = 5 after a restart:
'Image Pixels (U8)' EMPTY (shape (0,)), every error cluster (False, 0, ''), 'current image number' == b, 'Missed frames?'
TRUE. Cal stand-in (replay_get_image_cal.vi), 3 calls: pixels EMPTY, errors clean, 'Buffer Number Out' 0, 0, 0 (predicted 0,1,2).
The fixture frames are 8-bit 1280x1024 (tools/gpu/fixture.py:5), so a U16 image type is ruled out.

STAND-IN DESIGN (diag_replay_standins.py): For loop whose N comes from an auto-indexed String[] control 'Control Names'
(default meant to be ['1']); uninitialised shift register with Increment in the body; Increment.x+1 leaves by a border wire
(tunnel IndexMode 0) into a top-level Decrement -> k; Q&R(k, y) with control 'y' (default meant 10044); Index Array over
String[] control 'Control Names 2' (default meant = 10044 paths G:\m8_replay_frames\f%05d.tif) -> StrToPath.vi -> IMAQ
ReadFile (Image <- Image In, Image Out -> Image Out indicator). ReadFile's own error out is UNWIRED (the plan says error in
passes straight to error out). Defaults were set by gscript.make_default (SetControlValue on a vi_ref, then OpMakeDefault
'Make Current Default', then save), which returned 38,896 B; then the file was copied.

CLAIM (E1): the defaults did not persist in the saved stand-ins, so N = 0 (loop never runs; the mode-0 output tunnel yields
0; Decrement -> -1; coerced into U32 Buffer Number Out -> 0) and the path array is empty (empty path -> ReadFile errors,
silently, because its error out is unwired) -> the image stays empty. ALTERNATIVE I considered (E2): defaults persisted but
the counter/ReadFile body is at fault. Planned discriminator: a READ-ONLY cold load of both stand-ins reading the three
controls' values ('Control Names', 'Control Names 2', 'y') with nothing run (tools/bench/diag_replay_defaults.py).

Give the strongest reason E1 is wrong, a better alternative, what would falsify E1, and whether the planned read-only
discriminator actually separates E1 from the alternatives (e.g. does a cold vi_ref GetControlValue show saved defaults?).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

E1 isn't proven by what was observed: two of its steps are unverified, and one of them may contradict the evidence. The planned cold read is a valid test of whether the defaults were saved, but it can't tell which part of the body failed.

**1. Strongest reason E1 is wrong: it needs −1 to become 0, and that is unverified.**
- E1 says an empty loop outputs 0, Decrement makes it −1, and storing −1 in the U32 `Buffer Number Out` gives 0.
- An empty For loop does output the type's default value through a non-indexing tunnel ([NI forum](https://forums.ni.com/t5/LabVIEW/Default-value-output-of-for-loop-N-0/td-p/3119649)). That link is fine.
- The −1 → 0 step holds only if the counter chain is floating-point (float-to-integer conversion clamps at 0). The Increment on the uninitialised shift register has no source that fixes its type (`diag_replay_standins.py:38-53`), so nobody knows its type.
- If the counter is an integer, LabVIEW's integer-to-integer conversion probably keeps the bit pattern, so N = 0 would show 4294967295, not 0. I couldn't confirm this with a source; integer overflow in LabVIEW does wrap ([lv.qizhen](https://lv.qizhen.xyz/en/data_number/)), and [the NI thread](https://forums.ni.com/t5/LabVIEW/Data-conversion-from-I32-to-U8/td-p/2217324) doesn't settle conversion. If that holds, the observed 0,0,0 **falsifies** N = 0.

**Supporting weaknesses:**
- **The "silent" ReadFile error needs error handling to be off.** ReadFile's error out is unwired. With automatic error handling on in the stand-in, an error opens a dialog ([labviewwiki](https://labviewwiki.org/wiki/Automatic_Error_Handling), [NI help](https://documentation.help/NI-LabView-Local-Project-Settings/VI_Auto_ErrorHndl.html)). `_run`'s watchdog would catch that dialog and raise (`tools/gscript.py:365-379`), and none did. So either the stand-in has automatic error handling off (it was copied from an NI pane, so this is plausible but unmeasured), or ReadFile did not error.
- **The 38,896 B proves nothing about the defaults.** `make_default` never reads OpMakeDefault's error out and just returns `save()`'s byte count (`tools/gscript.py:2991-2995`). Run 1 returned 38,912 B with different wiring. This makes E1 *possible*; it doesn't show the defaults are missing.

**2. Alternative explanations**
- **E3: the defaults are present and the body fails.** The frames exist (`G:\m8_replay_frames\f00000.tif`–`f00002.tif` are on disk), so an empty image then means the fault is inside the stand-in's body. Candidates:
  - `claudeDev\StrToPath.vi` (`diag_replay_lib.py:22`), whose behaviour is never checked;
  - the index from Q&R reaching Index Array as a non-integer or NaN if the chain is floating-point (Q&R(x, 0) with y missing).
- **E4: the counter doesn't carry over between calls.** The harness is cached by `g.op` (`gscript.py:220-225`), so a non-reentrant stand-in should keep its shift register and count 0,1,2. A reentrant stand-in (inherited from the IMAQdx pane base) with clone churn gives 0,0,0 even when N = 1. So 0,0,0 alone doesn't pick between N = 0 and "no carry-over".

**3. What would falsify E1**
- The cold read returns `Control Names` = ['1'], `Control Names 2` with 10044 elements and [0] = `G:\m8_replay_frames\f00000.tif`, and `y` = 10044.
- Or the counter chain turns out to be an integer type (then N = 0 predicts 4294967295, not the 0 observed).

**4. Does the planned discriminator separate them?**
- **Only E1 from "the defaults are fine".** A VI freshly loaded after a restart and never run holds its saved defaults, so `GetControlValue` returns them. That is valid as long as nothing loaded it first; `diag_replay_defaults.py:14-17` restarts and touches nothing else, so it holds.
- **If it says the defaults are fine, it can't choose between E3 and E4.** It also doesn't check either unverified step above.

**Cheapest discriminating test: extend `diag_replay_defaults.py`, still read-only, in the same cold load.**
1. The three controls, as planned.
2. The numeric type of the Increment → Decrement → `Buffer Number Out` chain, read from the diagram report.
3. The VI's automatic error handling setting and its reentrancy setting.

**How to read the result:**
- **Defaults missing, counter floating-point, error handling off:** E1 holds as stated.
- **Defaults missing, counter an integer:** the N = 0 half of E1 is wrong even though the defaults are missing.
- **Defaults present:** the next step is a run, not a read. Put an indicator on the path after StrToPath and run IMAQ ReadFile on f00000.tif in a scratch harness.

I still think "missing defaults" is the most likely cause of the empty image. What would change my mind is either `Control Names 2` coming back full, or the counter being an integer.

Two notes:
- Plan mode blocked writing the plan file, so this review exists only in this reply.
- The Figma connector needs authorising in the claude.ai connector settings before it can be used; nothing here needed it.

## Sources

(extract from answer)

## What was done with it

Material session 76-5, 2026-09-25 05:1x (copied here by material session 76-6 from
`tools/bench/cards/disposition_76-5-t1.md`). Accepted as framing: E1 (defaults not persisted) is not proven by 0,0,0 alone;
E3 (body fault, e.g. StrToPath.vi / Q&R index) and E4 (reentrant stand-in, no carry-over) stay open. Applied s4 in part:
tools/bench/diag_replay_defaults.py (read-only cold load, nothing run) reads the three hidden controls' saved values plus
the VI's reentrancy / automatic-error-handling properties where the ActiveX interface exposes them. The counter chain's
numeric type was NOT read (no reader for a tunnel's type in this fleet). Result: tools/bench/replay_vis_76d_defaults.log
(saved defaults 'Control Names' = [] and 'y' = 0.0 lost, 10044-path array kept); the judgement session ruled on it in
`docs/m8-real-run-plan.md` Pre-decided 19.
