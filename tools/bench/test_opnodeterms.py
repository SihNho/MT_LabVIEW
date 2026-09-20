"""test_opnodeterms.py - FUNCTIONAL acceptance of OpNodeTerms_v0 (tools/recipes/build_opnodeterms_v0.py).

Oracle = the existing per-terminal walker (gscript.net_map, self-purging) on the SAME nodes: exact per-index tuples
(peer s3), never name sets. Prediction contract:
  T1 scratch copy of OpFPLabels_v0, diagram 0, EVERY node: op (Name, wire UID) per index == walker (name, wire uid)
     per index, same length (walker drops trailing empties; the op does not - trailing rows must be empty-name/0).
  T1b Is Source? semantics (peer s2) on primitives: Index Array `array`/`index` FALSE, `element` TRUE; Open VI
     Reference `vi path` FALSE, `vi reference` TRUE; an unwired input is FALSE with wire 0 and no error.
  T2 main VI diagram 19: walk it (oracle), find the global nodes by terminal name (Trans/Rot/Focus position), run the
     op on each; PRINT count / Name / IsSource / wire / error columns before any claim (peer s1). PREDICTION, stated
     before the run and only checked as a prediction: docs/main-vi-state.md says Trans/Rot are written at init and
     read by the motor loop, Focus written by the frame loop -> on diagram 19 predicted Trans READ (IsSource TRUE),
     Rot READ (TRUE), Focus WRITE (FALSE). A miss is a documentation finding, not a test failure - it is recorded.
  T3 handle audit 20 runs on the main VI (samples every 10, slope, post-idle).
Scratch unique per run, deleted; nothing saved; main VI by reference only.
  py tools/bgrun.py --max-min 15 --log tools/bench/test_opnodeterms.log -- py -u tools/bench/test_opnodeterms.py
"""
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpNodeTerms_v0.vi")
MAP = json.load(open(os.path.join(HERE, "opnodeterms_labels.json"), encoding="utf-8"))
LAB = {v: k for k, v in MAP.items()}
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_test_nodeterms_{os.getpid()}.vi")
for _old in [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_test_nodeterms")]:
    try:
        os.remove(os.path.join(g.CLAUDEDEV, _old))
    except OSError:
        pass
g._run.__defaults__ = (6.0, 120.0)
RESULTS = []


def rec(name, ok, detail):
    print(f"   -> {'PASS' if ok else 'FAIL'}: {name}: {detail}", flush=True)
    RESULTS.append((name, ok, detail))


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    return int(r.stdout.strip() or 0)


def errcol(vi, key):
    if key not in LAB:
        return None
    try:
        out = []
        for e in vi.GetControlValue(LAB[key]):
            e = tuple(e) if isinstance(e, (tuple, list)) else (e,)
            out.append(int(e[1]) if len(e) > 1 and e[0] else 0)
        return out
    except Exception:
        return None


def run_op(target, diagram, node):
    vi = g.op(OP)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue("index", diagram); vi.SetControlValue("index 2", node); vi.SetControlValue("index 3", 0)
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    t0 = time.time()
    g._run(vi)
    dt = time.time() - t0
    names = list(vi.GetControlValue(LAB["Name"]))
    src = [bool(x) for x in vi.GetControlValue(LAB["IsSource"])]
    wire = [int(x) for x in vi.GetControlValue(LAB["WireUID"])]
    errs = {k: errcol(vi, k) for k in ("NameErr", "SrcErr", "ConnErr", "WireErr")}
    rows = []
    for i in range(len(names)):
        rows.append({"i": i, "name": names[i], "is_source": src[i] if i < len(src) else None,
                     "wire": wire[i] if i < len(wire) else None,
                     **{k.lower(): (v[i] if v and i < len(v) else None) for k, v in errs.items()}})
    return rows, dt


def main():
    g._lv = None
    shutil.copyfile(SRC, S)
    # T1: walker oracle on the scratch (self-purging)
    nodes, _nets = g.net_map(S, 0, max_nodes=60, max_terms=24)
    n_ok = 0; n_bad = []
    for n, (uid, _l, terms) in nodes.items():
        rows, dt = run_op(S, 0, n)
        oracle = [(t, w) for _ti, t, w in terms]
        mine = [(r["name"], r["wire"]) for r in rows]
        head = mine[:len(oracle)]
        tail_ok = all(r["name"] == "" and not r["wire"] for r in rows[len(oracle):])
        if head == oracle and tail_ok:
            n_ok += 1
        else:
            n_bad.append((n, uid, oracle, mine))
        print(f"   node {n} (uid {uid}): {len(rows)} rows in {dt:.2f} s; match={head == oracle and tail_ok}", flush=True)
        for r in rows[:len(oracle) + 1]:
            print(f"      {r}", flush=True)
    rec("T1 per-index (Name, wire UID) == walker on every scratch node", not n_bad, f"{n_ok} ok, bad {n_bad[:2]}")

    # T1b Is Source? semantics on primitives + an unwired input
    checks = []
    for n, (uid, _l, terms) in nodes.items():
        names = [t for _ti, t, _w in terms]
        if {"array", "element", "index"} <= set(names):
            rows, _ = run_op(S, 0, n); by = {r["name"]: r for r in rows}
            checks.append(("IndexArray inputs FALSE / element TRUE",
                           by["array"]["is_source"] is False and by["index"]["is_source"] is False and by["element"]["is_source"] is True,
                           {k: (by[k]["is_source"], by[k]["wire"]) for k in ("array", "index", "element")}))
        if "vi reference" in names and "vi path" in names:
            rows, _ = run_op(S, 0, n); by = {r["name"]: r for r in rows}
            checks.append(("Open VI Reference: vi path FALSE / vi reference TRUE",
                           by["vi path"]["is_source"] is False and by["vi reference"]["is_source"] is True,
                           {k: (by[k]["is_source"], by[k]["wire"]) for k in ("vi path", "vi reference")}))
            unw = [r for r in rows if r["name"] and not r["wire"] and r["is_source"] is False]
            checks.append(("unwired input: IsSource FALSE, wire 0, no Name/Src error",
                           bool(unw) and all(not r["nameerr"] and not r["srcerr"] for r in unw),
                           [(r["name"], r["connerr"], r["wireerr"]) for r in unw][:4]))
    for name, ok, detail in checks:
        rec(f"T1b {name}", ok, str(detail))

    # T2 main VI diagram 19: observe the global nodes
    nodes19, _ = g.net_map(MAIN, 19, max_nodes=60, max_terms=24)
    predicted = {"Trans position": True, "Rot position": True, "Focus position": False}   # READ = IsSource TRUE
    found = {}
    for n, (uid, _l, terms) in nodes19.items():
        for _ti, t, _w in terms:
            if t in predicted:
                found[t] = (n, uid, [(tt, ww) for _a, tt, ww in terms])
    print(f"T2 global nodes on diagram 19 (walker): {found}", flush=True)
    for field, (n, uid, oracle) in found.items():
        rows, dt = run_op(MAIN, 19, n)
        data = [r for r in rows if r["name"]]
        print(f"   {field}: node {n} uid {uid}: {len(rows)} rows ({len(data)} named) in {dt:.2f} s", flush=True)
        for r in rows[:max(3, len(data))]:
            print(f"      {r}", flush=True)
        rec(f"T2 {field}: per-index (Name, wire) == walker", [(r['name'], r['wire']) for r in rows][:len(oracle)] == oracle,
            f"op {[(r['name'], r['wire']) for r in rows][:len(oracle)]} vs walker {oracle}")
        rec(f"T2 {field}: one named data terminal (OBSERVED, not assumed)", len(data) == 1, f"{len(data)} named terminals")
        if len(data) == 1:
            obs = data[0]["is_source"]
            rec(f"T2 {field}: direction prediction ({'READ' if predicted[field] else 'WRITE'}) - a miss is a documentation finding",
                True, f"observed IsSource={obs} -> {'READ' if obs else 'WRITE'}; predicted {'READ' if predicted[field] else 'WRITE'}; "
                      f"{'MATCH' if obs == predicted[field] else 'MISMATCH'}")
    rec("T2 all three globals found on diagram 19", set(found) == set(predicted), f"{sorted(found)}")
    with open(os.path.join(HERE, "main_vi_globals_direction.json"), "w", encoding="utf-8") as f:
        json.dump({"vi": MAIN, "diagram": 19, "nodes": {k: {"n": v[0], "uid": v[1], "terms": v[2]} for k, v in found.items()}},
                  f, indent=1)

    # T3 handles
    if found:
        n = list(found.values())[0][0]
        for _ in range(3):
            run_op(MAIN, 19, n)
        time.sleep(2); samples = [(0, handles())]; t0 = time.time()
        for k in range(1, 21):
            run_op(MAIN, 19, n)
            if k % 10 == 0:
                samples.append((k, handles()))
        time.sleep(5); h_idle = handles()
        xs = [k for k, _ in samples]; ys = [h for _, h in samples]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / max(1e-9, sum((x - mx) ** 2 for x in xs))
        rec("T3 handles over 20 runs on main VI", abs(h_idle - ys[0]) <= 100,
            f"samples {samples}; post-idle {h_idle} ({h_idle - ys[0]:+d}); slope {slope:+.2f}/run; {time.time() - t0:.0f} s")

    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:70} {detail[:160]}", flush=True)
    try:
        g.close_panel(S)
    except Exception as e:
        print("close_panel:", str(e)[:80], flush=True)
    try:
        time.sleep(0.3); os.remove(S); print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if all(ok for _n, ok, _d in RESULTS) else 3


if __name__ == "__main__":
    sys.exit(main())
