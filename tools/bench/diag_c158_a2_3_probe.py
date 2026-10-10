# ---
# labview: none
# hardware: none
# evidence: tools/stagekit.py:1790-1803
# ---
"""diag_c158_a2_3_probe - card 158-a2-3: OFFLINE structure probe (no LabVIEW, no edits). Prints the row shape of the sim end state
(step_23_wire.json), the plan's finalized base, and the scratch json's real_end_rows, so the measurement script can call
stagekit/vigraph on them. Inputs only + prints; existing functions used: stagekit.jload.
PREDICTION: prints keys; RESULT pass 1 when all three files load."""
import os, sys, json                                                                     # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
import protocol                                                                          # noqa: E402

S = K.jload(K.BENCH, "sim", "ring_p5s02a", "step_23_wire.json")
print("step keys", sorted(S))
L = S["state"]
print("state keys", sorted(L))
for k in sorted(L):
    v = L[k]
    print(" ", k, type(v).__name__, len(v) if hasattr(v, "__len__") else v)
print("term row sample", L["terminals"][:2])
print("objs sample", (L.get("objs") or [])[:2])
print("loops sample", str(L["loops"])[:300])
print("sym sample", list(L.get("sym", {}).items())[:60])
P = K.jload(K.BENCH, "plan_ring_p5s02a.json")
print("plan keys", sorted(P), "finalized", sorted(P["finalized"]))
B = K.jload(K.ROOT, P["finalized"]["base"]["path"])
print("base", P["finalized"]["base"], "keys", sorted(B))
print("base term sample", B["terminals"][:2])
print("base objs?", [k for k in B if "obj" in k], "loops?", [k for k in B if "loop" in k])
print("open_rows", P["open_rows"][:5], len(P["open_rows"]))
D = K.jload(K.BENCH, "diag_c156_p5s02a_scratch.json")
print("real_end_rows", len(D["real_end_rows"]), D["real_end_rows"][:2])
for o in D["stagexec"]:
    if o.get("bound"):
        print("bound op", o.get("k"), o.get("op"), o["bound"])
print("ops[0] keys", sorted(D["ops"][0]) if D["ops"] and isinstance(D["ops"][0], dict) else D["ops"][:1])
print(protocol.result_line("PASS", 1, 0))
