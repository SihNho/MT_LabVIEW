r"""diag_c118_p1b - card 118-3 P1 (rung 2 of 118-1; 118-2's diag_c118_p1 re-cut per PD234(i)): the POOL stage's CREATE routes + the three wire kinds
on a never-saved byte copy of the SAVED R2; every uid/name/position from the plan JSON named once below (PL). Verbs (all existing): loop_in, drop_subvi, queue_node,
create_const_loop_term, create_primitive_nested(donor=), create_indicator, wire, set_index_mode, tunnels; readers diag_c118_p0.read_num, wiki_build.read_live.
PRIOR ART: build_track_v6_queue.py:199-203 (Enqueue made IN the body, tunnel auto-made); build_track_v6_core.py:159-171 (wire then set_index_mode 1 heals);
review 2026-09-28-c118p1-names.md:85-100 (the donor is RUN and its indicator read - Constant.Value is void for arrays, NAMES.md:1157-1162).
PREDICTION: A1 donor constants made; D0 census SubVI/CallLibrary/Property/Invoke all 0; D1 ExecState 1; D2 indicator == Cam_pool00..19 after the run;
B1a For + 1 body; B1 no create error; B1b ForLoop/SubVI/Function +1/+1/+3, LoopTunnel +1 (Enqueue's); B2 ring dup bytes == #13245's; B3 both Obtain
typed on #13938.New Image's wire, no old row changed; B3b Enqueue 'queue' from a NEW tunnel's inner face; T1 the names wire makes ONE more tunnel;
T2 IndexMode 1 read back and its inner wire == Image Name's; T3 For N unwired; W1 element == pool New Image wire; W2 both max sizes wired from the I32s.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c118_p1b.log -- py -u tools/bench/diag_c118_p1b.py"""
import json, os, shutil, sys, time                                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                # noqa: E402
g = K.g
PLP = os.path.join(HERE, "diag_c118_p1b_plan.json"); PL = json.load(open(PLP, encoding="utf-8"))   # noqa: E702  ONE literal: stage_prerun.plan_files
Q, T, POS, PA, CC = PL["p0"], PL["terms"], PL["pos"], PL["paths"], PL["census_classes"]   # noqa: E702
R2, R2M = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]            # noqa: E702
DONOR, EMPTY = os.path.join(g.CLAUDEDEV, PA["donor"]), os.path.join(g.CLAUDEDEV, PA["empty"])   # noqa: E702
NAMES = ["{0}_pool{1:02d}".format(Q["base_name"], k) for k in range(20)]           # PD234(h): Cam_pool00..Cam_pool19
G0 = json.load(open(os.path.join(ROOT, PL["input"]["graph"]), encoding="utf-8"))
OUTJ, DRY, LN = os.path.join(HERE, "diag_c118_p1b.json"), bool(getattr(g.report_all, "_dry", False)), 9 * 99
s = K.Stage(R2, R2M, "scratch_c118_p1b", preload=False, deadline_min=38, reserve_s=2 * 90, out_json=OUTJ, task="card 118-3 P1")
_RD = g._run.__defaults__; B, P0M = K.mod("build_track_v6_core"), K.mod("diag_c118_p0"); g._run.__defaults__ = _RD   # noqa: E702
idx = lambda lst, u: lst.index(int(u)) if int(u) in lst else 0                     # noqa: E731
uidl = lambda t, c: [int(o["uid"]) for o in g.report_all(t, c)]                    # noqa: E731
VERIFIED = ["gscript.create_const_loop_term", "gscript.queue_node", "gscript.create_primitive_nested", "gscript.set_index_mode", "gscript.wire"]


def donor():
    shutil.copyfile(EMPTY, DONOR); g.open_panel(DONOR)                               # noqa: E702
    u_gc = B.drop(DONOR, PA["get_controls"], 0, tuple(POS["donor_gc"])); wt = B.walk(DONOR, 0)   # noqa: E702
    r1 = g.create_const_loop_term(DONOR, "for_n", wt[u_gc][0], value=NAMES, term_index=B.term(wt[u_gc][2], T["gc_names"], False)["i"])
    f0 = g.uids(DONOR, "ForLoop"); g.for_loop(DONOR, tuple(POS["donor_for"])); uf = sorted(g.uids(DONOR, "ForLoop") - f0)[0]   # noqa: E702
    r2 = g.create_const_loop_term(DONOR, "for_n", B.walk(DONOR, 0)[uf][0], value=len(NAMES))
    s.gate("A1 donor: both constants created (uid, no invoke error)", r1["created_uid"] and r2["created_uid"] and not r1["inv_err"] and not r2["inv_err"], (r1, r2), fatal=True)
    g.delete_object(DONOR, "SubVI", uidl(DONOR, "SubVI").index(u_gc), verify=False); g.remove_bad_wires_scripted(DONOR)   # noqa: E702
    # run 1 A3 + review archive/peer/2026-09-28-c118p1b-a3.md: a Constant is a GObject, not a Node - no existing op can put an
    # indicator on it (Constant.Terminal 634AC04 -> Create Indicator is a NEW op, a judgement decision). D2 (the names VALUE) is
    # therefore NOT MEASURED here; the donor is NOT run. Census + ExecState + membership are measured (the review's cheapest test).
    nod, con = [int(o["uid"]) for o in g.report_all(DONOR, "Node")], [int(o["uid"]) for o in g.report_all(DONOR, "Constant")]   # noqa: E702
    cen = dict((c, s.safe("census " + c, lambda c=c: len(g.report_all(DONOR, c)))) for c in CC)
    s.fact("DONOR CENSUS {0}; Node uids {1}; Constant uids {2}; node labels {3}".format(cen, nod, con, [r["label"] for r in g.node_labels(DONOR, 0)]))
    s.gate("A3 (review c118p1b-a3 test) both donor constants are in Traverse('Constant') and NEITHER is in Traverse('Node')",
           all(u in con and u not in nod for u in (r1["created_uid"], r2["created_uid"])), (nod, con))
    s.gate("D0 donor census: no SubVI / CallLibrary / Property / Invoke node (constants + loop only)", all(v == (0, "") for v in cen.values()), cen, fatal=True)
    es = g.exec_state(DONOR); s.gate("D1 donor ExecState 1 (runnable; NOT run - D2 needs the missing indicator op)", es == 1, es, fatal=True)   # noqa: E702
    s.fact("D2 NOT MEASURED: names value check needs Constant.Terminal -> Create Indicator (no op on disk) - OPEN to judgement")
    g.save(DONOR); g.close_panel(DONOR)                                             # noqa: E702
    rec = {"donor": DONOR, "md5": K.md5(DONOR), "names": r1["created_uid"], "i32": r2["created_uid"], "d2": "NOT MEASURED"}; return s.fact("DONOR RECORD {0}".format(rec)) and rec   # noqa: E702


def body(_):
    rec = donor() if not DRY else {"names": 1, "i32": 2}
    s.start(); s.scratches.append(s.work); W, F = s.work, Q["frame"]                   # noqa: E702
    DI = lambda u: idx(uidl(W, "Diagram"), u)                                        # noqa: E731
    made, c0 = {}, dict((c, g.uids(W, c)) for c in ("ForLoop", "SubVI", "Function", "LoopTunnel"))
    step = lambda tag, fn: made.__setitem__(tag, dict(zip(("ret", "err"), s.safe(tag, fn, None)))) or s.fact("CREATE {0}: {1}".format(tag, made[tag])) and made[tag]["ret"]   # noqa: E731
    d0 = set(uidl(W, "Diagram")); fl = step("for", lambda: g.loop_in("for", W, DI(F), tuple(POS["for"]))); nb = sorted(set(uidl(W, "Diagram")) - d0)   # noqa: E702
    s.gate("B1a For loop #{0} on #{1} with ONE body {2}".format(fl, F, nb), bool(fl) and len(nb) == 1 and not made["for"]["err"], (fl, nb), fatal=True)
    bd, sv0 = (nb[0] if nb else fl), set(uidl(W, "SubVI"))                          # noqa: E702  (dry: stub body)
    step("imaq", lambda: g.drop_subvi(W, PA["imaq_create"], DI(bd), tuple(POS["imaq"]))); im = (sorted(set(uidl(W, "SubVI")) - sv0) or [0])[0]   # noqa: E702
    step("names", lambda: g.create_primitive_nested(W, F, "pool_names", tuple(POS["names"]), donor={"donor": DONOR, "uid": rec["names"]}))
    for k in ("c20a", "c20b"):
        step(k, lambda k=k: g.create_primitive_nested(W, F, "i32_20", tuple(POS[k]), donor={"donor": DONOR, "uid": rec["i32"]}))
    step("ring", lambda: g.create_primitive_nested(W, bd, "ring_dup", tuple(POS["ring"]), donor={"donor": W, "uid": Q["ring"]}))
    for k in ("obt_free", "obt_work"):
        step(k, lambda k=k: g.queue_node("obtain", W, "SubVI", idx(uidl(W, "SubVI"), Q["imaq"]), T["imaq_out"], DI(F), tuple(POS[k])))
    of = (made["obt_free"]["ret"] or [0])[0]
    step("enq", lambda: g.queue_node("enqueue", W, "Function", idx(uidl(W, "Function"), of), T["q_out"], DI(bd), tuple(POS["enq"])))
    dc = dict((c, sorted(g.uids(W, c) - c0[c])) for c in c0); s.fact("NEW OBJECTS by class {0}; IMAQ #{1}; body #{2}".format(dc, im, bd))   # noqa: E702
    s.gate("B1 every create returned without error", all(not v["err"] for v in made.values()), dict((k, v["err"]) for k, v in made.items()), fatal=True)
    s.gate("B1b census: ForLoop +1, SubVI +1, Function +3 (2 Obtain + Enqueue), LoopTunnel +1 (the Enqueue's auto tunnel)",
           [len(dc[c]) for c in ("ForLoop", "SubVI", "Function", "LoopTunnel")] == [1, 1, 3, 1], dict((c, len(v)) for c, v in dc.items()))
    rl = lambda: {"terminals": G0["terminals"]} if DRY else K.mod("wiki_build").read_live(W, fs_pairs=G0["fs_tunnel_pairs"])   # noqa: E731
    L, old = rl()["terminals"], dict((int(r["term_uid"]), r) for r in G0["terminals"])
    row = lambda rows, u, n=None, src=False: next((r for r in rows if int(r["owner_uid"]) == int(u) and (n is None or r["term_name"] == n) and bool(r["is_source"]) == src), {})   # noqa: E731
    chg = [(r["term_uid"], old[int(r["term_uid"])]["wire_uid"], r["wire_uid"]) for r in L if int(r["term_uid"]) in old and r["wire_uid"] != old[int(r["term_uid"])]["wire_uid"]]
    rd = P0M.read_num(W, Q["ring"]), P0M.read_num(W, made["ring"]["ret"] or 0); hx = lambda r: (r.get("RingConstant") or {}).get("hex") if isinstance(r.get("RingConstant"), dict) else None   # noqa: E702,E731
    s.fact("RING #{0} {1} | dup {2}".format(Q["ring"], json.dumps(rd[0], default=str)[:LN], json.dumps(rd[1], default=str)[:LN]))
    s.gate("B2 ring dup bytes == #{0}'s (RingConstant route); #{0} unmoved on its old wire".format(Q["ring"]), hx(rd[0]) and hx(rd[0]) == hx(rd[1])
           and row(L, Q["ring"], None, True).get("frame_diagram") == F and not [c for c in chg if c[0] == row(L, Q["ring"], None, True).get("term_uid")], (hx(rd[0]), hx(rd[1])))
    ni = row(L, Q["imaq"], T["imaq_out"], True).get("wire_uid"); obs = [row(L, u, T["obt_type"]).get("wire_uid") for u in (made["obt_free"]["ret"] or []) + (made["obt_work"]["ret"] or [])]   # noqa: E702
    s.gate("B3 both Obtain 'element data type' on #{0}.New Image's wire w{1} (PD234(d)); no old row changed its wire".format(Q["imaq"], ni), bool(ni) and obs == [ni, ni] and not chg, (obs, chg[:10]))
    eq = (made["enq"]["ret"] or [0])[0]; qw = row(L, eq, T["enq_queue"]).get("wire_uid")   # noqa: E702
    tin = [r for r in L if r["owner_class"] == "LoopTunnel" and int(r["owner_uid"]) in dc["LoopTunnel"] and r["wire_uid"] == qw and r["is_source"]]
    s.gate("B3b Enqueue #{0} 'queue' wired (w{1}) from the NEW LoopTunnel's inner face".format(eq, qw), bool(qw) and len(tin) == 1, tin)
    # ---- the three wire kinds (PD234(i) T): names -> Image Name across the border, then flip; element and max sizes on their own diagrams
    nm = row(L, made["names"]["ret"] or 0, None, True); cs = uidl(W, "Constant"); t0 = set(uidl(W, "LoopTunnel"))   # noqa: E702
    e1 = s._op("wire", lambda: g.wire(W, "Constant", idx(cs, made["names"]["ret"] or 0), nm.get("term_name"), "SubVI", idx(uidl(W, "SubVI"), im), T["imaq_name"]), "names -> pool Image Name")["err"]
    nt = [o for o in g.report_all(W, "LoopTunnel") if int(o["uid"]) not in t0]
    s.gate("T1 the names wire made exactly ONE new LoopTunnel (source terminal {0!r}, err {1!r})".format(nm.get("term_name"), e1), len(nt) == 1 and not e1, nt, fatal=True)
    ti = int(nt[0]["i"]) if nt else 0; tun_ = lambda: g.tunnels(W, ti) if not DRY else {"index_mode": 0, "in_wires": []}   # noqa: E702,E731  (dry: stub)
    tb = tun_(); g.set_index_mode(W, ti, 1); ta = tun_(); s.fact("TUNNEL before {0} after {1}".format(tb, ta))   # noqa: E702
    w2 = s._op("wire", lambda: g.wire(W, "SubVI", idx(uidl(W, "SubVI"), im), T["imaq_out"], "Function", idx(uidl(W, "Function"), eq), T["enq_elem"]), "pool New Image -> Enqueue element"); e2 = w2["err"]   # noqa: E702
    e3 = [s._op("wire", lambda k=k, u=u: g.wire(W, "Constant", idx(cs, made[k]["ret"] or 0), row(L, made[k]["ret"] or 0, None, True).get("term_name"), "Function", idx(uidl(W, "Function"), u), T["obt_max"]), k + " -> max queue size")["err"]
          for k, u in zip(("c20a", "c20b"), [(made[q]["ret"] or [0])[0] for q in ("obt_free", "obt_work")])]
    L2 = rl()["terminals"]; wn = row(L2, im, T["imaq_name"]).get("wire_uid"); tun = [g.tunnels(W, i) for i, u in enumerate(uidl(W, "LoopTunnel")) if u in dc["LoopTunnel"] + [int(x["uid"]) for x in nt]]   # noqa: E702
    s.gate("T2 IndexMode 1 read back on the names tunnel and its inner wire == Image Name's w{0} (was mode {1})".format(wn, tb["index_mode"]), ta["index_mode"] == 1 and bool(wn) and wn in ta["in_wires"], ta)
    ncnt = [r for r in L2 if r["owner_class"] == "Tunnel" and int(r["frame_diagram"] or 0) == F and int(r["term_uid"]) not in old and not r["is_source"]]
    s.gate("T3 the new For loop's N (its Tunnel's outer sink on the frame) is UNWIRED", len(ncnt) == 1 and not ncnt[0]["wire_uid"], ncnt)
    s.gate("W1 pool IMAQ.New Image -> Enqueue.element on one wire (err {0!r})".format(e2), not e2 and row(L2, im, T["imaq_out"], True).get("wire_uid") and row(L2, im, T["imaq_out"], True).get("wire_uid") == row(L2, eq, T["enq_elem"]).get("wire_uid"), w2)
    mx = [row(L2, u, T["obt_max"]).get("wire_uid") for u in (made["obt_free"]["ret"] or [0]) + (made["obt_work"]["ret"] or [0])]
    s.gate("W2 both Obtain 'max queue size' wired from the two I32 20 constants (errs {0})".format(e3), not any(e3) and all(mx) and len(set(mx)) == 2
           and sorted(mx) == sorted(row(L2, made[k]["ret"] or 0, None, True).get("wire_uid") for k in ("c20a", "c20b")), mx)
    new = [r for r in L2 if int(r["term_uid"]) not in old]
    s.R["p1"] = {"made": made, "new_by_class": dc, "imaq": im, "body": bd, "new_rows": new, "changed_old_rows": chg, "ring": rd, "donor": rec, "tunnels": tun, "names_row": nm}
    if not s.fails and not DRY:
        for fn in VERIFIED:                                                        # stage_prerun.check_scratch: {function, status, t}
            p = os.path.join(HERE, "scratch_verify", "{0}_c118_{1}.json".format(fn, s.stamp))
            json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "118-3 P1", "log": "tools/bench/diag_c118_p1b.log", "input_md5": R2M, "plan": os.path.relpath(PLP, ROOT).replace("\\", "/")}, open(p, "w", encoding="utf-8"), indent=1)
            s.fact("SCRATCH-VERIFY record {0}".format(p))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
