r"""probe102b - offline only. (a) the plan's OWN recorded step 11/12 effects around LoopTunnel #11363;
(b) full re-simulation on a SCRATCH out dir under the refuted node:delete rule, with the flip routine instrumented,
to locate what seeds the k12 flip of #11363 (PD214(d)1)."""
import json, os, sys, shutil, tempfile
ROOT = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS  # noqa: E402
D = os.path.join(ROOT, "tools/bench/sim/disp")
for n in (11, 12):
    d = json.load(open(os.path.join(D, "step_{0}_move_in.json".format(n)), encoding="utf-8"))
    e = d.get("effect") or {}
    w = dict((r["term_uid"], (r["wire_uid"], r["is_source"], r["owner_uid"])) for r in d["state"]["terminals"])
    print("STEP", n, "effect keys", sorted(e.keys())[:20])
    print("   tunnel_flips", e.get("tunnel_flips"), "only_source", e.get("only_source"), "bare_deleted", e.get("bare_deleted"))
    print("   model_source", d.get("model_source"), "| params only_source", (d.get("params") or {}).get("only_source"))
    print("   terms", dict((u, w.get(u)) for u in (11365, 11369, 11270, 11316, 11320, 11323)))
    print("   w11352 rows", [(r["term_uid"], r["owner_uid"], r["term_class"], r["is_source"]) for r in d["state"]["terminals"] if r["wire_uid"] == 11352])
    print("   w11374 rows", [(r["term_uid"], r["owner_uid"], r["term_class"], r["is_source"]) for r in d["state"]["terminals"] if r["wire_uid"] == 11374])

# (b) instrumented re-sim under node:delete on scratch dirs
orig = SS._flip_orphaned_output_tunnels
LOG = []


def spy(st, wires, seeds=(), needs_wired=False, reg=None):
    out = orig(st, wires, seeds, needs_wired, reg)
    if any(f["tunnel"] == 11363 for f in out):
        LOG.append({"wires": sorted(w for w in wires if w), "seeds": [(s["term_uid"], s["owner_uid"], s["wire_uid"]) for s in seeds],
                    "flipped": out, "w11374_rows": [(r["term_uid"], r["is_source"]) for r in SS.wire_rows(st, 11374)],
                    "w11352_rows": [(r["term_uid"], r["is_source"]) for r in SS.wire_rows(st, 11352)]})
    return out


SS._flip_orphaned_output_tunnels = spy
tmp = tempfile.mkdtemp(prefix="c102sim_")
R4O = os.path.join(D, "stageplan_disp_r4_open.json")
gp = os.path.join(ROOT, json.load(open(R4O, encoding="utf-8"))["base"]["path"])
for label, rule in (("keep", {"constant": "delete", "default": "keep"}), ("node:delete", {"constant": "delete", "node": "delete", "default": "keep"})):
    SS.PROVISIONAL["move_in"]["params"]["only_source"] = rule
    LOG.clear()
    out = os.path.join(tmp, label.replace(":", "_"))
    os.makedirs(out)
    S = SS.simulate(R4O, gp, out_root=os.path.join(out, "sim"), plan_out_dir=out, log=lambda *_a: None)
    print("RESIM", label, "final", S["final"], "failed", S["failed"], "first_divergent", S["first_divergent"])
    st12 = json.load(open(os.path.join(out, "sim", "disp", "step_12_move_in.json"), encoding="utf-8")) if os.path.exists(os.path.join(out, "sim", "disp", "step_12_move_in.json")) else None
    if st12 is None:
        cand = [p for p in os.popen('dir /s /b "{0}"'.format(out)).read().split("\n") if p.endswith("step_12_move_in.json")]
        st12 = json.load(open(cand[0], encoding="utf-8")) if cand else None
    if st12:
        w = dict((r["term_uid"], (r["wire_uid"], r["is_source"])) for r in st12["state"]["terminals"])
        print("   step12 flips", (st12.get("effect") or {}).get("tunnel_flips"), "terms", dict((u, w.get(u)) for u in (11365, 11369, 11270)))
    print("   FLIP-OF-11363 calls:", json.dumps(LOG, default=str)[:1500])
shutil.rmtree(tmp, ignore_errors=True)
