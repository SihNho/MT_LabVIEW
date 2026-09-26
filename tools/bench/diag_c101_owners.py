r"""diag_c101_owners - card 101-3, PD213(g)3/(h)(3): the S1 OWNERS MAP, built READ-ONLY from claudeDev\D1_s1_copy.vi
(md5 3e3d23ce...), replacing the D1_k stand-in (sim/l2a1/graph_k_80_owners.json, an inference: c100-6-jevgate2.md s1).
PRIOR ART (reused, not rebuilt): tools/bench/l2a1_facts_80.py:57-66 (the owner walk: every Diagram, then each structure owning
one, build_d1_v0.owner_of strict=False) - the routine that produced the stand-in on D1_k; the read-only shape of
diag_c100_6_maxmin.py (gscript direct, no stagekit Stage: this script edits nothing, so it is not a stage). The read runs on a
BYTE COPY claudeDev\D1_s1_disp_ownersread_<ts>.vi (same folder = same subVI links), deleted after LabVIEW is killed; the
input is never opened. No new op.
OUTPUT tools/bench/sim/disp/s1_owners.json {"vi","md5","owners":{uid:[owner class, owner uid]}} (stagesim.base_state's
context.owners format, key "owners").
PREDICTION: O1 every live Diagram uid gets an owner (class != '?'); O2 every Diagram of par1359_95_graph.json objs is in the
map; O3 bodies #639/#25392 are owned by WhileLoops; H input md5 unchanged, scratch deleted, LabVIEW gone. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c101_owners.log -- py -u tools/bench/diag_c101_owners.py"""
import hashlib, json, os, shutil, subprocess, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import bench_prep                                                                  # noqa: E402
import stagekit as K                                                               # noqa: E402  (K.mod only)
import vigraph as V                                                                # noqa: E402
S1_VI = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi")
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
SCR = os.path.join(g.CLAUDEDEV, "D1_s1_disp_ownersread_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "sim", "disp", "s1_owners.json")
BASE = json.load(open(os.path.join(HERE, "par1359_95_graph.json"), encoding="utf-8"))
STANDIN = json.load(open(os.path.join(HERE, "sim", "l2a1", "graph_k_80_owners.json"), encoding="utf-8"))["owners"]
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def walk(BD):
    diags = [int(d["uid"]) for d in g.report_all(SCR, "Diagram")]
    print("  FACT live Diagram objects: {0}".format(len(diags)), flush=True)
    O, todo, errs = {}, list(diags), []
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        try:
            v = BD.owner_of(SCR, u, strict=False)
        except Exception as e:                                                     # noqa: BLE001
            v = ("?", 0); errs.append((u, str(e)[:120]))                           # noqa: E702
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    return diags, O, errs


def main():
    m0 = md5(S1_VI)
    gate("K1 input md5 == S1 pin", m0 == S1_MD5, m0)
    shutil.copyfile(S1_VI, SCR)
    gate("K2 scratch is a byte copy", md5(SCR) == S1_MD5, SCR)
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        t0 = time.time(); diags, O, errs = walk(K.mod("build_d1_v0"))              # noqa: E702
        print("  FACT OWNERS {0} objects resolved in {1:.0f} s; errors {2}".format(len(O), time.time() - t0, errs[:5]), flush=True)
        gate("O1 every live Diagram uid has a resolved owner", all(O[d][0] != "?" for d in diags),
             sorted(d for d in diags if O[d][0] == "?")[:20])
        bdiag = sorted(int(o["uid"]) for o in BASE.get("objs") or [] if o.get("class") == "Diagram")
        gate("O2 every Diagram of the base graph objs ({0}) is in the map".format(len(bdiag)), set(bdiag) <= set(O),
             sorted(set(bdiag) - set(O))[:20])
        print("  FACT owners #639 {0}; #25392 {1}; #686 {2}; #7911 {3}; #27537 {4}".format(
            O.get(639), O.get(25392), O.get(686), O.get(7911), O.get(27537)), flush=True)
        gate("O3 bodies #639 and #25392 are owned by WhileLoops", O.get(639, ("?",))[0] == "WhileLoop" and
             O.get(25392, ("?",))[0] == "WhileLoop", (O.get(639), O.get(25392)))
        sk = set(int(x) for x in STANDIN)
        diff = sorted(k for k in set(O) & sk if list(O[k]) != [STANDIN[str(k)][0], int(STANDIN[str(k)][1] or 0)])
        print("  FACT vs D1_k stand-in: common {0}; differing {1}: {2}; S1-only {3}; stand-in-only {4}".format(
            len(set(O) & sk), len(diff), [(k, O[k], STANDIN[str(k)]) for k in diff[:12]], len(set(O) - sk), len(sk - set(O))), flush=True)
        json.dump({"vi": S1_VI, "md5": S1_MD5, "source": "tools/bench/diag_c101_owners.py (build_d1_v0.owner_of on a byte copy)",
                   "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}, open(OUT, "w", encoding="utf-8"), indent=0)
        print("  FACT WROTE {0} md5 {1} ({2} keys)".format(OUT, md5(OUT), len(O)), flush=True)
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        try:
            os.remove(SCR)
        except OSError as e:
            print("  FACT scratch not removed: {0}".format(e), flush=True)
        gate("H LabVIEW gone; input md5 unchanged; scratch deleted", gone and md5(S1_VI) == m0 and not os.path.exists(SCR),
             (gone, md5(S1_VI), os.path.exists(SCR)))
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=[{"path": OUT, "md5": md5(OUT)}] if os.path.exists(OUT) else [])), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
