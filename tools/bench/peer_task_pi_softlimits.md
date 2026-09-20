API FACT question (web search required). Controller: Physik Instrumente C-863.11 Mercury (IDN reply
'(c)2013 Physik Instrumente(PI) Karlsruhe, C-863.11,0,1.3.0.7'), GCS 2.0 over serial, one axis '1'. Measured today:
TMN? = 0, TMX? = 52, so the controller's travel range is 0..52 mm, but the rig is only safe for 0..39 mm.

Question: can a SOFT LIMIT (upper and lower position limit) be set INSIDE the C-863.11 controller itself, so that
any MOV beyond it is refused/clamped by the controller regardless of which software sends it (LabVIEW, PIMikroMove,
our scripts)? Specifically:
1. Do the GCS commands NLM / PLM (or SPA parameters 0x15 "max position" / 0x30 "min position", or others) exist on
   the C-863.11 firmware 1.3.x, and what exact syntax sets the limits for axis 1 (e.g. `PLM 1 39.0`, `NLM 1 0.0`)?
2. Does setting them need the command level CCL 1 with the password (`CCL 1 advanced`)? Are they volatile (lost at
   power-cycle) unless written with WPA (`WPA 100`)? What does WPA overwrite?
3. Behaviour: is a MOV beyond the limit refused with an error (ERR? code) or clamped? Does TMN?/TMX? change to
   reflect them?
4. Can the same be set from PI's own GUI (PIMikroMove) or the PI GCS DLL / Python (pipython) as an alternative to
   raw serial?
5. Any caveats: interaction with reference switch (FRF), servo, or the 40.94 mm value LabVIEW uses.
Cite PI's C-863 user manual / GCS commands manual pages or URLs. No project files needed.
