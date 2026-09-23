# Failed prediction P6b in tools/bench/stage_d1_m4a.log (cycle 68) - attack the explanation

Build M4a on a LabVIEW VI (scripted edits, never run): in While loop #23032 (body Diagram #23058) a new boolean shift
register (right #23469 / left #23796), copied Not #23459 and And #9996; wire w23847 (Local #23499 -> case selector tunnel
#10429 of CaseStructure #10407) deleted and replaced by Local -> And.x, Local -> SR-right, SR-left -> Not.x,
Not -> And.y, And -> #10407 selector. All other gates passed (31/1): ExecState 1 after the rows and after save, 4 new
wires Is Broken? False on an ordered idempotent second pass, Remove Bad Wires removes 0 on the saved file, nodes_added
== exactly the 4 new uids, nodes_removed [] (`stage_d1_m4a.log:292`).

P6b predicted: in diff(bed,new) (vigraph edges keyed "uid|class|TERMINAL NAME|ordinal") every removed edge touches
#23499/#10429/#10407 and every added edge touches a new node. Observed (`:293-295`): besides the expected edges, 13
removed / 12 added edges whose ENDPOINT UIDS ARE THE SAME but whose terminal NAMES changed: the two pre-existing shift
registers on the SAME loop (#23868/#23880 'Outgoing Handle' -> 'VISA out'; #23895/#23909 'Out position' ->
'position [internal units]') and flat-sequence tunnel #7468 ('Outgoing Handle' -> 'VISA out'). Also: the 'sr' pair edge
#23868->#23880 is in removed but has no renamed twin in added, and the NEW pair #23469->#23796 has no 'sr' edge in added.

Our explanation: adding a shift register to loop #23032 made LabVIEW re-derive the names of that loop's existing
register terminals (a register terminal's Name follows the label/name of what is wired to it), and the graph keys by
name, so a pure RENAME appears as remove+add; the missing 'sr' pair edges are a graph-pairing artefact of the reader
(build4's pairing), not a change in the VI. No wiring changed on those registers.

A uid-keyed re-diff (`tools/bench/q_m4a_diffuid.py`) is being run as the discriminating read.
