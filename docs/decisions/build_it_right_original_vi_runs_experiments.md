---
name: build-it-right-the-original-vi-runs-experiments
description: "Do not sequence work around \"make the new version usable sooner\" — the original VI is the production instrument, so new features wait for the proper restructuring instead of being patched into the old code first"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-12T09:34:44.013Z
type: decision
status: in-force
date: 2026-09-12
source: memory/build_it_right_original_vi_runs_experiments.md
---

# The original VI runs the experiments, so build the new one properly rather than quickly

On 2026-09-12 the user wanted a rotor column added to the experiment scheduler. Two orders were possible: patch the
feature into the existing main VI now (small change, usable immediately, but it would have to be moved again during the
planned loop restructuring), or restructure first and add the feature into the new structure. Claude recommended the
first, arguing the feature looked experimentally urgent. The user chose the second:

> "실험이야 원본 vi로 하면 되는 일이고 재구성해서 넣자"

The reasoning is worth keeping because it generalises: **the original VI still works and still runs real experiments**,
so there is no pressure to make the in-progress version usable early. Feature urgency is not a reason to add something
to the old code, because the old code is already doing the science.

Standing consequence for how work is sequenced:

- When a new feature and a structural change both touch the same region, do the structural change first and build the
  feature into it. Do not propose the quick patch as the pragmatic default.
- "The user needs this soon" is not, by itself, an argument for the shortcut — ask whether the original already covers
  it, because it usually does.
- The value of doing it in the right order is not tidiness: work added to the old structure has to be moved and
  re-verified later, and every move is a chance to change behaviour in a project whose first rule is that the
  computation must not change.
