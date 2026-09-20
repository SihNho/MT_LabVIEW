# A failed prediction about LabVIEW `SaveInstrument` on an unedited copy of a large VI

Environment: LabVIEW 2026 (26.3.1f1) on Windows 10, driven over the exported ActiveX/COM
`LabVIEW.Application` interface from Python (pywin32). The VI under test is a 473 KB top-level
acquisition/tracking VI with 98 subVI calls, 170 diagrams, 626 nodes.

## PREDICTION (contract B in `tools/recipes/stage_d1_s1.py`)

A COM `SaveInstrument` save of an **UNEDITED byte copy** of the main VI, made in a LabVIEW instance
where the **ORIGINAL was preloaded read-only**, would leave the saved file reading `ExecState`
(cold 0, preloaded 1) — the same pair as a pristine byte copy — because a prior measurement
established that a cold read measures subVI **LINKAGE** and nothing in the VI was edited.

"cold" = the file is opened by `GetVIReference` in a freshly restarted LabVIEW with nothing else
loaded. "preloaded" = the ORIGINAL is first held resident read-only by `GetVIReference` in that
same instance, then the copy is opened and its `ExecState` read.

## OBSERVED (`tools/bench/stage_d1_s1.log`, four readings in four separate LabVIEW instances, pids 14028 / 21224 / 25544 / 21584)

- saved copy `D1_s1arm_savetest.vi`: cold **1** (`:36`), preloaded **1** (`:68`)
- pristine byte copy `D1_s1ctl_bytecopy.vi`: cold **0** (`:57`), preloaded **1** (`:79`)
- the save: `g.save()` → `SaveInstrument` returned 475,141 in 0.28 s, no exception (`:14-15`);
  bytes 473,317 → 475,141 (**+1,824**); md5 `2a78e17c…` → `e0112963…`; LabVIEW saved-version bytes
  `26 00 80 00` at offset 36 **UNCHANGED** (`:10`, `:17`); the ORIGINAL is byte-identical
  afterwards (`:85`).
- the copy lives in `…\LabVIEW 2026\user.lib\claudeDev\`, i.e. a **DIFFERENT directory** from the
  original it was copied from.
- Verbatim from the same log, the diagnostic the script took at the ONE cold `ExecState 0` reading
  (`:59-64`), which is the pristine-control leg:

```
    --- ExecState 0: MEASURE BEFORE CLOSING
    FACT SUBVI RESOLUTION: 7 calls over the first 8 of 170 diagrams; 4 with empty name/path or a path not on disk
        UNRESOLVED Diagram[3] uid 30804 name='MOV.vi'  path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb\MOV.vi'
        UNRESOLVED Diagram[4] uid 4620  name='GOH.vi'  path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\Limits.llb\GOH.vi'
        UNRESOLVED Diagram[5] uid 5403  name='VEL.vi'  path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb\VEL.vi'
        UNRESOLVED Diagram[5] uid 5497  name='POS?.vi' path='C:\Program Files\National Instruments\LabVIEW 2026\instr.lib\Mercury\GCS_LabVIEW\Low Level\General command.llb\POS?.vi'
```

(The same four names are also listed as resolved `subVI` entries in the same dump, i.e. the entries
exist but their stored paths do not point at files on disk. No equivalent dump exists for the other
three readings, because the script only takes it on an `ExecState 0`.)

## ALREADY RULED OUT — do not spend the answer on these

- It is **not a version upgrade**: the saved-version bytes are unchanged (`26 00 80 00`, offset 36).
- It is **not an edit**: no scripting call touched the diagram — the phase only copies, opens, reads
  and saves.
- It is **not instance contamination**: each of the four readings is its own child process and its
  own LabVIEW pid, verified distinct.

## THE QUESTIONS

1. What does LabVIEW actually rewrite when `SaveInstrument` is invoked on an **unedited** VI that
   was loaded with its subVI hierarchy resolvable, and does that plausibly explain a later **COLD**
   `ExecState` of 1?
2. Is there any mechanism by which the saved file could now **depend on, or have inherited state
   from, the in-memory ORIGINAL** — a cross-linking hazard that was asserted in this project's
   planning documents but never measured?
3. Could this save have changed the VI's **COMPUTATION** in any way (this project's rule 1a forbids
   that absolutely), and what is the **cheapest test that discriminates** "the save repaired a link
   table broken by the directory move" from "the save wrote something that can change behaviour"?
4. What would **falsify** the benign reading?

Answer each of the four explicitly. Name the cheapest discriminating test concretely enough that it
can be run over the same COM interface or offline on the bytes.
