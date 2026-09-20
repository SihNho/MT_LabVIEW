r"""d1_rewire_map.py - COMPLETE THE SOURCE MAP for D1's re-wire list, offline (no LabVIEW, no COM).

    py tools/bench/d1_rewire_map.py            -> tools/bench/d1_rewire_sources.json

`docs/d1-build-plan.md` §11j.2: "the re-wire source map is completed inside the build from `d1_step0_census.json`
+ `main_vi_nodeterms.json` (the 81/82 join the phase-full session computed) and written to
`tools/bench/d1_rewire_sources.json` as a by-product, not a precondition." STATUS OPEN 28b corrects "82/82" to
**45/82** and says the richer join was never written to disk. This file writes it, from four censuses that all
exist on disk already - nothing here is a new measurement:

  * `tools/bench/build_d1_v0.json`      - run 5/6's cut list: 109 terminals over 24 uids (the authoritative
                                          re-wire list, produced by S3b's own before/after diff)
  * `tools/bench/main_vi_nodeterms.json`- every NODE terminal of the VI, per diagram, with its wire uid
  * `tools/bench/opconstvaluen_scan.json` - 180 numeric CONSTANTS with the wire each one drives, its text and
                                          its Representation (toolkit row 47)
  * `tools/bench/d1_step0_census.json`  - the step-0 census: tunnels (132), shift registers (14), panel (114)

A LabVIEW wire is a NET, so "the source" is the one end with `is_source` TRUE. The four object kinds that can be
that end are NODE terminal, CONSTANT, CONTROL TERMINAL and LOOP TUNNEL / SHIFT REGISTER - and only the first is
in `main_vi_nodeterms.json`, which is exactly why the earlier join covered 45 of 82.

Every row is classified into the ACTION D1's PHASE "full" must take for it:
  same-loop      - both ends land in the SAME new loop  -> g.wire(), body to body
  cross-loop     - the ends land in DIFFERENT loops     -> a queue endpoint (plan §9)
  from-stay      - the source STAYS on 1.1              -> a queue endpoint (per-frame) or a tunnel (invariant)
  from-const     - the source is a diagram CONSTANT     -> OpCreateConstOnTerm_v0 with the SAME value (rule 1a)
  from-ctl       - the source is a CONTROL TERMINAL     -> the terminal moves with the node (plan §5d)
  from-tunnel    - the source is a LoopTunnel of #637   -> a NON-INDEXED tunnel on the new loop (plan §8)
  from-sr        - the source is a shift register       -> one of the 8 re-created registers (plan §5c)
  source-side    - the cut terminal is itself a SOURCE  -> driven from the sink side; no action of its own
  UNRESOLVED     - no end found in any census           -> reported, never guessed
"""
import json
import os
import sys
from collections import Counter, defaultdict

BENCH = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BENCH, "d1_rewire_sources.json")

MOVE = {"1.2": [5540, 9647, 10247, 10445, 10950, 17289, 10969, 10757, 1359, 2222, 2626, 6104, 8885, 9833,
                11261, 29874, 10686],
        "1.5": [10407, 48, 3529, 3560, 3447],
        "1.7": [376]}
DEST = {u: r for r, us in MOVE.items() for u in us}
KERNEL = 5058
# plan §5c - the 8 registers that move, by RIGHT/LEFT uid in the original
SR_UIDS = {1147: "1.2", 1142: "1.2", 5796: "1.2", 5805: "1.2", 119: "1.2", 2972: "1.2", 7311: "1.2",
           11001: "1.2", 4256: "1.5", 4274: "1.5", 4334: "1.5", 4344: "1.5", 15: "1.7", 51: "1.7",
           24: "1.7", 1108: "1.7"}
# plan §5c's own table, wire by wire - the RIGHT inner wire (the body source that FEEDS the register) and the
# LEFT inner wire (the register's value arriving in the body). A shift register is NOT a node on any diagram and
# NOT a LoopTunnel (`gscript.tunnels` says so in its own docstring), so neither `main_vi_nodeterms.json` nor the
# tunnel census can carry these eight - which is exactly the gap STATUS OPEN 28b records as "45 of 82".
SR_WIRES = {
    505:   (1147, 1142, "1.2", "x,y,z array out", "right-in"),
    1681:  (1147, 1142, "1.2", "x,y,z array out", "left-in"),
    5859:  (5796, 5805, "1.2", "Bead is good? array out", "right-in"),
    6041:  (5796, 5805, "1.2", "Bead is good? array out", "left-in"),
    121:   (119, 2972, "1.2", "pos in cal image out", "right-in"),
    7429:  (119, 2972, "1.2", "pos in cal image out", "left-in"),
    11389: (7311, 11001, "1.2", "Value", "right-in"),
    10763: (7311, 11001, "1.2", "Value", "left-in"),
    9113:  (4256, 4274, "1.5", "position [internal units]", "right-in"),
    3947:  (4256, 4274, "1.5", "position [internal units]", "left-in"),
    7337:  (4334, 4344, "1.5", "VISA out", "right-in"),
    1731:  (4334, 4344, "1.5", "VISA out", "left-in"),
    464:   (15, 51, "1.7", "total data array out", "right-in"),
    3497:  (15, 51, "1.7", "total data array out", "left-in"),
    541:   (24, 1108, "1.7", "error out", "right-in"),
    4880:  (24, 1108, "1.7", "error out", "left-in"),
}


def load(name):
    p = os.path.join(BENCH, name)
    if not os.path.exists(p):
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def build_map(cut):
    """The resolver, callable from a build: `cut` = S3b's own [[uid, i, name, is_source, wire], ...] list.
    Returns the payload written to `d1_rewire_sources.json`. No LabVIEW, no COM - four JSON censuses only."""
    return _resolve(cut, load("main_vi_nodeterms.json"), load("opconstvaluen_scan.json"),
                    load("d1_step0_census.json"))


def main():
    d1 = load("build_d1_v0.json")
    nt = load("main_vi_nodeterms.json")
    scan = load("opconstvaluen_scan.json")
    st0 = load("d1_step0_census.json")
    missing = [n for n, v in (("build_d1_v0.json", d1), ("main_vi_nodeterms.json", nt)) if v is None]
    if missing:
        print(f"MISSING: {missing}", flush=True)
        return 2

    payload = _resolve(d1["cut"], nt, scan, st0)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=1)
    cls = Counter(payload["by_action"])
    print(f"cut terminals {payload['cut_terminals']}; RESOLVED {payload['resolved']}/"
          f"{payload['cut_terminals']}; unresolved {payload['unresolved']}", flush=True)
    for k, v in cls.most_common():
        print(f"  {v:4d}  {k}", flush=True)
    print(f"  source censuses: {payload['counts']}", flush=True)
    for r in payload["rows"]:
        if r["action"] == "UNRESOLVED":
            print(f"  UNRESOLVED #{r['uid']} t{r['i']} {r['name']!r} w{r['wire']} "
                  f"other ends {r['other_ends']}", flush=True)
    print(f"-> {OUT}", flush=True)
    return 0


def _resolve(cut, nt, scan, st0):
    # ---- wire -> every NODE terminal on it
    by_wire = defaultdict(list)
    for dk, dv in nt["diagrams"].items():
        for n in dv["nodes"]:
            for t in n["terms"]:
                if t["wire"]:
                    by_wire[t["wire"]].append(dict(kind="node", diagram=dk, uid=n["uid"], i=t["i"],
                                                   name=t["name"], is_source=t["is_source"]))
    # ---- wire -> the CONSTANT that drives it (toolkit row 47 reads `Constant.Terminal` -> Connected Wire -> UID)
    const_by_wire = {}
    rows = []
    if isinstance(scan, dict):
        for k in ("rows", "constants", "numerics", "scan"):
            if isinstance(scan.get(k), list):
                rows = scan[k]
                break
        if not rows:
            rows = [v for v in scan.values() if isinstance(v, dict)]
    elif isinstance(scan, list):
        rows = scan
    for r in rows:
        if not isinstance(r, dict):
            continue
        w = r.get("wire") or r.get("wire_uid") or 0
        if w:
            const_by_wire[int(w)] = dict(kind="const", uid=r.get("uid"), text=r.get("txt", r.get("text")),
                                         repr=r.get("rep", r.get("repr")), val=r.get("val"))
    # ---- wire -> CONTROL TERMINAL (panel), and wire -> LoopTunnel / shift register, out of the step-0 census
    ctl_by_wire, tun_by_wire, sr_by_wire = {}, {}, {}
    if st0:
        for row in (st0.get("panel") or st0.get("panel_wiring") or []):
            if isinstance(row, dict) and row.get("wire"):
                ctl_by_wire[int(row["wire"])] = dict(kind="ctl", uid=row.get("uid"), label=row.get("label"),
                                                     indicator=row.get("indicator"))
        for row in (st0.get("tunnels") or []):
            if not isinstance(row, dict):
                continue
            for w in ([row.get("out_wire")] + list(row.get("in_wires") or [])):
                if w:
                    tun_by_wire[int(w)] = dict(kind="tunnel", uid=row.get("uid"),
                                               index_mode=row.get("index_mode"), out_name=row.get("out_name"))
        for row in (st0.get("shift_regs") or []):
            if not isinstance(row, dict):
                continue
            for w in ([row.get("out_wire")] + list(row.get("in_wires") or [])):
                if w:
                    sr_by_wire[int(w)] = dict(kind="sr", uid=row.get("uid"))

    out, cls = [], Counter()
    for uid, i, name, is_src, w in cut:
        ends = by_wire.get(w, [])
        others = [e for e in ends if not (e["uid"] == uid and e["i"] == i)]
        srcs = [e for e in ends if e["is_source"]]
        rec = dict(uid=uid, i=i, name=name, is_source=bool(is_src), wire=w, dest=DEST.get(uid),
                   other_ends=others, source=None, action=None)
        if w in SR_WIRES:
            right, left, row, nm, side = SR_WIRES[w]
            rec["source"] = dict(kind="sr", right=right, left=left, row=row, name=nm, side=side)
            rec["action"] = "from-sr" if side == "left-in" else "to-sr"
        elif is_src:
            rec["action"] = "source-side"
            rec["sinks"] = [e for e in others if not e["is_source"]]
        elif srcs:
            s = srcs[0]
            rec["source"] = s
            sd = DEST.get(s["uid"])
            if s["uid"] == KERNEL:
                rec["action"] = "from-kernel"        # #5058 is DELETED; the GPU kernel takes its place in 1.2
            elif sd and sd == rec["dest"]:
                rec["action"] = "same-loop"
            elif sd:
                rec["action"] = f"cross-loop:{sd}->{rec['dest']}"
            else:
                rec["action"] = f"from-stay:{s['uid']}"
        elif w in const_by_wire:
            rec["source"] = const_by_wire[w]
            rec["action"] = "from-const"
        elif w in ctl_by_wire:
            rec["source"] = ctl_by_wire[w]
            rec["action"] = "from-ctl"
        elif w in sr_by_wire or any(e["uid"] in SR_UIDS for e in others):
            rec["source"] = sr_by_wire.get(w) or dict(kind="sr", uid=next(
                (e["uid"] for e in others if e["uid"] in SR_UIDS), None))
            rec["action"] = "from-sr"
        elif w in tun_by_wire:
            rec["source"] = tun_by_wire[w]
            rec["action"] = "from-tunnel"
            # A LoopTunnel is a CARRIER, not a source: the value that reaches the moved node comes from whatever
            # drives the tunnel's OUTER wire, on the diagram that holds #637. D1 re-wires from THAT object, and
            # LabVIEW makes the new loop's tunnel itself (`gscript.wire`'s own contract). Without this second
            # hop the row names a tunnel that will not exist on the new loop.
            trec = next((t for t in (st0.get("tunnels") or []) if t.get("uid") == tun_by_wire[w]["uid"]), None)
            ow = (trec or {}).get("out_wire")
            rec["outer_wire"] = ow
            rec["outer_source"] = next((e for e in by_wire.get(ow, []) if e["is_source"]), None) if ow else None
            if rec["outer_source"] is None and ow:
                rec["outer_source"] = const_by_wire.get(ow) or ctl_by_wire.get(ow)
        else:
            rec["action"] = "UNRESOLVED"
        cls[rec["action"].split(":")[0]] += 1
        out.append(rec)

    resolved = sum(v for k, v in cls.items() if k != "UNRESOLVED")
    payload = dict(cut_terminals=len(out), resolved=resolved, unresolved=cls.get("UNRESOLVED", 0),
                   by_action=dict(cls), rows=out,
                   inputs=dict(cut="build_d1_v0.json", nodes="main_vi_nodeterms.json",
                               consts="opconstvaluen_scan.json" if const_by_wire else None,
                               step0="d1_step0_census.json" if st0 else None),
                   counts=dict(node_wires=len(by_wire), const_wires=len(const_by_wire),
                               ctl_wires=len(ctl_by_wire), tunnel_wires=len(tun_by_wire),
                               sr_wires=len(sr_by_wire)))
    return payload


if __name__ == "__main__":
    sys.exit(main())
