r"""diag_c118_p1b - card 119-1 P1 (re-run per PD234(k); card 118-3 run 2 landed 8 of 9 creates, diag_c118_p1b_r2.log:31-44): the POOL stage's CREATE
routes + the three wire kinds on a never-saved byte copy of the SAVED R2; every uid/name/position from the plan JSON (PL). Changes vs 118-3: the donor is the
KEPT file claudeDev\DonorPool_v0.vi (byte copy, card 119-1 C1; never made, run or saved here); every constant VALUE is read with gscript.read_const_value
(gscript.py:4226, built + scratch-verified by 118-4) - the donor names, the names copy IN THE BED, and the ring pair (value AND Representation, PD234(k)(2));
the ArrayConstant copy goes through create_primitive_nested's exception (gscript.py:4385-4400). Verbs (all existing): loop_in, drop_subvi, queue_node,
create_primitive_nested(donor=), wire, set_index_mode, tunnels, read_const_value; reader wiki_build.read_live.
PRIOR ART: build_track_v6_queue.py:199-203 (Enqueue made IN the body, tunnel auto-made); build_track_v6_core.py:159-171 (wire then set_index_mode 1 heals);
diag_c118_r1v.log:34-46 (read_const_value on #23583/#13245/donor #101 and the A2 copy on this same R2).
PREDICTION: K0 donor md5 == plan md5; A1 donor names == Cam_pool00..19; B1a For + 1 body; B1 no create error; B1b ForLoop/SubVI/Function +1/+1/+3,
LoopTunnel +1 (Enqueue's); V1 names copy IN THE BED == Cam_pool00..19; B2 ring dup value + Representation == #13245's; B3 both Obtain typed on
#13938.New Image's wire, no old row changed; B3b Enqueue 'queue' from a NEW tunnel's inner face; T1 the names wire makes ONE more tunnel;
T2 IndexMode 1 read back and its inner wire == Image Name's; T3 For N unwired; W1 element == pool New Image wire; W2 both max sizes wired from the I32s.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c119_p1b.log -- py -u tools/bench/diag_c118_p1b.py"""
import json, os, sys, time                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                # noqa: E402
g = K.g
PLP = os.path.join(HERE, "diag_c118_p1b_plan.json"); PL = json.load(open(PLP, encoding="utf-8"))   # noqa: E702  ONE literal: stage_prerun.plan_files
Q, T, POS, PA, DR = PL["p0"], PL["terms"], PL["pos"], PL["paths"], PL["donor"]       # noqa: E702
R2, R2M = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]            # noqa: E702
DONOR = os.path.join(g.CLAUDEDEV, DR["vi"])
NAMES = ["{0}_pool{1:02d}".format(Q["base_name"], k) for k in range(20)]           # PD234(h): Cam_pool00..Cam_pool19
G0 = json.load(open(os.path.join(ROOT, PL["input"]["graph"]), encoding="utf-8"))
OUTJ, DRY, LN = os.path.join(HERE, "diag_c119_p1b.json"), bool(getattr(g.report_all, "_dry", False)), 9 * 99
s = K.Stage(R2, R2M, "scratch_c119_p1b", preload=False, deadline_min=38, reserve_s=2 * 90, out_json=OUTJ, task="card 119-1 P1")
idx = lambda lst, u: lst.index(int(u)) if int(u) in lst else 0                     # noqa: E731
uidl = lambda t, c: [int(o["uid"]) for o in g.report_all(t, c)]                    # noqa: E731
rcv = lambda t, u, tag: {"dry": tag} if DRY else (s.safe(tag, lambda: g.read_const_value(t, u), {})[0] or {})   # noqa: E731  (dry: no value model)
VERIFIED = ["gscript.queue_node", "gscript.create_primitive_nested", "gscript.set_index_mode", "gscript.wire", "gscript.wire_const", "gscript.read_const_value"]


def body(_):
    rec = DR                                                                        # the KEPT donor (card 119-1 C1): never made, run or saved here
    s.gate("K0 donor {0} md5 == {1} (byte copy of the 118-3 donor)".format(DR["vi"], DR["md5"]), K.md5(DONOR) == DR["md5"], K.md5(DONOR), fatal=True)
    s.start(); s.scratches.append(s.work); W, F = s.work, Q["frame"]                   # noqa: E702
    rd = rcv(DONOR, DR["names"], "read donor names"); s.fact("DONOR #{0} {1}".format(DR["names"], json.dumps(rd, default=str)[:LN]))   # noqa: E702
    DRY or s.gate("A1 donor #{0} read_const_value == Cam_pool00..19 (ArrayConstant, uid echo, no error)".format(DR["names"]), list(rd.get("value") or []) == NAMES
                  and rd.get("cls") == "ArrayConstant" and rd.get("echo") == DR["names"] and not rd.get("err"), (rd.get("cls"), rd.get("err")), fatal=True)
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
    vn = rcv(W, made["names"]["ret"] or 0, "read names copy"); s.fact("NAMES COPY #{0} {1}".format(made["names"]["ret"], json.dumps(vn, default=str)[:LN]))   # noqa: E702
    s.gate("V1 names copy #{0} IN THE BED: read_const_value == Cam_pool00..19 (PD234(k) L4), ArrayConstant, no error".format(made["names"]["ret"]),
           list(vn.get("value") or []) == NAMES and vn.get("cls") == "ArrayConstant" and not vn.get("err"), (vn.get("cls"), vn.get("err")))
    rd = rcv(W, Q["ring"], "read ring"), rcv(W, made["ring"]["ret"] or 0, "read ring dup"); vr = lambda r: (r.get("value"), (r.get("type") or {}).get("representation"))   # noqa: E702,E731
    s.fact("RING #{0} {1} | dup {2}".format(Q["ring"], json.dumps(rd[0], default=str)[:LN], json.dumps(rd[1], default=str)[:LN]))
    s.gate("B2 ring dup value + Representation == #{0}'s (read_const_value, PD234(k)(2)); #{0} unmoved on its old wire".format(Q["ring"]), isinstance(rd[0].get("value"), int)
           and vr(rd[0])[1] is not None and vr(rd[0]) == vr(rd[1]) and not rd[0].get("err") and not rd[1].get("err") and rd[1].get("cls") == "RingConstant"
           and row(L, Q["ring"], None, True).get("frame_diagram") == F and not [c for c in chg if c[0] == row(L, Q["ring"], None, True).get("term_uid")], (vr(rd[0]), vr(rd[1])))
    ni = row(L, Q["imaq"], T["imaq_out"], True).get("wire_uid"); obs = [row(L, u, T["obt_type"]).get("wire_uid") for u in (made["obt_free"]["ret"] or []) + (made["obt_work"]["ret"] or [])]   # noqa: E702
    s.gate("B3 both Obtain 'element data type' on #{0}.New Image's wire w{1} (PD234(d)); no old row changed its wire".format(Q["imaq"], ni), bool(ni) and obs == [ni, ni] and not chg, (obs, chg[:10]))
    eq = (made["enq"]["ret"] or [0])[0]; qw = row(L, eq, T["enq_queue"]).get("wire_uid")   # noqa: E702
    tin = [r for r in L if r["owner_class"] == "LoopTunnel" and int(r["owner_uid"]) in dc["LoopTunnel"] and r["wire_uid"] == qw and r["is_source"]]
    s.gate("B3b Enqueue #{0} 'queue' wired (w{1}) from the NEW LoopTunnel's inner face".format(eq, qw), bool(qw) and len(tin) == 1, tin)
    # ---- the three wire kinds (PD234(i) T): names -> Image Name across the border, then flip; element and max sizes on their own diagrams
    # run c119 #1 (diag_c119_p1b.log:50): gscript.wire's source ladder casts to Node -> 1057 on a Constant. A bare constant source is
    # gscript.wire_const (OpConstWire_v1, card 85-1: Constant.Terminal -> Connect Wire; stagexec.py:1922-1930 route 188(c)).
    tix = lambda d, u, n: [int(r["i"]) for r in g.node_terms(W, DI(d), g._node_index(W, DI(d), u)) if r["name"] == n and not r["is_source"]][0]   # noqa: E731
    wc = lambda tag, cu, ccls, du, dcls, d, n: s._op("wire", lambda: g.wire_const(W, ccls, g._uid_index(W, ccls, cu), dcls, g._uid_index(W, dcls, du), tix(d, du, n)), tag)   # noqa: E731
    er = lambda rec: rec["err"] or (rec["result"][1] if isinstance(rec.get("result"), (list, tuple)) and len(rec["result"]) > 1 else "")   # noqa: E731
    nm = row(L, made["names"]["ret"] or 0, None, True); t0 = set(uidl(W, "LoopTunnel"))   # noqa: E702
    e1 = er(wc("names -> pool Image Name", made["names"]["ret"] or 0, PL["classes"]["names"], im, "SubVI", bd, T["imaq_name"]))
    nt = [o for o in g.report_all(W, "LoopTunnel") if int(o["uid"]) not in t0]
    s.gate("T1 the names wire made exactly ONE new LoopTunnel (source terminal {0!r}, err {1!r})".format(nm.get("term_name"), e1), len(nt) == 1 and not e1, nt, fatal=True)
    ti = int(nt[0]["i"]) if nt else 0; tun_ = lambda: g.tunnels(W, ti) if not DRY else {"index_mode": 0, "in_wires": []}   # noqa: E702,E731  (dry: stub)
    tb = tun_(); g.set_index_mode(W, ti, 1); ta = tun_(); s.fact("TUNNEL before {0} after {1}".format(tb, ta))   # noqa: E702
    w2 = s._op("wire", lambda: g.wire(W, "SubVI", idx(uidl(W, "SubVI"), im), T["imaq_out"], "Function", idx(uidl(W, "Function"), eq), T["enq_elem"]), "pool New Image -> Enqueue element"); e2 = w2["err"]   # noqa: E702
    e3 = [er(wc(k + " -> max queue size", made[k]["ret"] or 0, PL["classes"]["i32"], u, "Function", F, T["obt_max"]))
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
    s.gate("K donor md5 unchanged after the reads and copies", K.md5(DONOR) == DR["md5"], K.md5(DONOR))
    if not s.fails and not DRY:
        for fn in VERIFIED:                                                        # stage_prerun.check_scratch: {function, status, t}
            p = os.path.join(HERE, "scratch_verify", "{0}_c119_{1}.json".format(fn, s.stamp))
            json.dump({"function": fn, "status": "PASS", "t": time.time(), "card": "119-1 P1", "log": "tools/bench/diag_c119_p1b.log", "input_md5": R2M, "plan": os.path.relpath(PLP, ROOT).replace("\\", "/")}, open(p, "w", encoding="utf-8"), indent=1)
            s.fact("SCRATCH-VERIFY record {0}".format(p))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
