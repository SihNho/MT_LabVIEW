---
card: 154-a2-2
status: current
date: 2026-10-09
---
# 154-a2-2 facts - DonorQueue_v0.vi READ BACK (no rebuild, no save); donor_queue_v0.json written; cold re-read matches

Run: `tools/bench/diag_c154_a2_2_readback.py` -> `tools/bench/diag_c154_a2_2_readback.log` (BGRUN END rc=0 after 119 s; 12 pass / 0 fail).
- 154-a2-1 bug cause: `g.node_labels(..., strict=False)` returns a TUPLE (rows, err) (gscript.py:857-858); rows themselves are dicts {uid, label}.
- Row shapes (log "SH" lines): read_terms rows {frame_diagram, is_source, owner_class, owner_uid, term_name, term_uid, wire_uid} (29 rows);
  node_terms_uid -> (uid, rows {i, name, is_source, wire, node_uid, *_err}); Diagram[0].Nodes[] order [108, 44, 45, 46]; constants {52 ArrayConstant, 73 DigitalNumericConstant}.
- Objects (role uid class label, terminals):
  dbl_const #52 ArrayConstant (element #73 DigitalNumericConstant), not in Nodes[]: t51 'x,y,z array' src -> w82.
  obtain #108 Function 'Obtain Queue', 8 terms: 'element data type' t117 <- w82, 'queue out' t129 -> w109.
  enqueue #44 Function 'Enqueue Element', 7 terms: 'queue' t86 <- w109, 'element' t89 <- w82.
  dequeue #45 Function 'Dequeue Element', 7 terms: 'queue' t138 <- w109, 'element' t150 src unwired.
  release #46 Function 'Release Queue', 6 terms: 'queue' t161 <- w109.
- json: tools/bench/donor_queue_v0.json md5 15269b6cea348c20567204cbbd604478 (file, md5, objects[role, uid, class, label, terminals[index, name, is_source, term_uid, wire_uid]]).
- Donor md5 before/after: 81dba822efec5226123b3b88ee4383bc / same (no SaveInstrument, no panel open).
- Handles before/after: 34183 / 34182 (ops preloaded + warm read before).
- Cold re-read in a restarted LabVIEW: 5 uids + classes == json, element #73 same class.
- Invariants: 28 pins unchanged (s09 eb1d0f31, 7 tools, memory_model, 4 OpQueue*_v0, every Donor*.vi incl. DonorQueue). LabVIEW processes 0 at end.

OPEN: none.
