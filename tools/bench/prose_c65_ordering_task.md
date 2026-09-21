# Write ONE short paragraph for the user (Korean, 4–6 sentences). Facts only; do not add advice we did not give.

AUDIENCE: the user — a magnetic-tweezers experimentalist who owns the original LabVIEW VI. They read this in
STATUS.md. They decide; we do not.

WHAT IT IS ABOUT: we are refactoring their tracking VI without changing its computation. In the original, one wire
carried a value directly from a node to the input of a Case structure — LabVIEW's dataflow guaranteed the Case
structure could only run after that value arrived. To prepare the loop split, we replaced that single wire with
two halves: the node now writes a front-panel indicator, and a local variable reads that indicator and feeds the
Case structure. Both halves sit on the same block diagram with no data dependency between them.

THE CONSEQUENCE: LabVIEW does not guarantee any order between two things with no data dependency. So the Case
structure can legally read the value from the PREVIOUS loop iteration, or the control's default value on the first
iteration, where the original wire made that impossible.

WHY IT MATTERS PHYSICALLY: this Case structure drives the ASI focus axis.

WHAT WE HAVE AND HAVE NOT DONE:
- Two independent peer reviews raised this, on 2026-09-21, about two different rows.
- We built and saved the two files anyway, because they are intermediate artefacts that are never RUN — only
  structurally checked. Nothing has been executed.
- Every automatic check we have — ExecState, wire counts, which wires touch which terminals, the broken-wire
  reader — is blind to this. It will pass every gate we own.
- The next stage (M3) only MOVES nodes into the loop body; it does not add more of these substitutions, so work
  continues for now and the runner was not stopped.

THE DECISION WE NEED FROM THEM, stated as a question, not as options we prefer:
whether losing that ordering guarantee is acceptable in the FINAL VI — given that the seven-loop design they
approved already passes data between loops asynchronously — or whether this signal in particular must keep a
guaranteed order, in which case the transport for it has to be designed differently and the two S3b files get
rebuilt.

TONE: plain, direct, no hedging, no apology, no bullet points. Do not tell them what we recommend. Do not repeat
the file names or md5 hashes. End with the question.
