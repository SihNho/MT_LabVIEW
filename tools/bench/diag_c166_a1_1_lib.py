# ---
# labview: none
# hardware: none
# evidence: tools/bench/prep_c164_a3_7_write.py
# ---
"""diag_c166_a1_1_lib - card 166-a1-1: the ONE JSON rewrite helper both diag_c166_a1_1_mm.py and diag_c166_a1_1_census.py call
(no copy in either). Its serialisation rule is the one of tools/bench/prep_c164_a3_7_write.py:53-59 (`dumps`), which is an inline
helper of a script that runs on import, so it cannot be called; moving it into tools/stagekit.py is outside this card's write globs
(reported under `open`, docs/script-writing.md rule 4). Self-test: `py tools/bench/diag_c166_a1_1_lib.py` round-trips
memory_model.json and plan_ring_p5s02e_pred.json byte-exactly without writing anything."""
import json
import os
import shutil


def text_like(obj, old_text):
    """The serialisation of `obj` that reproduces the byte layout of `old_text` (indent 1, ascii or not, trailing newline or not),
    or None when no candidate round-trips old_text exactly. Newlines are '\\n' (the caller writes with the file's own ending)."""
    t = old_text.replace("\r\n", "\n")
    for kw in ({"indent": 1}, {"indent": 1, "ensure_ascii": False}):
        for tail in ("", "\n"):
            if json.dumps(json.loads(t), **kw) + tail == t:
                return json.dumps(obj, **kw) + tail
    return None


def newline_of(path):
    return "\r\n" if b"\r\n" in open(path, "rb").read() else "\n"


def rewrite_json(path, obj, backup):
    """Copy `path` to `backup`, then write `obj` in the old file's layout and line ending. Returns (written, old_obj).
    Writes nothing (written False) when the layout cannot be reproduced."""
    old = open(path, encoding="utf-8", newline="").read()
    nl = newline_of(path)
    t = text_like(obj, old)
    if t is None:
        return False, json.loads(old)
    shutil.copyfile(path, backup)
    with open(path, "w", encoding="utf-8", newline=nl) as f:
        f.write(t)
    return True, json.loads(old)


def changed_keys(a, b):
    """Top-level keys whose values differ between two dicts."""
    return sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))


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
