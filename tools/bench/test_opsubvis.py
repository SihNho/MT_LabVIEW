"""test_opsubvis.py - FUNCTIONAL acceptance of OpSubVIs_v0 (built by tools/recipes/build_opsubvis_v0.py).

Structural (ExecState 1) says nothing about the numbers. Prediction contract, all machine-checked:
  T1 scratch copy of OpFPLabels_v0, diagram 0: UID set == report_all(scratch,'SubVI') uids; every VI Name and
     VI Path non-empty; len(names) == len(paths) == len(uids).
  T2 main VI diagram 43 (frame loop): UID set == (diagram_tree_main.json diagrams['43'].uids  n  subvis keys);
     the tracking kernel call uid 5058 present; its name printed.
  T3 a main-VI diagram with NO subVI (first such in the cache): empty arrays, no error, no dialog.
  T4 handle audit: 20 runs on the scratch and 20 on the main VI - LabVIEW HandleCount flat within +-100 each
     (CLAUDE.md reference hygiene; SubVIs[] hands out N refs per run and nothing closes them explicitly).
  T5 timing: per-run seconds on the main VI (one Open VI Reference ~1 s expected, as for OpReportAll).
Scratch deleted; nothing saved; the main VI is opened by reference only (read-only), never edited.
  py tools/bgrun.py --max-min 15 --log tools/bench/test_opsubvis.log -- py -u tools/bench/test_opsubvis.py
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

# v0 (donor OpNodeInfo_v0) FAILED T2/T2b/T3b/T6 on 2026-09-14 10:4x: its `index` never selected a diagram (see the
# recipe header). v1 = donor OpNetInfo_v1, driven through gscript.subvis(), which also purges the donor's junk Invoke.
TREE = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
MAIN = TREE["vi"]
SRC = os.path.join(g.CLAUDEDEV, "OpFPLabels_v0.vi")
# Unique per run: 10:51 a rerun copied over a scratch whose previous instance was still loaded (close_panel had
# failed with 0x47D) and Traverse answered 1012 "Cannot load block diagram" (docs/NAMES.md: never load a VI you are
# about to overwrite). Leftovers from earlier runs are removed below on a best-effort basis.
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_test_opsubvis_{os.getpid()}.vi")
for _old in [p for p in os.listdir(g.CLAUDEDEV) if p.startswith("SCRATCH_test_opsubvis")]:
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


def run_op(target, diagram_index, **controls):
    """(names, paths, uids, err, seconds) through gscript.subvis - purge included, so dt is the real per-call cost."""
    t0 = time.time()
    rows, err = g.subvis(target, diagram_index, purge=True, strict=False, **controls)
    dt = time.time() - t0
    return [r["name"] for r in rows], [r["path"] for r in rows], [r["uid"] for r in rows], err, dt


def main():
    g._lv = None
    # T1 scratch
    try:
        g.close_panel(S); time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(S):
        os.remove(S)
    shutil.copyfile(SRC, S)
    expect = {o["uid"] for o in g.report_all(S, "SubVI")}
    # T0 does the op still drop a junk Invoke on its target? (peer s2: measure, do not assume) - one call WITHOUT
    # purge, count Invokes, then purge by hand so T1 starts clean.
    inv0 = g.uids(S, "Invoke")
    g.subvis(S, 0, purge=False, strict=False)
    junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
    rec("T0 junk Invokes dropped on the target per call (0 = creator-free op)", True, f"{len(junk)} per call")
    if junk:
        order = [o["uid"] for o in g.report_all(S, "Invoke")]
        for idx in sorted((order.index(u) for u in junk), reverse=True):
            g.delete_object(S, "Invoke", idx, verify=False)
        g.remove_bad_wires_scripted(S)
    inv_before, es_before = len(g.report_all(S, "Invoke")), g.exec_state(S)
    names, paths, uids, err, dt = run_op(S, 0)
    rec("T1 purge: scratch Invoke count and ExecState unchanged after a call",
        len(g.report_all(S, "Invoke")) == inv_before and g.exec_state(S) == es_before,
        f"Invoke {inv_before} -> {len(g.report_all(S, 'Invoke'))}, ExecState {es_before} -> {g.exec_state(S)}")
    print(f"T1 scratch: {len(names)} names {names}, paths {[os.path.basename(p) for p in paths]}, uids {uids}, err={err!r}, {dt:.2f} s",
          flush=True)
    rec("T1 UID set == report_all SubVI uids", set(uids) == expect and not err, f"op {sorted(uids)} vs traverse {sorted(expect)}")
    rec("T1 names/paths non-empty and aligned", len(names) == len(paths) == len(uids) and all(names) and all(paths),
        f"{len(names)}/{len(paths)}/{len(uids)}")

    # T2 main VI diagram 43
    subvis = {int(k) for k in TREE["subvis"].keys()}
    exp43 = set(TREE["diagrams"]["43"]["uids"]) & subvis
    names, paths, uids, err, dt = run_op(MAIN, 43)
    print(f"T2 main diagram 43: {len(uids)} subVI calls in {dt:.2f} s, err={err!r}", flush=True)
    for n, u in zip(names, uids):
        print(f"      uid {u:6d}  {n}", flush=True)
    rec("T2 UID set == cache (diagram 43 uids n subvis)", set(uids) == exp43 and not err,
        f"op {len(uids)} vs cache {len(exp43)}; missing {sorted(exp43 - set(uids))[:6]} extra {sorted(set(uids) - exp43)[:6]}")
    rec("T2 tracking kernel call uid 5058 present", 5058 in uids,
        f"name = {names[uids.index(5058)] if 5058 in uids else '-'}")
    t_main, uids43 = dt, list(uids)

    # T3 empty diagram
    empty = next((k for k, d in TREE["diagrams"].items() if not (set(d["uids"]) & subvis)), None)
    names, paths, uids, err, dt = run_op(MAIN, int(empty))
    rec(f"T3 diagram {empty} (no subVI in cache): empty arrays, no error", not names and not uids and not err,
        f"names {len(names)} uids {len(uids)} err={err!r} {dt:.2f} s")
    # T3b the discriminator for T3 (peer point d): an INVALID diagram index must show a real error on the SubVIs[]
    # node's error out, so "empty because nothing there" and "empty because it errored" are told apart.
    try:
        names, paths, uids, err, dt = run_op(MAIN, 9999)
        rec("T3b diagram 9999 (invalid): SubVIs[] error out non-empty, arrays empty", bool(err) and not uids,
            f"err={err!r} uids {len(uids)} {dt:.2f} s")
    except Exception as e:
        rec("T3b diagram 9999 (invalid)", False, f"EXC {str(e)[:160]}")

    rec("T2 UIDs unique (duplicate call sites keep distinct UIDs)", len(set(uids43)) == len(uids43), f"{len(uids43)} rows")

    # T2b a diagram with exactly ONE subVI call (the 1-element loop case)
    one = next((k for k, d in TREE["diagrams"].items() if len(set(d["uids"]) & subvis) == 1), None)
    if one is not None:
        names, paths, uids, err, dt = run_op(MAIN, int(one))
        rec(f"T2b diagram {one} (exactly one subVI in cache)", set(uids) == (set(TREE["diagrams"][one]["uids"]) & subvis)
            and len(names) == 1 and not err, f"{names} uids {uids} err={err!r}")

    # T4 handle audit - peer (archive/peer/2026-09-14-opsubvis-v0-plan.md c): 20 runs / +-100 can hide a small
    # per-run leak; sample every 10 runs, report the fitted slope per run, and the post-idle recovery.
    for label, tgt, di, n in (("scratch", S, 0, 30), ("main VI diagram 43", MAIN, 43, 30)):
        for _ in range(5):
            run_op(tgt, di)                                   # warm-up
        time.sleep(2); samples = [(0, handles())]; t0 = time.time()
        for k in range(1, n + 1):
            run_op(tgt, di)
            if k % 10 == 0:
                samples.append((k, handles()))
        time.sleep(5); h_idle = handles()
        xs = [k for k, _ in samples]; ys = [h for _, h in samples]
        mx, my = sum(xs) / len(xs), sum(ys) / len(ys)
        slope = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / max(1e-9, sum((x - mx) ** 2 for x in xs))
        rec(f"T4 handles over {n} runs on {label}", abs(h_idle - ys[0]) <= 100,
            f"samples {samples}; post-idle {h_idle} ({h_idle - ys[0]:+d}); slope {slope:+.2f} handles/run; {time.time() - t0:.0f} s")
    rec("T5 main-VI run time", True, f"{t_main:.2f} s per run (single, diagram 43)")

    # T6 the vestigial per-node chain (index 2 / index 3 readers) must be harmless: a huge legacy node index on a
    # valid diagram -> no dialog, run returns, the three arrays still correct (peer point e).
    try:
        names, paths, uids, err, dt = run_op(MAIN, 43, **{"index 2": 999})
        rec("T6 vestigial chain with index 2 = 999: arrays still correct, no dialog", set(uids) == exp43,
            f"{len(uids)} uids, err(SubVIs[] error out)={err!r}, {dt:.2f} s")
    except Exception as e:
        rec("T6 vestigial chain with index 2 = 999", False, f"EXC {str(e)[:160]}")

    print("\n################ SUMMARY ################", flush=True)
    for name, ok, detail in RESULTS:
        print(f"  {'PASS' if ok else 'FAIL'}  {name:58} {detail}", flush=True)
    try:
        g.close_panel(S); time.sleep(0.3); os.remove(S)
        print("scratch deleted", flush=True)
    except Exception as e:
        print("cleanup:", str(e)[:80], flush=True)
    return 0 if all(ok for _n, ok, _d in RESULTS) else 3


if __name__ == "__main__":
    sys.exit(main())
