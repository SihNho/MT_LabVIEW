# Brief chat-F3b - escalation (rung 1) of chat-F3: finish the real-LabVIEW function records

Read brief_chat-F3.md and result_chat-F3.json first (state: fp-42 released as FNTEST-EXEMPT, switch scope = plan_ring_p4_v18
+ s03v18, G1 run 2 recorded 5 PASS / 2 FAIL, failure budget of the first card spent).

Chat decisions:
1. loop_in 1055 on a bed with no SubVI is a REAL finding about a default (gscript.py:1530 src_cls 'SubVI' index 0), not a
   test bug: keep that FAIL record, and add the precondition "needs a SubVI on the target diagram (default source)" to
   loop_in's entry in tools/fncontract.py so it is checked at the call (fail with a clear reason instead of 1055).
2. Then test every function in the context the P4 plans use it: G1 run 3 with the PathToStr subVI dropped BEFORE the
   While (P4 beds always hold SubVIs), and guard creates against None. Do not change any function's behaviour.
3. Write and run G2 (connect / delete / stop / shift register / rle / const routes), then any remaining plans of the 58.
4. Coverage of the 58, gate mode by the stated rule, regenerate the capability block, PD + INDEX, commit.
Each LabVIEW batch < 25 min, handles flat, scratch only under claudeDev\fntest\, Edit tool only (no heredoc patches).
