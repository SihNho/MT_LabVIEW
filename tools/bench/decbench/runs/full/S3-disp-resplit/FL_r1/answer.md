**No, NEXT should change.** The 214(b)–(d) offline fixes are worth keeping, but a single all-or-nothing 47-op run is the wrong shape for the build.

**Why**

- **The stage has ended without a file in two consecutive cycles.** Cycle 100 stopped at op 2 with "NO FILE" (STATUS.md:77), after run 1 stopped at E1 parity and run 2 at op 2 binding (STATUS.md:80-81). Cycle 101's run r5 stopped in op 26 of 47, again "NO FILE" (STATUS.md:64).
- **The standing rule makes a decomposition plan mandatory here.** A stage that ends without a saved artefact, or fails twice, means the next cycle's first act is a decomposition plan, and a full-length retry is forbidden (CLAUDE.md, "Big or blocked work is SPLIT", item 3). Item 1 says a step is not done until it has left a file, and item 2 sets one saved artefact per natural stage, with re-wiring in batches of 10–15 rows.
- **NEXT prescribes exactly the forbidden shape.** It asks for "ONE record-mode run" of the whole recipe to a single `D1_s1_disp_<ts>.vi` (STATUS.md:60; plan :1801). Record mode saves only when every step matches (plan :1787), so any new defect in ops 26–47, which have never run, again leaves nothing.
- **Every failure so far was a tool or simulator defect, not a design defect.** The causes were the loop-body model (plan :1754-1756), the local-read index bug (plan :1789) and the refuted only-source rule (plan :1792; STATUS.md:66). Both escalation steps are spent and D-2026-09-27-01 is open (STATUS.md:65; decisions_pending.json:161-174).
- **"Each run gets further" is not evidence the rest is clean.** That recommendation (decisions_pending.json:170) rests on 0 → 3 → 25 steps, and the only-source rule is still unmeasured across four confounded samples (plan :1790-1793).
- **Saving a partial build is already permitted.** A broken-by-design intermediate under claudeDev may be saved by GUI Ctrl+S (CLAUDE.md, same section, item 6).

**What to keep**

- The 214(b) offline measurement, the 214(c) WARN rule, the tunnel-flip seed fix and the `plan_disp.json` md5 settlement (plan :1790-1800) are cheap, offline and needed either way.
- The 21 open rows accepted under rule 1a (plan :1725-1726) and the final pass criteria (STATUS.md:68-73) stay as the gate for the last sub-step only.
- Proceed under the assumption "continue" for D-2026-09-27-01 and flag it in the closing report (CLAUDE.md 2c).

**What the next cycle should do instead**

1. Write a one-page decomposition of the 47 ops into three or four sub-steps, for example creates (ops 1–25, already proven by r5), moves, re-wiring, then census and final save. Each gets its own saved file name, md5 and pass criterion, reviewed once for prior art.
2. Do the 214(b)–(d) offline work.
3. Run sub-step 1 only, save it as an intermediate, and start the next sub-step from that file in a fresh LabVIEW instance.

VERDICT: change NEXT
NEXT ACT: Write and review a decomposition plan that splits the 47-op display-loop stage into three or four sub-steps each saving its own claudeDev intermediate, do the 214(b)–(d) offline fixes, then run and save only the first sub-step (ops 1–25).