## Karpathy coding principles (livebench arm A13K only)

Source: `CLAUDE.md` of https://github.com/forrestchang/andrej-karpathy-skills (guidelines distilled from Andrej Karpathy's
remarks on LLM coding agents). Licence: the repository README declares **MIT**; the repository has no LICENSE file at its
root and `CLAUDE.md` itself carries no licence or attribution line (both read 2026-10-06, card chat-B7). This section is a
faithful PARAPHRASE with attribution, not the verbatim text. Where this section and the project's rules (CLAUDE.md,
STATUS.md, your card) disagree, the project's rules win.

1. **Think before coding.** State your assumptions before you act. When a request can be read more than one way, name
   the readings instead of silently picking one. Look for a simpler route and say so when you see one. If something is
   still unclear, stop and ask (in this project: put it under `open` in your result instead of guessing).
2. **Simplicity first.** Build only what was asked. No speculative features, no extra layers of abstraction or
   configuration, no guards for cases that cannot happen. If the code is more complex than the task needs, cut it.
3. **Surgical changes.** Touch only what the request needs. Do not tidy surrounding code; keep the existing style.
   Remove only the imports or variables your own edit made unused. Report unrelated problems you notice; do not fix them
   unless asked.
4. **Goal-driven execution.** Turn a vague goal into concrete, checkable outcomes. For multi-step work write a short
   numbered plan with a verification step for each item, and use those success criteria to keep going without asking.
