# ---
# labview: none
# hardware: none
# ---
r"""diag_c151_a1_1_fs - card 151-a3-1 (OFFLINE, no LabVIEW; PD367(d)): from one graph json (argv[1], the s08 graph read written by
diag_c151_a1_1_graph.py), print FS #29721's frames and every terminal row on its frame #29869 plus its border tunnels (both faces):
owner uid, POSITION index (addrcheck.pos_table = the T6 result-gate key, read order per node), owner class, term class, term name, term uid,
wire uid, is_source. Existing readers checked first: stagesim.fs_measured_state (borders, used here as-is) and addrcheck.pos_table (index);
no other script prints one frame's rows, so this is a 60-line reader over their outputs.
PREDICTION: fs_frames['29721'] == [29869] (as in graph_ring_p4s07_20261008_224835.json); >= 1 row on #29869; borders of fs 29721 listed.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c151_a1_1_fs.log -- py -u tools/bench/diag_c151_a1_1_fs.py <graph json>"""
import json, os, sys                                                                        # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import addrcheck as AC                                                                      # noqa: E402
FS, FR = 29721, 29869
gr = json.load(open(os.path.join(ROOT, sys.argv[1]), encoding="utf-8"))
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


fm = (gr.get("fs_measured") or {})
frames = (fm.get("fs_frames") or {}).get(str(FS))
print("FACT graph records fs_measured keys {0}; FS count {1}; border tunnels {2}".format(sorted(fm), len(fm.get("fs_frames") or {}), len(fm.get("borders") or {})), flush=True)
gate("F FS #{0} frames == [{1}]".format(FS, FR), frames == [FR], frames)
print("FACT owner of frame #{0}: {1}".format(FR, (gr.get("owners") or {}).get(str(FR))), flush=True)
rows = gr.get("terminals") or []
pos = AC.pos_table(rows)
bord = dict((int(k), v) for k, v in (fm.get("borders") or {}).items() if v.get("fs") == FS)
bowners = set(bord)
on = [r for r in rows if int(r.get("frame_diagram") or 0) == FR]
gate("R rows on frame #{0} > 0".format(FR), len(on) > 0, len(on))


def show(tag, r):
    k = pos.get(r["term_uid"])
    print("ROW {0} | owner #{1} | index {2} | {3} | {4} | name {5!r} | term #{6} | wire {7} | src {8} | frame {9}".format(
        tag, r.get("owner_uid"), k[1] if k else None, r.get("owner_class"), r.get("term_class"), r.get("term_name"), r.get("term_uid"),
        r.get("wire_uid"), bool(r.get("is_source")), r.get("frame_diagram")), flush=True)


for r in sorted(on, key=lambda r: (int(r["owner_uid"]), pos.get(r["term_uid"], (0, 0))[1])):
    show("frame{0}".format(FR), r)
for u, v in sorted(bord.items()):
    print("BORDER tunnel #{0} {1}".format(u, json.dumps(v, sort_keys=True)), flush=True)
    for r in rows:
        if int(r["owner_uid"]) == u and int(r.get("frame_diagram") or 0) != FR:
            show("border-outer", r)
print("FACT {0} rows on #{1}; {2} border tunnel(s) of FS #{3}: {4}".format(len(on), FR, len(bord), FS, sorted(bowners)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
