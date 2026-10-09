# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-2.md
# ---
r"""prep_c156_a1_2_measure - card 156-a1-2 item 1 (OFFLINE, before any tool edit): reproduce the K3/K4 refusal and measure the
two terminals the simulator compares, the frame of each case tunnel's inner faces, and what the current tools do with a
`frame` on the pass wire's dst end. Calls prep_c156_a1_2_lib (k_actions, sim_plan, last_state, term_brief).
PREDICTION CONTRACT:
  R0 the first 60 actions of plan_ring_p5s02r_in.json == plan_ring_p5s02r_all.json's 60 actions.
  R3/R4 K3 (resp. K4) as written fails at action 69 (w_k3pass / w_k4pass) with the stagesim.py:1536 message 'source on
     diagram -30, sink on diagram -29'; the resolved source = IK<k> InnerTerminal on the case frame 'True' (f1), the sink =
     OK<k> InnerTerminal on frame 'False' (f0) = OK<k>'s case_tunnel_frame.
  F  OK<k> has one InnerTerminal on EVERY frame of CQ7 (stagesim._case_tunnel, :1363); in graph 6716c499 every
     SelectorTunnel of base case #30726 has one inner face on each of its frames [30914, 30922].
  V  with `frame: 'True'` on the pass wire's dst: the CURRENT compile refuses (stagexec.py:857 group rule) - recorded text.
  B  compile of every stored plan written to tools/bench/sim/ring_p5s02pw/compile_before.json (before the edit).
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c156_a1_2_measure.log -- py -u tools/bench/prep_c156_a1_2_measure.py"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import protocol  # noqa: E402
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402
import prep_c156_a1_2_lib as L  # noqa: E402

G = {"pass": 0, "fail": 0}
FIRST = []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and not FIRST:
        FIRST.append(label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


print("FACT md5 stagexec {0} stagesim {1} graph {2} rin {3} all {4}".format(
    L.md5(os.path.join(ROOT, "tools", "stagexec.py")), L.md5(os.path.join(ROOT, "tools", "stagesim.py")), L.md5(L.GRAPH),
    L.md5(L.RIN), L.md5(L.ALLF)), flush=True)
gate("R0 first 60 actions of plan_ring_p5s02r_in.json == plan_ring_p5s02r_all.json actions",
     L.jload(L.RIN)["actions"][:60] == L.jload(L.ALLF)["actions"], len(L.jload(L.ALLF)["actions"]))
for k in ("3", "4"):
    top, acts = L.k_actions(("K" + k,))
    R = L.sim_plan(top, acts, "measure_k" + k)
    f = R.get("failed") or {}
    print("FACT R{0} failed n {1} op {2} id {3}: {4}".format(k, f.get("n"), f.get("op"), f.get("id"), f.get("error")), flush=True)
    st = L.last_state(R)
    a = acts[int(f.get("n") or 1) - 1]
    s = SS.resolve_addr(st, a["src"], True)
    d = SS.resolve_addr(st, a["dst"], False)
    cq = st["sym"]["new:CQ7"]
    frames = SS.case_frame_names(st, cq)
    ctf = st.get("case_tunnel_frame") or {}
    for nm in ("IK" + k, "OK" + k):
        u = st["sym"]["new:" + nm]
        faces = [L.term_brief(r) for r in st["terminals"] if r["owner_uid"] == u]
        print("FACT TUN {0} #{1} case_tunnel_frame {2}; rows (term, owner, class, term_class, frame, wire) {3}".format(
            nm, u, ctf.get(str(u)), faces), flush=True)
    print("FACT CASE CQ7 #{0} frames {1}".format(cq, frames), flush=True)
    print("FACT ENDS src {0} | dst {1}".format(L.term_brief(s), L.term_brief(d)), flush=True)
    fname = dict((f_, n_) for n_, f_ in frames)
    ou = st["sym"]["new:OK" + k]
    oin = sorted(r["frame_diagram"] for r in st["terminals"] if r["owner_uid"] == ou and r["term_class"] == "InnerTerminal")
    gate("R{0} K{0} as written fails at action 69 ({1}) with the stagesim.py:1536 border message; src IK{0}.inner on frame {2!r}, "
         "dst OK{0}.inner on frame {3!r} = OK{0}'s case_tunnel_frame".format(k, a["id"], fname.get(s["frame_diagram"]), fname.get(d["frame_diagram"])),
         f.get("n") == 69 and a["id"] == "w_k{0}pass".format(k) and "a border needs a tunnel/register action first" in str(f.get("error"))
         and fname.get(s["frame_diagram"]) == "True" and fname.get(d["frame_diagram"]) == "False"
         and int(ctf.get(str(ou))) == d["frame_diagram"], (L.term_brief(s), L.term_brief(d)))
    gate("F{0} OK{0} has ONE InnerTerminal on every frame of CQ7 (stagesim._case_tunnel)".format(k),
         oin == sorted(f_ for _n, f_ in frames), oin)
    ok3 = dict(a["dst"]) if isinstance(a["dst"], dict) else {"uid": a["dst"].split(".", 1)[0], "side": "inner"}
    ok3["frame"] = "True"
    d2 = SS.resolve_addr(st, ok3, False)
    gate("F{0}b resolve_addr OK{0} inner frame 'True' = its face on the same diagram as the source".format(k),
         d2["frame_diagram"] == s["frame_diagram"], L.term_brief(d2))
    top, acts = L.k_actions(("K" + k,), pass_frame="True")
    try:
        ops = SX.compile_plan(dict(top, actions=acts))
        print("FACT V{0} current compile ACCEPTS the frame pass wire: {1}".format(k, [(o["kind"], o["acts"]) for o in ops[-4:]]), flush=True)
        verr = None
    except SX.ExecStop as e:
        verr = str(e)
        print("FACT V{0} current compile refuses the frame pass wire: {1}".format(k, verr), flush=True)
    gate("V{0} the CURRENT compile refuses `frame` on the pass wire's dst (the tunnel group needs a frameless out-wire)".format(k),
         verr is not None and "must be followed by exactly one wire into it and one out of it" in verr, verr)
    R2 = L.sim_plan(top, acts, "measure_k{0}_frame".format(k))
    print("FACT V{0}s current stagesim on the frame pass wire: failed {1}; steps {2}; provisional {3}".format(
        k, R2.get("failed"), len(R2.get("steps") or []), [x["n"] for x in R2.get("steps") or [] if x.get("provisional")]), flush=True)
# ---- graph 6716c499: the base case #30726's tunnels
g = L.jload(L.GRAPH)
fr = SS.base_case_frames(g["owners"], 30726)
byo = collections.defaultdict(list)
for r in g["terminals"]:
    if r["owner_class"] in SS.CASE_FACE_CLS and r["term_class"] == "InnerTerminal" and int(r["frame_diagram"] or 0) in fr:
        byo[r["owner_uid"]].append(int(r["frame_diagram"]))
rows = dict((u, sorted(set(v))) for u, v in byo.items())
print("FACT G30726 frames {0}; tunnel inner faces per owner {1}".format(fr, rows), flush=True)
gate("G every tunnel/selector of base case #30726 in graph 6716c499 has an inner face on each frame {0}".format(fr),
     rows and all(v == sorted(fr) for v in rows.values()), rows)
# ---- B: before-list
os.makedirs(L.SIMD, exist_ok=True)
BEF = os.path.join(L.SIMD, "compile_before.json")
now = L.compile_all()
with open(BEF, "w", encoding="utf-8") as f:
    json.dump(now, f, indent=0, sort_keys=True)
print("FACT B plans {0} compiled {1} refused {2} skipped {3}; written {4} {5}".format(
    len(now), sum(1 for v in now.values() if "ops" in v), sum(1 for v in now.values() if "error" in v),
    sum(1 for v in now.values() if "skip" in v), os.path.relpath(BEF, ROOT), L.md5(BEF)), flush=True)
for p in ("plan_ring_p5s01a.json", "plan_ring_p5s01b.json", "plan_ring_p5s01_in.json", "plan_ring_p5s02a.json", "plan_ring_p5s02.json",
          "plan_ring_p5s02_all.json", "plan_ring_p5s02_in.json", "plan_ring_p5s02a_in.json", "plan_ring_p5s02r_all.json", "plan_ring_p5s02r_in.json"):
    v = now.get("tools/bench/" + p) or {}
    print("FACT B {0} md5 {1} ops {2} error {3}".format(p, (v.get("md5") or "")[:8], len(v.get("ops") or []), (v.get("error") or "")[:200]), flush=True)
gate("B before-list written ({0} plans)".format(len(now)), os.path.isfile(BEF) and len(now) > 100)
print(protocol.result_line({"status": "PASS" if not G["fail"] else "FAIL", "gates": G, "first_fail": FIRST[0] if FIRST else None,
                            "artefacts": [{"path": os.path.relpath(BEF, ROOT).replace("\\", "/"), "md5": L.md5(BEF)}]}))
sys.exit(1 if G["fail"] else 0)
