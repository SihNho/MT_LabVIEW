r"""card 126-3 (PD253(c)(e)) - OFFLINE self-test of the Flat Sequence plan support in tools/stagesim.py + tools/stagexec.py.
No LabVIEW, no COM: imports stagesim / stagexec / vigraph only.

WHAT EXISTED FIRST: stagesim had no FlatSequence create, no Add Frame, and refused a cross-diagram wire (op_wire
same_diagram); stagexec had routes for case/loop creators and connect_term_uid R1/R2 only. Facts used: card 126-1's run
(tools/bench/diag_c125_5_fsscr.log, 15/0) and its plan (diag_c125_5_fsscr_plan.json), census_samples.json.

PREDICTION CONTRACT (gates):
 S1 the fsscr plan, re-written as stageplan/1 on the P3a base graph, simulates every action (6/6, no error)
 S2 frame order: create + add(after f0) + add(after f1) -> new frames at index 1 then 2, the first stays leftmost
    (diag_c125_5_fsscr.log:32 [27641, 28470, 27722])
 S3 census of the FS steps == FlatSequence 1 + Diagram 3 (log:38), from the effects AND from the state delta
 S4 cross-frame wire census == FSIT 2, Terminal 4, Wire 3 (log:47-56) from the effect AND the state delta; PROVISIONAL tag
 S5 the 6 rows on the 3 new wires == log:57 (class, direction, frame) with sim frames mapped to 27641/28470, owner 27219
 S6 vigraph.build4 on the end state: ONE fs edge for the new tunnel (step 4b exact faces) and const -> x reachable
 S7 FSIT addressing: owner uid + frame ('f<k>', '#<diagram>') resolves; no frame / a non-face frame / a name -> SimError
 S8 refusals: non-adjacent frames, an already-wired source (both UNMEASURED) -> SimError naming the gap
 X1 stagexec.compile_plan: routes fs_create, fs_frame, fs_frame, primitive, primitive, connect_term_uid fs_frame_to_frame
 X2 stagexec.dry_run (nonfinal: no S1) PASS - binding, the fs binder and the step compare all run
 X3 check_symbols refuses 'new:FS1.f1' before any Add Frame and a FlatSequenceFrame on a non-FS
 X4 fs_wire_ops: a move_in'd base node pair across frames -> fs_frame_to_frame; a `frame` end -> fs_face
Ends with a RESULT line.
"""
import collections
import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol          # noqa: E402
import stagesim as SS    # noqa: E402
import stagexec as SX    # noqa: E402
import vigraph as V      # noqa: E402

GRAPH = "tools/bench/graph_ring_p3a_20261001_190155.json"
PASS, FAIL, first = [0], [0], [None]


def gate(label, ok, detail=""):
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]))
    if ok:
        PASS[0] += 1
    else:
        FAIL[0] += 1
        first[0] = first[0] or label


def plan(actions, stage="selftest_fs_c126"):
    return {"schema": "stageplan/1", "stage": stage, "goal": "card 126-3 replay of card 126-1's fsscr scratch (diag_c125_5_fsscr_plan.json)",
            "base": {"path": GRAPH, "md5": SS.md5_file(os.path.join(ROOT, GRAPH))}, "actions": actions}


ACTS = [
    {"op": "create", "id": "C-1", "class": "FlatSequence", "as": "FS1", "diagram": 27219, "why": "fsscr C-1: struct_copy_nested(fs_donor) onto case #22694 False"},
    {"op": "create", "id": "C-2a", "class": "FlatSequenceFrame", "diagram": "new:FS1.f0", "why": "fsscr C-2: Add Frame after 0"},
    {"op": "create", "id": "C-2b", "class": "FlatSequenceFrame", "diagram": "new:FS1.f1", "why": "fsscr C-2: Add Frame after 1"},
    {"op": "create", "id": "C-3a", "class": "DigitalNumericConstant", "as": "K1", "diagram": "new:FS1.f0", "prim": "const",
     "donor": {"donor": "DonorSRInit_v0.vi", "uid": 248}, "terminals": [{"name": "", "is_source": True}]},
    {"op": "create", "id": "C-3b", "class": "Comparison", "as": "MM1", "diagram": "new:FS1.f1", "prim": "Max & Min",
     "terminals": [{"name": "x", "is_source": False}]},
    {"op": "wire", "id": "W-1", "as": "FT1", "src": {"uid": "new:K1", "term": ""}, "dst": {"uid": "new:MM1", "term": "x"}},
]


def main():
    tmp = tempfile.mkdtemp(prefix="c126_3_fs_")
    try:
        pp_in = os.path.join(tmp, "plan_in.json")
        with open(pp_in, "w", encoding="utf-8") as f:
            json.dump(plan(ACTS), f, indent=1)
        ok, why = protocol.validate_obj(plan(ACTS))
        gate("S0 the replay plan validates against stageplan/1 (no schema change)", ok, why)
        S = SS.simulate(pp_in, os.path.join(ROOT, GRAPH), out_root=tmp, plan_out_dir=tmp, log=lambda *a: None, route_check=False)
        steps = [s for s in S["steps"] if s["n"]]
        gate("S1 6/6 actions simulated, no error", S["failed"] is None and len(steps) == 6, S["failed"])
        st = [json.load(open(s["file"]["path"], encoding="utf-8")) for s in S["steps"]]
        e = [x.get("effect") or {} for x in st]
        end = st[-1]["state"]
        fs = end["sym"]["new:FS1"]
        fr = end["fs_frames"][str(fs)]
        gate("S2 frames left->right: f0 kept, add(0,T) new at 1, add(1,T) new at 2 (log:32)",
             fr == [e[1]["frames"][0], e[2]["new_frame"], e[3]["new_frame"]] and e[2]["new_index"] == 1 and e[3]["new_index"] == 2
             and end["sym"]["new:FS1.f1"] == e[2]["new_frame"] and end["sym"]["new:FS1.f2"] == e[3]["new_frame"], (fr, e[2], e[3]))
        cen = collections.Counter()
        for x in e[1:4]:
            cen.update(x["census"])
        b0 = st[0]["state"]
        objd = collections.Counter(o["class"] for o in st[3]["state"]["objs"]) - collections.Counter(o["class"] for o in b0["objs"])
        newd = len(set(st[3]["state"]["diagrams"]) - set(b0["diagrams"]))
        gate("S3 FS census FlatSequence 1 + Diagram 3 (log:38): effects and state delta",
             dict(cen) == {"FlatSequence": 1, "Diagram": 3} and dict(objd) == {"FlatSequence": 1} and newd == 3, (dict(cen), dict(objd), newd))
        w = e[6]
        s5, s6 = st[5]["state"], end
        od = collections.Counter(o["class"] for o in s6["objs"]) - collections.Counter(o["class"] for o in s5["objs"])
        rows_new = [r for r in s6["terminals"] if r["owner_class"] == SS.FSIT_CLS and r["owner_uid"] < 0]
        wires_new = set(r["wire_uid"] for r in s6["terminals"] if r["wire_uid"]) - set(r["wire_uid"] for r in s5["terminals"] if r["wire_uid"])
        gate("S4 cross-frame wire census FSIT 2, Terminal 4, Wire 3 (log:47-56), PROVISIONAL pending 126-2",
             w.get("census") == {"FlatSequenceInnerTunnel": 2, "Terminal": 4, "Wire": 3} and dict(od) == {SS.FSIT_CLS: 2}
             and len(rows_new) == 4 and len(wires_new) == 3 and "PROVISIONAL" in w.get("model", "") and "126-2" in w.get("model", ""),
             (w.get("census"), dict(od), len(rows_new), len(wires_new), w.get("model")))
        real_of = {fr[0]: 27641, fr[1]: 28470, fr[2]: 27722, 27219: 27219}
        on = [r for r in s6["terminals"] if r["wire_uid"] in wires_new]
        got = sorted((r["owner_class"], bool(r["is_source"]), real_of.get(r["frame_diagram"], r["frame_diagram"])) for r in on)
        want = sorted([("FlatSequenceInnerTunnel", True, 27219), ("DigitalNumericConstant", True, 27641),
                       ("FlatSequenceInnerTunnel", False, 27641), ("FlatSequenceInnerTunnel", False, 27219),
                       ("Comparison", False, 28470), ("FlatSequenceInnerTunnel", True, 28470)])
        sizes = sorted(collections.Counter(r["wire_uid"] for r in on).values())
        one_owner = len(set(r["owner_uid"] for r in rows_new)) == 1 and all(r["term_name"] == "" for r in rows_new)
        gate("S5 the 6 rows on the 3 new wires == diag_c125_5_fsscr.log:57 (all 4 FSIT rows under ONE uid, names empty)",
             got == want and sizes == [2, 2, 2] and one_owner, (got, sizes, one_owner))
        G = V.build4(s6["terminals"], s6["objs"], s6["loops"], None, s6["fs_pairs"])
        ta = w["fs_frame_to_frame"]["tunnels"][0]
        fse = [x for x in G["edges"] if x[0] == "fs" and x[3] == "faces:{0}".format(ta)]
        k1, mm = s6["sym"]["new:K1"], s6["sym"]["new:MM1"]
        src = next(r for r in s6["terminals"] if r["owner_uid"] == k1)
        dst = next(r for r in s6["terminals"] if r["owner_uid"] == mm and r["term_name"] == "x")
        adj = collections.defaultdict(set)
        key = {}
        for x in G["edges"]:
            adj[x[1]].add(x[2])
        rk = dict((r["term_uid"], r) for r in s6["terminals"])
        seen, stack = set(), [V.row_key(src) if hasattr(V, "row_key") else None]
        # keys: find the key of a row through any edge that starts at the const's terminal
        ks = [x[1] for x in G["edges"] if x[0] == "wire" and x[3] == src["wire_uid"]]
        kd = [x[2] for x in G["edges"] if x[0] == "wire" and x[3] == dst["wire_uid"]]
        stack = list(ks)
        while stack:
            u = stack.pop()
            if u in seen:
                continue
            seen.add(u)
            stack.extend(adj[u])
        gate("S6 vigraph.build4: ONE exact fs edge (faces:<tunnel>) and const -> Max & Min x reachable through it",
             len(fse) == 1 and bool(kd) and kd[0] in seen, (len(fse), ks, kd, len(seen)))
        R = lambda ad, src_=True: SS.resolve_addr(s6, ad, src_)                                     # noqa: E731
        ft = s6["sym"]["new:FT1"]
        f_out, f_in = R({"uid": "new:FT1", "frame": "f1"}), R({"uid": "new:FT1", "frame": "f0"}, False)
        f_hash = R({"uid": "new:FT1", "frame": "#{0}".format(fr[1])})
        bad = []
        for ad, s_ in (({"uid": "new:FT1"}, True), ({"uid": "new:FT1", "frame": "f2"}, True), ({"uid": "new:FT1", "term": ""}, True),
                       ({"uid": "new:FT1", "frame": "#27219"}, True)):
            try:
                R(ad, s_)
                bad.append(ad)
            except SS.SimError:
                pass
        gate("S7 FSIT faces by owner uid + frame: f1 source / f0 sink / '#<diag>'; no frame, f2, a name, the owner diagram -> SimError",
             f_out["term_uid"] == w["fs_frame_to_frame"]["faces"]["out"] and f_in["term_uid"] == w["fs_frame_to_frame"]["faces"]["in"]
             and f_hash["term_uid"] == f_out["term_uid"] and f_out["owner_uid"] == ft and not bad, (f_out["term_uid"], f_in["term_uid"], bad))
        errs = []
        for a_ in ({"op": "wire", "src": {"uid": "new:K1", "term": ""}, "dst": {"uid": "new:MM2", "term": "x"}},):
            s_ = copy.deepcopy(st[5]["state"])
            SS.op_create(s_, {"op": "create", "class": "Comparison", "as": "MM2", "diagram": "new:FS1.f2", "terminals": [{"name": "x", "is_source": False}]}, {}, None, {})
            try:
                SS.op_wire(s_, a_, SS.model_for("wire", {})[0], None, {})
                errs.append("non-adjacent accepted")
            except SS.SimError as x:
                errs.append("ADJACENT" in str(x))
        s_ = copy.deepcopy(end)
        SS.op_create(s_, {"op": "create", "class": "Comparison", "as": "MM3", "diagram": "new:FS1.f1", "terminals": [{"name": "y", "is_source": False}]}, {}, None, {})
        SS.op_create(s_, {"op": "create", "class": "Comparison", "as": "MM4", "diagram": "new:FS1.f0", "terminals": [{"name": "y", "is_source": False}]}, {}, None, {})
        SS.op_wire(s_, {"op": "wire", "src": {"uid": "new:K1", "term": ""}, "dst": {"uid": "new:MM4", "term": "y"}}, SS.model_for("wire", {})[0], None, {})
        try:
            SS.op_wire(s_, {"op": "wire", "src": {"uid": "new:K1", "term": ""}, "dst": {"uid": "new:MM3", "term": "y"}}, SS.model_for("wire", {})[0], None, {})
            errs.append("wired source accepted")
        except SS.SimError as x:
            errs.append("UNMEASURED" in str(x))
        gate("S8 non-adjacent frames and an already-wired source are refused, naming the unmeasured gap", errs == [True, True], errs)
        ops = SX.compile_plan(plan(ACTS))
        got = [(o["kind"], o.get("route") or o.get("variant")) for o in ops]
        gate("X1 compile: fs_create, fs_frame x2, primitive x2, connect_term_uid fs_frame_to_frame (0 -> 1)",
             got == [("create", "fs_create"), ("create", "fs_frame"), ("create", "fs_frame"), ("create", "primitive"),
                     ("create", "primitive"), ("connect_term_uid", "fs_frame_to_frame")]
             and ops[-1]["from_index"] == 0 and ops[-1]["to_index"] == 1 and not SX.verbs_missing("fs_create") and not SX.verbs_missing("fs_frame"), got)
        pp = os.path.join(tmp, "plan_selftest_fs_c126.json")
        logs = []
        status, msg, ex = SX.dry_run(pp, log=logs.append, require_final=False)
        rep = [(r.get("k"), r.get("op"), (r.get("diff") or {}).get("n"), r.get("bound")) for r in (ex.report if ex else [])]
        gate("X2 stagexec dry (nonfinal, no S1): PASS, every op compared with diff 0, FS / frames / tunnel bound",
             status == "PASS" and ex is not None and all((r.get("diff") or {}).get("n") == 0 for r in ex.report)
             and len(ex.bind["diag"]) >= 3, (status, (msg or "")[:400], rep))
        bad = []
        for acts in ([ACTS[0], {"op": "create", "class": "Comparison", "as": "MM9", "diagram": "new:FS1.f1"}],
                     [{"op": "create", "class": "FlatSequenceFrame", "diagram": 27219}]):
            try:
                SX.compile_plan(plan(acts))
                bad.append(acts[-1])
            except SX.ExecStop:
                pass
        gate("X3 check_symbols / create_route refuse new:FS1.f1 before Add Frame and a FlatSequenceFrame not on 'new:FS<n>.f<k>'", not bad, bad)
        A4 = [ACTS[0], ACTS[1], {"op": "move_in", "nodes": [101], "dest_diagram": "new:FS1.f0", "pos": [10, 10]},
              {"op": "move_in", "nodes": [102], "dest_diagram": "new:FS1.f1", "pos": [10, 10]},
              {"op": "wire", "as": "FT2", "src": "101.out", "dst": "102.x"},
              {"op": "wire", "src": {"uid": "new:FT2", "frame": "f1"}, "dst": "103.x"}]
        fw = SX.fs_wire_ops(A4)
        gate("X4 fs_wire_ops: move_in'd base nodes on f0/f1 -> fs_frame_to_frame; an end with `frame` -> fs_face",
             fw.get(5, {}).get("variant") == "fs_frame_to_frame" and fw.get(6, {}).get("variant") == "fs_face" and 3 not in fw, fw)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("=== GATES: {0} pass / {1} fail".format(PASS[0], FAIL[0]))
    print(protocol.result_line(protocol.make_result(PASS[0], FAIL[0], first[0])))
    return 0 if FAIL[0] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
