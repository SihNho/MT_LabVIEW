r"""diag_c117a_cmp - card 117-1, OFFLINE (no LabVIEW, no VI): re-compare the joints ALREADY READ by diag_c117a_joints.py
(tools/bench/diag_c117a_joints_raw.json, written by that run) with card 116-4's reads (diag_c116d_j3_raw2.json) after normalising both
through json (COM returns nested TUPLES, the stored reference holds LISTS: diag_c117a_joints.log:4-21 show the decoded tuples equal on every
net while every raw '==' is False). Report-only: the L3b gate of diag_c117a_joints.log:25 stays FAIL as recorded; this prints what the
normalised comparison says. PREDICTION: prints one line per net (raw equal to R1 / to 116-4 after, normalised).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c117a_cmp.log -- py -u tools/bench/diag_c117a_cmp.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))   # noqa: E702
import protocol as P                                                               # noqa: E402
N = lambda x: json.loads(json.dumps(x, default=str))                               # noqa: E731
NEW = json.load(open(os.path.join(HERE, "diag_c117a_joints_raw.json"), encoding="utf-8"))
REF = json.load(open(os.path.join(HERE, "diag_c116d_j3_raw2.json"), encoding="utf-8"))
PD = [8590, 9051, 11253, 11389, 25438, 25461, 29122]
rows = []
for w in sorted(NEW, key=int):
    j = N(NEW[w]["joints"]) if NEW[w] else None
    a, b = REF["after"].get(w), REF["before"].get(w)
    ea, eb = bool(a and j == N(a["joints"])), bool(b and j == N(b["joints"]))
    rows.append((int(w), ea, eb))
    print("CMP w{0} pd230={1} raw==116-4after {2} raw==R1 {3}".format(w, int(w) in PD, ea, eb), flush=True)
l3b = all(eb for w, ea, eb in rows if w in PD and w not in (25438, 25461)) and all(ea for w, ea, eb in rows if w in (25438, 25461))
allafter = all(ea for _w, ea, _eb in rows)
print("SUM normalised: L3b condition holds {0}; every net raw == 116-4 after-read {1} ({2} nets)".format(l3b, allafter, len(rows)), flush=True)
print(P.result_line(P.make_result(1, 0, None, [])), flush=True)
