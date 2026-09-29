**Most likely root cause:** the "−2 already loose in R1" term in the pin is wrong. It rests on an inferred list of which nets carried loose ends in R1, and nobody measured that list. This is my reading of the logs, not yet tested on the machine.

**Evidence**
- **The gap is real, not a misread.** LabVIEW's own header says 53 items (`diag_c116b_scratch_el.log:27`). The other classes match the pin exactly (nosource 1, notconn 20, other 10, `:114`), so the whole shortfall of 2 is in "Wire has loose ends".
- **The −11 for the stubs held.** All 11 stubs are gone and no wire was added (`diag_c116b_scratch.log:279,283`). Remove Bad Wires treated them as bad in R1 and found nothing new (`:319-320`). So 22 = 24 − 11 + 9: only 9 of the 13 shared nets gained a new item. If each net shows at most one item, 4 of the 13 nets were already loose in R1, not 2.
- **Where [25438, 25461] came from.** It comes from R1's expected file, which licenses 7 loose items on 7 nets. That file says "LOCATION IS INFERRED, not measured" (`errorlist_expected_D1_l2_r1_20260928_055441.json:75`). It also says the other 17 loose items are unlocated (`:7`).
- **The earlier review warned about this.** It called the location argument circular, because `Wire.Terms[]` cannot see a free segment (`archive/peer/2026-09-28-c115e-sel.md:53,92-94`). It left the "swap" alternative OPEN (`:106-107,157-159`) and said no count licence should be carried into L2-R2 (`:121,138`). `plan_l2r2_make` carried it in anyway (`plan_l2r2_make.log:44`).
- **No gate could catch it.** ENDS and TD compare terminal lists only (`diag_c116b_scratch.log:284-285`), and loose segments have no terminals.

**Most plausible alternative:** the already-loose set really is just {25438, 25461}. Instead, the scripted LoopTunnel delete left no dangling branch on 2 of the nets, for example by removing the segment together with the tunnel. In that case the "+1 per deleted tunnel" model is what's wrong.

**Cheapest discriminating test:** don't touch the tunnel deletes at all. It is the c115e-sel review's own test (`archive/peer/2026-09-28-c115e-sel.md:126-129`), pointed at a different set of nets.
1. Make a byte copy of R1 (md5 `f465196b`).
2. Call `Wire.Remove Loose Ends` on the 11 nets the pin assumed were clean (the 13 minus 25438 and 25461).
3. Read the Error List once.
- If the root cause is right, loose ends drop from 24 to 22.
- If the alternative is right, the count stays at 24.
- Splitting the 11 nets in halves on later copies then names the two nets.

ROOT CAUSE: The pin subtracted only the 2 nets on PD230's inferred (never measured) location list, but 4 of the 13 shared nets already had a loose end in R1, so only 9 new "loose ends" items appeared instead of 11 (24 − 11 + 9 = 22).
TEST: On a byte copy of R1, call Wire.Remove Loose Ends on the 11 shared nets assumed clean and read the Error List once: 22 confirms the pre-loose nets; 24 points to the tunnel delete leaving no dangling branch on 2 nets.