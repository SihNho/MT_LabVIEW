# Brief for card 110-4 (cycle 110 judgement) — relaunch of L2-B1 after 110-3's PB rename; decisions, not yours to change

110-3 (`tools/bench/cards/result_110-3.json`): launch 1 did 27/27 ops, every checkpoint diff 0, D == sim, FU PASS, peak
625.1 MB, then PB failed on ONE extra row `(2626,'array')` (`tools/bench/stage_d1_l2b1.log:516-522,550`). Briefs 110-1
D/B, 110-2 J/R and 110-3 items 1–3 still hold.

## Decided
1. **The rename is LICENSED, keyed by terminal uid.** Wiring `#5058` onto `#2626` input uid 4168 (as planned) makes
   LabVIEW rename the three UNWIRED inputs uid 2832/4160/4165 from `element` to `array`. Those three are the per-frame
   data crossings owed to QRT (brief 110-1 D5). When QRT wires them, their types decide the names again. The acceptance
   of every split stage is still the recorded-frame X/Y/Z replay (rule 1a). PB therefore maps `#2626`'s sink rows **by
   terminal uid**: a real open row on uid 2832/4160/4165 equals the plan's open row on the same uid, whatever its name.
   Implement it where it touches the fewest released files (plan licence field, recipe PB mapping, or the PB helper).
   Say which one, and run the prior-art round if the launch gate asks for it. No other row is licensed. Any other
   extra or missing row is still FATAL.
2. **Measurement for the rule-1a note (log only, no pass condition):** after op 27 and after the save, log every `#2626`
   input's uid, name and data type string.
3. **RULE-SAME-ROW discharge of the new failure is ACCEPTED.** The failure is fully read from the machine (uid wiring ==
   plan, names differ only on unwired inputs). No hypothesis review is owed.
4. **This is the 2nd and last `stage_d1_l2b1.py` launch this cycle** (RETRY_CAP 2). The launch carries
   `--retry-card tools/bench/cards/task_110-4.json` only if the gate asks for it.
5. After the save: write the explicit expected Error List file `tools/bench/errorlist_expected_D1_l2_b1_<ts>.json` and
   run its reverdict (`tools/bench/diag_c110_errorlist.py`, already written), OK = 0 extra / 0 missing, or report the
   mismatch (PD223(a)).
6. For the B2 tooling card, not here: a stagesim Build Array input-rename rule (so plans predict it).
