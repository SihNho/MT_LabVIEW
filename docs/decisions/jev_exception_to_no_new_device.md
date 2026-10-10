---
name: jev-exception-to-no-new-device
description: "The user's 2026-09-22 decision — TypeSafe's Jev (fast, cheap typed-decision model) may be wired into existing decision points as an exception to the 2026-09-18 \"no more devices\" order, measured on a labelled set first and introduced as an advisory signal; the user wants it used to cut cycle time, not only for the firefighter"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-21T22:21:56.648Z
type: decision
status: in-force
date: 2026-09-21
source: memory/jev_exception_to_no_new_device.md
---

# Jev is the exception to "no more devices", and it is for cycle time

On 2026-09-22 the user obtained a TypeSafe API key, saw the first trial ($0.0032 for 40 calls, 0.5 s each,
92.5 % on corrected labels vs the runner regex's 77.5 %) and said:

> *"정말 엄청 싸네. 이정도면 소방수만 아니라 다른 부분에도 적용하면 좋겠는데? 빠르고 싸고 정확하니까"*
> *"지금 한 싸이클 도는게 엄청 오래걸리잖아. Jev 활용해서 시간을 절약하고 싶은데"*
> *"Jev 건은 예외로 추가하도록 하고"* — lifting, for Jev only, the 2026-09-18 order "장치는 더 만들지 말고 계속 진행".

## How I apply it

- **Jev-backed devices are allowed**, but only behind an EXISTING decision point (firefighter trigger, failed-
  prediction review gate, log classification, plan/NEXT checks), never as a new process layer of their own.
- **Measure before switching on**: each insertion gets its own labelled set (about 40 items, one bgrun, cents of API
  spend) and a regex/baseline comparison, like `tools/bench/jev_trial.py`; then it enters as an ADVISORY signal
  (logged `JEV-…`, overriding nothing) and is promoted only after a few cycles of agreement.
- **The goal is cycle time.** Measured 2026-09-22 (cycles 53–59): the judgement session's own reading/writing is
  ~52 % of wall time, peer reviews ~21 %, builds ~14 %. So the first insertions are the ones that remove reviews and
  reading: (1) "same failure class as an already-reviewed one" to discharge the mandatory review, (2) log triage that
  hands the session a one-line verdict, (3) the firefighter false-trigger veto.
- Probabilities between roughly 0.3 and 0.7 mean "unknown" and fall back to the existing path. Jev never
  generates text, never sees images, and the key stays in the user environment variable only.
- The full insertion table is `docs/jev-integration-plan.md`.
