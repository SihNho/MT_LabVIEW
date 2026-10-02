r"""selftest_c133_1_fsroutes - card 133-1 (PD280(b)(c), PD281(c), docs/d1/ring-p3b.md:114-122,134-137). Offline, no LabVIEW.
FACT behind the fix (diag_c133_1_peek.log): stagexec.compile_plan places Flat Sequence wires from the PLAN alone
(fs_wire_ops: frames only of an FS the plan CREATES), so P3b-2's 8 crossings into P3b-1's FS compile to a plain `connect`
- not a BIND kind (stagexec.py BIND_KINDS) - and the FS outer tunnel stagesim/the backend create is never bound: the route
check's op-24 STEP-DIFF (stage_prerun_c132_6_rebase_p3b2.log:76). Fix: stagesim writes finalized.fs_routes (the border route
it applied per wire, from the graph); compile_plan uses it where fs_wire_ops is silent. Prior art: fs_wire_ops (card 126-3),
FS_VARIANT_HOW cross-check (Executor.execute), carry_fs (card 132-6). The real plan is never written (copies in %TEMP%).
PREDICTION:
  R1 SP.rebase of a temp copy of plan_ring_p3b2.json (98992a59) on the real P3b-1 graph -> ok, re-sim final
  R2 its route check PASS, 39 rows, none unroutable; the dry report holds NO 'unbound' uid on any op
  R3 finalized.fs_routes names exactly the 8 crossing actions (ids p3b_x_*); compile -> connect_term_uid fs_* on those 8
  R4 op 24 (p3b_x_i_f1) binds the created FlatSequenceOuterTunnel (a bound obj of class FSOT)
  N1 the same plan with fs_routes REMOVED compiles op 24 to `connect` and its dry run FAILS at op 24 with 'unbound'
  P1 P3b-1 (plan_ring_p3b1.json, own FS) re-simulated on its own base: final, route check PASS, compile ops == the stored
     plan's (fs_routes changes nothing where fs_wire_ops already places the wire)
    py tools/bgrun.py --material --max-min 6 --log tools/bench/selftest_c133_1_fsroutes.log -- py -u tools/bench/selftest_c133_1_fsroutes.py"""
import json, os, sys, shutil, tempfile                                              # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP, stagesim as SS, stagexec as SX           # noqa: E401,E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(R, p), encoding="utf-8"))   # noqa: E731
NP, NF = [0], [None]


def gate(name, ok, val=""):
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:600]), flush=True)
    NP[0] += bool(ok)
    if not ok and NF[0] is None:
        NF[0] = name


def kinds(pl):
    return [(o["kind"], o.get("variant")) for o in SX.compile_plan(pl)]


tmp = tempfile.mkdtemp(prefix="st_c133_1_")
try:
    tp = os.path.join(tmp, "plan_ring_p3b2.json")
    shutil.copyfile(os.path.join(R, "tools/bench/plan_ring_p3b2.json"), tp)
    print("  FACT  input plan md5 {0}".format(SP.md5(tp)), flush=True)
    ok, det = SP.rebase(tp, os.path.join(R, "tools/bench/graph_ring_p3b1_20261002_073225.json"), log=lambda *a: None,
                        out_root=tmp)
    gate("R1 rebase on the real P3b-1 graph -> ok, final", ok and "final=True" in det, det)
    pl = J(tp)
    rc = (pl.get("finalized") or {}).get("route_check") or {}
    rows = rc.get("rows") or []
    st, ff, ex = SX.dry_run(tp, log=lambda *a: None) if ok else ("SKIP", "rebase failed", None)
    unb = [(r.get("k"), r["diff"]["unbound"]) for r in (ex.report if ex else []) if (r.get("diff") or {}).get("unbound")]
    gate("R2 route check PASS, 39 rows, none unroutable; dry PASS with no unbound uid", rc.get("status") == "PASS"
         and len(rows) == 39 and not any(r.get("unroutable") for r in rows) and st == "PASS" and not unb,
         (rc.get("status"), len(rows), str(rc.get("first_fail"))[:200], st, str(ff)[:300], unb[:3]))
    fr = (pl.get("finalized") or {}).get("fs_routes") or {}
    A = pl["actions"]
    xs = [i for i, a in enumerate(A, 1) if str(a.get("id", "")).startswith("p3b_x_")]
    kk = kinds(pl) if ok else []
    print("  FACT  fs_routes {0}".format(fr), flush=True)
    print("  FACT  ops of the crossings {0}; BIND ops {1}".format(
        [(i, kk[i - 1]) for i in xs] if kk else None,
        [k for k, o in enumerate(SX.compile_plan(pl), 1) if o["kind"] in SX.BIND_KINDS] if ok else None), flush=True)
    gate("R3 fs_routes == the 8 crossing actions; each compiles to connect_term_uid fs_*", sorted(int(k) for k in fr) == xs
         and len(xs) == 8 and all(kk[i - 1][0] == "connect_term_uid" and str(kk[i - 1][1]).startswith("fs_") for i in xs),
         (sorted(fr), xs))
    r24 = next((r for r in (ex.report if ex else []) if r.get("k") == 24), {})
    oc = dict((r_["owner_uid"], r_["owner_class"]) for r_ in J(pl["finalized"]["step_files"][24]["path"])["state"]["terminals"]) if ok else {}
    gate("R4 op 24 binds the created FlatSequenceOuterTunnel", any(oc.get(int(s)) == "FlatSequenceOuterTunnel"
                                                                   for s in (r24.get("bound") or {})), (r24.get("bound"), r24.get("diff", {}).get("n")))
    pn = dict(pl)
    pn["finalized"] = dict(pl.get("finalized") or {})
    pn["finalized"].pop("fs_routes", None)
    np_ = os.path.join(tmp, "plan_nofsr.json")
    json.dump(pn, open(np_, "w", encoding="utf-8"), indent=1)
    st2, ff2, ex2 = SX.dry_run(np_, log=lambda *a: None) if ok else ("SKIP", "", None)
    gate("N1 without fs_routes: op 24 compiles to connect and the dry FAILS at op 24 with 'unbound'", ok and
         kinds(pn)[23][0] == "connect" and st2 == "FAIL" and "after real op 24" in str(ff2) and "unbound" in str(ff2), str(ff2)[:300])
    p1 = J("tools/bench/plan_ring_p3b1.json")
    p1i = dict((k, v) for k, v in p1.items() if k not in ("final", "finalized"))
    p1p = os.path.join(tmp, "ring_p3b1_in.json")
    json.dump(p1i, open(p1p, "w", encoding="utf-8"), indent=1)
    S1 = SS.simulate(p1p, os.path.join(R, p1["finalized"]["base"]["path"]), out_root=tmp, plan_out_dir=tmp, log=lambda *a: None)
    q1 = J(S1["plan_out"]["path"])
    gate("P1 P3b-1 re-sim: final, route check PASS, compile ops == the stored plan's", S1["final"]
         and (S1.get("route_check") or {}).get("status") == "PASS" and kinds(q1) == kinds(p1),
         (S1["final"], (S1.get("route_check") or {}).get("status"), len((q1.get("finalized") or {}).get("fs_routes") or {})))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
N = 6
print(P.result_line(P.make_result(NP[0], N - NP[0], NF[0])), flush=True)
