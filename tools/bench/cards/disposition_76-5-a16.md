## What was done with it
(for archive/peer/2026-09-25-76-5-a16-replay-standins.md - card 76-5's write flags do not cover archive/peer/, so the
material session left the text here for the judgement session to paste)

Material session 76-5, 2026-09-25 04:4x. ACCEPTED in full. (1) Selector fault: `tools/bench/diag_replay_standins.py`
now names every pass-through by exact label (Session/error/Buffer Number In -> Out) and the Image pair by exact label
(the order-dependent `startswith` at the Image line removed); new fatal gate A15 asserts `pidx("Buffer Number In") !=
pidx("Buffer Number Mode (Next)")`. (2) Gate-prediction fault recorded as its own fault: run 1's A16 excluded only labels
starting with "Mode", so it could not pass on a correct build; A16 now excludes Mode, requires Mode bare and BN Out on BN
In's wire, and is FATAL. (3) Run-1 buf artefact (md5 0d5377256895b548dc6fe41e1bb2cdf0, BN Out <- Mode) is INVALID; the
rerun overwrites it and fatal gate B1b refuses to continue if that md5 survives. B1/C1-C3 are acknowledged blind to who
drives BN Out; only A16 and the run tests in diag_replay_gbtest.py (image number == b) check it.
