"""diag_c99_files5 - card 99-1 F3, FILES ONLY: the source of the S3 loop's stop comparison in the bed.
PREDICTION CONTRACT: P12 LoopTunnel #23172 has an OuterTerminal record in the bed graph (diag_c99_files3.log:6-7).
"""
import json
exec(open("tools/bench/diag_c99_files2.py", encoding="utf-8").read().split("s1 = G(")[0], globals())
bed = G("tools/bench/graph_s3_loop15_20260924.json")
bed.node(23172)
outer = [t for t in bed.by_owner[23172] if t["term_class"] == "OuterTerminal"]
gate("P12 #23172 outer record exists", bool(outer), outer)
for t in outer:
    for e in bed.ends(t["wire_uid"], 23172) if t["wire_uid"] else []:
        if e[2] == "SRC":
            bed.node(e[3], "(feeds #23172 outer)")
print("   obj 23032:", bed.objs.get(23032), " obj 23172:", bed.objs.get(23172))
ng = out["gates"]
print(f"RESULT {json.dumps({'schema':'result-line/1','status':'PASS' if not ng['fail'] else 'FAIL','gates':{'pass':len(ng['pass']),'fail':len(ng['fail'])},'first_fail':ng['fail'][0] if ng['fail'] else None,'artefacts':[]})}")
