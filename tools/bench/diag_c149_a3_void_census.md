---
type: facts
status: current
date: 2026-10-08
card: 149-a3-2
---
# Void-type census of wire terminals (PD363(c)) - card 149-a3-2, plain gscript reads (read_terms + report_all + read_term_type), no edit verb

## s06: D1_ring_p4s06_20261008_174730.vi (md5 569ffbf5) - json tools/bench/diag_c149_a3_void_s06.json md5 a8bbd19397ee76653652ab3cd563ba33
- coverage: 1112 of 4379 wired terminals read in 600.2 s (0.54 s/read, cap 600.0 s), order wire uid DESC; complete False; last wire read w26932
- wires covered: w86637 .. w26932 (511 distinct)
- Void terminals (any TD name containing 'void'): 0; read errors: 0
- NOTE gscript.TD_NAMES (tools/gscript.py:4585-4588) has no 0x00 entry, so a Void TD is named '0x00', never 'void': terminals with any TD code 0x00: 0; with no TD at all: 0
- top-level TD name distribution of the terminals read: {'I32': 254, 'Array': 195, 'DBL': 183, 'Refnum': 154, 'Cluster': 153, 'Boolean': 48, 'Typedef': 48, 'U32': 38, 'U16': 18, 'String': 9, 'SGL': 4, 'I8': 1}

## s05 (byte copy of D1_ring_p4s05_20261008_002621.vi 3f9ac26b): NOT RUN - the card returned at the s06 run's COV gate FAIL (first unexpected result, card chat-P2); s06-only list therefore not computable.

