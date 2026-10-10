---
card: 163-a3-1
status: current
date: 2026-10-10
---
# Brief 163-a3-1 (assignment 163-1) - K3/K4 GAP facts (PD396(f)), offline, FACTS ONLY. `labview: none`

Read `docs/d1/ring-p5b.md` lines 173-175 (PD391(h)) and 359-362 (PD396(f)), and `tools/bench/diag_c160_g1_1_facts.md:31-33` (the GAP finding). Step 3 (p5s02c, group I) is adopted; its graph is
`tools/bench/graph_ring_p5s02c_20261010_131658.json` (3d5196ab). The master plan of the remainder is the A41..A80 split recorded in `docs/d1/ring-p5b.md` (PD391(d)); the K3 / K4 groups and their actions
(A71..A80, K4 final action A79) are in the plan files named there (find them from that paragraph and the `plan_ring_p5s02*` / `plan_ring_p4*` files; do not rewrite or regenerate any plan).

Answer from files only (the graph json, plan json, census text, prerun/dry logs); NO LabVIEW, no plan written, no decision:
1. `w_k3pass` and `w_k4pass`: which diagram (frame; the census labels them -30 / -29) each END resolves to - quote the graph rows (uid, owner, frame, kind) and the plan action that names the wire.
2. The two borders each pass wire crosses (case / loop / sequence structures between source and sink) and WHICH tunnel or register the PD379(b) pass wire is meant to run between; quote PD379(b).
3. Which existing route (an existing tunnel / shift register / earlier action / adopted wire, with uid) could carry it, or "none exists".
4. Whether K4's census text "action 69" is a stale label for A79: quote the text, the action list around 69 and 79, and say what each is.
5. State which dry / prerun check reports the GAP (file:line) and the exact wording.

Report `tools/bench/diag_c163_a3_1_facts.md` (<= 40 lines): numbered answers 1-5 with file:line citations, `OPEN:` lines (measurements only). A helper script, if any, is `diag_c163_a3_1_*` (read-only; CALL shared functions).
No edit of any plan / recipe / pred / licence / graph / hooks; no originals touched; no decision about step 4 (the next judgement session decides).
