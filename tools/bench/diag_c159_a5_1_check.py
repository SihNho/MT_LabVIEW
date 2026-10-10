# ---
# labview: none
# hardware: none
# ---
"""Card 159-a5-1 check: docs/fn_descriptions.json after the edit vs (a) the card-pinned input (md5 c54377ea, rebuilt by cutting
the appended block out of the current text - proves the old bytes are untouched) and (b) git HEAD. Gates: parses, ~60 added,
no old entry changed/removed, no stagekit/stage_prerun key added, L12 clean (gen_capabilities.stale_descriptions), every new key
shows as 'side file' (described_rows), each <= 300 chars. Same checks as tools/bench/diag_c158_a2_5_check.py (hard-wired to
HEAD there), plus the pinned-bytes baseline. Prints facts and a RESULT line (protocol.result_line)."""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gen_capabilities as g  # noqa: E402
import protocol  # noqa: E402

REL = "docs/fn_descriptions.json"
PIN = "c54377eabbdbb8afa79e4e4c1ec42206"
FIRST_NEW = '  "stagexec.Addr.snap_loop"'
raw = open(os.path.join(ROOT, REL), "rb").read()
txt = raw.decode("utf-8")
i = txt.index(",\n" + FIRST_NEW) if ",\n" + FIRST_NEW in txt else txt.index(",\r\n" + FIRST_NEW)
j = txt.rindex("\n }")
if txt[j - 1] == "\r":
    j -= 1
pinned_txt = txt[:i] + txt[j:]
pin_md5 = hashlib.md5(pinned_txt.encode("utf-8")).hexdigest()
old = json.loads(pinned_txt)["items"]
head = json.loads(subprocess.check_output(["git", "show", "HEAD:" + REL], cwd=ROOT).decode("utf-8"))["items"]
new = json.loads(txt)["items"]
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail))


print("MD5 after %s ; rebuilt pinned %s (card pin %s)" % (hashlib.md5(raw).hexdigest(), pin_md5, PIN))
gate("C0 rebuilt pre-edit bytes == card pin", pin_md5 == PIN, pin_md5)
changed = [k for k in old if k in new and new[k] != old[k]]
removed = [k for k in old if k not in new]
added = [k for k in new if k not in old]
h_changed = [k for k in head if k in new and new[k] != head[k]]
h_removed = [k for k in head if k not in new]
by_mod = {}
for k in added:
    m = k.split(".", 1)[0]
    by_mod[m] = by_mod.get(m, 0) + 1
print("COUNT head %d pinned %d after %d added %d" % (len(head), len(old), len(new), len(added)))
print("ADDED BY MODULE %s" % json.dumps(by_mod, sort_keys=True))
gate("C1 no pinned entry changed", not changed, changed[:5])
gate("C2 no pinned entry removed", not removed, removed[:5])
gate("C1h no HEAD entry changed or removed", not h_changed and not h_removed, (h_changed[:5], h_removed[:5]))
gate("C3 about 60 added (50..75)", 50 <= len(added) <= 75, len(added))
gate("C3b none for stagekit / stage_prerun", not [k for k in added if k.split(".")[0] in ("stagekit", "stage_prerun")])
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
gate("C6 <= 300 chars", all(len(new[k]) <= 300 for k in added), [(k, len(new[k])) for k in added if len(new[k]) > 300])
print("LONGEST %s" % sorted(((len(new[k]), k) for k in added), reverse=True)[:3])
n_pass = sum(1 for _l, ok in gates if ok)
first = next((l for l, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first)))
sys.exit(0 if first is None else 1)
