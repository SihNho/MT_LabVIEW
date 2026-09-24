## What was done with it
(for archive/peer/2026-09-25-76-5-t1-replay-gbtest.md - card 76-5's write flags do not cover archive/peer/)

Material session 76-5, 2026-09-25 05:1x. Accepted as framing: E1 (defaults not persisted) is not proven by 0,0,0 alone;
E3 (body fault, e.g. StrToPath.vi / Q&R index) and E4 (reentrant stand-in, no carry-over) stay open. Applied s4 in part:
tools/bench/diag_replay_defaults.py (read-only cold load, nothing run) reads the three hidden controls' saved values plus
the VI's reentrancy / automatic-error-handling properties where the ActiveX interface exposes them. The counter chain's
numeric type was NOT read (no reader for a tunnel's type in this fleet). Result: see tools/bench/replay_vis_76d_defaults.log;
the next step is the judgement session's (failure budget 2 of diag_replay_gbtest.py is spent).
