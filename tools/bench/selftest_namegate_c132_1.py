r"""selftest_namegate_c132_1 - card 132-1 (PD275(c)) self-test of stagexec.tunnel_name_check (the per-op tunnel-name gate the
P3b-2 recipe runs through Executor(name_gate=True)). OFFLINE, no LabVIEW, no COM. Every name comes from a recorded log or a sim file.
PRIOR ART: stagexec.bind_fs_tunnel's BINDING key check (stagexec.py:916) - it compares names only when a class repeats; this gate
compares every new tunnel row's name. stagesim G74-G79 test the naming RULE, not a gate on real reads.
PREDICTION: E2 is_crossing_op selects ring_p3b1's fs_border wire steps and not its fs_frame_to_frame wire (step 16); M1 recorded
MATCH - the pin4 scratch run's new BORDER-tunnel terminal rows (NEWOBJ lines, stage_d1_ring_p3b1_scratch_pin4.log:457-574, E1 + both
names as predicted) vs the tunnels of the ring_p3b1 simulator's crossing steps (end state step_31): ok, >= 2 keys, names include
`Image Out` and `current image number` (run 1 compared ALL new tunnel rows and FAILED on the step-16 FS inner tunnel: sim '' vs
real 'error out' - hence the crossing-op restriction; printed as a FACT); X1 recorded MISMATCH - pin3 op 26 (stage_d1_ring_p3b1_scratch_pin3.log:370,
sim '' vs real 'Image Out'): NOT ok, the FlatSequenceOuterTunnel keys named; X2 the same pin4 rows with one name blanked: NOT ok;
E1 Executor(name_gate=...) accepted (signature) and an empty pair of states is ok.
    py tools/bgrun.py --material --max-min 4 --log tools/bench/selftest_namegate_c132_1.log -- py -u tools/bench/selftest_namegate_c132_1.py"""
import ast, copy, glob, inspect, json, os, re, sys                                    # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagexec as SX, protocol as P                                                 # noqa: E401,E402
res = []


def gate(name, ok, det=""):
    res.append((name, bool(ok)))
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:900]), flush=True)


lines = lambda f: open(os.path.join(B, f), encoding="utf-8", errors="replace").read().splitlines()   # noqa: E731
NEWOBJ = re.compile(r"NEWOBJ uid (\d+) class (\w+) \| owner #(\d+) (\w+) frame (\d+) term '(.*)' src (True|False) wire (\d+)")
real = []
for ln in lines("stage_d1_ring_p3b1_scratch_pin4.log"):
    m = NEWOBJ.search(ln)
    if m:
        real.append({"term_uid": int(m.group(1)), "term_class": m.group(2), "owner_uid": int(m.group(3)),
                     "owner_class": m.group(4), "frame_diagram": int(m.group(5)), "term_name": m.group(6),
                     "is_source": m.group(7) == "True", "wire_uid": int(m.group(8))})
STEPS = [json.load(open(f, encoding="utf-8")) for f in sorted(glob.glob(os.path.join(B, "sim", "ring_p3b1", "step_*.json")))]
s0, s31 = STEPS[0]["state"]["terminals"], STEPS[-1]["state"]["terminals"]
cross = [s["n"] for s in STEPS[1:] if SX.is_crossing_op([s.get("effect")])]
owners = set(u for s in STEPS[1:] if s["n"] in cross for u in s["effect"]["tunnels"])
ff = [s["n"] for s in STEPS[1:] if (s.get("effect") or {}).get("how") == "fs_frame_to_frame"]
gate("E2 is_crossing_op on ring_p3b1's sim steps: the fs_border wires {0} are crossings, the fs_frame_to_frame wire(s) {1} are not".format(cross, ff),
     cross and ff and not set(ff) & set(cross) and all(STEPS[n]["effect"].get("how") == "fs_border" for n in cross), (cross, ff))
# M1: the crossing steps' tunnels in the sim end state vs pin4's new rows owned by a border tunnel (an FS INNER tunnel is the
# frame-to-frame wire's, never a crossing's - see is_crossing_op)
s31x = [r for r in s31 if r["owner_uid"] in owners]
realx = [r for r in real if r["owner_class"] != "FlatSequenceInnerTunnel"]
ok, det = SX.tunnel_name_check(s0, s31x, [], realx)
names = set(n for v in det["real"].values() for n in v)
gate("M1 pin4 recorded new border-tunnel rows ({0} of {1} NEWOBJ terminal rows) == ring_p3b1 sim crossing steps' tunnels: ok".format(
    len(realx), len(real)), ok and len(det["real"]) >= 2 and {"Image Out", "current image number"} <= names, det)
okf, detf = SX.tunnel_name_check(s0, s31, [], real)
print("  FACT  whole-run incl. the fs_frame_to_frame inner tunnel: ok {0}, mismatch {1}: sim {2} real {3}".format(
    okf, detf["mismatch"], [detf["sim"].get(k) for k in detf["mismatch"]], [detf["real"].get(k) for k in detf["mismatch"]]), flush=True)
x = [ln for ln in lines("stage_d1_ring_p3b1_scratch_pin3.log")[369:370] if "terminal keys sim" in ln]
m = re.search(r"BINDING: (\w+) terminal keys sim (\{.*?\}) vs real (\{.*\})", x[0]) if x else None


def rows(cls, keys, base):
    out = []
    for (tc, src, nm), c in keys.items():
        for _ in range(c):
            base += 1
            out.append({"term_uid": base, "term_class": tc, "owner_class": cls, "is_source": src, "term_name": nm})
    return out


if m:
    sk, rk = ast.literal_eval(m.group(2)), ast.literal_eval(m.group(3))
    ok, det = SX.tunnel_name_check([], rows(m.group(1), sk, 1000), [], rows(m.group(1), rk, 2000))
    gate("X1 pin3 op 26 recorded mismatch (pin3.log:370 sim {0} vs real {1}): gate NOT ok, mismatch on {2}".format(sk, rk, m.group(1)),
         not ok and det["mismatch"] and all(k.startswith(m.group(1)) for k in det["mismatch"]), det)
else:
    gate("X1 pin3.log:370 carries the recorded BINDING key line", False, x)
r2 = copy.deepcopy(real)
nm = next(r for r in r2 if r["owner_class"] != "FlatSequenceInnerTunnel" and r["owner_class"].endswith("Tunnel") and r["term_name"])
nm["term_name"] = ""
ok, det = SX.tunnel_name_check(s0, s31x, [], [r for r in r2 if r["owner_class"] != "FlatSequenceInnerTunnel"])
gate("X2 pin4 border-tunnel rows with one recorded name blanked (uid {0}): gate NOT ok".format(nm["term_uid"]), not ok and det["mismatch"], det["mismatch"])
ok, det = SX.tunnel_name_check([], [], [], [])
gate("E1 Executor takes name_gate; empty states pass", "name_gate" in inspect.signature(SX.Executor.__init__).parameters and ok, det)
npass, nfail = sum(1 for _n, c in res if c), sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(npass, nfail, next((n for n, c in res if not c), None))), flush=True)
sys.stdout.flush()
os._exit(1 if nfail else 0)
