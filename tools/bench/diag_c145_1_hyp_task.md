ATTACK this claim about a failed prediction (card 145-a1-1, LabVIEW scratch run of P4 session 4).

Run: tools/recipes/stage_d1_ring_p4_s04v18_scratch.py (imports tools/recipes/stage_d1_ring_p4_s04v18.py unchanged), plan
tools/bench/plan_ring_p4_s04v18.json, log tools/bench/diag_c144_p4s04v18_scratch.log (BGRUN END rc=1, 409 s).

Prediction: every op real == simulated; both subVI drops (PS1 op 1 RingPickSlot_v0.vi, SQ1 op 10 RingSeqCheck_v0.vi) bind.
Observation: ops 1..9 PASS (STEPX diff 0; PS1 bound -1 -> #29719, log :83). Op 10 (SQ1 drop on Diagram #23166) created SubVI #29724
with 12 terminals (log :230-242): 8 named (n1 n2 last Latest discards sinks; valid, next discards, next last sources) + 4 rows named ''
(is_source False). The executor's binding refused (log :255-256):
  sim {(Terminal,False,n1):1, n2, last, Latest, discards, (Terminal,True,next last), next discards, valid} (8 keys)
  real {...the same 8... + (Terminal,False,''): 4}
Run stopped in op 10; work copy saved by the broken-intermediate route; LabVIEW gone; input md5 unchanged; peak 608.0 MB.

CLAIM (to attack): this is OUR PLAN's defect, not a LabVIEW/tool fault. The plan's SQ1 action (plan_ring_p4_s04v18.json:310-357) lists
only the 8 named terminals and its own `why` says "PROVISIONAL terminals ... (pane slots + unassigned '' rows unread)", while PS1's action
(:139) was written from the MEASURED pane and carries "unassigned slots '' sinks as bed SubVI rows" -> PS1 (12 rows, 7 '') bound and SQ1 did
not. A 12-pane connector with 8 assigned slots yields 4 '' sink rows on the SubVI node, so the fix is to take SQ1's terminal list from a
measured read of RingSeqCheck_v0.vi's connector pane (8 named + 4 '' sinks), then re-run simulation/dry/prerun and regenerate the pred
(including its Error List block) before a new scratch. No stage tool (stagexec/stagekit/stagesim/stage_prerun) needs a change.

Already ruled out (from the log): memory (peak 608.0 vs stop 680); wrong subVI file (label 'RingSeqCheck_v0.vi', 8 names match);
earlier ops (diff 0 through op 9).

Give: the strongest reason the claim is wrong; an alternative explanation (e.g. the binder should ignore '' rows, or the pane has a
different slot count, or '' rows differ between drops); what would falsify the claim; the cheapest discriminating test (offline if
possible, e.g. compare the PS1 plan rows to the PS1 real table at log :66-78, and read tools/stagexec.py's binding of SubVI keys).
