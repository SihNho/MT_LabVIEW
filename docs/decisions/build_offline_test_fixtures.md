---
name: build-offline-test-fixtures
description: "Validate analysis code against saved image data rather than live hardware, because Claude works while the user is away and anything touching instruments needs the user present"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T11:39:27.474Z
type: decision
status: in-force
date: 2026-08-27
source: memory/build_offline_test_fixtures.md
---

# Test against saved data; the user runs the hardware paths

The user set out the working model on 2026-08-27: *"보통 너가 작동하는 때는 내가 없을 때 체크
용도잖아. 그러니 전체 motor 코드 있는 거는 최종적으로 내가 확인하는 방향으로 해야겠지만, 그래도
분석 툴 확인 용도면 image 파일 두고 루프 도는 것만 확인하면 되니까."* — Claude typically works
unattended, so anything driving instruments has to be verified by the user, while analysis code only
needs saved image data and a loop that runs.

So the default for anything computational is an **offline fixture**: a stored frame (or frames) plus
whatever calibration data the algorithm needs, checked into a known location, so the processing path
can be exercised repeatedly with no rig, no motor, and no one present. Hardware-touching code is
written, left ready, and **handed to the user to run** — the user said explicitly they will operate
the movie-recording code once it exists rather than have Claude run it.

Two things make such a fixture much more valuable than a quick smoke test, and are worth building in
from the start:

- **Include the calibration data, not just an image.** In magnetic-tweezers bead tracking the Z
  coordinate comes from matching a bead's radial profile against a calibration stack, so a lone frame
  validates XY only. Ship the `.cal` data alongside it.
- **Store losslessly.** Use PNG or TIFF at the camera's real bit depth; JPEG's compression changes
  pixel values and therefore changes tracking output, which destroys the fixture's value as a
  numerical reference.

The same fixture then does double duty as the regression baseline for any rewrite — a GPU or C
implementation has to reproduce the stored result bead-by-bead before it can be trusted.

The user also prefers not to write extra plumbing for this: they declined to write movie-saving code
themselves, so keep the capture path as simple as possible (a numbered lossless frame sequence is far
less work than a real video encoder, and easier to analyse afterwards).
