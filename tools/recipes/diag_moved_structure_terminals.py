"""PART 1 of cycle-15 route-B session 2 — settle the SINK RULE's addressing, and find the REAL drift mechanism.

REVISED 2026-09-17 AFTER `archive/peer/2026-09-17-priorart-priorart-routeb-census.md` (claude/opus, ANSWERED,
6 findings, 0 novel). The first draft of this file re-measured something already on disk and, worse, built its
whole design on a premise the project's own census contradicts. Every change below is that review's, with its
citation; nothing here is my own second opinion.

WHAT THE REVIEW CORRECTED, and it changes the conclusion, not just the cost
---------------------------------------------------------------------------
* **A3 `contradicted`.** My premise — *"`#5540` terminal index 1 is `Bead is good? array out`, an OUTPUT tunnel"*
  — is FALSE on the pristine original. `tools/bench/main_vi_nodeterms.json:11292-11315`: t1 is an **unnamed SINK**
  (`is_source` false, wire 5979) and t2 is the named source (wire 5637). The index moved **during the failing run
  itself**: `tools/bench/build_opconnectfromwire_v0_run2.log:96` reads
  `T2 candidate sink #5540 t1 …: wire sequence [5979, 5637, 0]`, produced by `bare()`
  (`tools/recipes/build_opconnectfromwire_v0.py:530-545`), which **deletes a Wire object and runs
  `remove_bad_wires_scripted` between reads** — on a copy that `:522` made with a plain `shutil.copyfile` and
  **never restructured**. So the measured drift trigger is *wire deletion + Remove Bad Wires*, NOT a move, and a
  pre/post-MOVE comparison cannot reproduce it. Arm C exists because of this finding.
* **B4 `already-measured` + A4 `unread-evidence`.** Pass A already exists for ALL FIVE structures, from this same
  original at this same md5 (`main_vi_nodeterms.json`, diagram key `"43"`: `#5540` :11275-11364 n6 · `#2222`
  :11996 n13 · `#1359` :12293 n16 · `#10407` :12805 · `#29874` :14383; identity verified per node by UID,
  `docs/main-vi-panel-map.md:403`; current for today's md5, `archive/peer/2026-09-16-stop-condterm-failed-
  prediction.md:33`). It is now READ, not re-measured, and confirmed by five `node_terms_uid` identity reads —
  the shape `docs/cycle13-plan.md:126-130` already settled on for exactly one of these structures.
* **A1 `settled-already` + B3 `helper-exists`.** `docs/NAMES.md:900-905` already decides, this cycle, that
  **"a `(node, terminal index)` pair does not name the SIDE"**, and `OpTunnelRead_v0` (24/24) already read
  `#5540`'s tunnel sides — `docs/stage2-assembly-step-e.md:137-147` CENSUS B. Joined to `main_vi_nodeterms.json`
  BY WIRE UID the whole index → side → tunnel map falls out **with no LabVIEW run**, which is what arm D prints.
  No side reader is built here and none is needed.
* **A4(b).** `tools/bench/probe_move_into_v0.log:221,:231` already measured a `move_in` of a `CaseStructure` into
  a fresh sibling While loop: `Wire 1902 -> 1895, LoopTunnel 132 -> 130`, `ExecState 0`. So predicting an
  IDENTICAL map after a move was predicting against a measurement. P3 is re-stated below to gate only what the
  SINK RULE needs and to REPORT the rest.
* **B1 `already-built`.** `tools/bench/sweep_nodeterms_main.py:44-77` is this census machinery, and `:65-66`
  **trims trailing empty terminals** while my `census()` did not — so a raw `len()` compares two different
  things. The trim is adopted here so arm B's counts are comparable to the stored file.
* Prose note, accepted: the denominator is **16** from-tunnel rows, not 18
  (`archive/peer/2026-09-17-priorart-priorart-cfw-recipe.md:454`; STATUS OPEN 36(a)).

WHAT THIS RUN DOES — four arms, only two of which touch LabVIEW
---------------------------------------------------------------
 A (OFFLINE)  read the stored census for the five moved structures and apply the SINK RULE to every from-tunnel
              row. Confirmed by 5 identity reads on a fresh copy.
 D (OFFLINE)  join A to `stage2-assembly-step-e.md`'s CENSUS B by WIRE UID -> index -> side -> tunnel for #5540.
 B (LabVIEW)  the arm with no precedent: 3 fresh While loops, the five structures moved in, re-census.
 C (LabVIEW)  THE ARM THE EVIDENCE POINTS AT: on an UNMOVED copy, delete `#5540` t1's wire + Remove Bad Wires,
              exactly `bare()`'s sequence, and re-read the map.

PREDICTION CONTRACT
-------------------
 P0   original md5 `2a78e17c449cacdaf5da389818526859` BEFORE; handles recorded.
 PA1  the stored census holds all five uids on diagram "43" with per-index name / is_source / wire.
 PA2  **THE SINK RULE HOLDS ON THE PRISTINE ORIGINAL**: every from-tunnel row whose sink is one of the five
      moved structures reads `is_source` FALSE there. (If this passes, OPEN 37's "the sink was an OUTPUT tunnel"
      is refuted at the source, not by argument.)
 PA3  five `node_terms_uid` reads on a fresh copy echo the right node UID and reproduce the stored map.
 PD   #5540's seven indices each join to a tunnel and a side, from CENSUS B, with no LabVIEW call.
 PB1  copy B: WhileLoop 3->6, Diagram 170->173; all five structures reach their loop bodies.
 PB2  **gated**: no index that was a SINK (`is_source` FALSE) before the move reads SOURCE after it — the SINK
      RULE's precondition is what matters, not byte-identity of the map. Name/count changes are REPORTED:
      `probe_move_into_v0.log:231` already measured `LoopTunnel 132 -> 130` for two moves, so tunnels DO die.
 PC   **the discriminating arm**: on an unmoved copy, deleting `#5540` t1's wire and running Remove Bad Wires
      makes t1 report a DIFFERENT wire (the run-2 log's `[5979, 5637, 0]`). Predicted SHIFT, not stability.
 P5   both scratches deleted in this run; original md5 unchanged AFTER.

Rig disassembled; no hardware, no GUI; nothing saved.
"""
import hashlib
import json
import os
import re
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                   # noqa: E402
from bench_prep import labview_handles                                # noqa: E402
import build_d1_v0 as D1                                              # noqa: E402

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
BENCH = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(BENCH, "d1_moved_structure_terminals.json")
STORED = os.path.join(BENCH, "main_vi_nodeterms.json")
TUNNEL_SOURCES = os.path.join(BENCH, "d1_tunnel_sources.json")
CENSUS_B_DOC = os.path.join(ROOT, "docs", "stage2-assembly-step-e.md")
STAMP = time.strftime("%H%M%S")
COPY_A = os.path.join(g.CLAUDEDEV, f"SCRATCH_term_pre_{STAMP}.vi")
COPY_B = os.path.join(g.CLAUDEDEV, f"SCRATCH_term_post_{STAMP}.vi")

FRAME_BODY_UID = 639
SIBLING_DIAG_UID = 686
STRUCTURES = {5540: "1.2", 2222: "1.2", 1359: "1.2", 29874: "1.2", 10407: "1.5"}
BEFORE = dict(Diagram=170, WhileLoop=3)
CASE_5540 = 5540

g._run.__defaults__ = (6.0, 120.0)
passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def diag_index(target, uid):
    return [o["uid"] for o in g.report_all(target, "Diagram")].index(uid)


def trim(rows):
    """`tools/bench/sweep_nodeterms_main.py:65-66`, adopted verbatim (prior-art B1): trailing terminals with no
    name AND no wire are past the end of `Terminals[]`, and counting them makes two censuses incomparable."""
    out = list(rows)
    while out and not out[-1][1][0] and not out[-1][1][2]:
        out.pop()
    return out


def as_map(rows):
    """[node_terms row] -> [(i, (name, is_source, wire))], trailing empties trimmed."""
    return trim(sorted(((r["i"], (r["name"], r["is_source"], r["wire"])) for r in rows)))


def show(tag, uid, m):
    fact(f"{tag} #{uid}: {len(m)} terminals (trailing empties trimmed)")
    for i, (nm, src, w) in m:
        print(f"        t{i:<3} {'OUT (source)' if src else 'IN  (sink)  '}  wire {w:<6} name {nm!r}", flush=True)


# ============================================================================== A — OFFLINE
def arm_a():
    print("\n=== A (OFFLINE): the stored census for the five moved structures (prior-art B4)", flush=True)
    with open(STORED, encoding="utf-8") as f:
        stored = json.load(f)
    d43 = stored["diagrams"].get("43")
    if not gate("PA1a the stored census has diagram key '43'", bool(d43)):
        return None, None
    by_uid = {nd["uid"]: nd for nd in d43["nodes"]}
    out, nidx = {}, {}
    for uid in STRUCTURES:
        nd = by_uid.get(uid)
        if not gate(f"PA1 #{uid} is in the stored census of diagram 43", bool(nd)):
            continue
        nidx[uid] = nd["n"]
        m = trim(sorted((t["i"], (t["name"], t["is_source"], t["wire"])) for t in nd["terms"]))
        out[uid] = m
        show("A", uid, m)
    return out, nidx


def sink_rule(before, tag="A"):
    """PA2 — the SINK RULE applied to every from-tunnel row. `is_source` FALSE = the terminal is a SINK, which is
    exactly what `docs/d1-route-b-plan.md`'s frontmatter requires of a from-tunnel row's destination."""
    print(f"\n=== PA2 [{tag}]: the SINK RULE, row by row over d1_tunnel_sources.json", flush=True)
    with open(TUNNEL_SOURCES, encoding="utf-8") as f:
        rows = json.load(f)["rows"]
    verdicts, bad, n_moved = [], [], 0
    for r in rows:
        u, t, nm = r["sink_uid"], r["sink_term"], r.get("sink_name")
        if u not in STRUCTURES:
            kind = "fresh-drop" if u in (5058, 376) else "other"
            verdicts.append(dict(sink_uid=u, sink_term=t, kind=kind, ok=None, name=nm))
            print(f"      #{u} t{t} {nm!r}: {kind} — the sink is a FRESHLY DROPPED subVI's NAMED input; this "
                  f"census cannot speak for it", flush=True)
            continue
        n_moved += 1
        m = dict(before.get(u) or [])
        row = m.get(t)
        ok = bool(row) and row[1] is False
        verdicts.append(dict(sink_uid=u, sink_term=t, kind="moved-structure", ok=ok,
                             name=(row or (None,))[0], is_source=(row or (None, None))[1],
                             wire=(row or (None, None, None))[2], tunnel=r.get("tunnel_uid"),
                             outer_wire=r.get("outer_wire")))
        if not ok:
            bad.append((u, t, row))
        print(f"      #{u} t{t}: {(row or ('<missing>', None, None))[0]!r} is_source="
              f"{(row or (None, None))[1]} wire={(row or (None, None, None))[2]}  "
              f"(tunnel #{r.get('tunnel_uid')}, outer w{r.get('outer_wire')})  "
              f"-> {'SINK-RULE OK' if ok else '**VIOLATES THE SINK RULE**'}", flush=True)
    gate(f"PA2 [{tag}] every from-tunnel row on a MOVED structure has an Is Source? FALSE sink "
         f"({n_moved} rows)", not bad, f"{len(bad)} violate it: {bad}")
    return verdicts


# ============================================================================== D — OFFLINE
CENSUS_B_TUNNELS = {
    # docs/stage2-assembly-step-e.md:137-147, "CENSUS B MEASURED (2026-09-15)", OpTunnelRead_v0 24/24.
    # wire uid on diagram 43  ->  (side, tunnel class + uid, what it carries)
    5975: ("OUT", "SelectorTunnel 6016", "x,y,z array"),
    5637: ("OUT", "SelectorTunnel 5680", "Bead is good? array in"),
    1681: ("IN", "input tunnel 5825", "frame 5582 pass-through, driven by LeftShiftRegister 1142"),
    6041: ("IN", "input tunnel 5702", "frame 5582 pass-through, driven by LeftShiftRegister 5805"),
    5746: ("IN", "input tunnel 5725", "frame 5592 pass-through, driven by LoopTunnel 5752"),
    5979: ("IN", "input tunnel 5967", "frame 5592 pass-through, driven by LoopTunnel 5569"),
}


def arm_d(before):
    """PD — the index -> SIDE -> tunnel map for #5540, joined BY WIRE UID, with no LabVIEW call. This is the
    prior-art review's A4(a) reconstruction, and it answers the question `docs/NAMES.md:900-905` says a
    `(node, terminal index)` pair cannot: which tunnel an index belongs to and which side of it."""
    print("\n=== D (OFFLINE): #5540 index -> side -> tunnel, joined by WIRE UID (prior-art A4a / B3)", flush=True)
    m = dict(before.get(CASE_5540) or [])
    if not gate("PD #5540 is in the stored census", bool(m)):
        return None
    joined, unjoined = {}, []
    for i, (nm, src, w) in sorted(m.items()):
        hit = CENSUS_B_TUNNELS.get(w)
        joined[i] = dict(name=nm, is_source=src, wire=w, side=(hit or (None,))[0],
                         tunnel=(hit or (None, None))[1], carries=(hit or (None, None, None))[2])
        if not hit:
            unjoined.append((i, w))
        print(f"      t{i}  w{w:<6} {'OUT' if src else 'IN '}  "
              f"{(hit or ('-', '-', '-'))[0]:<4} {(hit or ('-', '-', '-'))[1]:<22} "
              f"{(hit or ('-', '-', ''))[2]}", flush=True)
    gate("PD every #5540 index except the selector joins to a CENSUS-B tunnel", len(unjoined) <= 1,
         f"unjoined {unjoined} (t0 w5709 is the CASE SELECTOR, not a tunnel - "
         f"stage2-assembly-step-e.md CENSUS B lists 4 input + 2 output tunnels for 7 terminals)")
    return joined


# ============================================================================== confirm A on a live copy
def arm_a_confirm(nidx):
    """PA3 — `docs/cycle13-plan.md:126-130`'s shape: the stored file is the census, and ONE identity-gated
    `node_terms_uid` read per structure confirms it (~0.8 s each) instead of a fresh sweep."""
    print("\n=== PA3: five identity reads on a fresh copy confirm the stored census", flush=True)
    if os.path.exists(COPY_A):
        os.remove(COPY_A)
    shutil.copy2(ORIGINAL, COPY_A)
    m = md5(COPY_A)
    if not gate("PA3a copy A on DISK is byte-identical to the original before LabVIEW sees it", m == ORIG_MD5, m):
        return None
    g.open_panel(COPY_A)
    time.sleep(1.0)
    d = diag_index(COPY_A, FRAME_BODY_UID)
    gate("PA3b Diagram #639 is Traverse index 43", d == 43, f"index {d}")
    live = {}
    for uid, n in nidx.items():
        node_uid, rows = g.node_terms_uid(COPY_A, d, n)
        if not gate(f"PA3 #{uid} Nodes[{n}] echoes its own uid", node_uid == uid, f"echoed {node_uid}"):
            continue
        live[uid] = as_map(rows)
    return live


# ============================================================================== B — the move arm
def arm_b(nidx):
    print("\n=== B: the five structures AFTER a move into fresh While loops (no precedent - prior-art B1)",
          flush=True)
    if os.path.exists(COPY_B):
        os.remove(COPY_B)
    shutil.copy2(ORIGINAL, COPY_B)
    m = md5(COPY_B)
    if not gate("PB0 copy B on DISK is byte-identical to the original before LabVIEW sees it", m == ORIG_MD5, m):
        return None
    g.open_panel(COPY_B)
    time.sleep(1.0)
    sib_i = diag_index(COPY_B, SIBLING_DIAG_UID)
    loops = {}
    for row, loc in (("1.2", (2600, 2600)), ("1.5", (2600, 3400)), ("1.7", (2600, 4200))):
        dg0, wl0 = g.uids(COPY_B, "Diagram"), g.uids(COPY_B, "WhileLoop")
        g.loop_in("while", COPY_B, sib_i, loc)
        nd, nw = g.new_since(COPY_B, "Diagram", dg0), g.new_since(COPY_B, "WhileLoop", wl0)
        if not gate(f"PB1 loop {row} created", len(nd) == 1 and len(nw) == 1,
                    f"+{len(nd)} diagrams, +{len(nw)} while loops"):
            return None
        loops[row] = dict(loop=nw[0]["uid"], body=nd[0]["uid"])
        fact(f"{row}: WhileLoop #{nw[0]['uid']}, body Diagram #{nd[0]['uid']}")
    gate("PB1 WhileLoop 3 -> 6 and Diagram 170 -> 173",
         g.count(COPY_B, "WhileLoop") == BEFORE["WhileLoop"] + 3
         and g.count(COPY_B, "Diagram") == BEFORE["Diagram"] + 3,
         f"WhileLoop {g.count(COPY_B, 'WhileLoop')}, Diagram {g.count(COPY_B, 'Diagram')}")
    w0, lt0 = g.count(COPY_B, "Wire"), g.count(COPY_B, "LoopTunnel")
    y = 60
    for uid, row in STRUCTURES.items():
        body_uid, loop_uid = loops[row]["body"], loops[row]["loop"]
        D1.move_in(COPY_B, uid, diag_index(COPY_B, body_uid), (60, y))
        y += 140
        try:
            oc, ou = D1.owner_of(COPY_B, uid)
            oc2, ou2 = D1.owner_of(COPY_B, ou) if ou else (None, None)
            ok = ou == body_uid and ou2 == loop_uid
        except Exception as e:
            oc = ou = oc2 = ou2 = f"<{str(e)[:50]}>"
            ok = False
        gate(f"PB1 #{uid} -> {row}", ok, f"owner {oc}#{ou} (want Diagram#{body_uid}); "
                                         f"owner(owner) {oc2}#{ou2} (want WhileLoop#{loop_uid})")
    fact(f"PB1 the five moves cost: Wire {w0} -> {g.count(COPY_B, 'Wire')}, "
         f"LoopTunnel {lt0} -> {g.count(COPY_B, 'LoopTunnel')} "
         f"(probe_move_into_v0.log:231 measured 1902->1895 / 132->130 for TWO moves - tunnels DO die)")
    after = {}
    for uid, row in STRUCTURES.items():
        bi = diag_index(COPY_B, loops[row]["body"])
        labels = [r["uid"] for r in g.node_labels(COPY_B, bi)]
        if uid not in labels:
            gate(f"PB2 #{uid} is a node on its new body diagram", False, f"diagram holds {labels}")
            continue
        n = labels.index(uid)
        node_uid, rows = g.node_terms_uid(COPY_B, bi, n)
        if not gate(f"PB2 #{uid} Nodes[{n}] on the new body echoes its own uid", node_uid == uid,
                    f"echoed {node_uid}"):
            continue
        after[uid] = as_map(rows)
        show("B", uid, after[uid])
    return after


def compare(before, after):
    """PB2 — gate ONLY the SINK RULE's precondition. `probe_move_into_v0.log:231` already measured that a move
    destroys wires and loop tunnels, so gating byte-identity would gate against a measurement (prior-art A4b)."""
    print("\n=== PB2: did any SINK become a SOURCE across the move?", flush=True)
    flips = []
    for uid in STRUCTURES:
        b, a = dict(before.get(uid) or []), dict((after or {}).get(uid) or [])
        if not b or not a:
            gate(f"PB2 #{uid} censused on both sides", False, f"before {len(b)}, after {len(a)}")
            continue
        fact(f"PB2 #{uid}: {len(b)} terminals before, {len(a)} after")
        for i, (bn, bs, bw) in sorted(b.items()):
            an, asrc, aw = a.get(i, ("<missing>", None, None))
            if bs is False and asrc is True:
                flips.append((uid, i, bn, an))
            if (an, asrc) != (bn, bs):
                print(f"      CHANGED #{uid} t{i}: ({bn!r}, src {bs}, w{bw}) -> ({an!r}, src {asrc}, w{aw})",
                      flush=True)
    gate("PB2 no terminal that was a SINK before the move reads SOURCE after it", not flips, f"{flips}")


# ============================================================================== C — the drift arm
def arm_c(nidx):
    """PC — reproduce `bare()` (`tools/recipes/build_opconnectfromwire_v0.py:530-545`) on an UNMOVED copy. The
    review's A3 says this, not the move, is the measured trigger of the index shift that made OPEN 37."""
    print("\n=== C: bare #5540 t1 on an UNMOVED copy — delete its wire + Remove Bad Wires (prior-art A3)",
          flush=True)
    d = diag_index(COPY_A, FRAME_BODY_UID)
    n = nidx.get(CASE_5540)
    if n is None:
        gate("PC #5540's node index is known", False)
        return None
    seq, maps = [], []
    for step in range(4):
        rows = g.node_terms(COPY_A, d, n)
        m = as_map(rows)
        maps.append(m)
        w = next((r["wire"] for r in rows if r["i"] == 1), 0)
        seq.append(w)
        print(f"      step {step}: t1 wire {w}; map "
              f"{[(i, nm, ('OUT' if s else 'IN'), ww) for i, (nm, s, ww) in m]}", flush=True)
        if not w:
            break
        order = [o["uid"] for o in g.report_all(COPY_A, "Wire")]
        if w not in order:
            fact(f"PC t1's wire {w} is not in Traverse('Wire') - stopping")
            break
        g.delete_object(COPY_A, "Wire", order.index(w), verify=False)
        g.remove_bad_wires_scripted(COPY_A)
    fact(f"PC #5540 t1 wire sequence across delete+RBW: {seq} "
         f"(build_opconnectfromwire_v0_run2.log:96 recorded [5979, 5637, 0])")
    shifted = len(seq) > 1 and seq[1] not in (0, seq[0])
    gate("PC deleting t1's wire + Remove Bad Wires SHIFTS what index 1 denotes "
         "(the measured cause of STATUS OPEN 37, not the move)", shifted,
         f"sequence {seq}; a second value that is neither 0 nor the first IS the shift")
    if len(maps) > 1:
        moved_names = [(i, maps[0][i][1][0] if i < len(maps[0]) else None,
                        maps[1][i][1][0] if i < len(maps[1]) else None)
                       for i in range(max(len(maps[0]), len(maps[1])))]
        fact(f"PC index -> name across the first delete: "
             f"{[(i, a, b) for i, a, b in moved_names if a != b]} (empty = names kept their indices)")
    return seq


# ============================================================================== main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    t0 = time.time()
    if "--restart" in sys.argv:
        import subprocess
        try:
            rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                                capture_output=True, text=True, timeout=600)
            fact(f"lv_restart rc={rc.returncode}: {(rc.stdout or '').strip().splitlines()[-1:]}")
        except Exception as e:
            fact(f"lv_restart FAILED ({str(e)[:100]})")
    g._lv = None
    m0 = md5(ORIGINAL)
    if not gate("P0 original md5 BEFORE", m0 == ORIG_MD5, m0):
        return 2
    gate("P0b the cited evidence files exist",
         all(os.path.exists(p) for p in (STORED, TUNNEL_SOURCES, CENSUS_B_DOC)),
         f"{[p for p in (STORED, TUNNEL_SOURCES, CENSUS_B_DOC) if not os.path.exists(p)]}")
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")
    before, nidx = arm_a()
    verdicts = sink_rule(before or {}, "stored/pristine") if before else None
    joined = arm_d(before) if before else None
    live = after = seq = None
    try:
        if nidx:
            live = arm_a_confirm(nidx)
            if live:
                same = [u for u in (before or {}) if dict(live.get(u) or []) == dict(before[u])]
                gate("PA3c the five live reads reproduce the stored census exactly",
                     len(same) == len(before), f"{len(same)} of {len(before)} match; "
                     f"differ: {[u for u in (before or {}) if u not in same]}")
            seq = arm_c(nidx)
            after = arm_b(nidx)
            if after:
                compare(before or {}, after)
    finally:
        for p in (COPY_A, COPY_B):
            try:
                g.close_panel(p)
            except Exception:
                pass
            try:
                if os.path.exists(p):
                    os.remove(p)
                gate(f"P5 scratch deleted in the same run: {os.path.basename(p)}", not os.path.exists(p))
            except Exception as e:
                gate(f"P5 scratch deleted in the same run: {os.path.basename(p)}", False, str(e)[:80])
        g._lv = None
        m1 = md5(ORIGINAL)
        gate("P5b original md5 AFTER", m1 == ORIG_MD5, m1)
        fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(dict(stored={str(k): v for k, v in (before or {}).items()},
                           live={str(k): v for k, v in (live or {}).items()},
                           after_move={str(k): v for k, v in (after or {}).items()},
                           sink_rule=verdicts, side_map_5540=joined, bare_sequence=seq,
                           md5_after=m1), f, indent=1, default=str)
    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== diag_moved_structure_terminals: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
