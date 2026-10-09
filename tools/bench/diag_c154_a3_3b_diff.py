# ---
# labview: none
# hardware: none
# ---
"""Card 154-a3-3b step 0: one-line diff of docs/violation-decisions.md vs git HEAD (git diff is not permitted here).
Prediction: HEAD md5 == 34da9f4f (card pin); exactly 1 changed line (1992), 07:0x -> 07:00."""
import difflib, hashlib, subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import protocol  # noqa: E402

P = "docs/violation-decisions.md"
root = Path(__file__).resolve().parents[2]
old_b = subprocess.run(["git", "show", "HEAD:" + P], capture_output=True, cwd=root).stdout
new_b = (root / P).read_bytes()
print("HEAD md5", hashlib.md5(old_b).hexdigest(), "disk md5", hashlib.md5(new_b).hexdigest())
old, new = old_b.decode("utf-8").splitlines(), new_b.decode("utf-8").splitlines()
d = list(difflib.unified_diff(old, new, "HEAD", "disk", lineterm="", n=0))
print("\n".join(d))
ch = [l for l in d if l[:1] in "+-" and not l.startswith(("+++", "---"))]
ok_head = hashlib.md5(old_b).hexdigest().startswith("34da9f4f")
ok_one = len(ch) == 2 and "07:0x" in ch[0] and "07:00" in ch[1] and ch[0].replace("07:0x", "07:00")[1:] == ch[1][1:]
print("changed lines", len(ch) // 2)
print(protocol.result_line({"status": "PASS" if ok_head and ok_one else "FAIL",
                            "gates": {"pass": ok_head + ok_one, "fail": 2 - ok_head - ok_one},
                            "first_fail": None if ok_head and ok_one else "diff"}))
