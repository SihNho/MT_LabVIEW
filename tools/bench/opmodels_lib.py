r"""opmodels_lib - PURE PYTHON (no LabVIEW) helpers for card chat-S1: the terminal-level graph of one read and the diff of
two reads. A "read" = (terms, objs): terms = allterms.read_terms rows {term_uid, term_name, is_source, wire_uid, owner_uid,
owner_class}; objs = gscript.report_all(vi, 'GObject') rows {uid, class, pos, owner(class name)}.

EDGE = (src_term_uid, sink_term_uid) joined by wire_uid inside ONE read (wire uids are the join key only within a read).
The diff is keyed by TERMINAL UID (review archive/peer/2026-09-24-c68-m4a-p6b-rename.md §4: names change on move/wire).
"""
import collections


def edges(terms):
    byw = collections.defaultdict(lambda: ([], []))
    for r in terms:
        if r["wire_uid"]:
            byw[r["wire_uid"]][0 if r["is_source"] else 1].append(r["term_uid"])
    out = {}
    for w, (src, snk) in byw.items():
        for a in src:
            for b in snk:
                out[(a, b)] = w
    half = sorted(w for w, (src, snk) in byw.items() if not src or not snk)
    return out, dict(byw), half


def snapshot_stats(terms, objs):
    e, _byw, half = edges(terms)
    return {"terms": len(terms), "objs": len(objs), "edges": len(e), "half_wires": len(half),
            "wire_objs": sum(1 for o in objs if o["class"] == "Wire"),
            "max_uid": max([int(o["uid"]) for o in objs] + [int(r["term_uid"]) for r in terms] + [0])}


def diff(before, after):
    """before/after = (terms, objs). Returns a JSON-able dict."""
    tb, ob = before
    ta, oa = after
    TB = dict((r["term_uid"], r) for r in tb)
    TA = dict((r["term_uid"], r) for r in ta)
    OB = dict((int(o["uid"]), o) for o in ob)
    OA = dict((int(o["uid"]), o) for o in oa)
    EB, WB, HB = edges(tb)
    EA, WA, HA = edges(ta)
    changed = []
    for u in sorted(set(TB) & set(TA)):
        a, b = TB[u], TA[u]
        ch = dict((k, [a[k], b[k]]) for k in ("term_name", "is_source", "wire_uid", "owner_uid", "owner_class")
                  if a.get(k) != b.get(k))
        if ch:
            changed.append({"term_uid": u, "owner_uid": b["owner_uid"], "owner_class": b["owner_class"],
                            "name": b["term_name"], "changed": ch})
    maxb = max([int(u) for u in OB] + [int(u) for u in TB] + [0])
    new_uids = sorted(set(OA) - set(OB))
    rm = sorted(set(EB) - set(EA))
    ad = sorted(set(EA) - set(EB))
    return {
        "stats_before": snapshot_stats(tb, ob), "stats_after": snapshot_stats(ta, oa),
        "terms_added": [TA[u] for u in sorted(set(TA) - set(TB))],
        "terms_removed": [TB[u] for u in sorted(set(TB) - set(TA))],
        "terms_changed": changed,
        "objs_added": [OA[u] for u in new_uids],
        "objs_removed": [OB[u] for u in sorted(set(OB) - set(OA))],
        "edges_removed": [{"src": a, "sink": b, "wire": EB[(a, b)],
                           "src_owner": (TB.get(a) or {}).get("owner_uid"),
                           "sink_owner": (TB.get(b) or {}).get("owner_uid")} for a, b in rm],
        "edges_added": [{"src": a, "sink": b, "wire": EA[(a, b)],
                         "src_owner": (TA.get(a) or {}).get("owner_uid"),
                         "sink_owner": (TA.get(b) or {}).get("owner_uid")} for a, b in ad],
        "edges_rewired": [{"src": a, "sink": b, "wire": [EB[(a, b)], EA[(a, b)]]}
                          for a, b in sorted(set(EB) & set(EA)) if EB[(a, b)] != EA[(a, b)]],
        "half_wires_before": HB, "half_wires_after": HA,
        "uid_alloc": {"max_uid_before": maxb, "new_obj_uids": new_uids,
                      "all_new_above_max": all(u > maxb for u in new_uids),
                      "new_term_uids": sorted(set(TA) - set(TB))},
    }


TUNNELS = ("LoopTunnel",)          # the direction-loss rule is MEASURED on LoopTunnel only (L7-1a #1929, #5020)


def apply_move(terms, node_uid):
    """MOVE MODEL v0 (fitted on L7-1a, S3 -> D1_l7_1a, move of SubVI #376): returns predicted terms after
    `move_in(node_uid)` into ANOTHER diagram. Pure; names are not modelled (they are not stable - key by term uid).
      R1 every terminal of the moved node leaves its wire (wire_uid -> 0); the Wire OBJECT survives (Wire count
         unchanged) as a half-wire if the node was its only source or only sink; other sinks of a branched net keep
         their edge from the same source.
      R2 a LoopTunnel whose INNER sink was fed ONLY by the moved node loses its direction: its source terminal(s)
         read is_source False, so every edge out of that tunnel disappears and its outer wire becomes a half-wire."""
    out = [dict(r) for r in terms]
    moved_wires = set(r["wire_uid"] for r in out if r["owner_uid"] == node_uid and r["wire_uid"])
    for r in out:
        if r["owner_uid"] == node_uid:
            r["wire_uid"] = 0
    byw = collections.defaultdict(list)
    for r in out:
        if r["wire_uid"]:
            byw[r["wire_uid"]].append(r)
    return _direction_loss(out, moved_wires)


def _direction_loss(out, touched_wires):
    """R2 with CASCADE (measured: delete_object #27605 flipped LoopTunnels #28311, #28343 AND #28370, which #28343's outer
    wire fed): a LoopTunnel whose sink terminal sits on a wire that now has NO source loses its direction; its source
    terminals flip to is_source False, which can leave the next wire sourceless, and so on."""
    dead_tunnels, todo = set(), set(touched_wires)
    while todo:
        byw = collections.defaultdict(list)
        for r in out:
            if r["wire_uid"]:
                byw[r["wire_uid"]].append(r)
        nxt = set()
        for w in todo:
            rs = byw.get(w, [])
            if rs and not any(x["is_source"] for x in rs):
                for x in rs:
                    if x["owner_class"] in TUNNELS and not x["is_source"] and x["owner_uid"] not in dead_tunnels:
                        dead_tunnels.add(x["owner_uid"])
                        for r in out:
                            if r["owner_uid"] == x["owner_uid"] and r["is_source"]:
                                r["is_source"] = False
                                if r["wire_uid"]:
                                    nxt.add(r["wire_uid"])
        todo = nxt
    return out, sorted(dead_tunnels)


def apply_delete_object(terms, node_uid):
    """DELETE_OBJECT MODEL v0 (delete_object #7201, #27605; plus the setup of remove_bad_wires_1, delete #1628): the node and
    its terminal rows disappear; a wire it SOURCED survives as a sink-side half-wire; a branched wire it sank keeps its other
    sinks; R2 direction loss with cascade as in apply_move. A wire whose ONLY sink was the node: AMBIGUOUS (w8385 from a
    constant was deleted outright; w2160 and w2187 survived as half-wires) - returned in `ambiguous`, not decided."""
    gone_wires = set(r["wire_uid"] for r in terms if r["owner_uid"] == node_uid and r["wire_uid"])
    out = [dict(r) for r in terms if r["owner_uid"] != node_uid]
    byw = collections.defaultdict(list)
    for r in out:
        if r["wire_uid"]:
            byw[r["wire_uid"]].append(r)
    ambiguous = sorted(w for w in gone_wires if byw.get(w) and not any(not x["is_source"] for x in byw[w]))
    out, dead = _direction_loss(out, gone_wires)
    return out, dead, ambiguous


def summary(d):
    return {k: len(d[k]) for k in ("terms_added", "terms_removed", "terms_changed", "objs_added", "objs_removed",
                                   "edges_removed", "edges_added", "edges_rewired")}
