r"""diag_c101_resim - card 101-3, PD213(h)(2)-(3). Pure Python, no LabVIEW.
(A) context.owners of stageplan_disp_r4_open.json := tools/bench/sim/disp/s1_owners.json (the S1 map read from
    D1_s1_copy.vi by diag_c101_owners.py; replaces the D1_k stand-in). Nothing else in the plan changes.
(B) re-simulate with the card-101-3 stagesim (a created loop's body owns the measured unnamed i/cond rows) -> plan_disp.json.
(C) REPLAY TEST: the simulated new-object set of plan ops 1-2 (step_00 -> step_01 -> step_02, grouped as
    stagexec.bind_new groups them BEFORE its bind['diag'] exclusion: V.node_of / V.node_class of rows whose node is a new
    negative uid) == the REAL E1 set of stage_d1_disp_r2.log:57 ({'Diagram': 1}, owners [23073]) exactly; both listed.
(D) bind_new (card-101-3 version) on op 2 with bind['diag'] = {sim body: 23073} and the MODEL's two rows renamed onto #23073
    (a MODEL of the real read - the real rows were never logged, c100-6-r2.md s3) binds no object and both body rows.
PRIOR ART: diag_c100_6_resim2.py (same A/B shape), stagexec.bind_new / compare. PREDICTION: R1 validates; R2 only
context.owners changed; R3 FINAL; R4 end cdiff rows == the 21 open_rows; REPLAY equal; D1 made {} + 2 term bindings.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c101_resim.log -- py -u tools/bench/diag_c101_resim.py"""
import collections, copy, json, os, re, sys                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol           # noqa: E402
import stagesim as SS     # noqa: E402
import stagexec as SX     # noqa: E402
import vigraph as V       # noqa: E402

R4O = os.path.join(HERE, "sim", "disp", "stageplan_disp_r4_open.json")
OWN = "tools/bench/sim/disp/s1_owners.json"
PO = os.path.join(HERE, "sim", "disp", "plan_disp.json")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


own = json.load(open(os.path.join(ROOT, OWN), encoding="utf-8"))
gate("R0 s1_owners.json is S1's (md5 field 3e3d23ce...)", own.get("md5") == "3e3d23cefd3a334001aa9d6156bf1aee", own.get("md5"))
old = json.load(open(R4O, encoding="utf-8"))
new = copy.deepcopy(old)
new["context"] = dict(old.get("context") or {}, owners={"path": OWN})
gate("R2 only context.owners changed (or already set by the first pass)",
     [k for k in set(old) | set(new) if old.get(k) != new.get(k)] in (["context"], []) and
     dict(new["context"], owners=None) == dict(old["context"], owners=None), new["context"])
ok, why = protocol.validate_obj(new)
gate("R1 validates under the installed schema", ok, why)
S = None
if ok:
    json.dump(new, open(R4O, "w", encoding="utf-8"), indent=1)
    S = SS.simulate(R4O, os.path.join(ROOT, new["base"]["path"]), out_root=os.path.join(HERE, "sim"),
                    plan_out_dir=os.path.join(HERE, "sim", "disp"), log=lambda *_a: None)
    gate("R3 simulates FINAL", S["final"], (S["failed"], S["undecided"], S["first_divergent"]))
    want = sorted(set((int(r["node"]), r["term"]) for r in new["open_rows"]))
    got = sorted(set((int(k.split("|")[0]), k.split("|")[2]) for k in S["end_cdiff_rows"] or []))
    print("  FACT end cdiff rows ({0}): {1}".format(len(S["end_cdiff_rows"] or []), S["end_cdiff_rows"]), flush=True)
    gate("R4 end cdiff rows == the {0} declared open_rows".format(len(want)), got == want,
         {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))})
if S is not None and S["final"]:
    P = json.load(open(PO, encoding="utf-8"))
    st = dict((f["n"], json.load(open(os.path.join(ROOT, f["path"]), encoding="utf-8"))["state"]) for f in P["finalized"]["step_files"][:3])
    sp = set(V.node_of(r) for r in st[1]["terminals"])
    new_sim = collections.OrderedDict()
    for r in st[2]["terminals"]:
        n = V.node_of(r)
        if n < 0 and n not in sp:
            new_sim.setdefault(n, []).append(r)
    sim_set = dict(collections.Counter(V.node_class(rs[0]) for rs in new_sim.values()))
    sim_rows = dict((n, sorted((r["term_class"], r["is_source"], r["term_name"]) for r in rs)) for n, rs in new_sim.items())
    log = open(os.path.join(HERE, "stage_d1_disp_r2.log"), encoding="utf-8").read()
    m = re.search(r"simulated new objects (\{.*?\}) != real new objects (\{.*?\}) \(real owners (\[.*?\])\)", log)
    real_set, real_owners = eval(m.group(2)), json.loads(m.group(3))                       # noqa: S307 (a logged dict literal)
    step1_diag = sorted(set(V.node_of(r) for r in st[1]["terminals"] if V.node_class(r) == "Diagram"))
    print("  FACT REPLAY sim new objects ops 1-2 {0} rows {1}; OLD sim (stage_d1_disp_r2.log:57) {2}; REAL {3} owners {4}".format(
        sim_set, sim_rows, m.group(1), real_set, real_owners), flush=True)
    gate("REPLAY sim of plan ops 1-2 new-object set == real E1 set of stage_d1_disp_r2.log exactly",
         sim_set == real_set and len(new_sim) == len(real_owners), {"sim": sim_set, "real": real_set})
    sb = P and st[2]["sym"]["new:DL1.body"]
    rows_m = [dict(r, owner_uid=23073, frame_diagram=23073, term_uid=990000 + i) for i, r in enumerate(new_sim.get(sb, []))]
    prev_real = [dict(r) for r in st[1]["terminals"] if r["term_uid"] > 0]
    bind = {"obj": {st[2]["sym"]["new:DL1"]: 23047}, "term": {}, "diag": {sb: 23073}}
    try:
        made = SX.bind_new(prev_real, prev_real + rows_m, st[1]["terminals"], st[2]["terminals"], bind)
        gate("D1 bind_new with bind['diag'] (MODEL real rows on #23073): no object bound, both body rows bound",
             made == {} and sorted(bind["term"].values()) == sorted(r["term_uid"] for r in rows_m) and len(rows_m) == 2,
             {"made": made, "term": bind["term"]})
    except SX.ExecStop as e:
        gate("D1 bind_new with bind['diag'] (MODEL real rows on #23073): no object bound, both body rows bound", False, str(e))
    # card 101-3 run r3: op 2 real == sim (STEPX 02 diff 0); op 3 (create For) stopped on real {'Tunnel': 1}. Replay op 3
    # as the NEW bind_new counts it (the For object and its body are bound by the create's return and excluded).
    s3 = json.load(open(os.path.join(ROOT, P["finalized"]["step_files"][3]["path"]), encoding="utf-8"))["state"]
    sp2 = set(V.node_of(r) for r in st[2]["terminals"])
    excl = {s3["sym"]["new:DLF1"], s3["sym"]["new:DLF1.body"]}
    new3 = collections.OrderedDict()
    for r in s3["terminals"]:
        n3 = V.node_of(r)
        if n3 < 0 and n3 not in sp2 and n3 not in excl:
            new3.setdefault(n3, []).append(r)
    set3 = dict(collections.Counter(V.node_class(rs[0]) for rs in new3.values()))
    body3 = sorted((r["term_class"], r["is_source"], r["term_name"]) for r in s3["terminals"] if V.node_of(r) == s3["sym"]["new:DLF1.body"])
    log3 = open(os.path.join(HERE, "stage_d1_disp_r3.log"), encoding="utf-8").read()
    m3 = re.search(r"simulated new objects (\{.*?\}) != real new objects (\{.*?\}) \(real owners (\[.*?\])\)", log3)
    m2 = re.search(r"STEPX 02 create .* diff (\d+)", log3)
    real3, own3 = eval(m3.group(2)), json.loads(m3.group(3))                                # noqa: S307 (a logged dict literal)
    print("  FACT REPLAY op 3 sim new objects {0} rows {1}; For body rows {2}; OLD sim (stage_d1_disp_r3.log:69) {3}; REAL {4} "
          "owners {5}; r3 STEPX 02 diff {6}".format(set3, dict((n, sorted((r["term_class"], r["is_source"], r["term_name"])
                                                                          for r in rs)) for n, rs in new3.items()),
                                                    body3, m3.group(1), real3, own3, m2 and m2.group(1)), flush=True)
    gate("REPLAY3 sim of plan op 3 new-object set == real E1 set of stage_d1_disp_r3.log exactly; op 2 real diff 0 in r3",
         set3 == real3 and len(new3) == len(own3) and m2 is not None and m2.group(1) == "0", {"sim": set3, "real": real3})
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
arts = [{"path": os.path.relpath(p, ROOT), "md5": SS.md5_file(p)} for p in (R4O, PO)]
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
