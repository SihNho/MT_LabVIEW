r"""p1_c70_f3a - cycle 70 P1 / retrospective-cycle69 F3a. MATERIAL, PURE PYTHON: no LabVIEW, no VI, no hardware.
P0 (tools/bench/p0_c69_census.log :68-129) walked ForLoop owner chains with OpOwnerChain_v1; every walk stopped at
error 1055 on a FlatSequenceFrame diagram (or at the 8-step cap). This re-derives the diagram tree from the bed's
terminal table's frame_diagram column (tools/bench/graph_s3_loop15_20260924.json, md5 1a11d92a), no LabVIEW call:
  regular tunnel / shift register: OuterTerminal frame A, InnerTerminal frame B  => parent(B) = A (directed);
  FlatSequenceInnerTunnel: reports 3 frame_diagrams = two SIBLING frames (union) + the sequence's OWNER diagram (the
  one whose objs owner is not FlatSequenceFrame; else the most frequent) => parent(frames) = owner (directed);
  FlatSequenceOuterTunnel: one frame is the sequence's owner diagram, the other a frame (undirected edge);
  BFS from TopLevelDiagram #536 over the group graph gives each group's parent group.
EXISTING TOOLS CHECKED: build_d1_v0.owner_of needs LabVIEW (the 1055 source); vigraph has no diagram tree.
PREDICTIONS: T0 17 ForLoop chains in the P0 log; T1 every directed tunnel/SR edge agrees with the BFS tree;
T2 every chain's last diagram reaches #536; Q1 no ForLoop chain passes through a plan structure's inner diagram
(split_rows_l2l7.json p1.structure_inner_frames); Q2 RECORDED: left SRs (uid, TOP=pos[1]) per body of
#637/#10170/#23041/#1359/#29874 and of every loop with SRs nested below them (bodies from the P0 'SR body' lines).
    py tools/bgrun.py --material --max-min 10 --log tools/bench/p1_c70_f3a.log -- py -u tools/bench/p1_c70_f3a.py
"""
import collections, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))
FAILS, TOP_D = [], 536
BODIES = {637: 639, 10170: 23166, 23041: 23405, 1359: 7911, 29874: 29894}


def gate(label, ok, detail=""):
    print("{0}  {1} | {2}".format("PASS" if ok else "FAIL", label, detail))
    FAILS.extend([] if ok else [label])


def main():
    g = J("tools/bench/graph_s3_loop15_20260924.json")
    objs = {o["uid"]: o for o in g["objs"]}
    by_owner = collections.defaultdict(list)
    [by_owner[t["owner_uid"]].append(t) for t in g["terminals"]]
    uf = {}

    def find(x):
        while uf.setdefault(x, x) != x:
            x = uf[x]
        return x
    directed, undirected, owner_faces = set(), set(), collections.Counter()
    isframe = lambda d: objs.get(d, {}).get("owner") == "FlatSequenceFrame"
    fsit = [sorted({t["frame_diagram"] for t in ts}) for ts in by_owner.values()
            if ts[0]["owner_class"] == "FlatSequenceInnerTunnel"]
    cnt = collections.Counter(d for fr in fsit for d in fr)
    for fr in fsit:              # run 1 lesson: an FSIT reports THREE frames - two sibling frames + the sequence's owner
        own = [d for d in fr if not isframe(d)] if len(fr) == 3 else []
        own = own if len(own) == 1 else ([max(fr, key=lambda d: cnt[d])] if len(fr) == 3 else [])
        sib = [d for d in fr if d not in own]
        [uf.__setitem__(find(b), find(sib[0])) for b in sib[1:]]
        directed.update((own[0], b) for b in sib) if own else None
        owner_faces[own[0] if own else None] += 1
    for u, ts in by_owner.items():
        c, fr = ts[0]["owner_class"], sorted({t["frame_diagram"] for t in ts})
        if c == "FlatSequenceInnerTunnel":
            continue
        elif c == "FlatSequenceOuterTunnel" and len(fr) == 2:
            undirected.add(tuple(fr))
        elif "Tunnel" in c or "ShiftRegister" in c:
            outs = {t["frame_diagram"] for t in ts if t["term_class"] == "OuterTerminal"}
            ins = {t["frame_diagram"] for t in ts if t["term_class"] == "InnerTerminal"}
            directed.update((a, b) for a in outs for b in ins if a != b)
    adj = collections.defaultdict(set)
    for a, b in directed | undirected:
        adj[find(a)].add(find(b)), adj[find(b)].add(find(a))
    par, q = {find(TOP_D): None}, [find(TOP_D)]
    while q:
        x = q.pop(0)
        for y in sorted(adj[x] - set(par)):
            par[y] = x
            q.append(y)
    members = collections.defaultdict(set)
    [members[find(d)].add(d) for d in list(uf)]
    print("FACT FSIT owner faces (owner diagram: FSIT count) {0}".format(owner_faces.most_common(12)))
    bad = [(a, b) for a, b in directed if par.get(find(b)) != find(a)]
    gate("T1 every directed tunnel/SR edge agrees with the BFS tree", not bad, "{0} directed + {1} FS-outer edges, "
         "{2} groups placed; contradictions {3}".format(len(directed), len(undirected), len(par), bad[:10]))

    def up(d):                   # [(group members...)] from d's group to the top; last entry 'TOP' or 'NO-PARENT'
        out, x = [], find(d)
        while x is not None:
            out.append(sorted(members[x]))
            if x not in par:
                return out + ["NO-PARENT"]
            x = par[x]
        return out + ["TOP"]
    log = open(os.path.join(ROOT, "tools/bench/p0_c69_census.log"), encoding="utf-8").read()
    chains = {int(m.group(1)): [int(x) for x in m.group(2).split(",") if x.strip()]
              for m in re.finditer(r"SR loop ForLoop #(\d+): rights \[[^\]]*\], chain \[([^\]]*)\]", log)}
    body_of = {int(m.group(2)): int(m.group(1)) for m in re.finditer(r"SR body #(\d+) of \('\w+', (\d+)\)", log)}
    body_of.update(BODIES)
    fsf = [lp for lp, ch in chains.items() if objs.get(ch[-1], {}).get("owner") == "FlatSequenceFrame"]
    gate("T0 17 ForLoop chains in the P0 log", len(chains) == 17, "{0} chains; last element a FlatSequenceFrame "
         "diagram in {1}: {2}".format(len(chains), len(fsf), sorted(fsf)))
    plan_in = {int(u): set(v) for u, v in J("tools/bench/split_rows_l2l7.json")["p1"]["structure_inner_frames"].items()}
    plan_d = {d: u for u, s in plan_in.items() for d in s}
    full, ok = {}, []
    for lp, ch in sorted(chains.items()):
        diags = [d for d in ch if objs.get(d, {}).get("class") == "Diagram"]
        ext = up(diags[-1])
        full[lp] = set(diags) | {d for grp in ext[:-1] for d in grp}
        ok.append(ext[-1] == "TOP")
        print("CHAIN ForLoop #{0}: P0 {1} -> derived groups {2}".format(lp, ch, ext))
    gate("T2 every ForLoop chain reaches TopLevelDiagram #536", all(ok), "reached {0}/{1}".format(sum(ok), len(ok)))
    inside = {lp: sorted((d, plan_d[d]) for d in ds if d in plan_d) for lp, ds in full.items()}
    gate("Q1 no ForLoop is nested inside an L2/L7 plan structure (inner diagrams)", not any(inside.values()),
         {k: v for k, v in inside.items() if v})
    lefts = collections.defaultdict(list)
    for u, ts in by_owner.items():
        if ts[0]["owner_class"] == "LeftShiftRegister":
            b = [t["frame_diagram"] for t in ts if t["term_class"] == "InnerTerminal"]
            lefts[b[0] if b else None].append((u, objs[u]["pos"][1]))
    for lp, body in BODIES.items():
        nested = sorted(f for f, ds in full.items() if body in ds)
        for L in [lp] + nested:
            bd = body_of.get(L)
            tops = collections.Counter(t for _, t in lefts.get(bd, []))
            print("SR loop #{0}{1} body #{2}: lefts(uid,TOP) {3}; TOP collisions {4}".format(
                L, "" if L == lp else " (nested in #{0})".format(lp), bd, sorted(lefts.get(bd, [])),
                [t for t, n in tops.items() if n > 1]))
        print("FACT loop #{0} body #{1}: ForLoops nested below it {2}".format(lp, body, nested))
    print("SUMMARY {0} fail: {1}".format(len(FAILS), FAILS))
    return 1 if FAILS else 0


if __name__ == "__main__":
    raise SystemExit(main())
