# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a1-1.md
# ---
r"""prep_c164_a1_1_cmp - card 164-a1-1 Part 2 (OFFLINE, json only): JSON compare plan_ring_p5s02r_in_pre164.json (d84634bd, byte copy) vs the edited
plan_ring_p5s02r_in.json. Ends are compared in the form the stage tools read them: stagexec._sym_of(end) (a 'new:X.inner' string and
{'uid':'new:X','side':'inner'} are the same end) plus every other dict key of the end. Raw leaf differences are printed as facts as well.
PREDICTION CONTRACT: same action count and ids; the normalised diff is exactly 4 added keys = A69 w_k3pass src/dst + A79 w_k4pass src/dst `frame`='True';
  the A33 w_gpass / A40 w_hpass / A52 w_c7_pass ends have the same key set {uid, side, frame} as the 4 edited ends; top-level keys equal.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a1_1_cmp.log -- py -u tools/bench/prep_c164_a1_1_cmp.py"""
import os, sys                                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    sys.path.insert(0, _p)
import stagexec as SX                                                                        # noqa: E402
import prep_c156_a1_1_lib as L                                                               # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
OLD, NEW = os.path.join(B, "plan_ring_p5s02r_in_pre164.json"), os.path.join(B, "plan_ring_p5s02r_in.json")
gate = L.Gate()
gate("PIN old copy md5 d84634bd", L.md5(OLD).startswith("d84634bd"), L.md5(OLD))
O, N = L.J(OLD), L.J(NEW)
print("FACT MD5 plan_ring_p5s02r_in.json {0} -> {1}".format(L.md5(OLD), L.md5(NEW)), flush=True)


def norm_end(e):
    """end -> dict of the keys the stage tools read: _sym_of pair (or the raw value) + every other key."""
    s = SX._sym_of(e)
    d = {"_sym": list(s) if s[0] else e} if not isinstance(e, dict) else dict(e, _sym=list(s) if s[0] else None)
    if isinstance(e, dict) and s[0]:
        d.pop("uid", None); d.pop("side", None); d.pop("term", None)                            # noqa: E702 - folded into _sym
    return d


def leaves(x, pre=""):
    if isinstance(x, dict):
        return dict(kv for k, v in x.items() for kv in leaves(v, pre + "/" + k).items())
    if isinstance(x, list):
        return dict(kv for i, v in enumerate(x) for kv in leaves(v, pre + "/" + str(i)).items())
    return {pre: x}


gate("TOP top-level keys and non-action content equal", dict((k, v) for k, v in O.items() if k != "actions") == dict((k, v) for k, v in N.items() if k != "actions"))
gate("IDS same action count and ids in order ({0})".format(len(O["actions"])), [a["id"] for a in O["actions"]] == [a["id"] for a in N["actions"]])
ADDED, OTHER = [], []
for i, (a, b) in enumerate(zip(O["actions"], N["actions"]), 1):
    lr, la = leaves(a), leaves(b)
    raw = sorted(k for k in set(lr) | set(la) if lr.get(k) != la.get(k))
    if raw:
        print("FACT RAW A{0} {1}: {2}".format(i, a["id"], [(k, lr.get(k), la.get(k)) for k in raw]), flush=True)
    na, nb = dict(a), dict(b)
    for s in ("src", "dst"):
        if s in na:
            na[s], nb[s] = norm_end(a[s]), norm_end(b[s])
    ln, lb = leaves(na), leaves(nb)
    for k in sorted(set(ln) | set(lb)):
        if ln.get(k) != lb.get(k):
            (ADDED if k not in ln and k.endswith("/frame") else OTHER).append(("A{0}".format(i), a["id"], k, ln.get(k), lb.get(k)))
print("FACT NORM added keys {0}".format(ADDED), flush=True)
print("FACT NORM other differences {0}".format(OTHER), flush=True)
want = [("A69", "w_k3pass", "/src/frame", None, "True"), ("A69", "w_k3pass", "/dst/frame", None, "True"),
        ("A79", "w_k4pass", "/src/frame", None, "True"), ("A79", "w_k4pass", "/dst/frame", None, "True")]
gate("CMP normalised diff == exactly the 4 added `frame`='True' keys on A69/A79 src+dst", sorted(ADDED) == sorted(want) and not OTHER, (ADDED, OTHER))
POS = dict((a["id"], a) for a in N["actions"])
lay = dict((x, sorted(POS[x][s].keys()) if isinstance(POS[x][s], dict) else None) for x in ("w_gpass", "w_hpass", "w_c7_pass", "w_k3pass", "w_k4pass") for s in ("src",))
lay.update(dict((x + ".dst", sorted(POS[x]["dst"].keys()) if isinstance(POS[x]["dst"], dict) else None) for x in ("w_gpass", "w_hpass", "w_c7_pass", "w_k3pass", "w_k4pass")))
print("FACT LAYOUT end key sets {0}".format(lay), flush=True)
gate("LAYOUT A69/A79 ends carry the A33/A40/A52 key layout {frame, side, uid}", len(set(map(str, lay.values()))) == 1, lay)
sys.exit(gate.result())
