r"""diag_c110f_dispgraph - card 110-6 R0: the display-loop VI's graph + its camera callee census, READ-ONLY, on a SCRATCH
byte copy (claudeDev\scratch_c110f_disp_<ts>.vi); no VI run; LabVIEW killed and scratch deleted at the end.
PRIOR ART (copied, nothing new): tools/bench/diag_c110_bedgraph.py (byte copy + restart + wiki_build.read_live -> the
terminal-list graph shape stage_prerun's OfflineGraph reads) and diag_replay_lib.census (g.subvis per diagram, the reader
stage_replay_swap.py's A2/A4 gates use). fs_pairs=[] exactly as stage_replay_swap.py:40/50 reads its edges.
OUTPUT tools/bench/graph_disp_20260927.json {vi, md5, terminals, objs, fs_tunnel_pairs, census, camera_callees}.
PREDICTION: K1 disp md5 == 245a1020...; K0 no LabVIEW before; K2 scratch is a byte copy; R0a #6810 calls
'get buff image-lost frames.vi' and #22692 calls 'IMAQdx Get Image.vi' (plan_replay_swap_78/95 rows; plan_disp.json names
neither uid); R0b no OTHER node calls either camera callee; H LabVIEW gone, disp md5 unchanged, scratch deleted.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c110f_dispgraph.log -- py -u tools/bench/diag_c110f_dispgraph.py"""
import hashlib, json, os, shutil, subprocess, sys, time                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import protocol as P, gscript as g, bench_prep, stagekit as K                            # noqa: E401,E402
import diag_replay_lib as L                                                              # noqa: E402
DSP, DSP_MD5 = os.path.join(g.CLAUDEDEV, "D1_s1_disp_20260927_041648.vi"), "245a10206b565cba0ba186bd891f5cb8"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c110f_disp_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_disp_20260927.json")
PLAN = json.load(open(os.path.join(HERE, "plans", "plan_replay_swap_95.json"), encoding="utf-8"))
WANT = dict((int(r["uid"]), r["old_callee"]) for r in PLAN["swaps"])
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def lv():
    return "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()


def main():
    gate("K1 disp md5 == pin", md5(DSP) == DSP_MD5, md5(DSP))
    running = lv()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or md5(DSP) != DSP_MD5:
        return finish(None)
    shutil.copyfile(DSP, SCR)
    gate("K2 scratch is a byte copy", md5(SCR) == DSP_MD5, SCR)
    gr = None
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                         # noqa: E702
        g.ensure_loaded(SCR)
        cen = L.census(SCR)
        cam = dict((u, p) for u, p in cen.items() if os.path.basename(str(p)) in set(WANT.values()))
        print("  FACT census {0} subVI nodes; camera callees {1}".format(len(cen), cam), flush=True)
        live = K.mod("wiki_build").read_live(SCR, fs_pairs=[])
        print("  FACT LIVE {0} terminal rows, {1} objs, secs {2}".format(len(live["terminals"]), len(live["objs"]), live["secs"]), flush=True)
        gr = {"vi": DSP, "md5": DSP_MD5, "source": "tools/bench/diag_c110f_dispgraph.py (read_live fs_pairs=[] + diag_replay_lib.census, byte copy)",
              "terminals": live["terminals"], "objs": live["objs"], "fs_tunnel_pairs": [],
              "census": dict((str(k), v) for k, v in sorted(cen.items())), "camera_callees": dict((str(k), v) for k, v in sorted(cam.items()))}
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = not lv()
        try:
            os.remove(SCR)
        except OSError as e:
            print("  FACT scratch not removed: {0}".format(e), flush=True)
        gate("H LabVIEW gone; disp md5 unchanged; scratch deleted", gone and md5(DSP) == DSP_MD5 and not os.path.exists(SCR),
             (gone, md5(DSP), os.path.exists(SCR)))
    if gr:
        cam = dict((int(k), v) for k, v in gr["camera_callees"].items())
        gate("R0a #6810 / #22692 present with the plan's old callees", all(os.path.basename(str(cam.get(u, ""))) == o for u, o in WANT.items()),
             dict((u, cam.get(u)) for u in WANT))
        gate("R0b no other node calls a camera callee", set(cam) == set(WANT), sorted(set(cam) - set(WANT)))
        json.dump(gr, open(OUT, "w", encoding="utf-8"))
        print("  FACT WROTE {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=[{"path": OUT, "md5": md5(OUT)}] if gr and os.path.exists(OUT) else [])), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
