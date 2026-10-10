---
name: read-the-code-before-asking
description: "The user's 2026-09-15 correction — most questions I put to them are already answered in the code, and asking before interpreting the code is what stalls the process; ask only what code cannot contain"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 1c79eb01-7150-4a78-9689-e6d4f34f7800
  modified: 2026-09-15T07:52:31.706Z
type: decision
status: in-force
date: 2026-09-15
source: memory/read_the_code_before_asking.md
---

# Read the code first. Ask only what the code cannot contain.

On 2026-09-15 the user said, after a stretch of me raising questions between measurements:

> *"왠만한 질문의 답은 사실 코드 자체에 있는 것 같음. 코드 해석이 되지 않은 상태에서 질문을 한다고 프로세스가
> 지체되는 경우가 많이 보임."*

They were right, and the example was live in the same conversation. I had just asked them where the PI motor and
rotor communication happens and how often — while the answer was sitting in the VI's diagram hierarchy, which
nobody had built because I had never read past the three loop bodies. The question was not a request for domain
knowledge; it was a substitute for work I had not done.

## The cost of getting this wrong

Asking looks cheap and is not. It stops the work, puts the burden on the user to decode a question written in my
vocabulary, and produces an answer I then have to verify against the code anyway. The same message that carried
this correction also carried the standing instruction to **document the diagram hierarchy properly** — because the
missing document, not the missing answer, was the real defect.

## The test to apply before asking anything

**Could this fact be present in the code, the logs, the fixture or the docs?** If yes, go and read it. Build the
reader if the fleet lacks one — that is cheaper than a round trip, and it leaves an artefact behind. Only the
following genuinely belong to the user:

- **Operational intent**: what a control MEANS to an experimenter (`Limit of Program` is the cap on auto-resets so
  a run that has lost its beads stops and saves — nothing in the diagram says that).
- **Rig physics and procedure**: that reassembly costs two hours of sample prep, that beads come unstuck on long
  runs, that focus adjustment is frequent in practice.
- **Priorities and acceptance**: which deviation is tolerable, which deliverable comes first.
- **Permission**: anything touching hardware.

Structure, call sites, wiring, which loop encloses what, what executes unconditionally, how a value is computed —
all of that is in the code, and reading it is my job.
