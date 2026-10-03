r"""build_ringpickslot_v0.py - card 142-1: claudeDev\RingPickSlot_v0.vi = plan v17's slot-selection group (GT1 FMN1 SW1 KMX1 KMX2
AMM1 LT1 and their wires, plan_ring_p4_v17.json:945-1126 + 1578-1689) as its own subVI, RUN on 7 vectors, 2 re-run from disk fresh.
FOUND FIRST: helpers/donors as diag_c140_5_run.py (cp = create_primitive_nested; top-level create_control/create_indicator by node
index); For-border wiring by connect_term_uid (diag_c138_6_run.py:116-119, 139-3 3 tunnels IndexMode 1); a 1-D I32 control = generator
For -> Greater?.y then create_control on .x (diag_c140_5_run.py:40-44) - the generator For + its N constant are DELETED after
(delete_object + remove_bad_wires_scripted, diag_c138_6_run.py:77). A SCALAR I32 `last`: Create Control on Greater?.y after x is an array
gives an ARRAY (diag_c139_3_facts.md:29), so `last` = create_control on .x of a helper Less? whose y holds KMX2 (I32), helper deleted.
Pane: EMPTY_v0 = 12 free slots (replay_vis_76c_skeleton.log:60); IMAQdx Get Image's map there puts slots 11/10 left-top, 3/2/1 right-top.
PREDICTION: every wire err '' / broken False; no ForLoop/Constant left after the scaffold delete; census Greater? 1, Less? 1, Select 1,
Array Max & Min 1, For 1, Constant 2 (I32 2147483647 each); prim labels == plan prims; ExecState 1; pane 11 Num 10 last 3 min Num 2 min
slot 1 found; saved by COM; 7 runs == Python ref; fresh instance: ExecState 1, vectors 2 and 5 equal; bed + s01 md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_ringpickslot_v0.log -- py -u tools/bench/build_ringpickslot_v0.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                    # noqa: E702
import diag_c138_6_run as D                                                                    # noqa: E402 (main() guarded)
S5, g, TB, P, BP = D.S5, D.g, D.TB, D.P, D.bench_prep                                           # noqa: E702
gate, fact, md5, Stop, rows, one, cp = D.gate, D.fact, D.md5, D.Stop, D.rows, D.one, D.cp       # noqa: E702
CD, BED, BEDM, TS, MAXV = g.CLAUDEDEV, S5.BED, S5.BED_MD5, time.strftime("%H%M%S"), 2147483647  # noqa: E702
S01, S01M = os.path.join(CD, "D1_ring_p4s01_20261002_232547.vi"), "dc61e193e0376ce760f88fdfcda7087b"   # noqa: E702
TGT = D.TGT2 = os.path.join(CD, "RingPickSlot_v0.vi"); BEDD = os.path.join(CD, "scratch_c142_1_bdon_%s.vi" % TS)   # noqa: E702
SEL, DMAX = {"donor": D.SEL_D, "uid": 529}, {"donor": D.DON, "uid": 127}; OUT, SCR = {"runs": [], "fresh": []}, S5.SCR   # noqa: E702
R3 = [20, 21, 22] + list(range(3, 20)); R5 = [-1, 21, 22] + list(range(3, 20)); I20 = list(range(20))   # noqa: E702
VEC = [([-1] * 20, -1), (I20, 4), (R3, 5), (R3, 19), (R5, 20), (R5, 22), (I20, 19)]
def ref(num, last):
    m = [n if n > last else MAXV for n in num]; return [min(m), m.index(min(m)), min(m) < MAXV]   # noqa: E702
def peak(): return S5.subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process LabVIEW | Select-Object -First 1).PeakWorkingSet64/1MB"], capture_output=True, text=True).stdout.strip()   # noqa: E704
def ti(u, name, src): return next(r["i"] for r in g.node_terms_uid(TGT, 0, TB.walk(TGT, 0)[u][0])[1] if r["name"] == name and bool(r["is_source"]) == src)   # noqa: E704
def mk(fn, u, name, src, tag):   # top-level route by node index (diag_c140_5_run.py:49-53); panel uid by panel_wiring diff
    p0 = set(int(r["uid"]) for r in g.panel_wiring(TGT)); r = fn(TGT, TB.walk(TGT, 0)[u][0], ti(u, name, src))   # noqa: E702
    np_ = [x for x in g.panel_wiring(TGT) if int(x["uid"]) not in p0]; OUT[tag] = {"ret": r, "panel": np_}; fact("PANEL %s" % tag, OUT[tag])   # noqa: E702
    gate("panel object %s created and wired" % tag, len(np_) == 1 and bool(np_[0]["wire"]), np_); return int(np_[0]["uid"])   # noqa: E702
def Wr(tag, snk, src):
    r = g.connect_term_uid(TGT, snk, src); OUT.setdefault("wires", {})[tag] = r; fact("WIRE %s" % tag, r)   # noqa: E702
    gate("wire %s err '' and Is Broken? False" % tag, not r.get("err") and r.get("broken") is False, r); return rows(TGT)   # noqa: E702
def kill(tag):
    g.reset(); S5.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)   # noqa: E702
    gate("%s LabVIEW gone" % tag, "labview.exe" not in S5.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)
def delete(u, cls):
    gone = g.delete_object(TGT, cls, g._uid_index(TGT, cls, u)); fact("DELETE #%s %s" % (u, cls), gone); return gone   # noqa: E702
def build():
    shutil.copyfile(BED, BEDD); SCR.append(BEDD); gate("bed byte copy md5 == bed", md5(BEDD) == BEDM)   # noqa: E702
    gate("target does not exist yet", not os.path.exists(TGT), TGT); shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT); SCR.append(TGT); g.open_panel(TGT)   # noqa: E702
    top = int(g.report_all(TGT, "Diagram")[0]["uid"]); d0, f0 = g.uids(TGT, "Diagram"), g.uids(TGT, "ForLoop")   # noqa: E702
    g.for_loop(TGT, (60, 520)); FG = sorted(g.uids(TGT, "ForLoop") - f0)[0]; fgb = sorted(g.uids(TGT, "Diagram") - d0)[0]   # noqa: E702
    g.create_const_loop_term(TGT, "for_n", TB.walk(TGT, 0)[FG][0], value=20); k0 = cp(fgb, "const_donor", (40, 40), {"donor": D.I0_D, "uid": 248})   # noqa: E702
    GT = cp(top, "Greater?", (300, 150), {"donor": BEDD, "uid": 11721})
    Wr("scaffold GT.y <- k0 (generator For out)", one(rows(TGT), owner_uid=GT, term_name="y")["term_uid"], one(rows(TGT), owner_uid=k0, is_source=True)["term_uid"])
    pn = mk(g.create_control, GT, "x", False, "Num")
    delete(FG, "ForLoop"); [delete(u, "Constant") for u in sorted(g.uids(TGT, "Constant"))]; fact("RBW 1", g.remove_bad_wires_scripted(TGT))   # noqa: E702
    R = rows(TGT); gate("scaffold gone: no ForLoop, no Constant, GT.y unwired, GT.x wired", not g.uids(TGT, "ForLoop") and not g.uids(TGT, "Constant")
                        and not one(R, owner_uid=GT, term_name="y")["wire_uid"] and one(R, owner_uid=GT, term_name="x")["wire_uid"])
    KMX2, H = cp(top, "const_donor", (900, 330), DMAX), cp(top, "Less?", (300, 650), {"donor": BEDD, "uid": 10950})   # noqa: E702
    Wr("scaffold H.y <- KMX2", one(rows(TGT), owner_uid=H, term_name="y")["term_uid"], one(rows(TGT), owner_uid=KMX2, is_source=True)["term_uid"])
    pl = mk(g.create_control, H, "x", False, "last")
    R = rows(TGT); lo = one(R, wire_uid=one(R, owner_uid=H, term_name="x")["wire_uid"], is_source=True)["owner_uid"]   # noqa: E702
    delete(H, one(R, owner_uid=H, term_name="y")["owner_class"]); fact("RBW 2", g.remove_bad_wires_scripted(TGT)); R = rows(TGT)   # noqa: E702
    gate("helper gone: KMX2 and the last control unwired", not one(R, owner_uid=KMX2, is_source=True)["wire_uid"] and not one(R, owner_uid=lo, is_source=True)["wire_uid"])
    R = Wr("GT.y <- last", one(R, owner_uid=GT, term_name="y")["term_uid"], one(R, owner_uid=lo, is_source=True)["term_uid"])
    num = one(R, wire_uid=one(R, owner_uid=GT, term_name="x")["wire_uid"], is_source=True)["term_uid"]
    d1, f1 = g.uids(TGT, "Diagram"), g.uids(TGT, "ForLoop"); g.for_loop(TGT, (480, 300))         # noqa: E702
    FMN = sorted(g.uids(TGT, "ForLoop") - f1)[0]; fmb = sorted(g.uids(TGT, "Diagram") - d1)[0]  # noqa: E702
    SW, KMX1 = cp(fmb, "Select", (120, 80), SEL), cp(fmb, "const_donor", (20, 140), DMAX)       # noqa: E702
    AMM, LT = cp(top, "Array Max & Min", (800, 150), {"donor": BEDD, "uid": 10969}), cp(top, "Less?", (1050, 150), {"donor": BEDD, "uid": 10950})   # noqa: E702
    B = OUT["B"] = {"top": top, "GT": GT, "KMX2": KMX2, "FMN": FMN, "fmb": fmb, "SW": SW, "KMX1": KMX1, "AMM": AMM, "LT": LT}; fact("created", B)   # noqa: E702
    R = Wr("SW.t <- Num (FMN in)", one(R, owner_uid=SW, term_name="t")["term_uid"], num)
    R = Wr("SW.s <- GT out (FMN in)", one(R, owner_uid=SW, term_name="s")["term_uid"], one(R, owner_uid=GT, is_source=True)["term_uid"])
    R = Wr("SW.f <- KMX1", one(R, owner_uid=SW, term_name="f")["term_uid"], one(R, owner_uid=KMX1, is_source=True)["term_uid"])
    R = Wr("AMM.array <- SW out (FMN out)", one(R, owner_uid=AMM, term_name="array")["term_uid"], one(R, owner_uid=SW, is_source=True)["term_uid"])
    pm, ps = mk(g.create_indicator, AMM, "min value", True, "min Num"), mk(g.create_indicator, AMM, "min index (indices)", True, "min slot")   # noqa: E702
    R = Wr("LT.y <- KMX2", one(rows(TGT), owner_uid=LT, term_name="y")["term_uid"], one(rows(TGT), owner_uid=KMX2, is_source=True)["term_uid"])
    R = Wr("LT.x <- AMM.min value", one(R, owner_uid=LT, term_name="x")["term_uid"], one(R, owner_uid=AMM, term_name="min value")["term_uid"])
    pf = mk(g.create_indicator, LT, "x < y?", True, "found"); want = {pn: "Num", pl: "last", pm: "min Num", ps: "min slot", pf: "found"}   # noqa: E702
    OUT["labels"] = [(r["uid"], g.set_control_label(TGT, i, want[int(r["uid"])])) for i, r in enumerate(g.panel_wiring(TGT)) if int(r["uid"]) in want]
    pw = OUT["panel"] = [(r["uid"], r["label"], r["indicator"], r["wire"]) for r in g.panel_wiring(TGT)]; fact("panel", pw)   # noqa: E702
    gate("panel == {Num, last} controls + {min Num, min slot, found} indicators, all wired", sorted((p[1], bool(p[2])) for p in pw) == sorted(
        [("Num", False), ("last", False), ("min Num", True), ("min slot", True), ("found", True)]) and all(p[3] for p in pw), pw)
    ws = sorted(set(x["wire_uid"] for x in rows(TGT) if x["wire_uid"])); WI = dict((int(r["uid"]), k) for k, r in enumerate(g.report_all(TGT, "Wire")))
    rle = dict((w, g.wire_remove_loose_ends(TGT, w, index=WI.get(w))) for w in ws); OUT["broken"] = [w for w, r in rle.items() if r.get("broken_before")]   # noqa: E702
    gate("every wire Is Broken? False (%d wires)" % len(ws), not OUT["broken"], OUT["broken"], need=False)
    lab = dict((int(x["uid"]), x["label"]) for di in (0, g._uid_index(TGT, "Diagram", fmb)) for x in g.node_labels(TGT, di))
    OUT["prim"] = dict((k, lab.get(B[k])) for k in ("GT", "SW", "AMM", "LT")); fact("node labels (all diagrams)", lab)   # noqa: E702
    gate("PRIM gate: GT Greater? / SW Select / AMM Array Max & Min / LT Less?", OUT["prim"] == {"GT": "Greater?", "SW": "Select", "AMM": "Array Max & Min", "LT": "Less?"}, OUT["prim"])
    cs = OUT["consts"] = dict((u, g.read_const_value(TGT, u)) for u in sorted(g.uids(TGT, "Constant"))); fact("constants", cs)   # noqa: E702
    lt = OUT["tunnels"] = [(t["uid"], t["index_mode"]) for t in (g.tunnels(TGT, k) for k in range(len(g.report_all(TGT, "LoopTunnel"))))]   # noqa: E702
    fact("LoopTunnels (uid, IndexMode)", lt); gate("3 LoopTunnels, IndexMode 1 each", len(lt) == 3 and all(t[1] == 1 for t in lt), lt, need=False)   # noqa: E702
    gate("census: For 1, Constant 2 = I32 2147483647", len(g.uids(TGT, "ForLoop")) == 1 and sorted(cs) == sorted([KMX1, KMX2]) and all(
        v.get("value") == MAXV and (v.get("type") or {}).get("repr_name") == "I32" for v in cs.values()), cs, need=False)
    gate("census: 1 each of Greater?/Less?/Select/Array Max & Min, no other function", sorted(v for v in lab.values() if v not in want.values() and v) == sorted(
        ["Array Max & Min", "Greater?", "Less?", "Select"]) or fact("census other labels", lab), sorted(lab.values()), need=False)
    es = OUT["es"] = g.exec_state(TGT); gate("ExecState 1", es == 1, es)                      # noqa: E702
    vi = g.op(g.OP_CONPANE_ASSIGN); L = [x for _i, x, _d in g.fp_labels(TGT)]                # noqa: E702 - diag_replay_skeleton.py:38-49
    for slot, l in ((11, "Num"), (10, "last"), (3, "min Num"), (2, "min slot"), (1, "found")):
        for k, v in (("vi path", TGT), ("index", L.index(l)), ("Terminal Index", slot), ("Names", []), ("Names 2", []), ("Class Name", ""), ("Class Name 2", "")):
            vi.SetControlValue(k, v)
        g._run(vi); gate("pane assign %s -> %s err ''" % (l, slot), not g._err(vi), g._err(vi))   # noqa: E702
    g.save(TGT); SCR.remove(TGT); OUT["pane"] = g.conpane(TGT); fact("pane read back", OUT["pane"])   # noqa: E702
    gate("pane read back: 11 Num, 10 last, 3 min Num, 2 min slot, 1 found, others free", OUT["pane"] == {**{k: None for k in range(12)}, 11: "Num", 10: "last", 3: "min Num", 2: "min slot", 1: "found"}, OUT["pane"])
    OUT["md5"] = md5(TGT); fact("saved", OUT["md5"])                                          # noqa: E702
def runs(tag, idx):
    vi = g.lv().GetVIReference(TGT, "", False, 0)
    for k in idx:
        num, last = VEC[k]; vi.SetControlValue("Num", num); vi.SetControlValue("last", last); g._run(vi)   # noqa: E702
        got = [vi.GetControlValue("min Num"), vi.GetControlValue("min slot"), vi.GetControlValue("found")]; want = ref(num, last)   # noqa: E702
        ok = got == want and all(isinstance(x, int) for x in got[:2] + [vi.GetControlValue("last")]); OUT[tag].append((k + 1, last, want, got))   # noqa: E702
        gate("%s vector %d last=%s -> %s (got %s)" % (tag, k + 1, last, want, got), ok, need=False)
def main():
    BP.restart_labview(); g.reset(); time.sleep(3); OUT["h0"] = BP.labview_handles()           # noqa: E702
    gate("bed + s01 md5 before", md5(BED) == BEDM and md5(S01) == S01M); build(); runs("runs", range(7))   # noqa: E702
    OUT["h1"], OUT["peak_mb"] = BP.labview_handles(), peak(); fact("handles / peak MB", (OUT["h0"], OUT["h1"], OUT["peak_mb"]))   # noqa: E702
    kill("A"); BP.restart_labview(); g.reset(); time.sleep(3)                                  # noqa: E702
    gate("fresh: saved md5 unchanged, ExecState 1", md5(TGT) == OUT["md5"] and g.exec_state(TGT) == 1); runs("fresh", (1, 4))   # noqa: E702
if __name__ == "__main__":
    try:
        main()
    except Stop as e:
        print("STOP at the first unexpected result: %s" % e, flush=True)
    except Exception as e:                                                                      # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)   # noqa: E702
    finally:
        kill("Z"); [os.path.exists(p) and os.remove(p) for p in SCR]                            # noqa: E702
        gate("scratch files deleted; bed + s01 md5 unchanged", not any(os.path.exists(p) for p in SCR) and md5(BED) == BEDM and md5(S01) == S01M, SCR, need=False)
        json.dump(OUT, open(os.path.join(HERE, "diag_c142_1_out.json"), "w", encoding="utf-8"), indent=1, default=str)
        bad = [k for k, v in S5.G.items() if not v]; arts = [{"path": TGT, "md5": md5(TGT)}] if os.path.exists(TGT) else []   # noqa: E702
        json.dump({"function": "RingPickSlot_v0 subVI build + run", "card": "142-1", "t": time.time(), "log": "tools/bench/build_ringpickslot_v0.log",
                   "status": "FAIL" if bad else "PASS", "out": OUT}, open(os.path.join(HERE, "scratch_verify", "ringpickslot_c142_1_%s.json" % TS), "w", encoding="utf-8"), indent=1, default=str)
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
        sys.exit(1 if bad else 0)
