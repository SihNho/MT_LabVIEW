r"""jev_next_q.py - the two Jev questions for insertion #5 of docs/jev-integration-plan.md (NEXT quality).

They live in ONE file so the measurement (tools/bench/jev_next_trial.py) and the advisory line in
tools/hooks/guard_bash.py:next_gate() ask the SAME question; a gate that asks a different question from the one
that was measured is not the thing that was measured. No key handling, no HTTP, no state: constants only.
"""

NEXT_Q = {
    "type": "noul",
    "instructions": (
        "`next` is the `## NEXT` hand-off section of a long-running LabVIEW project's STATUS.md. The next work "
        "cycle runs in a FRESH session that reads STATUS.md and the cycle plan and nothing else. Decide whether "
        "that session can START WORK from this text without re-deriving anything: is there a concrete first act, "
        "the file or plan section to start from, and a pass criterion or the name of the artefact to produce? "
        "Celebration of what was already delivered, warnings and open questions are normal and do not count "
        "against it; judge only whether the next act is startable as written."),
    "criteria": {
        "true": ("All three are present and specific: an act the session performs first (build/measure/repair X), "
                 "the file, recipe or plan section it starts from, and how it will know it succeeded - a pass "
                 "criterion, a gate count, or the name/md5 of the artefact it must leave on disk."),
        "false": ("At least one is missing or is left to the reader: no first act at all (a narrative, a summary "
                  "of findings, or a hand-back to the user), or an act with no named starting file/plan section, "
                  "or an act with no stated criterion or artefact, so the session has to decide for itself what "
                  "'done' means."),
    },
}

MISSING_Q = {
    "type": "choice",
    "instructions": (
        "`next` is the `## NEXT` hand-off section of a LabVIEW project's STATUS.md, judged not to be startable by "
        "a fresh session. Name the ONE element whose absence costs the most."),
    "criteria": {
        "first-act": "No concrete first act: the text narrates, summarises or hands back to the user.",
        "start-file": "There is a first act, but no file, recipe or plan section is named to start it from.",
        "criterion": "There is a first act and a starting point, but no pass criterion and no named artefact.",
        "none": "Nothing important is missing; the text is startable after all.",
    },
}
