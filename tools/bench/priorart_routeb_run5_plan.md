# D1 route-B — RUN 5, the recipe `tools/recipes/build_d1_routeb_v2.py`

⚠️ WHY A NEW FILE NAME. `build_d1_routeb_v1.py` carries a standing prior-art stop record released for its
hash 9ff90ded8f01; by design (`docs/cycle18-plan.md` Pre-decided 2) a changed hash means UNREVIEWED, and
`tools/stop_record.py` then refuses EVERY command naming it — including the command that would review it. So
v1 was restored byte-for-byte to its released hash (the launch gate itself verified this by allowing the copy
command) and the four changes were applied to a byte copy, `build_d1_routeb_v2.py`, which is what this review
is about. Nothing else differs between the two files.


Run 4 (`tools/bench/build_d1_routeb_v1_run4.log`) ended 80 PASS / 1 FAIL and then crashed with LabVIEW
`error 2` (memory full) inside `settle_index_modes()`. Run 5 changes FOUR things and nothing else. All four
were decided by the cycle-36 judgement session after the mandatory failed-prediction review
(`archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md`, claude/hypothesis opus-max, ANSWERED).

1. `TEMP_SINK_AUTHORISED = False -> True` (recipe `:285`-ish), authorising the TEMPORARY-SINK branch for the
   **`Z/dZ` row only**. The branch is already coded at `:1257-1278` and uses ONLY already-built ops:
   `OpCreateEqual_v0` -> `wire_control` -> `OpConnectFromWire_v0` -> `delete_object` +
   `remove_bad_wires_scripted`. No new op, no new device. `SR_QUEUE_AUTHORISED` stays `False` permanently.
   Grounds: the alternative (cycle15 Pre-decided 3's REORDER) has NO by-index route — `ControlTerminal #403`'s
   node index on `Diagram[56]` is `None` (`build_d1_routeb_v1_run4.log:163-164`) — and the review measured that
   the S3 node moves cut `w730`, not the `#403` reparent.
2. `fact(labview_handles())` inserted immediately BEFORE the `g.count(TARGET, "LoopTunnel")` call that raised
   `error 2`, because no handle reading brackets it and the SAME call succeeded at 51,284 handles at S1
   (`build_d1_routeb_v1_run4.log:26-27`).
3. The `done/failed/noroute` ledger print MOVED ABOVE `settle_index_modes()`, plus a counts `fact()`. Run 4
   lost all 66 `s3w` ledger rows because the print sat after the call that raised.
4. The `finally:` block RENAMES the working copy aside (`..._crash_<HHMMSS>.vi`) on the EXCEPTION path only;
   the normal path still deletes it. `s0()` removes any earlier `_crash_` copy so they cannot accumulate.

Unchanged: rule 1 (the original is copied, md5 gated before and after), the cold/preloaded `ExecState`
protocol (Pre-decided 14a/16), the SINK RULE, every gate, and the build order of `docs/d1-route-b-plan.md`.

QUESTION FOR THE PRIOR-ART REVIEW: has any of these four changes — the temporary-sink `Z/dZ` route in
particular — already been built, measured, refuted or settled in this project's own files?
