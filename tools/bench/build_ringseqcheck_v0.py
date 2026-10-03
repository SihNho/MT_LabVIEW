r"""build_ringseqcheck_v0.py - card 142-4 (PD330(a), docs/d1/ring-p4b.md:109): claudeDev\RingSeqCheck_v0.vi = plan_ring_p4_v17.json's sequence check
(EQ2 GT2 AND1 DEC1 SLL1 SLD1 INC2, :1297-1520, inner wires :1801-1875; group G5 in prep_c142_p1_subvi_table.md:204-212,228-229).
FOUND FIRST: build_ringpickslot_v2.py (card 142-3, PASS 87/0) is IMPORTED for reg/tr/Wr/mk/dele/kill/canon/peak (every terminal by its own uid, identity re-checked
before use); an I32 control = its 'last' route (helper Less? from the bed byte copy #10950, y <- DonorI32Max_v0 #127, Create Control on x, helper deleted + RBW;
v2.py:80-81, I32 measured v2.log:55). Nodes, donors, prims, terminal names and every wire come from v17 (no re-typed uid or terminal); v17 sources -> panel
names via EXT/OUTN (the brief's names). The Python reference is evaluated over v17's wires (which pin is t/f/s) and its formula printed.
PREDICTION: v17 external wires == brief (n1 -> EQ2.x GT2.x SLL1.t; n2 -> EQ2.y; last -> GT2.y; Latest -> DEC1.x; discards -> INC2.x SLD1.t); 'valid' = AND1 out,
carried to the 7 rollback Selects by p4_rb{A..F,R}_s. Scaffold end: Constant {} Comparison {}, 5 controls unwired. Prim gate: labels == v17 prim; 5 input pins I32;
every wire err ''/unbroken; Constant {}; ExecState 1; pane 11 n1 10 n2 9 last 8 Latest 7 discards | 3 next last 2 next discards 1 valid; formula
next last = (n1 if ((n1 == n2) and (n1 > last)) else (Latest - 1)), next discards = (discards if valid else (discards + 1)); 7 runs == reference
(5,5,4,9,0)->5,0,T (5,5,5,9,0)->8,1,F (5,6,4,9,3)->8,4,F (-1,-1,4,9,0)->8,1,F (25,25,4,30,2)->25,2,T (0,0,-1,0,0)->0,0,T (7,7,6,7,1)->7,1,T;
fresh: md5 same, ExecState 1, vectors 2+5 equal; handles +-100; bed + s01 md5 same; LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_ringseqcheck_v0.log -- py -u tools/bench/build_ringseqcheck_v0.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                    # noqa: E702
import build_ringpickslot_v2 as R2                                                             # noqa: E402 (main() guarded)
D, g, S5, P, BP, gate, fact, md5, Stop, cp = R2.D, R2.g, R2.S5, R2.P, R2.BP, R2.gate, R2.fact, R2.md5, R2.Stop, R2.cp   # noqa: E702
CD, TS, OUT, TU, SCR = g.CLAUDEDEV, time.strftime("%H%M%S"), R2.OUT, R2.TU, R2.SCR             # noqa: E702
TGT = R2.TGT = D.TGT2 = os.path.join(CD, "RingSeqCheck_v0.vi"); BEDD = os.path.join(CD, "scratch_c142_4_bdon_%s.vi" % TS)   # noqa: E702
PL = json.load(open(os.path.join(HERE, "plan_ring_p4_v17.json"), encoding="utf-8")); A = dict((a["id"], a) for a in PL["actions"])   # noqa: E702
NODES = ["p4_eq_seq", "p4_gt_n1", "p4_and", "p4_dec", "p4_sel_last", "p4_sel_disc", "p4_inc_disc"]; AS = dict((A[i]["as"], A[i]) for i in NODES)   # noqa: E702
EXT = {"TN1.outer": "n1", "IAN1.element": "n2", "SL1L.inner": "last", "LRL1.value": "Latest", "SD1L.inner": "discards"}; CTL = ["n1", "n2", "last", "Latest", "discards"]   # noqa: E702
OUTN = {"SLL1.s? t:f": "next last", "SLD1.s? t:f": "next discards", "AND1.x .and. y?": "valid"}; IND = list(OUTN.values())   # noqa: E702
BRIEF = {"n1": ["EQ2.x", "GT2.x", "SLL1.t"], "n2": ["EQ2.y"], "last": ["GT2.y"], "Latest": ["DEC1.x"], "discards": ["INC2.x", "SLD1.t"]}
VEC = [(5, 5, 4, 9, 0), (5, 5, 5, 9, 0), (5, 6, 4, 9, 3), (-1, -1, 4, 9, 0), (25, 25, 4, 30, 2), (0, 0, -1, 0, 0), (7, 7, 6, 7, 1)]
def nt(s): return (s[4:] if s.startswith("new:") else s) if isinstance(s, str) else "#bed"      # noqa: E704 - a bed source/sink is a dict {uid..} in v17 (run 1 log)
WIRES = [a for a in PL["actions"] if a.get("op") == "wire" and (nt(a["src"]).split(".")[0] in AS or nt(a["dst"]).split(".")[0] in AS)]
IN = dict((tuple(nt(w["dst"]).split(".", 1)), nt(w["src"])) for w in WIRES if nt(w["dst"]).split(".")[0] in AS)   # (node, pin) <- source, from v17
F = {"Equal?": lambda v: v["x"] == v["y"], "Greater?": lambda v: v["x"] > v["y"], "And": lambda v: v["x"] and v["y"], "Decrement": lambda v: v["x"] - 1,
     "Increment": lambda v: v["x"] + 1, "Select": lambda v: v["t"] if v["s"] else v["f"]}    # LabVIEW primitive semantics; the pins come from v17
S = {"Equal?": "({x} == {y})", "Greater?": "({x} > {y})", "And": "({x} and {y})", "Decrement": "({x} - 1)", "Increment": "({x} + 1)", "Select": "({t} if {s} else {f})"}
def ev(src, env, sym=False):
    if src in EXT: return EXT[src] if sym else env[EXT[src]]                                   # noqa: E701
    n = src.split(".")[0]; v = dict((p, ev(s, env, sym)) for (m, p), s in IN.items() if m == n)   # noqa: E702
    return S[AS[n]["prim"]].format(**v) if sym else F[AS[n]["prim"]](v)
def dep(n): return 1 + max([dep(s.split(".")[0]) for (m, _p), s in IN.items() if m == n and s.split(".")[0] in AS] or [0])   # noqa: E704
def plan_checks():
    got = dict((k, sorted("%s.%s" % mp for mp, s in IN.items() if s == src)) for src, k in EXT.items()); OUT["ext"] = got; fact("v17 external inputs (name -> pins)", got)   # noqa: E702
    gate("v17 external input wires == brief (no difference)", got == dict((k, sorted(v)) for k, v in BRIEF.items()), (got, BRIEF), need=False)
    gate("every group input pin is fed by a group node or EXT", all(s in EXT or s.split(".")[0] in AS for s in IN.values()), IN)
    vo = OUT["valid_wires"] = [(w["id"], nt(w["dst"])) for w in WIRES if nt(w["src"]) == "AND1.x .and. y?" and nt(w["dst"]).split(".")[0] not in AS]; fact("v17 wires carrying valid out of the group", vo)   # noqa: E702
    gate("valid reaches the 7 rollback Selects' s (p4_rb*_s)", sorted(d for _i, d in vo) == ["RB%d.s" % k for k in range(1, 8)], vo)
    outs = sorted(set(nt(w["src"]) for w in WIRES if nt(w["src"]).split(".")[0] in AS and nt(w["dst"]).split(".")[0] not in AS)); gate("group outputs == OUTN", outs == sorted(OUTN), outs)   # noqa: E702
    OUT["formula"] = dict((OUTN[o], ev(o, {}, True)) for o in OUTN); fact("REFERENCE FORMULA (from v17 wires)", OUT["formula"])   # noqa: E702
def build():
    shutil.copyfile(R2.BED, BEDD); SCR.append(BEDD); gate("bed byte copy md5 == bed", md5(BEDD) == R2.BEDM)   # noqa: E702
    gate("target does not exist yet", not os.path.exists(TGT), TGT); shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT); SCR.append(TGT); g.open_panel(TGT)   # noqa: E702
    R2.TOP[0] = top = int(g.report_all(TGT, "Diagram")[0]["uid"]); K = cp(top, "const_donor", (40, 40), R2.DMAX); R2.reg(K, "K", R2.KO); PN = {}   # noqa: E702
    for k, nm in enumerate(CTL):    # v2.py:80-81 'last' route, once per control
        H = cp(top, "Less?", (200, 60 + 120 * k), {"donor": BEDD, "uid": 10950}); R2.reg(H, "H", R2.CMP("x < y?")); R2.Wr("scaffold H.y <- K (%s)" % nm, "H.y", "K.")   # noqa: E702
        PN[R2.mk(g.create_control, H, "x", False, nm)] = nm; R2.dele(H, "Comparison"); fact("RBW %s" % nm, g.remove_bad_wires_scripted(TGT))   # noqa: E702
    R2.dele(K, "Constant"); fact("RBW K", g.remove_bad_wires_scripted(TGT)); R = R2.rows(TGT)   # noqa: E702
    SC = OUT["scaffold_end"] = {"const": sorted(g.uids(TGT, "Constant")), "cmp": sorted(g.uids(TGT, "Comparison")), "wires": dict((n, R2.tr(R, n)["wire_uid"]) for n in CTL)}
    gate("scaffold end: Constant {} Comparison {}, 5 controls unwired", SC["const"] == [] and SC["cmp"] == [] and not any(SC["wires"].values()), SC)
    U = OUT["U"] = {}
    for i, aid in enumerate(NODES):
        a = A[aid]; dn = a["donor"]; U[a["as"]] = cp(top, a["prim"], (500 + 220 * (i % 4), 80 + 220 * (i // 4)), {"donor": BEDD if dn["donor"] == "$work" else dn["donor"], "uid": dn["uid"]})   # noqa: E702
        R2.reg(U[a["as"]], a["as"], dict((t["name"], t["is_source"]) for t in a["terminals"]))
    lab = dict((int(x["uid"]), x["label"]) for x in g.node_labels(TGT, 0)); OUT["prim"] = dict((n, lab.get(U[n])) for n in AS); fact("created (as -> uid, label)", (U, OUT["prim"]))   # noqa: E702
    gate("PRIM gate: every created node's label == v17 prim", OUT["prim"] == dict((n, AS[n]["prim"]) for n in AS), OUT["prim"])
    for n in sorted(AS, key=lambda m: (dep(m), m)):                                             # topological: a node's inputs are wired before it feeds anything
        for (m, p), s in sorted(IN.items()):
            if m == n: R2.Wr("%s <- %s" % ("%s.%s" % (m, p), s), "%s.%s" % (m, p), EXT.get(s, s))   # noqa: E701
        for o, nm in OUTN.items():
            if o.split(".")[0] == n: PN[R2.mk(g.create_indicator, U[n], o.split(".", 1)[1], True, nm)] = nm   # noqa: E701 - before the source is branched (v2.py:97-98 order)
    OUT["types"] = dict((k, R2.canon(k)) for k in ("EQ2.x", "EQ2.y", "GT2.y", "DEC1.x", "INC2.x")); fact("input pin types", OUT["types"])   # noqa: E702
    gate("the 5 control-fed pins are I32", all(v[0] == "I32" for v in OUT["types"].values()), OUT["types"])   # no tr() after the relabel below
    OUT["labels"] = [(r["uid"], g.set_control_label(TGT, i, PN[int(r["uid"])])) for i, r in enumerate(g.panel_wiring(TGT)) if int(r["uid"]) in PN]
    pw = OUT["panel"] = [(r["uid"], r["label"], r["indicator"], r["wire"]) for r in g.panel_wiring(TGT)]; fact("panel", pw)   # noqa: E702
    gate("panel == 5 controls + 3 indicators, all wired", sorted((p[1], bool(p[2])) for p in pw) == sorted([(n, False) for n in CTL] + [(n, True) for n in IND]) and all(p[3] for p in pw), pw)
    ws = sorted(set(x["wire_uid"] for x in R2.rows(TGT) if x["wire_uid"])); WI = dict((int(r["uid"]), k) for k, r in enumerate(g.report_all(TGT, "Wire")))
    rle = dict((w, g.wire_remove_loose_ends(TGT, w, index=WI.get(w))) for w in ws); OUT["broken"] = [w for w, r in rle.items() if r.get("broken_before") or r.get("err")]   # noqa: E702
    gate("every wire Is Broken? False (%d wires)" % len(ws), not OUT["broken"], OUT["broken"], need=False)
    lab = dict((int(x["uid"]), x["label"]) for x in g.node_labels(TGT, 0)); fact("node labels (top)", lab)   # noqa: E702
    gate("census: node labels == Equal? 1 Greater? 1 And 1 Decrement 1 Select 2 Increment 1", sorted(v for v in lab.values() if v and v not in CTL + IND) == sorted(a["prim"] for a in AS.values()), sorted(lab.values()), need=False)
    gate("census: no Constant, no For/While", not g.uids(TGT, "Constant") and not g.uids(TGT, "ForLoop") and not g.uids(TGT, "WhileLoop"), need=False)
    es = OUT["es"] = g.exec_state(TGT); gate("ExecState 1", es == 1, es)                      # noqa: E702
    vi = g.op(g.OP_CONPANE_ASSIGN); L = [x for _i, x, _d in g.fp_labels(TGT)]; PANE = dict(zip((11, 10, 9, 8, 7, 3, 2, 1), CTL + IND))   # noqa: E702 - v2.py:114-117
    for slot, l in PANE.items():
        for k, v in (("vi path", TGT), ("index", L.index(l)), ("Terminal Index", slot), ("Names", []), ("Names 2", []), ("Class Name", ""), ("Class Name 2", "")): vi.SetControlValue(k, v)   # noqa: E701
        g._run(vi); gate("pane assign %s -> %s err ''" % (l, slot), not g._err(vi), g._err(vi))   # noqa: E702
    g.save(TGT); SCR.remove(TGT); OUT["pane"] = g.conpane(TGT); OUT["md5"] = md5(TGT); fact("pane read back / saved md5", (OUT["pane"], OUT["md5"]))   # noqa: E702
    gate("pane read back: 5 in (11..7) / 3 out (3..1), others free", OUT["pane"] == {**{k: None for k in range(12)}, **PANE}, OUT["pane"])
def runs(tag, idx):
    vi = g.lv().GetVIReference(TGT, "", False, 0); h = OUT["h_" + tag] = [BP.labview_handles()]; OUT[tag] = []   # noqa: E702
    for k in idx:
        env = dict(zip(CTL, VEC[k])); [vi.SetControlValue(n, v) for n, v in env.items()]; g._run(vi)   # noqa: E702
        got, want = [vi.GetControlValue(n) for n in IND], [ev(o, env) for o in OUTN]; back = dict((n, vi.GetControlValue(n)) for n in CTL); OUT[tag].append((k + 1, VEC[k], want, got, [type(x).__name__ for x in got]))   # noqa: E702
        gate("%s vector %d %s -> %s (got %s)" % (tag, k + 1, VEC[k], want, got), got == want and all(type(x) is int for x in got[:2] + list(back.values())) and back == env, need=False)
    h.append(BP.labview_handles()); gate("%s handles flat over the runs (+-100)" % tag, abs(h[1] - h[0]) <= 100, h, need=False)   # noqa: E702
def main():
    plan_checks(); BP.restart_labview(); g.reset(); time.sleep(3); OUT["h0"] = BP.labview_handles()   # noqa: E702
    gate("bed + s01 md5 before", md5(R2.BED) == R2.BEDM and md5(R2.S01) == R2.S01M); build(); runs("runs", range(7))   # noqa: E702
    OUT["h1"], OUT["peak_mb"] = BP.labview_handles(), R2.peak(); fact("handles h0/h1, peak MB", (OUT["h0"], OUT["h1"], OUT["peak_mb"]))   # noqa: E702
    R2.kill("A"); BP.restart_labview(); g.reset(); time.sleep(3)                               # noqa: E702
    gate("fresh: saved md5 unchanged, ExecState 1", md5(TGT) == OUT["md5"] and g.exec_state(TGT) == 1); runs("fresh", (1, 4))   # noqa: E702
if __name__ == "__main__":
    try: main()                                                                                 # noqa: E701
    except Stop as e: print("STOP at the first unexpected result: %s" % e, flush=True)         # noqa: E701
    except Exception as e: traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)   # noqa: E701,E702,BLE001
    finally:
        R2.kill("Z"); [os.path.exists(p) and os.remove(p) for p in SCR]; bad = [k for k, v in S5.G.items() if not v]; FL = TGT[:-3] + "_c142_4_FAIL_%s.vi" % TS   # noqa: E702
        if bad and OUT.get("md5") and os.path.exists(TGT): os.replace(TGT, FL); fact("OUR saved file moved aside (a gate failed)", FL)   # noqa: E701,E702
        gate("scratch files deleted; bed + s01 md5 unchanged", not any(os.path.exists(p) for p in SCR) and md5(R2.BED) == R2.BEDM and md5(R2.S01) == R2.S01M, SCR, need=False)
        json.dump(OUT, open(os.path.join(HERE, "diag_c142_4_out.json"), "w", encoding="utf-8"), indent=1, default=str); bad = [k for k, v in S5.G.items() if not v]   # noqa: E702
        json.dump({"function": "RingSeqCheck_v0 subVI build + run", "card": "142-4", "t": time.time(), "log": "tools/bench/build_ringseqcheck_v0.log", "status": "FAIL" if bad else "PASS", "out": OUT}, open(os.path.join(HERE, "scratch_verify", "ringseqcheck_c142_4_%s.json" % TS), "w", encoding="utf-8"), indent=1, default=str)
        arts = [{"path": TGT, "md5": md5(TGT)}] if os.path.exists(TGT) else []; print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)   # noqa: E702
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True); sys.exit(1 if bad else 0)   # noqa: E702
