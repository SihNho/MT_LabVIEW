# Brief 126-6 — measure every crossing kind P3b needs (PD255(g))

Decisions applied (do not re-open): `docs/d1-loop12-17-split-plan.md` PD254(e), PD255(a)(b)(g). Measurement only; each
crossing's census is RECORDED as a sample, not predicted (these routes have no sample yet).

## STEP A — `tools/bench/diag_c126_4_fs.py` (md5 `da7a851e…`, prerun 14/0, written by card 126-4, not yet run)
- On a P3a BYTE COPY: 3-frame FS in case `#22694`'s False frame `27219`; Q&R `#27373` remainder (`x-y*floor(x/y)`, t27401)
  → a node input in FS frame 1 by `connect_term_uid`, then a SECOND sink from the same source → a node input in FS frame 3.
- Per wire: census delta, `Is Broken?`, `wire_joints` free ends, tunnels made (class, uids, faces per frame); then
  `wire_remove_loose_ends` on each new wire and the same reads after. Error List: compare the TOTAL count and the
  `Wire has loose ends` count only (PD255(a): OCR'd class keys vary — `subvi`/`subvl`).

## STEP B — the multi-border forms (new script `diag_c126_6_cross.py`, ≤ 120 lines, on stagekit; dry + prerun first)
On a fresh P3a byte copy with the same 3-frame FS, one crossing each, by `connect_term_uid` (or, if it refuses a
multi-border crossing, the existing route `nested`, `gscript.connect_nested_v2`, which crossed several borders in P2a/P2b —
report which one worked):
1. BufNum `t6897` on `#639` (outside the case) → a node input in FS frame 3 (case border + FS border).
2. While `#637`'s `i` (t644) → a node input in FS frame 2 (loop-body diagram → case → FS).
3. Pool `#23099` (For `#23093` exit on FS1, outside While `#637`) → an `Index Array` input in FS frame 2 (For exit, While
   border, case border, FS border). A While-border array tunnel must come out NON-indexed (CLAUDE.md 1a: whole-array
   parameters cross loop borders non-indexed) — read the tunnel's indexing mode back.
Per crossing: census delta, tunnels per border (class, uid, indexing mode where a loop border), `Is Broken?`, free ends;
then `wire_remove_loose_ends` and the same reads; Error List total + `Wire has loose ends` count at the end.

## Always
- Bed md5 unchanged; scratch copies deleted; LabVIEW closed and verified gone.
- Return at the first unexpected result (finish the step cleanly). Facts in `result_126-6.json` with each crossing's
  measured census as a census sample in `tools/bench/census_samples.json`, and a `scratch_verify` record.
