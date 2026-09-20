Write the "FOR THE USER" entries for a lab-automation project's status file. Plain English, no jargon the user
has not used, short sentences. The reader is the scientist who owns the instrument; they read this to decide
whether to overturn a call I made while they were away. Address them directly. Do not add headings, do not add a
preamble, do not explain what the project is. Output exactly TWO numbered items, in the format shown, nothing
else.

Output format — exactly this shape, keeping the numbers:

4a. <one short paragraph>
5. <one short paragraph>

=== FACTS FOR ITEM 4a — a repair I made against a standing order ===
- The user's standing order is "stop building 장치" (stop building process machinery/devices).
- A watchdog script is supposed to notice when LabVIEW has frozen. It has now fired SIX times and been wrong
  all six times — measured, not estimated. Latest false alarm: 2026-09-19 04:16, on a job that finished
  normally at 04:28.
- Every false alarm blocks the next build until a paid peer review clears it. Cost so far: $6.16.
- I approved a ONE-LINE change to that existing script: only write the blocking record when the watchdog
  actually finds a stuck dialog box. Its self-test now passes 8 of 8.
- I read the order as "stop building NEW machinery", not "leave a broken one breaking things".
- I scheduled it AFTER the main build launched, never before it, exactly as planned.
- This is the call to overturn if I read the order wrong.

=== FACTS FOR ITEM 5 — what cycle 40 found ===
- The main build (run 8) ran for 30 minutes. Every prediction written down beforehand turned out wrong.
- I first read that as good news, because the four rows the predictions named all improved.
- A paid review ($4.48) showed I was wrong to read it that way: overall the run went BACKWARDS — 54 wired rows
  became 53, and 9 failed rows became 12. I had judged the run by the handful of rows the predictions happened
  to name. That was my mistake and it is now written into the status file.
- The genuinely useful result: the test that had been failing one particular connection ("Z/dZ") for four runs
  in a row was itself wrong. It demanded that the number of wires come back unchanged after a temporary helper
  part is deleted — but the whole purpose of that step is to leave exactly one new wire behind. So the test was
  asking for the opposite of success.
- I did NOT take the reviewer's word for that. I confirmed it by reading our own code. The connection is in
  fact made: it checks out by identity, it is not broken, and it reads back as the same wire.
- Second result: the one measurement the run existed to produce could not be read at all. The command that
  lists every wire in the file hits the same LabVIEW memory error that crashes the run. The next run will read
  the individual connection points instead, which is cheaper and tells us more.
- The old explanation for that memory error — "too many open handles" — is dead. The runs were healthy at
  51,349 handles and crashed at 35,555. Fewer handles, not more.
- Also cleared out: four saved "crash copies" we had been keeping as evidence turn out to be byte-for-byte
  identical to the untouched original file. They contain nothing and never did.
- The cycle's own review came back with no violations: "this cycle was run well and was worth its cost."
- Nothing here blocks the next step. The one other call the user may want to overturn: to clear a blocked gate
  caused by a trivial typo in a test, I spent a cheap Gemini review instead of a $4.50 Opus one.
