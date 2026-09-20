r"""diag_u2g_terminals.py - what ARE the terminals of `UID to GObject Reference.vi` once it is dropped?

WHY. `tools/bench/probe_move_into_v0.log:78-80` - phase 1 of probe_move_into_v0 stopped at
    U2G node[15] terminals: [(0, 'error out', 0), (1, '', 0), (2, 'GObject', 0), (3, 'dup Owning VI', 0)]
    **FAIL** P1 OpMoveIn_v0 builds  could not identify the UID->GObject terminals by name
The probe matched the VI-reference and UID INPUTS by name ("vi"+"ref", "uid"), and net_map showed neither: only
four terminals, three of them outputs and one with an EMPTY name. That is a fact about the reader or about the
node, and the probe's next line must be written from a measurement, not from a guess about which name to try
(CLAUDE.md: "the second time a class of failure is explained by inference rather than read from the machine, the
next build is the READER for it" - here the readers already exist, they were just not asked).

WHAT ALREADY EXISTS - checked first:
  * `gscript.conpane(target)` (gscript.py:2539, OpConPane_v0, 2026-09-10) returns a VI's CONNECTOR PANE as
    {terminal index: control label} straight from the FILE - the authoritative index->name map, and the one the
    dropped node's Terminals[] is ordered by. Nothing to build.
  * `gscript.node_terms(target, diagram, node)` / `node_terms_uid` (OpNodeTerms_v0) returns every terminal of ONE
    node with name, Is Source? and wire - a different reader from `net_map`, which is what produced the four-row
    list above.
  * `gscript.fp_labels(target)` gives the VI's own control/indicator labels for cross-checking.

READ-ONLY on the ORIGINAL (md5 asserted) and on the NI-shipped U2G VI. It reads `OpMoveIn_v0.vi` - the artefact
the failed probe run left in claudeDev - and does not modify it.

PREDICTION CONTRACT
  D1 `conpane(U2G)` returns a non-empty map; every index the dropped node exposes has a name there.
  D2 `node_terms` on the dropped U2G instance returns AT LEAST as many terminals as `net_map` did (4), and
     reports `is_source` per terminal so inputs and outputs are distinguishable without name-matching.
  D3 the two agree on the output terminal carrying the GObject reference.
  Either reader returning fewer rows than the connector pane has terminals is itself the finding.

  MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/diag_u2g_terminals.log \
      -- py -u tools/bench/diag_u2g_terminals.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g  # noqa: E402

U2G = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
OPIN = os.path.join(g.CLAUDEDEV, "OpMoveIn_v0.vi")
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
OUT = os.path.join(HERE, "u2g_terminals.json")

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    m0 = hashlib.md5(open(ORIGINAL, "rb").read()).hexdigest()
    gate("D0a original md5 before", m0 == ORIG_MD5, m0)
    out = {}

    print("\n=== A: the connector pane of the U2G VI itself (authoritative index -> label)", flush=True)
    try:
        cp = g.conpane(U2G)
        out["conpane"] = {str(k): v for k, v in cp.items()}
        for i, lab in sorted(cp.items()):
            print(f"    conpane[{i}] = {lab!r}", flush=True)
        gate("D1 conpane(U2G) returned a non-empty map", bool(cp), f"{len(cp)} terminals")
    except Exception as e:
        out["conpane_error"] = str(e)[:300]
        gate("D1 conpane(U2G) returned a non-empty map", False, f"{type(e).__name__} {str(e)[:200]}")

    print("\n=== B: the U2G VI's own front-panel labels", flush=True)
    try:
        fl = g.fp_labels(U2G)
        out["fp_labels"] = [list(r) for r in fl]
        print(f"    {fl}", flush=True)
    except Exception as e:
        out["fp_labels_error"] = str(e)[:300]
        print(f"    EXC {type(e).__name__} {str(e)[:200]}", flush=True)

    print("\n=== C: the DROPPED instance in OpMoveIn_v0.vi (left by the failed probe run)", flush=True)
    if not os.path.exists(OPIN):
        gate("D2 the dropped U2G instance is readable", False, f"{OPIN} not on disk")
    else:
        g.open_panel(OPIN)
        subs = g.report_all(OPIN, "SubVI")
        out["subvis"] = subs
        print(f"    SubVI objects: {[(s['uid'], s.get('label')) for s in subs]}", flush=True)
        rows_by_node = {}
        for n in range(40):
            uid, rows = g.node_terms_uid(OPIN, 0, n)
            if not uid:
                break
            rows_by_node[n] = (uid, rows)
        out["node_terms"] = {str(n): {"uid": u, "rows": r} for n, (u, r) in rows_by_node.items()}
        u2g_uids = {s["uid"] for s in subs}
        hit = [(n, u, r) for n, (u, r) in rows_by_node.items() if u in u2g_uids]
        for n, u, r in hit:
            print(f"    node[{n}] uid {u} ({len(r)} terminals):", flush=True)
            for row in r:
                print(f"        [{row['i']}] {row['name']!r}  is_source={row['is_source']}  wire={row['wire']}",
                      flush=True)
        gate("D2 node_terms sees the dropped U2G with its terminals", bool(hit),
             f"{[(n, u, len(r)) for n, u, r in hit]}")
        if hit:
            n_max = max(len(r) for _n, _u, r in hit)
            gate("D2b node_terms reports MORE terminals than net_map's four", n_max > 4, f"{n_max} terminals")

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1, default=str)
    m1 = hashlib.md5(open(ORIGINAL, "rb").read()).hexdigest()
    gate("D0b original md5 after", m1 == ORIG_MD5, m1)
    g._lv = None
    print(f"\n=== diag_u2g_terminals: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
