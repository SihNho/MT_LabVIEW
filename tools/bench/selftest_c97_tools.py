r"""selftest_c97_tools.py - card 97-3: SELF-TEST of the five PD206(d) tools (tools/gscript.py "CARD 97-3" section) on a
NEVER-SAVED scratch byte copy of D1_s1_copy.vi (S1 md5 3e3d23ce...): For #1359 (body Diagram 7911) inside While #637
(body Diagram 639). The scratch is deleted at the end; S1, the bed and every original are never opened for writing.
Judgement c97: a self-test on a never-saved scratch may skip the stagekit dry/prerun, so this file does not import
stagekit (gscript level, like diag_c92_clfn_thread.py). Ops: tools/bench/diag_c97_tools_opbuild.log (18/0, cold ES 1).
PREDICTIONS (gates):
 K   S1 md5 before; scratch byte-identical
 T4a a carrier Index Array on the top level + create_control(index) -> exactly one new I32 control L (the selector source)
 T1  case_in(7911) / case_in(639): owner == that diagram; 2 frames, each owned by the case; uid echo == case; the boolean
     #11639 output (on 639) wired into each selector -> names read again (the True/False <-> frame uid map)
 T1N case_in(Diagram 99999999) raises ValueError, CaseStructure count unchanged; T1H 20 case_in calls: handles +-100
 T2  PD206(b) set into case A's frame: edge table (src term uid -> sink term uid, new tunnels collapsed) == before;
     only tunnel classes (+Wire/Node) change; T2N a member on another diagram -> ValueError, Wire count unchanged
 T3  BuildArray #11261 + indicator terminal #8323 into case B's frame: table == before; T3N ctl #8476 -> ValueError
 T5  an existing OUTPUT SelectorTunnel: 20 alternating writes read back, restored; case A's new tunnels set True;
     negative LoopTunnel[0] -> error text
 T4  20 label writes read back + the PD206(c) label; negative index past the end -> error, panel labels unchanged;
     default 9 set in memory and read back after ReinitializeAllToDefault (value 5 in between)
 H   refs live 0, LabVIEW gone, scratch deleted, S1 md5 unchanged
    py tools/bgrun.py --material --max-min 30 --log tools/bench/selftest_c97_tools.log -- py -u tools/bench/selftest_c97_tools.py
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
S1, S1_MD5 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"
TS = time.strftime("%Y%m%d_%H%M%S"); FIX = os.path.join(g.CLAUDEDEV, "scratch_c97_s1_%s.vi" % TS)  # noqa: E702
OUT = os.path.join(HERE, "selftest_c97_tools.json")
SET_A = [8741, 8775, 8795, 8476, 8764, 28180, 29009, 28233, 27716, 11310]   # PD206(b), f1359_gate_facts_97.json
SET_B = [11261, 8323]                                                     # PD206(c) case B
LABEL = "Force graph: update every N frames"                              # PD206(c)
G, R = {}, {"facts": []}


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:400]), flush=True); return bool(ok)  # noqa: E702


def fact(s): R["facts"].append(str(s)); print("  FACT  " + str(s)[:500], flush=True)     # noqa: E702


def H(): return BP.labview_handles()


def raises(fn):
    try:
        fn(); return None                                                                 # noqa: E702
    except ValueError as e:
        return str(e)


def selector(case_uid, src):
    """Wire the boolean source (diag idx, node idx, term idx) into the case's one unwired SINK terminal."""
    d = B.owner_of(FIX, case_uid, strict=False)[1]; di = g._uid_index(FIX, "Diagram", d)  # noqa: E702
    ni = g._node_index(FIX, di, case_uid); _u, rows = g.node_terms_uid(FIX, di, ni)     # noqa: E702
    sinks = [r for r in rows if not r["is_source"] and not r["wire"]] or [r for r in rows if not r["is_source"]]
    fact("case #%s terminals %r" % (case_uid, [(r["i"], r["name"], r["is_source"], r["wire"]) for r in rows]))
    CNL = json.load(open(CN.MAP_OUT, encoding="utf-8"))
    return CN.connect_nested_v1(FIX, di, ni, sinks[0]["i"], src[0], src[1], src[2], CNL) if sinks else "no free sink"


def section(name, fn, *a):
    try:
        return fn(*a)
    except Exception as e:                                                                # noqa: BLE001
        import traceback
        traceback.print_exc(); gate("%s section completed without an exception" % name, False, repr(e)[:300])  # noqa: E702
        return None


def body():
    gate("K S1 md5 before", md5(S1) == S1_MD5)
    BP.restart_labview(); g.reset(); time.sleep(3)                                        # noqa: E702
    shutil.copyfile(S1, FIX); time.sleep(0.4)                                             # noqa: E702
    gate("K scratch is a byte copy of S1", md5(FIX) == S1_MD5, os.path.basename(FIX))
    g.ensure_loaded(FIX); h0 = H(); fact("handles after load %r; ExecState %r" % (h0, g.exec_state(FIX)))  # noqa: E702
    rows0, dt = A.read_terms(FIX); fact("allterms %d rows in %.1f s" % (len(rows0), dt))  # noqa: E702
    # ---- T4a: a new I32 control from a carrier Index Array on the top level
    ia0 = g.uids(FIX, "IndexArray"); g.build_index_array(FIX, (9000, 9000))              # noqa: E702
    ia = [u for u in g.uids(FIX, "IndexArray") if u not in ia0][0]
    ni = [t[0] for t in g.node_info(FIX) if t[1] == "Index Array"][-1]
    new, L = g.create_control(FIX, ni, 2)
    gate("T4a one new control L from the carrier IA #%s 'index'" % ia, len(new) == 1 and bool(L), (new, L))
    cases = section("T1", t1, L) or {}
    if "A" in cases and "B" in cases:
        section("T2T3", t23, cases)
    section("T5", t5, rows0)
    section("T4", t4, L)
    R["es_end"] = g.exec_state(FIX); R["refs"] = g.ref_counts(); R["handles"] = (h0, H())  # noqa: E702


def t1(L):
    d639, d7911 = 639, 7911
    di = g._uid_index(FIX, "Diagram", d639); n11639 = g._node_index(FIX, di, 11639)      # noqa: E702
    _u, rr = g.node_terms_uid(FIX, di, n11639); t_out = [r["i"] for r in rr if r["is_source"]][0]  # noqa: E702
    boolsrc = (di, n11639, t_out)
    cases = {}
    for tag, D, loc, pos in (("A", d7911, (9000, 9300), (5250, 1600)), ("B", d639, (9000, 9700), (5800, 1760))):
        c = g.case_in(FIX, D, loc, L, position=pos)
        fo = [B.owner_of(FIX, f, strict=False) for f in c["frames"]]
        fact("T1 %s %r; frame owners %r" % (tag, c, fo))
        gate("T1 %s case #%s owned by Diagram #%s" % (tag, c["case"], D), c["owner"] == D, (c["owner_class"], c["owner"]))
        gate("T1 %s two frames, each owned by the case, uid echo clean" % tag,
             len(c["frames"]) == 2 and all(o[1] == c["case"] for o in fo) and not c["err"], (c["names"], c["err"]))
        r = selector(c["case"], boolsrc); fr = g.case_frames(FIX, c["case"])             # noqa: E702
        fact("T1 %s boolean #11639 -> selector: %r; frames now %r" % (tag, str(r)[:160], fr))
        gate("T1 %s frame names after a boolean selector read back (names %r)" % (tag, fr["names"]),
             len(fr["frames"]) == 2 and set(fr["frames"]) == set(c["frames"]) and not fr["err"], fr)
        tr = [f for n, f in zip(fr["names"], fr["frames"]) if n.strip().lower() == "true"]
        cases[tag] = (c["case"], (tr or [fr["frames"][-1]])[0], fr)
    nc = g.count(FIX, "CaseStructure")
    e = raises(lambda: g.case_in(FIX, 99999999, (9000, 9900), L))
    gate("T1N case_in(Diagram 99999999) refused before any edit", e and g.count(FIX, "CaseStructure") == nc, e)
    h1 = H()
    for k in range(20):
        g.case_in(FIX, d639, (9000, 10000 + 40 * k), L, position=(6200, 1800 + 40 * k))
    h2 = H(); gate("T1H 20 case_in calls: handles flat +-100", abs(h2 - h1) <= 100, (h1, h2))  # noqa: E702
    return cases


def t23(cases):
    for tag, (case, frame, fr), members, neg, spot in (("T2", cases["A"], SET_A, [11261], (5250, 1600)),
                                                        ("T3", cases["B"], SET_B, [8476], (5800, 1760))):
        fact("%s into case #%s frame #%s (names %r frames %r)" % (tag, case, frame, fr["names"], fr["frames"]))
        ha = H(); r = g.move_into_frame(FIX, frame, members, spot); hb = H()              # noqa: E702
        R[tag] = r
        fact("%s ops: %r" % (tag, [(o["edge"], o["verb"], o["result"][:80]) for o in r["ops"]]))
        fact("%s census before %r after %r; new tunnels %r" % (tag, r["census_before"], r["census_after"], r["new_tunnels"]))
        gate("%s every member now owned by frame #%s" % (tag, frame), all(o[1] == frame for o in r["owners_after"].values()), r["owners_after"])
        gate("%s edge table (src uid -> sink uid, new tunnels collapsed) == before (%d edges)" % (tag, len(r["edges_before"])),
             not r["missing"] and not r["extra"], {"missing": r["missing"], "extra": r["extra"]})
        same = [c for c in ("CaseStructure", "Diagram", "SubVI", "ControlTerminal", "Constant", "LoopTunnel")
                if r["census_after"][c] != r["census_before"][c]]
        gate("%s only tunnels added (structure/node classes unchanged, SelectorTunnel +%d)" % (tag, r["census_after"]["SelectorTunnel"] - r["census_before"]["SelectorTunnel"]),
             not same and r["census_after"]["SelectorTunnel"] > r["census_before"]["SelectorTunnel"], same)
        gate("%s handles over %d op calls: flat +-100" % (tag, len(r["ops"]) + len(members)), abs(hb - ha) <= 100, (ha, hb))
        w0 = g.count(FIX, "Wire"); e = raises(lambda: g.move_into_frame(FIX, frame, neg, spot))  # noqa: E702
        gate("%sN member %r not on the case's diagram refused before any edit" % (tag, neg), e and g.count(FIX, "Wire") == w0, e)


def t5(rows0):
    so = dict((int(r["owner_uid"]), [0, 0]) for r in rows0 if r["owner_class"] == "SelectorTunnel")
    for r in rows0:
        if int(r["owner_uid"]) in so:
            so[int(r["owner_uid"])][0 if r["is_source"] else 1] += 1
    tun = [u for u, (ns, nk) in sorted(so.items()) if ns == 1 and nk >= 2][0]
    first = g.tunnel_use_default(FIX, tun, True); orig = first["before"]                  # noqa: E702
    h3 = H(); rs = [g.tunnel_use_default(FIX, tun, bool(k % 2)) for k in range(20)]; h4 = H()  # noqa: E702
    back = g.tunnel_use_default(FIX, tun, orig)
    fact("T5 output SelectorTunnel #%s: first %r; restored %r" % (tun, first, back))
    gate("T5 20 writes read back (after == value, before == previous, echo == uid, no error)",
         all(x["after"] == bool(k % 2) and x["echo"] == tun and not x["err"] for k, x in enumerate(rs))
         and all(rs[k]["before"] == rs[k - 1]["after"] for k in range(1, 20)), [(x["before"], x["after"], x["err"][:40]) for x in rs[:3]])
    gate("T5 20 calls: handles flat +-100", abs(h4 - h3) <= 100, (h3, h4))
    ta = []
    for t in (R.get("T2") or {}).get("new_tunnels", []):
        try:
            ta.append((t, g.tunnel_use_default(FIX, t, True)))
        except ValueError as ex:
            ta.append((t, "not a SelectorTunnel: %s" % ex))
    fact("T5 case A new tunnels -> True: %r" % ta)
    gate("T5 at least one of case A's new tunnels reads UseDefault True after the write",
         any(isinstance(x, dict) and x["after"] and not x["err"] for _t, x in ta), ta)
    neg = g.tunnel_use_default_at(FIX, "LoopTunnel", 0, True)
    gate("T5N a LoopTunnel is refused by the cast (error text)", bool(neg["err"]), neg)


def t4(L):
    pw = g.panel_wiring(FIX); p = [i for i, r in enumerate(pw) if r["label"] == L]        # noqa: E702
    gate("T4 control L found on the panel", len(p) == 1, (L, p))
    h5 = H(); rl = [g.set_control_label(FIX, p[0], "c97 label %d" % k) for k in range(20)]; h6 = H()  # noqa: E702
    gate("T4 20 label writes read back", all(x["text_back"] == "c97 label %d" % k and not x["err"] for k, x in enumerate(rl)), rl[:2])
    gate("T4 20 calls: handles flat +-100", abs(h6 - h5) <= 100, (h5, h6))
    fin = g.set_control_label(FIX, p[0], LABEL); pw2 = g.panel_wiring(FIX)                # noqa: E702
    gate("T4 final label %r read back by the op AND by panel_wiring" % LABEL, fin["text_back"] == LABEL and pw2[p[0]]["label"] == LABEL, (fin, pw2[p[0]]))
    labs = [r["label"] for r in pw2]; ng = g.set_control_label(FIX, len(pw2) + 5, "must not land")  # noqa: E702
    gate("T4N index past the end: error text, no panel label changed", bool(ng["err"]) and [r["label"] for r in g.panel_wiring(FIX)] == labs, ng)
    dv = g.set_default_in_memory(FIX, LABEL, 9, 5)
    gate("T4 default 9 read back after ReinitializeAllToDefault (5 in between)", int(dv["after_reinit"]) == 9 and not dv["err"], dv)


try:
    body()
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
