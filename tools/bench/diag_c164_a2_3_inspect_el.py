# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-3.md
# ---
"""diag_c164_a2_3_inspect_el - card 164-a2-3 (OFFLINE, read-only): print the 26d45c71 expected Error List rows compactly (item, class, count,
object, clears_by, label) and the 163 predicted file's top keys, so the step-4 EL maker is written against the real keys."""
import json, os, sys                                                                        # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(B)))
from tools import protocol  # noqa: E402
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
ex = J("errorlist_expected_D1_ring_p5s02c_20261010_125755.json")
print("EXP keys", [k for k in ex if k != "expected"])
print("EXP total", ex.get("total"), "bed", ex.get("bed"), "measured_from", ex.get("measured_from"), ex.get("measured_md5"))
for r in ex["expected"]:
    print("ROW", r.get("item"), r.get("class"), r.get("count"), json.dumps(r.get("object"))[:160], "CB", json.dumps(r.get("clears_by"))[:200],
          "|", str(r.get("label"))[:110], "| keys", sorted(r))
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
sys.exit(0)
