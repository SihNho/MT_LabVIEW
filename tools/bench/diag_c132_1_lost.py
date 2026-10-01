r"""diag_c132_1_lost - card 132-1 step C0 (offline, read-only): for a simulated stage (argv[1] = tools/bench/sim/<stage>), the wires
of step_00 absent from the last step (LOST = retired) with their base terminal profile (sources/sinks, owners), and the one-sided
wires (stubs) of base and end. Measures what a computed Error-List debit could be keyed on; decides nothing."""
import collections, glob, json, os, sys                                            # noqa: E401
d = sys.argv[1]
fs = sorted(glob.glob(os.path.join(d, "step_*.json")))
st = lambda f: json.load(open(f, encoding="utf-8"))["state"]["terminals"]           # noqa: E731


def prof(terms):
    w = collections.defaultdict(lambda: [0, 0, []])
    for t in terms:
        wu = t.get("wire_uid")
        if wu in (None, 0, -1):
            continue
        w[wu][0 if t.get("is_source") else 1] += 1
        w[wu][2].append((t["term_uid"], t["term_name"], t["owner_uid"], t["owner_class"], bool(t["is_source"])))
    return w


b, e = prof(st(fs[0])), prof(st(fs[-1]))
lost = sorted(set(b) - set(e))
print("BASE {0} wires {1} stubs {2}; END {3} wires {4} stubs {5}".format(os.path.basename(fs[0]), len(b),
      sorted(k for k, v in b.items() if not v[0] or not v[1]), os.path.basename(fs[-1]), len(e),
      sorted(k for k, v in e.items() if not v[0] or not v[1])))
for k in lost:
    print("LOST w{0} src/snk {1}/{2} terms {3}".format(k, b[k][0], b[k][1], b[k][2][:6]))
for k in sorted(set(e) - set(b)):
    if not e[k][0] or not e[k][1]:
        print("NEWSTUB w{0} src/snk {1}/{2} terms {3}".format(k, e[k][0], e[k][1], e[k][2][:4]))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
