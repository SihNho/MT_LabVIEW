r"""errorlist_recheck_80 - card 80-4 E3: offline re-verdict of the saved cycle-80 Error List json with the patched
errorlist_check.compare (PD179(d) header licence). No LabVIEW: gates are taken from the saved json unchanged, licences
re-derived from its plan_file, expected file as saved (null -> []).

PREDICTION CONTRACT: 22 items; extra [] ; missing [] ; item 0 licensed 'header-of 1'; gates all true -> verdict OK.
"""
import copy, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
import errorlist_check as C                                                        # noqa: E402
import protocol                                                                     # noqa: E402

J = os.path.join(HERE, "errorlist_D1_k_20260925_100155_20260925_104258.json")


def main():
    d = json.load(open(J, encoding="utf-8"))
    items = copy.deepcopy(d["items"])
    for i in items:
        i.pop("licensed_by", None)
    plan = json.load(open(d["plan_file"], encoding="utf-8"))
    expected = json.load(open(d["expected_file"], encoding="utf-8")).get("expected", []) if d.get("expected_file") else []
    extra, missing, usage = C.compare(items, expected, C.derive_expected(plan))
    gates = d.get("gates") or {}
    read_ok = bool(gates) and all(gates.values())
    verdict = ("OK" if not (extra or missing) else "MISMATCH") if read_ok else "FAIL"
    print("saved verdict %s extra %r missing %r" % (d["verdict"], d["extra"], d["missing"]))
    print("gates %d/%d true: %s" % (sum(bool(v) for v in gates.values()), len(gates), sorted(gates)))
    for i in items:
        print("item %2s lic %-24s raw %r" % (i.get("index"), i.get("licensed_by"), (i.get("raw") or "")[:70]))
    print("usage: %s" % json.dumps(usage))
    print("RECHECK items %d extra %r missing %r -> verdict %s" % (len(items), extra, missing, verdict))
    ok = verdict == "OK" and items[0].get("licensed_by") == "header-of 1"
    print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1,
                                                    None if ok else "recheck verdict %s extra %r" % (verdict, extra),
                                                    [], status="PASS" if ok else "FAIL")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
