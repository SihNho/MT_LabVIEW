---
type: decision
kind: topic
status: current
date: 2026-10-08
parent: docs/d1/INDEX.md
tags: [d1, tooling, gates, stagekit, terminal-identity, pre-decided]
---

# Result gates D / TD / PB key terminals by POSITION

Opened by card chat-T6 because `docs/d1/tooling.md` is at its 400-line cap. Numbered PD366: the highest PD in the main tree's
`docs/d1/*.md` was PD365 when this was written (2026-10-08, `ring-p4c.md` PD365 = cycle 150's name-free `rebind` key, the same
rename problem on the PLAN side); code cites this file, not the number.

## Pre-decided

366. **(card chat-T6, user 2026-10-08: "두 가지 모두 적용하자"; "단자 네이밍은 몇 차례나 이야기했던 것 같은데, 왜 아직도 수정이 안되는거임?")**
     S1 (PD337, `tooling.md`) moved PLAN ADDRESSING to (owner, terminal index, terminal class); the post-run RESULT gates of
     `tools/stagekit.py` stayed on names and wire uids, so LabVIEW's own renames on wiring (#2626 'array'->'element',
     #9503 'Value'->'') and its re-issue of a deleted wire uid (23807) failed a correct build (cycle 147, `result_147-a1-8.json`)
     and a per-batch renames LICENCE (PD356(b), PD357) had to whitelist them.
     - **(a) Terminal = POSITION KEY** (node, index among the node's rows in READ order, term class, direction):
       `addrcheck.pos_table`, the same index as `addrcheck.triple` (node = `vigraph.node_of`, rows de-duplicated first-wins).
       The name is a report column only (`renames`, INFO).
     - **(b) Wire = its two ends' position keys** (frozenset of sources, frozenset of sinks), never its uid; a deleted wire uid
       present again at the end is INFO (`reuse_noted`); `reuse_bad` is always empty.
     - **(c) TD** (`stagekit.term_identity_gates` -> `term_identity_pos`): lost (base keys absent from real, plus a deleted key
       real holds under another term uid) == gone (base keys absent from the sim end); no `moved` (a kept key whose term uid
       changed - an index or class swap at one node); no `unwired`. **D**: lost wires == the sim's (sets, base space), new wires
       whose every end is on a kept base node == the sim's (sets), and |new| == |sim new|.
     - **(d) Created objects are compared by COUNT, not position:** the simulator's terminal order for a created object is not
       LabVIEW's (s03 Replace Array Subset #29396 'index' vs 'new element/subarray', s04 Wait #11081 in/out reversed: 4/15,
       2/13, 1/8, 2/4 created objects per batch, `tools/bench/selftest_t6_poskey.log` FACT lines) - `stagekit.kept_nodes`.
       Making the simulator emit LabVIEW's order is a separate change (not in this card).
     - **(e) PB** (`stagekit.pb_rename_rows`): every real row on a kept base node whose position key the sim end has gets the
       sim end's name before `vigraph.build4`; wires are untouched, so a wiring change still shows in the cdiff. `unlicensed`
       is always []. Created objects keep their real names (NG checks them).
     - **(f) Licences:** `licence_renames` still parses a pb-licence/1 `renames` list; the gates only echo it
       (`licence_renames_listed`). No new licence needs a `renames` field. The name-keyed code is kept as
       `stagekit.term_identity_names` for comparison only.
     - **(g) Measured, offline** (`tools/bench/selftest_t6_poskey.py`, 43/0, log beside it): per-node read order base vs real
       end identical in ring P4 batches s03/s04/s05/s06 (0 nodes differ); all five stored end reads (s06 twice: 147-a1-8 and the
       147-c3 rerun) PASS TD / D / PB with NO licence, and the 147-a1-8 read that FAILED on names still fails under
       `term_identity_names`; drop / unwire / source change / index swap / class change / a new wire's source change at equal
       counts / `selftest_c147_b1_2`'s T3 and T4 scenarios each FAIL; renaming every terminal or renumbering every wire uid
       still PASSES; `selftest_td_key_c141_3`'s 141-2 uid-re-use case re-asked (K2-K7) as there. The 147-a1-8 end read is kept
       as `tools/bench/fixtures/t6_s06_a1_8_end.json` (git 07202624 blob e364374c). Regressions: `tools/bench/selftest_t6_regress.py`.
     - **(i) Old tests rewritten to these semantics** (card chat-T6 follow-up): `selftest_c147_b1_2.py` - RETIRED assertions
       T0 "default == pre-edit code", T0b "pb_rename_rows(.., None) untouched", T2 "TD FAILS naming 9505/9508", T3
       "reuse_bad == [23807]", T4b "TD FAILS on an unlicensed name"; their scenarios now assert name = INFO, re-use = INFO, loss /
       owner change / kept removed sink = FAIL, plus T1n (no licence). `selftest_td_key_c141_3.py` - RETIRED `recycled == [28004,
       28979]` (T2) and `xu in recycled` (T4); T1-T7 kept on position keys; it imports stagekit inside main() and now declares
       `labview: none`, like `selftest_c147_b1_2.py`. Pins in both match raw OR LF-content md5 (a CRLF worktree checkout).
     - **(h) Recipes need no edit:** the s06 recipe's calls (`term_identity_gates(..., renames=REN, bind=...)`,
       `pb_rename_rows(BASE, L, real, REN)`, `unlic == []`) keep their signatures and output keys; their gate TEXT still says
       "wire uid + source identity" / "licensed" - wording only, the key is the position.
