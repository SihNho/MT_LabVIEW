"""diag_c101c_peek - card 101-5: print the r5 record's per-op stagexec entries (which k carry a REAL read). No LabVIEW."""
import json, os, sys                                                                # noqa: E401
p = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "stage_d1_disp.json")
r = json.load(open(p, encoding="utf-8"))
print("stamp", r.get("stamp"), "task", r.get("task"))
for x in r.get("stagexec", []):
    d = x.get("diff")
    print(x.get("k"), x.get("op"), x.get("ids"), sorted(k for k in x if k not in ("k", "op", "ids", "diff", "acts")),
          None if d is None else {a: b for a, b in d.items() if b and a not in ("who",)})
