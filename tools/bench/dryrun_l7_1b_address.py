r"""dryrun_l7_1b_address - cycle 72 firefighter, retrospective-cycle71 F2a/F3 + Pre-decided 174: OFFLINE (no LabVIEW) dry run
of EVERY end the L7-1b recipe hands to `Stage.address`, taken from the recipe's ACTUAL decision record
(tools/bench/decision_l7_1b_body.json, the r2 record whose candidate ends carry `term_uid`) plus the init/tunnel RULE
rows and the four second-pass ends as the recipe builds them (stage_d1_l7_1b.py:79-96). The four readers `address`
calls are stubbed so that the NAME path succeeds on an UNWIRED terminal and the UID path can only succeed on a WIRED
one; which branch `address` took is read from its returned `how`. PREDICTION: every first-wiring end resolves by
NAME (how == 'node'); every verify end resolves by uid ONLY after the wire landed; r2's ends (#3934/#5683/#3954/#5782,
stage_d1_l7_1b_r2.log:41-45) no longer raise.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/dryrun_l7_1b_address.log -- py -u tools/bench/dryrun_l7_1b_address.py"""
import json, os, sys                                                               # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))                 # noqa: E731
REC = J(K.BENCH, "decision_l7_1b_body.json")
R2_UIDS = {3934, 5683, 3954, 5782}
STUB = {"rows": [], "all": []}


class _AT(object):
    @staticmethod
    def read_terms(_t):
        return STUB["all"], 0.0


def stage_for(end, is_source, wired, all_rows):
    """One stub layout per end: the end's node alone on its diagram, ONE terminal of the end's name and direction,
    wire 0 (unwired) or 777 (wired). `all_rows` = whole-VI terminal table the uid path reads."""
    STUB["rows"] = [{"i": 0, "name": end["term"], "is_source": bool(is_source), "wire": 777 if wired else 0}]
    STUB["all"] = all_rows
    K.g.report_all = lambda _t, _c: [{"i": 3, "uid": int(end["diagram"])}]
    K.g.node_labels = lambda _t, _d: [{"uid": int(end["uid"])}]
    K.g.node_terms_uid = lambda _t, _d, _n: (int(end["uid"]), STUB["rows"])


def main():
    ok, n = True, 0
    saved = dict((k, getattr(K.g, k)) for k in ("report_all", "node_labels", "node_terms_uid"))
    saved_mod = K.mod
    K.mod = lambda name: _AT if name == "allterms" else saved_mod(name)
    s = K.Stage.__new__(K.Stage)
    s.work = "stub.vi"
    ends = []
    for d in REC["decisions"]:                                                     # the 4 body rows, r2's actual ends
        ex = d["exec"]
        ends.append(("body {0} src".format(d["id"]), ex["src"], True))
        ends.append(("body {0} dst".format(d["id"]), ex["dst"], False))
    for iid, src, term_uid in (("err_init", 4910, 4911), ("acc_init", 781, 782)):     # rules rows as stage_d1_l7_1b.py:79-81
        ends.append(("rule {0} src".format(iid), {"uid": src, "term": "error out", "term_uid": term_uid, "diagram": 686}, True))
        ends.append(("rule {0} dst".format(iid), {"uid": 23041, "term": "total data array out", "diagram": 686}, False))
    for iid, old, sink in (("tun_cal", 3644, "cal cluster path"), ("tun_size", 2294, "file size"), ("tun_path", 5096, "selected path")):
        ends.append(("rule {0} dst".format(iid), {"uid": 376, "term": sink, "diagram": 23405}, False))
    try:
        seen_r2 = set()
        for label, end, is_src in ends:
            end = dict(end, owner_class="", term_class="")
            stage_for(end, is_src, wired=False, all_rows=[])                       # unwired terminal, empty uid table
            try:
                trip, how = s.address(end, is_src)
                good = trip == (3, 0, 0) and how == "node"
            except RuntimeError as e:
                trip, how, good = None, "RAISED " + str(e), False
            ok &= good
            n += 1
            if end.get("term_uid") in R2_UIDS:
                seen_r2.add(end["term_uid"])
            print("  {0}  D1 first wiring by NAME on an UNWIRED terminal: {1} term_uid={2!r} -> {3} {4!r}".format(
                "PASS" if good else "FAIL", label, end.get("term_uid"), trip, how), flush=True)
        good = seen_r2 == R2_UIDS
        ok &= good
        print("  {0}  D2 the four r2 ends (#3934/#5683/#3954/#5782) were among the first-wiring ends: {1}".format(
            "PASS" if good else "FAIL", sorted(seen_r2)), flush=True)
        for lab, u, t, dg, tu in (("err_L", 376, "error in", 23405, 5683), ("acc_L", 376, "total data array in", 23405, 5782),
                                  ("err_init", 23041, "", 686, 24140), ("acc_init", 23041, "", 686, 24190)):
            end = {"uid": u, "term": t, "verify_term_uid": tu, "diagram": dg, "owner_class": "", "term_class": ""}  # recipe :96
            stage_for(dict(end, term="renamed after wiring"), False, wired=True,
                      all_rows=[{"term_uid": tu, "term_name": "", "is_source": False, "wire_uid": 777, "owner_uid": u}])
            try:
                trip, how = s.address(end, False)
                good = trip == (3, 0, 0) and "uid #{0}".format(tu) in how
            except RuntimeError as e:
                trip, how, good = None, "RAISED " + str(e), False
            ok &= good
            print("  {0}  D3 second pass {1} by verify_term_uid #{2} after the wire landed + rename: {3} {4!r}".format(
                "PASS" if good else "FAIL", lab, tu, trip, how), flush=True)
            stage_for(end, False, wired=False, all_rows=[{"term_uid": tu, "term_name": t, "is_source": False, "wire_uid": 0, "owner_uid": u}])
            try:
                s.address(end, False)
                good, how = False, "no raise"
            except RuntimeError as e:
                good, how = "wired" in str(e), str(e)
            ok &= good
            print("  {0}  D4 second pass {1} on an UNWIRED terminal RAISES (no name fallback, PD174(b) rejected): {2!r}".format(
                "PASS" if good else "FAIL", lab, how), flush=True)
    finally:
        for k, v in saved.items():
            setattr(K.g, k, v)
        K.mod = saved_mod
    print("=== GATES: {0} ends dry-run; overall {1}".format(n, "PASS" if ok else "FAIL"), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
