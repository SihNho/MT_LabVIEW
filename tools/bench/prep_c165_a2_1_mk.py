# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-2-1.md
# ---
r"""prep_c165_a2_1_mk - card 165-2-1 parts 4+5 (OFFLINE, json only, never launched): plan_ring_p5s02e.json = P5-2 step 5 = the longest whole-group
prefix of K3f K4 K4f of plan_ring_p5s02r_in.json 0b895983 (K3f = dw_10362 + w_k3f, K4 = sr_k4..w_k4pass, K4f = dw_25232 + w_k4f; PD400(a)(c)),
MAIN <= 675, rows <= 40, FINAL on step 4's REAL graph 2a5fa0c4 (VI 6dcd5c3d). Existing makers found and reused: prep_plan_flow_lib.make_step_plan
(ONE call, same argument shape as prep_c164_a3_1_mk.py:53-55); prep_c164_a3_1_mk.py itself is a module-level script (importing it re-runs step 4),
so it is not imported - its argument set is followed with step-5 values. Census = prep_c164_a3_1_census.json (bb30814a) with the two PD400(a) rows
added to K3f / K4f at their plan positions (the maker reads only `group` / `actions`). plan_in = plan_ring_p5s02e_in.json: gate L0 accepts
<stem>_in / _in<digits> (stagekit.plan_in_matches_stem, tools/stagekit.py:3015-3022), so no copy of r_in is made. Sources p5s02a..d: each used
symbol is bound by the adopted step that made it (creation map of the run that saved its VI); new:OK3 must equal 31803 (diag_c164_p5s02d_scratch.log:208).
PD401(b) prediction per stub-delete + connect pair -> prep_c165_a2_1_pd401b.json (the plan format has no field for it).
Part 5: sim END graph (last finalized step file): w10362 / w25232 0 terminal rows; t8776 on the wire whose source is OK3 #31803's outer terminal
(w31792 in 2a5fa0c4), t24342 on the wire whose source is OK4's outer terminal.
PREDICTION CONTRACT: M0 pins; GRP [(72,73,2),(74,82,9),(83,84,2)]; OWN/MAP (OK3 -> 31803); FRM; ROWS; STUB PASS; C K3f, K3f+K4, K3f+K4+K4f compile,
  every delete_wire a checkpoint; plan = K3f+K4+K4f (13 rows) if MAIN <= 675; PROBE / TIE / SB final True, 0 PROVISIONAL, route PASS, 0 UNROUTABLE;
  C-OUT / IDS; X8 / X17 clean; DWSTEP face wire 0 after each delete; END w10362 / w25232 0 rows, t8776 on OK3.outer's net, t24342 on OK4.outer's net;
  U pins unchanged.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/prep_c165_a2_1_mk.log -- py -u tools/bench/prep_c165_a2_1_mk.py"""
import json, os, sys                                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, rel, CD, ROOT = FL.L, FL.J, FL.md5, FL.rel, FL.CD, FL.ROOT
P = lambda n: os.path.normpath(os.path.join(B, n))                                           # noqa: E731
WANT = dict((os.path.normpath(os.path.join(ROOT, i["path"])), i["md5"]) for i in J("tools/bench/cards/task_165-2-1.json")["inputs"])
VID, VIC = os.path.join(CD, "D1_ring_p5s02d_20261010_152518.vi"), os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi")
VIA, VIB = os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"), os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi")
WANT.update({VID: "6dcd5c3d", VIC: "564d8cbe", VIA: "94ffff94", VIB: "f9ae7751", P("plan_ring_p5s02a.json"): "4284c22a",
             P("plan_ring_p5s02b.json"): "f4520b10", P("plan_ring_p5s02c.json"): "930699ec", P("graph_ring_p5s02a_20261010_032547.json"): "7ac24924",
             P("graph_ring_p5s02b_20261010_111905.json"): "431cfd83", P("graph_ring_p5s02c_20261010_131658.json"): "3d5196ab",
             P("prep_c164_a3_1_census.json"): "bb30814a"})
gate = L.Gate()
M0 = dict((p, md5(p)) for p in WANT)
gate("M0 input md5 == card / brief pins", all(M0[p].startswith(w[:8]) for p, w in WANT.items()), dict((os.path.basename(p), M0[p][:8]) for p in WANT))
OUT = P("plan_ring_p5s02e.json")
prev = md5(OUT) if os.path.isfile(OUT) else None
KEEP = P("plan_ring_p5s02e_prev{0}.json".format(prev[:8])) if prev else None
print("FACT OLD plan_ring_p5s02e.json before: {0}; plan_ring_p5s02e_in.json before: {1}".format(prev, md5(P("plan_ring_p5s02e_in.json"))
      if os.path.isfile(P("plan_ring_p5s02e_in.json")) else None), flush=True)
# census: K3f / K4f of prep_c164_a3_1_census.json + the PD400(a) stub deletes at their plan positions
NEWROWS = {"K3f": "dw_10362", "K4f": "dw_25232"}
CEN = J(P("prep_c164_a3_1_census.json"))
RA = [a["id"] for a in J(P("plan_ring_p5s02r_in.json"))["actions"]]
for c in CEN["census"]:
    if c["group"] in NEWROWS:
        old = list(c["actions"])
        c["actions"] = [i for i in RA if i in old or i == NEWROWS[c["group"]]]
        print("FACT CENSUS {0} {1} -> {2}".format(c["group"], old, c["actions"]), flush=True)
CENP = P("prep_c165_a2_1_census.json")
json.dump(CEN, open(CENP, "w", encoding="utf-8"), indent=1)
GRAPH = P("graph_ring_p5s02d_20261010_154830.json")
SRC = [{"name": "p5s02a", "plan": P("plan_ring_p5s02a.json"), "graph_after": P("graph_ring_p5s02a_20261010_032547.json"), "vi": VIA},
       {"name": "p5s02b", "plan": P("plan_ring_p5s02b.json"), "graph_after": P("graph_ring_p5s02b_20261010_111905.json"), "vi": VIB},
       {"name": "p5s02c", "plan": P("plan_ring_p5s02c.json"), "graph_after": P("graph_ring_p5s02c_20261010_131658.json"), "vi": VIC},
       {"name": "p5s02d", "plan": P("plan_ring_p5s02d.json"), "graph_after": GRAPH, "vi": VID}]
goal = lambda lo, hi, cand, ch: ("RING P5-2 step 5 (card 165-2-1, PD400(a)(c), PD401(b)): A{0}..A{1} of plan_ring_p5s02r_in.json 0b895983 (K3f/K4f = stub "
                                 "delete_wire + connect onto the kept tunnels' inner faces t8776/t24342) on the REAL 6dcd5c3d graph 2a5fa0c4; plan {2} = "
                                 "longest whole-group prefix with MAIN <= 675, rows <= 40; MAIN per prefix {3}").format(
                                 lo, hi, ch, dict((k, v.get("main")) for k, v in cand.items()))[:400]   # noqa: E731
F = FL.make_step_plan(gate, P("plan_ring_p5s02r_in.json"), ["K3f", "K4", "K4f"], GRAPH, VID, P("plan_ring_p5s02d.json"), SRC, "c165-2-1",
                      "ring_p5s02e", P("plan_ring_p5s02e_in.json"), P("prep_c165_a2_1_session.json"), goal,
                      "card 165-2-1 PROBE (fact only): step-5 rows K3f K4 K4f on 6dcd5c3d", keep_prev=KEEP, census=CENP)
if KEEP:
    gate("ASIDE previous plan kept as {0} == {1}".format(os.path.basename(KEEP), prev[:8]), md5(KEEP) == prev, md5(KEEP))
REAL = F["symbol_map"]
print("FACT SYMBOLS {0}".format(REAL), flush=True)
gate("B1 new:OK3 -> 31803 == step-4 binding record diag_c164_p5s02d_scratch.log:208 (-18: 31803)", int(REAL.get("new:OK3", REAL.get("OK3", -1))) == 31803,
     REAL)
for nm, c in F["candidates"].items():
    print("FACT PREFIX {0}: rows {1}, MAIN {2}, peak {3}, N {4}, R {5}, cps {6}, error {7}".format(nm, c["rows"], c.get("main"), c.get("peak"), c.get("N"),
          c.get("R"), c.get("cps"), c.get("error")), flush=True)
print("FACT CHOSEN {0}: actions {1}".format(F["chosen"], F["actions"]), flush=True)
gate("RC rows == 2 (K3f) / 11 (K3f+K4) / 13 (K3f+K4+K4f)", len(F["actions"]) == {"K3f": 2, "K3f+K4": 11, "K3f+K4+K4f": 13}.get(F["chosen"]),
     (F["chosen"], len(F["actions"])))
PL = J(OUT)
sf = sorted((PL.get("finalized") or {}).get("step_files") or [], key=lambda x: int(x["n"]))
FACES = {10362: 8776, 25232: 24342}
dws = {}
for s in sf:
    stt = J(os.path.join(ROOT, s["path"]))["state"]
    rows = dict((w, sorted((r["term_uid"], r["wire_uid"]) for r in stt["terminals"] if int(r["term_uid"]) == t)) for w, t in FACES.items())
    print("FACT STEP n={0} {1} {2}: face rows {3}; stub rows {4}".format(s["n"], s["op"], s.get("ids") or s.get("acts"), rows,
          dict((w, len([r for r in stt["terminals"] if int(r["wire_uid"] or 0) == w])) for w in FACES)), flush=True)
    if s["op"] == "delete_wire":
        dws[s["n"]] = rows
last = sf[-1]
gate("E2 last step file md5 == recorded {0} ({1})".format(last["md5"][:8], last["path"]), md5(os.path.join(ROOT, last["path"])) == last["md5"])
END = J(os.path.join(ROOT, last["path"]))["state"]
SYM = END.get("sym") or {}
print("FACT END sym {0}".format(dict((k, v) for k, v in SYM.items() if "OK" in str(k)))[:600], flush=True)
ok4 = SYM.get("new:OK4", SYM.get("OK4"))
OWN = {8776: ("OK3", 31803), 24342: ("OK4", ok4)}
PRED = {"card": "165-2-1", "plan": None, "pairs": []}
for w, t in FACES.items():
    stub = [r for r in END["terminals"] if int(r["wire_uid"] or 0) == w]
    sobj = [o for o in END["objs"] if int(o["uid"]) == w]
    face = [r for r in END["terminals"] if int(r["term_uid"]) == t]
    for r in stub + face:
        print("FACT END w{0} t{1} {2} owner #{3} {4} {5} {6}".format(r["wire_uid"], r["term_uid"], "SRC " if r["is_source"] else "SINK", r["owner_uid"],
              r["owner_class"], r["term_class"], r.get("term_name")), flush=True)
    gate("END-STUB w{0}: 0 terminal rows in the sim end graph (Wire object {1})".format(w, "absent" if not sobj else "present"), not stub, stub)
    fw = sorted(set(int(r["wire_uid"] or 0) for r in face))
    net = [r for r in END["terminals"] if fw and int(r["wire_uid"] or 0) == fw[0]]
    srcs = [r for r in net if r["is_source"]]
    for r in net:
        print("FACT END NET w{0} t{1} {2} owner #{3} {4} {5}".format(r["wire_uid"], r["term_uid"], "SRC " if r["is_source"] else "SINK", r["owner_uid"],
              r["owner_class"], r["term_class"]), flush=True)
    nm, ou = OWN[t]
    gate("END-FACE t{0} on one wire {1} whose ONE source is {2} #{3}'s outer terminal: {4}".format(t, fw, nm, ou, [(r["term_uid"], r["owner_uid"],
         r["term_class"]) for r in srcs]), len(fw) == 1 and fw[0] != 0 and len(srcs) == 1 and ou is not None and int(srcs[0]["owner_uid"]) == int(ou)
         and "Outer" in str(srcs[0]["term_class"]), srcs)
    dn = [n for n, rows in dws.items() if rows[w] and all(x[1] == 0 for x in rows[w])]
    PRED["pairs"].append({"stub_delete": "dw_{0}".format(w), "wire": w, "face_term": t, "face_owner": {8776: 5204, 24342: 10404}[t],
                          "connect": {8776: "w_k3f", 24342: "w_k4f"}[t], "source": "new:{0}.outer".format(nm), "source_uid_real_or_sim": ou,
                          "after_delete_face_wire": 0, "sim_after_delete_steps_face_wire0": dn,
                          "after_connect_census_in": [{}, {"Wire": 1}], "after_connect_face_on_net_of": "{0}.outer".format(nm),
                          "sim_end_net_wire": fw, "sim_end_net_source_term": [r["term_uid"] for r in srcs], "is_broken": False,
                          "el_delta": "the plan's predicted one (pred maker, card 165-2-2)"})
    gate("DWSTEP after the delete_wire step of w{0} the face t{1} has wire 0 (steps {2})".format(w, t, dn), bool(dn), dws)
PRED["plan"] = {"path": rel(OUT), "md5": md5(OUT)}
json.dump(PRED, open(P("prep_c165_a2_1_pd401b.json"), "w", encoding="utf-8"), indent=1)
gate.ARTS.append({"path": rel(P("prep_c165_a2_1_pd401b.json")), "md5": md5(P("prep_c165_a2_1_pd401b.json"))})
gate("U inputs / VI / tool pins untouched", all(md5(q) == M0[q] for q in WANT), [os.path.basename(q) for q in WANT if md5(q) != M0[q]])
sys.exit(gate.result())
