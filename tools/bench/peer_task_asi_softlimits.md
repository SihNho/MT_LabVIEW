API FACT question (web search required). ASI (Applied Scientific Instrumentation) stage controller, serial ASCII
protocol (MS-2000 / Tiger command set; replies ':A'), axes X Y Z; WHERE/MOVE units are tenths of microns. Today the
stage sits at X=-18475 Y=-27744 (units) and the safe window is +-1.0 mm around that in X/Y; Z is free.

Question: can SOFTWARE LIMITS be set INSIDE the ASI controller so that any MOVE/MOVREL beyond them is refused or
clamped regardless of which host sends it?
1. Exact commands and syntax: SETLOW (SL) / SETUP (SU)? e.g. `SL X=-2.85 Y=-3.77`, `SU X=-0.85 Y=-1.77` - what UNITS
   do SL/SU take (mm? tenths of microns?) and how are they queried (`SL X? Y?`)?
2. Behaviour on an out-of-limit MOVE: refused with an error code (:N-?) or clamped to the limit? Does MOVREL behave
   the same? Does the limit apply to HOME (!) and joystick motion?
3. Volatile vs persistent: are SL/SU values lost at power-cycle unless saved with SAVESET (SS Z)? What else does SS Z
   save? Is there a way to save only these? What restores factory values (SS X?)?
4. Are the limits tied to the current coordinate zero (i.e. would HERE / ZERO / H shift them)?
5. Any differences between MS-2000 and Tiger (TG-1000) firmware for these commands.
Cite ASI's command documentation pages (asiimaging.com/docs/commands/...). No project files needed.
