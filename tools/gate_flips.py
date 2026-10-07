# ---
# labview: none
# hardware: none
# ---
r"""gate_flips - measure, at DECISION level, which bench logs a gate edit flips. PORTED to the main repo by card chat-T3
(PD347(a)) from bench arm A (V6_bench\A\tools\gate_flips.py, built there by card 145-a1-1, reviewed by reading it: loads
both sides by path, never writes or monkeypatches the live modules, md5-checks them before and after); unchanged except
this paragraph. Arm A's own history follows. (card 145-a1-1, PD341(c); the device for the
retrospective-cycle144 `inference-over-measurement` fault: card 144-a3-2 wrote "only the s03 log flips" into a pass clause and
19 benign logs plus one real hole (diag_c144_a2_3_adopt.log) flipped too). A gate-change card READS this tool's output before
it writes its pass clause.

OLD vs NEW = two sets of gate modules (`tools/gateclass.py`, `tools/stagexec.py`). Default old = the live files; a patched copy
is given BY PATH (`--new gateclass=C:/tmp/gateclass_x.py`, or a bare path whose file name starts with `gateclass`/`stagexec`).
Every module, live or copy, is loaded by importlib under a unique module name; the live files are never written and the imported
live modules are never monkeypatched (the side's stagexec gets its own `gateclass` attribute bound to that side's gateclass).

Per log (corpus default `tools/bench/*.log`, same as tools/bench/selftest_c144_a3_1_hardmark.py:82), each side decides:
  adopt        stagexec.adopt_verdict(last BGRUN segment, required)["ok"]     (the failure check adopt_scratch runs,
               stagexec.py:3782-3815,3830-3832)
  soft_only    gateclass.soft_only(protocol.last_segment, all_result_lines)   (guard_peer's LOG-only release)
  address_only gateclass.address_only(same segment)                           (PD337(b) release)
  hard_marker  gateclass.HARD_MARK_RE.search(whole file)                       (the 144-a3-1 corpus count)
True = ACCEPTED (adopted / owes no review). Flip kind per decision: refused->accepted, accepted->refused, unchanged.
Side-independent facts: Traceback present; summed RESULT gates.fail; number of LOG-class FAIL lines (NEW side's classify_line);
unaccounted_fail = max(0, sum - LOG lines). SAFETY rows = logs that become accepted on any decision AND carry a Traceback or an
unaccounted RESULT fail; a safe edit has an empty SAFETY list.

Existing tools reused, nothing rebuilt: gateclass.soft_only/address_only/classify_line/FAIL_LINE_RE, stagexec.adopt_verdict,
protocol.last_segment/all_result_lines/result_line/make_result. Found before writing: selftest_c144_a3_1_hardmark.py (one fixed
regex swap, not a module-path tool); no other old-vs-new gate comparer in tools/ (grep 'adopt_verdict' tools/*.py).

Usage: py tools/gate_flips.py --new gateclass=<copy.py> [--new stagexec=<copy.py>] [--old ...] --tag <name>
       [--corpus <glob>]... [--log <file>]... [--required <log name>=E1,NG,...]... [--all-rows] [--out <json>]
Writes tools/bench/gate_flips_<tag>.json, prints one `FLIP` line per flipped decision and one `SAFETY` line per unsafe log,
ends with a C6 RESULT line (FAIL when SAFETY is non-empty or a live module's md5 changed during the run).
"""
import argparse
import glob
import hashlib
import importlib.util
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
for _p in (HERE, BENCH):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import protocol  # noqa: E402

MODULES = ("gateclass", "stagexec")
LIVE = {m: os.path.join(HERE, m + ".py") for m in MODULES}
DEFAULT_CORPUS = [os.path.join(BENCH, "*.log")]
# the one log adopt_scratch judged with a required list (diag_c144_a2_3_adopt.py:49; selftest_c144_a3_1_hardmark.py:46)
DEFAULT_REQUIRED = {"diag_c143_p4s03v18_scratch.log": ["E1", "NG", "PRIM", "FR", "D", "TD", "PB", "PS"]}
DECISIONS = ("adopt", "soft_only", "address_only")
TRACEBACK = "Traceback (most recent call last)"
_N = [0]


def md5(path):
    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def _load(name, path, label):
    _N[0] += 1
    uniq = "_gateflips_{0}_{1}_{2}".format(label, name, _N[0])
    spec = importlib.util.spec_from_file_location(uniq, path)
    mod = importlib.util.module_from_spec(spec)
    # a copy runs AS IF it sat at the live location: stagexec resolves its data files from __file__ at import
    # (stagexec.py:47-49 -> bench/memory_model.json); the source is still read from `path` by the loader.
    mod.__file__ = LIVE[name]
    sys.modules[uniq] = mod
    spec.loader.exec_module(mod)
    return mod


def load_side(paths, label):
    """(gateclass module, stagexec module) for one side, both loaded by path; stagexec is bound to THIS side's gateclass."""
    import stagesim, vigraph  # noqa: F401,E401  pre-import stagexec's deps with the live gateclass in sys.modules
    gpath = os.path.abspath(paths.get("gateclass") or LIVE["gateclass"])
    spath = os.path.abspath(paths.get("stagexec") or LIVE["stagexec"])
    G = _load("gateclass", gpath, label)
    had = "gateclass" in sys.modules
    saved = sys.modules.get("gateclass")
    sys.modules["gateclass"] = G
    try:
        S = _load("stagexec", spath, label)
    finally:
        if had:
            sys.modules["gateclass"] = saved
        else:
            sys.modules.pop("gateclass", None)
    S.gateclass = G
    return G, S, {"gateclass": {"path": gpath, "md5": md5(gpath)}, "stagexec": {"path": spath, "md5": md5(spath)}}


def parse_spec(items):
    """['gateclass=p', 'p/stagexec_x.py'] -> {'gateclass': p, 'stagexec': p}."""
    out = {}
    for it in items or []:
        if "=" in it and it.split("=", 1)[0] in MODULES:
            name, path = it.split("=", 1)
        else:
            path = it
            stem = os.path.basename(it).lower()
            name = next((m for m in MODULES if stem.startswith(m)), None)
            if not name:
                raise SystemExit("gate_flips: cannot tell which module {0!r} replaces - use gateclass=<path> / stagexec=<path>"
                                 .format(it))
        if not os.path.isfile(path):
            raise SystemExit("gate_flips: no such module file: {0}".format(path))
        out[name] = path
    return out


def rel(p):
    """Project-relative forward-slash path; the absolute path when p is on another drive (a %TEMP% corpus)."""
    try:
        return os.path.relpath(p, ROOT).replace("\\", "/")
    except ValueError:
        return os.path.abspath(p).replace("\\", "/")


def rd(p):
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def _segments(t):
    i = t.rfind("BGRUN START")
    aseg = t[i:] if i >= 0 else t
    pseg = protocol.last_segment(t)[2]
    return aseg, pseg


def _fail_sum(results):
    s = 0
    for d in results:
        g = d.get("gates") if isinstance(d.get("gates"), dict) else None
        if g is not None:
            try:
                s += int(g.get("fail", 0))
                continue
            except (TypeError, ValueError):
                pass
        if d.get("status") not in ("PASS", "SKIP"):
            s += 1                                       # malformed / gate-less failing RESULT line counts as one
    return s


def facts(seg, G):
    res = protocol.all_result_lines(seg)
    fsum = _fail_sum(res)
    nlog = sum(1 for ln in seg.splitlines() if G.FAIL_LINE_RE.match(ln) and G.classify_line(ln) == "log")
    return {"traceback": TRACEBACK in seg, "result_fail_sum": fsum, "log_fail_lines": nlog,
            "unaccounted_fail": max(0, fsum - nlog)}


def decide(t, aseg, pseg, res, G, S, req):
    a = S.adopt_verdict(aseg, req)
    return {"adopt": bool(a["ok"]), "adopt_why": a["why"][:3], "soft_only": bool(G.soft_only(pseg, res)),
            "address_only": bool(G.address_only(pseg, res)), "hard_marker": bool(G.HARD_MARK_RE.search(t))}


def flip_kind(o, n):
    return "refused->accepted" if (n and not o) else ("accepted->refused" if (o and not n) else "unchanged")


def collect_logs(corpus, extra):
    seen, out = set(), []
    for g in corpus:
        for p in sorted(glob.glob(g)):
            k = os.path.normcase(os.path.abspath(p))
            if k not in seen:
                seen.add(k)
                out.append(p)
    for p in extra or []:
        k = os.path.normcase(os.path.abspath(p))
        if k not in seen and os.path.isfile(p):
            seen.add(k)
            out.append(p)
    return out


def run(old=None, new=None, tag="adhoc", corpus=None, extra=None, required=None, all_rows=False, out=None, quiet=False):
    """The comparison. Returns the report dict and writes it to `out` (default tools/bench/gate_flips_<tag>.json)."""
    t0 = time.time()
    live0 = {m: md5(p) for m, p in LIVE.items()}
    Go, So, old_src = load_side(old or {}, "old")
    Gn, Sn, new_src = load_side(new or {}, "new")
    req_map = dict(DEFAULT_REQUIRED)
    req_map.update(required or {})
    corpus = list(corpus or DEFAULT_CORPUS)
    logs = collect_logs(corpus, extra)
    rows, safety = [], []
    counts = {"logs": len(logs), "hard_marker_changed": 0, "flip_logs": 0, "unchanged_logs": 0}
    for d in DECISIONS:
        counts[d] = {"refused->accepted": 0, "accepted->refused": 0}
    for p in logs:
        name = os.path.basename(p)
        t = rd(p)
        aseg, pseg = _segments(t)
        res = protocol.all_result_lines(pseg)
        req = req_map.get(name, ())
        do = decide(t, aseg, pseg, res, Go, So, req)
        dn = decide(t, aseg, pseg, res, Gn, Sn, req)
        flips = {d: flip_kind(do[d], dn[d]) for d in DECISIONS}
        hard_changed = do["hard_marker"] != dn["hard_marker"]
        flipped = [d for d in DECISIONS if flips[d] != "unchanged"]
        if hard_changed:
            counts["hard_marker_changed"] += 1
        if flipped:
            counts["flip_logs"] += 1
            for d in flipped:
                counts[d][flips[d]] += 1
        else:
            counts["unchanged_logs"] += 1
        if not (flipped or hard_changed or all_rows):
            continue
        fa, fp = facts(aseg, Gn), facts(pseg, Gn)
        fx = {"traceback": fa["traceback"] or fp["traceback"],
              "result_fail_sum": max(fa["result_fail_sum"], fp["result_fail_sum"]),
              "log_fail_lines": max(fa["log_fail_lines"], fp["log_fail_lines"]),
              "unaccounted_fail": max(fa["unaccounted_fail"], fp["unaccounted_fail"])}
        kind = ("refused->accepted" if any(flips[d] == "refused->accepted" for d in DECISIONS) else
                "accepted->refused" if flipped else "unchanged")
        row = {"log": name, "path": rel(p), "kind": kind,
               "hard_marker": {"old": do["hard_marker"], "new": dn["hard_marker"]}}
        for d in DECISIONS:
            row[d] = {"old": do[d], "new": dn[d], "flip": flips[d]}
        row["adopt"]["why_old"], row["adopt"]["why_new"] = do["adopt_why"], dn["adopt_why"]
        row.update(fx)
        rows.append(row)
        for d in flipped:
            if not quiet:
                print("FLIP {0} {1} {2}".format(name, d, flips[d]), flush=True)
        up = [d for d in DECISIONS if flips[d] == "refused->accepted"]
        if up and (fx["traceback"] or fx["unaccounted_fail"] > 0):
            s = {"log": name, "accepted_by": up, "traceback": fx["traceback"], "unaccounted_fail": fx["unaccounted_fail"],
                 "result_fail_sum": fx["result_fail_sum"], "log_fail_lines": fx["log_fail_lines"]}
            safety.append(s)
            if not quiet:
                print("SAFETY {0} accepted_by={1} traceback={2} unaccounted_fail={3}".format(
                    name, ",".join(up), fx["traceback"], fx["unaccounted_fail"]), flush=True)
    live1 = {m: md5(p) for m, p in LIVE.items()}
    rep = {"schema": "gate_flips/1", "tag": tag, "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
           "old": old_src, "new": new_src, "corpus": {"globs": [rel(g) for g in corpus],
                                                       "extra": list(extra or []), "n_logs": len(logs)},
           "required": req_map, "counts": counts, "rows": rows, "safety": safety, "safe": not safety,
           "live_md5": {"before": live0, "after": live1, "unchanged": live0 == live1},
           "seconds": round(time.time() - t0, 1)}
    out = out or os.path.join(BENCH, "gate_flips_{0}.json".format(tag))
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rep, f, indent=1)
    rep["_out"] = out
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--old", action="append", default=[], help="module copy for the OLD side (default: live)")
    ap.add_argument("--new", action="append", default=[], help="module copy for the NEW side (default: live)")
    ap.add_argument("--tag", required=True)
    ap.add_argument("--corpus", action="append", default=[], help="glob(s) of logs (default tools/bench/*.log)")
    ap.add_argument("--log", action="append", default=[], help="extra log file(s)")
    ap.add_argument("--required", action="append", default=[], help="<log name>=E1,NG,... (adopt_verdict required)")
    ap.add_argument("--all-rows", action="store_true")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    if not re.match(r"^[A-Za-z0-9_.-]+$", a.tag):
        raise SystemExit("gate_flips: --tag must be [A-Za-z0-9_.-]+")
    req = {}
    for r in a.required:
        k, _, v = r.partition("=")
        req[k] = [x for x in v.split(",") if x]
    rep = run(parse_spec(a.old), parse_spec(a.new), a.tag, a.corpus or None, a.log, req, a.all_rows, a.out)
    c = rep["counts"]
    print("COUNTS logs {0} | hard-marker changed {1} | flip logs {2} | adopt {3} | soft_only {4} | address_only {5} | "
          "safety {6} | {7}s".format(c["logs"], c["hard_marker_changed"], c["flip_logs"], c["adopt"], c["soft_only"],
                                     c["address_only"], len(rep["safety"]), rep["seconds"]), flush=True)
    print("WROTE {0} md5 {1}".format(rep["_out"], md5(rep["_out"])), flush=True)
    P, F = [], []
    (P if rep["live_md5"]["unchanged"] else F).append("live gateclass/stagexec md5 unchanged")
    (P if rep["safe"] else F).append("SAFETY list empty ({0} log(s))".format(len(rep["safety"])))
    art = [{"path": rel(rep["_out"]), "md5": md5(rep["_out"])}]
    print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None, art)))
    return 0 if not F else 1


if __name__ == "__main__":
    sys.exit(main())
