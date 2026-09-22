r"""allterms - the whole-VI TERMINAL table and the WIRE table joined from it.

`docs/connectivity-map-plan.md` step 1. Two halves, deliberately separable:

  read_terms(vi)   ONE call to `OpAllTerms_v0.vi` (claudeDev) -> one row per terminal on the whole
                   block diagram: term_uid, term_name, is_source, wire_uid (0 = unwired), owner_uid,
                   owner_class. `Traverse for GObjects` class `Terminal` returns 5,811 rows on the
                   D1 bed in 5.28 s in ONE round trip (`tools/bench/diag_allwires_probe.log`),
                   against ~508 s for `node_terms` per node - the reason this op exists.

  join_wires(rows) PURE PYTHON, no LabVIEW: groups the rows by wire_uid and emits one row per wire -
                   wire_uid, src_uid/src_class/src_term, sink_uid/sink_class/sink_term, n_src, n_sink.
                   A wire with n_src == 0 or n_sink == 0 is a SEVERED half-wire; the D1 bed has 11
                   (uids [1731,1893,2819,3947,4833,7337,7388,9635,11232,23502,23540]).

Record keys are **node UID + terminal name** (Pre-decided 137); wire UIDs are transient and are the
join key only WITHIN one read. Nothing here mutates the target: it is a reader, it lives in `tools/`
and not `tools/recipes/`, so `guard_cycle.BUILD_RE` does not gate it.

  py tools/allterms.py <vi-path> [--out tools/bench/allterms_<bed>_<date>.json]
"""
import argparse
import collections
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gscript as g                                                                # noqa: E402

OP_ALLTERMS = os.path.join(g.CLAUDEDEV, "OpAllTerms_v0.vi")
LABELS = os.path.join(HERE, "bench", "opallterms_labels.json")
FIELDS = ("term_uid", "term_name", "is_source", "wire_uid", "owner_uid", "owner_class")
_LABELS = None


def _labels():
    """{field: front-panel indicator label} - WRITTEN BY THE BUILD RECIPE from what LabVIEW named the
    indicators, never guessed here (the OpReportAll_v0 precedent, gscript.py:_REPORT_ALL_FIELDS)."""
    global _LABELS
    if _LABELS is None:
        with open(LABELS, encoding="utf-8") as f:
            _LABELS = json.load(f)
    return _LABELS


def read_terms(target, op=OP_ALLTERMS):
    """Every terminal of `target`'s block diagram in ONE op run. Returns (rows, seconds)."""
    lab = _labels()
    vi = g.op(op)
    vi.SetControlValue(lab["vi_path"], target)
    # The op inherits `OpReportAll_v0`'s CALL-TIME Traverse class control, so the class is set here
    # rather than frozen into the VI - one op, any class, and `Terminal` is what this reader is for.
    vi.SetControlValue(lab["class_name"], "Terminal")
    t0 = time.time()
    g._run(vi)
    dt = time.time() - t0
    err = g._err(vi)
    if err:
        raise RuntimeError("read_terms({0}): {1}".format(os.path.basename(target), err))
    cols = dict((f, list(vi.GetControlValue(lab[f]))) for f in FIELDS)
    n = min(len(v) for v in cols.values())
    rows = [dict((f, cols[f][i]) for f in FIELDS) for i in range(n)]
    for r in rows:
        r["term_uid"] = int(r["term_uid"])
        r["wire_uid"] = int(r["wire_uid"])
        r["owner_uid"] = int(r["owner_uid"])
        r["is_source"] = bool(r["is_source"])
    return rows, dt


def join_wires(rows):
    """One row per wire, joined from the terminal table by wire_uid. Pure; no LabVIEW."""
    by_wire = collections.defaultdict(list)
    for r in rows:
        if r["wire_uid"]:
            by_wire[r["wire_uid"]].append(r)
    out = []
    for wire_uid in sorted(by_wire):
        terms = by_wire[wire_uid]
        src = [t for t in terms if t["is_source"]]
        snk = [t for t in terms if not t["is_source"]]
        first = (src or [None])[0]
        last = (snk or [None])[0]
        out.append({
            "wire_uid": wire_uid,
            "src_uid": first["owner_uid"] if first else 0,
            "src_class": first["owner_class"] if first else "",
            "src_term": first["term_name"] if first else "",
            "sink_uid": last["owner_uid"] if last else 0,
            "sink_class": last["owner_class"] if last else "",
            "sink_term": last["term_name"] if last else "",
            "n_src": len(src),
            "n_sink": len(snk),
        })
    return out


def severed(wires):
    """Wires missing a side - the shape the D1 bed's 11 broken wires are expected to show."""
    return [w for w in wires if w["n_src"] == 0 or w["n_sink"] == 0]


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("vi")
    ap.add_argument("--out", default=None, help="terminal-table JSON (the wire table goes beside it)")
    ap.add_argument("--op", default=OP_ALLTERMS)
    a = ap.parse_args(argv)

    rows, dt = read_terms(a.vi, a.op)
    wires = join_wires(rows)
    bad = severed(wires)
    stem = a.out or os.path.join(HERE, "bench", "allterms_{0}_{1}.json".format(
        os.path.splitext(os.path.basename(a.vi))[0][:40], time.strftime("%Y%m%d")))
    wire_out = stem[:-5] + "_wires.json" if stem.endswith(".json") else stem + "_wires.json"
    meta = {"vi": a.vi, "op": a.op, "read_seconds": round(dt, 2), "n_terminals": len(rows),
            "n_wires": len(wires), "n_severed": len(bad),
            "severed_uids": [w["wire_uid"] for w in bad], "when": time.strftime("%Y-%m-%d %H:%M:%S")}
    for path, payload in ((stem, {"meta": meta, "terminals": rows}),
                          (wire_out, {"meta": meta, "wires": wires})):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=1)
    print(json.dumps(meta, indent=2), flush=True)
    print("terminals -> {0}\nwires     -> {1}".format(stem, wire_out), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
