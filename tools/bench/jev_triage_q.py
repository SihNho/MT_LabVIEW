r"""jev_triage_q.py - the ONE triage question for docs/jev-integration-plan.md insertion #2.

Kept in one file so the measurement (tools/bench/jev_triage_trial.py) and the tool (tools/jev_triage.py) ask the
SAME question: a tool that asks a different question from the one that was measured is not the measured tool.
Constants only - no key handling, no HTTP, no state.
"""

CLASSES = ["script-bug", "address-invalid", "labview-refused", "expected-reading"]

TRIAGE_Q = {
    "type": "choice",
    "instructions": (
        "A compact extract of ONE failing run from a LabVIEW VI-scripting project is given as `log`: the script "
        "that ran, how the run ended (rc or TIMEOUT), the first failing gate line with its context, and the last "
        "lines of the run (uids and long numbers are replaced by '#'). Decide which ONE of the four classes the "
        "run's FIRST failure belongs to, so a judgement session knows who has to fix it. Judge the first failing "
        "gate or traceback, not the later consequences it caused."),
    "criteria": {
        "script-bug": (
            "Our own Python is at fault: a traceback, a name/import/format/type error, a wrong path, or a static "
            "checker of our recipes refusing them (a forbidden call, a %-format arity mismatch, a banned flag). "
            "The defect lives outside LabVIEW and is fixed by editing a .py file."),
        "address-invalid": (
            "An address into the VI does not resolve or resolves to the wrong thing: a uid with no Nodes[] index, "
            "diag_index returning None or raising, 'not found', a stale or missing index, an owner class that is "
            "not what the route assumed, or a write that landed on the wrong terminal. LabVIEW answered; the "
            "answer says the target could not be located as named."),
        "labview-refused": (
            "The machine declined or could not complete the edit: error 5001, ExecState reading 0 after a "
            "mutation, a save refused because the VI is broken, an op that returned without creating or changing "
            "anything, a property node error across a whole sweep, or a COM call that hung or hit the deadline."),
        "expected-reading": (
            "Nothing was blocked: the run reached its own summary and the failing gate is a designed reading, a "
            "declared discriminating arm, or a prediction about counts/names that the measurement refuted. The "
            "run produced the fact it existed to produce, and rc != 0 only records the refuted prediction."),
    },
}
