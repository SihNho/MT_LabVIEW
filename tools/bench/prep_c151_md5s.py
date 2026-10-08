import hashlib, sys
for f in sys.argv[1:]:
    try:
        print(hashlib.md5(open(f, 'rb').read()).hexdigest(), f)
    except Exception:
        print('MISSING', f)
# ---
# labview: none
# hardware: none
# ---
