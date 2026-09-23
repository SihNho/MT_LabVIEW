"""q_m4_iter_indicator - READ-ONLY, no LabVIEW (cycle 68 material, brief Q1).
Question: does the ORIGINAL (D1_s1_copy graph = byte copy of the original) or the M3a-4 bed's prior graph carry a
front-panel terminal or Local whose value is the frame loop's iteration count, i.e. is fed from Terminal #644
(owner Diagram #639 = WhileLoop #637 body, wire 3268) DIRECTLY or through transparent (scheduling) nodes only?
Existing tools found and reused: tools/vigraph.py (build4 graph, transparent, effective_sources, reach4),
tools/jev_candidates.py (load S1_KEY / BED_KEY graphs). Nothing new built.
PREDICTION: 0 panel terminals / Locals on the transparent-only closure (docs/frame-loop-wire-graph.md:161 lists
w3268's sinks as subVI/function params, one tunnel pair). Full (through-computation) reach may hit indicators.
Method: (a) transparent-only BFS downstream of every #644 source key, recording the path; any ControlTerminal /
Local / Global terminal reached is a candidate. (b) cross-check with effective_sources(): every FP/Local terminal
whose effective_sources contains a #644 key. (c) full reach4 (through computation) -> FP terminals, for context."""
import collections, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import jev_candidates as JC   # noqa: E402
import vigraph as V           # noqa: E402

CAND_CLS = ("ControlTerminal", "Local", "Global")


def closure(G, starts):
    prev = {s: None for s in starts}
    stack = list(starts)
    while stack:
        cur = stack.pop()
        for kind, nxt, _i in G["out"].get(cur, ()):
            if nxt in prev:
                continue
            prev[nxt] = (cur, kind)
            node = V.key_parts(nxt)[0]
            # stop at computation terminals; walk through scheduling relays (and FP relays per V.transparent)
            if V.transparent(G, nxt) or G["cls"].get(node) in CAND_CLS:
                stack.append(nxt)
    return prev


def trail(prev, k):
    out = []
    while k is not None:
        p = prev[k]
        out.append(V.show(k) + (f" <-{p[1]}-" if p else ""))
        k = p[0] if p else None
    return " ".join(reversed(out))


for key in (JC.S1_KEY, JC.BED_KEY):
    print("=" * 20, key)
    G = JC.load(key)
    starts = [k for k in V.terminals(G, term_uid=644) if (JC.term_row(G, k) or {}).get("is_source")]
    if not starts:
        starts = [k for k in V.wire_terminals(G, 3268) if V.key_parts(k)[0] == 639]
    print("start keys:", [V.show(k) for k in starts], "cls(639)=", G["cls"].get(639), "cls(637)=", G["cls"].get(637))
    prev = closure(G, starts)
    reached = [k for k in prev if k not in starts]
    print("(a) transparent-only closure size:", len(reached))
    for k in sorted(reached):
        node = V.key_parts(k)[0]
        c = G["cls"].get(node)
        tag = "CANDIDATE" if c in CAND_CLS else ("relay" if V.transparent(G, k) else "stop")
        print(f"    [{tag}] {V.show(k)} cls={c} label={G['labels'].get(node)!r}")
        if c in CAND_CLS:
            print("        path:", trail(prev, k))
    # (b) effective_sources cross-check over every FP/Local/Global terminal
    s = set(starts)
    memo = {}
    hitb = []
    for k, r in G["rows"].items():
        node = r["node"]
        if G["cls"].get(node) in CAND_CLS and s & V.effective_sources(G, k, memo):
            hitb.append(k)
    print("(b) FP/Local/Global terminals with #644 in effective_sources:", [V.show(k) for k in sorted(hitb)])
    # (c) full reach through computation -> FP terminals (context only: these carry f(i), not i)
    full = V.reach4(G, starts)
    fp = collections.defaultdict(list)
    for k in full:
        node = V.key_parts(k)[0]
        if G["cls"].get(node) in CAND_CLS:
            fp[G["cls"].get(node)].append(f"#{node} {G['labels'].get(node)!r}")
    for c in fp:
        print(f"(c) full-reach {c}: n={len(set(fp[c]))}", sorted(set(fp[c]))[:25])
    # locals in #637's body diagram and their labels
    locs = [(n, G["labels"].get(n)) for n, c in G["cls"].items() if c == "Local"]
    print("    all Locals on graph:", locs)
    # (d) counter-like indicators named in docs/main-vi-panel-map.md:383/:332/:379/:413 - what REALLY feeds them
    for tag, w in (("current image number w3747", 3747), ("SubCycle w16421", 16421), ("Total cycle # w31687", 31687)):
        for k in V.wire_terminals(G, w):
            r = JC.term_row(G, k) or {}
            if not r.get("is_source"):
                print(f"(d) {tag}: sink {V.show(k)} eff_src={[V.show(x) for x in V.effective_sources(G, k, memo)][:6]}")
    for k in V.terminals(G, node=4277):
        print(f"(d) Local#4277 'File # Saved' {V.show(k)} eff_src={[V.show(x) for x in V.effective_sources(G, k, memo)][:6]}")
