# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_165-3-3.md
# ---
r"""prep_c165_a3_3_pd402 - card 165-3-3 (OFFLINE, json only): adds to plan_ring_p5s02e_pred.json the PD401(b) expectation of
prep_c165_a3_2_pd401b.json (copied as facts, md5-pinned, key `pd401b`) and the PD402 expectation (key `pd402`) per stub-delete + connect pair:
the inner face has wire 0 after the delete, census after the connect in [{}, {'Wire': 1}], Is Broken? False. The step-4 PD399 driver
(prep_c164_a3_4_pd399.py) is a top-level script hard-wired to dw_23460 / rle_23519 (its lines 21, 41-56), so it cannot be called for these rows; the
shared reads are prep_c164_a2_3_lib.J / md5 / rel / wires_of and the Gate of prep_c156_a1_1_lib. Every value is READ (plan rows, base graph 2a5fa0c4,
the plan's sim step files, the pd401b file), none typed except the two row-id pairs of the PD401(b) file, which are checked against it.
PREDICTION CONTRACT: P0 pred keyed to fd23974e; F pd401b md5 2ea89c4b, keyed to the plan; per pair (dw_10362/w_k3f, dw_25232/w_k4f):
G base wire = ONE sink row on the face term (no source), face owner == pd401b's; S1 face wired at step n_del-1, wire 0 at step n_del (== pd401b
sim step); S2 face on a sourced net at the connect step and at the end, net source == pd401b's; W re-read.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c165_a3_3_pd402.log -- py -u tools/bench/prep_c165_a3_3_pd402.py"""
import json, os, sys                                                                        # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import prep_c164_a2_3_lib as LB                                                             # noqa: E402
B, J, md5, rel, ROOT = LB.B, LB.J, LB.md5, LB.rel, LB.ROOT
PLAN, PP, PDB = os.path.join(B, "plan_ring_p5s02e.json"), os.path.join(B, "plan_ring_p5s02e_pred.json"), os.path.join(B, "prep_c165_a3_2_pd401b.json")
g = LB.L.Gate(width=1200)
P, PR, PD = J(PLAN), J(PP), J(PDB)
g("P0 pred keyed to the plan md5 {0} (pin fd23974e)".format(md5(PLAN)[:8]), PR["plan"]["md5"] == md5(PLAN) and md5(PLAN).startswith("fd23974e"), PR["plan"])
g("F pd401b file {0} md5 {1} (pin 2ea89c4b) keyed to this plan; {2} pair(s)".format(rel(PDB), md5(PDB)[:8], len(PD["pairs"])),
  md5(PDB).startswith("2ea89c4b") and PD["plan"]["md5"] == md5(PLAN) and len(PD["pairs"]) == 2, PD["plan"])
A = P["actions"]
pos = dict((a["id"], n) for n, a in enumerate(A, 1))
base = J(os.path.join(ROOT, P["finalized"]["base"]["path"]))
SFN = dict((int(x["n"]), x) for x in P["finalized"]["step_files"])
st = lambda n: J(os.path.join(ROOT, SFN[n]["path"]))["state"]                               # noqa: E731
N = len(A)


def face(state, tu):
    """The terminal row of term uid `tu` in a sim / graph state (None when absent)."""
    return next((t for t in state["terminals"] if int(t["term_uid"]) == int(tu)), None)


def net_src(state, wu):
    """Source term uids of wire `wu` in a state."""
    return sorted(int(t["term_uid"]) for t in state["terminals"] if wu and t.get("wire_uid") == wu and t.get("is_source"))


out = []
for pr in PD["pairs"]:
    dw, cn = A[pos[pr["stub_delete"]] - 1], A[pos[pr["connect"]] - 1]
    w, tu = int(dw["wire_uid"]), int(cn["dst"]["term_uid"])
    rows = [t for t in base["terminals"] if t.get("wire_uid") == w]
    g("G {0}: base w{1} rows {2} = ONE sink on face t{3} (connect {4} dst), owner #{5} == pd401b #{6}".format(
      pr["stub_delete"], w, [(t["term_uid"], t["owner_uid"], bool(t.get("is_source"))) for t in rows], tu, pr["connect"], rows and rows[0]["owner_uid"], pr["face_owner"]),
      w == pr["wire"] and tu == pr["face_term"] and len(rows) == 1 and not rows[0].get("is_source") and int(rows[0]["term_uid"]) == tu
      and int(rows[0]["owner_uid"]) == pr["face_owner"])
    nd, nc = pos[pr["stub_delete"]], pos[pr["connect"]]
    f_pre, f_del = face(st(nd - 1), tu), face(st(nd), tu)
    g("S1 t{0}: wire {1} at step {2}, wire {3} at step {4} ({5}); pd401b sim steps {6}".format(tu, f_pre and f_pre.get("wire_uid"), nd - 1, f_del and f_del.get("wire_uid"),
      nd, pr["stub_delete"], pr["sim_after_delete_steps_face_wire0"]), f_pre and f_pre.get("wire_uid") == w and f_del and not f_del.get("wire_uid")
      and pr["sim_after_delete_steps_face_wire0"] == [nd])
    fc, fe = face(st(nc), tu), face(st(N), tu)
    sc, se = net_src(st(nc), fc and fc.get("wire_uid")), net_src(st(N), fe and fe.get("wire_uid"))
    g("S2 t{0}: net w{1} src {2} at step {3} ({4}); at the end net w{5} src {6}; pd401b net {7} src {8}".format(tu, fc and fc.get("wire_uid"), sc, nc, pr["connect"],
      fe and fe.get("wire_uid"), se, pr["sim_end_net_wire"], pr["sim_end_net_source_term"]),
      len(sc) == 1 and se == pr["sim_end_net_source_term"] and [fe.get("wire_uid")] == pr["sim_end_net_wire"])
    out.append({"stub_delete": pr["stub_delete"], "A_delete": 71 + nd, "connect": pr["connect"], "A_connect": 71 + nc, "wire": w, "face_term": tu,
                "face_owner": pr["face_owner"], "source": pr["source"],
                "expect_after_delete": {"face_wire": 0, "sim": {"step": nd, "face_wire": f_del.get("wire_uid")}},
                "expect_after_connect": {"census_in": pr["after_connect_census_in"], "face_on_net_of": pr["after_connect_face_on_net_of"], "is_broken": False,
                                         "sim": {"step": nc, "net_wire": fc.get("wire_uid"), "net_src": sc, "end_net_wire": fe.get("wire_uid"), "end_net_src": se}},
                "real_expect": "after {0} the inner face t{1} carries no wire; after {2} t{1} sits on the net sourced by {3}, census delta in {4}, "
                               "Wire.Is Broken? False".format(pr["stub_delete"], tu, pr["connect"], pr["source"], pr["after_connect_census_in"])})
PR["pd401b"] = {"file": {"path": rel(PDB), "md5": md5(PDB)}, "card": PD.get("card"), "pairs": PD["pairs"],
                "note": "copied as facts from card 165-3-2 (sim values; none measured in LabVIEW); the scratch (card 165-3-4) measures them"}
PR["pd402"] = {"rule": "docs/d1/ring-p5c.md PD402 (lines 140-232) + brief_165-3-3.md:25: t8776 / t24342 wire 0 after the delete, census in "
                       "[{}, {'Wire': 1}], Is Broken? False; PRIME-SKIP of both faces (stagexec 1d5309f4, diag_c165_a3_1_facts.md)",
               "pairs": out, "evidence": {"base": {"path": P["finalized"]["base"]["path"], "md5": md5(os.path.join(ROOT, P["finalized"]["base"]["path"]))},
                                          "maker": "tools/bench/prep_c165_a3_3_pd402.py"}}
json.dump(PR, open(PP, "w", encoding="utf-8"), indent=1)
W = J(PP)
g("W pred re-read: pd401b + pd402 present ({0} pairs), plan md5 unchanged".format(len(W.get("pd402", {}).get("pairs") or [])),
  len(W["pd402"]["pairs"]) == 2 and W["pd401b"]["file"]["md5"] == md5(PDB) and W["plan"]["md5"] == md5(PLAN))
print("FACT md5 {0} {1}".format(md5(PP), rel(PP)), flush=True)
sys.exit(g.result([{"path": rel(PP), "md5": md5(PP)}]))
