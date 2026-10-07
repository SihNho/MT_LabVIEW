# ---
# labview: none
# hardware: none
# ---
r"""lb_recollect - re-run lb_collect for finished arms with EXACTLY the arguments lb_run.collect() passes (lb_run.py:226-236),
without importing lb_run (its scope is labview: build; this file only reads JSON and runs the LabVIEW-free collector).
Card chat-T3 item 4: the collector's cost rule changed (lb_collect.costs), so every arm is re-collected. The previous
<arm>.json is kept as <arm>.json.pre_t3 and the per-arm $ delta is printed. Ends with a C6 RESULT line.
Usage: py tools/bench/livebench/lb_recollect.py A B A13 A13K
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(os.path.dirname(HERE)))
import protocol  # noqa: E402


def main(arms):
    ARMS = json.load(open(os.path.join(HERE, "arms.json"), encoding="utf-8"))
    P, F = [], []
    for arm in arms:
        S = json.load(open(os.path.join(HERE, "setup_%s.json" % arm), encoding="utf-8"))
        R = json.load(open(os.path.join(HERE, "%s_run.json" % arm), encoding="utf-8"))
        out_json = os.path.join(HERE, "%s.json" % arm)
        old = json.load(open(out_json, encoding="utf-8")) if os.path.exists(out_json) else None
        if old is not None and not os.path.exists(out_json + ".pre_t3"):
            shutil.copyfile(out_json, out_json + ".pre_t3")
        c = subprocess.run([sys.executable, "-u", os.path.join(HERE, "lb_collect.py"), "--worktree", S["worktree"], "--arm", arm,
                            "--setup-commit", S["setup_commit"], "--t0", str(R["t0"]), "--t1", str(R["t1"]),
                            "--claudedev-out", S["claudedev_out"], "--writelog", S["env"]["LIVEBENCH_WRITELOG"],
                            "--snapshots", os.path.join(HERE, "%s_snapshots.json" % arm), "--flow", S["flow"],
                            "--extras", ",".join(S["extras"]), "--start-vi", json.dumps(ARMS["start_vi"]),
                            "--agent", ARMS["arms"][arm].get("agent", "claude-code"), "--out", out_json])
        if c.returncode != 0 or not os.path.exists(out_json):
            F.append("collect %s rc %s" % (arm, c.returncode))
            continue
        new = json.load(open(out_json, encoding="utf-8"))
        u0 = (old or {}).get("usd", {}).get("total_usd")
        u1 = new["usd"]["total_usd"]
        print("RECOLLECT %s total_usd %s -> %s (sessions %s, peers %s, excluded %s in %d session(s): %s)" % (
            arm, u0, u1, new["usd"]["sessions_usd"], new["usd"]["peers_usd"], new["usd"]["excluded_usd"],
            len(new["usd"]["excluded"]), [(x["log"], round(x["usd"], 2), x["started"], x["why"]) for x in new["usd"]["excluded"]]),
            flush=True)
        same = [k for k in ("plan_progress", "cycles", "cards", "labview_runs", "handbacks", "adoptions")
                if old is not None and json.dumps(old.get(k), sort_keys=True) == json.dumps(new.get(k), sort_keys=True)]
        print("RECOLLECT %s unchanged sections %s" % (arm, same), flush=True)
        P.append("collect %s" % arm)
    print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None)))
    return 0 if not F else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or ["A", "B", "A13", "A13K"]))
