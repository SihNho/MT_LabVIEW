r"""diag_c125_joints - card 125-4 STEP C (brief_125-4.md, review archive/peer/2026-10-01-c125-2-loose-hyp.md §cheapest test): READ-ONLY
Wire.Joints[] (gscript.wire_joints -> OpWireJoints_v1, hygiene 2,066 calls) of the 12 nets the P3a stage touched (11 new wires + w3747
BufNum, which gained the wire_sr RightIn and connect_from_wire branches; graph diff diag_c125_loose.log NEWWIRE) on BYTE COPIES of the P2b
bed and the P3a bed. PRIOR ART reused line for line: diag_c117a_joints.py (one report_all(Wire) index map, wire_joints(index=)),
diag_c116d_decode.py joint layout [[x,y], flags, n_nb, nb0..nb3]: flags & 0x1 terminal joint, & 0x100 LOOSE.
A FREE END = a joint with exactly 1 neighbour and no terminal flag. MEASUREMENT ONLY: no prediction on how many free ends exist.
Gates: R every present net read (echo == uid, err ''); X both beds' md5 unchanged, copies deleted, LabVIEW gone.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c125_joints.log -- py -u tools/bench/diag_c125_joints.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402
BEDS = {"p2b": ("D1_ring_p2b_20261001_140658.vi", "652b1447ebbda761a7d5ba36455a0fa1"),
        "p3a": ("D1_ring_p3a_20261001_180540.vi", "4dfa44aac8fb32f706b3eb792ee7d3cc")}
NETS = [3747, 27073, 27167, 27245, 27331, 27337, 27350, 27378, 27404, 27911, 39296, 39360]
TS = time.strftime("%Y%m%d_%H%M%S")
SCR = dict((k, os.path.join(g.CLAUDEDEV, "scratch_c125_j_%s_%s.vi" % (k, TS))) for k in BEDS)
G, OUT = {}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:1500]), flush=True); return bool(ok)  # noqa: E702


def dec(r):
    """(n joints, loose joints, terminal joints, free ends [(joint index, [x, y])])"""
    if not r or not r.get("joints"):
        return None
    J = [list(x) for x in r["joints"]]
    free = [(i, list(x[0])) for i, x in enumerate(J) if int(x[2]) == 1 and not int(x[1]) & 0x1]
    return {"joints": len(J), "loose": sum(1 for x in J if int(x[1]) & 0x100), "terms": sum(1 for x in J if int(x[1]) & 0x1), "free": free}


try:
    for k, (f, m) in BEDS.items():
        p = os.path.join(g.CLAUDEDEV, f)
        gate("K %s bed md5 == %s" % (k, m[:8]), os.path.exists(p) and md5(p) == m, p)
        shutil.copyfile(p, SCR[k])
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    for k in BEDS:
        order = [int(o["uid"]) for o in g.report_all(SCR[k], "Wire")]
        pos = dict((u, i) for i, u in enumerate(order))
        OUT[k] = {}
        print("  FACT  %s: %d wires in Traverse(Wire)" % (k, len(order)), flush=True)
        for w in NETS:
            r = g.wire_joints(SCR[k], w, index=pos[w]) if w in pos else None
            OUT[k][w] = r
            print("  FACT  %s w%s present %s echo %s err %r dec %s" % (k, w, w in pos, r and r["echo"], r and r["err"], dec(r)), flush=True)
    bad = [(k, w) for k in OUT for w, r in OUT[k].items() if r is not None and (r["err"] or r["echo"] != w)]
    gate("R every present net read (echo == uid, err '')", not bad, bad)
    rows = []
    for w in NETS:
        a, b = dec(OUT["p2b"].get(w)), dec(OUT["p3a"].get(w))
        fa = set(tuple(x[1]) for x in (a or {}).get("free", []))
        extra = [x for x in (b or {}).get("free", []) if tuple(x[1]) not in fa]
        rows.append({"net": w, "p2b": a, "p3a": b, "p3a_extra_free_ends": extra})
        print("  TABLE w%s | p2b %s | p3a %s | P3a-extra free ends %s" % (w, a and (a["joints"], a["loose"], a["terms"], len(a["free"])),
              b and (b["joints"], b["loose"], b["terms"], len(b["free"])), extra), flush=True)
    ex = [r["net"] for r in rows if r["p3a_extra_free_ends"]]
    print("  FACT  nets with a P3a-extra free end: %s (%d free ends)" % (ex, sum(len(r["p3a_extra_free_ends"]) for r in rows)), flush=True)
    json.dump({"beds": BEDS, "nets": NETS, "raw": dict((k, dict((str(w), v) for w, v in OUT[k].items())) for k in OUT), "table": rows},
              open(os.path.join(HERE, "diag_c125_joints_raw.json"), "w", encoding="utf-8"), default=str, indent=1)
except Exception as e:                                                                       # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    for p in SCR.values():
        for _i in range(5):
            try:
                os.path.exists(p) and os.remove(p); break                                    # noqa: E702
            except OSError:
                time.sleep(3)
    gate("X LabVIEW gone; copies deleted; both beds' md5 unchanged",
         "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
         and not any(os.path.exists(p) for p in SCR.values())
         and all(md5(os.path.join(g.CLAUDEDEV, f)) == m for f, m in BEDS.values()))
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
    sys.exit(1 if bad else 0)
