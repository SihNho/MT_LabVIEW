# ---
# labview: none
# hardware: none
# ---
"""Card 159-a5-1: md5 of the files gen_capabilities / doc_lint may rewrite (docs/toolkit-capabilities.md,
tools/bench/capabilities_*) and of docs/fn_descriptions.json, plus `git status --short` for them - run before and after
the regeneration so the facts can name every tracked file the tools rewrote. Read-only. Prints a RESULT line."""
import glob
import hashlib
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

files = ["docs/toolkit-capabilities.md", "docs/fn_descriptions.json"] + sorted(
    os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, "tools", "bench", "capabilities_*"))) + sys.argv[1:]
for f in files:
    print("MD5 %s %s" % (hashlib.md5(open(os.path.join(ROOT, f), "rb").read()).hexdigest(), f))
print(subprocess.check_output(["git", "status", "--short", "--"] + files, cwd=ROOT).decode("utf-8", "replace"))
print(protocol.result_line(protocol.make_result(len(files), 0)))
