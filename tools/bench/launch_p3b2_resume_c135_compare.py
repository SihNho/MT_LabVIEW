r"""launch_p3b2_resume_c135_compare - card 135-2 pass 2 (PD294(b)): the STRICT graph compare of the P3b-2 runner with BOTH graphs
re-annotated by the CURRENT border annotation before comparing. Pure, offline, no LabVIEW, no file write.
WHY: launch_p3b2_c135.compare (launch_p3b2_c135.py:57-81) compared the STORED `fs_measured.borders`; the reference read
graph_ring_p3b2a_fs_20261002_102553.json was written before card 134-6 added `status: UNMEASURED` to stagesim.fs_measured_state
(stagesim.py:386), so 7 nested-FS borders differed by that key alone (result_135-1.json, launch_p3b2_c135.log:43).
WHAT EXISTED (reused, unchanged): launch_p3b2_c135.graph_key / compare (every field: (uid, class) of every obj, every terminal row
in full, wire -> term uids, fs_frames, borders) and stagesim.fs_measured_state (the annotation the reader writes,
diag_c134_1_graph.py:68-69). Nothing is dropped: the borders of each graph are RECOMPUTED by the current fs_measured_state from that
graph's own terminal rows + fs_frames (both compared anyway), and the recomputation is checked against the stored borders - a
change other than an ADDED annotation key (ANNOT_KEYS) on either side is itself a difference (`reannotation`), never absorbed."""
import copy, json, os, sys                                                         # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(B))
sys.path.insert(0, B)
import stagesim as SS                                                              # noqa: E402
import launch_p3b2_c135 as C135                                                    # noqa: E402
ANNOT_KEYS = ("status",)          # annotation keys the reader may ADD to a stored border; any other change is a difference


def reannotate(g):
    """(copy of g with fs_measured.borders = current annotation, changes {border uid: {added, removed, changed, presence}})."""
    g2 = copy.deepcopy(g)
    fm = g2.get("fs_measured")
    if not isinstance(fm, dict):
        return g2, {}
    cur = json.loads(json.dumps(dict((str(k), v) for k, v in SS.fs_measured_state(g)["borders"].items()), default=str))
    old = json.loads(json.dumps(fm.get("borders") or {}, default=str))
    ch = {}
    for u in sorted(set(cur) | set(old)):
        a, b = old.get(u), cur.get(u)
        if a is None or b is None:
            ch[u] = {"presence": "only_stored" if b is None else "only_current"}
            continue
        c = {"added": sorted(set(b) - set(a)), "removed": sorted(set(a) - set(b)),
             "changed": sorted(k for k in set(a) & set(b) if a[k] != b[k])}
        if any(c.values()):
            ch[u] = c
    fm["borders"] = cur
    return g2, ch


def annotation_only(ch):
    return all(not c.get("presence") and not c.get("removed") and not c.get("changed") and set(c.get("added") or ()) <= set(ANNOT_KEYS)
               for c in ch.values())


def compare(new, ref):
    """(equal, diff, changes) - C135.compare on the re-annotated pair; a non-annotation re-annotation change on either side is
    listed under diff['reannotation'] and makes the result DIFFERENT (strict, PD288(e), rule 1a)."""
    n2, cn = reannotate(new)
    r2, cr = reannotate(ref)
    eq, diff = C135.compare(n2, r2)
    bad = dict((side, dict(list(ch.items())[:5])) for side, ch in (("new", cn), ("ref", cr)) if not annotation_only(ch))
    if bad:
        diff["reannotation"] = bad
    return not diff, diff, {"new": dict(list(cn.items())[:10]), "ref": dict(list(cr.items())[:10]), "n_new": len(cn), "n_ref": len(cr)}
