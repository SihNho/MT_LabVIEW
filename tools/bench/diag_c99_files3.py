"""diag_c99_files3 - card 99-1, FILES ONLY. Third pass: named nodes only (reuses diag_c99_files2.G).

PREDICTION CONTRACT
 P9  bed loop #23032's conditional terminal #23080 is fed by Comparison #23035 (diag_c99_files2.log:124)
 P10 S1 #1359 is a ForLoop whose body is diagram 7911 (tunnel #11363 inner fd 7911, files2.log:20)
Everything else is printed as FACT, not gated.
"""
import json, importlib.util, sys
spec = importlib.util.spec_from_file_location("f2", "tools/bench/diag_c99_files2.py")
src = open("tools/bench/diag_c99_files2.py", encoding="utf-8").read()
G = None
exec(src.split("s1 = G(")[0], globals())   # class G + gate/out only, no side effects of the second pass

B = "tools/bench/"
s1 = G(B + "par1359_95_graph.json")
bed = G(B + "graph_s3_loop15_20260924.json")

print("[F3] bed: the S3 loop's stop and the S3 locals")
for u in (23035, 23523, 23499, 11639):
    bed.node(u)
p9 = [e for e in bed.ends(23145) if e[3] == 23035]
gate("P9 #23080 <- #23035", bool(p9), p9)
print("   bed ControlTerminals named TurnOff / stop:", [(t["term_uid"], t["term_name"], t["frame_diagram"], t["wire_uid"]) for t in bed.d["terminals"] if t["term_class"] == "ControlTerminal" and ("TurnOff" in t["term_name"] or "stop" in t["term_name"].lower())])
print("   bed Local terminals:", {u: [(t["term_name"], "SRC" if t["is_source"] else "sink", t["frame_diagram"], t["wire_uid"]) for t in bed.by_owner[u]] for u, o in bed.objs.items() if o["class"] == "Local"})
print("   S1 Local terminals with fd/wire:", {u: [(t["term_name"], "SRC" if t["is_source"] else "sink", t["frame_diagram"], t["wire_uid"]) for t in s1.by_owner[u]] for u, o in s1.objs.items() if o["class"] == "Local"})

print("\n[F1b] S1 ring + loop count of #1359")
print("   obj 1359:", s1.objs.get(1359))
gate("P10 #1359 obj class ForLoop", (s1.objs.get(1359) or {}).get("class") == "ForLoop", s1.objs.get(1359))
for u in (8634, 9018, 9025, 8566, 8741, 27716, 11374):
    s1.node(u)
print("   terminals in fd 7911 owned by 7911 (N / i of #1359):", [(t["term_uid"], t["term_name"], "SRC" if t["is_source"] else "sink", t["wire_uid"], s1.ends(t["wire_uid"], 7911)) for t in s1.by_owner[7911]][:12])
print("   LoopTunnels with an InnerTerminal in fd 7911:")
for t in s1.d["terminals"]:
    if t["frame_diagram"] == 7911 and t["owner_class"] in ("LoopTunnel", "LeftShiftRegister", "RightShiftRegister") and t["term_class"] == "InnerTerminal":
        outer = [x for x in s1.by_owner[t["owner_uid"]] if x["term_class"] == "OuterTerminal"]
        print("     ", t["owner_uid"], t["owner_class"], repr(t["term_name"]), "in-w", t["wire_uid"], "| outer", [(x["term_name"], "SRC" if x["is_source"] else "sink", x["wire_uid"], s1.ends(x["wire_uid"], t["owner_uid"])) for x in outer])

print("\n[F2/F4] where the Z/dZ plot outputs go, and the 'Extension vs Time' indicator's source")
for u in (6104, 9833, 29172, 2276):
    s1.node(u)
for w in (6363, 4906):
    pass

json.dump(out, open(B + "diag_c99_files3.json", "w"), indent=1)
ng = out["gates"]
print(f"RESULT {json.dumps({'schema':'result-line/1','status':'PASS' if not ng['fail'] else 'FAIL','gates':{'pass':len(ng['pass']),'fail':len(ng['fail'])},'first_fail':ng['fail'][0] if ng['fail'] else None,'artefacts':[]})}")
