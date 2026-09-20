---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# walker-zero-junk-anomaly

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (71s)
- **why asked:** failed prediction: net_map (OpNetInfo_v1) dropped 78-130 junk Invokes per walk all morning and 0 on every walk after build_opnodeterms_v0 run 2 (which deleted the creator from a COPY); disk md5 unchanged.
- **verdict:** peer favours an in-memory aliasing of the loaded OpNetInfo instance (H2/H1), not a counting failure; decisive test = LabVIEW restart + one walk on a scratch (tools/bench/walk_junk_probe.py); disk files judged safe (donor md5 unchanged after save; the copy intentionally creator-free). OUTCOME (tools/bench/walk_junk_probe.log, 12:25): neither H1 nor H2 — **H5, found from the logs' one common factor**: the junk drop is an EDIT, and a target loaded by reference only declines edits silently (the 2026-08-28 rule). Same scratch, same process, same op: reference-only walk → 0 junk; after open_panel → 78 junk. So the "anomaly" was that the two zero-junk scripts never opened their targets. Consequence: the overnight sweep of the main VI (reference-only) did NOT pour junk into it; purge only matters on open_panel'ed build targets.

## Question

FAILED PREDICTION / anomaly review (be concrete, brief). tools/gscript.py net_map drives OpNetInfo_v1.vi, whose erdosmiller 'Create Invoke Node.vi' creator drops one untyped junk Invoke node on the TARGET per op run (docs/keystone-op-spec.md s33; measured all morning: 'net_map: 8 nodes walked; 78 junk purged', 13 nodes -> 130, in tools/bench/build_oppanelwiring_v0.log, build_opnodeterms_v0.log run 2 at 12:05-12:08 still 130/111/14). From tools/bench/test_opnodeterms.log (12:1x) onward EVERY walk reports 0 junk ('8 nodes walked in 2.0 s; 0 junk', '21 nodes walked in 167 s; 0 junk' on the main VI), while OpNetInfo_v1.vi on disk is md5-unchanged. What happened between 12:08 and 12:1x: tools/recipes/build_opnodeterms_v0.py run 2 = copy OpNetInfo_v1.vi -> OpNodeTerms_v0.vi, open_panel the copy, net_map it, delete_object(copy,'SubVI', <creator>) + Remove Bad Wires, build the loop, set_auto_error_handling(copy, False), save(copy); LabVIEW (pid 1728) NOT restarted since 10:52. HYPOTHESES: (H1) the delete hit the in-memory OpNetInfo_v1 instead of / as well as the copy (same-name subVI cross-linking? the copy shares every subVI with the donor, but the creator NODE is per-VI...); (H2) LabVIEW resolved the copy's Open VI Reference / op cache so that gscript.op(OpNetInfo_v1 path) now returns the modified copy's instance (both VIs have identical front panels/control names); (H3) the creator only drops junk when its 'Diagram in' ref is valid and something in the sequence left OpNetInfo_v1's creator input broken/error-fed; (H4) report_all-based junk counting broke (uids() now uses report_all - but earlier walks today counted fine with it). DISCRIMINATORS I can run: (a) LabVIEW restart (standing permission) then one walk on a scratch: junk returns -> in-memory state; (b) py count of SubVI objects in the in-memory OpNetInfo_v1 is NOT possible (pointing an op at a running op = error 6500), but a scratch COPY of the disk file walked once tells the disk state; (c) check whether gscript.op() caching by path could have been fed the copy (read tools/gscript.py op()). Which hypothesis do the facts favour, what is the cheapest decisive test, and is there any way this state could have CORRUPTED OpNetInfo_v1.vi or OpNodeTerms_v0.vi on disk (the copy was saved after the delete - intended)?

## Answer

The facts favour **H2?셲 underlying mechanism?봍abVIEW returned/retained an aliased loaded instance?봱ather than Python caching itself**. H1 is only plausible as a consequence of that aliasing.

Why:

- `gscript.op()` caches strictly by the exact path string; `OpNetInfo_v1.vi` and `OpNodeTerms_v0.vi` cannot collide in `_cache` ([gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:73)). Each logged build/test is also a separate Python process, so the Python cache cannot cross the 12:08 boundary.
- The transition occurs immediately after loading a byte-copy, deleting creator UID 243 from that copy, and saving it.
- `net_map` still traverses correctly?봧ncluding the 167-second main-VI walk?봟ut creates nothing. That strongly indicates the executing op became creator-free, not that `report_all` merely stopped counting.
- H3 is weak: every `net_map` call explicitly resets both error inputs and creator strings. A persistently broken creator feed should normally make the op broken or change traversal behaviour, neither observed.
- H4 is weakest: `report_all` successfully supplies the initial and final Invoke snapshots and other object censuses throughout the same tests. A selective failure returning plausible empty deltas is possible, but unsupported.

Cheapest decisive test: **restart LabVIEW, make one walk on a disposable scratch target, and observe the junk count.**

- Junk returns ??transient in-memory identity/reference aliasing; strongly supports H2/H1.
- Still zero ??the on-disk `OpNetInfo_v1.vi` is creator-free despite the recorded MD5 assumption, or the creator?셲 runtime behaviour changed for another persistent reason. Recompute the MD5 against a trusted earlier digest and test a uniquely named disk copy of the donor.
- No need to test the main VI.

Disk-corruption assessment:

- **`OpNetInfo_v1.vi`: very unlikely.** Its MD5 was checked unchanged after `save(OP)`, so neither deletion nor save changed its bytes.
- **`OpNodeTerms_v0.vi`: no corruption indicated.** It was intentionally saved creator-free, remained executable, and passed exact functional comparisons.
- The credible damage is limited to the **loaded in-memory OpNetInfo instance**. A future accidental save of that aliased instance could persist the creator deletion, but the recorded build did not: the donor MD5 proves that for this run.

One additional trap: the recipe calls `close_panel(OP)` before overwriting the copy, but that call itself obtains a VI reference; therefore an old loaded `OpNodeTerms_v0` instance may survive while its disk file is replaced. That makes loaded-instance aliasing/staleness more credible than cross-VI node deletion.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
