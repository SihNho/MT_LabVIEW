# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-1.md
# ---
r"""prep_c164_a3_1_mk - card 164-3-1 parts 4+5 (OFFLINE, json only, never launched): plan_ring_p5s02d.json = P5-2 step 4 = the longest whole-group
prefix of J K3 of plan_ring_p5s02r_in.json 9dadb0c1 (= 4d93c82d + dw_23460 after A53 + rle_23519 after A56, prep_c164_a3_1_cmp.log; PD399(a)),
MAIN <= 675, rows <= 40, FINAL on the real p5s02c graph 3d5196ab (VI 564d8cbe). Same inputs and ONE call of prep_plan_flow_lib.make_step_plan as
prep_c164_a2_2_mk.py (872822f3), with: pins from task_164-3-1.json; census = prep_c164_a3_1_census.json (= prep_c156_a1_1_session.json with group J's
action list + the 2 new ids at their plan positions; written here, the only change); keep_prev = plan_ring_p5s02d_prev872822f3.json; plan_in / session
under prep_c164_a3_1_*. Part 5 (PD399(a), the peer's discriminating test): in the sim END state of the plan (last finalized step file) w23460 has no
terminal row and no Wire object; w23519 has source t8494 and sinks EXACTLY {t23450, t23241, t7606}.
PREDICTION CONTRACT: M0 pins; GRP [(53,62,10),(63,71,9)]; MAP/FRM as 872822f3; ROWS; STUB PASS; C J and J+K3 compile; plan = J+K3 (19 rows, MAIN <= 675);
  PROBE / TIE / SB final True, 0 PROVISIONAL, route PASS, 0 UNROUTABLE; C-OUT / IDS A53..A71; X8 / X17 clean; END w23460 absent, w23519 sinks
  {23450, 23241, 7606}; U pins unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c164_a3_1_mk.log -- py -u tools/bench/prep_c164_a3_1_mk.py"""
import json, os, sys                                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, rel, CD, ROOT = FL.L, FL.J, FL.md5, FL.rel, FL.CD, FL.ROOT
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
WANT = dict((os.path.normpath(os.path.join(ROOT, i["path"])), i["md5"]) for i in J("tools/bench/cards/task_164-3-1.json")["inputs"])
WANT[P("plan_ring_p5s02r_in.json")] = "9dadb0c1"                                             # edited in part 3 (prep_c164_a3_1_cmp.log)
WANT.pop(P("plan_ring_p5s02d.json"))                                                         # replaced by this maker (prev kept aside)
VIC, VIA = os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"), os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi")
VIB = os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")
WANT.update({P("plan_ring_p5s02a.json"): "4284c22a", P("plan_ring_p5s02b.json"): "f4520b10", P("graph_ring_p5s02a_20261010_032547.json"): "7ac24924",
             P("graph_ring_p5s02b_20261010_111905.json"): "431cfd83", VIC: "564d8cbe", VIA: "94ffff94", VIB: "f9ae7751",
             P("plan_ring_p5s02r_in_pre164r3.json"): "4d93c82d", P("prep_c156_a1_1_session.json"): md5(P("prep_c156_a1_1_session.json"))})
gate = L.Gate()
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card / brief pins", all(M0[p].startswith(w) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
gate("M1 plan_ring_p5s02d.json before == 872822f3", md5(P("plan_ring_p5s02d.json")).startswith("872822f3"), md5(P("plan_ring_p5s02d.json")))
# census: group J of prep_c156_a1_1_session.json + the two PD399(a) rows at their plan positions (the maker reads only `group` / `actions`)
CEN = J(P("prep_c156_a1_1_session.json"))
RA = [a["id"] for a in J(P("plan_ring_p5s02r_in.json"))["actions"]]
for c in CEN["census"]:
    if c["group"] == "J":
        old = list(c["actions"])
        c["actions"] = [i for i in RA if i in old or i in ("dw_23460", "rle_23519")]
        print("FACT CENSUS J {0} -> {1}".format(old, c["actions"]), flush=True)
CENP = P("prep_c164_a3_1_census.json")
json.dump(CEN, open(CENP, "w", encoding="utf-8"), indent=1)
GRAPH = P("graph_ring_p5s02c_20261010_131658.json")
SRC = [{"name": "p5s02a", "plan": P("plan_ring_p5s02a.json"), "graph_after": P("graph_ring_p5s02a_20261010_032547.json"), "vi": VIA},
       {"name": "p5s02b", "plan": P("plan_ring_p5s02b.json"), "graph_after": P("graph_ring_p5s02b_20261010_111905.json"), "vi": VIB},
       {"name": "p5s02c", "plan": P("plan_ring_p5s02c.json"), "graph_after": GRAPH, "vi": VIC}]
goal = lambda lo, hi, cand, ch: ("RING P5-2 step 4 (card 164-3-1, PD399(a)(b)): A{0}..A{1} of plan_ring_p5s02r_in.json 9dadb0c1 (J in the P4 delete form: "
                                 "dw_23460 before the deletes, rle_23519 after #23501; K3f/K4/K4f next step) on the REAL 564d8cbe graph 3d5196ab; plan {2} = "
                                 "longest whole-group prefix with MAIN <= 675, rows <= 40; MAIN per prefix {3}").format(
                                 lo, hi, ch, dict((k, v.get("main")) for k, v in cand.items()))[:400]   # noqa: E731
F = FL.make_step_plan(gate, P("plan_ring_p5s02r_in.json"), ["J", "K3"], GRAPH, VIC, P("plan_ring_p5s02c.json"), SRC, "c164-3-1",
                      "ring_p5s02d", P("prep_c164_a3_1_plan_in.json"), P("prep_c164_a3_1_session.json"), goal,
                      "card 164-3-1 PROBE (fact only): step-4 rows J+K3 on 564d8cbe", keep_prev=P("plan_ring_p5s02d_prev872822f3.json"), census=CENP)
gate("ASIDE previous plan kept as plan_ring_p5s02d_prev872822f3.json == 872822f3", md5(P("plan_ring_p5s02d_prev872822f3.json")).startswith("872822f3"),
     md5(P("plan_ring_p5s02d_prev872822f3.json")))
for nm, c in F["candidates"].items():
    print("FACT PREFIX {0}: rows {1}, MAIN {2}, peak {3}, error {4}".format(nm, c["rows"], c.get("main"), c.get("peak"), c.get("error")), flush=True)
print("FACT CHOSEN {0}: actions {1}".format(F["chosen"], F["actions"]), flush=True)
gate("RC rows == 10 (J) + 9 (K3) = 19 when J+K3 is chosen, 10 when J alone", len(F["actions"]) == {"J": 10, "J+K3": 19}.get(F["chosen"]), (F["chosen"], len(F["actions"])))
PL = J(P("plan_ring_p5s02d.json"))
sf = sorted((PL.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
for s in sf:
    if s["op"] in ("delete_wire", "delete_object", "wire_remove_loose_ends"):
        stt = J(os.path.join(ROOT, s["path"]))["state"]
        print("FACT ENDSTEP n={0} {1}: w23460 rows {2}; w23519 rows {3}".format(s["n"], s["op"], sorted(r["term_uid"] for r in stt["terminals"] if r["wire_uid"] == 23460),
              sorted((r["term_uid"], r["is_source"]) for r in stt["terminals"] if r["wire_uid"] == 23519)), flush=True)
last = sf[-1]
gate("E2 last step file md5 == recorded {0} ({1})".format(last["md5"][:8], last["path"]), md5(os.path.join(ROOT, last["path"])) == last["md5"])
END = J(os.path.join(ROOT, last["path"]))["state"]
r60 = [r for r in END["terminals"] if r["wire_uid"] == 23460]
o60 = [o for o in END["objs"] if int(o["uid"]) == 23460]
r19 = [r for r in END["terminals"] if r["wire_uid"] == 23519]
for r in r60 + r19:
    print("FACT END w{0} t{1} {2} owner #{3} {4} {5}".format(r["wire_uid"], r["term_uid"], "SRC " if r["is_source"] else "SINK", r["owner_uid"], r["owner_class"], r["term_class"]), flush=True)
gate("END1 w23460 absent in the sim end graph: rows {0}, objs {1}".format([r["term_uid"] for r in r60], o60), not r60 and not o60)
snk = sorted(int(r["term_uid"]) for r in r19 if not r["is_source"])
gate("END2 w23519 source t8494, sinks exactly {{23450, 23241, 7606}}: source {0}, sinks {1}".format([r["term_uid"] for r in r19 if r["is_source"]], snk),
     snk == sorted([23450, 23241, 7606]) and [int(r["term_uid"]) for r in r19 if r["is_source"]] == [8494])
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT), [os.path.basename(q) for q in WANT if md5(q) != M0[q]])
sys.exit(gate.result())
