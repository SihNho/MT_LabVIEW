r"""diag_c100_6_maxmin - card 100-6 (ii), PD213(f)3: READ the terminal rows of the registered `Max & Min` donor node
(claudeDev\OpPrimDonor_v0.vi, uid from facts_c100_oplabels.json OpPrimCopyNested_v0.donors) with allterms.read_terms
(OpAllTerms_v1, the same reader stagexec's real backend uses). Read-only; the donor is a claudeDev byte copy (never
saved here). PRIOR ART: diag_c100_verbs_build4.log:7-9 found the node by label (uid 43, class 'Comparison') but
never read its terminals. PREDICTION: 4 terminal rows on the donor node, 2 sinks + 2 sources (gated); whether the
names equal plan_disp.json r7_max's x, y, max(x, y), min(x, y) and whether the class is the plan's 'Function' (the
donor registry says 'Comparison') is REPORTED as a fact - card 100-6 (ii) says read, then re-simulate if different. Writes tools/bench/facts_c100_maxmin.json. LabVIEW killed and verified gone at exit.
    py tools/bgrun.py --material --max-min 6 --log tools/bench/diag_c100_6_maxmin.log -- py -u tools/bench/diag_c100_6_maxmin.py"""
import hashlib, json, os, subprocess, sys, time                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import allterms as AT                                                              # noqa: E402
import bench_prep                                                                  # noqa: E402

LAB = json.load(open(os.path.join(HERE, "facts_c100_oplabels.json"), encoding="utf-8"))
REG = LAB["OpPrimCopyNested_v0"]["donors"]["Max & Min"]
PLAN = json.load(open(os.path.join(HERE, "sim", "disp", "plan_disp.json"), encoding="utf-8"))
WANT = next(a for a in PLAN["actions"] if a.get("id") == "r7_max")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    out = {"donor": REG["donor"], "uid": REG["uid"]}
    m0 = md5(REG["donor"])
    gate("D0 donor md5 == registry", m0 == REG["md5"], m0)
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        rows, _dt = AT.read_terms(REG["donor"], AT.OP_ALLTERMS_V1)
        mine = [r for r in rows if int(r["owner_uid"]) == int(REG["uid"])]
        out["rows"] = mine
        print("  FACT rows of #{0}: {1}".format(REG["uid"], mine), flush=True)
        # run 1 (this log's previous BGRUN block): OpAllTerms_v1 rows carry NO term_class key -> KeyError; compare
        # names + directions only. The contract is READ-then-report (card 100-6 (ii)): a difference is a FACT for the
        # re-simulation, not a failure of this reader.
        got = sorted((r["term_name"], bool(r["is_source"])) for r in mine)
        want = sorted((t["name"], bool(t["is_source"])) for t in WANT["terminals"])
        out["names"] = got
        out["names_match"] = got == want
        out["owner_class"] = sorted(set(r["owner_class"] for r in mine))
        gate("M1 four terminal rows of the donor node read (2 sinks, 2 sources)", len(mine) == 4
             and sum(1 for r in mine if r["is_source"]) == 2, got)
        print("  FACT names/directions == plan r7_max: {0} (read {1}, plan {2}); owner_class {3} (plan {4!r})".format(
            out["names_match"], got, want, out["owner_class"], WANT["class"]), flush=True)
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        gate("H LabVIEW gone at exit; donor bytes unchanged", gone and md5(REG["donor"]) == m0, gone)
    fp = os.path.join(HERE, "facts_c100_maxmin.json")
    json.dump(out, open(fp, "w", encoding="utf-8"), indent=1, default=str)
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
