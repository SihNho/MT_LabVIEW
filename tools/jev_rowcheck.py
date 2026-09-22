r"""jev_rowcheck.py - insertion #5 of the SECOND WAVE table in docs/jev-integration-plan.md: ROW-TABLE CHECK.

    py tools/jev_rowcheck.py tools/bench/d1_rewire_sources.json [--limit N]

One judgement per PLANNED RE-WIRING ROW - (source uid, terminal) -> (sink uid, terminal) - against the
measured terminal tables this project already owns:

    tools/bench/d1_rewire_sources.json   the 109 cut terminals, each with its wire, its source and its action
    tools/bench/main_vi_nodeterms.json   every diagram's nodes with their terminal index / name / direction

The model sees the row and ONLY the measured entries that mention either uid; it never sees the VI. It answers
one noul: is this row consistent with the measurement? Output is one line per row:

    JEV-ROW | <n> | ok/suspect p=<p>

ADVISORY. It is a reader of a table, not a gate on a build: a "suspect" row is a row to re-measure, and a row
the tables do not mention at all is reported as `unknown`, never as ok.

PRIOR ART CHECKED before writing: tools/jev.py (transport, unknown band); tools/bench/d1_rewire_sources.json
and main_vi_nodeterms.json (the measured tables - read, never rewritten); tools/jev_drift.py /
tools/jev_preflight.py (sibling advisories). No LabVIEW, no COM.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402

SOURCES = os.path.join(BENCH, "d1_rewire_sources.json")
NODETERMS = os.path.join(BENCH, "main_vi_nodeterms.json")

ROW_Q = {
    "type": "noul",
    "instructions": (
        "A LabVIEW block diagram is being re-wired. `row` is ONE planned connection: a SOURCE terminal "
        "(an object uid, a terminal index, the terminal's name) and the SINK terminal it must drive, plus the "
        "wire that currently carries it. `measured_source` and `measured_sink` are the rows for those two uids "
        "in this project's own measured terminal tables - the only ground truth available. Decide whether the "
        "planned row is CONSISTENT with the measurement: do both uids appear, does each named terminal exist "
        "at that index with that name, and does the direction agree (the source end is a source, the sink end "
        "is a sink)? Judge the row against the tables only. A row the tables describe exactly is consistent "
        "even if the connection looks unusual; a row whose uid, index, name or direction disagrees with the "
        "tables is not, however plausible it reads."),
    "criteria": {
        "true": ("Every element of the row is confirmed by the measured entries: both uids are present, the "
                 "terminal index and name match, and the source/sink directions agree with the tables."),
        "false": ("At least one element contradicts the measured entries - a uid the tables give different "
                  "terminals for, a terminal name or index that does not appear on that uid, a direction the "
                  "other way round, or the two ends swapped."),
    },
}


def load_tables(sources=SOURCES, nodeterms=NODETERMS):
    """(rows, by_uid) - the 109 cut-terminal rows and a uid -> list-of-measured-entries index."""
    rows, by_uid = [], {}
    try:
        with open(sources, encoding="utf-8") as fh:
            doc = json.load(fh)
        rows = doc.get("rows") or []
    except (OSError, ValueError):
        rows = []
    for r in rows:
        for end in (r, r.get("source") or {}):
            u = end.get("uid")
            if u is None:
                continue
            by_uid.setdefault(int(u), []).append(
                {"table": "d1_rewire_sources", "uid": int(u), "i": end.get("i"), "name": end.get("name"),
                 "is_source": end.get("is_source"), "wire": r.get("wire"), "kind": end.get("kind")})
    try:
        with open(nodeterms, encoding="utf-8") as fh:
            nd = json.load(fh)
        for dnum, d in (nd.get("diagrams") or {}).items():
            for n in d.get("nodes") or []:
                u = n.get("uid")
                if u is None:
                    continue
                for t in n.get("terms") or []:
                    by_uid.setdefault(int(u), []).append(
                        {"table": "main_vi_nodeterms", "uid": int(u), "diagram": dnum,
                         "owner": d.get("owner"), "i": t.get("i"), "name": t.get("name"),
                         "is_source": t.get("is_source"), "wire": t.get("wire")})
    except (OSError, ValueError):
        pass
    return rows, by_uid


def row_text(row):
    """One readable line for a planned row."""
    s, k = row.get("source") or {}, row
    return ("source uid %s terminal[%s] %r (is_source=%s)  ->  sink uid %s terminal[%s] %r (is_source=%s)"
            "  via wire %s" % (s.get("uid"), s.get("i"), s.get("name"), s.get("is_source"),
                               k.get("uid"), k.get("i"), k.get("name"), k.get("is_source"), k.get("wire")))


def entries_for(row, by_uid, limit=12):
    """(measured source entries, measured sink entries) - only the rows mentioning that uid."""
    s = (row.get("source") or {}).get("uid")
    k = row.get("uid")
    return (by_uid.get(int(s), [])[:limit] if s is not None else [],
            by_uid.get(int(k), [])[:limit] if k is not None else [])


def check_row(row, by_uid, timeout=25, retries=0, purpose="rowcheck"):
    """(p, verdict, err). verdict is 'ok' / 'suspect' / 'unknown' by the project's band."""
    ms, mk = entries_for(row, by_uid)
    if not ms and not mk:
        return None, "unknown", "neither uid appears in the measured tables"
    state = {"row": row_text(row),
             "measured_source": json.dumps(ms, ensure_ascii=False)[:2400],
             "measured_sink": json.dumps(mk, ensure_ascii=False)[:2400]}
    resp, err = jev.ask(state, {"consistent": ROW_Q}, purpose=purpose, timeout=timeout, retries=retries)
    if err:
        return None, "unknown", err
    p = jev.noul(resp, "consistent")
    if p is None:
        return None, "unknown", "no noul in response"
    v = jev.verdict(p)
    return p, {"yes": "ok", "no": "suspect"}.get(v, "unknown"), None


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    path = argv[0] if argv else SOURCES
    limit = None
    if "--limit" in argv:
        try:
            limit = int(argv[argv.index("--limit") + 1])
        except (IndexError, ValueError):
            limit = None
    if not os.path.isabs(path):
        path = os.path.join(ROOT, path)
    try:
        with open(path, encoding="utf-8") as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as e:
        print("JEV-ROW | - | unreadable %s: %s" % (os.path.basename(path), e))
        return 2
    planned = doc.get("rows") if isinstance(doc, dict) else doc
    if not isinstance(planned, list):
        print("JEV-ROW | - | no `rows` list in %s" % os.path.basename(path))
        return 2
    _tbl_rows, by_uid = load_tables()
    if limit:
        planned = planned[:limit]
    n_ok = n_suspect = n_unknown = 0
    for i, row in enumerate(planned):
        p, verdict, err = check_row(row, by_uid)
        n_ok += verdict == "ok"
        n_suspect += verdict == "suspect"
        n_unknown += verdict == "unknown"
        print("JEV-ROW | %d | %s p=%s%s" % (
            i, verdict, ("%.2f" % p) if p is not None else "?", ("  (%s)" % err[:60]) if err else ""))
        sys.stdout.flush()
    print("JEV-ROW | TOTAL | %d ok / %d suspect / %d unknown of %d" % (
        n_ok, n_suspect, n_unknown, len(planned)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
