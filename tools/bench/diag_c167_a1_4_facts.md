---
type: facts
status: current
date: 2026-10-12
card: 167-a1-4
---
# Card 167-a1-4 facts - P6-2 replay readiness (PD404(g)), offline, LabVIEW reads 0
- Run `tools/bench/diag_c167_a1_4_ready.py` -> `diag_c167_a1_4_ready.log` 13/0 (log holds two runs; the second wrote the outputs). `p6_replay_ready.md`
  ee2c7cb5bb54815f378b071d9331bd38, `p6_replay_ready.json` 50029b317615488eff22470f499a0ae5. 9 inputs + seven VIs equal before/after; no LabVIEW.
- Swap sites (plans 78/95/110 identical): #6810 'get buff image-lost frames.vi' (S1 json:89810), #22692 IMAQdx Get Image.vi (S1 json:90152);
  the recipe resolves BY UID (stage_replay_swap.py:30,39-40,44); A2 is fatal if the callee basename differs.
- Both uids present in 7815af09, class SubVI, same frame diagram (6810 d639 = loop 1.1; 22692 d22650 in Sequence #22541), same terminal names.
  #22692 wire partners = S1. #6810 differ: Image Out -> #28565 SelectorTunnel (S1 #5058 'Image In'); 'current image number' adds
  #26879/#27039/#28512; error out adds #28785 (json sites[0].wire_partners_diff). P5 callee names unread (no subvi_calls in the P5 graph).
- Card 110-6 ran nothing (BLOCKED on X9, result_110-6.json facts[7]); the replay legs ran under 110-7 (result_110-7.json facts[5]).
- Motors NOT kept off: only the two camera calls are swapped; each leg runs v5.main() on the swapped copy, whose device init "drives the
  PI stage and the ASI" (v5:549-550). Guards: VISA open/close of Rotor + ASRL5::INSTR (v5:540; legguard:15,34); motor_gate --session start
  before Run, refused on exit != 0 (v5:554-561; v4:205-210); LabVIEW gone, then post-run TMX? == 39 (v5:715-723). Both 110-7 legs
  motor_tmx_after 39.0 (leg.json); last v5 json G93: POS_BEFORE=30 travelled=30.000 (m8_v5_replay_s1_p15_r120.json:191).
  Headers say `hardware: none` (drive_m8_replay_110.py:103, diag_c104_leg.py:237, drive_m8.py:150).
- Compared: first tra* and cal* per run_dir only (m8b_replay_compare.py:16,27); TIFFs deleted (v5:688). X/Y/Z = per-cell f64 bits of cols 3..
  over min(rows) rows (:35-36,45), not file bytes; cal = byte compare (md5 + first diff offset), NOT gated (:47,50).
- 110-7: rows 4443/8548, common 4443, X/Y/Z diff 0; col1 trans 114 rows, col2 rot 1 row differ; cal len 857376 both, first diff byte 857296.
- Missing for a ring file: PLANS literal 78/95/110 (stage_replay_swap.py:22); driver hard-codes S1 replay copy 126f8497, stage_replay_swap_110.json,
  label 110-7, INDEX text (drive_m8_replay_110.py:19-20,80,86); --leg replay_s1 + m8_replay_s1_*.json (diag_c104_leg.py:33,176; drive_m8.py:68);
  M7 fixed md5s (drive_m8.py:121); cal/other files ungated vs PD374(f) 'saved files bit-identical' (docs/d1/ring-p5.md:70); no stored ring
  callee census (only build_ringpickslot_v0.py holds the names).
- P5 SubVI uids with no S1 call row: 9317, 23099, 29719 (while#16483), 29724 (loop 1.2), callees unread; S1 calls not SubVI in P5:
  7774, 9944, 14858, 19705, 28233 (md X3/X4).
- Frames G:\m8_replay_frames + manifest exist; stand-in frame = f(k mod 10044), k = own call counter; buf BN Out = BN In, cal BN Out = k
  (diag_replay_standins.py:8-9). Replay VIs + S1 replay copy equal their pins. No D1_ring_p6_*.vi exists.
- Rewritten (not importable): line_of, lv_running (diag_c167_a1_2_crows.py:62-80). Gate fp-99 logged (protocol.py:572 name match on a grep).
