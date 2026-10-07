# Brief chat-T4 - finish fault 2 (object identity): port arm A13K's address fix so the s04 rebase passes

Card chat-T3 (result_chat-T3.json, PD347) made the creation map work: s03->s04 binds 15 nodes + the row-less While by map,
0 fallbacks. The full s04 rebase then refuses at ADDRESS #-28.'inner' (unnamed shift-register inner terminal) and
#-45.'cond' (row-less While's stop terminal). Arm A13K solved exactly this offline in its own worktree (V6_bench\A13K,
card 145-a3-1 and the cycle-145 round-3 cards; PURPOSE_MET 13:11) - but that code is not in main.
Do: review A13K's change (git diff of V6_bench\A13K vs its setup commit 298a0030 for tools/addrcheck.py, stage_prerun.py,
stagexec.py and their self-tests), port only what resolves these two address classes (face/cond selector by recorded
creation map / terminal index - no guessing), and show on the recorded fixtures (tools/bench/fixtures/cmap_s03s04) that the
full s04 rebase now PASSES binding + addressing, then dry + prerun of the s04 plan offline. Existing self-tests green or
explained. PD in docs/d1/tooling.md + INDEX; commit by explicit path. OFFLINE ONLY (experiment running; no LabVIEW).
Return one result/1.
