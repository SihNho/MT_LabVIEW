"""Self-test of card 118-4 A1 (PD234(j)(2)): gscript.create_primitive_nested's one-node rule, relaxed ONLY for an
ArrayConstant donor to exactly {one new ArrayConstant, one object owned by it}. No LabVIEW: every COM-touching helper of
gscript and build_d1_v0.owner_of are stubbed; the decision code under test is the real one.
PREDICTION (8 gates): T1 array donor + {arr, elem owned by arr} -> returns arr; T2 elem owned elsewhere -> refused;
T3 NON-array donor with 2 new -> refused (one-node rule kept); T4 non-array donor, 1 new -> returned; T5 array donor, 3 new
-> refused; T6 array donor, 2 new, none an ArrayConstant -> refused; T7 array pair but the array is not on the diagram ->
refused; T8 array donor with exactly 1 new (a plain copy) -> returned (the one-node path is unchanged).
Usage: py tools/bench/selftest_c118_primnested.py"""
import os
import sys
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
import gscript as g  # noqa: E402

TGT, D = os.path.join(g.CLAUDEDEV, "scratch_c118_selftest.vi"), 13236
DONOR = os.path.join(g.CLAUDEDEV, "OpPoolDonor_v0.vi")
LAB = {"DonorUIDin": "uid in", "position": "position", "duplicate": "duplicate", "DonorUID": "UID d", "DiagUID": "UID g",
       "Err": "error out", "controls": [], "donors": {}}
S = {}


class VI(object):
    def SetControlValue(self, k, v):
        pass

    def GetControlValue(self, k):
        return {"UID d": S["donor_uid"], "UID g": D}.get(k)


def uids(path, cls):
    if path == DONOR:
        return set(S["donor_arrays"]) if cls == "ArrayConstant" else set()
    if cls == "Node":
        return set(S["new"]) if S["ran"] else set()
    if cls == "ArrayConstant":
        return set(S["arrays"]) if S["ran"] else set()
    return set()


g._c100 = lambda key: LAB
g.ensure_loaded = lambda t: None
g._uid_index = lambda t, c, u: 0
g.uids = uids
g.op = lambda p: VI()
g._run = lambda vi, *a, **k: S.__setitem__("ran", True)
g._err = lambda vi, k: ""
g._c97_paths = lambda: None
sys.modules["build_d1_v0"] = types.SimpleNamespace(owner_of=lambda t, u, strict=True: S["owners"].get(int(u), ("?", 0)))


def case(new, arrays, owners, donor_is_array=True):
    S.update(ran=False, new=new, arrays=arrays, owners=owners, donor_uid=101, donor_arrays=[101] if donor_is_array else [])
    try:
        return g.create_primitive_nested(TGT, D, "pool_names", (0, 0), donor={"donor": DONOR, "uid": 101})
    except RuntimeError as e:
        return "REFUSED " + str(e)


gates = []


def gate(label, ok, detail):
    gates.append(bool(ok))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:220]), flush=True)


r = case([500, 501], [500], {500: ("Diagram", D), 501: ("ArrayConstant", 500)})
gate("T1 array donor + {ArrayConstant 500, element 501 owned by it} -> 500", r == 500, r)
r = case([500, 501], [500], {500: ("Diagram", D), 501: ("Diagram", D)})
gate("T2 element NOT owned by the new array -> refused", str(r).startswith("REFUSED") and "not ArrayConstant #500" in r, r)
r = case([500, 501], [500], {500: ("Diagram", D), 501: ("ArrayConstant", 500)}, donor_is_array=False)
gate("T3 non-ArrayConstant donor, 2 new -> refused (one-node rule kept)", str(r).startswith("REFUSED") and "2 new Node(s)" in r, r)
r = case([600], [], {600: ("Diagram", D)}, donor_is_array=False)
gate("T4 non-ArrayConstant donor, 1 new on the diagram -> 600", r == 600, r)
r = case([500, 501, 502], [500], {500: ("Diagram", D), 501: ("ArrayConstant", 500), 502: ("ArrayConstant", 500)})
gate("T5 array donor, 3 new -> refused", str(r).startswith("REFUSED") and "3 new Node(s)" in r, r)
r = case([500, 501], [], {500: ("Diagram", D), 501: ("ArrayConstant", 500)})
gate("T6 array donor, 2 new but no new ArrayConstant -> refused", str(r).startswith("REFUSED") and "0 of the new" in r, r)
r = case([500, 501], [500], {500: ("Diagram", 999), 501: ("ArrayConstant", 500)})
gate("T7 array pair whose array is NOT on Diagram #13236 -> refused", str(r).startswith("REFUSED") and "not Diagram #13236" in r, r)
r = case([500], [500], {500: ("Diagram", D)})
gate("T8 array donor, exactly 1 new -> 500 (one-node path unchanged)", r == 500, r)

bad = [i for i, ok in enumerate(gates, 1) if not ok]
print("=== GATES: %d pass / %d fail" % (len(gates) - len(bad), len(bad)), flush=True)
print(protocol.result_line(protocol.make_result(len(gates) - len(bad), len(bad), ("T%d" % bad[0]) if bad else None, [])), flush=True)
sys.exit(1 if bad else 0)
