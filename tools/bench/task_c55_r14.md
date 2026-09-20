ATTACK the explanation below. Find the strongest reason it is WRONG. Do not agree with it.

## The failed prediction

`tools/bench/reverse_census_walk.py` (a files-only diagnostic; LabVIEW was never opened) ran at 08:52 and
ended `BGRUN END rc=1`, 26 pass / 1 fail. The failing line in `tools/bench/reverse_census_walk.log` is:

    FAIL  R14 every uid c53_row_class.json keys is present in nodeterms  8/12 present; missing [4256, 4274, 4334, 4344]

The gate's predicted value was 8/8. The run measured 8/12.

## The explanation I formed, which you must try to destroy

"The measurement is correct and the GATE'S WORDING was wrong. I built the set `keyed` from
`tools/bench/c53_row_class.json` by unioning (a) every `table[].owner_uid`, (b) every
`table[].other_end[].uid` whose `kind` is `node`, (c) `focus_set`, and (d) BOTH uids of each entry in
`sr_pairs` ({visa: [4334, 4344], position: [4256, 4274]}). (a)-(c) give 8 uids
{48, 3447, 3529, 3560, 10407, 10686, 10757, 12589} and all 8 are present in
`tools/bench/main_vi_nodeterms.json`. (d) adds the four SHIFT-REGISTER uids, and a shift register is not a
`Node` — `tools/gscript.py:947-948` states the LabVIEW classes are `LeftShiftRegister` / `RightShiftRegister`
— so a census that enumerates `Nodes[]` per diagram cannot contain them. The gate therefore could not have
succeeded against ANY correct census, so it is being demoted to a FACT line rather than re-emitted."

## Specific things to attack

1. Is "a shift register is absent from `main_vi_nodeterms.json` **by construction**" actually established
   by the evidence cited, or is it an inference dressed as a citation? `gscript.py:947-948` is a docstring
   about `LoopTunnel`s, not about what `Nodes[]` returns. Name what would have to be read to establish it
   properly, and say whether the cited line does that job.
2. Is there a reading on which 4256 / 4274 / 4334 / 4344 SHOULD have appeared in that census — e.g. the
   uids are not shift registers at all, or `Nodes[]` does include them on some diagram, or
   `c53_row_class.json`'s `sr_pairs` means something other than shift-register object uids?
3. Is demoting a failing gate to a fact after seeing it fail the same "post-hoc gate rewrite" pattern that
   `archive/peer/2026-09-20-c54-netmap-wires-g12.md` named as a fault in cycle 54? If so, say what the
   honest alternative is.
4. The same run claims (gates R5/R6/R7) that the ONLY node uid on which `main_vi_netmap.json` and
   `main_vi_nodeterms.json` disagree is 22963, and therefore that `c53_row_class.json` — an input to the
   17-row loop-1.5 table — is unaffected by the 635-vs-626 discrepancy. Attack that too: what could make
   "the censuses agree on every uid but one" true and still leave `c53_row_class.json` mis-keyed?

## Already ruled out — do not spend the answer on these

* The netmap's 9 extra entries and the tree's 11 were both measured to be uid 22963 and nothing else; the
  netmap sites (diagrams 23, 80, 118, 136, 137, 146, 149, 166, 167) and the tree sites (0, 3, 5, 31, 53, 69,
  75, 84, 128, 143, 151) are disjoint, and `sweep_nodeterms_main.py:56-59` breaks the per-diagram loop at the
  first UID 0, which accounts for 637 - 11 = 626 exactly.
* No `.vi` was opened and no COM call was made in this run, so a live-LabVIEW race is not a candidate.
* `main_vi_netmap.json` is known to truncate TERMINAL lists (`gscript.py:2549`, `:2557-2560`); that is about
  terminals, not about which node uids the file keys.

End with: the cheapest discriminating test, in one sentence, that separates "gate wording was wrong" from
"the census is missing objects it should hold".
