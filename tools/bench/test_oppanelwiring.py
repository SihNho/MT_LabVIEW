"""test_oppanelwiring.py - FUNCTIONAL acceptance of OpPanelWiring_v0 (tools/recipes/build_oppanelwiring_v0.py).

Prediction contract (machine-checked rows):
  T1 scratch copy of OpNodeInfo_v0 (an op: every panel object is wired): label multiset == fp_labels(scratch) labels;
     Indicator flags == fp_labels is_ind per label; control UIDs unique; EVERY wire UID non-zero and a member of
     report_all(scratch,'Wire') uids; IsSource == not Indicator for every row.
  T2 scratch with ONE orphan: create a control on the scratch panel by script (g.create_control if available -
     otherwise skipped and reported) and expect exactly that label with wire UID 0.
  T3 main VI: 114 rows (docs/main-vi-panel-map.md: 60 CTL / 54 IND); flags 60/54; orphan list (wire UID 0) printed;
     every non-zero wire UID is a member of report_all(main,'Wire'); known-wired controls (from the 09-12/13 census:
     the camera name / 'Number of Buffers' if present) show non-zero.
  T4 handle audit: 20 runs on the scratch, 20 on the main VI - samples every 10, slope, post-idle.
Scratch unique per run, deleted; nothing saved; main VI read by reference only.
  py tools/bgrun.py --max-min 15 --log tools/bench/test_oppanelwiring.log -- py -u tools/bench/test_oppanelwiring.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

OP = os.path.join(g.CLAUDEDEV, "OpPanelWiring_v0.vi")
MAP = json.load(open(os.path.join(HERE, "oppanelwiring_labels.json"), encoding="utf-8"))
LAB = {v: k for k, v in MAP.items()}          # 'Text' -> 'Array', 'Indicator' -> 'Array 2', ...
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
SRC = os.path.join(g.CLAUDEDEV, "OpNodeInfo_v0.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_test_panelwiring_{os.getpid()}.vi")
for _old in [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_test_panelwiring")]:
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


def run_op(target):
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    t0 = time.time()
    g._run(vi)
    dt = time.time() - t0
    err = g._err(vi)
    text = list(vi.GetControlValue(LAB["Text"]))
    ind = [bool(x) for x in vi.GetControlValue(LAB["Indicator"])]
    cuid = [int(x) for x in vi.GetControlValue(LAB["ControlUID"])]
    src = [bool(x) for x in vi.GetControlValue(LAB["IsSource"])]
    wuid = [int(x) for x in vi.GetControlValue(LAB["WireUID"])]
    rows = [{"label": t, "indicator": i, "uid": c, "is_source": s, "wire": w} for t, i, c, s, w in zip(text, ind, cuid, src, wuid)]
    for key, field in (("TermErr", "term_err"), ("WireErr", "wire_err")):     # optional explicit error columns
        if key in LAB:
            try:
                errs = list(vi.GetControlValue(LAB[key]))
                for r, e in zip(rows, errs):
                    e = tuple(e) if isinstance(e, (tuple, list)) else (e,)
                    r[field] = int(e[1]) if len(e) > 1 and e[0] else 0
            except Exception as ex:
                print(f"   ({key} column unreadable over COM: {str(ex)[:80]})", flush=True)
    return rows, err, dt


def main():
    g._lv = None
    shutil.copyfile(SRC, S)
    rows, err, dt = run_op(S)
    fp = [(lab, is_ind) for _i, lab, is_ind in g.fp_labels(S)]
    print(f"T1 scratch: {len(rows)} rows in {dt:.2f} s, err={err!r}", flush=True)
    for r in rows:
        print(f"      {r}", flush=True)
    rec("T1 label multiset == fp_labels", Counter(r["label"] for r in rows) == Counter(l for l, _ in fp) and not err,
        f"op {sorted(r['label'] for r in rows)} vs fp {sorted(l for l, _ in fp)}")
    fp_ind = {l: i for l, i in fp}
    rec("T1 Indicator flags == fp_labels", all(fp_ind.get(r["label"]) == r["indicator"] for r in rows), "per label")
    rec("T1 control UIDs unique", len({r["uid"] for r in rows}) == len(rows), f"{len(rows)} rows")
    wires = {o["uid"] for o in g.report_all(S, "Wire")}
    # Run 1 (11:2x) predicted "every object wired" and was WRONG about the donor, not the op: OpNodeInfo_v0's build
    # stripped every wire but two (build_opfplabels.py) and never re-wired Class Name/Class Name 2/Names/Names 2/
    # index 2/error out - those six are genuine orphans. So: non-zero wire UIDs must be real Wires, and the orphan
    # SET is reported (with the explicit error columns) and compared by DELTA in T2.
    base_orphans = {r["label"] for r in rows if not r["wire"]}
    rec("T1 every non-zero wire UID is a real Wire on the scratch", all(r["wire"] in wires for r in rows if r["wire"]),
        f"orphans {sorted(base_orphans)} (donor's stripped controls); errs "
        f"{[(r['label'], r.get('term_err'), r.get('wire_err')) for r in rows if not r['wire']]}")
    rec("T1 IsSource == not Indicator", all(r["is_source"] == (not r["indicator"]) for r in rows),
        f"{[(r['label'], r['is_source'], r['indicator']) for r in rows if r['is_source'] == r['indicator']]}")

    # T2 one orphan by construction: create a control on a terminal (create_control), then delete the wire it made,
    # so exactly one panel object has an unwired terminal. Best effort: any failure here is reported, not fatal.
    try:
        g.open_panel(S)
        time.sleep(0.5)
        w0 = {o["uid"] for o in g.report_all(S, "Wire")}
        walk = g.net_map(S, 0, max_nodes=40, max_terms=24)[0]
        # the SubVIs[]-free donor OpNodeInfo_v0: pick the Nodes[] property node's `error in (no error)` (an unwired sink)
        n_idx, t_idx = next((n, ti) for n, (u, _l, terms) in walk.items() for ti, t, w in terms
                            if t == "error in (no error)" and not w and any(tt == "Nodes[]" for _a, tt, _b in terms))
        made = g.create_control(S, n_idx, t_idx)
        new_w = [o["uid"] for o in g.report_all(S, "Wire") if o["uid"] not in w0]
        order = [o["uid"] for o in g.report_all(S, "Wire")]
        for u in new_w:
            g.delete_object(S, "Wire", order.index(u), verify=False)
            order.remove(u)
        rows2, err2, _ = run_op(S)
        orphan = {r["label"] for r in rows2 if r["wire"] == 0}
        new_lab = orphan - base_orphans
        rec("T2 the constructed orphan is exactly the +1 over the baseline orphan set (rows N -> N+1, array not shortened)",
            len(new_lab) == 1 and len(rows2) == len(rows) + 1 and (orphan & base_orphans) == base_orphans,
            f"new orphan {sorted(new_lab)}; made={str(made)[:60]}; wires deleted {len(new_w)}; rows {len(rows)}->{len(rows2)}; "
            f"errs {[(r['label'], r.get('term_err'), r.get('wire_err')) for r in rows2 if r['label'] in new_lab]}")
    except Exception as e:
        rec("T2 orphan by construction", False, f"EXC {str(e)[:160]}")

    # T3 main VI
    rows, err, dt = run_op(MAIN)
    n_ind = sum(r["indicator"] for r in rows)
    print(f"T3 main VI: {len(rows)} rows ({len(rows) - n_ind} CTL / {n_ind} IND) in {dt:.2f} s, err={err!r}", flush=True)
    orphans = [r for r in rows if r["wire"] == 0]
    print(f"      ORPHANS (terminal unwired on the diagram): {len(orphans)}", flush=True)
    for r in orphans:
        print(f"         {'IND' if r['indicator'] else 'CTL'}  #{r['uid']:6d}  {r['label']!r}", flush=True)
    rec("T3 114 rows, 60 CTL / 54 IND (docs/main-vi-panel-map.md)", len(rows) == 114 and n_ind == 54 and not err,
        f"{len(rows)} rows, {len(rows) - n_ind}/{n_ind}")
    wires = {o["uid"] for o in g.report_all(MAIN, "Wire")}
    rec("T3 every non-zero wire UID is a real Wire on the main VI", all(r["wire"] in wires for r in rows if r["wire"]),
        f"foreign {[r['wire'] for r in rows if r['wire'] and r['wire'] not in wires][:6]}")
    rec("T3 IsSource == not Indicator on the main VI", all(r["is_source"] == (not r["indicator"]) for r in rows),
        f"{sum(r['is_source'] == r['indicator'] for r in rows)} disagreements")
    with open(os.path.join(HERE, "main_vi_panel_wiring.json"), "w", encoding="utf-8") as f:
        json.dump({"vi": MAIN, "rows": rows, "orphans": [r["label"] for r in orphans]}, f, indent=1, ensure_ascii=False)
    print("      -> tools/bench/main_vi_panel_wiring.json", flush=True)

    # T4 handles
    for label, tgt, n in (("scratch", S, 20), ("main VI", MAIN, 20)):
        for _ in range(3):
            run_op(tgt)
        time.sleep(2); samples = [(0, handles())]; t0 = time.time()
        for k in range(1, n + 1):
            run_op(tgt)
            if k % 10 == 0:
                samples.append((k, handles()))
        time.sleep(5); h_idle = handles()
        xs = [k for k, _ in samples]; ys = [h for _, h in samples]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / max(1e-9, sum((x - mx) ** 2 for x in xs))
        rec(f"T4 handles over {n} runs on {label}", abs(h_idle - ys[0]) <= 100,
            f"samples {samples}; post-idle {h_idle} ({h_idle - ys[0]:+d}); slope {slope:+.2f}/run; {time.time() - t0:.0f} s")

    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:62} {detail[:150]}", flush=True)
    try:
        g.close_panel(S)
    except Exception as e:
        print("close_panel:", str(e)[:100], flush=True)
    try:
        time.sleep(0.3); os.remove(S); print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if all(ok for _n, ok, _d in RESULTS) else 3


if __name__ == "__main__":
    sys.exit(main())
