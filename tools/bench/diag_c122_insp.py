r"""diag_c122_insp - card 122-5 (offline, no LabVIEW): print the shape of a graph JSON (keys, one obj/terminal row, class census,
flat-sequence owners, panel labels) so the P2b plan generator reads the right fields. Read-only.
PREDICTION: prints; exit 0.
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c122_insp.log -- py -u tools/bench/diag_c122_insp.py <graph.json>"""
import collections, json, os, sys                                                 # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol                                                                    # noqa: E402
G = json.load(open(sys.argv[1], encoding="utf-8"))
print(list(G.keys()))
print("OBJ0", G["objs"][0]); print("TERM0", G["terminals"][0])
print(collections.Counter(o["class"] for o in G["objs"]).most_common(60))
print("CT", [o for o in G["objs"] if o["class"] == "ControlTerminal"][:3])
for k, v in sorted(G["owners"].items(), key=lambda kv: int(kv[0])):
    if str(v[0]).startswith("FlatSequence") or int(v[1] or 0) in (686, 536):
        print("OWNER", k, v)
labs = sorted(set(str(o.get("label")) for o in G["objs"] if o.get("label") is not None))
print("LABELS", len(labs), [x for x in labs if x in ("Num", "TransPos", "RotPos", "FrameIdx", "Latest")])
print(protocol.result_line(protocol.make_result(1, 0, None)))
