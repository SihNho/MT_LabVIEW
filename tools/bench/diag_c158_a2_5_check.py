# ---
# labview: none
# hardware: none
# ---
"""Card 158-a2-5 check: docs/fn_descriptions.json vs its git HEAD version - parses, count before/after, no old entry changed or
removed, added keys by module, every added key resolves to an existing function (gen_capabilities.stale_descriptions) and now
shows as 'side file' (described_rows). Prints facts and a RESULT line (protocol.result_line)."""
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gen_capabilities as g  # noqa: E402
import protocol  # noqa: E402

REL = "docs/fn_descriptions.json"
old = json.loads(subprocess.check_output(["git", "show", "HEAD:" + REL], cwd=ROOT).decode("utf-8"))["items"]
with open(os.path.join(ROOT, REL), encoding="utf-8") as f:
    new = json.load(f)["items"]
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail))


changed = [k for k in old if k in new and new[k] != old[k]]
removed = [k for k in old if k not in new]
added = [k for k in new if k not in old]
by_mod = {}
for k in added:
    m = k.split(".", 1)[0]
    by_mod[m] = by_mod.get(m, 0) + 1
print("COUNT before %d after %d added %d" % (len(old), len(new), len(added)))
print("ADDED BY MODULE %s" % json.dumps(by_mod, sort_keys=True))
gate("C1 no existing entry changed", not changed, changed[:5])
gate("C2 no existing entry removed", not removed, removed[:5])
gate("C3 about 60 added (50..75)", 50 <= len(added) <= 75, len(added))
stale = g.stale_descriptions(ROOT)
gate("C4 L12 clean for the new keys", not [k for k in stale if k in added], [k for k in stale if k in added])
print("STALE (all keys) %s" % stale)
side = set()
for p, note, users, rows in g.described_rows(ROOT):
    mod = p.rsplit("/", 1)[-1][:-3]
    for r in rows:
        if r[3] == "side file":
            side.add("%s.%s" % (mod, r[0]))
missing = [k for k in added if k not in side]
gate("C5 every added key shows as 'side file'", not missing, missing[:10])
gate("C6 one sentence-ish, <= 300 chars", all(len(new[k]) <= 300 for k in added), [k for k in added if len(new[k]) > 300])
n_pass = sum(1 for _l, ok in gates if ok)
first = next((l for l, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first)))
sys.exit(0 if first is None else 1)
