r"""diag_c120_g - card 120-1 G1/G3/G8 LIVE part, READ-ONLY on a byte copy of the POOL bed (D1_qrt_pool_20260928_141055.vi).
Prior art (reused, not rebuilt): diag_c118_p0.py:69-83 (read_live + k_contract_79.mloops + build_d1_v0.owner_of dump, same format
as graph_l2r2_saved_20260928.json) and :95-100 (gscript.subvis per frame diagram for SubVI callees). No type / Concatenate reader
exists (NAMES.md:470-484, result_113-3.json:15) - those are reported by the OFFLINE half diag_c120_facts.py, not probed here.
Nothing is wired, created, deleted or saved; the work copy is a scratch (deleted by Stage.close); LabVIEW killed at exit.
PREDICTION: G1 dump == R2's 5801 rows + the pool's new terminals (> 5801), every Diagram owner resolved (no '?');
G3a #6810 and #5058 are SubVI rows on the dump; their callee paths read by subvis with uid present; the pool's IMAQ Create
(new SubVI uid, not in R2) reads a path ending 'IMAQ Create.vi'; H2 bed md5 unchanged; H5 refs balanced; LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c120_g.log -- py -u tools/bench/diag_c120_g.py"""
import json, os, subprocess, sys                                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K, vigraph as V                                                 # noqa: E401,E402
g = K.g
BED, BEDM = os.path.join(g.CLAUDEDEV, "D1_qrt_pool_20260928_141055.vi"), "9353936895141d3ec2f890649c5cf22f"
OUTG, OUTJ = os.path.join(HERE, "graph_qrt_pool_20260928.json"), os.path.join(HERE, "diag_c120_g.json")
R2G = json.load(open(os.path.join(HERE, "graph_l2r2_saved_20260928.json"), encoding="utf-8"))
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(BED, BEDM, "scratch_c120_g", preload=False, deadline_min=25, reserve_s=180, out_json=OUTJ, task="card 120-1 G1/G3") if __name__ == "__main__" else None


def body(_):
    s.start(); s.scratches.append(s.work)                                          # noqa: E702  read-only: the work copy is a scratch
    s.R["H"]["handles_after_open"] = s.safe("handles after open", K.mod("bench_prep").labview_handles)[0]
    s.fact("LabVIEW handle count AFTER opening the scratch: {0!r}".format(s.R["H"]["handles_after_open"]))
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=R2G["fs_tunnel_pairs"])
    loops, BD = K.mod("k_contract_79").mloops(s, s.work), K.mod("build_d1_v0")
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo = {}, list(diags)
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        v = s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(s.work, u, strict=False), ("?", 0))[0] or ("?", 0)
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    gr = {"vi": BED, "md5": BEDM, "source": "tools/bench/diag_c120_g.py (read_live + mloops + owner_of on a byte copy of the SAVED pool bed; "
          "fs_tunnel_pairs reused from graph_l2r2_saved_20260928.json)", "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops,
          "fs_tunnel_pairs": R2G["fs_tunnel_pairs"], "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}
    DRY or (json.dump(gr, open(OUTG, "w", encoding="utf-8")), s.fact("WROTE {0} md5 {1}".format(OUTG, K.md5(OUTG))))
    T = lv["terminals"]
    s.gate("G1 dump: {0} rows (R2 saved {1}), {2} objs, {3} loops, every Diagram owner resolved".format(
        len(T), len(R2G["terminals"]), len(lv["objs"]), len(loops)),
        len(T) > len(R2G["terminals"]) and all(O[d][0] != "?" for d in diags), [d for d in diags if O[d][0] == "?"][:10])
    callees(T)


def callees(T):
    old = set(int(r["owner_uid"]) for r in R2G["terminals"])
    want = set([6810, 5058, 13938]) | set(int(r["owner_uid"]) for r in T if r["owner_class"] == "SubVI" and int(r["owner_uid"]) not in old)
    fds = sorted(set(int(r["frame_diagram"] or 0) for r in T if int(r["owner_uid"]) in want and r["owner_class"] == "SubVI"))
    DL = [int(o["uid"]) for o in g.report_all(s.work, "Diagram")]
    subs = {}
    for fd in fds:
        if fd not in DL:
            s.fact("frame diagram #{0} is not in Traverse('Diagram') - no subvis read".format(fd))
            continue
        for row in s.safe("subvis #{0}".format(fd), lambda: g.subvis(s.work, DL.index(fd), strict=False)[0], [])[0] or []:
            if int(row["uid"]) in want:
                subs[int(row["uid"])] = {"path": row.get("path"), "frame_diagram": fd}
    for u in sorted(want):
        s.fact("CALLEE #{0} -> {1}".format(u, subs.get(u)))
    s.gate("G3a callee paths read for #6810 and #5058", all(subs.get(u, {}).get("path") for u in (6810, 5058)), [subs.get(6810), subs.get(5058)])
    # run 1 (diag_c120_g.log 14:44, JEV-LADDER our-script-bug): an .llb member's path has NO '.vi' suffix ('Basics.llb\IMAQ Create')
    newic = [u for u in want - {6810, 5058, 13938} if str((subs.get(u) or {}).get("path") or "").lower().rstrip(".vi").endswith("imaq create")]
    s.gate("G3b the pool's new SubVI is IMAQ Create (path read)", len(newic) == 1, sorted(want - {6810, 5058, 13938}))
    s.R["callees"] = dict((str(u), v) for u, v in subs.items())
    s.dump()


def gone():
    out = subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
    return "labview.exe" not in out


if __name__ == "__main__":
    rc = K.run(body, s)
    if not DRY:
        K.mod("stagexec").kill_labview_at_exit()
        print("  FACT  G8 LabVIEW process gone after kill: {0}".format(gone()), flush=True)
    sys.exit(rc)
