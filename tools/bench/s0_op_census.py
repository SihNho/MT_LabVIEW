r"""s0_op_census.py - S0 PHASE 1: READ-ONLY census of the four traverse ops. EDITS NOTHING, SAVES NO VI.

WHY (cycle 45, act 2 brief): S0 run 2's stage 3 failed with **no loop created, no new tunnel and an EXACT
branch** (`tools/bench/build_s0_closeref_v3.log:178`, `:190-192`, `:202`, `dw=0`) and still read `ExecState 0`.
Whether the construction (For Loop + a body node + the `References` array wired into it) was ALREADY on disk in
each op is UNMEASURED, and reading it is cheap. This file is that reading.

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "check what already exists"):
  * `tools/bench/s0_hygiene_probe.py` / `_run2.log` - counts nodes and the reference-creating CHAIN per op, and
    profiles handles/private bytes.
    ** CORRECTION, 2026-09-19 21:0x, forced by `archive/peer/2026-09-19-census-notfail.md` section 1 (ANSWERED,
    claude/hypothesis opus max): RUN 1 OF THIS FILE CLAIMED HERE THAT THE PROBE "does NOT report ForLoop /
    Close Reference / tunnel IndexMode per op … nothing here re-measures the probe". THAT CLAIM WAS FALSE.
    `s0_hygiene_probe_run2.log:9`,`:15`,`:41` already report close-ref counts per op, `:36` already prints
    `#113 ForLoop 'For Loop'`, and `:65-68` already gate them WITH THE CORRECT POLARITY
    (`PASS P1 OpReport_v3.vi has NO Close Reference []`, `PASS P2 KernelBuilder_v1.vi HAS a Close Reference
    donor node [('Function','Close Reference',157)]`). Only the per-tunnel IndexMode table and the COLD
    ExecState readings were new, and run 1 produced both (`s0_op_census.log:114-118`, `:55`,`:71`,`:104`). **
  * Run 1 of this census is IN THIS SAME LOG FILE, above the second `BGRUN START` - 15 PASS / 8 FAIL, and its
    JSON is preserved at `tools/bench/s0_op_census.json` (run 2 writes a DIFFERENT file, `…_run2.json`).
  * `tools/bench/s0_body_census.py` / `.log` - the BODY of `OpReportAll_v0` only (one op, one diagram).
  * `tools/bench/s0_terminal_names.py` / `.log` - the exact terminal bytes used below (`References`, `reference`,
    `error in (no error)`), 6/6, read-only.
  * `gscript.report_all` / `tunnels` / `node_terms_uid` / `node_labels` / `exec_state` - all built; NO NEW OP.
  * `fresh()` / `mem()` / `com_preflight()` are cut from `tools/recipes/build_s0_closeref_v3.py:201-249`
    (the same bytes, so the "cold in a fresh instance" condition is the SAME condition run 2 used).

PREDICTION CONTRACT - printed before anything runs; every line is a gate, PASS/FAIL, and NO gate stops the run
(this is a measurement, not a build):
  C0  the route-B original's md5 is the pinned value BEFORE and AFTER, and every existing op VI's md5 is
      unchanged AFTER (rule 1: this census modifies nothing).
  C1  `OpReport_v3.vi`, `OpWireSource_v5.vi`, `OpReportAll_v0.vi` exist and are read; any VI that does not exist
      is reported as MISSING and is not a failure of this census.
  C2  each existing op reads `ExecState` COLD in a fresh instance. **Predicted 1** for all three
      (`docs/cycle27-plan.md:434-439`, measured seven times). A 0 would be a NEW fact.
  C3  per op, three structural facts are printed: ForLoop present Y/N, a `Close Reference` Function node present
      Y/N (identified by its measured terminal triple, `docs/NAMES.md:239-243`), and whether the Traverse's
      `References` wire enters a LoopTunnel - with that tunnel's IndexMode AS READ.
      Predicted from `docs/REFERENCES.md:151-159` and gated as MEASURED == EXPECTED (see `EXPECT` below):
      OpReport_v3 N/N/N, OpWireSource_v5 N/N/N, OpReportAll_v0 **Y** ForLoop / N Close Reference /
      **Y** References-into-loop. A FAIL line therefore means a DEVIATION, which is the finding.
  C3d the two independent `Close Reference` detectors (terminal triple, node label) AGREE on every VI.
  C3e **POSITIVE CONTROL** (added run 2 on the review's section-4 test): `KernelBuilder_v1.vi` is censused too,
      expected ForLoop N / Close Reference **Y** (#157) / References-into-loop N. If C3b prints `0 found: []`
      there, the triple detector is BLIND and the three nulls above are instrument failures, not measurements.
  C4  LabVIEW handle count and private bytes are printed before and after.

  py tools/bgrun.py --material --max-min 30 --log tools/bench/s0_op_census.log -- py -u tools/bench/s0_op_census.py
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CD = g.CLAUDEDEV
LV_EXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
OUT = os.path.join(HERE, "s0_op_census_run2.json")   # run 1's JSON is NEVER overwritten (review section 5.2)

# `KernelBuilder_v1.vi` is the POSITIVE CONTROL for the C3b detector, added on the review's section-4 test: the
# triple-matcher below had never once been run against a node that SHOULD match, so its three nulls certified an
# instrument nobody had shown able to fire (`archive/peer/2026-09-19-census-notfail.md:112`, `:117-118`, `:122`).
TARGETS = ["OpReport_v3.vi", "OpWireSource_v5.vi", "OpReportAll_v1.vi", "OpReportAll_v0.vi",
           "KernelBuilder_v1.vi"]
GATED = ["OpReport_v3.vi", "OpWireSource_v5.vi", "OpReportAll_v1.vi", "OpReportAll_v0.vi",
         "KernelBuilder_v1.vi"]

# EXPECTED structure per op, from `docs/REFERENCES.md:151-159` (measured 2026-09-19 by s0_hygiene_probe).
# (ForLoop, Close Reference, `References` into a LoopTunnel). A gate compares MEASURED == EXPECTED, so a FAIL
# line means a DEVIATION from the prediction - never a predicted absence. RUN 1 of this census (above in this
# same log file) phrased the same three gates as assertions of PRESENCE, so six predicted absences printed FAIL
# and bgrun called the run an inner failure; the measurements were identical and are unchanged.
EXPECT = {"OpReport_v3.vi": (False, False, False),
          "OpWireSource_v5.vi": (False, False, False),
          "OpReportAll_v0.vi": (True, False, True),
          # the control: ForLoop 0 (its loop references are the SubVIs `Create/Exit For Loop.vi`,
          # s0_hygiene_probe_run2.log:49-50, not a structure), Close Reference 1 (#157), no Traverse => no tunnel
          "KernelBuilder_v1.vi": (False, True, False)}

TRAVERSE_LABEL = "Traverse for GObjects.vi"
REFS_TERM = "References"                                    # tools/bench/s0_terminal_names.log
CR_TERMS = {"error out", "error in (no error)", "reference"}  # docs/NAMES.md:239-243, measured 2026-09-19

g._run.__defaults__ = (6.0, 120.0)
GATES = []


def gate(name, ok, detail=""):
    GATES.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)
    return bool(ok)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def lv_pid():
    out = subprocess.run(["powershell", "-NoProfile", "-Command",
                          "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).Id"],
                         capture_output=True, text=True, timeout=30).stdout.strip()
    return out or None


def mem():
    r = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "$p=Get-Process LabVIEW -ErrorAction SilentlyContinue|Select-Object -First 1;"
         "if($p){\"{0} {1}\" -f $p.HandleCount,$p.PrivateMemorySize64}else{'0 0'}"],
        capture_output=True, text=True)
    try:
        a, b = r.stdout.strip().split()
        return int(a), int(b)
    except Exception:
        return 0, 0


def com_preflight(tries=12, gap=4.0):
    """Two spaced round-trips agreeing against an unchanged pid (build_s0_closeref_v3.py:214-233)."""
    probe = os.path.join(CD, "OpWhileCast_v0.vi")
    last = None
    for k in range(tries):
        try:
            p0 = lv_pid()
            n = g.count(probe, "Wire")
            time.sleep(gap)
            n2 = g.count(probe, "Wire")
            p1 = lv_pid()
            if n == n2 and p0 and p0 == p1:
                print(f"   COM preflight OK (pid {p0}, two round-trips agree: {n} wires)", flush=True)
                return True
            last = f"pid {p0}->{p1}, wires {n}->{n2}"
        except Exception as e:
            last = str(e)[:160]
        print(f"   COM preflight attempt {k + 1}/{tries}: {last}", flush=True)
        time.sleep(gap)
    raise RuntimeError(f"COM preflight FAILED after {tries} attempts: {last}")


def fresh():
    print(f"   fresh(): killing LabVIEW pid {lv_pid()}", flush=True)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) "
                    "{ Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    subprocess.run(["powershell", "-NoProfile", "-Command", f"Start-Process '{LV_EXE}'"],
                   capture_output=True, text=True, timeout=60)
    time.sleep(35)
    g.reset()
    com_preflight()
    print(f"   fresh(): new LabVIEW pid {lv_pid()}", flush=True)


def walk(target, diagram):
    """Node uid -> (access index, label, terminal rows) for one diagram. Cut from build_track_v6_core.walk:84-92."""
    try:
        labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    except Exception as e:
        print(f"      node_labels(D[{diagram}]) EXC {str(e)[:120]}", flush=True)
        labels = {}
    out = {}
    for n in range(80):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def census_one(name):
    path = os.path.join(CD, name)
    rec = {"name": name, "path": path, "exists": os.path.exists(path)}
    exp = EXPECT.get(name)
    print(f"\n=== {name} ===", flush=True)
    if not rec["exists"]:
        # MISSING is an accepted outcome (contract C1), so the gate records that it was REPORTED, not that the
        # file is there - `OpReportAll_v1.vi` is expected to be absent: run 2 saved nothing.
        gate(f"C1 {name}: presence on disk REPORTED (MISSING is an accepted outcome)", True, "MISSING")
        return rec
    gate(f"C1 {name}: presence on disk REPORTED", True, "present")
    rec["md5"] = md5(path)
    rec["bytes"] = os.path.getsize(path)
    print(f"   md5 {rec['md5']}  ({rec['bytes']} B)", flush=True)

    # --- ExecState COLD: fresh instance, after the COM preflight (which loads OpWhileCast_v0 as the probe and
    #     OpReport_v3 as the READER op - the condition is named, never implied), before ANY structural read.
    try:
        rec["exec_state_cold"] = g.exec_state(path)
    except Exception as e:
        rec["exec_state_cold"] = f"EXC {str(e)[:140]}"
    print(f"   CONDITION: fresh LabVIEW instance, preflighted, nothing edited, first read of this VI", flush=True)
    if name == "KernelBuilder_v1.vi":
        # The control is a DONOR, not one of the three ops; `docs/cycle27-plan.md:434-439` predicts nothing about
        # it, so its reading is RECORDED, not gated. Gating an unpredicted fact is what run 1 got wrong.
        gate(f"C2 {name}: ExecState COLD RECORDED (no prediction exists for the donor)", True,
             f"ExecState {rec['exec_state_cold']}")
    else:
        gate(f"C2 {name}: ExecState COLD == 1 (predicted, docs/cycle27-plan.md:434-439)",
             rec["exec_state_cold"] == 1, f"ExecState {rec['exec_state_cold']}")

    # --- structure
    try:
        dias = [{"i": d["i"], "uid": d["uid"], "owner": d["owner"]} for d in g.report(path, "Diagram")]
    except Exception as e:
        dias = []
        print(f"   report(Diagram) EXC {str(e)[:160]}", flush=True)
    rec["diagrams"] = dias
    print(f"   diagrams: {[(d['i'], d['uid'], d['owner']) for d in dias]}", flush=True)

    try:
        rec["forloop_count"] = g.count(path, "ForLoop")
    except Exception as e:
        rec["forloop_count"] = f"EXC {str(e)[:120]}"
    rec["forloop_present"] = rec["forloop_count"] == 1 or (isinstance(rec["forloop_count"], int)
                                                           and rec["forloop_count"] > 0)
    gate(f"C3a {name}: For Loop present == {exp[0] if exp else '?'} (docs/REFERENCES.md:151-159)",
         exp is None or bool(rec["forloop_present"]) == exp[0], f"ForLoop count {rec['forloop_count']}")

    # --- Close Reference node: TWO INDEPENDENT detectors, printed side by side.
    # (a) the measured terminal TRIPLE (docs/NAMES.md:239-243); (b) the node LABEL.
    # Run 1's comment here said "not by a label (primitives are unlabeled)" - that is WRONG and the review caught
    # it: `docs/NAMES.md:249-252` records that a primitive's `Node.Label` reads as its type name, and
    # `s0_hygiene_probe_run2.log:10-14`,`:58` print `'Close Reference'`, `'Index Array'`, `'Open VI Reference'`
    # as labels. Both detectors now run, so a disagreement between them is itself visible
    # (`archive/peer/2026-09-19-census-notfail.md:110`).
    try:
        fn_uids = set(o["uid"] for o in g.report_all(path, "Function"))
    except Exception as e:
        fn_uids = set()
        print(f"   report_all(Function) EXC {str(e)[:160]}", flush=True)
    rec["function_uids"] = sorted(fn_uids)
    crs, by_label, per_diagram = [], [], {}
    for d in dias:
        w = walk(path, d["i"])
        per_diagram[d["i"]] = sorted(w)
        for u, (n, lab, rows) in sorted(w.items()):
            names = set(r["name"].strip().lower() for r in rows)
            hit_triple = u in fn_uids and names == CR_TERMS
            hit_label = str(lab or "").strip().lower() == "close reference"
            if hit_triple:
                crs.append({"uid": u, "diagram": d["i"], "node_index": n, "label": lab,
                            "terminals": [(r["i"], r["name"], r["is_source"], r.get("wire")) for r in rows]})
            if hit_label:
                by_label.append({"uid": u, "diagram": d["i"], "node_index": n, "label": lab})
            print(f"      D[{d['i']}] node {n} #{u} {lab!r} terms={[r['name'] for r in rows]}"
                  f"{'   <- CLOSEREF by triple' if hit_triple else ''}"
                  f"{'   <- CLOSEREF by label' if hit_label else ''}", flush=True)
    rec["nodes_per_diagram"] = per_diagram
    rec["close_reference_nodes"] = crs
    rec["close_reference_by_label"] = by_label
    gate(f"C3d {name}: the two detectors AGREE (terminal triple vs node label)",
         sorted(x["uid"] for x in crs) == sorted(x["uid"] for x in by_label),
         f"triple {[x['uid'] for x in crs]} vs label {[x['uid'] for x in by_label]}")
    gate(f"C3b {name}: `Close Reference` node present == {exp[1] if exp else '?'} "
         f"(docs/REFERENCES.md:151-159)", exp is None or bool(crs) == exp[1], f"{len(crs)} found: {crs}")

    # --- is the `References` array wired into the loop?
    w0 = walk(path, 0)
    tv = next((u for u in w0 if w0[u][1] == TRAVERSE_LABEL), None)
    rec["traverse_uid"] = tv
    refs_wire = None
    if tv is not None:
        row = next((r for r in w0[tv][2] if r["name"] == REFS_TERM and r["is_source"]), None)
        refs_wire = (row or {}).get("wire")
    rec["references_wire"] = refs_wire
    print(f"   Traverse #{tv} '{REFS_TERM}' drives wire {refs_wire}", flush=True)

    tuns = []
    try:
        n_t = g.count(path, "LoopTunnel")
    except Exception:
        n_t = 0
    for i in range(int(n_t) if isinstance(n_t, int) else 0):
        try:
            t = g.tunnels(path, i)
        except Exception as e:
            print(f"   tunnels({i}) EXC {str(e)[:140]}", flush=True)
            continue
        tuns.append({"i": i, "uid": t["uid"], "index_mode": t["index_mode"], "out_wire": t["out_wire"],
                     "in_wires": t["in_wires"], "out_name": t["out_name"]})
        print(f"   LoopTunnel[{i}] #{t['uid']} IndexMode AS READ {t['index_mode']} outer w{t['out_wire']} "
              f"inner {t['in_wires']}", flush=True)
    rec["loop_tunnels"] = tuns
    hit = [t for t in tuns if refs_wire and t["out_wire"] == refs_wire]
    rec["references_into_loop"] = bool(hit)
    rec["references_tunnel_index_mode"] = hit[0]["index_mode"] if hit else None
    gate(f"C3c {name}: `References` enters a LoopTunnel == {exp[2] if exp else '?'} "
         f"(docs/REFERENCES.md:151-159)", exp is None or bool(hit) == exp[2],
         f"matching tunnels {hit} (IndexMode {rec['references_tunnel_index_mode']})")
    return rec


def main():
    print(__doc__, flush=True)
    print(f"\n=== S0 PHASE 1 CENSUS  {time.strftime('%Y-%m-%d %H:%M:%S')} ===", flush=True)
    h0, p0 = mem()
    print(f"   LabVIEW handles BEFORE {h0}, private bytes {p0}", flush=True)

    before = {}
    for n in GATED:
        fp = os.path.join(CD, n)
        before[n] = md5(fp) if os.path.exists(fp) else None
    orig_before = md5(ORIGINAL) if os.path.exists(ORIGINAL) else None
    print(f"   original md5 BEFORE {orig_before}", flush=True)
    gate("C0a the route-B original is the pinned md5 BEFORE", orig_before == ORIG_MD5, str(orig_before))
    for n in GATED:
        print(f"   md5 BEFORE {n}: {before[n]}", flush=True)

    fresh()
    out = {"when": time.strftime("%Y-%m-%dT%H:%M:%S"), "condition": "fresh LabVIEW instance, COM-preflighted, "
           "no edit of any kind; each op's ExecState read before its own structural reads", "ops": []}
    for n in TARGETS:
        try:
            out["ops"].append(census_one(n))
        except Exception as e:
            import traceback
            traceback.print_exc()
            out["ops"].append({"name": n, "error": str(e)[:300]})

    print("\n=== md5 AFTER (rule 1: this census modified nothing) ===", flush=True)
    for n in GATED:
        fp = os.path.join(CD, n)
        after = md5(fp) if os.path.exists(fp) else None
        print(f"   md5 AFTER  {n}: {after}", flush=True)
        gate(f"C0b {n}: UNCHANGED by this census", after == before[n], f"{before[n]} -> {after}")
    orig_after = md5(ORIGINAL) if os.path.exists(ORIGINAL) else None
    gate("C0c the route-B original is UNCHANGED", orig_after == orig_before, f"{orig_before} -> {orig_after}")
    out["md5_before"] = before
    out["md5_after"] = {n: (md5(os.path.join(CD, n)) if os.path.exists(os.path.join(CD, n)) else None)
                        for n in GATED}
    out["original_md5"] = {"before": orig_before, "after": orig_after}

    h1, p1 = mem()
    print(f"\n   LabVIEW handles AFTER {h1} (delta {h1 - h0}), private bytes {p1} "
          f"(delta {(p1 - p0) / 1e6:.1f} MB)", flush=True)
    print(f"   gscript VI Server reference counters: {g.ref_counts()}", flush=True)
    out["ref_counts"] = g.ref_counts()
    out["handles"] = {"before": h0, "after": h1}
    out["private_bytes"] = {"before": p0, "after": p1}
    out["gates"] = [{"name": n, "pass": ok} for n, ok in GATES]

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
    print(f"\n   CENSUS WRITTEN {OUT}", flush=True)
    print(f"   census md5 {md5(OUT)}  ({os.path.getsize(OUT)} B)", flush=True)

    npass = sum(1 for _n, ok in GATES if ok)
    print(f"\n=== {npass} PASS / {len(GATES) - npass} FAIL ===", flush=True)
    for n, ok in GATES:
        if not ok:
            print(f"   FAIL {n}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    finally:
        try:
            g.reset()          # release every cached VI Server reference this client holds (CLAUDE.md hygiene)
        except Exception:
            pass
