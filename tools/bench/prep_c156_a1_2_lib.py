# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_156-a1-2.md
# ---
r"""prep_c156_a1_2_lib - card 156-a1-2 (OFFLINE, json only): the helpers the card's measure, regression and self-test scripts
share, CALLED by prep_c156_a1_2_measure.py, prep_c156_a1_2_regress.py and selftest_c156_passwire.py (never pasted).

WHAT EXISTED FIRST: prep_c155_a1_1_regress.py / prep_c155_a1_1_suite.py do the compile-all and the suite run, but are
card-155-specific (fixed output paths, no parameters), so they cannot be called; their logic is re-cut here as
parametric functions (OPEN in the facts: a shared tools/ module would own them; outside this card's write globs).
The K3/K4 rows are the ones the 156-a1-1 maker wrote into plan_ring_p5s02r_in.json (d84634bd, prep_c156_a1_1_mk.py:249-264):
the first 60 actions of that file are plan_ring_p5s02r_all.json (15da9551) and the K groups follow it.
Self-test: tools/bench/selftest_c156_passwire.py (k_actions, sim_plan on recorded data)."""
import copy
import glob
import hashlib
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS  # noqa: E402
import stagexec as SX  # noqa: E402

GRAPH = os.path.join(HERE, "graph_ring_p5s01_20261009_125622.json")
RIN = os.path.join(HERE, "plan_ring_p5s02r_in.json")
ALLF = os.path.join(HERE, "plan_ring_p5s02r_all.json")
SIMD = os.path.join(HERE, "sim", "ring_p5s02pw")
K_IDS = {"K3": ["sr_k3", "c_k3i", "w_k3i", "t_k3o", "w_k3out", "w_k3r", "t_k3i", "w_k3l", "w_k3pass"], "K3f": ["w_k3f"],
         "K4": ["sr_k4", "c_k4i", "w_k4i", "t_k4o", "w_k4out", "w_k4r", "t_k4i", "w_k4l", "w_k4pass"], "K4f": ["w_k4f"]}
SUITE = [("stagexec", ["tools/stagexec.py", "selftest"]), ("stagesim", ["tools/stagesim.py", "selftest"]),
         ("c155_basecase_frame", ["tools/bench/selftest_c155_basecase_frame.py"]),
         ("c120_caseshape", ["tools/bench/selftest_c120_caseshape.py", "tools/bench/graph_qrt_pool_20260928.json"]),
         ("case_frame_c124", ["tools/bench/selftest_case_frame_c124.py"]),
         ("stagexec_gate", ["tools/bench/selftest_stagexec_gate.py"]),
         ("stagesim_tunnel_naming", ["tools/bench/selftest_stagesim_tunnel_naming.py"]),
         ("fs_c126", ["tools/bench/selftest_fs_c126.py"]), ("t6_regress", ["tools/bench/selftest_t6_regress.py"])]


def md5(p):
    """md5 hex digest of file p."""
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def jload(p):
    """The JSON object stored at p (utf-8)."""
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def k_actions(groups=("K3", "K3f", "K4", "K4f"), pass_frame=None):
    """(top-level plan dict without actions, action list): the 60 all-plan actions of plan_ring_p5s02r_in.json followed by
    the K groups named in `groups` (rows as the 156-a1-1 maker wrote them). pass_frame=None keeps the pass wires as written
    (frameless dst); a frame name ('True') puts `frame` on the pass wire's DST end (OK<k>.inner in that frame) - the plan
    field card 156-a1-2 adds. Self-test: selftest_c156_passwire.py."""
    p = jload(RIN)
    acts = copy.deepcopy(p["actions"])
    head = acts[:60]
    byid = dict((a["id"], a) for a in acts[60:])
    out = list(head)
    for g in groups:
        for i in K_IDS[g]:
            a = copy.deepcopy(byid[i])
            if pass_frame is not None and i.endswith("pass"):
                a["dst"] = {"uid": a["dst"].split(".", 1)[0], "side": "inner", "frame": pass_frame}
            out.append(a)
    top = dict((k, v) for k, v in p.items() if k != "actions")
    return top, out


def sim_plan(top, acts, name, route_check=False):
    """stagesim.simulate of `top` + `acts` written to tools/bench/sim/ring_p5s02pw/<name>/plan_<name>_in.json on the P5-1 graph
    (6716c499); returns the simulate() result dict. Self-test: selftest_c156_passwire.py."""
    d = os.path.join(SIMD, name)
    os.makedirs(d, exist_ok=True)
    pin = os.path.join(d, "plan_{0}_in.json".format(name))
    with open(pin, "w", encoding="utf-8") as f:
        json.dump(dict(top, stage=name, actions=acts), f, indent=1)
    return SS.simulate(pin, GRAPH, out_root=d, plan_out_dir=d, log=lambda *x: None, route_check=route_check)


def last_state(R):
    """The simulated state of the last step a simulate() result R recorded (the state BEFORE a failing action)."""
    return jload(R["steps"][-1]["file"]["path"])["state"]


def term_brief(r):
    """(term_uid, owner_uid, owner_class, term_class, frame_diagram, wire_uid) of a terminal row."""
    return (r["term_uid"], r["owner_uid"], r["owner_class"], r["term_class"], r.get("frame_diagram"), r.get("wire_uid"))


def compile_all(pattern="plan_*.json"):
    """{repo-relative plan path: {md5, ops} | {md5, error} | {skip}} - stagexec.compile_plan over every stored plan matching
    tools/bench/<pattern> (the 155-a1-1 regression read, prep_c155_a1_1_regress.py:30-43, made callable)."""
    res = {}
    for p in sorted(glob.glob(os.path.join(HERE, pattern))):
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        try:
            plan = jload(p)
            if not isinstance(plan, dict) or "actions" not in plan:
                res[rel] = {"skip": "no actions"}
                continue
            res[rel] = {"md5": md5(p), "ops": SX.compile_plan(plan)}
        except Exception as e:  # noqa: BLE001 - the error text IS the record
            res[rel] = {"md5": md5(p), "error": "{0}: {1}".format(type(e).__name__, e)}
    return json.loads(json.dumps(res, sort_keys=True, default=str))


def run_suite(tag, outdir=HERE):
    """[(name, rc, pass_lines, fail_lines, last RESULT/summary line)] - each SUITE self-test run as a child (offline), its
    full output written to <outdir>/prep_c156_a1_2_suite_<tag>_<name>.out (the 155-a1-1 suite read, made callable)."""
    rows = []
    for name, cmd in SUITE:
        p = subprocess.run([sys.executable, "-u"] + cmd, cwd=ROOT, capture_output=True, text=True, timeout=900,
                           encoding="utf-8", errors="replace")
        out = p.stdout + p.stderr
        with open(os.path.join(outdir, "prep_c156_a1_2_suite_{0}_{1}.out".format(tag, name)), "w", encoding="utf-8") as f:
            f.write(out)
        npass = len(re.findall(r"^\s*(?:GATE )?PASS\b", out, re.M))
        nfail = len(re.findall(r"^\s*(?:GATE )?FAIL\b", out, re.M))
        res = [ln for ln in out.splitlines() if ln.startswith("RESULT") or re.search(r"\b\d+ */ *\d+\b", ln)]
        rows.append((name, p.returncode, npass, nfail, (res[-1] if res else "")[:300]))
    return rows
