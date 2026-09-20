"""build_oploopcast_v1.py - OpLoopCast_v1.vi = OpLoopCast_v0 + ForLoop 'Is Parallelism Enabled?' 6362004 and 'Number of
Static Parallel Instances' 6362005 (single-property nodes on the TMSC output, branch) with scalar indicators + error
outs. Plan review: archive/peer/2026-09-14-oploopcast-v1-parallelism-plan.md (parallel_enabled decisive, instances
descriptive). Labels: v0 map + {ParEnabled, ParInstances, ParEnabledErr, ParInstancesErr} -> tools/bench/oploopcast_v1_labels.json
  py tools/bgrun.py --max-min 15 --log tools/bench/build_oploopcast_v1.log -- py -u tools/recipes/build_oploopcast_v1.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpLoopCast_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpLoopCast_v1.vi")
MAP_IN = os.path.join(os.path.dirname(HERE), "bench", "oploopcast_labels.json")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "oploopcast_v1_labels.json")
P_PAR_ENABLED, P_PAR_INSTANCES = "6362004", "6362005"
T_CAST_OUT = "specific class reference"
g._run.__defaults__ = (6.0, 120.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def snap(tag=""):
    return f"{tag} Property={len(g.report_all(OP, 'Property'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}"


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def node_terms_of(uid):
    for cand in range(60):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            return None, None
        if nu == uid:
            return cand, rows
    return None, None


def make_indicator(uid, term_name):
    n, rows = node_terms_of(uid)
    t = next(r["i"] for r in rows if r["name"] == term_name)
    before = set(inds()); g.create_indicator(OP, n, t)
    new = [l for l in inds() if l not in before]
    assert len(new) == 1, f"indicator on {term_name}: {new}"
    return new[0]


def main():
    g._lv = None
    try:
        g.close_panel(OP); time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        os.remove(OP)
    donor_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(OP)

    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy not runnable.", flush=True); return 2
    tmsc = None
    for cand in range(60):
        nu, rows = g.node_terms_uid(OP, 0, cand)
        if not nu:
            break
        if any(r["name"] == T_CAST_OUT for r in rows) and any(r["name"] == "target class" for r in rows):
            tmsc = nu
    if tmsc is None:
        print("STOP: TMSC not found.", flush=True); return 2
    label_map = json.load(open(MAP_IN, encoding="utf-8"))
    for pid, pos, meaning in ((P_PAR_ENABLED, (900, 1150), "ParEnabled"), (P_PAR_INSTANCES, (900, 1300), "ParInstances")):
        u = step(f"PN ForLoop[{meaning}] {pid}", "Property +1", lambda pid=pid, pos=pos: g.build_property(OP, "VI Server:ForLoop", [(pid, False)], pos)[-1]["uid"])
        if not u:
            return 3
        step(f"wire TMSC out -> PN[{meaning}].reference (branch)", "ExecState 1",
             lambda u=u: (g.wire(OP, "Function", idx("Function", tmsc), T_CAST_OUT, "Property", idx("Property", u), "reference", branch=True), snap("after"))[1])
        purge()
        if g.exec_state(OP) != 1:
            print(f"STOP: not runnable after PN[{meaning}].", flush=True); return 3
        _n, rows = node_terms_of(u); t_data = next(r["name"] for r in rows if r["i"] == 4)
        print(f"   PN[{meaning}] data terminal {t_data!r}", flush=True)
        label_map[make_indicator(u, t_data)] = meaning
        label_map[make_indicator(u, "error out")] = meaning + "Err"
    step("auto error handling OFF", "no dialog", lambda: g.set_auto_error_handling(OP, False))
    purge(); es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True); print("label map:", json.dumps(label_map), flush=True)
    if es != 1 or any(k == "exc" for _, k in STEPS):
        print(f"\nVERDICT: BROKEN (ExecState {es}) - NOT SAVING.", flush=True); return 4
    g.save(OP)
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(label_map, f, indent=2)
    print(f"donor md5 unchanged: {hashlib.md5(open(SRC, 'rb').read()).hexdigest() == donor_md5}", flush=True)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    print("\nVERDICT: OpLoopCast_v1 BUILT and SAVED (structural only - run tools/bench/test_oploopcast_v1.py next)", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
