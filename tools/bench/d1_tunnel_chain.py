r"""d1_tunnel_chain.py - OFFLINE resolution of the 18 `from-tunnel` re-wire rows, by ITERATING the one hop
`d1_rewire_map.py:205-214` already takes once. No LabVIEW, no op, no new VI.

    MATERIAL=1 py -u tools/bench/d1_tunnel_chain.py

WHY THIS AND NOT `OpTunnelSource_v0` (archive/peer/2026-09-17-priorart-tunnelsource-onehop.md, ANSWERED, 5
findings, 0 novel - all accepted, none refuted):
  * **B4 `already-measured`**: `d1_step0_census.json` already holds ALL 132 LoopTunnels with `out_wire`/`in_wires`
    and `main_vi_nodeterms.json` every diagram's terminals with `i/name/is_source/wire`. "Does the chain reach an
    addressable source?" can therefore be measured with ZERO LabVIEW runs - it just was never tried, because
    `d1_rewire_map.py:212-214` never consults the `tun_by_wire` map it builds 50 lines earlier at `:152-158`.
  * **B3 `helper-exists`**: the composition (tunnel census + OpWireSource_v5 + offline join) is already
    implemented and measured 91/91 (`diag_d1_step0.py:375-395,:432-455`), so this is an EDIT, not construction.
  * **B2 `already-failed`**: the `OpWireSource_v5` 1055 is a CALLER defect - `diag_d1_full_route.py:265-273`
    never sets the op's `UID 2` input while the op is UID-addressed (`toolkit-capabilities.md:48`,
    `opwiresource_v5_labels.json:7`), and the callers that DO set it answered correctly with the same 1055 as the
    documented terminator (`diag_d1_step0.log:21-58`, `NAMES.md:944-945`). So no LabVIEW run is spent proving the
    op is broken; if a row needs the machine, the caller sets `UID 2` and never reuses the ORIGINAL-hard-coded
    `build_opwiresource_v5.read_terminal` (`:35,:161`).
  * **A4 `unread-evidence`**: a source terminal whose owner is a **Diagram** is the CONTROL-TERMINAL signature
    (`camera-acquisition-facts.md:235-237`, `diag_autofocus_border.log:19-26` - wire 3268 driven by
    ('Diagram', 639)). It is a THIRD owner case with no `Nodes[]/Terminals[]` index, so this resolver classifies
    it separately (`from-ctl`) instead of pretending `OpConnectNested_v1` can address it.
  * **A3 `contradicted`**: "the value comes from further out through more unnamed tunnels" is a LITERAL printed by
    `build_d1_v0.py:1012-1018` whenever `outer_source` is not a NAMED node - it fired on `#376` t7, whose source
    WAS resolved (`build_d1_v0_run7.log:317`). So the "CHAIN with no origin" premise of `d1-build-plan.md:740-743`
    was never measured. This run measures it.

OUTPUT `tools/bench/d1_tunnel_chain.json`: per row, the hop list and one of
    node   -> (census diagram key, node uid, terminal index)  = addressable by OpConnectNested_v1
    const  -> a diagram constant                              = OpCreateConstOnTerm_v0 re-creates the literal
    ctl    -> a panel control terminal (Diagram-owned source) = wire_control / a moved ControlTerminal
    sr     -> a shift register
    dead   -> the chain ends with nothing driving the wire
"""
import json
import os
import sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
ST0 = os.path.join(HERE, "d1_step0_census.json")
NT = os.path.join(HERE, "main_vi_nodeterms.json")
SCAN = os.path.join(HERE, "opconstvaluen_scan.json")
ROWS_IN = os.path.join(HERE, "d1_rewire_sources.json")
OUT = os.path.join(HERE, "d1_tunnel_chain.json")
MAX_HOPS = 8


def load(p):
    if not os.path.exists(p):
        print(f"  MISSING {p}", flush=True)
        return None
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def main():
    st0, nt, scan, rows_in = load(ST0), load(NT), load(SCAN), load(ROWS_IN)
    if not (st0 and nt and rows_in):
        return 1

    by_wire = defaultdict(list)
    for dk, dv in nt["diagrams"].items():
        for n in dv["nodes"]:
            for t in n["terms"]:
                if t["wire"]:
                    by_wire[t["wire"]].append(dict(kind="node", diagram=dk, uid=n["uid"], i=t["i"],
                                                   name=t["name"], is_source=t["is_source"]))
    const_by_wire = {}
    rows = []
    if isinstance(scan, dict):
        for k in ("rows", "constants", "numerics", "scan"):
            if isinstance(scan.get(k), list):
                rows = scan[k]
                break
    elif isinstance(scan, list):
        rows = scan
    for r in rows:
        if isinstance(r, dict):
            w = r.get("wire") or r.get("wire_uid") or 0
            if w:
                const_by_wire[int(w)] = dict(kind="const", uid=r.get("uid"), val=r.get("val"),
                                             text=r.get("txt", r.get("text")))
    ctl_by_wire, tun_by_wire, sr_by_wire = {}, {}, {}
    for row in (st0.get("panel") or st0.get("panel_wiring") or []):
        if isinstance(row, dict) and row.get("wire"):
            ctl_by_wire[int(row["wire"])] = dict(kind="ctl", uid=row.get("uid"), label=row.get("label"),
                                                 indicator=row.get("indicator"))
    tun_by_uid = {}
    for row in (st0.get("tunnels") or []):
        if not isinstance(row, dict):
            continue
        tun_by_uid[row.get("uid")] = row
        for w in ([row.get("out_wire")] + list(row.get("in_wires") or [])):
            if w:
                tun_by_wire[int(w)] = row
    for row in (st0.get("shift_regs") or []):
        if not isinstance(row, dict):
            continue
        for w in ([row.get("out_wire")] + list(row.get("in_wires") or [])):
            if w:
                sr_by_wire[int(w)] = dict(kind="sr", uid=row.get("uid"))
    print(f"census: {len(by_wire)} node wires, {len(const_by_wire)} const, {len(ctl_by_wire)} ctl, "
          f"{len(tun_by_wire)} tunnel, {len(sr_by_wire)} sr; {len(tun_by_uid)} tunnels by uid", flush=True)

    def hop(w, seen):
        """one hop on wire w -> ('node'|'const'|'ctl'|'sr'|'tunnel'|'dead', payload)"""
        src = next((e for e in by_wire.get(w, []) if e["is_source"]), None)
        if src:
            return "node", src
        if w in const_by_wire:
            return "const", const_by_wire[w]
        if w in ctl_by_wire:
            return "ctl", ctl_by_wire[w]
        if w in sr_by_wire:
            return "sr", sr_by_wire[w]
        t = tun_by_wire.get(w)
        if t and t.get("uid") not in seen:
            return "tunnel", t
        return "dead", None

    out, cls = [], Counter()
    ft = [r for r in rows_in["rows"] if r.get("action") == "from-tunnel"]
    for r in ft:
        w = r.get("outer_wire")
        seen, hops, kind, payload = set(), [], "dead", None
        if r["source"].get("uid"):
            seen.add(r["source"]["uid"])
        for _ in range(MAX_HOPS):
            if not w:
                kind, payload = "dead", None
                break
            kind, payload = hop(w, seen)
            hops.append(dict(wire=w, kind=kind,
                             uid=(payload or {}).get("uid"), name=(payload or {}).get("name"),
                             label=(payload or {}).get("label"), i=(payload or {}).get("i"),
                             diagram=(payload or {}).get("diagram")))
            if kind != "tunnel":
                break
            seen.add(payload.get("uid"))
            nxt = payload.get("out_wire")
            # the tunnel we arrived on may BE the one whose outer wire we already used: step to its outer wire,
            # and when that is the same wire, try its inner wires' sources instead (a nested structure's border)
            if nxt and nxt != w:
                w = nxt
                continue
            cand = [x for x in list(payload.get("in_wires") or []) if x and x != w]
            w = cand[0] if cand else None
        rec = dict(sink_uid=r["uid"], sink_term=r["i"], sink_name=r["name"], dest=r["dest"],
                   tunnel_uid=r["source"]["uid"], outer_wire=r.get("outer_wire"),
                   census_outer_source=r.get("outer_source"), kind=kind, source=payload, hops=hops)
        addressable = kind == "node"
        rec["addressable_by_connectnested_v1"] = addressable
        cls[kind] += 1
        out.append(rec)
        tail = ""
        if kind == "node":
            tail = (f"diagram {payload['diagram']} node #{payload['uid']} t{payload['i']} "
                    f"{payload['name']!r}")
        elif payload:
            tail = f"uid {payload.get('uid')} {payload.get('label') or payload.get('val') or ''}"
        print(f"  #{r['uid']:>6} t{r['i']:<3} {r['name']!r:<34.34} -> {len(hops)} hop(s) -> {kind:<7} {tail}",
              flush=True)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(dict(rows=out, by_kind=dict(cls), max_hops=MAX_HOPS), f, indent=1)
    print(f"\n{len(out)} from-tunnel rows: " + ", ".join(f"{v} {k}" for k, v in cls.most_common()), flush=True)
    print(f"addressable by OpConnectNested_v1 (node source): {cls['node']}/{len(out)}", flush=True)
    print(f"-> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
