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

WIRED INTO `tools/stagekit.py` 2026-09-23 (user: "배선 하나하나 물어본다던지 Jev 최대한 활용하는 방법으로 제시한게
위의 테이블이잖아"). `Stage.plan_rows(rows)` declares a stage's planned re-wiring rows and `check_rows()` below
reads them FROM MEMORY, before the stage's first mutating call. The CLI is unchanged.

TWO ROW SCHEMAS ARE ACCEPTED (`normalise_row`), because the table this reads is written by two different
producers; every other shape is reported as `unknown`, never guessed at:

  A  the d1_rewire_sources.json shape - the SINK is the row itself, the source is nested:
       {"uid": 10429, "i": 21, "name": "Tunnel", "is_source": false, "wire": 1731,
        "source": {"uid": 23868, "i": 3, "name": "output", "is_source": true}}

  B  the SEVERED-ROW TABLE shape that M3a-4's first act writes - both ends named, either as sub-dicts or flat:
       {"row": "D", "wire": 1731,
        "source": {"uid": 23868, "term": 3,  "name": "output"},      # `term` | `i` | `index` | `terminal`
        "sink":   {"uid": 10429, "term": 21, "name": "Tunnel"}}      # `sink` | `dest` | `dst` | `target`
     flat keys work too: src_uid/src_term/src_name (or source_uid/...) and sink_uid/sink_term/sink_name.
     `row`/`label`/`id` is carried through as the row's label; `wire` is optional in both shapes.

PRIOR ART CHECKED before writing: tools/jev.py (transport, unknown band); tools/bench/d1_rewire_sources.json
and main_vi_nodeterms.json (the measured tables - read, never rewritten); tools/jev_drift.py /
tools/jev_preflight.py (sibling advisories). No LabVIEW, no COM.
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402

SOURCES = os.path.join(BENCH, "d1_rewire_sources.json")
NODETERMS = os.path.join(BENCH, "main_vi_nodeterms.json")
GATE_LOG = os.path.join(BENCH, "jev_gate.log")     # the one place every Jev advisory in this project lands

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


# ------------------------------------------------------------------- the in-memory API (stagekit, 2026-09-23)
_TERM_KEYS = ("i", "term", "index", "terminal", "term_index", "terms_index")
_SINK_KEYS = ("sink", "dest", "dst", "target")
_SRC_KEYS = ("source", "src")


def _end(d, keys, prefix):
    """One end of a row as {uid, i, name, is_source}, from a sub-dict or from flat `<prefix>_*` keys."""
    sub = None
    for k in keys:
        v = d.get(k)
        if isinstance(v, dict):
            sub = v
            break
    if sub is None:
        sub = {}
        for suffix, out in (("uid", "uid"), ("name", "name")):
            for pre in prefix:
                if pre + "_" + suffix in d:
                    sub[out] = d[pre + "_" + suffix]
                    break
        for tk in _TERM_KEYS:
            hit = next((pre + "_" + tk for pre in prefix if pre + "_" + tk in d), None)
            if hit:
                sub["i"] = d[hit]
                break
        if "uid" not in sub:
            return None
    out = {"uid": sub.get("uid"), "name": sub.get("name"), "is_source": sub.get("is_source")}
    for tk in _TERM_KEYS:
        if tk in sub:
            out["i"] = sub[tk]
            break
    out.setdefault("i", None)
    return out if out.get("uid") is not None else None


def normalise_row(row):
    """Either accepted schema -> the schema `check_row` reads (shape A), or None when neither fits.

    Shape A is returned unchanged apart from defaults; shape B is folded into it. A row whose SINK end has no
    uid is not guessed at - the caller reports it as `unknown`, which is what the docstring promises."""
    if not isinstance(row, dict):
        return None
    src = _end(row, _SRC_KEYS, ("src", "source"))
    sink = _end(row, _SINK_KEYS, ("sink", "dst", "dest", "target"))
    if sink is None and row.get("uid") is not None:      # shape A: the row itself IS the sink
        sink = {"uid": row.get("uid"), "i": row.get("i"), "name": row.get("name"),
                "is_source": row.get("is_source")}
    if sink is None:
        return None
    out = dict(sink)
    out["source"] = src or {}
    out["wire"] = row.get("wire")
    out["label"] = row.get("row") or row.get("label") or row.get("id")
    return out


def check_rows(rows, by_uid=None, limit=None, budget_s=60.0, timeout=20, retries=0, purpose="rowcheck-stage"):
    """Judge an IN-MEMORY row list. Returns [{i,label,verdict,p,err,text}]. Never raises, never blocks.

    Time-capped by construction: once `budget_s` of wall clock has been spent the remaining rows are returned
    with verdict `skipped` and no call is made, so a 66-row stage cannot hold a build behind 66 HTTP calls."""
    t0 = time.time()
    out = []
    try:
        rows = list(rows or [])
    except TypeError:
        return out
    if limit:
        rows = rows[:limit]
    if by_uid is None:
        try:
            _r, by_uid = load_tables()
        except Exception:                       # noqa: BLE001 - a missing table is `unknown`, not a crash
            by_uid = {}
    have_key = bool(jev.get_key())
    for i, raw in enumerate(rows):
        label = None
        if isinstance(raw, dict):
            label = raw.get("row") or raw.get("label") or raw.get("id")
        label = str(label) if label is not None else str(i)
        row = normalise_row(raw)
        if row is None:
            out.append({"i": i, "label": label, "verdict": "unknown", "p": None,
                        "err": "row matches neither accepted schema", "text": repr(raw)[:160]})
            continue
        text = row_text(row)
        if not have_key:
            out.append({"i": i, "label": label, "verdict": "skipped", "p": None, "err": "no key",
                        "text": text})
            continue
        if time.time() - t0 > budget_s:
            out.append({"i": i, "label": label, "verdict": "skipped", "p": None, "err": "budget spent",
                        "text": text})
            continue
        try:
            p, verdict, err = check_row(row, by_uid, timeout=timeout, retries=retries, purpose=purpose)
        except Exception as e:                  # noqa: BLE001
            p, verdict, err = None, "unknown", "%s: %s" % (type(e).__name__, str(e)[:80])
        out.append({"i": i, "label": label, "verdict": verdict, "p": p, "err": err, "text": text})
    return out


def stage_lines(rows, stage_name, by_uid=None, limit=None, budget_s=60.0, write_log=True):
    """The stagekit entry point: one `JEV-ROWCHECK | <stage> | <row> | <class> p=<p>` line per row.

    Returns the list of lines (the caller prints them into its own log). They are also appended to
    tools/bench/jev_gate.log, beside every other Jev advisory. ADVISORY: nothing here refuses anything, and
    every failure - no key, no network, a malformed row - is a line, not an exception."""
    results = check_rows(rows, by_uid=by_uid, limit=limit, budget_s=budget_s)
    lines = []
    if not results:
        return lines
    if all(r["verdict"] == "skipped" and r.get("err") == "no key" for r in results):
        lines.append("JEV-ROWCHECK | %s | - | skipped (no key) for %d row(s)" % (stage_name, len(results)))
    else:
        for r in results:
            lines.append("JEV-ROWCHECK | %s | %s | %s p=%s%s" % (
                stage_name, r["label"], r["verdict"],
                ("%.2f" % r["p"]) if r["p"] is not None else "?",
                ("  (%s)" % str(r["err"])[:60]) if r.get("err") else ""))
        n = {}
        for r in results:
            n[r["verdict"]] = n.get(r["verdict"], 0) + 1
        lines.append("JEV-ROWCHECK | %s | TOTAL | %s of %d row(s)" % (
            stage_name, ", ".join("%d %s" % (v, k) for k, v in sorted(n.items())), len(results)))
    if write_log:
        try:
            with open(GATE_LOG, "a", encoding="utf-8") as fh:
                ts = time.strftime("%Y-%m-%d %H:%M:%S")
                fh.write("".join("%s | %s | rowcheck\n" % (ts, ln) for ln in lines))
        except OSError:
            pass
    return lines


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
