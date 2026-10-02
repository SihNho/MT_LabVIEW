r"""selftest_c133_6_fr - card 133-6 step 0, OFFLINE (no LabVIEW): the FR gate's base-frame set after PD285(b).
Takes the `frames` / `basef` lambdas TEXTUALLY from each recipe (so the test checks the recipe code, not a copy) and evaluates
the FR condition `on and set(on) <= bf and frames(end) == bf` on:
  F1 133-5's case: on = [27641, 27722, 32464] (stage_d1_ring_p3b2a_scratch.log:350) -> PASS with basef, FAIL with the old
     terminal-only set (reproduces 133-5);
  F2 a NEW frame (uid 999999 added to `on`) -> FAIL;
  F3 the simulator's end state (plan's last step file) satisfies frames(end) == basef(BASE) (the gate's second clause, as E1
     makes real == sim);
for recipe a (base sim/ring_p3b2_base_real_fsmap.json) and recipe b (its current base, provisional until --rebase).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/selftest_c133_6_fr.log -- py -u tools/bench/selftest_c133_6_fr.py"""
import json, os, re, sys                                                            # noqa: E401
B = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(B))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
ok = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:600]), flush=True)


def lambdas(path):
    src = open(path, encoding="utf-8").read()
    ns = {}
    for nm in ("frames", "basef"):
        m = re.search(r"^{0} = lambda .*$".format(nm), src, re.M)
        exec(m.group(0).split("#")[0], ns)                                          # noqa: S102 - the recipe's own line
    return ns["frames"], ns["basef"], src


def fr(on, bf, endf):
    return bool(on) and set(on) <= bf and endf == bf


for tag, rp, pp in (("a", "tools/recipes/stage_d1_ring_p3b2a.py", "tools/bench/plan_ring_p3b2a.json"),
                    ("b", "tools/recipes/stage_d1_ring_p3b2b.py", "tools/bench/plan_ring_p3b2b.json")):
    frames, basef, src = lambdas(os.path.join(ROOT, rp))
    gate("{0}: FR uses basef(BASE) (one line), no other FR change".format(tag), src.count("bf = basef(BASE)") == 1 and "bf = frames(BASE" not in src)
    pl = J(pp); BASE = J(pl["finalized"]["base"]["path"])
    end = J(pl["finalized"]["step_files"][-1]["path"])["state"]["terminals"]
    bf, old = basef(BASE), frames(BASE["terminals"])
    fsl = sorted(int(f) for fl in BASE["fs_frames"].values() for f in fl)
    print("  FACT  {0}: base {1}; fs_frames {2}; 27641 in terminal frames {3}; |bf| {4} |old| {5}".format(
        tag, pl["finalized"]["base"]["path"], fsl, 27641 in old, len(bf), len(old)), flush=True)
    on = [27641, 27722, 32464]
    gate("{0} F1 133-5's case on={1} passes with basef".format(tag, on), fr(on, bf, frames(end)), sorted(set(on) - bf))
    if tag == "a":
        gate("a F1' the old terminal-only set FAILS it (reproduces 133-5, log:350)", not (set(on) <= old), sorted(set(on) - old))
    gate("{0} F2 a NEW frame 999999 fails".format(tag), not fr(on + [999999], bf, frames(end)))
    gate("{0} F3 sim end frames == basef(BASE)".format(tag), frames(end) == bf, {"end-bf": sorted(frames(end) - bf), "bf-end": sorted(bf - frames(end))})
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), [])), flush=True)
sys.exit(1 if nf else 0)
