"""UserPromptSubmit hook: inject rule 2b at the moment it matters — every user message.

Why (user, 2026-09-04, third recurrence): the "answer first" rule lives in CLAUDE.md, which is read
at session start and fades after context compaction; a mid-turn message then gets a tool call and a
progress line instead of an answer. This hook prints the rule as context on EVERY user prompt, so the
structure, not memory, keeps it.
stdout (exit 0) is added to Claude's context for that turn.
"""
import sys

MSG = (
    "[hook answer_first] RULE 2b: the FIRST LINE of your reply is the direct answer to this message "
    "(a yes/no question gets its yes/no in the first sentence). Tool calls come after the answer; a "
    "progress line is not an answer. If the message implies stop/redirect, stop the running work. "
    "Foreground commands that touch LabVIEW: timeout <= 30 s, otherwise run_in_background."
)

if __name__ == "__main__":
    sys.stdout.write(MSG + "\n")
    sys.exit(0)
