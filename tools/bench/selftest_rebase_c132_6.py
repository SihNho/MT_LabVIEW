r"""selftest_rebase_c132_6 - card 132-6 (PD279(b)(c), docs/d1/ring-p3b.md:95-100): stage_prerun.carry_fs + rebase's
no-write-on-failed-re-sim, on the REAL P3b-1 graph vs the recovered provisional plan_ring_p3b2.json. Offline; the real plan
is never written (copies under %TEMP%, out_root = %TEMP%). Prior art: rebind (card 132-5) binds the frames (B3 there) but
not the FS object and carries no map; stagesim.base_state kept the FS keys only for a provisional (neg) state (:303-311).
PREDICTION:
  F1 carry_fs on the real graph: created FS -1 -> the ONE new real FlatSequence object; fs_frames {FS: [27641,32464,27722]}
  F2 owners of 27641/32464/27722 -> ['FlatSequence', FS] (were ['FlatSequenceFrame', 0]); diagrams[27641] == 27219
  F3 fs_tunnels / fs_border_entries / fs_frame_inferred carry NO negative uid; twin -43 -> FSIT -42's 28333; the two
     created fs_pairs entries are added on 28333 (faces 28361/28340, swapped)
  F4 stagesim.base_state(augmented) -> fs_of(st, 27641) == (FS, 0), fs_of(st, 27722) == (FS, 2); terminals unchanged
  F5 an unbound created frame (-3 dropped from M) REFUSES (FS-CARRY)
  F6 an owners disagreement (real owners[32464] = ['Diagram', 5]) REFUSES (FS-CARRY)
  F7 rebase with a NON-final re-sim (stagesim.simulate stubbed final=False) leaves the plan file byte-identical
  F8 rebase with a FINAL re-sim (stub) writes the plan; its base is the augmented file, base md5 == file
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_rebase_c132_6.log -- py -u tools/bench/selftest_rebase_c132_6.py"""
import json, os, sys, shutil, tempfile                                              # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
R = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.dirname(B))
import protocol as P, stage_prerun as SP, stagesim as SS                           # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(R, p), encoding="utf-8"))               # noqa: E731
NP, NF = [0], [None]


def gate(name, ok, val=""):
    print("{0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(val)[:400]), flush=True)
    NP[0] += bool(ok)
    if not ok and NF[0] is None:
        NF[0] = name


PLAN = "tools/bench/plan_ring_p3b2.json"
GRAPH = os.path.join(R, "tools/bench/graph_ring_p3b1_20261002_073225.json")
plan = J(PLAN)
print("  FACT  plan {0} md5 {1} base {2}".format(PLAN, SP.md5(os.path.join(R, PLAN)), plan["base"]), flush=True)
pv = J(plan["base"]["path"])
pn = J(plan["base"]["sim_of"]["plan"])
bn = (pn.get("finalized") or {}).get("base") or pn.get("base")
bf = J(bn["path"])
rl = J("tools/bench/graph_ring_p3b1_20261002_073225.json")
info = {}
M, why = SP.rebind(bf["terminals"], pv["terminals"], rl["terminals"], prov_doc=pv, real_doc=rl, before_doc=bf, info=info)
print("  FACT  rebind why={0} M={1}".format(why, None if M is None else len(M)), flush=True)
aug, w2 = SP.carry_fs(pv, rl, bf, M, info)
fsb = info.get("fs_bound")
FS = fsb[1] if fsb else None
fm = info.get("fs_map") or {}
print("  FACT  fs_bound {0}; fs_map {1}; owners_changed {2}".format(fsb, json.dumps(fm)[:700], info.get("owners_changed")), flush=True)
gate("F1 FS -1 -> one new real FlatSequence; fs_frames {FS: [27641,32464,27722]}", aug is not None and fsb and fsb[0] == -1
     and fm.get("fs_frames") == {str(FS): [27641, 32464, 27722]}, (w2, fsb, fm.get("fs_frames")))
own = (aug or {}).get("owners") or {}
gate("F2 frame owners -> ['FlatSequence', FS]; diagrams[27641] == 27219", aug is not None and all(
    own.get(str(f)) == ["FlatSequence", FS] for f in (27641, 32464, 27722)) and fm.get("diagrams", {}).get("27641") == 27219,
     ([own.get(str(f)) for f in (27641, 32464, 27722)], fm.get("diagrams")))


def negs(x):
    if isinstance(x, dict):
        return [n for k, v in x.items() for n in negs(v) + ([int(k)] if str(k).lstrip("-").isdigit() and int(k) < 0 else [])
                ] + [n for k in x if "|" in str(k) for n in [int(p) for p in str(k).split("|") if p.lstrip("-").isdigit() and int(p) < 0]]
    if isinstance(x, list):
        return [n for v in x for n in negs(v)]
    return [x] if isinstance(x, int) and not isinstance(x, bool) and x < 0 else []


ad = ((aug or {}).get("fs_carried") or {}).get("fs_pairs_added") or []
gate("F3 FS tables carry no negative uid; twin -43 -> 28333; 2 fs_pairs added on 28333",
     aug is not None and not negs(dict((k, fm.get(k)) for k in ("fs_tunnels", "fs_border_entries", "fs_frame_inferred", "diagrams")))
     and info.get("twins") == {-43: 28333} and sorted((p["uid"], p["term_a"], p["term_b"]) for p in ad) ==
     [(28333, 28340, 28361), (28333, 28361, 28340)] and len(aug["fs_tunnel_pairs"]) == len(rl["fs_tunnel_pairs"]) + 2,
     (negs(fm)[:10], info.get("twins"), [(p["uid"], p["term_a"], p["term_b"]) for p in ad], fm.get("fs_tunnels")))
st = SS.base_state(aug or {"terminals": []})
gate("F4 base_state(augmented): fs_of 27641 -> (FS,0), 27722 -> (FS,2); terminals unchanged", aug is not None
     and SS.fs_of(st, 27641) == (FS, 0) and SS.fs_of(st, 27722) == (FS, 2) and len(st["terminals"]) == len(SS.V.dedupe_rows(rl["terminals"])[0]),
     (SS.fs_of(st, 27641), SS.fs_of(st, 27722)))
M2 = dict(M or {})
M2.pop(-3, None)
a5, w5 = SP.carry_fs(pv, rl, bf, M2, {})
gate("F5 an unbound created frame REFUSES", a5 is None and w5 and "FS-CARRY" in w5, w5)
rl6 = json.loads(json.dumps(rl))
rl6["owners"]["32464"] = ["Diagram", 5]
a6, w6 = SP.carry_fs(pv, rl6, bf, M, {})
gate("F6 an owners disagreement REFUSES", a6 is None and w6 and "FS-CARRY" in w6 and "32464" in w6, w6)
tmp = tempfile.mkdtemp(prefix="c132_6_rebase_")
real_sim = SS.simulate
try:
    pp = os.path.join(tmp, "plan_ring_p3b2.json")
    shutil.copyfile(os.path.join(R, PLAN), pp)
    m0 = SP.md5(pp)

    def stub(final):
        def f(plan_path, graph_path, **kw):
            p = json.load(open(plan_path, encoding="utf-8"))
            p["final"] = final
            p["finalized"] = {"base": {"path": graph_path, "md5": SP.md5(graph_path)}}
            op = os.path.join(kw["plan_out_dir"], "plan_{0}.json".format(p["stage"]))
            json.dump(p, open(op, "w", encoding="utf-8"), indent=1)
            return {"final": final, "failed": None if final else {"n": 24}, "plan_out": {"path": op, "md5": SP.md5(op)}}
        return f
    SS.simulate = stub(False)
    ok7, d7 = SP.rebase(pp, GRAPH, log=lambda s: print("  LOG   " + s[:300], flush=True), simulate=True, out_root=tmp)
    gate("F7 non-final re-sim: plan file byte-identical, rebase FAILS", not ok7 and SP.md5(pp) == m0 and "NOT written" in d7, (ok7, d7[-200:]))
    SS.simulate = stub(True)
    ok8, d8 = SP.rebase(pp, GRAPH, log=lambda s: None, simulate=True, out_root=tmp)
    n8 = json.load(open(pp, encoding="utf-8"))
    bp = n8["base"]["path"]
    bp = bp if os.path.isabs(bp) else os.path.join(R, bp)
    gate("F8 final re-sim: plan written, base = augmented file, md5 matches", ok8 and SP.md5(pp) != m0 and n8.get("final") is True
         and bp.endswith("ring_p3b2_base_real_fsmap.json") and SP.md5(bp) == n8["base"]["md5"]
         and "fs_carried" in json.load(open(bp, encoding="utf-8")), (ok8, d8[-160:], n8["base"]))
finally:
    SS.simulate = real_sim
    shutil.rmtree(tmp, ignore_errors=True)
NT = 8
print(P.result_line(P.make_result(NP[0], NT - NP[0], NF[0])), flush=True)
sys.stdout.flush()
os._exit(0 if NP[0] == NT else 1)
