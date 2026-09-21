# REFUTE THIS CLAIM — the two hygiene failures in `tools/bench/diag_c67_opvi.log` are a defect in the diagnostic's own comparison, not a changed file

## The failure

`tools/bench/diag_c67_opvi.log` (`BGRUN END rc=1 after 124s`) ends `HYGIENE GATES: 12 pass / 2 fail`. Both
fails are the same shape:

```
FAIL  Y OpAddShiftReg_v0 is byte-unchanged by this run  before 'HASH C:\...\OpAddShiftReg_v0.vi |
exists=1 | size=13864 | md5=42841674debec182c6add6fe23972fec | sha256=554444ba...' ;
after md5 '42841674debec182c6add6fe23972fec' size '13864'

FAIL  Y OpAddShiftRegF_v0 is byte-unchanged by this run  before 'HASH C:\...\OpAddShiftRegF_v0.vi |
exists=1 | size=16433 | md5=01e62ec5b907d4bb84eb236a35f8cef5 | sha256=bcf98484...' ;
after md5 '01e62ec5b907d4bb84eb236a35f8cef5' size '16433'
```

These two VIs are read-only inputs to the run. The diagnostic never edits or saves them; it opens them by
`Application.GetVIReference` and calls `GetControlValue` on their panel objects, and in the write legs it
runs `OpAddShiftReg_v0.vi` through the project's ordinary `_run` path.

## The code that produced the failure, verbatim (`tools/bench/diag_c67_opvi.py`, the `[Y]` block)

```python
pr = probe("Y %s AFTER (it was READ, never edited or saved)" % tag, opath)
before = next((h["line"] for h in R["hash_probe"]
               if h["tag"] == "[L0] %s ON DISK" % tag), None)
same = before is not None and before.split(" | ", 1)[1] == \
    ("md5=%s | size=%s" % (pr.get("md5"), pr.get("size")))
gate("Y %s is byte-unchanged by this run" % tag, same or before is None, ...)
```

`probe()` stores the raw line that `tools/hash_probe.py` emits and returns it parsed:

```python
def probe(tag, path):
    line = HASH(path)                       # "HASH <path> | exists=1 | size=<n> | md5=<x> | sha256=<y>"
    R["hash_probe"].append({"tag": tag, "line": line})
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])
```

## The claim to refute

> **Both gates failed because the comparison is wrong, not because either file changed.**
> `before.split(" | ", 1)[1]` yields `"exists=1 | size=13864 | md5=42841674… | sha256=554444ba…"` — four
> fields, in that order — and it is compared for string equality against `"md5=42841674… | size=13864"`,
> two fields in the opposite order. The two strings can never be equal for any input, so the gate is
> unconditionally false whenever the file exists. **The evidence that the files did NOT change is printed on
> the failing lines themselves: the `before` md5 and size (`42841674…`/13864 and `01e62ec5…`/16433) are
> character-for-character identical to the `after` md5 and size.** The fix is to compare the PARSED md5 and
> size fields instead of the raw line; nothing about the run's behaviour changes.

## Already ruled out (do not re-argue these)

1. **A save by this diagnostic.** It calls no `save`, no `gui_save`, no `make_default`, no `revert`; the
   static gate `tools/bench/c60c_astcheck.py` passed 12/12 on it (`tools/bench/c67c_astcheck.log`,
   `=== ASTCHECK OK`) including gate 2 (`gui_save` neither imported nor called).
2. **A different file.** `[L0]` and `[Y]` probe the same two absolute paths, printed in full on both lines.
3. **A truncated or missing `after` read.** The `after` values are present and well-formed on both lines.

## What we need from you

1. **Attack the claim.** Give the strongest reason it is wrong, and any alternative explanation under which
   one of those two `.vi` files really did change on disk during the run and the md5 still reads identical.
   In particular: is there any circumstance in which LabVIEW rewrites a `.vi` it has loaded — for example on
   a recompile, on a relink of subVIs, or when the front panel of a VI that was run is closed — that would
   leave the file byte-identical, or that would change it between the `after` probe and a later read?
2. **Is `md5 + size` a sufficient unchanged-check here at all?** The probe also carries a sha256 that this
   gate ignores. Say whether ignoring it weakens the conclusion, and whether mtime should be part of the
   check (the diagnostic reads mtime separately at `[L0d]`: `2026-09-14 22:41:42` and `2026-09-14 23:49:26`
   for the two files, i.e. their build dates).
3. **Running a VI over ActiveX writes to its front-panel indicators.** `OpAddShiftReg_v0.vi` was run four
   times in this session and its `UID 2` indicator went `0 → 23561 → 23693 → 23561 → 23498`. Does that
   in-memory change put the loaded VI in a state where LabVIEW may later write the file (a dirty-dot save
   prompt, an auto-save, an unload-time save)? What is the cheapest READ that would detect such a write
   after the fact? This matters because the project's rule 1 forbids modifying any pre-existing `.vi`.
4. **What would falsify the claim, and what is the cheapest discriminating test?**

## Constraints on your answer

* Answer with reads and tests, not a redesign. Any route change, new verb or repair you propose will be
  quoted verbatim and handed to a separate judgement session; it will NOT be acted on here.
* Where you assert LabVIEW behaviour, say whether it is documented, measured elsewhere, or inferred.
