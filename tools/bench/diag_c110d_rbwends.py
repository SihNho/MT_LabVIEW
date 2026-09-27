"""Card 110-4 L4 prep: OFFLINE (no LabVIEW) classification of the wires Remove Bad Wires deleted on a scratch of the saved
L2-B1 file, from the stage log's own `RBW ENDS` fact (tools/recipes/stage_d1_l2b1.py:109, the pre-save whole-VI read).
PRIOR ART: the L2-A3 attribution used the same four classes by hand (errorlist_expected_D1_l2_a3_20260927_151224.json
"attribution": 13 source-only / 9 termless / 3 sink-only / 2 SubVI-sink + SelectorTunnel); this file only counts them.
PREDICTION CONTRACT:
  G1 the log holds exactly one RBW ENDS fact and one RBW deleted list, with the same wire set
  G2 every deleted wire falls in exactly one class (termless / source-only / sink-only / multi-source / src+sink)
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c110d_rbwends.log -- py -u tools/bench/diag_c110d_rbwends.py"""
import ast, collections, os, sys                                                    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                     # noqa: E402
LOG = os.path.join(ROOT, "tools", "bench", "stage_d1_l2b1_c110d.log")
gates = {}


def gate(k, ok, msg):
    gates[k] = bool(ok)
    print("%s  %s  %s" % ("PASS" if ok else "FAIL", k, str(msg)[:600]), flush=True)


lines = open(LOG, encoding="utf-8", errors="replace").read().splitlines()
ends_l = [ln for ln in lines if "FACT  RBW ENDS" in ln]
del_l = [ln for ln in lines if "FACT  RBW deleted" in ln]
d = ast.literal_eval(ends_l[0][ends_l[0].index("{"):]) if ends_l else {}
dl = ast.literal_eval(del_l[0][del_l[0].index("["):]) if del_l else []
gate("G1_one_fact_same_set", len(ends_l) == 1 and len(del_l) == 1 and sorted(d) == sorted(dl), (len(ends_l), len(del_l), len(d), len(dl)))
cls = collections.defaultdict(list)
for w, ends in sorted(d.items()):
    src, snk = [e for e in ends if e[3]], [e for e in ends if not e[3]]
    k = ("termless" if not ends else "source-only" if not snk else "sink-only" if not src
         else "multi-source" if len(src) > 1 else "src+sink")
    cls[k].append(w)
    print("WIRE %6d %-12s %s" % (w, k, ends), flush=True)
for k, v in sorted(cls.items()):
    print("CLASS %-12s %3d %s" % (k, len(v), v), flush=True)
gate("G2_every_wire_one_class", sum(len(v) for v in cls.values()) == len(d), {k: len(v) for k, v in cls.items()})
n_pass = sum(1 for x in gates.values() if x); n_fail = len(gates) - n_pass           # noqa: E702
first = next((k for k, x in gates.items() if not x), None)
print("=== GATES: %d pass / %d fail%s" % (n_pass, n_fail, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, [])))
sys.exit(0 if n_fail == 0 else 1)
