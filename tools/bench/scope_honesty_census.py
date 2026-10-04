# ---
# labview: none
# hardware: none
# ---
"""card chat-E3: census of the migrated scope headers - every tools script: header valid, honest, compiles (.py only;
the PowerShell parser is one process per file, so .ps1 parse is sampled by the self-test instead). OFFLINE, reads only.
PREDICTION: 0 invalid headers; 0 missing (except the 2 chat-A1 files, registry); honesty problems listed by kind."""
import collections
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol            # noqa: E402
import scope_header as S   # noqa: E402

c = collections.Counter()
rows = []
for p in S.tracked_scripts():
    rel = S._rel(p)
    h, err = S.read(p)
    if err:
        c["invalid"] += 1
        rows.append((rel, "INVALID " + err))
        continue
    if h is None:
        c["missing"] += 1
        rows.append((rel, "MISSING"))
        continue
    c["lv:" + h["labview"]] += 1
    if p.endswith(".py"):
        ce = S.compile_error(p)
        if ce:
            c["no-compile"] += 1
            rows.append((rel, "NO-COMPILE " + ce[:120]))
    try:
        hp = S.honesty(p, h)
    except Exception as e:     # noqa: BLE001
        hp = ["honesty crashed: %s" % e]
    for x in hp:
        c["honesty:" + x.split(" - ")[0][:70]] += 1
        rows.append((rel, "HONESTY " + x[:160]))
for k, v in sorted(c.items()):
    print("%5d  %s" % (v, k))
for r in rows:
    print("  %s | %s" % r)
bad = c["invalid"] + c["missing"] - 2
print(protocol.result_line(protocol.make_result(1 if bad <= 0 else 0, 0 if bad <= 0 else 1,
                                                None if bad <= 0 else "%d invalid/missing headers" % bad)))
