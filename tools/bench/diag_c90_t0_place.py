r"""diag_c90_t0_place - card 90-4 B (placement check): can `build_clfn` put a stamp CLFN INSIDE a nested loop body of S1?
MEASURED on a throwaway byte copy of D1_s1_copy.vi (scratch_c90_place_<ts>.vi, deleted at close). Nothing is saved.

FOUND FIRST: gscript.build_clfn (OpCLFNBuild_v0: PN `VI.Block Diagram` -> NI Create.vi(diagram, position) - it has NO diagram
parameter; the `Class Name`/`index` controls are the donor OpBuildIA_v0's leftover Traverse chain, build_opclfn.py:11-12,152),
stagekit.Stage.move_in (build_d1_v0.move_in:318 = OpMoveIn_v0, uid -> Diagram[index], the verb L2-A1 used for 14 moves),
build_d1_m3a1.find_node (which diagram lists a uid, uid echo), diag_c90_t0stamp_scratch.py FLAT_STAMP (the 3-param stamp record).
S1 diagram indices from the offline table (t0_sites_s1.json): 43 = #639 frame loop #637 body; 99 = #15266 display loop #15173 body.

PREDICTION CONTRACT: PL1 build_clfn at a location inside loop #637's bounds creates 1 CallLibrary and find_node lists it on
diagram index 0 (top level) - the op owns no diagram parameter; PL2 move_in(uid, 43, pos) then lists it on index 43 (#639) with
uid echo; PL3 a second CLFN moved into index 99 (#15266) lists there; PL4 the moved node keeps 3 parameter terminals
(node_terms_uid rows >= 4); + stagekit H gates (scratch deleted, pins, refs), then COM Quit and LabVIEW verified gone (Q1).
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu")); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import stagekit as K                                                             # noqa: E402
import gscript as g                                                              # noqa: E402
import clfn_params as cp                                                         # noqa: E402
import struct                                                                    # noqa: E402

DLL = os.path.join(K.CLAUDEDEV, "t0stamp.dll")
SRC = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); SRC_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
EXTRA = [("kswap", os.path.join(K.CLAUDEDEV, "D1_s1_kswap_20260926_004935.vi")), ("L2-A1 bed", os.path.join(K.CLAUDEDEV, "D1_l2_a1_20260925_235224.vi"))]
PINS = tuple(K.DEFAULT_PINS) + tuple((n, p, K.md5(p)) for n, p in EXTRA)
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "t0_sites_s1_place.json")
s = K.Stage(SRC, SRC_MD5, "diag_c90_t0_place", work_name="scratch_c90_place_%s.vi" % STAMP, pins=PINS, preload=False, deadline_min=30,
            out_json=OUT, task="card 90-4 B placement check")
TARGETS = [(43, 639, (1200, 900)), (99, 15266, (1200, 900))]


def rec(name, kind, num, passing, dims, const=0):
    r = cp.record(name, kind, num, passing, dims); return r[:-5] + bytes([const]) + r[-4:]


FLAT_STAMP = (struct.pack(">i", 3) + rec("return value", "num", "I32", "value", 0) + rec("site", "num", "I32", "value", 0)
              + rec("any", "any", None, "value", 0, const=1)).hex()


def where(uid, hints, tag):
    M = K.mod("build_d1_m3a1")
    loc = M.find_node(s.work, uid, list(hints), tag, quiet=True)
    f = loc.get("found") or {}
    s.fact("%s #%d lives on Diagram idx %r uid %r (Nodes[%r]) after scanning %d diagrams" % (tag, uid, f.get("diagram_index"), f.get("diagram_uid"), f.get("nodes_index"), len(loc.get("scanned", []))))
    return f


def body(_stage):
    W = s.start(); s.discard_work(); s.es("after open")
    s.head("[1] build_clfn on the S1 scratch (top-level op), then move_in to loop bodies")
    res = []
    for k, (idx, duid, pos) in enumerate(TARGETS):
        inv0 = g.uids(W, "Invoke")
        u, nt, e = g.build_clfn(W, (200 + 400 * k, 100), DLL, "stamp", FLAT_STAMP)
        for o in g.new_since(W, "Invoke", inv0):
            ids = [x["uid"] for x in g.report(W, "Invoke")]
            if o["uid"] in ids:
                g.delete_object(W, "Invoke", ids.index(o["uid"]))
        f0 = where(u, [0, idx], "PL%d-before" % (1 + 2 * k))
        if k == 0:
            s.gate("PL1 build_clfn creates 1 CallLibrary (%d terms) and it lists on diagram index 0 (no diagram param)" % nt, f0.get("diagram_index") == 0, "errs %r" % (e,))
        r = s.move_in(u, idx, pos)
        f1 = where(u, [idx, 0], "PL%d-after" % (2 + 2 * k))
        s.gate("PL%d move_in(#%d -> Diagram[%d] = #%d) lists the node there" % (2 + 2 * k if k == 0 else 3, u, idx, duid), f1.get("diagram_index") == idx and f1.get("diagram_uid") == duid, "err %r found %r" % (r.get("err"), f1))
        if f1.get("nodes_index") is not None:
            echo, rows = g.node_terms_uid(W, idx, f1["nodes_index"])
            s.gate("PL4 moved CLFN #%d keeps its terminals (echo %r, %d rows)" % (u, echo, len(rows)), echo == u and len(rows) >= 4)
        res.append({"clfn_uid": u, "n_terms": nt, "built_on_index": f0.get("diagram_index"), "moved_to_index": idx, "diagram_uid": duid, "found_after": f1, "move_err": r.get("err")})
    s.R["placement"] = res
    s.head("[2] owner-chain walk (build_d1_v0.owner_of, strict uid echo) for the tunnel-tree gap diagrams - review c90-sites-p2-treegap test")
    V = K.mod("build_d1_v0"); chains = {}
    for start, why in ((639, "positive control: expect WhileLoop #637"), (3121, "sites #6216/#5987"), (686, "site #6384; loop #637 sits on it"), (15041, "loop #15173 sits on it")):
        chain, uid, hops = [], start, 0
        while hops < 14:
            try:
                cls, ou = V.owner_of(W, uid, strict=True)
            except Exception as e:                                                   # noqa: BLE001
                chain.append({"uid": uid, "err": str(e)[:160]}); break
            chain.append({"uid": uid, "owner_class": cls, "owner_uid": ou}); hops += 1
            if not ou or cls in ("TopLevelDiagram", "VI", "") or ou == uid:
                break
            uid = ou
        chains[start] = chain
        s.fact("OWNER CHAIN from #%d (%s): %s" % (start, why, " -> ".join("#%d[%s]" % (c["uid"], c.get("owner_class", c.get("err"))) for c in chain)))
    s.R["owner_chains"] = chains
    s.gate("OC1 positive control: #639's owner is WhileLoop #637", chains[639] and chains[639][0].get("owner_class") == "WhileLoop" and chains[639][0].get("owner_uid") == 637, repr(chains[639][:1]))
    for start in (3121, 686, 15041):
        whiles = [c for c in chains[start] if c.get("owner_class") == "WhileLoop"]
        s.gate("OC2 chain from #%d reaches the top level; While loops above it: %r" % (start, [c["owner_uid"] for c in whiles]), any(c.get("owner_class") == "TopLevelDiagram" or c.get("owner_uid") == 536 for c in chains[start]), repr(chains[start]))
    s.R["verdict"] = "build_clfn has no diagram parameter (top level only); a nested placement = build_clfn at top level + stagekit.move_in(uid, diagram_index, pos)"


if __name__ == "__main__":
    rc = K.run(body, s)
    s.head("[Q] COM Quit, verify LabVIEW gone")
    r = subprocess.run([sys.executable, "-c", "import win32com.client as w\nw.Dispatch('LabVIEW.Application').Quit()\n"], capture_output=True, text=True, timeout=90)
    t0 = time.time()
    while "labview" in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower() and time.time() - t0 < 60:
        time.sleep(2)
    gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    if not gone:
        subprocess.run(["taskkill", "/F", "/T", "/IM", "LabVIEW.exe"], capture_output=True); time.sleep(5)
        gone = "labview" not in subprocess.run("tasklist", capture_output=True, text=True).stdout.lower()
    s.gate("Q1 LabVIEW gone (quit rc %d, forced=%s)" % (r.returncode, not gone), gone)
    s.gate("Q2 md5 pins after quit", s.pin_check("FINAL")); s.dump()
    sys.exit(s.summary())
