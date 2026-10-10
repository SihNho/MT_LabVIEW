# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-1.md
# ---
r"""prep_c164_a3_1_hash - card 164-3-1 parts 1+2 (OFFLINE, read-only): md5 of every card input + the five claudeDev VIs (bytes, matched by md5
prefix; "not hashed" if unreadable), then the two PD399(a) wire gates quoted from graph 3d5196ab BEFORE any edit:
  W1 every endpoint of w23460 lies on a terminal of #23042 or #23501;  W2 w23519 keeps >= 1 sink outside #23042 / #23501 (sinks listed).
Calls prep_c156_a1_1_lib Gate / md5 / J (no logic copied).
PREDICTION CONTRACT: M every card input == its pin; VI 564d8cbe f9ae7751 94ffff94 7f2582ae eb1d0f31 found; W1 rows t23505 (#23501 src), t23481 / t23477
  (#23042 sinks) -> PASS; W2 sinks t23514 (#23501), t23450 (#23417), t23241 (#23172), t7606 (#7201) -> outside {t23450, t23241, t7606} -> PASS.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c164_a3_1_hash.log -- py -u tools/bench/prep_c164_a3_1_hash.py"""
import glob, os, sys                                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_c156_a1_1_lib as L                                                               # noqa: E402
import prep_plan_flow_lib as FL                                                              # noqa: E402
md5, J, ROOT, CD = L.md5, L.J, FL.ROOT, FL.CD
gate = L.Gate(fatal_default=False)
CARD = J(os.path.join(ROOT, "tools/bench/cards/task_164-3-1.json"))
for i in CARD["inputs"]:
    h = md5(os.path.join(ROOT, i["path"]))
    print("FACT MD5 {0} {1} pin {2} {3}".format(h, i["path"], i["md5"][:8], "equal" if h == i["md5"] else "CHANGED"), flush=True)
    gate("M {0} == card pin {1}".format(i["path"], i["md5"][:8]), h == i["md5"], h)
VIPIN = ["564d8cbe", "f9ae7751", "94ffff94", "7f2582ae", "eb1d0f31"]
try:
    found = {}
    for p in sorted(glob.glob(os.path.join(CD, "D1_*.vi"))):
        h = md5(p)
        if h[:8] in VIPIN:
            found[h[:8]] = (os.path.basename(p), h)
    for v in VIPIN:
        print("FACT VI {0}: {1}".format(v, found.get(v, "NOT FOUND among claudeDev D1_*.vi")), flush=True)
    gate("VI five claudeDev VIs found by md5", all(v in found for v in VIPIN), sorted(set(VIPIN) - set(found)))
except OSError as e:
    print("FACT VI not hashed: {0}".format(e), flush=True)
GR = J(os.path.join(B, "graph_ring_p5s02c_20261010_131658.json"))
NODES = {23042, 23501}
for w in (23460, 23519):
    for r in GR["terminals"]:
        if int(r.get("wire_uid") or 0) == w:
            print("FACT W w{0} t{1} {2} owner #{3} {4} {5!r} {6}".format(w, r["term_uid"], "SRC " if r["is_source"] else "SINK", r["owner_uid"], r["owner_class"],
                  r["term_name"], r["term_class"]), flush=True)
r60 = [r for r in GR["terminals"] if int(r.get("wire_uid") or 0) == 23460]
gate("W1 every endpoint of w23460 on #23042/#23501: {0}".format(sorted((r["term_uid"], r["owner_uid"], r["is_source"]) for r in r60)),
     bool(r60) and any(r["is_source"] for r in r60) and all(int(r["owner_uid"]) in NODES for r in r60))
s19 = [r for r in GR["terminals"] if int(r.get("wire_uid") or 0) == 23519 and not r["is_source"]]
out19 = sorted(int(r["term_uid"]) for r in s19 if int(r["owner_uid"]) not in NODES)
gate("W2 w23519 keeps >= 1 sink outside #23042/#23501; sinks {0}; outside {1}".format(sorted((r["term_uid"], r["owner_uid"]) for r in s19), out19),
     len(out19) >= 1)
gate("W2b sinks outside == {t23450, t23241, t7606} (diag_c164_a2_4 prediction)", out19 == sorted([23450, 23241, 7606]), out19)
sys.exit(gate.result())
