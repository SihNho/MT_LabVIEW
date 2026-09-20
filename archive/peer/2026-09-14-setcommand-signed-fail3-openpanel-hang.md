---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, main-vi]
---

# setcommand-signed-fail3-openpanel-hang

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (23s)
- **why asked:** OpenFrontPanel blocked 180 s in build_setcommand_signed.log run 3 after a loaded TEST copy was overwritten on disk
- **verdict:** unverified

## Question

FAILED PREDICTION / hang check (brief). tools/bench/build_setcommand_signed.log run 3 (tools/recipes/build_setcommand_signed.py): the very first step, OpenFrontPanel on a fresh file copy of the driver (SetCommand_signed.vi), did not return within 180 s (no modal dialog; bgrun killed the client). Run 2, 2 minutes earlier, had saved that same file, closed its panel, then built a TEST copy that failed (ExecState 0) and RETURNED WITHOUT closing the TEST copy's panel; run 3 deleted both files from disk while the TEST copy was still loaded in LabVIEW, copied the original over SetCommand_signed.vi and called OpenFrontPanel on it. MY EXPLANATION: overwriting/deleting a VI that is still loaded in the running LabVIEW (our documented 'never load a VI you are about to overwrite' rule: earlier it produced Traverse error 1012, here a blocked OpenFrontPanel), possibly plus a reserved op after the abandoned client. PLAN: (1) ping LabVIEW; restart it (standing permission) if a VI Server call still blocks; (2) recipe: close every panel on every exit path (try/finally), and give the TEST copies unique per-run names; (3) rerun. ATTACK: (a) plausible? any other cause of a silent 180-s OpenFrontPanel block (e.g. a hidden 'file changed on disk / reload?' prompt that our dialog scan does not see)? (b) is a LabVIEW restart the right recovery, and should the deliverable SetCommand_signed.vi saved by run 2 be trusted (it was saved via VI.Save with ExecState 1 before the mess) or rebuilt?

## Answer

Your explanation is highly plausible and is the leading hypothesis.

- NI explicitly documents that changing a VI on disk while LabVIEW retains another version in memory can trigger a ?쐁hanged on disk??dialog when its front panel loads, warning that memory and disk components may be inconsistent. That maps closely to the block occurring specifically at `OpenFrontPanel`. A hidden or off-screen instance of this dialog is therefore a credible alternative?봭ot a separate root cause?봢ven if your current modal scan missed it. [NI: VI Has Changed on Disk](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE&l=en-US)
- `ExecState 1` does not prove that no stale reservation/reference remains; NI says ?쏳unning??can mean reserved by an active hierarchy, while ?쏧dle??merely means loaded but not running. [NI: execution states](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YIEJCA4)

Recommended disposition:

1. Ping with a harmless VI Server call. If that also blocks, restart LabVIEW. Given the abandoned ActiveX call plus an unresolved loaded/disk identity conflict, restart is the correct deterministic recovery.
2. Even if ping succeeds, I would still restart before rebuilding: closing one visible panel does not establish that every reference or in-memory dependency was unloaded.
3. Add `finally` cleanup for every opened VI/reference and unique TEST filenames. Also keep TEST files until after LabVIEW has released them; uniqueness alone prevents collisions but not stale loaded objects.
4. Rebuild `SetCommand_signed.vi` after restart. Run 2?셲 `VI.Save` probably produced valid bytes because it completed before the later incident, but the evidence does not establish that it saved the intended in-memory identity rather than a stale/conflicted one. Treat it as a diagnostic artifact, not the deliverable. Preserve it for hash/reporter comparison against the clean rebuild.

Cheap confirmation: before restarting, inspect all LabVIEW-owned windows?봭ot only modal-class windows?봣or text matching ?쐁hanged on disk,???쏳evert,??or ?쏞ancel.??NI confirms that this condition presents a Revert/Cancel decision during front-panel loading. [NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kEssSAE&l=en-US)

## Sources

(extract from answer)

## What was done with it

The dialog was found on screen (dialog_1939_crop.png: 'changed on disk - Revert/Cancel') exactly as the reviewer suspected; restart + finally-cleanup adopted. Verdict: correct.
