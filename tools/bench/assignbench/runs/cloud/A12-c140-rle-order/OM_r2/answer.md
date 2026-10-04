ACTION: CLOSE
CARD: -
REASON: Card 140-1 PASSed 7 of 7 gates, and that covers all three purpose items.
1. **Session table:** the X10 table for v14 has 9 sessions on the current read model and 8 if BIND reads are merged. Every session peaks at or under 675 MB (prep_c140_1_sessions_r2.log:7-23).
2. **BIND merges:** step 1 goes from 29 reads to 14 at the minimum. Even so, step 1 still can't run as a single session (712.7 MB).
3. **Facts file and OPEN line:** the facts file is written and its OPEN line covers the cut choice and whether a deferred-bind edit to stagexec is worth building.

Card 140-2 went beyond the purpose. It stopped at error 1055 in op 3 of its scratch run: removing loose ends on w23255 right after op 2 deleted #10171. Whether to change the plan order, accept a 678.5 MB peak, and remove the stale provisional flag from v14 are all plan decisions for judgement, not a retry.
HANDBACK-QUESTION: -