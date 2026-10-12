# Applied: scope-cwd-fix-20261012 (card chat-X11, 2026-10-12)

User 2026-10-12: "동의 받고 고쳐 ... 우선은 조심할것". Applied after both debaters wrote the agreement in round 6.

## Agreement lines (verbatim from STATE.agreed)

Claude, `relay/round_06_claude.md`:
- scope-cwd-fix-20261012 동의
- cwd를 경로 추출·중첩 PowerShell·bgrun 자식·in_tools·R4(guardcore.py:183)까지 전달
- 칸 파일 실행 시 honesty 검사, 실패 시 scope_gate 거부
- 미확인 tools/ 실행 혼합과 폴더 변경(cd/Set-Location/pushd) 시 시간 제한 면제 금지(본 폴더 포함)
- 정규화한 cwd≠ROOT이면 드라이브까지 쓴 절대 경로 실행만 면제(bgrun 자식·중첩 PowerShell 포함)
- cwd의 tools/ 밖 실행은 면제 금지
- 상대 경로 제한으로 거부할 때만 칸 내부 절대 경로 안내
- 본 폴더 Codex의 숨은 workdir 문제는 이번에 해결된 것으로 보고하지 않고 별도 안건으로 기록
- 시험: cwd=ROOT 단일 일반 명령(예: debate_gdoc.py say) 판정 유지를 대표 사례로 포함

GPT, `relay/round_06_gpt.md`:
- scope-cwd-fix-20261012 동의
- 본 폴더 Codex의 상대 경로 제한은 이번 범위에서 제외하고 숨겨진 workdir 문제는 별도 기록
- cwd를 경로 추출·중첩 실행·in_tools·R4까지 전달
- 칸 파일 실행 시 honesty 검사 및 실패 시 scope_gate 거부
- 미확인 tools/ 실행 혼합과 폴더 변경 시 공통으로 시간 제한 면제 금지
- 정규화한 cwd≠ROOT이면 칸 내부의 드라이브까지 명시된 절대 경로만 면제
- 상대 경로 제한으로 거부할 때만 절대 경로 안내
- cwd=ROOT의 기존 일반 명령 호환성 유지

## What was changed

| file | md5 at test time | change |
|---|---|---|
| `tools/scope_header.py` | fc973af3030ec8a147b5e4112155d984 | `_abs`/`in_tools`/`launches`/`_seg_launches`/`launch_scope` take `cwd` (None = old behaviour); new `_runs`/`_seg_runs` (keep the raw path token), `_pwsh_inner` (shared by launch reading and the folder-change check), `changes_folder`, `_judged` (ROOT tools/ + cwd tools/), `_cell_honesty` (honesty() of a script outside ROOT tools/, fails closed), `offline_exemption(cmd, cwd)` |
| `tools/hooks/guard_bash.py` | f1219088285f644c291b0e2abd19d671 | `_main` reads `data["cwd"]`; `scope_gate(cmd, cwd)`; `offline_scripts_only(cmd, cwd)` calls `SH.offline_exemption`; the 2b refusal appends the absolute-path hint only when that rule was the reason |
| `tools/hooks/guardcore.py` | 4a8efa7d45a630f72aee8b261b81e567 | R4: `labview_launches(cmd, cwd)`, `concurrency_ban` passes `ev["cwd"]` |
| `tools/bench/selftest_scope_cwd.py` | 6a0bf5b5759f2fc645933244635eb79c | new, 26 gates (A-F below) |
| `docs/guardcore.md` | 9c2d718b2dc3e2ba214b96d9d95bfccd | "Payload cwd" section + the OPEN line for the hidden Codex workdir |

Implementation choices inside the agreement (stated so the debaters can check them):
1. cwd None (payload without `cwd`) = the old rule byte for byte. guardcore events always carry a cwd (`event()`
   defaults it to ROOT, as before), so through guardcore the cwd=ROOT rules apply.
2. Folder change words: cd, chdir, pushd, popd, Set-Location, Push-Location, Pop-Location, sl - at the start of any
   segment (subshell `(`/`{` skipped) or of a nested `powershell -Command`.
3. "Unconfirmed / outside" = a launch that `launches()` parsed whose path is not a file under the cwd's `tools/` (the
   paths `scope_header.py:510` used to skip). Text-only mentions of `py tools/x.py` (e.g. inside a say message) are
   not launches and do not cancel the exemption.
4. The bgrun child resolves against bgrun's PROJECT (`tools/bgrun.py:32,236`), which equals the cwd whenever bgrun
   itself lies in the cwd's `tools/` - the only case that can be exempt.
5. launch_scope judges scripts under ROOT's tools/ AND the cwd's tools/ (union), so scope_gate and R4 never lose a
   main-tree launch made from a cell cwd. Honesty runs only for scripts outside ROOT's tools/.
6. Drive-absolute = `^[A-Za-z]:[\\/]`.

## Test results (logs in `reg/`, run 2026-10-12 13:28-13:33 with the md5s above)

New `selftest_scope_cwd.py`: 26/26 PASS -
A cwd=ROOT `py tools/debate_gdoc.py say` allowed (plain, ROOT spelled with / lower-case trailing, nested powershell);
B cwd=ROOT refused without hint after cd / Set-Location / pushd / Push-Location / nested `powershell -Command "cd ..."`,
  with a missing tools/ file mixed in, with a script outside ROOT tools/ mixed in;
C cell cwd: relative none script refused WITH the absolute-path hint (plain, nested powershell, relative bgrun child);
  drive-absolute allowed (plain, nested powershell, abs bgrun + abs child);
D cell cwd: abs labview build refused; main-tree script and `<cell>/sub/tools/` script refused; cd + abs refused;
  dishonest `labview: none` (imports gscript) = scope_gate "not honest" refusal, absolute and relative;
E no cwd: say allowed, say + missing file still allowed (old rule), cell-relative not seen (refused as before);
F guardcore R4 sees the cell's labview build script via cwd, not without.

Hook self-tests (39 run; 4 with `labview: read` headers not run - card flags.labview none: selftest_census_hookin_c123,
selftest_leg_guard, selftest_prim_gate_c141_1, selftest_stagexec_gate):
- all pass except `selftest_c155_gatefp73` 8/2 (G1, G5 `discard_work`) - the same two fails as the 2026-10-10 log
  `tools/bench/diag_c163_a1_4_st_c155_gatefp73.log` (pre-existing, not diagnosed).
- `selftest_guardcore` 111/0, `selftest_guard_bash_codex` 23/0 (process rc 0; bgrun marks its RESULT line malformed:
  no `gates` field, pre-existing format), `selftest_protocol` 48/0, `selftest_protocol_wiring` 66/0,
  `selftest_shellguard_cand` 93/0, `selftest_launch_gate` 29/0, `selftest_motor_gate2` 85/85.
- printed summaries without a RESULT line, all 0 fail: guard_cycle_fixed 6+2, guard_cycle_rerun 7, guard_peer_budget
  12, guard_peer_failre 29, guard_peer_ladder 21, guard_session 27/27; guard_peer_scan_tmp PASS (schema spelled
  result_line/1, pre-existing).

Not run here: the GPT step 0 (a live codex exec; outside this card's scope).
