r"""diag_stop_save_seam.py - cycle 15 step 1(b)+(c): the original's STOP path, its FILE WRITER, its SHUTDOWN
nodes, and the exact per-frame TRACKER SEAM in diagram 43. Read-only on the main VI (rule 1d).

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "before creating any new op, tool or recipe"):
  * `tools/bench/main_vi_nodeterms.json` (2026-09-14, 626 nodes / 3328 terminals) ALREADY holds every node's
    terminal list with name / is_source / wire uid for all 170 diagrams. The main VI's md5 is unchanged since
    (2a78e17c449cacdaf5da389818526859), so that census is CURRENT and is used as the offline half of this run.
    Nothing it answers is re-measured here.
  * `tools/bench/diagram_tree_main.json` gives diagram index -> owner class + node uid list (offline).
  * `docs/main-vi-panel-map.md:280,329` gives the two stop controls (`stop (end)` uid 7 wire 6929;
    `stop (end) 2` uid 19587 wire 15230) - not re-read.
  * `docs/main-vi-subvi-identity.md:59,68,90,105` gives `save N xyz traces.vi` #6384 on diagram 19 and the
    shutdown calls on diagram 83 - confirmed here with `subvis()`, not re-derived.
  * `OpWireSource_v5.vi` (wire uid -> the object that DRIVES it, 12/12) and `OpOwnerChain_v1.vi` (any uid -> its
    owner, 20/20) are BUILT; their drivers `read_terminal` / `read_owner` are imported VERBATIM. NO new op.
  * `g.subvis(target, diagram_index)` is the cast-free subVI identity reader. NO new reader.

WHY ANY LabVIEW RUN IS NEEDED AT ALL: the offline census resolves a wire only when BOTH of its ends are node
terminals. A wire that crosses a structure border is TWO Wire objects, and a control terminal that is not in
Nodes[] leaves the other end blank. 19 wires on the stop / save / shutdown / tracker paths have exactly one end
in the census; `OpWireSource_v5`'s reciprocal `Connected Wire` is the only reader that resolves those.

PREDICTION CONTRACT (machine-checked; a miss is a failed prediction and owes a peer review):
  P1  `subvis(MAIN, 43)` contains uid 5058 and its name is `Track N beads four-fold over-kernel-v3.vi`
      (frame-loop-anatomy.md; test_opsubvis_v1.log).
  P2  `subvis(MAIN, 19)` contains uid 6384 named `save N xyz traces.vi`.
  P3  `subvis(MAIN, 83)` contains 1839 / 2078 (IMAQdx Stop Acquisition / Close Camera) and 29815 (ASI Close).
  P4  every wire read returns EXACTLY ONE terminal with `Is Source?` TRUE whose reciprocal `Connected Wire` is
      the wire asked about, and `cast_class == owner_class` on every terminal (the v5 identity check).
  P5  `read_owner(22082)` - the node that wire 15229 feeds - returns a class that is a loop CONDITIONAL terminal
      (`ConditionalTerminal` or similar Terminal class), and its owner chain reaches WhileLoop #637.
  P6  `read_owner(11639)` and `read_owner(17883)` (the two `result`/`value` GrowableFunctions the two stop
      controls feed) both own-chain to the diagram whose owner is WhileLoop #637.
  P7  MAIN md5 is 2a78e17c449cacdaf5da389818526859 before AND after.
A miss on P5 is reported as a fact, not repaired here.

This script REPORTS. Which tracker D1 should be built from, and whether the stop path may be reused as-is, are
JUDGEMENT and are deliberately not written here (CLAUDE.md 3, result-dependent actions).

  MATERIAL=1 py tools/bgrun.py --max-min 28 --log tools/bench/diag_stop_save_seam.log -- py -u tools/bench/diag_stop_save_seam.py
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh  # noqa: E402
from build_opwiresource_v5 import OP as OP_WIRE, MAP_OUT, read_terminal  # noqa: E402
from build_opownerchain_v1 import MAIN, OP as OP_OWNER, read_owner  # noqa: E402

MD5_EXPECTED = "2a78e17c449cacdaf5da389818526859"
CENSUS = os.path.join(HERE, "main_vi_nodeterms.json")
OUT = os.path.join(HERE, "stop_save_seam.json")

# (wire uid, what it is) - ONLY wires the offline census cannot resolve on both ends.
WIRES = [
    # (b)(i) stop path
    (6929,  "panel `stop (end)` (ctl uid 7) -> Or#11639 t2 `value` (diagram 43): who DRIVES it"),
    (15230, "panel `stop (end) 2` (ctl uid 19587) -> Or#17883 t1 `value` (diagram 43): who DRIVES it"),
    (3457,  "Or#11639 `result` -> ? (no second end in the census)"),
    (15229, "Or#17883 `result` -> node 22082 t0 (unnamed): confirm both ends"),
    # (b)(ii) file writer
    (1920,  "save N xyz traces.vi #6384 `error out` -> ?"),
    # (b)(iii) shutdown, diagram 83
    (1316,  "IMAQ Dispose #2431 `Image` in <- ?"),
    (2134,  "IMAQdx Stop Acquisition #1839 `error out` -> ?"),
    (2129,  "IMAQdx Stop Acquisition #1839 `Session Out` -> ?"),
    (2138,  "IMAQdx Close Camera #2078 `error out` -> ?"),
    (2271,  "`Total Lost Frames` local #2143 -> `x != 0?` #7223"),
    (7291,  "`x != 0?` #7223 -> node 195"),
    # (c) the tracker seam: the 8 terminals of #5058 whose wire has one end only
    (373,   "#5058 t2 `cross size` in"),
    (5859,  "#5058 t3 `Bead is good? array out` OUT"),
    (42,    "#5058 t9 `# of bead 4 packs` in"),
    (3512,  "#5058 t11 `4 pack remainder` in"),
    (3646,  "#5058 t12 `Array of cal clusters` in"),
    (7429,  "#5058 t13 `pos in cal image in` in"),
    (3912,  "#5058 t14 `Real-space cosine window` in"),
    (4027,  "#5058 t15 `Cosine bandpass\\nfor Hilbert ` in"),
]

# (uid, why) - owner chain, one hop; a second hop is taken automatically on the first hop's answer.
OWNERS = [
    (22082, "the node wire 15229 feeds - the suspected loop CONDITIONAL terminal"),
    (11639, "GrowableFunction fed by `stop (end)`"),
    (17883, "GrowableFunction fed by `stop (end) 2`"),
    (5058,  "the tracker call site (expect diagram of WhileLoop#637)"),
    (6384,  "save N xyz traces.vi"),
    (2078,  "IMAQdx Close Camera"),
    (29815, "ASI TG-1000 Close.vi"),
    (637,   "the frame While loop itself"),
]

_gates = []


def gate(label, ok, detail=""):
    _gates.append((label, bool(ok)))
    print(f"  {'PASS' if ok else '-> FAIL'}  {label}{('   ' + detail) if detail else ''}", flush=True)
    return bool(ok)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def offline_index():
    """wire uid -> [(diagram, node uid, term index, name, is_source)] from the 2026-09-14 census."""
    dg = json.load(open(CENSUS, encoding="utf-8"))["diagrams"]
    wires, nodes = {}, {}
    for k, v in dg.items():
        for nd in v["nodes"]:
            nodes[nd["uid"]] = (k, v["owner"], nd)
            for t in nd["terms"]:
                if t["wire"]:
                    wires.setdefault(t["wire"], []).append((k, nd["uid"], t["i"], t["name"], t["is_source"]))
    return wires, nodes


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    before = md5(MAIN)
    print(f"MAIN md5 before: {before}", flush=True)
    gate("P7a md5 before == recorded", before == MD5_EXPECTED, before)
    wires_off, nodes_off = offline_index()
    labels = json.load(open(MAP_OUT, encoding="utf-8"))
    out = {"md5_before": before, "subvis": {}, "wires": [], "owners": [], "offline": {}}

    fresh()
    try:
        # --- identity confirmations -------------------------------------------------
        for di, expect in ((43, {5058: "Track N beads four-fold over-kernel-v3.vi"}),
                           (19, {6384: "save N xyz traces.vi"}),
                           (83, {1839: "IMAQdx Stop Acquisition.vi", 2078: "IMAQdx Close Camera.vi",
                                 29815: "Close.vi"})):
            rows = g.subvis(MAIN, di)
            out["subvis"][di] = rows
            print(f"SUBVIS diagram {di}: " + " | ".join(f"#{r['uid']} {r['name']}" for r in rows), flush=True)
            byuid = {r["uid"]: r["name"] for r in rows}
            for u, nm in expect.items():
                gate(f"P{1 if di == 43 else (2 if di == 19 else 3)} diagram {di} has #{u} ~ {nm!r}",
                     u in byuid and nm.lower() in byuid[u].lower(), str(byuid.get(u)))

        # --- wire sources -----------------------------------------------------------
        vi = g.op(OP_WIRE)
        for w, why in WIRES:
            rows = []
            for i in range(8):
                r = read_terminal(vi, labels, w, i)
                if r["errs"] and r["owner_uid"] == 0:
                    break
                rows.append(r)
            srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == w]
            sinks = [(r["owner_class"], r["owner_uid"]) for r in rows if not r["is_source"]]
            ident = bool(rows) and all(r["cast_class"] == r["owner_class"] for r in rows)
            gate(f"P4 wire {w}: exactly one source, identity checks OK", len(srcs) == 1 and ident,
                 f"srcs={len(srcs)} ident={ident}")
            src = (srcs[0]["owner_class"], srcs[0]["owner_uid"]) if srcs else None
            print(f"RESULT wire {w} ({why}): driven by {src}; sinks {sinks}", flush=True)
            out["wires"].append(dict(wire=w, why=why, source=src, sinks=sinks, ident=ident,
                                     offline=wires_off.get(w, []), rows=rows))

        # --- owner chains -----------------------------------------------------------
        vi2 = g.op(OP_OWNER)
        for u, why in OWNERS:
            h1 = read_owner(vi2, labels, u)
            h2 = read_owner(vi2, labels, h1["owner_uid"]) if h1["owner_uid"] else None
            print(f"RESULT owner chain {u} ({why}): {h1['cls_back']!r}#{u} -> {h1['ownercls']!r}#{h1['owner_uid']}"
                  + (f" -> {h2['ownercls']!r}#{h2['owner_uid']}" if h2 else ""), flush=True)
            out["owners"].append(dict(uid=u, why=why, hop1=h1, hop2=h2))
        by = {r["uid"]: r for r in out["owners"]}
        for u in (11639, 17883, 22082):
            r = by.get(u)
            if r:
                gate(f"P5/P6 uid {u} own-chains to WhileLoop#637",
                     bool(r["hop2"]) and r["hop2"]["owner_uid"] == 637,
                     f"hop1={r['hop1']['ownercls']}#{r['hop1']['owner_uid']} "
                     f"hop2={(r['hop2'] or {}).get('ownercls')}#{(r['hop2'] or {}).get('owner_uid')}")
        r = by.get(22082)
        if r:
            gate("P5 node 22082 is a terminal-like class (conditional terminal)",
                 "erminal" in str(r["hop1"]["cls_back"]), str(r["hop1"]["cls_back"]))
    finally:
        after = md5(MAIN)
        out["md5_after"] = after
        gate("P7b MAIN md5 unchanged", after == before, after)
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1, default=str)
        npass = sum(1 for _, ok in _gates if ok)
        print(f"SUMMARY {npass}/{len(_gates)} gates pass; "
              f"failing: {[n for n, ok in _gates if not ok]}", flush=True)
        print(f"MAIN md5 after: {after}", flush=True)
    return 0 if all(ok for _, ok in _gates) else 1


if __name__ == "__main__":
    sys.exit(main())
