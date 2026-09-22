r"""diag_wiki_probe - measure the routes `tools/wiki_build.py` (plan step 3) needs, before the 94-VI run.

PREDICTION CONTRACT
  P1 `gscript.report_all(vi, 'GObject')` returns > 0 rows on a background-VI copy. If it errors, the class
     census falls back to per-class calls. FACT either way (this is a capability probe, not a claim).
  P2 `allterms.read_terms(vi)` returns > 0 rows on each sample and each read finishes in < 25 s. GATE.
  P3 the 2026-09-23 join ruling on the D1 bed: `all_wire_uids` = 1920; `join_wires(bed_rows, uids)` =
     1913 termed + 7 termless; `severed()` == [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540]
     EXACTLY. GATE (three rows).
  P4 CONNECTOR-PANE ROUTE: a subVI CALL node dropped on a scratch copy of `EMPTY_v0.vi` exposes its
     connector-pane terminals to the same Terminal traverse (term_name + is_source). GATE: every dropped
     node shows >= 1 terminal, and `gscript.subvis` names it.
  P5 rows whose `owner_class` == 'Diagram' are the VI's own front-panel control/indicator terminals - the
     FALLBACK conpane source. FACT: count per sample.
  P6 `report_all(vi,'Diagram')` count and `gscript.subvis(vi, idx)` seconds per diagram. FACT (budget input).

PRIOR ART READ FIRST (CLAUDE.md "check what exists"): `tools/allterms.py` (read_terms/join_wires/
all_wire_uids - the last one added today), `gscript.report_all` / `subvis` / `drop_subvi` / `open_panel` /
`ensure_loaded` / `count`, `tools/bench/allterms_bed_20260923*.json`, `claudeDev\EMPTY_v0.vi`,
`tools/bench/bench_prep.labview_handles`. Nothing new is built here.

NOTHING IS MUTATED except one dated scratch COPY of EMPTY_v0 under claudeDev, deleted at the end. No VI is
run. The 94 `background VIs_COPY` files are md5-pinned before and after.
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
for _p in (TOOLS, HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import allterms as A                                                               # noqa: E402
import bench_prep                                                                  # noqa: E402

BG = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")
BED_JSON = os.path.join(HERE, "allterms_bed_20260923.json")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
EXPECT_SEVERED = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
OUT = os.path.join(HERE, "diag_wiki_probe.json")
P, F, REC = [0], [0], {}


def gate(label, ok, detail=""):
    (P if ok else F)[0] += 1
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, detail), flush=True)


def fact(line):
    print("  FACT  {0}".format(line), flush=True)


def head(t):
    print("\n---------- [{0}]".format(t), flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pins():
    out = {}
    for dp, _d, fs in os.walk(BG):
        for f in fs:
            if f.lower().endswith(".vi"):
                out[os.path.relpath(os.path.join(dp, f), BG)] = md5(os.path.join(dp, f))
    return out


def main():
    t_all = time.time()
    before = pins()
    fact("copies pinned: {0}; ORIGINAL md5 {1} (want {2})".format(
        len(before), md5(g.ORIGINAL), g.ORIG_MD5))
    gate("K1 ORIGINAL md5 unchanged", md5(g.ORIGINAL) == g.ORIG_MD5)
    h0 = bench_prep.labview_handles()
    fact("LabVIEW handles at start: {0}".format(h0))

    files = sorted(before)
    by_size = sorted(files, key=lambda k: os.path.getsize(os.path.join(BG, k)))
    samples = [by_size[0], by_size[len(by_size) // 2], by_size[-2]]
    fact("samples: {0}".format([(s, os.path.getsize(os.path.join(BG, s))) for s in samples]))

    head("P3 the join ruling on the D1 bed")
    bed_rows = json.load(open(BED_JSON, encoding="utf-8"))["terminals"]
    uids, dt_w = A.all_wire_uids(BED)
    wires = A.join_wires(bed_rows, uids)
    sev = sorted(w["wire_uid"] for w in A.severed(wires))
    termed = [w for w in wires if not w["termless"]]
    fact("report_all('Wire') {0} uids in {1:.2f} s".format(len(uids), dt_w))
    gate("P3a all_wire_uids == 1920", len(uids) == 1920, str(len(uids)))
    gate("P3b 1913 termed + 7 termless", len(termed) == 1913 and len(wires) - len(termed) == 7,
         "{0} termed / {1} termless".format(len(termed), len(wires) - len(termed)))
    gate("P3c severed == the 11 known uids", sev == EXPECT_SEVERED, str(sev))
    REC["bed"] = {"wire_objects": len(uids), "termed": len(termed), "termless": len(wires) - len(termed),
                  "severed": sev, "wire_traverse_s": round(dt_w, 2)}

    head("P1/P2/P5/P6 per-sample reads")
    REC["samples"] = {}
    for s in samples:
        p = os.path.join(BG, s)
        rec = {"bytes": os.path.getsize(p)}
        t0 = time.time()
        try:
            go = g.report_all(p, "GObject")
            rec["gobject_rows"], rec["gobject_s"] = len(go), round(time.time() - t0, 2)
            cls = {}
            for r in go:
                cls[r["class"]] = cls.get(r["class"], 0) + 1
            rec["classes"] = dict(sorted(cls.items(), key=lambda kv: -kv[1])[:12])
        except Exception as e:                                                     # noqa: BLE001
            rec["gobject_rows"], rec["gobject_err"] = None, str(e)[:160]
        t0 = time.time()
        try:
            rows, dt = A.read_terms(p)
            rec["term_rows"], rec["term_s"] = len(rows), round(dt, 2)
            rec["fp_terminals"] = sum(1 for r in rows if r["owner_class"] == "Diagram")
            rec["fp_sample"] = [(r["term_name"], r["is_source"]) for r in rows
                                if r["owner_class"] == "Diagram"][:6]
        except Exception as e:                                                     # noqa: BLE001
            rec["term_rows"], rec["term_err"] = None, str(e)[:160]
        t0 = time.time()
        try:
            rec["diagrams"] = g.count(p, "Diagram")
            sv = g.subvis(p, 0)
            rec["subvis_d0"], rec["subvis_s"] = [x["name"] for x in sv][:8], round(time.time() - t0, 2)
        except Exception as e:                                                     # noqa: BLE001
            rec["subvis_err"] = str(e)[:160]
        REC["samples"][s] = rec
        fact("{0}: {1}".format(s, json.dumps(rec)[:420]))
        gate("P2 read_terms rows > 0 and < 25 s [{0}]".format(s[:28]),
             bool(rec.get("term_rows")) and rec.get("term_s", 99) < 25,
             "{0} rows / {1} s".format(rec.get("term_rows"), rec.get("term_s")))
    gate("P1 report_all('GObject') works on every sample",
         all(REC["samples"][s].get("gobject_rows") for s in samples),
         str({s[:20]: REC["samples"][s].get("gobject_rows") or REC["samples"][s].get("gobject_err")
              for s in samples})[:300])

    head("P4 connector-pane route: subVI call nodes on a scratch EMPTY_v0 copy")
    scratch = os.path.join(g.CLAUDEDEV, "wikiprobe_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
    import shutil
    shutil.copy2(EMPTY, scratch)
    try:
        g.open_panel(scratch)
        placed = {}
        for i, s in enumerate(samples):
            t0 = time.time()
            g.drop_subvi(scratch, os.path.join(BG, s), 0, (200 + 340 * i, 200))
            placed[s] = round(time.time() - t0, 2)
        fact("drop_subvi seconds {0}".format(placed))
        sv = g.subvis(scratch, 0)
        fact("subvis on scratch: {0}".format([(x["uid"], x["name"]) for x in sv]))
        rows, dt = A.read_terms(scratch)
        by_owner = {}
        for r in rows:
            by_owner.setdefault(r["owner_uid"], []).append(r)
        REC["conpane"] = {}
        for x in sv:
            terms = [{"label": r["term_name"], "direction": "output" if r["is_source"] else "input"}
                     for r in by_owner.get(x["uid"], [])]
            REC["conpane"][x["name"]] = terms
            fact("{0}: {1} conpane terminals {2}".format(x["name"], len(terms), json.dumps(terms)[:260]))
        gate("P4 every dropped subVI node shows >= 1 terminal",
             bool(sv) and all(REC["conpane"][x["name"]] for x in sv),
             "{0} nodes".format(len(sv)))
        REC["conpane_read_s"] = round(dt, 2)
    finally:
        g.close_panel_safe = None
        try:
            g.close_panel(scratch)
        except Exception:                                                          # noqa: BLE001
            pass
        try:
            os.remove(scratch)
        except Exception as e:                                                     # noqa: BLE001
            fact("scratch not removed: {0}".format(str(e)[:120]))
    gate("H4 scratch deleted", not os.path.exists(scratch), scratch)

    head("H HYGIENE")
    after = pins()
    changed = [k for k in after if before.get(k) != after[k]]
    gate("H1 all 94 copies byte-unchanged", not changed and len(after) == len(before), str(changed[:5]))
    gate("H2 ORIGINAL md5 unchanged", md5(g.ORIGINAL) == g.ORIG_MD5)
    fact("gscript ref_counts {0}".format(g.ref_counts()))
    h1 = bench_prep.labview_handles()
    fact("LabVIEW handles at end: {0} (delta {1})".format(h1, (h1 - h0) if (h1 and h0) else "?"))
    REC["handles"] = [h0, h1]
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(REC, f, indent=1)
    print("\n" + "=" * 90, flush=True)
    print("=== GATES: {0} pass / {1} fail   elapsed {2:.1f}s   JSON {3}".format(
        P[0], F[0], time.time() - t_all, OUT), flush=True)
    return 1 if F[0] else 0


if __name__ == "__main__":
    sys.exit(main())
