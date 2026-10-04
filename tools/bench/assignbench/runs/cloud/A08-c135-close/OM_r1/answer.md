ACTION: ISSUE
CARD: PD297 follow-up, offline doc work only: update docs/d1/INDEX.md so the current bed is D1_ring_p3b2b_20261002_130007.vi (md5 39511877) and the broken-file count reads 4 of 6. Update the bed sentence at STATUS.md:93 to match. Use tasklist to confirm LabVIEW is gone. Report facts only.
REASON: Three of the four pass items are met. Step 0 is done (135-1). Launch a passed: CEN2 matched the census and the peak was 645.7 (135-1). Launch b passed: peak 620.6, 51 items, only loose ends went from 22 to 20, and the expected file is eac21f43 with reverdict OK (135-4, 135-5).
The fourth item is only partly done. 135-5 moved the STATUS current-bed key and deleted 6cc69221 and the a-file. It did not update INDEX, it did not record the broken-file count as 4 of 6, and STATUS.md:93 still names P3b-1 (135-5 open).
LabVIEW being gone has so far been checked only by the runner gates B2 and E4. Both direct tasklist checks were refused (135-3, 135-4).
This is a small offline card, about 21 minutes of the remaining budget of about 99. Close the cycle after it.
HANDBACK-QUESTION: -