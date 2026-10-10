# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-a2-1.md
# ---
r"""prep_c164_a2_1_cmp - card 164-a2-1 Part 2 (OFFLINE, json only), PD398(a): the edited plan_ring_p5s02r_in.json (A69 w_k3pass / A79 w_k4pass: src
`frame` dropped, dst `frame`='True' kept) compared both ways: (i) vs plan_ring_p5s02r_in_pre164.json d84634bd, (ii) vs plan_ring_p5s02r_in_both164.json
(byte copy of 4c8d3645). Ends are compared as the stage tools read them: stagexec._sym_of(end) plus every other key of the end (same normalisation as
prep_c164_a1_1_cmp.py:31-37 norm_end - that block is inline there; a shared copy would belong in prep_plan_flow_lib, outside this card's write globs);
leaves = prep_plan_flow_lib.leaves (called).
PREDICTION CONTRACT: pins d84634bd / 4c8d3645; top-level keys + action ids equal both ways; (i) exactly 2 ADDED keys A69/A79 /dst/frame='True', nothing else;
  (ii) exactly 2 REMOVED keys A69/A79 /src/frame='True', nothing else (raw leaves and normalised agree).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a2_1_cmp.log -- py -u tools/bench/prep_c164_a2_1_cmp.py"""
import os, sys                                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    sys.path.insert(0, _p)
import stagexec as SX                                                                        # noqa: E402
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5 = FL.L, FL.J, FL.md5
B = os.path.join(ROOT, "tools", "bench")
NEW, PRE, BOTH = (os.path.join(B, n) for n in ("plan_ring_p5s02r_in.json", "plan_ring_p5s02r_in_pre164.json", "plan_ring_p5s02r_in_both164.json"))
gate = L.Gate()
gate("PIN pre164 d84634bd, both164 4c8d3645", md5(PRE).startswith("d84634bd") and md5(BOTH).startswith("4c8d3645"), (md5(PRE), md5(BOTH)))
print("FACT MD5 plan_ring_p5s02r_in.json 4c8d3645 -> {0}".format(md5(NEW)), flush=True)


def norm_end(e):
    s = SX._sym_of(e)
    if not isinstance(e, dict):
        return {"_sym": list(s) if s[0] else e}
    d = dict(e, _sym=list(s) if s[0] else None)
    if s[0]:
        d.pop("uid", None); d.pop("side", None); d.pop("term", None)                            # noqa: E702
    return d


def diff(O, N, normalise):
    out = []
    for i, (a, b) in enumerate(zip(O["actions"], N["actions"]), 1):
        if normalise:
            a, b = dict(a), dict(b)
            for s in ("src", "dst"):
                if s in a:
                    a[s], b[s] = norm_end(a[s]), norm_end(b[s])
        la, lb = FL.leaves(a), FL.leaves(b)
        out += [("A{0}".format(i), a["id"], k, la.get(k), lb.get(k)) for k in sorted(set(la) | set(lb)) if la.get(k) != lb.get(k)]
    return out


N = J(NEW)
for nm, O, want in (("pre164", J(PRE), [("A69", "w_k3pass", "/dst/frame", None, "True"), ("A79", "w_k4pass", "/dst/frame", None, "True")]),
                    ("both164", J(BOTH), [("A69", "w_k3pass", "/src/frame", "True", None), ("A79", "w_k4pass", "/src/frame", "True", None)])):
    gate("TOP {0}: top-level non-action content equal".format(nm), dict((k, v) for k, v in O.items() if k != "actions") == dict((k, v) for k, v in N.items() if k != "actions"))
    gate("IDS {0}: same action ids in order ({1})".format(nm, len(O["actions"])), [a["id"] for a in O["actions"]] == [a["id"] for a in N["actions"]])
    raw, nrm = diff(O, N, False), diff(O, N, True)
    print("FACT RAW {0} -> new: {1}".format(nm, raw), flush=True)
    print("FACT NORM {0} -> new: {1}".format(nm, nrm), flush=True)
    gate("CMP {0} -> new: normalised diff == exactly {1}".format(nm, want), nrm == want, nrm)
    if nm == "both164":
        gate("RAW both164 -> new: raw leaf diff == the same 2 removed keys", raw == want, raw)
POS = dict((a["id"], a) for a in N["actions"])
print("FACT ENDS w_k3pass {0} -> {1}; w_k4pass {2} -> {3}".format(POS["w_k3pass"]["src"], POS["w_k3pass"]["dst"], POS["w_k4pass"]["src"], POS["w_k4pass"]["dst"]), flush=True)
sys.exit(gate.result())
