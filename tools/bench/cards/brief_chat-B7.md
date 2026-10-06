# Brief chat-B7 - live-cycle bench harness: 4 arms x 2 cycles, each in its own bench directory

User 2026-10-06: "두 싸이클을 돌려보는데, 원본에 바로 적용하지 말고 우선은 벤치 전용 디렉토리를 만들어서 변경 사항 저장하는게
좋을듯. 이후에 Chat GPT로도 싸이클 돌려보고 비교할 예정" ... "A 조건, A+1~3 적용 조건, A+1~3 + Karpathy 조건, B 조건 이렇게
벤치 돌려보자. 여기 최적화 결과를 바탕으로 GPT 비교 할 예정임." Questions to answer: (1) are the rule changes useful,
(2) is the agent change useful. The result format must later accept a ChatGPT (Codex CLI) arm too.

## Arms (each 2 runner cycles, same starting state)
| arm | tools commit | flow | extra |
|---|---|---|---|
| A | master 0fc16ea0 (S1 + early-error hooks E3 + purpose flow A1) | purpose (Sonnet 5.5 high assignment) | - |
| B | same commit as A | `--flow legacy` (Opus judgement dispatches, 6-card cap) | - |
| A13 | master after card chat-F2 (+ chat-F3 records) | purpose | postconditions, test records, generated docs |
| A13K | same as A13 | purpose | Karpathy's 4 principles added to the material + assignment agent prompts |

Karpathy text: forrestchang/andrej-karpathy-skills CLAUDE.md - fetch it, record its licence; add it (verbatim if the
licence allows, else a faithful paraphrase with attribution) as one section in that arm's agent prompts only.

## Harness (build now, offline; do not run any arm)
- One git worktree per arm OUTSIDE the project folder (e.g. G:\...\2. Tracking\V6_bench\<arm>), branch bench/<arm>; the
  main project's working tree, STATUS and runner are never touched; the main STATUS STOP line stays.
- In each worktree: .claude/settings.json hook paths re-pointed to that worktree; STATUS without the STOP line; a fixed
  purpose next.json = the SAME for every arm (P4 session 3 from the adopted s02 file, as tools/bench/next.json now says).
- LabVIEW outputs of an arm go to claudeDev\bench\<arm>\ only; the start VI (D1_ring_p4s02_20261003_110001.vi, md5
  84cac487...) is byte-copied there; nothing in claudeDev outside bench\<arm>\ is written (make the claudeDev root an
  env/config the tools read; verify with a dry run that every write path resolves under bench\<arm>\).
- Runner per arm: `cycle_runner.py --cycles 2` from the worktree, no supervisor; motor limit / Error List / LabVIEW-close
  hooks stay on (rig assembled, motor grant in force). Arms run ONE AT A TIME (one LabVIEW).
- A driver script runs a given arm and, after it, collects metrics into tools/bench/livebench/<arm>.json (in the MAIN
  repo, so results survive): purpose met per cycle; wall time; USD (runner + every sub-session); cards issued / PASS /
  FAIL / WAITING with first_fail classes; early catches (guard_write and launch-gate refusals, count + class); hand-backs
  and their trigger; LabVIEW runs; saved VIs (md5); files and lines changed outside claudeDev; tools created. Same JSON
  schema for any future arm (e.g. a Codex arm).
- Dry-run the whole harness with a stub claude for one arm (no LabVIEW, no motors) and show the metrics JSON.
- Write tools/bench/livebench/README.md: arms, commits, how to run, the order (A, B now; A13 and A13K after chat-F2/F3).

## Limits
labview none, hardware none in this card (it only builds and stub-tests the harness). Do NOT edit tools that chat-F2 is
changing (gscript.py, stagekit.py, stagexec.py, stage_prerun.py, doc_lint.py, docs/toolkit-capabilities.md); if the
harness needs a change there, put it in the worktree only or report it. git worktree add / branch creation allowed;
commit your harness files in the main repo by explicit path. Edit tool only. Return one result/1 JSON object.
