---
card: 152-b1-1
status: current
date: 2026-10-09
---
# Brief 152-b1-1 - MEASURE the name a new FS border tunnel takes from a LoopTunnel source (docs/d1/ring-p4d.md PD369(d)); the ONE LabVIEW card of this step

Why: card 152-a2-2 stopped at v18 op 187 `p4_x_slot_fs` (LoopTunnel #30179 outer face 'min slot' -> IndexArray #29879.index inside FS #29721, 0 border tunnels today).
`stagesim.py:1892` refuses it because no one has recorded the name the faces of a NEW FS border tunnel take from a LoopTunnel source (`diag_c152_a2_2_facts.md` section 3).
This card only MEASURES. It edits no stage tool, no hook, no original, and builds no deliverable.

## Read first (and nothing else)
`docs/d1/ring-p4d.md` PD369(c)(d); `tools/bench/diag_c152_a2_2_facts.md` (the refusal, the rows of FS #29721); `tools/bench/diag_c127_1_fsinner.py` (stagekit skeleton that already builds a scratch FS inside a structure,
does the FIRST crossing with `connect_term_uid`, then reads every tunnel's faces with `allterms.read_terms`, strict echo, `wire_remove_loose_ends`, `kill_labview_at_exit`) and `tools/bench/diag_c126_6_cross.py` (same, FS built from the donor);
`tools/bench/fs_tunnel_naming_table.json` (the 18 existing crossings and their columns); `tools/stagesim.py:1875-1895` (the rule being extended; READ ONLY).

## Steps
1. **Invariants before:** md5 of stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, stagesim c24bd39a, fs_tunnel_naming_table 0c0ba43a,
   memory_model a28b6dd7, s08 VI f99e8414, graph 44858dbf (copy `diag_c151_a1_1_inv.py` -> `diag_c152_b1_1_inv.py`, names only). LabVIEW process count and handle count (`tools/lv_gui.ps1 -Action` handle reader or `handle_audit` as the existing diags do) before.
2. **Offline graph read (pass item 0):** from graph `tools/bench/graph_ring_p4s08_20261009_033522.json` (44858dbf, read only) read and quote with file:line of YOUR output log: (a) the owner structure class of LoopTunnel #30179
   (WhileLoop / ForLoop / other) and its uid; (b) its outer face (t30192 'min slot', wire w30166): what KIND of inner source feeds the loop-side face (SubVI / Function / Local / Property / BuildArray / shift register / other,
   with the source node's class and uid); (c) the single other sink already on w30166; (d) that #29879 / #30002 / #30016 sit in frame #29869 of FS #29721 on diagram #23166, 0 border tunnels. These (a)(b)(c) decide the scratch case in step 3.
3. **Scratch crossing** `tools/bench/diag_c152_b1_1_cross.py`, <= 120 lines on `tools/stagekit.py` (header `# labview: build`, `# hardware: none`), ONE run, mirrors op 187 exactly as PD369(d) lists:
   a NEW minimal scratch VI (created in the run under claudeDev with a unique scratch name, NEVER saved as a deliverable, DELETED at the end) containing: a loop of the class found in (a) with an output LoopTunnel whose inner source is of the kind found in (b);
   the loop-side/outer face already wired to ONE other sink (as in (c)); a 1-frame Flat Sequence with 0 border tunnels, on the same diagram as the outer face, holding an IndexArray; the crossing = `connect_term_uid(IndexArray.index, outer face)`.
   Before the crossing read every face name (term_name, owner class/uid, is_source, frame_diagram, wire_uid via `allterms.read_terms`) of the source LoopTunnel and of the other tunnels on that net; after it read the same plus every face of the created FS border tunnel;
   strict uid echo on every read; `wire_remove_loose_ends` on the new wire(s) exactly as 127-1 does and re-read. Quote the log lines.
   **Prediction (write it in the script header; a different result is REPORTED, not fixed, no retry inside this card):** the created FS tunnel's faces take ONE of (i) the LoopTunnel source's terminal name 'min slot'-style as for a SubVI/Local source, (ii) '' as for a Function source,
   (iii) differing names on outer vs inner face; and the source net's existing tunnels keep their names. State which you predict from `fs_tunnel_naming_table.json` rows with the nearest source class.
4. **After the run:** scratch VI deleted (listdir of claudeDev for the scratch name: none), LabVIEW handle count after (flat +-100 vs before), `tasklist` LabVIEW count 0 (closed AND verified gone), md5 of every pin in step 1 unchanged.
5. **Do not** edit the table, stagesim or any selftest in this card (that is card 152-b1-2). No `tools/hooks` edit. A gate that refuses your OWN command text is a false positive: `py tools/gate_fp.py log` and go on, or name it in OPEN; never an env bypass.
   Run under `py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c152_b1_1_cross.log -- py -u tools/bench/diag_c152_b1_1_cross.py` (dry first if the skeleton supports it).

## Report `tools/bench/diag_c152_b1_1_facts.md` (<= 40 lines)
Graph read (a)-(d) with log lines; the scratch case as built (loop class, source kind, sink, FS shape); every face name before/after as a table; census delta; `Is Broken?`; BGRUN END rc; handles before/after; scratch deleted; pins unchanged; LabVIEW gone. `OPEN:` line. Facts only; a result-dependent action is not yours (RETURN with the facts).
