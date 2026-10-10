# ---
# labview: none
# hardware: none
# ---
"""Print md5 of each path given on argv (bytes only)."""
import hashlib, sys
for p in sys.argv[1:]:
    print(hashlib.md5(open(p, "rb").read()).hexdigest(), p)
