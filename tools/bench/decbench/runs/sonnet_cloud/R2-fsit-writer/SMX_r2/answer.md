**Legend:** L86=`tools/bench/diag_c86_norbw.log`, L78=`tools/bench/c78_rowd_writer.log`, L80=`tools/bench/c80_rowd_routeA_r2.log`, S=`STATUS.md`.

**1. Strongest reason the claim is wrong.** An on-disk writer already addressed the FSIT sink and landed Row D on a scratch copy. L86 cell A (scratch = pinned bed, `:8`, `:36`):
- After deleting wire 7506 with Remove Bad Wires banned, #7468 still resolves and #7488 is bare (`:74-76`).
- One call of `OpFsInnerTunnelConnect_v1.vi` (md5 `5b4e5f0f…`, `:22`) returns `term_uid`=7488 and `uid_back`=7468 (`:87`).
- It puts wire 25324 on #7488 and the new border (`:96-97`), leaving exactly one source (RightShiftRegister #23868), #4334 off the net, and `Is Broken?` False (`:107-110`).

So "no writer can address an FSIT sink" is false. "Build a new op first" is already done: the op was built and saved at c84 (`tools/bench/build_d1_m3a3b_d3.log:47-48`), and S:54's own NEXT runs it (`tools/recipes/stage_d1_m3a3_rowD.py:8-9`).

**2. Alternative explanations of the same evidence.**
- The cited "W1 gate" is not in L78. Its gates are A1–B3, 5 pass/0 fail, and the zero is "a FACT, not a gate failure" (L78:33,39). W1 is a lookup in the recipe's own `WRITERS` dict (`tools/recipes/build_d1_m3a3.py:626,632-647`). `tunnel_uid` has been bound since the re-cut (`:302-309`).
- The census counts a uid sink only if a `sink*` value starts with "uid" (`tools/bench/diag_c78_rowd_writer.py:162-163,186-188`). v1's map keeps `sink_*` as index names and stores the uid under `fsit_uid` (`tools/bench/opfsinnertunnelconnect_v1_labels.json:5-7,12`). Today's census would still print 0 beside a working writer. "Invoked on the SINK" is an adopted convention (`docs/NAMES.md:850`; `archive/peer/2026-09-22-c79-rowd-writer.md:143`).
- "No file" is sequencing: the stage recipe is "NOT yet run" (S:54), cycle 66 died at its deadline with c85's recipe unrun (S:26), and c86 saves nothing by design (L86:3).
- The c83 "delete → #7468 unresolvable" ran Remove Bad Wires right after the delete (`tools/bench/diag_c83_connect2x2_r2.py:449-450`; `docs/cycle27-plan.md:3381-3389`). c80 read #7488 post-delete with no Remove Bad Wires (0 mentions, L80:104-105).

**3. Falsifier.** Any on-disk op putting a new source on #7488's net. Observed twice: L86:96-97, and L80:253-261 (swapped `OpConnectFromWire_v0`).

**4. Cheapest discriminating test.** Free: grep `AM3b|AM4a` in L86. New: run the written, unrun `stage_d1_m3a3_rowD.py` on the md5-pinned bed. If D0/D2/D3 pass, the claim is dead. If D0/D1 fail, the blocker is delete-order or merge semantics, still not "no writer".

**Caveats.** L86 has no `BGRUN END`, stops mid-cell B (`:134`), is n=1, and S:26 still calls it "IN PROGRESS", so it is strong but unratified. Row D's missing file (S:9) survives; the "no writer" reason does not.

DEFECT: blocker - Both the premise (no writer can address an FSIT sink) and the action (build another op first) are refuted by the saved `OpFsInnerTunnelConnect_v1.vi` landing Row D on a scratch copy in L86 cell A.