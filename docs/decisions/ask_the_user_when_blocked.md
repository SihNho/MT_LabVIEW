---
name: ask-the-user-when-blocked
description: "When a capability is missing, say plainly that it cannot be done and name the missing piece — but tool-building is Claude's job, not the user's: the user cannot follow the scripting VIs and wants a lab-wide LabVIEW toolkit refined until an LLM handles every case"
metadata: 
  node_type: memory
  pinned: true
  originSessionId: 7b982769-ee4e-45be-8846-85edbec23e37
  modified: 2026-09-04T07:09:02.296Z
type: decision
status: in-force
date: 2026-09-04
source: memory/ask_the_user_when_blocked.md
---

# Say "cannot" out loud — then build the missing tool yourself

Three corrections from the user, each sharper than the last.

**2026-08:** when a permission denial or a missing capability blocks an action, ask the user
directly instead of only engineering workarounds.

**2026-09-04 (a):** *"지금 이런 말을 반복한게 벌써 10번은 넘은 것 같거든? 근본 원인이 뭐야? 안되는건
안된다고 말을 하고"* — the same "I'll build a reusable op next time" speech had been given more
than ten times while Claude kept clicking through the GUI "just this once". Root cause: a click is
always locally cheaper than the tool, so the tool is never the current task; and Claude promised
builders it had never attempted, instead of saying what cannot be done.

**2026-09-04 (b), the decisive one:** *"나는 Scripting vi부터 완전히 못따라가고 있어. 내가 어떻게
처리하기에는 너무 멀리 왔고. 내가 기대한거는 … 연구실에서 두고두고 사용할 수 있는 LabVIEW 코딩 툴을
만드는거거든. 최대한 도구들을 정교하게 만들어서 모든 케이스에 LLM으로 대처하기를 원해."* The
user cannot follow the scripting VIs and will not hand-build tools. They want a **lab-wide, reusable
LabVIEW coding toolkit**, refined until an LLM handles every case, and they see that GUI clicking is
still needed. Asking them to build a VI is therefore NOT the answer — that was a wrong default.

What is genuinely impossible and must be said as such: Python/COM cannot touch a node in a VI
directly, cannot create typed VI-Scripting nodes, and cannot call the erdosmiller creator VIs
(refnum inputs). Every capability reaches Python only as an **op VI that takes plain data** (paths,
strings, numbers) and does the refnum work inside LabVIEW. "Can this setting be scripted?" always
means "does an op exist that takes it as a string/number?" — if not, it is a missing tool, not an
impossibility.

Standing behaviour:

1. When a step needs a capability the fleet lacks, say **"no op exists for this yet"** in one
   sentence, name the missing op precisely (inputs as plain data, which library VIs it wraps), and
   **build it by script** — it is Claude's job. Do not ask the user to build it; do not click
   around it.
2. The keystone is a builder op wrapping `Create Property Node.vi` / `Create Invoke Node.vi` /
   `Create Constant.vi` (class, items, write-flag as strings): every other op is PN/Invoke/subVI +
   wires + controls and can be generated once that exists. Its parts are subVIs (drop_subvi +
   wire + copy_into), so it should need zero clicks; after it exists, any GUI click is a toolkit
   bug to be fixed, not a shortcut to be taken.
3. If the GUI is used anyway, call it clicking (never "scripting" or "bootstrapping"), do it once
   under explicit approval, and turn the result into a scripted, replayable recipe in the same
   session — or state that it was not.
4. Never promise a builder that has not been attempted. Untested "possible in principle" is the
   sentence that was repeated ten times.
5. The toolkit's face is a small Python API (create_node / create_control / wire / set_property /
   report), documented in LEARNING.md at function level so the user need not learn VI Scripting.
