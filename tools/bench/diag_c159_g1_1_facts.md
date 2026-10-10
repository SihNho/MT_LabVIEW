# Card 159-g1-1 facts - is the cycle-158 retrospective still `retro-undisposed`? (PD389(f)), 2026-10-10 04:54
- Gate = `cycle_runner.retro_undisposed` (tools/cycle_runner.py:1031-1052) -> shared parser `dispo.disposition_len` (tools/dispo.py:59-64), heading via `dispo.heading_index` (tools/dispo.py:36-48). Called, not re-implemented: tools/bench/diag_c159_g1_1_check.py, log tools/bench/diag_c159_g1_1_check.log (BGRUN END rc=0, RESULT PASS 3/0).
- File archive/peer/2026-10-10-retrospective-cycle158.md (526 lines): disposition heading at line 517 (char 63312); section = lines 517-526 (to EOF).
- Parser verdict: REAL TEXT - disposition_len = 920 (threshold < 80 = placeholder). Text is the cycle-159 judgement disposition (device-failed ACCEPTED, FINDINGS 1-6).
- Nothing written: verdict was not placeholder, so the retrospective is unchanged (no disposition added, no re-run needed).
- Gate state now: `retro_undisposed('archive/peer')` = None -> cycle 158 is NO LONGER listed as due (it is also the newest `*retrospective*.md` by mtime).
- History: the runner logged `RETRO-UNDISPOSED ... cycle158.md | 2026-10-10 03:17:39 | cycle 159` (tools/bench/cycle_runner.log:1562) BEFORE the disposition was written at 03:2x; that entry in assign_159_3.json gates_due is stale.
- Side note: the hook copy guard_peer.undisposed (tools/hooks/guard_peer.py:849-851) splits at the FIRST substring match, which in this file is the inline quote at line 147; its tail is > 80 chars, so it also reads as disposed (same verdict, wrong section).
- No other archive/ or docs/ file modified; no tools/ or tools/hooks/ edit; retrospective.py not run; STATUS / next.json untouched.
