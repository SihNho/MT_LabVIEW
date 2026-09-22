# FAILED PREDICTION — `Terminal.Connect Wire` 6349C03 is a SILENT NO-OP when its `Wire Source` terminal is BARE

Log: `tools/bench/build_opfsinnertunnelconnect_v0.log` (45 gates pass / 2 fail, `BGRUN END rc=1 after 324s`).
The two failing lines are the same gate, G4f, plus its STOP echo.

## What was predicted, and by whom

`docs/cycle27-plan.md` Pre-decided 127 (the judgement session's design for D-2) predicted that a new op
`OpFsInnerTunnelConnect_v0.vi` — built as the smallest edit of `OpConnectFromWire_v0.vi`, with ONLY the
source-half acquisition changed from (`wire_uid`, `Wire.Terms[]` index) to
(`fsit_uid` → `UID to GObject Reference.vi` → TMSC `FlatSequenceInnerTunnel` → `LeftTerm` 1C3A9000) —
would, on a scratch copy of the bed, after wire **7506** is deleted, connect the FSIT LeftTerm **#7488**
into the NEW loop's shift-register OUTER terminal (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`,
'Outgoing Handle'), so that the border terminal would go from wire 0 to a non-zero wire.

That prediction rested on `tools/bench/c80_rowd_routeA_r2.log:244`, where the SAME Invoke binding (the
Invoke on the border terminal, the FSIT terminal handed to `Wire Source`) DID make the border terminal go
BARE → wire 7506 — but there the source terminal #7488 was still carrying wire 7506.

## What was observed

The op was built and saved and is legal:

* `ExecState` 1 on the saved op, md5 `c0d5efe3389b0dea388ee565433fb683`, 17,881 B (`:78-84`).
* Both uid echoes are correct on EVERY call, with every error column empty: the resolver's own
  `uid_back` = **7468** (the uid passed in) and the LeftTerm's own uid `term_uid` = **7488**
  (`:92-93`, `:323`, `:325-326`).

**Arm 1 — wire 7506 ALIVE** (the 20-call handle scratch, bed unmodified, `:92-93`):
every one of the 20 calls returned `sink_wire=7506`, `is_broken=True`, `err=''`. So the border terminal
WAS attached, to the existing net, which then has multiple sources — the same branch behaviour
`c80_rowd_routeA_r2.log:253-261` measured. The verb fires. It also mints exactly **1.00 stray `Invoke`
node per call** in the target (`:97-99`, purged).

**Arm 2 — wire 7506 DELETED, both ends bare** (the exercise scratch, `:315-342`):

```
G4 Diagram[19].Nodes[21] uid echo 23032 (MATCH); t1 'Outgoing Handle' is_source=True wire=0
G4 deleted wire w7506 ; border t1 wire=0 (BARE)   <- PASS G4c
G4 CALL RETURN: {"err": "", "err_uidvi": "", "err_fsit": "", "err_termuid": "", "err_uidback": "",
                 "term_uid": 7488, "uid_back": 7468, "sink_wire_uid": 0, "is_broken": false,
                 "UID": 23032, "Name": "", "wire_delta": 0}
G4 AFTER the connect: border t1 wire=0 ; the op's own `UID 2` = 0 ; wire_delta 0
**FAIL** G4f the border terminal went BARE -> NON-ZERO   wire 0
```

No error, anywhere: the op's `error out`, and the per-stage indicators for the UID-to-GObject subVI, the
FSIT property node, the LeftTerm-UID node and the resolver-UID node, are ALL empty strings. One junk
`Invoke` was still minted (`:328`), so the Invoke node DID execute.

## The hypothesis you are asked to REFUTE

**`Terminal.Connect Wire` 6349C03 silently declines when the terminal handed to `Wire Source` carries no
wire.** On this reading the method does not create a wire between two bare terminals at all; what it does
is attach the Invoke's own terminal to the NET the `Wire Source` terminal already belongs to — which is
why arm 1 works (and branches) and arm 2 does nothing. If that is right, delete-THEN-connect cannot work
with this method no matter which op resolves the source terminal, and the whole Route-A family is bounded
by it.

## Already ruled out — do not re-derive these

1. **Not an addressing error.** The sink address was resolved LIVE with a node-uid echo (`23032` MATCH),
   the terminal name read back as `'Outgoing Handle'`, and gate G4c asserted `wire == 0` immediately
   before the call. The op's `UID` indicator echoed `23032` back out of the call.
2. **Not a source-resolution error.** On the SAME call, after the delete, `uid_back` = 7468 and
   `term_uid` = 7488 with every error column empty — so the `FlatSequenceInnerTunnel #7468` LeftTerm
   reference WAS obtained from a BARE tunnel terminal. (Independently consistent with
   `c80_rowd_routeA_r2.log:104,265`.)
3. **Not a stale/history echo.** Every readout (`uid_back`, `term_uid`, `UID 2`, `Is Broken?`) is poisoned
   before each run, `Is Broken?` to True, per Pre-decided 125.
4. **Not the "already-wired sink" hazard** (`tools/gscript.py:2522-2523`): the sink read wire 0.
5. **Not an op defect that breaks the VI**: `ExecState` 1, auto error handling OFF, 20/20 calls in arm 1
   returned the intended values, handle count +94 over 20 calls, private-bytes drift 0.03 MB, refs 22/22/0.

## What we want from you

1. The strongest reason the hypothesis above is WRONG.
2. An alternative explanation of arm 2's silent no-op that arm 1 does not already refute.
3. What would FALSIFY the hypothesis — stated as an observation, not an argument.
4. The CHEAPEST discriminating test, runnable on a dated scratch copy of a VI with the ops already on
   disk. Name the exact ops/inputs. Note that `tools/gscript.py` already has `connect_terminals`
   (6349C03 on two NODE-INDEX-addressed terminals) and `wire()` (the erdosmiller name-based route), so a
   test that decides whether 6349C03 EVER wires two bare terminals — on a trivial scratch VI, away from
   the bed — is available at near-zero cost.
5. If the hypothesis survives: is there a documented NI verb that creates a wire between two bare
   terminals given one of them only as a reference? (`Create Described Wire` and `Node.Connect Wires`
   were both examined on 2026-09-22 and are recorded as not fitting — say if that record is wrong.)

Answer with citations. A claim about LabVIEW's own semantics needs a source; a claim about OUR tools needs
a `file:line`.
