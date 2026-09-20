ATTACK THIS PLAN. It is a master plan for restructuring a LabVIEW magnetic-tweezers tracking VI into seven
parallel loops, covering everything the team believes it can do BEFORE the physical rig is reassembled. The plan is
`docs/pre-rig-master-plan.md` in this project directory; read it, and read the files it cites.

Your job is to find where it is WRONG, not to summarise it. Specifically:

1. **The central claim to attack: the dependency split.** The plan asserts three separate physical dependencies —
   "needs beads in a mounted flow channel" (blocked), "needs motors/serial" (available now, window closes at
   reassembly), "needs the camera" (available now, no beads required). It uses this to move live camera
   acquisition acceptance (track C3) out of the deferred pile. **Is that split real?** Name anything in C1-C6 or
   E1-E5 that silently needs a mounted sample, a flow cell, fluid, a magnetic field, or a bead — and anything in
   track F that does NOT need one and is therefore deferred for no reason.

2. **Track A6 is new and load-bearing.** The user states that ASI focus correction is issued by SOFTWARE when the
   image goes off focus, and that they have never adjusted it by hand during an experiment. Our own file
   `docs/camera-acquisition-facts.md` had inferred the opposite from the fact that the subVI's `+Inc`/`-Inc`/
   `Focus inc` inputs are control references. The plan now says "find every writer of those control references and
   the off-focus criterion". **Is that search well posed?** What would it miss — a path that writes focus without
   touching those terminals, an autofocus living in another VI or in the ASI controller's own firmware, a
   hardware joystick path? How would you tell "no writer exists in this VI" from "we did not look in the right
   place"?

3. **Ordering.** The plan claims track C outranks track D because C's window closes. Attack that: what does
   starting hardware measurement before the map (track A) is finished cost, and is there a cheaper ordering?

4. **Acceptance.** E1 demands all 10,043 fixture frames bit-identical, where today only the first 10,018 (those
   before the first bead loss) pass. Is bit-identity through a reseed path even the right criterion, given the
   reseed is a re-initialisation rather than a continuation?

5. **What is missing entirely.** Name work that must happen before reassembly and appears in no track.

Context you must respect as given, not re-litigate: the original VI is never modified (work happens in a copy);
the per-bead maths must not change (scheduling may); the camera free-runs and nothing may gate its acquisition;
the ASI piezo stage must never be driven; and the buffer number, not a software timestamp, is the time axis.

State your strongest reason the dependency split in (1) is wrong, give an alternative explanation for why this work
was previously deferred, say what observation would falsify your objection, and name the cheapest test that
discriminates.
