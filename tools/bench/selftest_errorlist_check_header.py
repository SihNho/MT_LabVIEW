r"""selftest_errorlist_check_header - card 80-4 (plan PD179(d)): the empty-raw tree-header licence in
tools/errorlist_check.py `compare` -> `license_headers`. No LabVIEW: items come from the saved cycle-80 json.
Existing tests checked first: selftest_errorlist_retry.py covers cycle_runner's retry only; nothing exercised compare().

PREDICTION CONTRACT (5 cases, licences derived from plan_k_split.json exactly as main() does):
  P1 items 0+1 of the cycle-80 json            -> extra [] ; item 0 licensed_by 'header-of 1'
  N1 same header + an UNLICENSED next item     -> extra == ['', <next raw>]
  N2 header + licensed next, DIFFERENT detail  -> extra == ['']
  N3 header as the LAST item                   -> extra == ['']
  N4 two empty headers in a row + item 1       -> extra == [''] (only the one directly above item 1)
"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import errorlist_check as C                                                        # noqa: E402
import protocol                                                                     # noqa: E402

J = os.path.join(HERE, "errorlist_D1_k_20260925_100155_20260925_104258.json")


def clean(items):
    out = copy.deepcopy(items)
    for i in out:
        i.pop("licensed_by", None)
    return out


def main():
    d = json.load(open(J, encoding="utf-8"))
    plan = json.load(open(d["plan_file"], encoding="utf-8"))
    derived = C.derive_expected(plan)
    h, one = clean(d["items"][:2])
    bad = dict(one, index=1, raw="Frobnicate 'X': something unlicensed", object="Frobnicate 'X'",
               reason="something unlicensed")
    other_det = dict(h, detail="One or more required inputs to this function are not wired or are wired incorrectly.")
    h2 = dict(h, index=0)
    cases = {
        "P1": ([h, one], [], (0, "header-of 1")),
        "N1": ([h, bad], ["", bad["raw"]], (0, None)),
        "N2": ([other_det, one], [""], (0, None)),
        "N3": ([one, dict(h, index=2)], [""], (1, None)),
        "N4": ([h2, dict(h, index=1), dict(one, index=2)], [""], (1, "header-of 2")),
    }
    npass = nfail = 0
    first = None
    for k, (items, want, (pos, lic)) in cases.items():
        items = clean(items)
        extra, missing, usage = C.compare(items, [], derived)
        got_lic = items[pos].get("licensed_by")
        ok = extra == want and missing == [] and got_lic == lic
        print("%s %s: extra %r missing %r item[%d].licensed_by %r (want extra %r lic %r) header_of used %s" % (
            "PASS" if ok else "FAIL", k, extra, missing, pos, got_lic, want, lic, usage[-1]["used"]), flush=True)
        npass += ok
        nfail += not ok
        first = first or (None if ok else k)
    print("%d/%d PASS" % (npass, npass + nfail))
    print(protocol.result_line(protocol.make_result(npass, nfail, first, [],
                                                    status="PASS" if not nfail else "FAIL")))
    return 0 if not nfail else 1


if __name__ == "__main__":
    sys.exit(main())
