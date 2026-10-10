---
name: rig-standardised-on-labview-2026
description: "The user decided on 2026-08-31 to run everything — harness work and experiments — on LabVIEW 2026, ending the 2026/2019 split; the originals are already in 2026 format and that is now correct"
metadata:
    pinned: false
type: decision
status: in-force
date: 2026-08-31
source: memory/two_labview_versions_2026_harness_2019_rig.md
---

# The rig is standardising on LabVIEW 2026

For a long time this machine ran a split: **harness and VI-scripting work in LabVIEW 2026, real
magnetic-tweezers experiments in LabVIEW 2019** (the user's own description on 2026-08-30,
*"그동안 LabVIEW 하네스 코딩할때는 LabVIEW 2026으로 하고, 실험은 LabVIEW2019로 했어"*). Both are
64-bit and both are installed side by side.

**On 2026-08-31 the user ended that split: *"앞으로는 그냥 2026 버전 이용할 예정."*** Everything now
targets LabVIEW 2026.

## Why this matters, and what it cancels

A VI saved by a newer LabVIEW can never be opened by an older one — the upgrade is one-way, undone
only by an explicit `File ▸ Save for Previous Version…`. While the split existed, this made any
save in 2026 a threat to the experiment rig: it silently removed the VI from the machine that
actually took data, and the failure surfaced days later.

**That hazard is now gone.** The experiment hierarchy had in fact already been upgraded to 2026
format — 34 files, most of them in one batch — and with the rig moving to 2026 that is simply the
correct state, not damage to repair. Do **not** plan a downgrade to 2019, and do not treat "opens
in 2019" as an acceptance criterion.

The project's separate rule against modifying original VIs still stands in full; it protects their
*content*, which was never the part this version story was about.

## Two techniques worth keeping

**Read a VI's saved version offline.** Every `.vi` carries it as a four-byte value: `19 00 80 00`
is LabVIEW 2019, `26 00 80 00` is LabVIEW 2026. Scanning the file for those patterns and taking
whichever dominates identifies the version with no LabVIEW instance running and no risk of touching
anything.

**Expect the save prompt when opening an old hierarchy in a newer LabVIEW.** When a stored subVI
path no longer matches, LabVIEW relinks by name and marks the caller dirty, so it asks to save on
exit — which is how a whole hierarchy gets rewritten in the newer format without anyone deciding to
save it. Now that the target is 2026 this is no longer dangerous, but it is still the reason a VI
you only looked at can come back modified.
