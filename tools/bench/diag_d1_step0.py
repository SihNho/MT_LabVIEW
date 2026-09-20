r"""diag_d1_step0.py - D1 STEP 0: the BEFORE census and the three classifications the build diffs against.

Cycle 15, D1 build session. READ-ONLY on the original (rule 1d: headless reads, never opened for writing).
This script REPORTS. It takes no decision: which node moves where is written in docs/d1-build-plan.md REV 3
sections 4/5/8 and section 11a; step 0 measures whether the WIRING agrees with that assignment, and reports a
disagreement as a fact (CLAUDE.md s3: no result-dependent action).

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "before creating any new op/tool/recipe"):
  * `tools/bench/main_vi_nodeterms.json` (2026-09-14, 626 nodes on all 170 diagrams: name / is_source / wire uid
    per terminal). MAIN's md5 is unchanged since, so it is CURRENT and is the offline half of this run. Nothing
    it answers is re-measured. Same reuse as `tools/bench/diag_stop_save_seam.py:5-8`.
  * `tools/bench/main_vi_node_labels.json` (OpNodeLabels_v0) - node identity (implicit Property -> its panel
    object, subVI -> file name, primitive -> type).
  * `OpWireSource_v5` (wire uid -> the terminal that DRIVES it) and `OpOwnerChain_v1` (uid -> owner) are BUILT;
    their drivers `read_terminal` / `read_owner` are imported VERBATIM from their build recipes. NO new op.
  * `g.tunnels()` (OpTunnels_v0, 132 tunnels censused), `g.shift_reg_left()` (OpShiftRegs_v1, 14 registers of the
    frame loop), `g.panel_wiring()` (OpPanelWiring_v0, 114 panel objects) all exist and are used as readers.
  * `docs/main-vi-stop-and-save.md` s4 already holds #5058's 16 terminals; gate G1 re-derives them from the
    offline census as an IDENTITY check on the census, and nothing else about the seam is re-measured.
  * `grep "^def " tools/gscript.py` has no whole-VI "wire -> both ends" helper and no slice/reachability helper;
    the reachability here is 30 lines over the census dict, not a new op.

WHY A LabVIEW RUN IS NEEDED AT ALL: the offline census resolves a wire only when BOTH ends are node terminals.
64 wires on the D1 move set have exactly ONE end there - the loop's tunnels and shift registers, diagram
constants and front-panel control terminals are not in `Nodes[]`. Those are what the tunnel / shift-register /
panel censuses and `OpWireSource_v5` resolve.

WHAT IT PRODUCES (the three things the brief asks for)
  (a) the BACKWARD SLICE of the kernel - the 7 nodes of `docs/frame-loop-wire-graph.md:43` - each with every
      terminal's resolved source/sink, classified by the MEASURED wiring per d1-build-plan s11a.2:
        moves-with-kernel  := the node carries PER-FRAME data, i.e. within diagram 43 it is forward-reachable
                              from a per-frame source (#6810 `Image Out` / `current image number`, or a #5058
                              output wire 505/121/5859) AND it forward-reaches a #5058 input.
        stays-with-tunnel  := none of its inputs is per-frame - every one arrives on a LoopTunnel / constant /
                              panel terminal - so its value crosses the new loop border on a tunnel.
        stays-with-acquisition := it IS the frame source (#6810, row 1.8 REUSE decision).
      A node that satisfies neither is reported as UNCLASSIFIED; it is not guessed.
  (b) `#10407`'s per-frame inputs derived from the kernel's outputs -> the 1.5 notifier's PAYLOAD WIDTH
      (d1-build-plan s11a.3: one value => a DBL notifier, more => a DBL array; never a cluster).
  (c) the `node_terms` BEFORE census of every node in the move set, written to
      `tools/bench/d1_step0_census.json`, which is what the build's after-move census is diffed against
      (s11a.2: the terminals that go wired->bare are the authoritative re-wire list).

PREDICTION CONTRACT (machine-checked; a miss is a failed prediction and owes a peer review)
  G0a/G0b  MAIN md5 == 2a78e17c449cacdaf5da389818526859 before AND after.
  G1   the offline census gives #5058 exactly 16 terminals and its 13 wired ones carry exactly the wire uids
       recorded in docs/main-vi-stop-and-save.md s4 (5637 3040 373 5859 505 5975 121 42 3512 3646 7429 3912 4027).
  G2   every one of the 7 backward-slice nodes of frame-loop-wire-graph.md:43 is on diagram 43.
  G3   the tunnel census returns 132 LoopTunnels (docs/toolkit-capabilities.md:24) and resolves the 6
       loop-invariant kernel inputs (wires 373 42 3512 3646 3912 4027) to tunnels #2580 #2396 #4432 #3656 #3920
       #4031 (docs/main-vi-stop-and-save.md s4).
  G4   the shift-register census returns 14 registers for WhileLoop index 1 (#637) and among them the pair that
       carries wire 7429 into the kernel and wire 5859 out of it - expected #2972 (left) and #5796 (right).
  G5   panel_wiring returns 114 rows (toolkit-capabilities.md:511).
  G6   EVERY boundary wire of the move set is resolved to exactly one of {LoopTunnel, ShiftRegister, panel
       terminal, OpWireSource_v5 answer}; the count of still-unresolved wires is reported and gates at 0 for the
       wires of the 7 backward-slice nodes + #5058 + #10407 + #48 (the step-0 subject set), not for the rest.
  G7   `#10407` has at least one SINK terminal fed - transitively, within diagram 43 - by a #5058 output wire.
       The WIDTH is the measured number; it is reported, never predicted.
  G8   each of the 7 backward-slice nodes gets exactly one classification (no UNCLASSIFIED).

  MATERIAL=1 py tools/bgrun.py --max-min 28 --log tools/bench/diag_d1_step0.log -- py -u tools/bench/diag_d1_step0.py
"""
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opwiresource_v5 import MAP_OUT, read_terminal  # noqa: E402
from build_opwiresource_v5 import OP as OP_WIRE  # noqa: E402
from build_opownerchain_v1 import MAIN, read_owner  # noqa: E402
from build_opownerchain_v1 import OP as OP_OWNER  # noqa: E402

MD5_EXPECTED = "2a78e17c449cacdaf5da389818526859"
CENSUS = os.path.join(HERE, "main_vi_nodeterms.json")
LABELS_JSON = os.path.join(HERE, "main_vi_node_labels.json")
OUT = os.path.join(HERE, "d1_step0_census.json")

D_FRAME = "43"            # the frame loop's body diagram (Traverse index), owner WhileLoop #637
D_SIB = "19"              # the FlatSequenceFrame diagram that holds #637 itself and #6384
KERNEL = 5058
KERNEL_OUT_WIRES = (505, 121, 5859)
FRAME_SRC = 6810
WHILE_INDEX_637 = 1       # tools/bench/loopendref_637.json: #637 is WhileLoop Traverse index 1
N_SHIFT_REGS = 14         # docs/toolkit-capabilities.md:27

# docs/frame-loop-wire-graph.md:43 - the kernel's BACKWARD slice, verbatim
BACKWARD = [5540, 6810, 9647, 10247, 10445, 10950, 17289]
# docs/frame-loop-wire-graph.md:45 - the kernel's FORWARD slice, verbatim
FORWARD = [376, 1359, 2222, 2626, 6104, 8885, 9833, 10407, 10757, 10969, 11261, 11639, 12589, 29874]
# d1-build-plan s4/s5/s6: everything the build touches on diagram 43, plus the stop path and the writer
MOVE_SET = sorted(set(BACKWARD + FORWARD + [
    KERNEL, 48,                      # the kernel seam and the ASI focus subVI (row 1.5)
    22700, 22082, 17883, 10019, 22284, 17837,   # TIFF writer + the two stop paths (s3)
    10686, 3191, 57, 5119, 3052, 23175, 11608, 2136, 1114, 10068, 29240,
    20474, 30117, 4580, 10382, 11529, 22703, 3057,
]))
# diagram 19 (outside the frame loop): the writer call and its feeders
SIB_SET = [637, 6384, 2048, 781, 27605]
# the subject set of step 0 - G6 gates only these
SUBJECT = sorted(set(BACKWARD + [KERNEL, 10407, 48]))

_gates = []
_facts = []


class _Skip(Exception):
    """`--offline`: jump straight past the LabVIEW block to the classification."""


def gate(label, ok, detail=""):
    _gates.append((label, bool(ok)))
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}{('   ' + detail) if detail else ''}", flush=True)
    return bool(ok)


def fact(line):
    _facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def handles():
    r = subprocess.run(["powershell", "-NoProfile", "-Command",
                        "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1).HandleCount"],
                       capture_output=True, text=True)
    try:
        return int(r.stdout.strip() or 0)
    except ValueError:
        return 0


def fresh():
    """STATUS OPEN 23: the previous batch left LabVIEW at 51,530 handles (baseline ~31,500) and STATUS says
    restart before the next batch. Standing restart permission (CLAUDE.md s3). Verbatim shape of
    build_opconstvalue_v1.fresh(), without its GUI/bench dependencies."""
    before = handles()
    print(f"   fresh(): handles before restart {before}", flush=True)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; "
                    "if ($p) { Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=90)
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    r"Start-Process 'C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe'"],
                   capture_output=True, text=True, timeout=90)
    g.reset()
    t0 = time.time()
    while time.time() - t0 < 180:
        try:
            g._lv = None
            g.lv().Version
            break
        except Exception:
            time.sleep(5)
    else:
        raise RuntimeError("LabVIEW did not answer COM after restart")
    after = handles()
    print(f"   fresh(): handles after restart {after}", flush=True)
    return before, after


# ------------------------------------------------------------------ offline census
def load_offline():
    dg = json.load(open(CENSUS, encoding="utf-8"))["diagrams"]
    try:
        lab_raw = json.load(open(LABELS_JSON, encoding="utf-8"))["diagrams"]
    except Exception:
        lab_raw = {}
    labels = {}
    for _d, rows in lab_raw.items():
        for r in rows:
            labels[r["uid"]] = r.get("label", "")
    return dg, labels


def wire_index(nodes):
    """wire uid -> [(node uid, term index, name, is_source)] within ONE diagram."""
    w = {}
    for u, n in nodes.items():
        for t in n["terms"]:
            if t["wire"]:
                w.setdefault(t["wire"], []).append((u, t["i"], t["name"], t["is_source"]))
    return w


def forward_reach(nodes, wi, seed_wires, seed_nodes=(), sr_edges=None, panel_edges=None):
    """Every node of this diagram reachable by following data FORWARD from `seed_wires`.

    EDGE MODEL v2, and the reason it exists. v1 followed WIRES only, and on this diagram that is not the data
    flow: it classified `CaseStructure #5540` - the reseed case that feeds two of the kernel's own inputs - as
    carrying no per-frame value, contradicting docs/d1-build-plan.md s4/s8. Two carriers are invisible to a wire
    graph, and both are MEASURED here rather than assumed:
      * SHIFT REGISTERS. `Nodes[]` does not contain them (docs/toolkit-capabilities.md:494), so the kernel's own
        outputs re-enter the next iteration through a pair whose two inner wires have no common node. Measured by
        `g.shift_reg_left()`: e.g. right #1147 inner wire 505 (= #5058 `x,y,z array out`) -> left #1142 inner wire
        1681 -> #5540 t5. `sr_edges` maps right-inner wire -> left-inner wires.
      * THE FRONT PANEL. An indicator written on the diagram and read back by an IMPLICIT PROPERTY NODE is a data
        path through the UI, with no wire between them: #10969 `min value` (wire 17287) writes the indicator
        `min value` uid 17257, and `Property 'min value'.Value` #17289 reads it back into #10950. Measured by
        `g.panel_wiring()` (the wire on the indicator's terminal) joined to `OpNodeLabels_v0`'s label for the
        implicit node. `panel_edges` maps that wire -> the reader nodes.
    Both classifications are reported, so the correction is visible instead of silently replacing v1."""
    sr_edges = sr_edges or {}
    panel_edges = panel_edges or {}
    seen, frontier = set(seed_nodes), list(seed_wires)
    for u in seed_nodes:
        for t in nodes.get(u, {}).get("terms", []):
            if t["wire"] and t["is_source"]:
                frontier.append(t["wire"])
    done_w = set()
    while frontier:
        w = frontier.pop()
        if w in done_w:
            continue
        done_w.add(w)
        frontier.extend(sr_edges.get(w, []))
        for u in panel_edges.get(w, []):
            if u in nodes and u not in seen:
                seen.add(u)
                frontier.extend(t["wire"] for t in nodes[u]["terms"] if t["wire"] and t["is_source"])
        for u, _i, _nm, is_src in wi.get(w, []):
            if is_src or u in seen:
                continue
            seen.add(u)
            for t in nodes[u]["terms"]:
                if t["wire"] and t["is_source"]:
                    frontier.append(t["wire"])
    return seen


def backward_reach(nodes, wi, sink_nodes, sr_edges=None, panel_edges=None):
    """Every node whose data eventually reaches one of `sink_nodes` - the transpose of forward_reach, with the
    same two extra carriers (a shift-register pair, an indicator written then read back by an implicit Property
    node) traversed in the opposite direction."""
    sr_back, panel_back = {}, {}
    for r_w, l_ws in (sr_edges or {}).items():
        for l_w in l_ws:
            sr_back.setdefault(l_w, []).append(r_w)
    for w, us in (panel_edges or {}).items():
        for u in us:
            panel_back.setdefault(u, []).append(w)
    seen, frontier = set(), []
    for u in sink_nodes:
        for t in nodes.get(u, {}).get("terms", []):
            if t["wire"] and not t["is_source"]:
                frontier.append(t["wire"])
    done_w = set()
    while frontier:
        w = frontier.pop()
        if w in done_w:
            continue
        done_w.add(w)
        frontier.extend(sr_back.get(w, []))
        for u, _i, _nm, is_src in wi.get(w, []):
            if not is_src or u in seen:
                continue
            seen.add(u)
            frontier.extend(panel_back.get(u, []))
            for t in nodes[u]["terms"]:
                if t["wire"] and not t["is_source"]:
                    frontier.append(t["wire"])
    return seen


def build_extra_edges(sr_rows, panel_rows, labels, nodes):
    """sr_edges: right-register inner wire -> the paired left register's inner wires (the value re-entering the
    next iteration). panel_edges: an INDICATOR's terminal wire -> every node on this diagram whose OpNodeLabels_v0
    label is that indicator's label (an implicit `Value` property node or a Local reading it back)."""
    sr_edges = {}
    for r in sr_rows:
        rights = [t["wire"] for t in r.get("inside", []) if t.get("wire")]
        lefts = [t["wire"] for t in r.get("left", {}).get("inside", []) if t.get("wire")]
        for rw in rights:
            sr_edges.setdefault(rw, []).extend(lefts)
    by_label = {}
    for u in nodes:
        lb = (labels.get(u) or "").strip()
        if lb:
            by_label.setdefault(lb, []).append(u)
    panel_edges = {}
    for row in panel_rows:
        w = int(row.get("wire") or 0)
        lb = (row.get("label") or "").strip()
        if w and lb and row.get("indicator"):
            readers = by_label.get(lb, [])
            if readers:
                panel_edges.setdefault(w, []).extend(readers)
    return sr_edges, panel_edges


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    before = md5(MAIN)
    print(f"MAIN md5 before: {before}", flush=True)
    gate("G0a MAIN md5 before == recorded", before == MD5_EXPECTED, before)
    if before != MD5_EXPECTED:
        return 1

    dg, labels = load_offline()
    n43 = {n["uid"]: n for n in dg[D_FRAME]["nodes"]}
    n19 = {n["uid"]: n for n in dg[D_SIB]["nodes"]}
    w43, w19 = wire_index(n43), wire_index(n19)
    print(f"offline: diagram {D_FRAME} has {len(n43)} nodes / {len(w43)} wire uids; "
          f"diagram {D_SIB} has {len(n19)} nodes / {len(w19)} wire uids", flush=True)

    # ---- G1: the seam, re-derived from the census -------------------------------------
    k = n43.get(KERNEL)
    k_wires = [t["wire"] for t in (k["terms"] if k else []) if t["wire"]]
    expect = [5637, 3040, 373, 5859, 505, 5975, 121, 42, 3512, 3646, 7429, 3912, 4027]
    gate("G1 the census gives #5058 16 terminals carrying the 13 recorded wires",
         bool(k) and len(k["terms"]) == 16 and k_wires == expect,
         f"{len(k['terms']) if k else 0} terminals, wires {k_wires}")
    gate("G2 all 7 backward-slice nodes are on diagram 43",
         all(u in n43 for u in BACKWARD), f"missing {[u for u in BACKWARD if u not in n43]}")

    # ---- reachability seeds (the graphs themselves need the LabVIEW half, below) --------
    per_frame_seeds = list(KERNEL_OUT_WIRES)
    for t in n43[FRAME_SRC]["terms"]:
        if t["is_source"] and t["wire"] and t["name"] in ("Image Out", "current image number", "Missed frames?"):
            per_frame_seeds.append(t["wire"])
    fact(f"per-frame seed wires {sorted(set(per_frame_seeds))}")

    # ---- the LabVIEW half: resolve every boundary wire ---------------------------------
    bnd = {}          # wire -> [(uid, i, name, is_source)] ends we already know, on d43
    for u in MOVE_SET:
        if u not in n43:
            continue
        for t in n43[u]["terms"]:
            w = t["wire"]
            if w and not [e for e in w43.get(w, []) if e[0] != u]:
                bnd.setdefault(w, []).append((u, t["i"], t["name"], t["is_source"]))
    for u in SIB_SET:
        if u not in n19:
            continue
        for t in n19[u]["terms"]:
            w = t["wire"]
            if w and not [e for e in w19.get(w, []) if e[0] != u]:
                bnd.setdefault(w, []).append((u, t["i"], t["name"], t["is_source"], "d19"))
    fact(f"{len(bnd)} boundary wires on the move set (one census end only): {sorted(bnd)}")

    resolved = {}     # wire -> {"kind":..., "detail":...}
    tun_rows, sr_rows, panel_rows, ws_rows, owners = [], [], [], [], {}
    # `--offline` re-runs ONLY the classification, from the census this script wrote on its LabVIEW pass. It exists
    # because the edge model was corrected after the first pass (see forward_reach); re-measuring the same
    # read-only facts to re-run 30 lines of graph code would be a LabVIEW batch for nothing.
    if "--offline" in sys.argv:
        prev = json.load(open(OUT, encoding="utf-8"))
        gate("G0z --offline: the saved census is for this md5", prev.get("md5") == before, str(prev.get("md5")))
        resolved = {int(k): v for k, v in prev["resolved_boundary"].items()}
        tun_rows, sr_rows, panel_rows = prev["tunnels"], prev["shift_regs"], prev["panel"]
        ws_rows, owners, h0, h1 = prev["wiresource"], prev.get("owners", {}), 0, 0
        fact(f"--offline: reusing {len(resolved)} resolved wires, {len(tun_rows)} tunnels, {len(sr_rows)} "
             f"shift registers, {len(panel_rows)} panel rows from {os.path.basename(OUT)}")
    else:
        h0, h1 = fresh()
    try:
        if "--offline" in sys.argv:
            raise _Skip()
        # --- tunnels ------------------------------------------------------------------
        t0 = time.time()
        i = 0
        while i < 200:
            r = g.tunnels(MAIN, i)
            if not r["uid"]:
                break
            tun_rows.append(r)
            i += 1
        fact(f"tunnel census: {len(tun_rows)} LoopTunnels in {time.time() - t0:.0f} s")
        gate("G3a the tunnel census returns 132 LoopTunnels", len(tun_rows) == 132, str(len(tun_rows)))
        for r in tun_rows:
            for w, side in [(r["out_wire"], "outer")] + [(x, "inner") for x in r["in_wires"]]:
                if w and w in bnd and w not in resolved:
                    resolved[w] = {"kind": "LoopTunnel", "uid": r["uid"], "index_mode": r["index_mode"],
                                   "side": side, "out_wire": r["out_wire"], "in_wires": r["in_wires"],
                                   "out_name": r["out_name"]}
        want = {373: 2580, 42: 2396, 3512: 4432, 3646: 3656, 3912: 3920, 4027: 4031}
        got = {w: resolved.get(w, {}).get("uid") for w in want}
        gate("G3 the 6 loop-invariant kernel inputs resolve to the recorded LoopTunnels",
             got == want, f"{got} vs {want}")

        # --- shift registers of #637 ---------------------------------------------------
        for ri in range(N_SHIFT_REGS + 2):
            try:
                r = g.shift_reg_left(MAIN, WHILE_INDEX_637, ri, 0, "WhileLoop")
            except Exception as e:
                fact(f"shift_reg_left({ri}) raised {str(e)[:80]}")
                break
            if not r.get("uid"):
                break
            sr_rows.append(r)
            for side, rec in (("right", r), ("left", r["left"])):
                for w, which in [(rec["out"]["wire"], "outside")] + \
                                [(t["wire"], "inside") for t in rec["inside"]]:
                    if w and w in bnd and w not in resolved:
                        resolved[w] = {"kind": f"{side}ShiftRegister", "uid": rec.get("uid"),
                                       "class": rec.get("class"), "side": which}
        fact(f"shift-register census: {len(sr_rows)} registers of WhileLoop[{WHILE_INDEX_637}]; "
             f"uids {[r.get('uid') for r in sr_rows]} / lefts {[r['left'].get('uid') for r in sr_rows]}")
        gate("G4a the frame loop has 14 shift registers", len(sr_rows) == N_SHIFT_REGS, str(len(sr_rows)))
        sr_7429 = resolved.get(7429, {})
        sr_5859 = resolved.get(5859, {})
        gate("G4 wires 7429 (pos in cal image in) and 5859 (Bead is good? array out) are shift-register terminals",
             "ShiftRegister" in str(sr_7429.get("kind")) and "ShiftRegister" in str(sr_5859.get("kind")),
             f"7429 -> {sr_7429}; 5859 -> {sr_5859}")

        # --- panel terminals -----------------------------------------------------------
        panel_rows = g.panel_wiring(MAIN)
        gate("G5 panel_wiring returns 114 rows", len(panel_rows) == 114, str(len(panel_rows)))
        for r in panel_rows:
            w = int(r.get("wire") or 0)
            if w and w in bnd and w not in resolved:
                resolved[w] = {"kind": "PanelTerminal", "label": r.get("label"),
                               "indicator": r.get("indicator"), "uid": r.get("uid"),
                               "is_source": r.get("is_source")}

        # --- OpWireSource_v5 on what is left, subject set first -------------------------
        left = [w for w in bnd if w not in resolved]
        subj_left = [w for w in left if any(e[0] in SUBJECT for e in bnd[w])]
        order = subj_left + [w for w in left if w not in subj_left]
        fact(f"after tunnels/SRs/panel: {len(resolved)}/{len(bnd)} boundary wires resolved; "
             f"{len(left)} left ({len(subj_left)} of them on the step-0 subject set)")
        wl = json.load(open(MAP_OUT, encoding="utf-8"))
        vi = g.op(OP_WIRE)
        t0 = time.time()
        for w in order:
            if time.time() - t0 > 600:
                fact(f"OpWireSource_v5 budget reached; {len(order) - order.index(w)} wires not read")
                break
            rows = []
            for ti in range(8):
                r = read_terminal(vi, wl, w, ti)
                if r["errs"] and r["owner_uid"] == 0:
                    break
                rows.append(r)
            srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == w]
            ws_rows.append({"wire": w, "rows": rows})
            if srcs:
                resolved[w] = {"kind": "OpWireSource_v5", "owner_class": srcs[0]["owner_class"],
                               "owner_uid": srcs[0]["owner_uid"],
                               "sinks": [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]}
            else:
                resolved[w] = {"kind": "UNRESOLVED",
                               "terminals": [(r["owner_class"], r["owner_uid"], r["is_source"]) for r in rows]}
            print(f"    wire {w} -> {resolved[w]}", flush=True)
        still = [w for w in bnd if w not in resolved or resolved[w]["kind"] == "UNRESOLVED"]
        subj_still = [w for w in still if any(e[0] in SUBJECT for e in bnd[w])]
        gate("G6 every boundary wire of the step-0 subject set is resolved",
             not subj_still, f"unresolved on subject set: {subj_still}; overall still open: {still}")

        # --- owner chain spot checks ---------------------------------------------------
        vi2 = g.op(OP_OWNER)
        for u in (KERNEL, 10407, 48, 5540, 12589, 11639, 6810):
            h = read_owner(vi2, wl, u)
            owners[u] = h
            print(f"    owner({u}) = {h['ownercls']!r}#{h['owner_uid']} (self {h['cls_back']!r}#{h['uid_back']})",
                  flush=True)
    except _Skip:
        pass
    finally:
        h2 = handles() if "--offline" not in sys.argv else 0
        after = md5(MAIN)
        gate("G0b MAIN md5 after == before", after == before, after)
        print(f"handles: {h0} -> restart -> {h1} -> end {h2}", flush=True)

    # ---- the two edge models, and the reachability each of them gives -------------------
    sr_edges, panel_edges = build_extra_edges(sr_rows, panel_rows, labels, n43)
    fwd1 = forward_reach(n43, w43, per_frame_seeds)
    back1 = backward_reach(n43, w43, [KERNEL])
    fwd = forward_reach(n43, w43, per_frame_seeds, sr_edges=sr_edges, panel_edges=panel_edges)
    back = backward_reach(n43, w43, [KERNEL], sr_edges=sr_edges, panel_edges=panel_edges)
    fact(f"edge model v1 (wires only): {len(fwd1)} nodes carry a per-frame value, {len(back1)} reach a #5058 "
         f"input. edge model v2 (+{len(sr_edges)} shift-register hops, +{len(panel_edges)} indicator->implicit-"
         f"property hops): {len(fwd)} and {len(back)}")
    moved = sorted((fwd - fwd1) | (back - back1))
    fact(f"nodes the corrected model adds: {[(u, labels.get(u, '')) for u in moved]}")

    # ---- (a) classify the 7 backward-slice nodes --------------------------------------
    def srcs_of(u):
        out = []
        for t in n43[u]["terms"]:
            if t["is_source"] or not t["wire"]:
                continue
            ends = [e for e in w43.get(t["wire"], []) if e[0] != u and e[3]]
            out.append((t["i"], t["name"], t["wire"], ends or resolved.get(t["wire"], {"kind": "?"})))
        return out

    def sinks_of(u):
        out = []
        for t in n43[u]["terms"]:
            if not t["is_source"] or not t["wire"]:
                continue
            ends = [e for e in w43.get(t["wire"], []) if e[0] != u and not e[3]]
            out.append((t["i"], t["name"], t["wire"], ends or resolved.get(t["wire"], {"kind": "?"})))
        return out

    def classify(u, fw, bk, model):
        """The rule, applied identically under both edge models so the difference between them is visible.
        `per_frame_in` = an input whose value is carried by something already known to be per-frame: a node end
        that is per-frame, a shift-register pair whose RIGHT inner wire is per-frame, or an indicator terminal
        whose wire is per-frame."""
        pf = []
        for t in n43[u]["terms"]:
            if t["is_source"] or not t["wire"]:
                continue
            for e in w43.get(t["wire"], []):
                if e[0] != u and e[3] and (e[0] in fw or e[0] in (KERNEL, FRAME_SRC)):
                    pf.append((t["i"], t["name"], t["wire"], f"node #{e[0]}"))
            if model == "v2":
                for rw, lws in sr_edges.items():
                    if t["wire"] in lws and (rw in per_frame_wires(fw)):
                        pf.append((t["i"], t["name"], t["wire"], f"shift register, previous iteration of w{rw}"))
        reaches = u in bk
        if u == FRAME_SRC:
            return "stays-with-acquisition", ("it IS the frame source (row 1.8 REUSE); its `Image Out` crosses "
                                              "to 1.2 through Q_work"), pf
        if pf and reaches:
            return "moves-with-kernel", f"per-frame inputs {pf}; and it reaches a #5058 input", pf
        if pf and not reaches:
            return "moves-with-kernel (downstream side)", f"per-frame inputs {pf}; no path back into #5058", pf
        has_wired_input = any((not t["is_source"]) and t["wire"] for t in n43[u]["terms"])
        if not has_wired_input and u in fw:
            # An IMPLICIT PROPERTY NODE has no data input at all - it reads a front-panel object. So "per-frame
            # input" is the wrong question for it: it is per-frame because the object it reads is WRITTEN each
            # frame (the panel edge that put it in `fw`), and its placement follows the consumers of its `Value`.
            return ("moves-with-kernel (panel read, no data input)",
                    "no wired input; it reads a front-panel object that a per-frame node writes, so it is "
                    "per-frame and must be evaluated in the same loop, after that writer, to keep the original's "
                    "order", pf)
        if not pf and reaches:
            return "stays-with-tunnel", ("no per-frame input under this model; its value is loop-invariant and "
                                         "crosses the new border on a tunnel"), pf
        return "UNCLASSIFIED", "neither per-frame nor kernel-reaching under this model", pf

    def per_frame_wires(fw):
        """Every wire SOURCED by a per-frame node, plus the seeds - what a shift register may be carrying."""
        s = set(per_frame_seeds)
        for u_ in fw:
            for t in n43[u_]["terms"]:
                if t["is_source"] and t["wire"]:
                    s.add(t["wire"])
        return s

    classification = {}
    print("\n=== (a) BACKWARD SLICE - the 7 nodes of frame-loop-wire-graph.md:43 ===", flush=True)
    for u in BACKWARD:
        c1, _why1, _pf1 = classify(u, fwd1, back1, "v1")
        cls, why, pf = classify(u, fwd, back, "v2")
        classification[u] = {"class": cls, "class_wires_only": c1, "why": why, "label": labels.get(u, ""),
                             "per_frame_inputs": pf, "sources": srcs_of(u), "sinks": sinks_of(u)}
        print(f"\n  #{u} {labels.get(u, '')!r}  ->  {cls}"
              + (f"   [wire-graph-only model said: {c1}]" if c1 != cls else ""), flush=True)
        print(f"      because: {why}", flush=True)
        for i_, nm, w, e in classification[u]["sources"]:
            print(f"      IN  t{i_:<2} {nm!r:44} w{w:<6} <- {e}", flush=True)
        for i_, nm, w, e in classification[u]["sinks"]:
            print(f"      OUT t{i_:<2} {nm!r:44} w{w:<6} -> {e}", flush=True)
    gate("G8 each of the 7 backward-slice nodes has exactly one classification",
         all(v["class"] != "UNCLASSIFIED" for v in classification.values()),
         str({u: v["class"] for u, v in classification.items()}))
    # d1-build-plan s4 / s8 name the placement of exactly two of the seven. The other five are what step 0 is FOR,
    # and are reported, not predicted.
    plan_says = {5540: "moves-with-kernel", 6810: "stays-with-acquisition"}
    gate("G9 the measured classification agrees with d1-build-plan s4/s8 where the plan states a placement",
         all(classification[u]["class"] == v for u, v in plan_says.items()),
         str({u: (classification[u]["class"], v) for u, v in plan_says.items()}))

    # ---- (b) the notifier payload ------------------------------------------------------
    print("\n=== (b) #10407's per-frame inputs derived from the kernel's outputs ===", flush=True)
    kfwd = forward_reach(n43, w43, KERNEL_OUT_WIRES, seed_nodes=[KERNEL])
    payload = []
    for host in (10407, 48):
        if host not in n43:
            continue
        for t in n43[host]["terms"]:
            if t["is_source"] or not t["wire"]:
                continue
            for e in w43.get(t["wire"], []):
                if e[0] != host and e[3] and (e[0] in kfwd or e[0] == KERNEL):
                    payload.append({"host": host, "term": t["i"], "name": t["name"], "wire": t["wire"],
                                    "from_node": e[0], "from_term": e[2],
                                    "from_label": labels.get(e[0], "")})
                    print(f"  #{host} t{t['i']} {t['name']!r} <- w{t['wire']} <- #{e[0]} "
                          f"{labels.get(e[0], '')!r} {e[2]!r}", flush=True)
    others = []
    for host in (10407, 48):
        for t in n43.get(host, {}).get("terms", []):
            if t["is_source"] or not t["wire"]:
                continue
            if not any(p["host"] == host and p["term"] == t["i"] for p in payload):
                ends = [e for e in w43.get(t["wire"], []) if e[0] != host and e[3]]
                others.append((host, t["i"], t["name"], t["wire"], ends or resolved.get(t["wire"], {"kind": "?"})))
    print("  the focus loop's OTHER inputs (not kernel-derived - tunnel / panel / VISA / its own partner):",
          flush=True)
    for row in others:
        print(f"    #{row[0]} t{row[1]} {row[2]!r:44} w{row[3]} <- {row[4]}", flush=True)
    width = len({(p["host"], p["term"]) for p in payload})
    fact(f"NOTIFIER PAYLOAD WIDTH (measured) = {width} value(s): "
         f"{[(p['host'], p['term'], p['name']) for p in payload]}")
    gate("G7 #10407 / #48 consume at least one kernel-derived per-frame value", width >= 1, str(width))

    # the reverse crossing, if any: what the focus pair FEEDS that stays behind
    rev = []
    for host in (10407, 48):
        for t in n43.get(host, {}).get("terms", []):
            if not t["is_source"] or not t["wire"]:
                continue
            for e in w43.get(t["wire"], []):
                if e[0] != host and not e[3] and e[0] not in (10407, 48):
                    rev.append((host, t["i"], t["name"], t["wire"], e[0], labels.get(e[0], ""), e[2]))
    for r in rev:
        fact(f"REVERSE CROSSING: #{r[0]} t{r[1]} {r[2]!r} w{r[3]} -> #{r[4]} {r[5]!r} {r[6]!r} "
             f"(a value the 1.5 loop produces that a node outside it consumes)")

    # ---- (c) the BEFORE census ---------------------------------------------------------
    census = {"md5": before, "diagram_43": {}, "diagram_19": {}, "resolved_boundary": resolved,
              "classification": classification, "payload": payload, "payload_width": width,
              "focus_other_inputs": others, "reverse_crossings": rev,
              "tunnels": tun_rows, "shift_regs": sr_rows, "panel": panel_rows,
              "wiresource": ws_rows, "owners": {str(k_): v for k_, v in owners.items()}}
    for u in MOVE_SET:
        if u in n43:
            census["diagram_43"][str(u)] = {"label": labels.get(u, ""), "n": n43[u]["n"],
                                            "terms": n43[u]["terms"]}
    for u in SIB_SET:
        if u in n19:
            census["diagram_19"][str(u)] = {"label": labels.get(u, ""), "n": n19[u]["n"],
                                            "terms": n19[u]["terms"]}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(census, f, indent=1, default=str)
    fact(f"BEFORE census written: {OUT} "
         f"({len(census['diagram_43'])} nodes on d43, {len(census['diagram_19'])} on d19)")

    print("\n--- FACTS ---", flush=True)
    for line in _facts:
        print("  " + line, flush=True)
    npass = sum(1 for _, ok in _gates if ok)
    print(f"\nSUMMARY {npass}/{len(_gates)} gates pass; failing: {[n for n, ok in _gates if not ok]}", flush=True)
    return 0 if npass == len(_gates) else 1


if __name__ == "__main__":
    sys.exit(main())
