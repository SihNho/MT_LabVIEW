ATTACK this claim about the failed run tools/bench/diag_c122_route.log (script tools/bench/diag_c122_route.py).

FAILURE: gate "S0 #3121 is a flat-sequence frame diagram" FAILED (diag_c122_route.log:267-270):
  OBSERVED uid 3121 -> owner 'FlatSequenceFrame' uid 0 | self 'Diagram'#3121 | 482 says 'FlatSequenceFrame' cast '' | error 1055: Property Node in OpOwnerChain_v1.vi
  owner_of(3121) raised RuntimeError (strict=True) because uid_back/errs were not clean.

CLAIM (the explanation we formed): the failure is the SCRIPT's premise, not a LabVIEW or tool defect.
  - S0 called tools/recipes/build_d1_v0.py owner_of(W, 3121, strict=True) (diag_c122_route.py:49); strict=True raises when
    the owner chain op reports any error (build_d1_v0.py:351-353).
  - For a flat-sequence FRAME diagram, OpOwnerChain_v1 reads Owner -> class 'FlatSequenceFrame' but the frame is not a GObject
    with a UID in the chain op, so it returns uid 0 plus error 1055 - an expected, previously seen answer
    (see archive/peer/2026-09-28-c120-fs-owner-frame.md).
  - The same script's graph() calls owner_of(strict=False) (diag_c122_route.py:36) and accepted every Diagram owner (G1 PASS,
    log :265-266), so ('FlatSequenceFrame', 0) under strict=False IS the accepted FS-frame check (plan PD244(b),
    docs/d1-loop12-17-split-plan.md:2364-2365).
  - Consequence used next: the P2b build (card 122-6) checks its target frame #4866 with owner_of(strict=False) ==
    ('FlatSequenceFrame', 0) and does not re-run diag_c122_route.py; the P2b scratch run on a bed byte copy is the route's
    verification (PD244(d)).

Already ruled out: (1) the bed being wrong (graph md5 field == bed md5, G1 PASS); (2) #3121 not being a Diagram
(self 'Diagram'#3121 echoed); (3) handle/ref leaks (refs 7/7, LabVIEW gone, diag_c122_route.log:276-296).

Questions: is there evidence in the repo that error 1055 on a FS-frame Owner read means something OTHER than "frame has no
uid" (e.g. a stale reference, a wrong Traverse index, a frame that is not on the expected flat sequence)? Could #4866 behave
differently from #3121? What is the cheapest discriminating test before the P2b scratch run relies on strict=False?
