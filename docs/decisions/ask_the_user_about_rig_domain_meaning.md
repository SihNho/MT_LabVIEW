---
name: ask-the-user-about-rig-domain-meaning
description: "A parameter being structurally unreachable never proves it is functionally unnecessary — the user holds rig domain knowledge Claude cannot derive, so ask instead of inferring irrelevance"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-08-29T16:17:12.660Z
type: decision
status: in-force
date: 2026-08-29
source: memory/ask_the_user_about_rig_domain_meaning.md
---

# Structural unreachability is not functional irrelevance — ask the user what a parameter is for

On 2026-08-30, while rebuilding the magnetic-tweezers tracking kernel, Claude found that the name
`cosine bandpass` could not be wired to the bead kernel (a 5001 "name not found" from the scripting
library) and concluded in STATUS that such inputs were **"not our problem"** because unreachable
inputs simply keep the kernel's own defaults. The user challenged this from domain memory: they
recalled `cosine bandpass` being a real parameter in the main VI governing the **valid calculation
range and band-pass filtering of the bead's radius profile along the z axis** — i.e. something that
plausibly changes the tracking result, not a decoration.

The error was not the measurement; the 5001 was real. The error was the **leap from a structural
fact to a functional verdict**. "This terminal cannot be wired" answers a wiring question. It says
nothing about whether the quantity matters to the physics, whether the old code delivered it by
another route, whether a sibling sub-kernel consumes it, or whether the value silently defaults to
something wrong for this experiment. Dropping a parameter is a change in behaviour, and behaviour
is exactly what a structural check cannot see.

**So: whenever a build decision would drop, default, or route around a named parameter, treat it as
a domain question and put it to the user.** They designed and run the rig, and they can say in one
sentence what a parameter is for — knowledge that would otherwise cost hours of tracing dense
diagrams, and that Claude cannot derive from wiring probes at all. This is cheaper for everyone
than discovering the omission after a numeric comparison fails.

This is the same failure family as over-claiming verification (see
`search_the_web_when_troubleshooting.md` and the project's "two levels of verification" rule): a
cheap, satisfying, scriptable check gets promoted into a conclusion much larger than it supports.
Here the specific antidote is: **name the parameter to the user and ask what it does, before
designing it out.**
