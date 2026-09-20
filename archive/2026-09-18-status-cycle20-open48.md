---
type: archive
status: archived
date: 2026-09-18
tags: [status, open-items, cycle20, fstunnel-reader]
---

# STATUS OPEN 48 — the pre-release body, relocated VERBATIM (rule 4, STATUS was at 121 lines)

Relocated 2026-09-18 03:5x by the cycle-20 step-2 material session when the item was superseded by OPEN 48a
(the four findings accepted, the recipe rewritten, the release validated). Nothing rewritten; the live line in
`STATUS.md` now points here.

48. 🔴 **JUDGEMENT — cycle 20 step 2's op is WRITTEN but STOPPED; only judgement may release it.**
   `tools/recipes/build_opfstunnelterm_v0.py` (sha `de04c05f5f65`): prior art = **4 findings, 0 novel**
   (`archive/peer/2026-09-18-priorart-fstunnel-reader.md:300-303`) — `contradicted` (FSOT-only, but **14 of 18**
   measured non-node crossings are `FlatSequenceInnerTunnel`; FSIT 518 vs FSOT 58) · `unread-evidence` (the
   accepted dual review's **T2 face test** is absent; gate L4 scores a non-advancing hop as CROSSED) ·
   `helper-exists` (`diag_tunnelsource_onehop.py:198-233` already has the hop loop **and** its "does not advance"
   refusal) · `already-measured` (`Owner→cast→UID` = uid 0 + error 1055 at a FlatSequenceFrame,
   `diag_ownerchain_hop.log:7`; L1 never reads `owner_uid`). Launch refused until `FIXED:`/`REFUTED:` stands.
   ✅ **MEASURED MEANWHILE** (`tools/bench/diag_uid_identity.log`, 3/3): **both** VIs carry 28343 (LoopTunnel),
   43605 (FSOT) and 44036 (SubVI) — **the uid space is SHARED, so a uid names no VI**; the *caches* are keyed to
   the V6 copy (`nodeterms.vi`, census `md5 2a78e17c…`) and the ORIGINAL has **97 SubVIs vs V6's 98** (1898 vs
   1902 wires) = the census's own 97. Fixture RESOLVED with existing ops: `LoopTunnel 28343` → out_wire 28392 ←
   `SubVI 27605` = **Max Trans Pos.vi · 'Magnet position output'**.
