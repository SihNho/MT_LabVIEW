ATTACK this claim about a failed prediction in tools/bench/vigraph_check.log (script tools/bench/diag_vigraph_check.py).

Context (card 74-2 result, tools/bench/cards/result_74-2.json): tools/vigraph.py was patched so a Diagram-owned `Terminal`
SOURCE row (e.g. loop `i` #644, owner Diagram #639) becomes its own graph node (term_uid, class DiagramTerminal) instead of
being keyed on its owner node 639 (a SCHEDULING owner that effective_sources walked through to {}). See tools/vigraph.py:237-241,298,310.
After the patch, gate G8 (vigraph_check.log:707) failed: diff(S1, Row-D bed) minus flat-sequence edges was predicted 15/42/9
(removed/added/changed_sinks, the step-4 baseline) and measured 15/39/9 - three fewer ADDED edges. All other gates pass:
G1a diff(S1,S1) empty, G4 cdiff(S1,bed) 0 rows, G12a/b/c (every wired diagram-owned Terminal source is now an edge source;
#376 'frame index' effective source == #644; a synthetic drop gives exactly 1 cdiff row).

CLAIM (a): the old keying put diagram-owned source and sink Terminal rows into one ordinal group per owner node, so 3 of the
42 "added" edges were ordinal-shift artefacts of that grouping; the new keying removes them, 15/39/9 is the correct count,
and DIFF_BEFORE in diag_vigraph_check.py should be re-baselined to 15/39/9.
COMPETING (b): three real added edges now collide with S1 keys under the new keying (the patch hides real differences).

Say which is more likely from the code (tools/vigraph.py diff / key functions, tools/bench/diag_vigraph_check.py G8), what
would falsify (a), and the cheapest discriminating test (e.g. list the 3 edges present in the old-key added set and absent
in the new one, by term uid - tools/bench/cdiff_blindspot_74.py was written for this and never ran).
