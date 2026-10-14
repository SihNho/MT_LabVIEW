# ---
# labview: none
# hardware: none
# ---
"""p6close_sum - offline, read-only: the p6close table (4 conditions) vs fail1 (and the latest observer run for W100), plus the
stop facts. Reads out_p6close/p6fix_legs.json + align_<TAG>.json (written by the leg chain, p6fix_align unchanged), the run
dirs' tra/cal, fail1's align_fail1_<TAG>.json (out_latest2) and leg.json (out_latest/legs/<TAG>_a1), the observer run's
align_W100OBS.json + leg.json (out_latest2). cal: p6fix_cal.py (unchanged) vs S1. Writes out_p6close/p6close_sum.json.
    py tools/bench/lean_bench/p6close_sum.py"""
import json, os, re, subprocess, sys                                                      # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import p6fix_align as PA                                                                  # noqa: E402
M = PA.M
S1 = os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928")
NEW, L1, L2 = (os.path.join(HERE, d) for d in (sys.argv[1] if len(sys.argv) > 1 else "out_p6close", "out_latest", "out_latest2"))
OBS_CONST = 20896          # lean_report_latest.md:157,181 - the observer run's start constant (picked Num - col 0), from its pick log


def leg_facts(leg_json):
    if not leg_json or not os.path.isfile(leg_json):
        return {}
    d = json.load(open(leg_json, encoding="utf-8"))
    s = json.dumps(d, default=str)
    m = re.search(r"frame=(\d+)", s)
    fd = re.search(r'"frames_delta": (\d+)', s)
    return {"frame_at_stop": int(m.group(1)) if m else None, "frames_delta": int(fd.group(1)) if fd else None}


def run_facts(run_dir, mode):
    tb = M.tra(run_dir)[1]
    c0 = tb[:, 0]
    st = np.diff(c0)
    r = {"rows": int(len(tb)), "col0_first": float(c0[0]), "col0_last": float(c0[-1]),
         "col0_max_step": float(st.max()) if len(st) else None, "col0_step_hist": {str(k): int(v) for k, v in zip(*np.unique(st, return_counts=True))}}
    out = subprocess.run([sys.executable, os.path.join(HERE, "p6fix_cal.py"), S1, run_dir], capture_output=True, text=True, encoding="utf-8")
    try:
        r["cal"] = json.loads(out.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        r["cal"] = {"error": (out.stdout + out.stderr)[-300:]}
    return r


def cond(align_json):
    a = json.load(open(align_json, encoding="utf-8"))
    al, c, t = a.get("align", {}), a.get("col0", {}), a.get("transrot", {})
    return {"rows": al.get("rows_B"), "own": "%s/%s" % (c.get("col0_own"), c.get("rows")), "xyz": "%s/%s" % (al.get("matched"), al.get("rows_B")),
            "damaged": al.get("damaged"), "strictly_increasing": al.get("strictly_increasing"), "col0_strictly_increasing": c.get("col0_strictly_increasing"),
            "span": [al.get("first_A"), al.get("last_A")], "lost": al.get("lost_in_span"), "gap_hist": al.get("gap_hist"), "lost_from_col0": c.get("lost_from_col0"),
            "s1gap_crosscheck": c.get("s1gap_crosscheck"), "transrot_post_rows": t.get("post_init_rows"), "transrot_post_differ": t.get("post_init_differ")}


if __name__ == "__main__":
    legs = json.load(open(os.path.join(NEW, "p6fix_legs.json"), encoding="utf-8"))
    out = {"gates": legs.get("gates"), "cond": {}}
    for tag in ("P62", "GAP", "W40", "W100"):
        L = legs["legs"].get(tag)
        if not L:
            out["cond"][tag] = {"missing": True}
            continue
        mode = L.get("mode")
        r = {"new": cond(os.path.join(NEW, "align_%s.json" % tag)), "new_run": run_facts(L["run_dir"], mode),
             "new_leg": leg_facts(os.path.join(L["leg_dir"], "leg.json") if L.get("leg_dir") else None),
             "attempts": L.get("attempts"), "secs": L.get("secs"), "run_dir": os.path.relpath(L["run_dir"], HERE),
             "fail1": cond(os.path.join(L2, "align_fail1_%s.json" % tag)), "fail1_leg": leg_facts(os.path.join(L1, "legs", "%s_a1" % tag, "leg.json"))}
        f1 = json.load(open(os.path.join(L1, "p6fix_legs.json"), encoding="utf-8"))["legs"].get(tag, {})
        if f1.get("run_dir") and os.path.isdir(f1["run_dir"]):
            tb = M.tra(f1["run_dir"])[1]
            r["fail1_col0_last"] = float(tb[-1, 0])
        out["cond"][tag] = r
    ob = json.load(open(os.path.join(L2, "p6fix_legs.json"), encoding="utf-8"))["legs"]["W100OBS"]
    tb = M.tra(ob["run_dir"])[1]
    olf = leg_facts(os.path.join(ob["leg_dir"], "leg.json"))
    out["obs"] = {"cond": cond(os.path.join(L2, "align_W100OBS.json")), "leg": olf, "col0_last": float(tb[-1, 0]), "const": OBS_CONST,
                  "last_saved_num": OBS_CONST + float(tb[-1, 0]), "end_lag": olf.get("frame_at_stop") - (OBS_CONST + float(tb[-1, 0]))}
    if os.path.basename(NEW) == "out_p6close":                                          # a dry test on another dir only prints
        json.dump(out, open(os.path.join(NEW, "p6close_sum.json"), "w", encoding="utf-8"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str))
