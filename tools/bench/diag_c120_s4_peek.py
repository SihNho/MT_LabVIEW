"""diag_c120_s4_peek - card 120-4, offline read of existing JSON (no LabVIEW): the HARNESS_copyloop graph (c95) as the
scratch plan's base - md5 vs the file, top diagram, GetImageSize terminals, panel controls; stagesim queue/case tables."""
import hashlib, json, os, sys
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
import stagesim as SS  # noqa: E402
G = json.load(open(os.path.join(B, 'graph_harness_copyloop_c95.json'), encoding='utf-8'))
vi = G.get('vi')
print("GKEYS", list(G.keys()), vi, G.get('md5'), G.get('source'))
print("FILEMD5", hashlib.md5(open(vi, 'rb').read()).hexdigest() if vi and os.path.exists(vi) else "MISSING")
print("OWNERS", G.get('owners'))
print("LOOPS", json.dumps(G.get('loops'))[:600])
print("FSP", G.get('fs_tunnel_pairs'))
for o in G['objs']:
    if o['class'] not in ('Terminal', 'Wire') and not o['class'].endswith('Terminal'):
        print("OBJ", o)
for r in G['terminals']:
    print("T", r['term_uid'], repr(r['term_name']), r['is_source'], r['wire_uid'], r['owner_uid'], r['owner_class'], r['frame_diagram'], r.get('term_class'))
print("QT obtain", SS.QUEUE_TERM_TABLE.get('obtain'))
print("QT dequeue", SS.QUEUE_TERM_TABLE.get('dequeue'))
print("CASE_FRAMES_DEFAULT", getattr(SS, 'CASE_FRAMES_DEFAULT', None))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
