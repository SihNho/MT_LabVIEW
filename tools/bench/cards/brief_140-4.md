# Brief for card 140-4 (judgement cycle 140) — census of array-write nodes: intended vs real primitive (OFFLINE, measure only)

Trigger: review `archive/peer/2026-10-02-c140-3-el52.md` (verdict supported): donor `#29157` is an Insert Into Array
(`tools/bench/main_vi_node_labels.json:1120-1121`); created node #29489 read back 'Insert Into Array' (`diag_c140_3_scratch.log:219,225`);
P3b-2 bed nodes #29265 (`p3b_ras_rotpos`, `launch_p3b2_c135_b.log:94-103`) and #29316 (`p3b_ras_frameidx`, `:164-173`) came from the
same donor. The design is "local read → Replace Array Subset → local write" (PD246(c), `docs/d1/INDEX.md:87`).

1. CENSUS — every action in the P3a, P3b-1, P3b-2 (a and b) plans and in P4 v15 whose plan intent is an array element write
   (prim/label/route naming Replace Array Subset, Insert Into Array, Build Array, Index/Replace, `ras`), one row each: action id,
   plan's declared prim, donor (file + uid), the created uid in the bed (from the launch logs / real graph
   `tools/bench/graph_ring_p3b2b_20261002_133824.json`), the label and class READ BACK, the terminal names in the graph, and the
   verdict REAL == INTENDED yes/no. Cite file:line for every read-back.
2. DONORS — every node in the bed graph and in the claudeDev donor VIs whose read-back label is 'Replace Array Subset' (uid, file,
   terminal names); say which one is a measured, wired-in-the-original node (the Error List item at
   `errorlist_scratch_c140_3_*205859.json:316` names one).
3. TERMINAL MAP — measured terminal-name lists of Replace Array Subset vs Insert Into Array (1-D) from the graph/NAMES.md, with the
   one-to-one map a node swap would use; flag any terminal without a counterpart.
4. TOOLS — does gscript/stagexec/stagesim have a measured way to REPLACE a node in place (LabVIEW `Replace` method or similar) or only
   delete + create + reconnect? file:line; which routes a delete + create + 4 reconnects would use and whether each is measured.
5. ITEM 52 — look at `tools/bench/errorlist_shots/bd_210806_after11.png` (the review's discriminating test): is the selected node the new
   node in frame 32464, not #29265/#29316? Say what the image shows.
6. Facts `tools/bench/diag_c140_4_facts.md` (≤ 40 lines). Measure only: no plan edit, no tool edit, no LabVIEW. If a read-back needs
   LabVIEW, return with OPEN naming it.
