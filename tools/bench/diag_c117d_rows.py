"""Card 117-4 (offline, no LabVIEW, read-only): facts for the QRT-W draft row table on the SAVED L2-R1 graph.

Existing tools used, not edited (same set as diag_c117b_qrt.py:3-6): stagesim.base_state/cdiff_inputs/graph
(tools/stagesim.py), vigraph.key_parts, jev_candidates._ancestors, stage_prerun.read_stage_runs/read_records/
_run_pattern/_run_clean (tools/stage_prerun.py:2221,2333,2347). Nothing here opens LabVIEW or writes outside
tools/bench/diag_c117d_*.
Prediction contract: graph md5 == e429f7ad..., facts md5 == bee2a8f3...; every focus uid is present in the graph with
>= 1 terminal row; per focus uid the script records every terminal (name, direction, wire, frame diagram -> loop) and,
per wire, every terminal on it (so a source with sinks outside the QRT pair is visible); a class census of the bed for
the classes a QRT-W step would copy (Bundler / Unbundler / QuotientRemainder / queue primitives); and, per clean past
stage run, its pattern signature (for T4 proven_pattern). Writes tools/bench/diag_c117d_rows.json; ends with one RESULT.
"""
import collections, hashlib, json, os, sys

ROOT = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                # noqa: E402

B = os.path.join(ROOT, "tools", "bench")
GP = os.path.join(B, "graph_l2r1_saved_20260928.json")
FP = os.path.join(B, "facts_c117_qrt.json")
OUT = os.path.join(B, "diag_c117d_rows.json")
LOOPS = {637: "1.1", 10170: "1.2", 23032: "1.5", 23041: "1.7"}
BODY = {639: 637, 23166: 10170, 23405: 23041}
FOCUS = [6810, 30117, 4580, 5119, 10068, 29240, 11608, 11576, 1114, 2626, 376, 11261, 11363, 11310, 5058, 8634, 28083,
         29625, 29973, 10177, 9503, 29777, 10114, 29415, 20497, 22703, 3045, 2136, 12195]
# run 1 (diag_c117d_rows.log:45,167-172) gated #644 (the loop i terminal) and the three WhileLoops, which own no rows of
# their own in this graph (a loop's terminals sit on its tunnels / Diagram) - the contract was wrong, not the graph.
# They are listed as INFO below, not gated.
INFO_ONLY = [644, 637, 10170, 23041]
npass = nfail = 0
first_fail = None


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(ok, label):
    global npass, nfail, first_fail
    print(("  PASS  " if ok else "  FAIL  ") + label)
    if ok:
        npass += 1
    else:
        nfail += 1
        first_fail = first_fail or label


gate(md5(GP) == "e429f7ad7b2eebdaabaf0db1a462f10e", "G0 md5 graph_l2r1_saved == card")
gate(md5(FP) == "bee2a8f3db90a0e87394d5b06ab1f2f8", "G0b md5 facts_c117_qrt == card")
g = json.load(open(GP, encoding="utf-8"))
print("GRAPH keys", sorted(g.keys()))
terms = g.get("terminals") or []
objs = dict((int(o["uid"]), o) for o in g.get("objs") or [] if o.get("uid") is not None)
print("terminals", len(terms), "objs", len(objs), "objkeys", sorted((list(objs.values()) or [{}])[0].keys()))
import stagesim as SS          # noqa: E402
owners_raw = SS.base_state(g)["owners"]
print("owners n", len(owners_raw), "sample", list(owners_raw.items())[:3])


def owner_of(u):
    o = owners_raw.get(str(u)) or owners_raw.get(u)
    if isinstance(o, (list, tuple)) and len(o) >= 2:
        return o[0], int(o[1]) if str(o[1]).lstrip("-").isdigit() else o[1]
    return None


def loop_of_diagram(d, depth=0):
    """walk owners from a diagram uid up to a known loop body."""
    seen = []
    x = d
    while x is not None and depth < 30:
        seen.append(x)
        if x in BODY:
            return LOOPS[BODY[x]], seen
        o = owner_of(x)
        if not o:
            break
        x = o[1] if isinstance(o[1], int) else None
        depth += 1
    return "top", seen


by_owner = collections.defaultdict(list)
by_wire = collections.defaultdict(list)
for r in terms:
    by_owner[int(r["owner_uid"])].append(r)
    if r.get("wire_uid"):
        by_wire[int(r["wire_uid"])].append(r)


def trow(r):
    fd = r.get("frame_diagram")
    lp = loop_of_diagram(int(fd))[0] if fd else None
    return {"term_uid": r["term_uid"], "name": r.get("term_name"), "src": bool(r.get("is_source")),
            "wire": r.get("wire_uid"), "owner": r.get("owner_uid"), "owner_class": r.get("owner_class"),
            "term_class": r.get("term_class"), "fd": fd, "loop": lp}


focus = {}
for u in FOCUS:
    rows = [trow(r) for r in by_owner.get(u, [])]
    o = objs.get(u, {})
    own = owner_of(u)
    lp = loop_of_diagram(own[1])[0] if own and isinstance(own[1], int) else None
    wires = {}
    for r in rows:
        if r["wire"]:
            wires[str(r["wire"])] = [trow(x) for x in by_wire.get(int(r["wire"]), [])]
    focus[str(u)] = {"class": o.get("class"), "label": o.get("label") or o.get("name"), "owner": own, "loop": lp,
                     "terminals": rows, "wires": wires}
    gate(bool(rows), "G1 #{0} ({1}) has terminal rows: {2}".format(u, o.get("class"), len(rows)))
    print("FOCUS", u, o.get("class"), "owner", own, "loop", lp)
    for r in rows:
        on = by_wire.get(int(r["wire"]), []) if r["wire"] else []
        print("   T{0:>6} {1:<32} {2} w{3} fd{4}({5}) ->".format(r["term_uid"], str(r["name"])[:32], "SRC" if r["src"] else "snk",
                                                              r["wire"], r["fd"], r["loop"]),
              ["#{0}{1}:{2}{3}".format(x["owner_uid"], x.get("owner_class"), x.get("term_name"), "*" if x.get("is_source") else "")
               for x in on if int(x["owner_uid"]) != u][:8])

for u in INFO_ONLY:
    print("INFO", u, (objs.get(u) or {}).get("class"), "rows", len(by_owner.get(u, [])), "owner", owner_of(u))
# loop i terminal: the Diagram-639 source on w3268
print("I-TERM on w3268", [trow(x) for x in by_wire.get(3268, []) if x.get("is_source")])

# Bundler / Unbundler sizes and loops (copy_in donors for a QRT-W step)
sizes = {}
for u, o in sorted(objs.items()):
    if o.get("class") in ("Bundler", "Unbundler", "NamedBundler", "NamedUnbundler"):
        rows = by_owner.get(u, [])
        fds = sorted(set(r.get("frame_diagram") for r in rows))
        lp = [loop_of_diagram(int(f))[0] for f in fds if f]
        sizes[str(u)] = {"class": o.get("class"), "n_in": sum(1 for r in rows if not r.get("is_source")),
                         "n_out": sum(1 for r in rows if r.get("is_source")), "fd": fds, "loop": lp,
                         "names": [(r.get("term_name"), bool(r.get("is_source")), r.get("wire_uid")) for r in rows]}
        print("SIZE", u, sizes[str(u)])

census = collections.Counter(o.get("class") for o in objs.values())
want = [c for c in census if any(k in str(c) for k in ("Bundl", "Unbundl", "Quotient", "Queue", "Function"))]
print("CENSUS", {c: census[c] for c in sorted(want, key=str)})
qr = [u for u, o in objs.items() if o.get("class") == (objs.get(10068) or {}).get("class")]
bd = [u for u, o in objs.items() if o.get("class") == (objs.get(11608) or {}).get("class")]
ub = [u for u, o in objs.items() if "Unbundl" in str(o.get("class"))]
print("SAMECLASS as #10068", sorted(qr), "as #11608", sorted(bd), "Unbundle*", sorted(ub))

# ---- T4: signatures of clean past stage runs (stage_prerun predicate, read only)
import stage_prerun as SP     # noqa: E402
runs = SP.read_stage_runs()
recs = SP.read_records()
sigs = []
for r in runs:
    if r.get("by") != SP.COUNTED_BY:
        continue
    try:
        pat = SP._run_pattern(r, recs)
    except Exception as e:                                                        # noqa: BLE001
        pat = "ERR %s" % e
    try:
        clean = SP._run_clean(r)
    except Exception as e:                                                        # noqa: BLE001
        clean = "ERR %s" % e
    sigs.append({"stage": r.get("stage"), "log": r.get("log"), "clean": clean,
                 "pattern": sorted(pat) if isinstance(pat, set) else pat})
    print("RUN", r.get("stage"), r.get("log"), "clean", clean, "pattern", sorted(pat) if isinstance(pat, set) else pat)
gate(len(sigs) > 0, "G2 stage_runs read: {0} bgrun records".format(len(sigs)))

json.dump({"schema": "diag/c117d-rows", "graph": {"path": "tools/bench/graph_l2r1_saved_20260928.json", "md5": md5(GP)},
           "focus": focus, "census": {str(c): census[c] for c in want},
           "same_class": {"QR_like_10068": sorted(qr), "bundle_like_11608": sorted(bd), "unbundle": sorted(ub)},
           "bundler_sizes": sizes,
           "runs": sigs}, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
gate(os.path.exists(OUT), "G3 written " + OUT)
print(protocol.result_line(protocol.make_result(npass, nfail, first_fail,
                                                [{"path": "tools/bench/diag_c117d_rows.json", "md5": md5(OUT)}])))
