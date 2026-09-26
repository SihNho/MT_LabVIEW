ATTACK this claim about the failed prediction in tools/bench/diag_c101b_syntax.log (script tools/bench/diag_c101b_syntax.py).

Failed gate: `S2 <= 120 lines (121)` - the read-only parse check of the edited stage recipe tools/recipes/stage_d1_disp.py
(card 101-4; the project rule is "every stage script is a <=120-line file on stagekit", CLAUDE.md "Stages are SIMULATED" /
"stage script <=120 lines on stagekit" in the card). S1 (ast.parse) and S3 (no undefined name) passed.

CLAIM: the defect is in the RECIPE, not in the checker: the card-101-4 edit added a 5-line docstring paragraph and a
13-line cdiff() helper, and the file reached 121 lines. The repair is a docstring-only trim (the paragraph re-wrapped to 4
lines) - no statement changed - after which the file is 120 lines. The checker counts `len(src.splitlines())`, which is
the same count an editor shows for a file that ends with one newline.

Already ruled out: (1) a CRLF/encoding artefact - the file is read with encoding utf-8 and splitlines() treats \r\n as one
break; (2) the checker counting a trailing blank line - splitlines() does not yield an empty last element for a trailing
newline.

Name the strongest reason this claim is wrong, the cheapest discriminating test, and whether anything else in the failing
log (tools/bench/diag_c101b_syntax.log) indicates a problem the claim does not cover (e.g. "pyflakes not installed" means
S3 checked nothing).
