r"""wiki_build - the subVI WIKI: one md5-gated JSON per VI, built from the machine, no model in it.

`docs/connectivity-map-plan.md` step 3. Targets: every `.vi` under `claudeDev\background VIs_COPY`
(94, byte-identical to `zz_LabView VI\background VIs` - rule 1: the originals are never opened), the D1
S1 copy `claudeDev\D1_s1_copy.vi` (= the main VI's bytes) and the current bed.

PER-VI JSON (`docs/wiki/subvi/<name>.json`)
    file md5 bytes
    connector_pane        [{index, label, direction, type}]  + connector_pane_source
    terminals             the reader table, each row tagged with its LEAF class
    wires                 the join (termed + termless), + severed
    graph_summary         {nodes, wires, loops, cases, sequences, locals, globals, subvi_calls[]}
    io_paths              {conpane output label: [conpane input labels that reach it]}  (vigraph)
    summary               ""  - the ONE-SENTENCE LLM line is a SEPARATE pass (Pre-decided 140: once per md5)
    call_sites_in_main    from tools/bench/main_vi_subvis.json

ROUTES, ALL MEASURED FIRST (`tools/bench/diag_wiki_probe.log` 12/0, `diag_wiki_probe2.log`):
  * class census      `gscript.report_all(vi, 'GObject')` - ONE call, every object's LEAF class, uid,
    position and owner class. 0.04 s / 35 objects .. 3.58 s / 3,926. It also supplies the Wire uids, so
    `allterms.all_wire_uids` is NOT called again per VI.
  * terminal table    `allterms.read_terms(vi)` - `Traverse('Terminal')`, INCLUSIVE of its subclasses.
  * CONNECTOR PANE    the chosen route, `connector_pane_source = "call-node-terminals"`: each subVI is
    DROPPED ONCE on a dated scratch copy of `claudeDev\EMPTY_v0.vi`, and the call node's own terminals
    (read by the same traverse) ARE the connector pane - label + direction, exactly the pane's assigned
    terminals. Verified against the front panel: `rect coord from center.vi` 4 == 4, `build cal image.vi`
    5 == 5. No VI Server `Connector Pane`/`Conpane.Connections[]` reader exists in this fleet (grep of
    gscript.py/NAMES.md: none), and the main-VI call-node fallback the brief allows would cover only the
    subVIs the main VI calls. `type` is left "" - no data-type property is reachable on this route.
    FALLBACK `"fp-control-terminals"`: the VI's own `ControlTerminal` rows (a SUPERSET of the pane).
  * subVI call names  `gscript.subvis(vi, d)` per Diagram index d (not recursive; SubVIs[] is per diagram).

md5 GATE (Pre-decided 140): a VI whose md5 equals its index entry is SKIPPED and logged "skipped,
unchanged". `--force` re-reads everything. Each VI's JSON AND the index are written the moment that VI
finishes, so a kill loses one file, not the run.

    MATERIAL=1 py tools/bgrun.py --max-min 90 --log tools/bench/wiki_build.log -- py -u tools/wiki_build.py
    py tools/wiki_build.py --only "rect coord*" --force
"""
import argparse
import collections
import fnmatch
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (HERE, os.path.join(HERE, "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import allterms as A                                                               # noqa: E402
import vigraph                                                                     # noqa: E402

BG = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
EXTRA = [os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"),
         os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_rowD_20260922_161040.vi")]
WIKI = os.path.join(ROOT, "docs", "wiki", "subvi")
INDEX = os.path.join(ROOT, "docs", "wiki", "index.json")
MAIN_SUBVIS = os.path.join(HERE, "bench", "main_vi_subvis.json")

# The terminal reader, rebindable by --op. `read_terms`' default is bound at def time, so every call
# site passes it explicitly.
OPREADER = [A.OP_ALLTERMS]

LOOPS = ("ForLoop", "WhileLoop", "TimedLoop")
CASES = ("CaseStructure", "Case", "CaseSelector", "EventStructure")
SEQS = ("FlatSequence", "StackedSequence", "Sequence", "FlatSequenceFrame")
SUBVI_CLASSES = ("SubVI", "PolymorphicSubVI")


def subvi_rows(target, diagram_index):
    """`gscript.subvis(strict=False)` returns (rows, err) - rows only, and an error on ONE diagram
    (an invalid index gives error 1055 on the node's own error out) never kills the VI's record."""
    rows, _err = g.subvis(target, diagram_index, strict=False)
    return rows


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def fact(line):
    print("  FACT  {0}".format(line), flush=True)


def targets():
    out = []
    for dp, _d, fs in os.walk(BG):
        for f in sorted(fs):
            if f.lower().endswith(".vi"):
                out.append(os.path.join(dp, f))
    return sorted(out) + [p for p in EXTRA if os.path.exists(p)]


def key_of(path):
    """The wiki key. NOT the bare file name: `background VIs` carries the subfolder
    `Tracking kernel (xy_profile)` whose two VIs REPEAT two top-level names
    (`Find xy center with sock corr.vi`, `Track xy and profile.vi`), so a basename key would silently
    merge four VIs into two. The key is the path relative to the copy folder, separators as `__`."""
    if path.startswith(BG):
        rel = os.path.relpath(path, BG)
    else:
        rel = os.path.basename(path)
    return os.path.splitext(rel)[0].replace(os.sep, "__")


def call_sites_index():
    try:
        d = json.load(open(MAIN_SUBVIS, encoding="utf-8"))
    except Exception:                                                              # noqa: BLE001
        return {}, ""
    out = collections.defaultdict(list)
    for uid, rec in d.get("by_uid", {}).items():
        out[rec["name"]].append({"node_uid": int(uid), "diagram": rec.get("diagram")})
    return out, d.get("vi", "")


def conpane_pass(paths, chunk=12):
    """{path: [{index, label, direction, type}]} - drop each VI on a scratch EMPTY_v0 copy and read the
    CALL NODE's terminals. Chunked so one bad VI costs one chunk, and every scratch is deleted."""
    out, failed = {}, {}
    for c0 in range(0, len(paths), chunk):
        part = paths[c0:c0 + chunk]
        scratch = os.path.join(g.CLAUDEDEV, "wikipane_{0}_{1}.vi".format(
            time.strftime("%H%M%S"), c0))
        shutil.copy2(EMPTY, scratch)
        try:
            g.open_panel(scratch)
            # The call node is identified by the uid the DROP created, never by the subVI's name: two
            # pairs of VIs share a name across the copy folder's subfolder (see key_of).
            owner_uids = {}
            seen = set(int(o["uid"]) for o in g.report_all(scratch, "GObject"))
            for i, p in enumerate(part):
                try:
                    g.drop_subvi(scratch, p, 0, (200 + 300 * (i % 8), 200 + 220 * (i // 8)))
                except Exception as e:                                             # noqa: BLE001
                    failed[p] = "drop: {0}".format(str(e)[:120])
                    continue
                now = g.report_all(scratch, "GObject")
                fresh = [int(o["uid"]) for o in now
                         if int(o["uid"]) not in seen and o["class"] in SUBVI_CLASSES]
                seen = set(int(o["uid"]) for o in now)
                if fresh:
                    owner_uids[p] = fresh
                else:
                    failed[p] = "drop added no SubVI/PolymorphicSubVI node"
            rows, _dt = A.read_terms(scratch, op=OPREADER[0])
            by_owner = collections.defaultdict(list)
            for r in rows:
                by_owner[r["owner_uid"]].append(r)
            for p in part:
                terms = []
                for uid in owner_uids.get(p, []):
                    for r in by_owner.get(uid, []):
                        terms.append({"label": r["term_name"],
                                      "direction": "output" if r["is_source"] else "input",
                                      "type": ""})
                if terms:
                    # MEASURED (smoke run 2026-09-23): the CALL NODE exposes every slot of the VI's
                    # connector-pane PATTERN, and an UNASSIGNED slot comes back with an empty Name and
                    # is_source False. `Find brightest peak.vi` returned 12 slots for 2 real terminals
                    # (== its 2 ControlTerminals); `rect coord from center.vi` returned 4 for 4. So the
                    # empty ones are dropped and only COUNTED. `index` is the TRAVERSE order, not the
                    # pattern's own index - no conpane-index property is reachable on this route.
                    for i, t in enumerate(terms):
                        t["index"] = i
                    blank = [t for t in terms if not t["label"]]
                    out[p] = [t for t in terms if t["label"]]
                    out[p + "\x00blank"] = len(blank)
                    if not out[p]:
                        failed[p] = "call node exposed {0} slots, all unassigned".format(len(blank))
                        del out[p]
                elif p not in failed:
                    failed[p] = "no call-node terminals (node class not in SubVIs[]?)"
        finally:
            try:
                g.close_panel(scratch)
            except Exception:                                                      # noqa: BLE001
                pass
            try:
                os.remove(scratch)
            except Exception as e:                                                 # noqa: BLE001
                fact("scratch NOT removed {0}: {1}".format(scratch, str(e)[:100]))
        fact("conpane chunk {0}..{1}: {2} read, {3} failed".format(
            c0, c0 + len(part) - 1, sum(1 for p in part if p in out),
            sum(1 for p in part if p in failed)))
    return out, failed


FS_KINDS = {"FlatSequenceOuterTunnel": "OUT", "FlatSequenceInnerTunnel": "IN"}


def read_fs_tunnels(path, objs, uids=None):
    """STEP 4b: every flat-sequence tunnel's two faces, READ from the machine, one op run per tunnel.

    NOTHING NEW IS BUILT: the two uid-addressed readers exist since 2026-09-18
    (`tools/recipes/build_opfstunnelterm_v2.py`, 38/38) - `OpFsTunnelTerm_v0` (FSOT: `OuterTerminal`
    3195B800 / `InnerTerminal` 3195B801) and `OpFsInnerTunnelTerm_v0` (FSIT: `LeftTerm` 1C3A9000 /
    `RightTerm` 1C3A9001) - and their poisoned caller `read_tunnel` is imported, never re-typed.
    Returns [{uid, class, face_a, term_a, wire_a, face_b, term_b, wire_b, err, err_a, err_b, errs}]."""
    rec_dir = os.path.join(HERE, "recipes")
    if rec_dir not in sys.path:
        sys.path.insert(0, rec_dir)
    import importlib
    T = importlib.import_module("build_opfstunnelterm_v2")
    ops, out = {}, []
    for o in objs:
        k = FS_KINDS.get(o["class"])
        if not k or (uids is not None and int(o["uid"]) not in uids):
            continue
        if k not in ops:
            lab = json.load(open(T.LABELS_OUT if k == "OUT" else T.LABELS_IN, encoding="utf-8"))
            ops[k] = (g.op(T.OP_OUT if k == "OUT" else T.OP_IN), lab)
        vi, lab = ops[k]
        r = T.read_tunnel(vi, lab, path, int(o["uid"]))
        out.append({"uid": int(o["uid"]), "class": o["class"],
                    "face_a": lab["face_a"], "term_a": r["term_a_uid"], "wire_a": r["wire_a"],
                    "face_b": lab["face_b"], "term_b": r["term_b_uid"], "wire_b": r["wire_b"],
                    "uid_back": r["uid_back"], "err": r["err"], "err_a": r["err_a"],
                    "err_b": r["err_b"], "errs": r["errs"]})
    return out


def read_one(path, conpane, calls, main_vi):
    """One VI -> the wiki record. Two op runs (GObject census, Terminal traverse) + one subvis per diagram."""
    t0 = time.time()
    objs, seen = [], set()
    for o in g.report_all(path, "GObject"):
        u = int(o["uid"])
        if u in seen:                       # the traverse repeats a few uids (measured, probe2)
            continue
        seen.add(u)
        objs.append({"uid": u, "class": o["class"], "pos": tuple(o["pos"]), "owner": o["owner"]})
    leaf = dict((o["uid"], o["class"]) for o in objs)
    t_obj = time.time() - t0

    # STEP 4b: the flat-sequence tunnels' faces, READ (tools/bench/diag_fstunnel_pairs.log, 14/0).
    t0 = time.time()
    fs_pairs = read_fs_tunnels(path, objs) if any(o["class"] in FS_KINDS for o in objs) else []
    t_fs = time.time() - t0

    rows, t_term = A.read_terms(path, op=OPREADER[0])
    for r in rows:
        r["term_class"] = leaf.get(r["term_uid"], "")
    wire_uids = [o["uid"] for o in objs if o["class"] == "Wire"]
    wires = A.join_wires(rows, wire_uids)
    sev = [w["wire_uid"] for w in A.severed(wires)]

    t0 = time.time()
    subvi_calls, diag_n = [], 0
    try:
        diag_n = g.count(path, "Diagram")
        for d in range(diag_n):
            for x in subvi_rows(path, d):
                subvi_calls.append({"node_uid": int(x["uid"]), "subvi_name": x["name"],
                                    "diagram": d, "path": x.get("path", "")})
    except Exception as e:                                                         # noqa: BLE001
        subvi_calls = []
        fact("{0}: subvis failed: {1}".format(key_of(path), str(e)[:140]))
    t_sub = time.time() - t0

    cls_count = collections.Counter(o["class"] for o in objs)
    graph = vigraph.build(rows, wires, objs)
    pane = conpane.get(path)
    if pane:
        source = "call-node-terminals"
    else:
        pane = [{"index": i, "label": t["label"], "direction": t["direction"], "type": ""}
                for i, t in enumerate(vigraph.fp_terminals(rows))]
        source = "fp-control-terminals"
    lin = set(t["label"] for t in pane if t["direction"] == "input")
    lout = set(t["label"] for t in pane if t["direction"] == "output")
    paths_io = vigraph.io_paths(graph, rows, lin, lout)
    fp_labels = set(t["label"] for t in vigraph.fp_terminals(rows))

    return {
        "file": path,
        "md5": md5(path),
        "bytes": os.path.getsize(path),
        "read": {"gobject_s": round(t_obj, 2), "terminals_s": round(t_term, 2),
                 "subvis_s": round(t_sub, 2), "fs_tunnels_s": round(t_fs, 2),
                 "when": time.strftime("%Y-%m-%d %H:%M:%S")},
        # STEP 4b. One row per FlatSequence{Outer,Inner}Tunnel uid, both faces READ by uid:
        # FSOT face_a OuterTerminal / face_b InnerTerminal; FSIT face_a LeftTerm / face_b RightTerm.
        # MEASURED on S1: every physical inner tunnel is TWO FSIT uids reporting the same two faces
        # (Left/Right swapped). vigraph.build4 turns each row into ONE exact `fs` edge, sink face ->
        # source face, and falls back to the heuristic when this key is absent.
        "fs_tunnel_pairs": fs_pairs,
        "connector_pane": pane,
        "connector_pane_source": source,
        "connector_pane_unassigned_slots": conpane.get(path + "\x00blank", 0),
        "connector_pane_unmatched_on_diagram": sorted(
            set(t["label"] for t in pane) - fp_labels),
        "terminals": rows,
        "wires": wires,
        "severed_wires": sev,
        "graph_summary": {
            "objects": len(objs),
            "nodes": len(graph["nodes"]),
            "wires": len(wire_uids),
            "terminals": len(rows),
            "diagrams": diag_n,
            "loops": sum(cls_count[c] for c in LOOPS),
            "cases": sum(cls_count[c] for c in CASES),
            "sequences": sum(cls_count[c] for c in SEQS),
            "locals": cls_count["Local"],
            "globals": cls_count["Global"],
            "subvi_nodes": sum(cls_count[c] for c in SUBVI_CLASSES),
            "subvi_calls": subvi_calls,
            "class_census": dict(sorted(cls_count.items(), key=lambda kv: -kv[1])),
            "edge_method": graph["method"],
        },
        "io_paths": paths_io,
        "summary": "",
        "call_sites_in_main": {"main_vi": main_vi,
                               "sites": calls.get(os.path.basename(path), [])},
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--force", action="store_true", help="re-read every VI, ignoring the md5 gate")
    ap.add_argument("--only", default=None, help="fnmatch on the file name")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--op", default="v0", choices=("v0", "v1"),
                    help="v1 = OpAllTerms_v1.vi, which adds the 7th column frame_diagram (the frame a "
                         "terminal sits on). The delivered wiki was built on v0; switching costs a full "
                         "re-read of every VI (~14 min for 96), so it is a deliberate flag, not a default.")
    ap.add_argument("--refresh", action="append", default=[],
                    help="fnmatch on the wiki KEY: force a re-read of just these entries, ignoring the md5 "
                         "gate for them only (the others stay md5-gated). Repeatable.")
    a = ap.parse_args(argv)
    OPREADER[0] = A.OP_ALLTERMS_V1 if a.op == "v1" else A.OP_ALLTERMS
    fact("terminal reader: {0}".format(os.path.basename(OPREADER[0])))

    os.makedirs(WIKI, exist_ok=True)
    index = {}
    if os.path.exists(INDEX):
        index = json.load(open(INDEX, encoding="utf-8")).get("vis", {})
    calls, main_vi = call_sites_index()

    allp = targets()
    if a.only:
        allp = [p for p in allp if fnmatch.fnmatch(os.path.basename(p), a.only)]
    if a.limit:
        allp = allp[:a.limit]
    fact("targets: {0} ({1} background copies + {2} extra)".format(
        len(allp), sum(1 for p in allp if p.startswith(BG)), sum(1 for p in allp if not p.startswith(BG))))

    todo, skipped = [], []
    for p in allp:
        k = key_of(p)
        forced = a.force or any(fnmatch.fnmatch(k, pat) for pat in a.refresh)
        if not forced and index.get(k, {}).get("md5") == md5(p) and \
                os.path.exists(os.path.join(WIKI, k + ".json")):
            skipped.append(k)
        else:
            todo.append(p)
    for k in skipped:
        print("  SKIP  {0}  skipped, unchanged".format(k), flush=True)
    fact("to read: {0}; skipped, unchanged: {1}".format(len(todo), len(skipped)))
    if not todo:
        return 0

    conpane, cp_failed = conpane_pass([p for p in todo if p.startswith(BG)])
    fact("connector panes read for {0} VI(s); {1} fell back".format(
        sum(1 for k in conpane if "\x00" not in k), len(cp_failed)))
    for p, why in sorted(cp_failed.items()):
        fact("conpane FALLBACK {0}: {1}".format(key_of(p), why))

    times, errors = {}, {}
    for n, p in enumerate(todo, 1):
        k = key_of(p)
        t0 = time.time()
        try:
            rec = read_one(p, conpane, calls, main_vi)
        except Exception as e:                                                     # noqa: BLE001
            errors[k] = str(e)[:200]
            print("  FACT  [{0}/{1}] {2}  UNREAD: {3}".format(n, len(todo), k, errors[k]), flush=True)
            continue
        with open(os.path.join(WIKI, k + ".json"), "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=1)
        gs = rec["graph_summary"]
        index[k] = {"file": p, "md5": rec["md5"], "bytes": rec["bytes"],
                    "json": "docs/wiki/subvi/{0}.json".format(k),
                    "connector_pane": len(rec["connector_pane"]),
                    "connector_pane_source": rec["connector_pane_source"],
                    "terminals": gs["terminals"], "wires": gs["wires"], "nodes": gs["nodes"],
                    "subvi_calls": len(gs["subvi_calls"]), "io_paths": len(rec["io_paths"]),
                    "summary": index.get(k, {}).get("summary", ""), "read": rec["read"]}
        with open(INDEX, "w", encoding="utf-8") as f:
            json.dump({"built": time.strftime("%Y-%m-%d %H:%M:%S"), "n": len(index), "vis": index},
                      f, indent=1)
        times[k] = round(time.time() - t0, 2)
        if rec["fs_tunnel_pairs"]:
            try:
                import bench_prep
                hnd = bench_prep.labview_handles()
            except Exception as e:                                                 # noqa: BLE001
                hnd = "unread: {0}".format(str(e)[:60])
            fsr = rec["fs_tunnel_pairs"]
            fact("{0}: fs_tunnel_pairs {1} rows ({2} FSOT / {3} FSIT), clean both faces {4}, {5}s; "
                 "LabVIEW handles now {6}".format(
                     k, len(fsr), sum(1 for x in fsr if x["class"].endswith("OuterTunnel")),
                     sum(1 for x in fsr if x["class"].endswith("InnerTunnel")),
                     sum(1 for x in fsr if x["term_a"] and x["term_b"] and not x["err_a"] and not x["err_b"]),
                     rec["read"]["fs_tunnels_s"], hnd))
        print("  FACT  [{0}/{1}] {2}  {3}s  terms {4} wires {5} pane {6}/{7} subvis {8} io {9}".format(
            n, len(todo), k, times[k], gs["terminals"], gs["wires"], len(rec["connector_pane"]),
            rec["connector_pane_source"][:4], len(gs["subvi_calls"]), len(rec["io_paths"])), flush=True)

    if times:
        v = sorted(times.values())
        fact("per-VI seconds: min {0} median {1} max {2} total {3:.1f}".format(
            v[0], v[len(v) // 2], v[-1], sum(v)))
    fact("UNREAD: {0}".format(json.dumps(errors)[:800] if errors else "none"))
    print("=== WIKI: {0} written / {1} skipped / {2} unread; index {3}".format(
        len(times), len(skipped), len(errors), INDEX), flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
