Claim under attack: a LabVIEW VI-Server `ExecState` reading taken on a copy of a large VI placed outside its
original folder measures SUBVI LINKAGE, not the legality of the edits made to that copy — so a build recipe that
reads `ExecState` without first loading the original into the same LabVIEW instance cannot distinguish "my edits
broke the VI" from "this copy's subVIs did not resolve".
Evidence: three BYTE-IDENTICAL files (md5 c39f36e0675339673b707c59f0784fee, 471,257 B) read ExecState 0 when
opened cold in a fresh LabVIEW 2026 instance, and ExecState 1 in the same instance when the original was opened
read-only first (tools/bench/diag_d0_execstate_preload.log, 9 gates pass, rc=0).
What we are about to do on the strength of it: a 9-minute build run (tools/recipes/build_d1_routeb_v0.py) ended
`ExecState 0` and was attributed to its own skipped build steps (its docstring at :131-135 predicted exactly that
in advance); that run never preloaded the original — the gate is g.exec_state(TARGET) at :1289, i.e.
GetVIReference(...).ExecState on a live instance (tools/gscript.py:1920-1921). We intend to declare that
attribution unsupported and re-run the build with the original preloaded before believing any ExecState result.
Already ruled out: (1) file damage — the three files are byte-identical and the original itself reads 1; (2) one
damaged copy — a copy made fresh during the same run behaves identically; (3) unresolved subVI paths visible to
our readers — 7 subVI calls returned well-formed names and paths, and 4 apparent "missing" ones were members
inside .llb containers.
Attack this. In particular: what else makes a cold-opened copy read 0 while a preloaded one reads 1; and what
would make the PRELOADED reading the wrong one — e.g. the preload masking a genuine break by supplying in-memory
subVIs that the saved VI would not resolve on its own. Name the cheapest test that separates "linkage" from "the
edits are legal".
