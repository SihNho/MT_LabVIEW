---
card: 159-a2-1
status: current
date: 2026-10-10
---
# Brief 159-a2-1 (assignment 159-1) - OFFLINE side facts, PD387(g) first half (runs beside the LabVIEW graph read)

No LabVIEW, no tool edit, no hook edit, no gate_fp entry. Read-only work; the only file written is `tools/bench/diag_c159_side_facts.md`.

Two diagnostics from cycle 158 printed an oddity. Find the CAUSE LINE (file:line) of each by reading the code and the logs; do not guess.
1. `tools/bench/diag_c158_a2_3_probe*` (script and its log): a `result_line` call raised `TypeError`. Quote the log line of the traceback, the
   `file:line` where the call is made, and the argument that has the wrong type/arity versus `tools/protocol.py` `result_line` / `make_result`
   (read the signature). State whether the probe's own output is still valid (the measurement it was meant to take) or not.
2. `tools/bench/diag_c158_a3_2_pascope*`: it printed `no scope`. Quote the log line, the code that prints it, and the condition that was false
   (what the script looked for, what the loaded graph/session actually had). State whether this is a script defect, a missing input, or by design.

For each: one line "cause: <file:line> - <one sentence>", one line "affects: <what depends on it>" and, if the repair is a script edit in a file
this card may not write, say which file and which line. Do NOT log to `gate_fp_queue.jsonl`: neither is a gate false positive unless the code shows a
gate refused a correct input (if so, quote the refusal text and say so, but still do not log it).

Report `tools/bench/diag_c159_side_facts.md` (<= 25 lines): frontmatter (type: facts, status: current, date: 2026-10-10, card: 159-a2-1), the two blocks above,
then `OPEN:` lines. Facts only.
