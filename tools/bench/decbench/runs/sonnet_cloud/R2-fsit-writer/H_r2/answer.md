The claim is wrong. The log it cites never measured the fact the claim depends on, and a later run showed that an existing writer does reach an FSIT terminal sink.

**1. Strongest reason it's wrong: the log has no failing "W1" gate, and it never touched LabVIEW.**
- `tools/bench/c78_rowd_writer.log` describes itself as "FILES ONLY, no LabVIEW, nothing mutated" (`:3`). It ends with "5 pass / 0 fail" (`:39`) and `rc=0` (`:41`). There is no W1 gate in it.
- The "measurement" is a search of label-map JSON files for writers whose sink is "addressed by a UID rather than by (diagram, Nodes[], Terminals[]) indices: 0" (`:33`). The log itself calls this "a FACT, not a gate failure".
- That records how existing writers' label maps describe their sink inputs. It does not test whether any writer can reach an FSIT terminal.

**2. Alternative explanation: the writer already worked, and the real blocker is cleaning up the net afterwards.**
- In `tools/bench/c80_rowd_routeA_r2.log`, an existing writer was called with its roles swapped: the wire uid plus terminal index pointed at the FSIT terminal as the sink (`:237`).
- Right after the connect, sink terminal #7488 on FSIT #7468 "carries wire 7506, state 'WIRED'" (`:240`). Net 7506 then had 3 source terminals: the new register #23868, FSIT #7468 and the old register #4334 (`:258`).
- The log's own discriminator passed: "THE SWAPPED CALL CONNECTED" (`:260`). The verdict there was that Row D "reduces to REMOVING THE OLD SOURCE #4334" (`:259`).
- So the failures recorded there are multi-source and broken-wire faults (`Is Broken? True`, `:237`). They are not cases of a writer being unable to reach the sink.
- The same log reports 0 machine refusals (`:...H8b`, near the end). Its 5 failing gates are all "the sink terminal carries a wire after the write" plus the route verdicts. That is consistent with a wire being made, then deleted or left with several sources.

**3. Observation that falsifies the claim.**
- That observation already exists: c80 r2 shows an existing op reaching the FSIT sink (`:240`, `:260`).
- There is earlier evidence on a different FSIT, though on the source side rather than the sink. The prior-art review found that `docs/toolkit-capabilities.md:70` records `OpConnectFromWire_v0` accepting a source terminal owned by FSIT #5818 and creating a wire (`priorart_c82_fsitconnect.log:39`).

**4. The proposed next step is out of date.**
- "Build a new op" has already been done. `OpFsInnerTunnelConnect_v0.vi` is on disk (`build_opfsinnertunnelconnect_v0.log:362`), although that build run ended `rc=1` (`:368`).
- Its prior-art review found the shape had been designed back on 2026-09-17 (`priorart_c82_fsitconnect.log:18`).
- STATUS's current first action is to run `stage_d1_m3a3_rowD.py`, not to build an op (`STATUS.md:54`).

**Cheapest discriminating test:** on a dated scratch copy of the row-C bed (md5 `33ef524e…`), make one swapped-role `OpConnectFromWire_v0` call. Then delete only wire/source #4334 and read net 7506.
- If it ends with exactly one source (#23868) and `Is Broken? False`, the claim is false: the existing writer is enough.
- If the connect itself is refused, or the terminal never reads WIRED, the claim survives. c80 r2 already observed the opposite.

What would change my mind: a re-run showing #7488 never carrying wire 7506 after the swapped call. That would mean the r2 readings were echoes, which is the "==1 ⇒ arm VOID" case defined at `:259`.

DEFECT: blocker - the claim rests on a file-only label-map search with zero failing gates as if it measured whether the writer works, and ignores the c80 r2 run where an existing writer did connect to FSIT sink #7488.