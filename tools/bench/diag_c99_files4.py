"""diag_c99_files4 - card 99-1, FILES ONLY. Fourth pass: ring size source, the Extension-vs-Time chain, diagram 11936.

PREDICTION CONTRACT
 P11 ring LeftSR #9025 is initialised by Initialize Array #8953 on 686 (diag_c99_files3.log:35)
Everything else is FACT.
"""
import json
src = open("tools/bench/diag_c99_files2.py", encoding="utf-8").read()
exec(src.split("s1 = G(")[0], globals())
B = "tools/bench/"
s1 = G(B + "par1359_95_graph.json")

print("[F1b] ring initialiser and its size inputs")
s1.node(8953)
gate("P11 #9025 <- #8953", any(e[3] == 8953 for e in s1.ends(9051)), s1.ends(9051))
for t in s1.by_owner[8953]:
    if not t["is_source"]:
        for e in s1.ends(t["wire_uid"], 8953) if t["wire_uid"] else []:
            if e[2] == "SRC":
                s1.node(e[3], f"(feeds #8953 {t['term_name']!r})")
print("   SubVI #1114 (F-x out source):", s1.objs.get(1114), "c97 label:", json.load(open(B + "diag_c97_gatefacts.json", encoding="utf-8"))["labels"].get("1114"))
for u in (10004, 10177, 8885, 30135):
    s1.node(u)

print("\n[F4] the Extension-vs-Time chain: For-loop tunnels with an inner terminal in body 29894")
for t in s1.d["terminals"]:
    if t["frame_diagram"] == 29894 and t["owner_class"] in ("LoopTunnel", "LeftShiftRegister", "RightShiftRegister") and t["term_class"] == "InnerTerminal":
        outer = [x for x in s1.by_owner[t["owner_uid"]] if x["term_class"] == "OuterTerminal"]
        print("     ", t["owner_uid"], t["owner_class"], repr(t["term_name"]), "SRC" if t["is_source"] else "sink", "| outer", [(x["term_name"], "SRC" if x["is_source"] else "sink", x["wire_uid"], s1.ends(x["wire_uid"], t["owner_uid"])) for x in outer])

print("\n[F2] diagram 11936 / 3628 in diagram_tree_main.json")
tree = json.load(open(B + "diagram_tree_main.json", encoding="utf-8"))
txt = json.dumps(tree)
for key in ("11936", "3628", "29894", "7911", "2235"):
    i = txt.find(key)
    print("  ", key, txt[max(0, i - 200): i + 200] if i >= 0 else "not in tree")
for u in (30549, 30617, 50177, 50244):
    s1.node(u, "(label 'Extension (nm) vs Time (Frame #)')")

json.dump(out, open(B + "diag_c99_files4.json", "w"), indent=1)
ng = out["gates"]
print(f"RESULT {json.dumps({'schema':'result-line/1','status':'PASS' if not ng['fail'] else 'FAIL','gates':{'pass':len(ng['pass']),'fail':len(ng['fail'])},'first_fail':ng['fail'][0] if ng['fail'] else None,'artefacts':[]})}")
