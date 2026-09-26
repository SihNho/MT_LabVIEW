r"""selftest_c98_move.py - card 98-2 (PD207(c)(d)): SELF-TEST of the patched gscript.move_into_frame (orphan-wire deletion
by uid + ExecState/termless gate, `expect_broken`) and the new reader gscript.wire_health, on a NEVER-SAVED scratch byte
copy of D1_s1_copy.vi (S1 md5 3e3d23ce...). Gscript level, no stagekit (precedent: selftest_c97_tools.py, judgement c97:
a never-saved scratch skips dry/prerun). FOUND FIRST: allterms.read_terms/all_wire_uids (termless criterion of
join_wires), gscript.delete_object('Wire', idx) as build_opfsinnertunnelconnect_v0.del_wire:336, build_d1_v0.owner_of;
no new op. Setup mirrors stage_d1_fgate.body:41-58 (carrier IA -> control L -> case_in A/B, L's wire + IA deleted) with
the selectors fed by boolean #11639 (selftest_c97_tools.selector).
PREDICTIONS (gates):
 K   S1 md5; scratch byte copy.   E1  ExecState 1 after setup, 0 termless (98-1: E1 1, 0 termless)
 A   move_into_frame(A True frame, set_a, expect_broken=True): edges equal; >=1 orphan deleted (98-1: 8), termless left
     0, no other wire gone; ExecState 0 PREDICTED (A's new output tunnel has no value in ' False ' until Use Default) ->
     UseDefault on A's out tunnel(s) feeding LoopTunnel #11363 -> ExecState 1
 BN  NEGATIVE: move_into_frame(B True frame, set_b, _keep_orphans=1, expect_broken False) RAISES MoveIntoFrameBroken
     (98-1: B leaves 1 orphan), .result edges equal, termless_left == kept; then that one wire deleted by uid ->
     wire_health: 0 termless, ExecState 1
 H20 20 wire_health calls: handles flat +-100.  H refs, LabVIEW gone, scratch deleted, S1 md5 unchanged
    MATERIAL=1 py tools/bgrun.py --max-min 50 --log tools/bench/selftest_c98_move.log -- py -u tools/bench/selftest_c98_move.py
"""
import hashlib, json, os, shutil, subprocess, sys, time                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep as BP                                                                   # noqa: E402
import allterms as A                                                                      # noqa: E402
import build_d1_v0 as B                                                                   # noqa: E402
import build_opconnectnested_v1 as CN                                                     # noqa: E402
g._run.__defaults__ = (6.0, 120.0)
PL = json.load(open(os.path.join(HERE, "plans", "plan_fgate_97.json"), encoding="utf-8"))
U, XY = PL["uids"], PL["pos"]                                                             # noqa: E702
S1, S1_MD5 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"), PL["input"]["md5"]
TS = time.strftime("%Y%m%d_%H%M%S"); FIX = os.path.join(g.CLAUDEDEV, "scratch_c98_s1_%s.vi" % TS)  # noqa: E702
OUT = os.path.join(HERE, "selftest_c98_move.json")
G, R = {}, {"facts": []}
Fatal = type("Fatal", (Exception,), {})


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d="", fatal=False):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:400]), flush=True)  # noqa: E702
    if fatal and not ok:
        raise Fatal(k)
    return bool(ok)


def fact(s): R["facts"].append(str(s)); print("  FACT  " + str(s)[:500], flush=True)     # noqa: E702


def H(): return BP.labview_handles()


def selector(case_uid, src):
    """selftest_c97_tools.selector: wire the boolean source into the case's one unwired SINK terminal."""
    d = B.owner_of(FIX, case_uid, strict=False)[1]; di = g._uid_index(FIX, "Diagram", d)  # noqa: E702
    ni = g._node_index(FIX, di, case_uid); _u, rows = g.node_terms_uid(FIX, di, ni)     # noqa: E702
    sinks = [r for r in rows if not r["is_source"] and not r["wire"]] or [r for r in rows if not r["is_source"]]
    return CN.connect_nested_v1(FIX, di, ni, sinks[0]["i"], src[0], src[1], src[2], json.load(open(CN.MAP_OUT, encoding="utf-8")))


def true_frame(c):
    fr = g.case_frames(FIX, c)
    return [f for n, f in zip(fr["names"], fr["frames"]) if str(n).strip() == "True"][0], fr


def move_summary(tag, r):
    R[tag] = dict((k, v) for k, v in r.items() if k != "ops")
    fact("%s edges %d missing %r extra %r new tunnels %r; orphans deleted %r kept %r owners %r; termless left %r total %d; "
         "ExecState %r; other wires gone %r" % (tag, len(r["edges_before"]), r["missing"], r["extra"], r["new_tunnels"],
                                               r["orphans_deleted"], r["orphans_kept"], r["orphan_owners"], r["termless_left"],
                                               r["termless_total"], r["exec_state"], r["wires_gone_unexpectedly"]))


def body():
    gate("K S1 md5 before", md5(S1) == S1_MD5, fatal=True)
    BP.restart_labview(); g.reset(); time.sleep(3)                                        # noqa: E702
    shutil.copyfile(S1, FIX); time.sleep(0.4)                                             # noqa: E702
    gate("K scratch is a byte copy of S1", md5(FIX) == S1_MD5, os.path.basename(FIX), fatal=True)
    g.ensure_loaded(FIX); fact("handles after load %r; ExecState %r" % (H(), g.exec_state(FIX)))  # noqa: E702
    # ---- setup = stage_d1_fgate.body:41-58 (no label/default: not under test)
    ia0 = g.uids(FIX, "IndexArray"); g.build_index_array(FIX, tuple(XY["carrier"]))       # noqa: E702
    ia = [u for u in g.uids(FIX, "IndexArray") if u not in ia0][0]
    ni = [t[0] for t in g.node_info(FIX) if t[1] == "Index Array"][-1]
    new, L = g.create_control(FIX, ni, PL["carrier_term"])
    gate("S1 one new control L from carrier IA #%s" % ia, len(new) == 1 and bool(L), (new, L), fatal=True)
    cases = {}
    for t, D in (("A", U["for_body"]), ("B", U["loop_body"])):
        c = g.case_in(FIX, D, tuple(XY["build_" + t]), L, position=tuple(XY["case_" + t]))
        gate("S2 case %s #%s owned by Diagram #%s, 2 frames" % (t, c["case"], D), c["owner"] == D and len(c["frames"]) == 2, c, fatal=True)
        cases[t] = c["case"]
    wl = [r for r in g.panel_wiring(FIX) if r["label"] == L][0].get("wire")
    for cls, u in (("Wire", wl), ("IndexArray", ia)):
        if u:
            g.delete_object(FIX, cls, [o["uid"] for o in g.report_all(FIX, cls)].index(u), verify=False)
    gate("S3 carrier IA #%s and L's top-level wire w%s gone" % (ia, wl), ia not in g.uids(FIX, "IndexArray") and wl not in g.uids(FIX, "Wire"), (ia, wl), fatal=True)
    di = g._uid_index(FIX, "Diagram", U["loop_body"]); n11639 = g._node_index(FIX, di, 11639)   # noqa: E702
    _u, rr = g.node_terms_uid(FIX, di, n11639); src = (di, n11639, [r["i"] for r in rr if r["is_source"]][0])  # noqa: E702
    tf = {}
    for t in ("A", "B"):
        fact("S4 selector %s <- #11639: %s" % (t, str(selector(cases[t], src))[:160]))
        tf[t], fr = true_frame(cases[t]); fact("S4 case %s frames %r -> True #%s" % (t, fr, tf[t]))   # noqa: E702
    h = g.wire_health(FIX); R["E1"] = {"termless": h["termless"], "exec_state": h["exec_state"], "wires": len(h["wires"])}  # noqa: E702
    gate("E1 ExecState 1 and 0 termless before the moves (wires %d)" % len(h["wires"]), h["exec_state"] == 1 and not h["termless"], R["E1"], fatal=True)
    # ---- A: positive deletion (98-1 predicts 8 orphans); broken by design until UseDefault
    ha = H(); ra = g.move_into_frame(FIX, tf["A"], PL["set_a"], tuple(XY["case_A"]), expect_broken=True); hb = H()  # noqa: E702
    move_summary("A", ra); fact("A handles %r -> %r over %d op calls" % (ha, hb, len(ra["ops"])))   # noqa: E702
    gate("A every member owned by True frame #%s" % tf["A"], all(o[1] == tf["A"] for o in ra["owners_after"].values()), ra["owners_after"])
    gate("A edge table == before (%d edges)" % len(ra["edges_before"]), not ra["missing"] and not ra["extra"], (ra["missing"], ra["extra"]))
    gate("A >=1 orphan deleted by uid (98-1: 8), termless left 0, no other wire gone",
         len(ra["orphans_deleted"]) >= 1 and not ra["termless_left"] and not ra["wires_gone_unexpectedly"],
         (ra["orphans_deleted"], ra["termless_left"], ra["wires_gone_unexpectedly"]))
    rows = A.read_terms(FIX)[0]
    wo = [x["wire_uid"] for x in rows if int(x["owner_uid"]) == U["out_loop_tunnel"] and not x["is_source"]][0]
    outA = sorted(set(int(x["owner_uid"]) for x in rows if x["wire_uid"] == wo and x["is_source"] and int(x["owner_uid"]) in ra["new_tunnels"]))
    gate("A output tunnel(s) %r feeding #%s: %d expected" % (outA, U["out_loop_tunnel"], PL["a_out_tunnels"]), len(outA) == PL["a_out_tunnels"], outA, fatal=True)
    for tu in outA:
        u = g.tunnel_use_default(FIX, tu, True); gate("A UseDefault #%s reads True" % tu, u["after"] is True and not u["err"], u)  # noqa: E702
    h = g.wire_health(FIX, rows)
    gate("A ExecState 1 and 0 termless after move A + UseDefault", h["exec_state"] == 1 and not h["termless"], (h["exec_state"], h["termless"]))
    # ---- B: NEGATIVE - one orphan deliberately kept, expect_broken False -> the verb must raise
    raised = None
    try:
        g.move_into_frame(FIX, tf["B"], PL["set_b"], tuple(XY["case_B"]), _keep_orphans=1)
    except g.MoveIntoFrameBroken as e:
        raised = e
    gate("BN verb RAISED MoveIntoFrameBroken on a kept orphan (expect_broken False)", raised is not None, str(raised)[:300], fatal=True)
    rb = raised.result; move_summary("B", rb); fact("BN message: %s" % str(raised)[:400])   # noqa: E702
    gate("BN edge table == before (%d edges); members in True frame #%s" % (len(rb["edges_before"]), tf["B"]),
         not rb["missing"] and not rb["extra"] and all(o[1] == tf["B"] for o in rb["owners_after"].values()), (rb["missing"], rb["extra"], rb["owners_after"]))
    gate("BN termless_left == the kept orphan(s) %r, no other wire gone" % rb["orphans_kept"],
         len(rb["orphans_kept"]) == 1 and rb["termless_left"] == rb["orphans_kept"] and not rb["wires_gone_unexpectedly"], rb)
    for w in rb["orphans_kept"]:
        g.delete_object(FIX, "Wire", [o["uid"] for o in g.report_all(FIX, "Wire")].index(w), verify=False)
    h = g.wire_health(FIX); R["final"] = {"termless": h["termless"], "exec_state": h["exec_state"], "wires": len(h["wires"])}  # noqa: E702
    gate("BF after deleting the kept orphan by uid: ExecState 1, 0 termless", h["exec_state"] == 1 and not h["termless"], R["final"])
    # ---- handles over 20 calls of the new reader
    h1 = H(); [g.wire_health(FIX) for _k in range(20)]; h2 = H()                          # noqa: E702
    gate("H20 20 wire_health calls: handles flat +-100", abs(h2 - h1) <= 100, (h1, h2))
    R["refs"] = g.ref_counts()


try:
    body()
except Fatal as e:
    fact("stopped at fatal gate %s" % e)
except Exception as e:                                                                    # noqa: BLE001
    import traceback
    traceback.print_exc(); G["EXC %s" % str(e)[:120]] = False                            # noqa: E702
finally:
    fact("refs %r" % (g.ref_counts(),))
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    for _k in range(5):
        try:
            if os.path.exists(FIX):
                os.remove(FIX)
            break
        except OSError:
            time.sleep(2)
    gate("H LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    gate("H scratch deleted", not os.path.exists(FIX)); gate("H S1 md5 unchanged", md5(S1) == S1_MD5)  # noqa: E702
    R["gates"] = G; json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)  # noqa: E702
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                      [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
    sys.exit(1 if bad else 0)
