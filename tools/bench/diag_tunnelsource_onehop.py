r"""diag_tunnelsource_onehop.py - the ONE-HOP tunnel-source reader of `docs/d1-build-plan.md` §11r, built as a
COMPOSITION of two ops that already exist, and measured before anything is built.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/diag_tunnelsource_onehop.log \
        -- py -u tools/bench/diag_tunnelsource_onehop.py

WHAT ALREADY EXISTS (checked before a line was written - CLAUDE.md's standing rule, and §11q.2's own B2):
  * `gscript.tunnels(target, index)` -> `OpTunnels_v0.vi` (`tools/gscript.py:887-922`) already returns the
    LoopTunnel's uid, IndexMode and **`out_wire`** = the OUTSIDE terminal's connected wire. Verified
    `tools/bench/test_optunnels.log`. So `Tunnel.Outside Terminal` 6356001 need not be re-created.
  * `OpWireSource_v5.vi` (`tools/recipes/build_opwiresource_v5.py:155-174`) already takes (vi path, wire uid,
    terminal index) and returns `Is Source?`, the owner's CLASS and UID, the reciprocal wire and the cast class.
    So `Wire.Terminals[]`, `Is Source?` and the `Generic.Owner` cast (§11q.2 item 4) all exist already.
  * `tools/bench/d1_rewire_sources.json` already carries every `from-tunnel` row with its `outer_wire`.
  * the terminal's INDEX WITHIN ITS OWNER is pure Python: `node_terms()` rows carry the wire uid per terminal.
=> No new op VI is built unless this composition is MEASURED to fail. §11r's budget of 2 builds is untouched here.

THE CONTRACT (each gate a prediction; nothing is written outside tools/bench/ and no VI is modified at all)
 G0  original working copy md5 2a78e17c449cacdaf5da389818526859 BEFORE; LabVIEW restarted (COM poison guard);
     handles recorded. The VI is read HEADLESS (GetVIReference only, rule 1d) - no panel, no edit, no save.
 G1  `exec_state` of OpWireSource_v5.vi, OpTunnels_v0.vi, OpConnectNested_v1.vi READ FROM THE MACHINE. This is
     §11q.2 item 2 answered by measurement instead of inference: `diag_d1_full_route.json:49-52` recorded 0 rows /
     error 1055 with `execstate_discriminator` 0 in all three arms, and nobody ever read the op VI's own state.
 G2  THE PUBLISHED CONTROL, re-run: wire 10850 on the working copy must give EXACTLY ONE terminal that is a
     source and whose reciprocal wire is 10850 (`docs/NAMES.md:946` records 12/12; `diag_d1_full_route.json`
     records the same op returning 1055). Whichever reproduces, it is read, not argued.
 G3  THREE from-tunnel rows resolved one hop and cross-checked against `tools/bench/d1_rewire_sources.json`'s own
     `outer_source` where it has one (row `#1359` t9 `Magnet position output` <- `#27605`; `#376` t7 <- a source
     terminal of `#637`), plus `#5058` t12 (`Array of cal clusters`, tunnel #3656, outer wire 3668).
 G4  ALL 18 from-tunnel rows resolved to (owner class, owner uid, terminal index within the owner) and, where the
     owner can be located, to the (diagram index, node index, terminal index) triple `OpConnectNested_v1` takes.
     An owner that is itself a tunnel is re-read ONE HOP at a time from Python (max 6 hops), never by an owner
     walker inside LabVIEW (§11q.2 item 4's FlatSequenceFrame dead end is therefore not on the path).
 G5  `tools/bench/d1_tunnel_sources.json` written; unresolved rows reported AS unresolved, never guessed.
 G6  original md5 unchanged AFTER; handles after.

FAILURE BUDGET 2 (CLAUDE.md §3).
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g                        # noqa: E402
from bench_prep import labview_handles      # noqa: E402
from build_opconstvalue_v1 import fresh     # noqa: E402

MAIN = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
MAIN_MD5 = "2a78e17c449cacdaf5da389818526859"
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
V5_LABELS = os.path.join(HERE, "opwiresource_v5_labels.json")
ROWS_IN = os.path.join(HERE, "d1_rewire_sources.json")
OUT = os.path.join(HERE, "d1_tunnel_sources.json")
CONTROL_WIRE = 10850
CONTROL_OWNERS = {10739: "the constant scan's answer", 3628: "the v2 wire-walk's answer"}
# diagrams searched for an owner, cheapest first: 19 = the frame loop's holder, 43 = the frame loop body,
# 0 = the top level. `d1_step0_census.json` names 19 and 43; anything else is reported unlocated.
DIAGRAMS = (19, 43, 0)
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    print(f"  {'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}", flush=True)
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


# ---------------------------------------------------------------- the ONE HOP (OpWireSource_v5, generalised)
_LAB = None


def labels():
    global _LAB
    if _LAB is None:
        with open(V5_LABELS, encoding="utf-8") as f:
            _LAB = json.load(f)
    return _LAB


def read_terminal(target, wire_uid, idx):
    """One terminal of one wire: (is_source, owner class, owner uid, reciprocal wire). Poison every readout
    first, exactly as build_opwiresource_v5.read_terminal does, so a stale value cannot be read as an answer."""
    lab = labels()
    vi = g.op(V5)
    for k in (lab["ownercls"], lab["cls_back"], lab["cast_class"]):
        try:
            vi.SetControlValue(k, "POISON")
        except Exception:
            pass
    for k in (lab["uid_back"], lab["owner_uid"], lab["recip_wire"]):
        try:
            vi.SetControlValue(k, 0)
        except Exception:
            pass
    vi.SetControlValue(lab["is_source"], False)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(lab["uid_in"], int(wire_uid))
    vi.SetControlValue(lab["term_index"], int(idx))
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:90]}"
    errs = " ".join(x for x in (g._err(vi, lab[k]) or "" for k in
                                ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO")) if x)
    return dict(wire=int(wire_uid), index=idx,
                uid_back=int(vi.GetControlValue(lab["uid_back"])),
                wire_class=vi.GetControlValue(lab["cls_back"]),
                is_source=bool(vi.GetControlValue(lab["is_source"])),
                owner_class=vi.GetControlValue(lab["ownercls"]),
                owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                recip_wire=int(vi.GetControlValue(lab["recip_wire"])),
                cast_class=vi.GetControlValue(lab["cast_class"]), err=err, errs=errs)


def wire_terminals(target, wire_uid, maxn=8):
    """Every terminal on `wire_uid`, stopping at the end of Wire.Terminals[]."""
    rows = []
    for i in range(maxn):
        r = read_terminal(target, wire_uid, i)
        past = (r["owner_uid"] == 0 and not r["is_source"] and (r["errs"] or r["err"]))
        if past:
            break
        rows.append(r)
        print(f"        w{wire_uid} Terms[{i}] source={r['is_source']} owner {r['owner_class']!r:.24} "
              f"uid {r['owner_uid']} recip w{r['recip_wire']} {r['err'][:30]}", flush=True)
    return rows


def wire_source(target, wire_uid):
    """The ONE terminal on `wire_uid` that is a source and points back at it; None when there is not exactly one."""
    rows = wire_terminals(target, wire_uid)
    srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire_uid]
    return (srcs[0] if len(srcs) == 1 else None), rows


# ---------------------------------------------------------------- locating an owner, OFFLINE (review B4)
# `main_vi_nodeterms.json` holds EVERY diagram's nodes with {i, name, is_source, wire}, and `d1_step0_census.json`
# all 132 LoopTunnels with out_wire/in_wires. So the owner lookup and the tunnel hop cost no LabVIEW call at all -
# only `Wire.Terminals[]` needs the machine, because no census covers non-Node GObjects (constants, control
# terminals, flat-sequence tunnels) by wire.
_NT = None
_TUN = None


def offline():
    global _NT, _TUN
    if _NT is None:
        with open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8") as f:
            nt = json.load(f)
        _NT = {}
        for dk, dv in nt["diagrams"].items():
            for n_i, n in enumerate(dv["nodes"]):
                _NT[n["uid"]] = (int(dk), n.get("n", n_i), n["terms"])
        with open(os.path.join(HERE, "d1_step0_census.json"), encoding="utf-8") as f:
            st0 = json.load(f)
        _TUN = {t["uid"]: t for t in st0.get("tunnels") or []}
        fact(f"offline maps: {len(_NT)} nodes by uid, {len(_TUN)} LoopTunnels by uid")
    return _NT, _TUN


def locate(target, uid):
    """(diagram index, node index, rows) for a node uid - read from main_vi_nodeterms.json, not from LabVIEW."""
    nt, _ = offline()
    if uid in nt:
        d, n, rows = nt[uid]
        return d, n, rows
    return None, None, None


def tunnel_map(target):
    _, tun = offline()
    return tun


def resolve(target, tunnel_uid, outer_wire, max_hops=6):
    """§11r: one hop at a time from Python. Returns the resolution dict."""
    hops = []
    wire = outer_wire
    for hop in range(max_hops):
        src, rows = wire_source(target, wire)
        if src is None:
            return dict(ok=False, why=f"wire {wire}: not exactly one source terminal",
                        hops=hops, terminals=[{k: r[k] for k in ("index", "is_source", "owner_class",
                                                                 "owner_uid", "recip_wire", "err")} for r in rows])
        hops.append(dict(wire=wire, owner_class=src["owner_class"], owner_uid=src["owner_uid"],
                         term_i_on_wire=src["index"]))
        d, n, node_rows = locate(target, src["owner_uid"])
        if d is not None:
            ti = [r["i"] for r in node_rows if r["wire"] == wire and r["is_source"]]
            relaxed = False
            if not ti:                       # reported, not silently accepted: the node's own Terminals[] may
                ti = [r["i"] for r in node_rows if r["wire"] == wire]   # not mark a border terminal as a source
                relaxed = bool(ti)
            if ti:
                return dict(ok=True, diagram=d, node=n, term=ti[0], owner_class=src["owner_class"],
                            owner_uid=src["owner_uid"], is_source_on_node=not relaxed,
                            term_name=next(r["name"] for r in node_rows if r["i"] == ti[0]), hops=hops)
            return dict(ok=False, why=f"owner {src['owner_uid']} located on diagram {d} node {n} but NO "
                                      f"terminal of it carries w{wire}", hops=hops)
        # the owner is not a node on a searched diagram - is it a tunnel? then take ONE more hop
        tm = tunnel_map(target)
        t = tm.get(src["owner_uid"])
        if not t:
            return dict(ok=False, why=f"owner uid {src['owner_uid']} ({src['owner_class']}) is neither a node on "
                                      f"diagrams {DIAGRAMS} nor a LoopTunnel", hops=hops)
        if t["out_wire"] in (0, wire):
            return dict(ok=False, why=f"tunnel {t['uid']} outer wire {t['out_wire']} does not advance the hop",
                        hops=hops)
        wire = t["out_wire"]
    return dict(ok=False, why=f"{max_hops} hops without reaching a locatable owner", hops=hops)


# ---------------------------------------------------------------- the run
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    t0 = time.time()
    gate("G0a original working copy md5 BEFORE", md5(MAIN) == MAIN_MD5, md5(MAIN))
    fresh()
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")

    print("\n=== G1: the op VIs' own ExecState (the 1055 question, MEASURED)", flush=True)
    for p in (V5, g.OP_TUNNELS, os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")):
        try:
            es = g.exec_state(p)
        except Exception as e:
            es = f"EXC {str(e)[:60]}"
        gate(f"G1 {os.path.basename(p)} ExecState 1", es == 1, f"ExecState {es}")

    print("\n=== G2: the published control - wire 10850 on the working copy", flush=True)
    src, rows = wire_source(MAIN, CONTROL_WIRE)
    fact(f"G2 wire {CONTROL_WIRE}: {len(rows)} terminals read, "
         f"{sum(1 for r in rows if r['is_source'])} report Is Source? TRUE; first error "
         f"{(rows[0]['err'] or rows[0]['errs'])[:90]!r}" if rows else "G2 wire 10850: NO terminal rows at all")
    ok2 = gate("G2 the control reproduces: exactly one source terminal whose reciprocal wire is itself",
               src is not None, f"{[(r['index'], r['is_source'], r['owner_uid'], r['recip_wire']) for r in rows]}")
    if src:
        fact(f"G2 source owner {src['owner_class']} uid {src['owner_uid']} = "
             f"{CONTROL_OWNERS.get(src['owner_uid'], 'neither previous claim')}")

    print("\n=== G3/G4: the from-tunnel rows, one hop at a time", flush=True)
    with open(ROWS_IN, encoding="utf-8") as f:
        data = json.load(f)
    ft = [r for r in data["rows"] if r.get("action") == "from-tunnel"]
    fact(f"{len(ft)} from-tunnel rows; {sum(1 for r in ft if not r.get('outer_source'))} carry outer_source null")
    out = []
    if ok2:
        for r in ft:
            print(f"    row #{r['uid']} t{r['i']} {r['name']!r} <- tunnel #{r['source']['uid']} "
                  f"outer w{r['outer_wire']}", flush=True)
            res = resolve(MAIN, r["source"]["uid"], r["outer_wire"])
            res.update(sink_uid=r["uid"], sink_term=r["i"], sink_name=r["name"], dest=r["dest"],
                       tunnel_uid=r["source"]["uid"], outer_wire=r["outer_wire"],
                       census_outer_source=r.get("outer_source"))
            out.append(res)
            print(f"      => {'RESOLVED' if res['ok'] else 'UNRESOLVED'} "
                  f"{ {k: res[k] for k in ('diagram', 'node', 'term', 'owner_class', 'owner_uid', 'term_name')} if res['ok'] else res['why']}",
                  flush=True)
    else:
        fact("G3/G4 SKIPPED - the back half failed its own control, so a resolution would not be evidence")

    n_ok = sum(1 for r in out if r["ok"])
    # G3: the three cross-checkable rows
    checks = []
    for res in out:
        cs = res.get("census_outer_source")
        if res["ok"] and cs and cs.get("kind") == "node":
            agree = (res["owner_uid"] == cs["uid"])
            checks.append((res["sink_uid"], res["sink_term"], res["owner_uid"], cs["uid"], agree))
    for c in checks:
        fact(f"G3 cross-check #{c[0]} t{c[1]}: one-hop owner {c[2]} vs census outer_source {c[3]} "
             f"{'AGREE' if c[4] else 'DISAGREE'}")
    if out:
        gate("G3 every row that HAS a census outer_source agrees with the one-hop read",
             bool(checks) and all(c[4] for c in checks), f"{len(checks)} cross-checks")
        gate("G4 at least 3 from-tunnel rows resolve to a (diagram, node, terminal) triple", n_ok >= 3,
             f"{n_ok} of {len(out)} resolved")
        gate("G4b ALL from-tunnel rows resolve", n_ok == len(out), f"{n_ok}/{len(out)}")
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"rows": out, "control": {"wire": CONTROL_WIRE, "source": src, "terminals": rows},
                   "diagrams_searched": list(DIAGRAMS)}, f, indent=1, default=str)
    fact(f"G5 wrote {OUT} ({n_ok}/{len(out)} resolved)")
    gate("G6 original working copy md5 AFTER", md5(MAIN) == MAIN_MD5, md5(MAIN))
    fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
    print("\n--- FACTS ---", flush=True)
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== diag_tunnelsource_onehop: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
