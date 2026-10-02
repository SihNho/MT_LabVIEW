Reading the evidence now. I've covered the c78 log, the c79 and c82 reviews, and `cycle27-plan.md`. I did not open `c80_rowd_routeA_r2.log` itself, so what it shows is second-hand.

**1. Strongest reason the claim is wrong: the log measures something narrower than the claim says.**
- `c78_rowd_writer.log` has no "W1" gate. Its gates are A1, A2 and B1–B3, and all five pass (`:39`).
- The number the claim leans on is a census of label maps. Four writers declare method 6349C03, and 0 of them take a sink by UID instead of by (diagram, `Nodes[]`, `Terminals[]`) index (`:33`).
- The log says outright that this zero is "a FACT, not a gate failure" (`:33`).
- "No existing op takes a UID sink" does not mean "no writer can address an FSIT sink".
- `Terminal.Connect Wire` is invoked on the sink and needs only a reference to it (`:20`, citing `docs/NAMES.md:245`).
- The FSIT reader on disk already returns that reference. `opfsinnertunnelterm_labels.json` has no `method` key (`:31–32`), and `OpFsInnerTunnelTerm_v0` returns `#7488` even after wire 7506 is deleted (`docs/cycle27-plan.md:3569–3572`).
- `UID to GObject Reference.vi` also resolves terminal uids, with `#7488` returning class `'Terminal'` (`docs/cycle27-plan.md:3512–3514`, Pre-decided 124).

**2. Alternative explanations of the same evidence.**
- (a) The missing capability is only a UID-sink convenience wrapper, not FSIT addressing.
- (b) The real blocker is the state of the sink after the old wire is deleted. STATUS later says the open question is whether `#7468` still yields a BARE LeftTerm and whether either connect polarity creates a wire between two bare terminals (`STATUS.md:26`).
- (c) An existing op may already work. `docs/toolkit-capabilities.md:70` records `OpConnectFromWire_v0` accepting an FSIT-owned source terminal (#5818), and the M3a-3 initial-value rows already landed with FSIT sources (`STATUS.md:9`).

**3. Falsifying observation.** One existing-op call that creates a wire whose sink is FSIT `#7468`'s LeftTerm, ending with `Wire.Is Broken?` False. The c79 review accepted this as "route A", which swaps the roles of `OpConnectFromWire_v0` and needs nothing built (`archive/peer/2026-09-22-c79-rowd-writer.md:240–244`, Pre-decided 116). That review also says "the W1 measurement itself is NOT disputed" (`:240`), so only its scope is in question.

**4. Cheapest discriminating test.** On a dated scratch copy of the bed, run `OpConnectFromWire_v0` with `wire_uid`=7506 and the `Wire.Terms[]` index of `#7488`, into the new loop's bare sink. This is about 2 minutes. Read the sink wire uid and `Wire.Is Broken?`. If it creates the wire, the claim and "build first" are both false. If it refuses, the claim's conclusion survives, but for a different reason than the log gives.

**Where the claim still holds.** The plan does choose to build an FSIT-head op: `OpFsInnerTunnelConnect_v0` (`docs/cycle27-plan.md:3548–3580`). It rests on a measured reading half and on routes A and B being unmeasurable or dead (`:3512–3520`, `:3548–3554`). The c82 review also found a real defect in that build: its UID echo sits on the wrong end (`archive/peer/2026-09-22-priorart-c82-fsitconnect.md`, A3).

DEFECT: major - the claim attributes to a nonexistent "W1" gate a capability finding that the log never made (its zero is an index-addressed label-map census), and so presents "build a new op" as forced when the log does not require it.