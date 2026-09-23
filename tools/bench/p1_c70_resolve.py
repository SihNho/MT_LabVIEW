r"""p1_c70_resolve - cycle 70 step P1 of docs/d1-loop12-17-split-plan.md. MATERIAL, PURE PYTHON: no LabVIEW, no VI
opened, no motor/ASI/camera. Reads files only; writes new fields into tools/bench/split_rows_l2l7.json.
EXISTING TOOLS CHECKED: vigraph.wire_terminals needs a build4 graph; a wire_uid filter over the terminal table is
enough. stagekit.Stage is LabVIEW-bound, so plain PASS/FAIL lines. P0 resolved rows by uid+terminal name only.
METHOD: a structure row (uid, index, wire) is the OUTER terminal of one tunnel: bed terminals on the row's wire, tunnel
owner, OuterTerminal, on #639, same direction. Where a wire touches two plan structures' tunnels (w28847, w31166) the
inner-frame match with the structure's single-candidate tunnels picks. The SAME two-pass rule over S1's own terminal
table (D1_s1_copy.json) must name the same tunnel uid (run 1 applied pass 1 only on S1 -> 5 two-candidate "fails").
PREDICTIONS: A0 rows == build_d1_v0 cut; A1 33 rows on #639; A2 one tunnel each (0 ambiguous/missing); A3 == S1 tunnel;
A4 one inner-frame set per structure, pairwise disjoint; A5 92/92 resolved (59 name + 33 tunnel).
    MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/p1_c70_resolve.log -- py -u tools/bench/p1_c70_resolve.py
"""
import collections, json, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
ROWS_P = os.path.join(ROOT, "tools", "bench", "split_rows_l2l7.json")
TUN = {"Tunnel", "SelectorTunnel", "LoopTunnel", "FlatSequenceOuterTunnel"}
FAILS = []


def gate(label, ok, detail=""):
    print("{0}  {1} | {2}".format("PASS" if ok else "FAIL", label, detail))
    FAILS.extend([] if ok else [label])


def index(terms):
    bw, bo = collections.defaultdict(list), collections.defaultdict(list)
    [(bw[t["wire_uid"]].append(t), bo[t["owner_uid"]].append(t)) for t in terms]
    return bw, bo


def cands(by_wire, r, frame):
    return [t for t in by_wire.get(r["wire"], []) if t["owner_class"] in TUN and t["term_class"] == "OuterTerminal"
            and t["is_source"] == r["is_source"] and (frame is None or t["frame_diagram"] == frame)]


def inner(by_owner, tun):
    return sorted({t["frame_diagram"] for t in by_owner[tun] if t["term_class"] == "InnerTerminal"})


def main():
    D = J("tools/bench/split_rows_l2l7.json")
    bed_w, bed_o = index(J("tools/bench/graph_s3_loop15_20260924.json")["terminals"])
    s1_w, s1_o = index(J("docs/wiki/subvi/D1_s1_copy.json")["terminals"])
    cut = {(c[0], c[1]): c for c in J("tools/bench/build_d1_v0.json")["cut"]}
    miss = [r for r in D["rows"] if r["resolved_by"] == "missing"]
    frames = {r["uid"]: D["where"][str(r["uid"])]["owner"][1] for r in miss}
    gate("A1 structure rows = 33, all owned by Diagram #639", len(miss) == 33 and set(frames.values()) == {639},
         "{0} rows, owners {1}".format(len(miss), sorted(set(frames.values()))))
    gate("A0 every row matches build_d1_v0 cut (uid,i,name,is_source,wire)",
         all(cut.get((r["uid"], r["i"])) == [r["uid"], r["i"], r["name"], r["is_source"], r["wire"]] for r in miss))
    def picker(w, o, fr):    # pass 1: single-candidate rows fix each structure's inner-frame set; pass 2 filters by it
        sets = collections.defaultdict(set)
        for r in miss:
            c = cands(w, r, fr(r))
            if len(c) == 1:
                sets[r["uid"]].update(inner(o, c[0]["owner_uid"]))
        return lambda r: (lambda c: (c, [t for t in c if set(inner(o, t["owner_uid"])) & sets[r["uid"]]]
                                     if len(c) > 1 else c))(cands(w, r, fr(r)))
    bed_pick, s1_pick = picker(bed_w, bed_o, lambda r: frames[r["uid"]]), picker(s1_w, s1_o, lambda r: None)
    out, amb, lost = {}, [], []
    for r in miss:
        c, c2 = bed_pick(r)
        s1u = sorted({t["owner_uid"] for t in s1_pick(r)[1]})
        if len(c2) != 1:
            (amb if c2 else lost).append((r["uid"], r["i"], r["wire"], [(t["owner_uid"], t["owner_class"],
                                           inner(bed_o, t["owner_uid"])) for t in c]))
            continue
        t = c2[0]
        out[(r["uid"], r["i"])] = {"tunnel_uid": t["owner_uid"], "tunnel_class": t["owner_class"], "face": "outer",
                                   "outer_term_uid": t["term_uid"], "outer_frame_diagram": t["frame_diagram"],
                                   "inner_frame_diagrams": inner(bed_o, t["owner_uid"]),
                                   "wire_candidates_on_bed": len(c), "s1_tunnel_uids": s1u,
                                   "s1_agrees": s1u == [t["owner_uid"]]}
        print("ROW  #{0} t{1} {2!r} w{3} src={4} -> tunnel #{tunnel_uid} {tunnel_class} outer term #{outer_term_uid} "
              "on #{outer_frame_diagram}; inner {inner_frame_diagrams}; wire cands {wire_candidates_on_bed}; S1 "
              "{s1_tunnel_uids}".format(r["uid"], r["i"], r["name"], r["wire"], r["is_source"], **out[(r["uid"], r["i"])]))
    for tag, a in [("AMBIGUOUS", a) for a in amb] + [("UNRESOLVED", a) for a in lost]:
        print("{0} #{1} t{2} w{3} candidates {4}".format(tag, *a))
    gate("A2 33/33 structure rows -> exactly one bed tunnel", len(out) == 33,
         "resolved {0}, ambiguous {1}, unresolved {2}".format(len(out), len(amb), len(lost)))
    bad = [k for k, v in out.items() if not v["s1_agrees"]]
    gate("A3 bed tunnel uid == S1 tunnel uid (wire identity) for every resolved row", not bad, "disagree {0}".format(bad))
    per = collections.defaultdict(list)
    [per[u].append((i, v["tunnel_uid"], tuple(v["inner_frame_diagrams"]))) for (u, i), v in out.items()]
    frame_sets = {u: {f for _, _, x in lst for f in x} for u, lst in per.items()}
    for u, lst in sorted(per.items()):
        fs = frame_sets[u]
        print("FACT structure #{0}: {1} rows -> tunnels {2}; inner frame diagrams {3}".format(
            u, len(lst), sorted({t for _, t, _ in lst}), sorted(fs)))
    split = [u for u, lst in per.items() if len({x for _, _, x in lst if x}) > 1 and
             not set.intersection(*[set(x) for _, _, x in lst if x])]
    gate("A4a each structure's tunnels share its inner frames", not split, "split {0}".format(split))
    over = [(a, b) for a in frame_sets for b in frame_sets if a < b and frame_sets[a] & frame_sets[b]]
    gate("A4b the five structures' inner frame sets are pairwise disjoint", not over, "overlap {0}".format(over))
    for r in D["rows"]:
        k = (r["uid"], r["i"])
        if k in out:
            r["p1_tunnel"], r["resolved_by_p1"] = out[k], "tunnel"
        elif r["resolved_by"] != "missing":
            r["resolved_by_p1"] = r["resolved_by"]
            r["p1_wire_on_bed"] = bool(bed_w.get(r["wire"]))
        else:
            r["resolved_by_p1"] = "ambiguous" if any(a[:2] == k for a in amb) else "unresolved"
    D["p1"] = {"cycle": 70, "script": "tools/bench/p1_c70_resolve.py", "tally": dict(collections.Counter(
        r["resolved_by_p1"] for r in D["rows"])), "ambiguous": amb, "unresolved": lost,
        "structure_inner_frames": {str(u): sorted(v) for u, v in frame_sets.items()}}
    n_ok = sum(1 for r in D["rows"] if r["resolved_by_p1"] in ("name", "tunnel"))
    wireless = [(r["uid"], r["i"], r["wire"]) for r in D["rows"] if r.get("p1_wire_on_bed") is False]
    print("FACT name-resolved rows whose S1 wire uid is absent on the bed: {0} {1}".format(len(wireless), wireless))
    gate("A5 92/92 rows resolved, 0 ambiguous", n_ok == 92 and not amb, "tally {0}".format(D["p1"]["tally"]))
    with open(ROWS_P, "w", encoding="utf-8") as f:
        json.dump(D, f, indent=1)
    print("WROTE {0} (new fields p1_tunnel / resolved_by_p1 / p1_wire_on_bed / top-level p1)".format(ROWS_P))
    print("SUMMARY {0} fail: {1}".format(len(FAILS), FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
