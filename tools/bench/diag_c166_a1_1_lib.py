# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c164_a3_7_write.py
# ---
"""diag_c166_a1_1_lib - card 166-a1-1: the ONE JSON rewrite helper both diag_c166_a1_1_mm.py and diag_c166_a1_1_census.py call
(no copy in either). Its serialisation rule is the one of tools/bench/prep_c164_a3_7_write.py:53-59 (`dumps`), which is an inline
helper of a script that runs on import, so it cannot be called; moving it into tools/stagekit.py is outside this card's write globs
(reported under `open`, docs/script-writing.md rule 4). Self-test: `py tools/bench/diag_c166_a1_1_lib.py` round-trips
memory_model.json and plan_ring_p5s02e_pred.json byte-exactly without writing anything.
Card 167-a1-5 (PD404 note (2)): the four helpers now live ONCE in tools/stagekit.py (json_text_like, json_newline_of, rewrite_json,
json_changed_keys; self-test stagekit.rewrite_json_selftest); the names below are kept so diag_c166_a1_1_mm.py / _census.py call them
unchanged."""
import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")), "tools"))
import stagekit as _K  # noqa: E402

text_like = _K.json_text_like
newline_of = _K.json_newline_of
rewrite_json = _K.rewrite_json
changed_keys = _K.json_changed_keys


if __name__ == "__main__":
    import sys
    root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
    sys.path.insert(0, os.path.join(root, "tools"))
    import protocol as PR
    bad = []
    for rel in ("tools/bench/memory_model.json", "tools/bench/plan_ring_p5s02e_pred.json"):
        p = os.path.join(root, rel)
        raw = open(p, "rb").read()
        old = raw.decode("utf-8")
        t = text_like(json.loads(old), old)
        ok = t is not None and t.replace("\n", newline_of(p)).encode("utf-8") == raw
        print("SELFTEST {0} round-trip {1} (newline {2!r})".format(rel, "OK" if ok else "FAIL", newline_of(p)), flush=True)
        ok or bad.append(rel)                                                                  # noqa: E701
    print(PR.result_line({"status": "FAIL" if bad else "PASS", "gates": {"pass": 2 - len(bad), "fail": len(bad)},
                          "first_fail": bad[0] if bad else None, "artefacts": []}), flush=True)
    sys.exit(1 if bad else 0)
