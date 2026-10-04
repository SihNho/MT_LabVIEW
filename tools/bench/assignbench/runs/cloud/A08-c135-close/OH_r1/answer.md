ACTION: ISSUE
CARD: PD297 bookkeeping, offline. (1) In `docs/d1/INDEX.md`, record the P3b-2 final `D1_ring_p3b2b_20261002_130007.vi` (md5 39511877) as the bed and set the broken-file count to 4 of 6. (2) Rewrite the bed narrative at `STATUS.md:93`, which still names P3b-1, so it agrees with the current-bed key. (3) Check that LabVIEW is gone with `tasklist`, re-read the md5s of the bed and the kept files, and return facts only.
REASON: Pass items 1–3 are met. Step 0 held in 135-1. Session a passed every gate (CEN2 matched, peak 645.7 MB) and the compare is EQUAL after the 135-2 fix. Session b in 135-4 passed 11/0 and 13/0 with peak 620.6 MB, the final file was saved, and the Error List read 51 items with loose ends going 22 → 20. 135-5 wrote the expected file (reverdict OK) and deleted 49cf7f77 and 6cc69221. Pass item 4 is still incomplete:
- 135-5 could not write to INDEX, so the INDEX bed entry and the "4 of 6" count are not recorded.
- 135-5 reported that `STATUS.md:93` still names P3b-1.
- The LabVIEW-gone check by `tasklist` was permission-denied in 135-3 and 135-4. Only runner gate E4 covers it.

These are small offline edits that need no judgement. Time used is 81 of 180 minutes.
HANDBACK-QUESTION: -