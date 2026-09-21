# API FACT QUESTION — LabVIEW ActiveX / VI Server: does a scripting read/edit leave `VI.ExecState` stale at 0, and can a recompile be forced over ActiveX?

This is a pure API-fact question about LabVIEW's own ActiveX / VI Server interface (LabVIEW 2026, Windows,
driven from Python via `win32com` `LabVIEW.Application`). Search NI's documentation, the LabVIEW VI Scripting
property/method reference, NI forums and any other external source. Answer with facts and citations (URLs),
not with an opinion about our project.

## The observation that motivates it

Driving LabVIEW over ActiveX, we call a scripting op VI that (a) reads the property `Wire.Is Broken?`
(property short-name id `6371004`) off a wire reference obtained from a terminal reference, and (b) invokes
`Terminal.Connect Wire` on a nested block diagram. After an IDEMPOTENT connect that creates no new wire at all
(wire count unchanged 1905 -> 1905, the op returning an empty error cluster and `Is Broken? = False`), the
owning VI's `VI.ExecState` flips from 1 (Good/runnable) to 0 (Bad/broken) and STAYS 0 for at least 14 seconds
across eight re-reads, across a released-and-reacquired VI reference, and across a dropped-and-recreated COM
Application proxy. A separate control showed that a scripting edit touching no wire at all also drives
`ExecState` 1 -> 0 on the same VI.

## The questions

1. Over LabVIEW's ActiveX / VI Server interface, is `VI.ExecState` known to report 0 / "Bad" after a VI
   Scripting operation (a property read such as `Wire.Is Broken?`, or an invoke such as
   `Terminal.Connect Wire`) purely because the VI has been MARKED as needing recompilation, rather than
   because it is genuinely broken? I.e. is `ExecState` documented (or widely reported) to be a CACHED /
   deferred value that only refreshes when LabVIEW recompiles or revalidates the VI?

2. If so, what makes it refresh? Specifically, is any of these reachable over ActiveX from an external client
   (not from inside a LabVIEW scripting VI):
   - a VI-class method that forces a compile or a recompile of one VI;
   - the `VI.Broken?` / `Is Broken` style property, and does it differ from `ExecState`;
   - `VI.Get Errors` / the error-list method (we have evidence this is ABSENT from the exported
     `VirtualInstrument` ActiveX interface — confirm or refute);
   - Mass Compile as a method/invoke node reachable over ActiveX;
   - a side effect of `VI.Save:Instrument` (saving the VI) that revalidates it;
   - opening/closing the front panel or block diagram window, `VI.FPWinOpen`, or a `Reinitialize`/`Revalidate`
     style call.
   For each, say whether it exists in the ActiveX type library, its exact name, and cite the source.

3. Is the documented meaning of `ExecState` values authoritative anywhere — what exactly do 0 and 1 mean, and
   is there an enumeration value that means "needs recompile" distinct from "broken"?

4. What is the CHEAPEST documented way, from an external ActiveX client, to obtain a TRUSTWORTHY answer to
   "is this VI actually broken?" after a scripting edit, without saving the VI and without running it?

## What I am NOT asking

Do not design our experiment, do not ask me to confirm anything, and do not comment on our project's process.
Facts plus citations only. "No documented mechanism exists" is a perfectly acceptable answer if that is what
the sources say — say so plainly and say what the sources DO establish.
