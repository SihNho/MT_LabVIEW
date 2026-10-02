# Brief chat-S3 - apply the user's three answers of 2026-10-03 (after chat-M2 and chat-S2)

User: "메모리 낮추고 터널 개수차이로 멈춤은 유지하고 터널 단자행만 다를 경우 기록하자".
1. **Memory limits lower:** X10 predicted-peak FAIL threshold 690 -> **680 MB** (memory_model.json `fail_above_mb`
   or wherever stage_prerun reads it) and the run-time hard stop MEMSTOP 700 -> **695 MB** (find every definition:
   stagekit/stagexec/meter code, launch gates; one source of truth if several copies exist). Basis: chat-M2 measured
   LabVIEW error 2 at 704.8 MB (tools/bench/diag_chat_m1_mem.log:170-173). Update the self-tests that pin 690/700.
2. **Tunnel OBJECT count differences stay STOP** (no change; confirm gateclass treats LoopTunnel, FlatSequence*Tunnel,
   SelectorTunnel, Tunnel as semantic and say so in a comment citing the user).
3. **E1 per-step diffs that are ONLY tunnel FACE/terminal ROWS** (only_sim / only_real terminal rows on tunnel faces,
   names or counts, with no difference in objects, wires or node classes) become **LOG-only** via tools/gateclass.py
   (same soft log tools/bench/gate_soft_log.jsonl). Any object/wire/class difference in the same step still STOPs.
   Self-test: face-row-only diff logs; face rows + an extra tunnel object stops; face rows + a wire diff stops.
4. Re-run gateclass, stagexec, stage_prerun X10 and guard_peer self-tests; all green or explained.
5. Record the decision in docs/d1/tooling.md (next PD number) with the user's words; one line in docs/d1/INDEX.md.
Offline only, runner stopped, no LabVIEW. Edit tool only. git commit allowed. Return one result/1 JSON object.
