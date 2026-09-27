r"""diag_c108d_graph - card 108-4 V2 prerequisite: the GRAPH JSON of the scratch-verify fixture claudeDev\TRACK_kernel_v1.vi,
READ-ONLY, so `stage_prerun --dry/--prerun --graph` can check tools/bench/diag_c108d_selind.py offline (review
archive/peer/2026-09-27-c108d-selind-dry.md s1: find_graph needs a graph JSON of the fixture's md5).
PRIOR ART (copied, not rebuilt): tools/bench/diag_c108b_graph.py / diag_c107b_bedgraph.py - wiki_build.read_live on a byte copy in
claudeDev, kill LabVIEW, delete the copy. No flat sequence in the fixture, so fs_pairs = [] (read_live reuses it). No VI is run.
OUTPUT tools/bench/diag_c108d_graph_track.json {vi, md5 = the fixture's, terminals, objs, fs_tunnel_pairs}.
PREDICTION: K fixture md5 read, byte copy equal, no LabVIEW before; L >=1 terminal row, >=1 SelectorTunnel OuterTerminal SOURCE
row, 1 CaseStructure obj; H LabVIEW gone, fixture md5 unchanged, copy deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c108d_graph.log -- py -u tools/bench/diag_c108d_graph.py"""
import hashlib, json, os, subprocess, shutil, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K                      # noqa: E401,E402
FIX = os.path.join(g.CLAUDEDEV, "TRACK_kernel_v1.vi")
SCR = os.path.join(g.CLAUDEDEV, "scratch_c108d_graph_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "diag_c108d_graph_track.json")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def main():
    m0 = md5(FIX)
    print("  FACT fixture {0} md5 {1}".format(FIX, m0), flush=True)
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running:
        return finish(None)
    shutil.copyfile(FIX, SCR)
    gate("K2 scratch is a byte copy of the fixture", md5(SCR) == m0, SCR)
    gr = None
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        lv = K.mod("wiki_build").read_live(SCR, fs_pairs=[])
        T, O = lv["terminals"], lv["objs"]
        sel = [r for r in T if r["owner_class"] == "SelectorTunnel" and r["term_class"] == "OuterTerminal" and r["is_source"]]
        gate("L terminal rows {0}, objs {1}, secs {2}".format(len(T), len(O), lv["secs"]), T and O)
        gate("L >=1 SelectorTunnel OuterTerminal SOURCE row ({0})".format(len(sel)), sel,
             [(r["owner_uid"], r["term_uid"], r["wire_uid"], r["term_name"]) for r in sel])
        gate("L exactly 1 CaseStructure obj", sum(1 for o in O if o["class"] == "CaseStructure") == 1,
             [o["uid"] for o in O if o["class"] == "CaseStructure"])
        gr = {"vi": FIX, "md5": m0, "source": "tools/bench/diag_c108d_graph.py (read_live on a byte copy)",
              "terminals": T, "objs": O, "fs_tunnel_pairs": []}
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        for _k in range(4):
            try:
                os.remove(SCR)
                break
            except OSError:
                time.sleep(2)
        gate("H LabVIEW gone; fixture md5 unchanged; copy deleted", gone and md5(FIX) == m0 and not os.path.exists(SCR),
             (gone, md5(FIX), os.path.exists(SCR)))
    if gr:
        json.dump(gr, open(OUT, "w", encoding="utf-8"), default=str)
        print("  FACT WROTE {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=[{"path": OUT, "md5": md5(OUT)}] if gr and os.path.exists(OUT) else [])), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
