r"""dryrun_l7_r_address - cycle 73: OFFLINE (no LabVIEW) dry run of EVERY end tools/recipes/stage_d1_l7_r.py hands to `Stage.address`
(through the recipe's own `at()`), on the MEASURED terminal tables of the input (tools/bench/c73_l7r_live.log NODETERMS lines, parsed, not
retyped), with the recipe's deletes applied (the P["del_w"] wires set to 0). Template: dryrun_l7_1b_address.py (same stubs).
PREDICTION: every first-wiring end resolves BY NAME to the index listed below; #2048 'length' needs the tie-break (plain `address` raises on the
two unwired 'length' sinks) and resolves to Terminals[3]; the tie-break REFUSES while Terminals[3] is still wired; every verify end in
P["second"] resolves by verify_term_uid only once its wire exists and raises while unwired.
    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/dryrun_l7_r_address.log -- py -u tools/bench/dryrun_l7_r_address.py"""
import ast, os, re, sys                                                            # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K                                                               # noqa: E402
import stage_d1_l7_r as R                                                          # noqa: E402
LOG = open(os.path.join(K.BENCH, "c73_l7r_live.log"), encoding="utf-8", errors="replace").read()
ROWS = {}
for dg, u, body in re.findall(r"NODETERMS D#(\d+) #(\d+) echo \d+: (\[.*\])", LOG):
    ROWS[int(u)] = (int(dg), [{"i": i, "name": n, "is_source": s_, "wire": 0 if w in R.P["del_w"] else w} for i, n, s_, w in ast.literal_eval(body)])
ROWS[3052] = (23405, ROWS[3052][1])                                                # the recipe moves #3052 into #23405 before it wires it
DIAG = {686: 19, 23405: 20}
ALL = {"rows": []}


class _AT(object):
    @staticmethod
    def read_terms(_t):
        return ALL["rows"], 0.0


def install():
    K.g.report_all = lambda _t, _c: [{"i": i, "uid": u} for u, i in DIAG.items()]
    K.g.node_labels = lambda _t, di: [{"uid": u} for u, (dg, _r) in sorted(ROWS.items()) if DIAG[dg] == di]
    K.g.node_terms_uid = lambda _t, di, ni: (K.g.node_labels(_t, di)[ni]["uid"], ROWS[K.g.node_labels(_t, di)[ni]["uid"]][1])
    R.g.report_all, R.g.node_labels, R.g.node_terms_uid = K.g.report_all, K.g.node_labels, K.g.node_terms_uid


def main():
    saved = dict((k, getattr(K.g, k)) for k in ("report_all", "node_labels", "node_terms_uid")); saved_mod = K.mod  # noqa: E702
    K.mod = lambda name: _AT if name == "allterms" else saved_mod(name)
    s = K.Stage.__new__(K.Stage); s.work, s.passes, s.fails, s.facts = "stub.vi", [], [], []  # noqa: E702
    ok, n = True, 0
    try:
        install()
        for dg, u, name, src, want in ((686, 23041, "", True, 3), (686, 23041, "error out", True, 1), (686, 2048, "array", False, 0),
                                       (686, 6384, "error in", False, 8), (23405, 376, "file progress", True, 3), (686, 2048, "length", False, 3),
                                       (686, 6384, "actual # data points", False, 7), (23405, 376, "file number to append out", True, 4),
                                       (686, 6384, "file # to append", False, 10), (23405, 3052, "File # Saved", True, 0), (23405, 376, "saved file refnum", False, 8)):
            try:
                got = R.at(s, dg, u, name, src); good = got == (DIAG[dg], [x for x, (d, _r) in sorted(ROWS.items()) if d == dg].index(u), want)  # noqa: E702
            except Exception as e:                                                 # noqa: BLE001
                got, good = "RAISED {0}: {1}".format(type(e).__name__, e), False
            ok &= good; n += 1                                                     # noqa: E702
            print("  {0}  D1 first wiring BY NAME {1} #{2} {3!r} ({4}) -> {5} (want Terminals[{6}])".format("PASS" if good else "FAIL", dg, u, name, "src" if src else "sink", got, want), flush=True)
        try:
            s.address({"uid": 2048, "term": "length", "diagram": 686, "owner_class": "", "term_class": ""}, False); good = False  # noqa: E702
        except RuntimeError as e:
            good = "2 matches" in str(e)
        ok &= good
        print("  {0}  D2 plain `address` RAISES on #2048's two unwired 'length' sinks (the tie-break is needed)".format("PASS" if good else "FAIL"), flush=True)
        ROWS[2048][1][3]["wire"] = 4337                                            # EXPECTED refusal: a silent gate stub, so no FAIL token is printed
        fired = []                                                                 # review c73-l7r-dryrun-negtest test 1: record, then attribute
        s.gate = lambda label, ok_, detail="", fatal=False: fired.append((label, ok_, detail)) or ok_ or (_ for _ in ()).throw(K.Stop(label))
        try:
            R.at(s, 686, 2048, "length", False); good = False                      # noqa: E702
        except K.Stop:
            good = len(fired) == 1 and not fired[0][1] and fired[0][2].get("wire") == 4337 and fired[0][2].get("name") == "length" and fired[0][2].get("is_source") is False
        del s.gate; ROWS[2048][1][3]["wire"] = 0; ok &= good                       # noqa: E702
        print("  {0}  D3 the tie-break REFUSES (Stop) while Terminals[3] still carries w4337; exactly one gate fired, detail {1}".format("PASS" if good else "FAIL", fired), flush=True)
        for lab, _srcs, u, t, tu in R.P["second"]:
            dg, rows = ROWS[u]; ti = [r["i"] for r in rows if r["name"] == t and not r["is_source"]][0 if (u, t) != (2048, "length") else 0]
            end = {"uid": u, "term": t, "verify_term_uid": tu, "diagram": dg, "owner_class": "", "term_class": ""}
            ALL["rows"] = [{"term_uid": tu, "term_name": "", "is_source": False, "wire_uid": 0, "owner_uid": u}]
            try:
                s.address(end, False); g0 = False                                  # noqa: E702
            except RuntimeError:
                g0 = True
            rows[ti]["wire"] = 900 + ti; ALL["rows"][0]["wire_uid"] = 900 + ti     # noqa: E702
            try:
                trip, how = s.address(end, False); g1 = trip[2] == ti and "uid #{0}".format(tu) in how  # noqa: E702
            except RuntimeError as e:
                trip, how, g1 = None, str(e), False
            rows[ti]["wire"] = 0; ok &= g0 and g1                                  # noqa: E702
            print("  {0}  D4 verify end {1} #{2} {3!r} by verify_term_uid #{4}: raises unwired {5}; after the wire -> Terminals[{6}] {7!r}".format(
                "PASS" if g0 and g1 else "FAIL", lab, u, t, tu, g0, ti, how), flush=True)
    finally:
        for k, v in saved.items():
            setattr(K.g, k, v)
        K.mod = saved_mod
    print("=== GATES: {0} first-wiring ends + D2/D3 + {1} verify ends; overall {2}".format(n, len(R.P["second"]), "PASS" if ok else "FAIL"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
