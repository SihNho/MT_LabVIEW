---
card: 170-a2-2
status: current
date: 2026-10-13
---
# Brief 170-a2-2 (assignment 170-2, the ONE retry of 170-a2-1) - write the .cal date/time field rule from the F4 read already taken

Plan: `docs/d1/ring-p6.md` PD410(e), PD409(b). Previous card: `tools/bench/cards/result_170-a2-1.json` (FAIL: gate V2 and gate H). Its LabVIEW read WORKED: the cluster
type and #26126 were read, nothing was saved, `D1_s1_copy.vi` is 3e3d23ce, LabVIEW is gone (`tools/bench/diag_c170_a2_1_f4.log:3-30`, json `diag_c170_a2_1_f4.json`).
Why it failed, and what this retry changes:
- Gate H was a script criterion error (abs handle delta <= 100; the count FELL 57984 -> 51489, refs live 0, `f4.log:25-26`). It is recorded as a fact with the
  correct meaning (growth is the leak signal; a fall is not). No new LabVIEW session is needed for it.
- Gate V2: `OpConstValue_v1` reads a StringConstant only; #26136 is a FixedConstant and #26145 an EnumConstant, and the base-class cast returned a void variant
  (`f4.log:21-24`; `gscript.py:4410,4429`). No existing op reads them. This card does NOT build a new op and does NOT open LabVIEW (the purpose says ONE
  read-only LabVIEW card, and it ran). The two values are written as "NOT READ by an existing op", and the text they produce is shown as OBSERVED in the stored cal001
  of 110-7 (labelled observed, not read). Whether a value read matters is the judgement's, not this card's.

## Steps (offline: NO LabVIEW session, no hardware; stop at the first unexpected result)
1. **Run the offline decoder** `tools/bench/diag_c170_a2_1_cal.py` (written by the previous card, 2 asserts, not run yet; its header says `labview: read` but it makes no
   LabVIEW call, which is why this card carries `labview: read`): `py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c170_a2_2_cal.log -- py -u tools/bench/diag_c170_a2_1_cal.py`.
   (The decoder's own `.log`/`.json` are named `diag_c170_a2_1_cal.*`; if bgrun needs a new log path use the one above.) Its gates D1, D2, W (walk consumes cal001 of
   leg A and leg B exactly), F (printable text) are read as written. A decoder bug found now is fixed in that file (it is yours, new this cycle) and re-run ONCE.
   Review it first for the rules in `docs/script-writing.md` (calls into shared functions: it imports `gscript.parse_type_descriptors`, good; its `walk`/`td_label` are new).
2. **Write the rule into `tools/bench/p6_replay_facts.md` F4** (replace that section's body only, edit with the Edit tool, keep every other line) and key `f4` of `p6_replay_facts.json`:
   - the cluster layout as read: 9 elements in order with types (from `f4.log:13`), 'Date and time' = element 6 (0-based), a String, bundled by NamedBundler #26446 whose output type equals #26159's (`f4.log:17`);
   - the write call: #26615 ReadWriteFile 'data' <- #26446; 'prepend array or string size? (T)' and 'byte order' unwired = defaults (big-endian, size-prefixed) (`p6_replay_facts.md` F4 old text, graph cites);
   - the position RULE: walk the flattened cluster from byte 0 (arrays: one I32 per dimension then the elements; I32 scalars 4 B; DBL 8 B), the field starts after elements 0-5 and is
     I32 length N + N text bytes (length = 4 + N), i.e. offset and length are read from the file itself by this walk; give the decoder's function name and file:line;
   - the date/time text formats: #26126 'want seconds?' = TRUE (`f4.log:19-20`); #26136 and #26145 NOT READ (`f4.log:21-24`); the OBSERVED text of both stored cal001 files and its split (date, separator, time), labelled OBSERVED;
   - the per-file facts for 110-7 legs A and B from the decoder (offset, length, text, bytes outside the field identical or not). Facts only; any difference outside the field is REPORTED, not diagnosed.
   verdict word: FACT for the layout and the offset/length rule; NOT-DETERMINED only for the two values.
3. **Gate H as a fact** in the facts file or the card result: handles fell by 6495, refs live 0 (growth-only criterion). Do not edit `diag_c170_a2_1_f4.py` or its log.
4. **End of card:** `tasklist` shows no LabVIEW; hash `3e3d23ce`, `c2d9c13c`, `126f8497` again (unchanged); only facts/diag files written.

## Not in this card
No LabVIEW session, no new op VI, no recipe/plan/STATUS/INDEX/hook edit, no motor/camera, no peer. A gate FAIL = RETURN with the facts, no second attempt.
