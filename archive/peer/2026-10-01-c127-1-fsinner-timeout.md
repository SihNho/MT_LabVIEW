# c127-1-fsinner-timeout

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2944  in 24 / out 11538 / cache-create 102535 / cache-read 1216438  (136s, 16 turn(s))
- **date:** 2026-10-01 23:06:25
- **outcome:** ANSWERED (140s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about tools/bench/diag_c127_1_fsinner.log (script tools/bench/diag_c127_1_fsinner.py, plan tools/bench/diag_c127_1_fsinner_plan.json).

FAILURE: `BGRUN TIMEOUT killed after 2402s (limit 40.0 min)` (diag_c127_1_fsinner.log:116). The last line before the kill is
`PASS S_latest connect_term_uid op err ''` (log:112), i.e. the 6th and last wire returned in 6.7 s; the kill came during the
post-connect reads (census snapshot, OpAllTerms_v1 read, wire_joints, wire_remove_loose_ends, then an Error List GUI read).

CLAIM: the timeout is a BUDGET error in the script, not a LabVIEW hang or a defect of the measured route:
 - the script does an Error List GUI read (errorlist_check E.read, ~125 KB raw each) after the first crossings and after EACH
   second sink; raw-file mtimes 22:35:51, 22:44:34, 22:53:00, 23:01:30 => one wire + its reads + one Error List read takes
   ~8.5 min; 4 such reads + setup (start 22:22:33) cannot fit in 40 min, and S_latest's would have ended ~23:10;
 - bgrun --max-min 40 was BELOW the Stage's own deadline_min=42 (diag_c127_1_fsinner.py:22), so the Stage's orderly close
   (scratch delete, md5 checks, LabVIEW kill) never ran; LabVIEW (PID 17792) and the scratch were left behind.
 - every measured prediction up to the kill held: A_i/A_bn census == 126-6's; 3 second sinks (S_rat1/rar1/raf1) census {},
   FS outer tunnels 60 -> 60, Is Broken? False, wire 32859 joints 3/4->4->6->7, terms 2->3->4->5, loose 0, Error List 61 / loose 24
   unchanged (log:79-109). S_latest's op returned wire 27589 (the existing inner-face wire), err '' (log:112) but its census was
   never read.

Questions: what is the strongest reason this claim is wrong (e.g. a slow-down per read that signals a growing leak / handle
growth, or a GUI read that hung rather than ran slow)? An alternative explanation? What would falsify it? The cheapest
discriminating test before re-running (e.g. Error List read once at the end only, deadline ordering bgrun > Stage deadline)?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is half right.** The budget arithmetic holds: the run was simply too long for 40 minutes, and nothing in the record suggests LabVIEW hung or slowed down. But its explanation of why the orderly close never ran is wrong, and it puts the kill at the wrong point.

## 1. Strongest reason it is wrong: the Stage deadline would not have saved the run

The claim says the kill limit of 40 min was below the Stage's own 42 min, so the Stage's orderly close never ran. That implies a kill limit above 42 min would have produced an orderly close. It would not.

- `Stage(deadline_min=…)` stops nothing by itself. `left_s()` (`tools/stagekit.py:294-295`) is only read by the Jev row-check time budget (`stagekit.py:564`).
- `diag_c127_1_fsinner.py` never calls `left_s()`. Scripts that do stop early check it themselves (`tools/bench/allterms_s4.py:112`, `tools/bench/c90d_border.py:26`).
- With any kill limit, the script would have gone on into S_latest's Error List read, ending around 23:10–23:11 (about 48 min). Any limit under about 49 min still kills it. That includes the script's own documented launch line, `--max-min 45` (`diag_c127_1_fsinner.py:12`).
- Unexplained fact: the run was launched with 40 min (`log:1`), not the documented 45. Something or someone changed the limit, and the claim does not mention it.

So swapping the two deadlines is not a fix. The fix is a `s.left_s()` check before each second wire (and before each Error List read), plus a kill limit above `deadline_min`.

## 2. The kill did not land in an Error List read, and "not a hang" is not shown

I split the time using `tools/gui_actions.log`, whose lines are timestamped (the diag log's lines are not):

| Error List read | GUI actions | first → last action | raw file written (from the brief) | gap to the next read's first action |
|---|---|---|---|---|
| first | 65 | 22:28:05 → 22:33:44 (`gui_actions.log:7953-8017`) | 22:35:51 | 102 s |
| S_rat1 | 63 | 22:37:33 → 22:42:40 (`:8018-8080`) | 22:44:34 | 99 s |
| S_rar1 | 63 | 22:46:13 → 22:51:06 (`:8081-8143`) | 22:53:00 | 102 s |
| S_raf1 | 63 | 22:54:42 → 22:59:36 (`:8144-8206`) | 23:01:30 | — |

- **The kill came at 23:02:34** (start 22:22:32 + 2402 s).
- **There is no GUI action after 22:59:36**, so S_latest's Error List read never started.
- **`CENSUS S_latest` never printed.** It is printed at `diag_c127_1_fsinner.py:60`, right after the post-connect `census_snapshot`, `g.uids` and `terms(W)` (lines 54-55). So the kill landed inside those reads, not in "wire_joints, wire_remove_loose_ends, then an Error List read".

**Alternative explanation:** the post-connect `report_all` census or the `OpAllTerms_v1` read for S_latest hung. Its op returned wire 27589, the existing wire on the inner face.

What the evidence says about this alternative:
- **It does not settle hang vs. slow.** At the kill, the run was 64 s past the last raw-file write, 6.7 s of that in the connect. Earlier wires needed about 100 s for their whole non-GUI stretch before the next read's first GUI action, so 64 s is inside the normal range. The log has no timestamps, though, and cannot show whether that read was running or stuck.
- **There is no sign of a leak or slowdown.** The GUI time per read shrank (5.65, 5.1, 4.9, 4.9 min), the actions came at a steady 4–5 s each, and connect times stayed flat (7.2 / 6.5 / 6.6 / 6.7 s). The weak spot: handle count was read only once, after the restart (33,993, `log:17`), so handle growth during the run was never measured.

How the 8.5 min per wire divides up:
- About 5 min of GUI walking per Error List read.
- About 2 min more between the last GUI action and the raw file being written. My guess is the UI tree dump (`lv_errorlist.read`'s `dump_tree=True` default, `tools/lv_errorlist.py:798`); I have not measured this.
- About 100 s of script and COM work: the wire and its reads, plus opening the Error List.

The claim's attribution of most of the time to the Error List read is correct.

## 3. What would falsify the claim

A rerun that skips the per-wire Error List reads, where S_latest's post-connect census still produces no `CENSUS` line for more than about 3 minutes. That would be a hang tied to this wire, not a budget problem. A slowing per-read pattern on a longer run would point to a leak instead.

## 4. Cheapest discriminating test

1. **Free, with no LabVIEW:** nothing beyond the timeline above. It already shows the run was within normal timing at the kill.
2. **One rerun:**
   - Put a timestamp on every `s.fact` (or log `time.time()-s.t0`) before and after each read inside `wire()`.
   - Do one Error List read at the end only, with `dump_tree=False`.
   - Add `if s.left_s() < 300: break` before each second wire.
   - Launch with `--max-min` at least `deadline_min` + 5.

   Expected: about 5 min of setup, 4 × about 100 s of wires, and one Error List read of about 7 min, so roughly 20 min in total. If `CENSUS S_latest` prints within about 60 s of its connect, the claim is confirmed; if it stalls, the hang alternative holds.

## Also owed

- **Leftovers.** The X md5 gate, scratch deletion and LabVIEW kill never ran, so check that the scratch VI `scratch_c127_1_fsinner_20261001_222233.vi` and LabVIEW PID 17792 are gone. Check the input md5 directly, since the gate never ran (the input should not have been written: the script only ever opens a copy).
- **Lost results.** `OUT` is written only at the end (`diag_c127_1_fsinner.py:123`), so the three completed second-wire results live only in the log text. That breaks the "a step leaves a file" rule (§ splitting big steps in `CLAUDE.md`). Dump `OUT` after each wire.

Everything above comes from this project's files. I made no claims about outside tools, so no web search was needed. I checked the raw-file times only through the `gui_actions.log` timeline, not with `stat`.

## Sources

(extract from answer)

## What was done with it

Material session, card 127-1 (no decision taken here; the rerun is the judgement session's call, card chat-P2):
- ACCEPTED as fact: `Stage(deadline_min)` stops nothing by itself (`tools/stagekit.py:294-295`); the 40-vs-42 min ordering was
  not the cause; the kill landed in S_latest's post-connect census/OpAllTerms reads (no GUI action after 22:59:36), not in an
  Error List read. The launch used `--max-min 40` (the docstring said 45) because the card's 50-min budget was already partly
  spent - a material-session choice, recorded.
- Leftovers handled after this review: LabVIEW kill, scratch delete and bed/original md5 check by `tools/bench/diag_c127_1_cleanup.py`
  (log `tools/bench/diag_c127_1_cleanup.log`).
- The three completed 2nd-sink results were saved from the log into `tools/bench/census_samples.json`
  (`connect_term_uid` / `fs_inner_face_branch`, cites log:83,93,103,109) and `tools/bench/scratch_verify/gscript.connect_term_uid_20261001_230600.json`.
- The review's rerun shape (one Error List read at the end with `dump_tree=False`, `s.left_s()` check before each 2nd wire,
  timestamps, `--max-min >= deadline_min + 5`, OUT dumped per wire) is passed to judgement as the proposed retry; not run here.
