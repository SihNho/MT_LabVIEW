---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# opbuildpn-v1-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (69s)
- **why asked:** See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
- **verdict:** see 'What was done with it' / STATUS.md 2026-09-14

## Question

ATTACK this small build plan before I execute it (LabVIEW 2026 VI Scripting over ActiveX; the project's rule is plan -> peer review -> build). CONTEXT: our keystone op OpBuildPN_v0 wraps erdosmiller 'Create Property Node.vi' (terminals: Diagram in, Class Name, Properties [array of (ID string, write?)], location, reference, error in, and OUTPUTS: Diagram out, reference out, Inputs, Outputs, error out). Read from a file copy today: the creator's 'error out' and 'Outputs' are UNWIRED; the op's front-panel 'error out' indicator is fed from elsewhere. Consequence, confirmed by you earlier: an ID the class does not support raises error 1077 inside the creator and is silently dropped, leaving a rows-less Property node that looks identical to success. PLAN for OpBuildPN_v1 (built by script from a file COPY of v0; v0 untouched): (1) wire creator.'error out' -> a NEW front-panel indicator 'creator error' (via Terminal.Create Indicator on that terminal); (2) wire creator.'Outputs' -> a NEW indicator 'Outputs' (an array of Terminal refnums - Create Indicator on that terminal should give the right array type); (3) save only if ExecState==1; (4) VERIFY with a control and a known-bad case on one scratch VI: GObject.Position 632A800 -> expect creator error none, Outputs length 1; a deliberately bogus ID 'FFFFFFF' -> expect a non-zero creator error (1077?) and Outputs length 0; then Control.Terminal 6332006 and AbstractDiagram.SubVIs[] 6375802 -> classify by the SAME two readings. Python then reads 'creator error' and len('Outputs') and raises on failure, ending silent empty nodes. QUESTIONS: (a) is 'Outputs' on the erdosmiller creator the array of the new node's output terminal refnums, and will Create Indicator on that terminal produce a usable refnum-array indicator readable over ActiveX (or does an array of refnums read back as something unusable, in which case I should instead wire it to an Array Size and indicate the integer)? (b) any reason wiring the creator's error out to an indicator could CHANGE the creator's behaviour (auto error handling was turned off on v0 at some point - will a wired error out re-enable a dialog)? (c) is there a risk that the creator returns Outputs of length 1 even when the property row failed (a default row)? (d) anything simpler that makes 'attached' deterministic that I am missing (e.g. reading Property.Property Count 636F80X on the returned reference inside the op)? Keep it to what changes the build.

## Answer

Verdict: build v1, but change its external contract to `creator error` + integer `Output count`. Do not expose `Outputs` to Python.

- `(a)` The creator?셲 `Outputs` very likely means the property-item output terminals, separate from `reference out`; that interpretation matches the connector pane and LabVIEW?셲 Property Node terminal organization. Property nodes also contain reference/error terminals plus property-item terminals. [NI Community terminal breakdown](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

  `Create Indicator` should preserve the array-of-Terminal-refnums datatype because creating an indicator from an output terminal adopts that terminal?셲 type. [NI User Manual](https://download.ni.com/support/manuals/320999b.pdf)

  However, this project has already established that ActiveX `GetControlValue` cannot marshal even scalar refnum indicators. Do not assume wrapping refnums in an array fixes that. Wire `Outputs ??Array Size ??Output count (I32)` and read only the integer. NI confirms that Array Size returns the number of array elements. [NI Community](https://forums.ni.com/t5/LabVIEW/Determine-array-size-on-vi-scripting/m-p/3728136/highlight/true)

- `(b)` Wiring `error out` will not re-enable a dialog or change the creator?셲 functional action. It does the opposite at that node: a wired error output is considered handled and suppresses automatic error handling there, even if VI-level automatic error handling is enabled. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)

  Wiring it to an indicator adds only a dataflow dependency before the wrapper finishes. There is no reason to restore auto-error handling on v1.

- `(c)` Yes, treat `Outputs length == 1 on failure` as possible until measured. The library may allocate or retain a default property row before the ID assignment fails. Therefore:

  ```text
  success = creator error.status == FALSE
  Output count = corroboration, not the primary verdict
  ```

  Require `count == requested read-property count` only after `creator error` is clean. Never let a plausible count override an error. Likewise, expect ?쐍on-zero error,??not specifically 1077: NI defines 1077 as ?쏧nvalid property value,??but an unsupported scripting ID could conceivably produce a different error in this path. [NI error-1077 article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P6FSSA0&l=en-US)

- `(d)` `creator error` is the simplest deterministic attachment signal. Do not add `Property Count 636F80X` to v1 yet: it introduces another class/property-ID operation and another possible swallowed error. At most, use it later as independent verification?봭ot as the primary success test.

Changes I would make before execution:

1. Expose `creator error` and `Output count`, not the refnum array.
2. Python raises immediately when `creator error.status` is true; include code and source.
3. Only after a clean error require the expected count.
4. For the bad-ID control, require `error.status == true`; record the actual code rather than asserting 1077.
5. Reset/recreate the scratch target between probes. Otherwise a failed/default node from one case can contaminate `ExecState` or the next count.
6. Keep `ExecState == 1` as the save gate, but remember it proves compilability, not that the requested member attached.

Expected classification contract:

```text
clean error + expected count  ??attached
non-clean creator error       ??rejected; raise
clean error + wrong count     ??inconsistent; raise
```

That closes the silent-empty-node failure without adding another private or version-sensitive property read.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
