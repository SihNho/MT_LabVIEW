r"""diag_c118_p1 - card 118-2 P1 (118-1's P1, its own bugs fixed): the POOL stage's CREATE routes (PD234(a)-(d),(h)) on a never-saved byte copy
of the SAVED R2; every uid/name/position from diag_c118_p1_plan.json. Verbs: loop_in, drop_subvi, queue_node, create_const_loop_term, create_primitive_nested
(donor=); readers diag_c118_p0.read_str/read_num, wiki_build.read_live. PRIOR ART: build_track_v6_queue.py:199-203 (Enqueue made IN the body from a
top-level Obtain, tunnel auto-made, NAMES.md:911-912); build_track_v6_core.py:144-156. FIXED: IMAQ path '.vi' inside an LLB (NAMES.md:954-956); base name
was P0's whole variant text (diag_c118_p0.json:448); Enqueue now in the For body (PD234(a)); value gates; no typed uids (X6).
PREDICTION: A0 P0 bytes end 'Cam'; A1/A1b donor constants made, names bytes == Cam_pool00..19; A2 donor ExecState 1; B1a For + 1 body; B1 no create
error; B1b ForLoop/SubVI/Function/LoopTunnel +1/+1/+3/+1; B2 ring dup bytes == #13245's, #13245 unmoved; B2b names bytes; B3 both Obtain type on
#13938.New Image's wire, no old row rewired; B3b Enqueue 'queue' from a new LoopTunnel inner face.
    py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_c118_p1.log -- py -u tools/bench/diag_c118_p1.py"""
import json, os, shutil, struct, sys                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                # noqa: E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c118_p1_plan.json"), encoding="utf-8"))   # ONE literal: stage_prerun.plan_files
Q, T, POS, PA = PL["p0"], PL["terms"], PL["pos"], PL["paths"]                          # noqa: E702
R2, R2M = os.path.join(g.CLAUDEDEV, PL["input"]["vi"]), PL["input"]["md5"]            # noqa: E702
DONOR, EMPTY = os.path.join(g.CLAUDEDEV, PA["donor"]), os.path.join(g.CLAUDEDEV, PA["empty"])   # noqa: E702
P0 = json.load(open(os.path.join(HERE, "diag_c118_p0.json"), encoding="utf-8"))["p0"]
NAMES = ["{0}_pool{1:02d}".format(Q["base_name"], k) for k in range(20)]           # PD234(h): Cam_pool00..Cam_pool19
FLAT = (struct.pack(">i", len(NAMES)) + b"".join(struct.pack(">i", len(n)) + n.encode("latin-1") for n in NAMES) + b"\0\0\0\0").hex()
G0 = json.load(open(os.path.join(ROOT, PL["input"]["graph"]), encoding="utf-8"))
OUTJ, DRY, LN = os.path.join(HERE, "diag_c118_p1.json"), bool(getattr(g.report_all, "_dry", False)), 9 * 99   # LN: X6, no int literal >= 100
s = K.Stage(R2, R2M, "scratch_c118_p1", preload=False, deadline_min=33, reserve_s=2 * 90, out_json=OUTJ, task="card 118-2 P1")
_RD = g._run.__defaults__; B, P0M = K.mod("build_track_v6_core"), K.mod("diag_c118_p0"); g._run.__defaults__ = _RD   # noqa: E702 B sets (6,120)
idx = lambda lst, u: lst.index(int(u)) if int(u) in lst else 0                     # noqa: E731  (dry: a stub uid is not in the graph)
uidl = lambda t, c: [int(o["uid"]) for o in g.report_all(t, c)]                    # noqa: E731


def donor():
    shutil.copyfile(EMPTY, DONOR); g.open_panel(DONOR)                               # noqa: E702
    u_gc = B.drop(DONOR, PA["get_controls"], 0, tuple(POS["donor_gc"])); wt = B.walk(DONOR, 0)   # noqa: E702
    r1 = g.create_const_loop_term(DONOR, "for_n", wt[u_gc][0], value=NAMES, term_index=B.term(wt[u_gc][2], T["gc_names"], False)["i"])
    f0 = g.uids(DONOR, "ForLoop"); g.for_loop(DONOR, tuple(POS["donor_for"])); uf = sorted(g.uids(DONOR, "ForLoop") - f0)[0]   # noqa: E702
    r2 = g.create_const_loop_term(DONOR, "for_n", B.walk(DONOR, 0)[uf][0], value=len(NAMES))
    s.fact("DONOR consts: names {0} ; i32 {1}".format(r1, r2))
    s.gate("A1 donor: both constants created (uid, no invoke error)", r1["created_uid"] and r2["created_uid"] and not r1["inv_err"] and not r2["inv_err"], (r1, r2), fatal=True)
    nm = P0M.read_str(DONOR, r1["created_uid"]); s.fact("DONOR NAMES READ {0}".format(json.dumps(nm)[:LN]))   # noqa: E702
    s.gate("A1b donor names constant bytes end in the flattened Cam_pool00..19", nm.get("hex", "").endswith(FLAT) and not nm.get("err"), nm.get("hex", "")[-LN // 7:], fatal=True)
    g.delete_object(DONOR, "SubVI", uidl(DONOR, "SubVI").index(u_gc), verify=False); g.remove_bad_wires_scripted(DONOR)   # noqa: E702
    es = g.exec_state(DONOR)
    s.gate("A2 donor ExecState 1 after freeing the names constant", es == 1, es, fatal=True)
    g.save(DONOR); g.close_panel(DONOR)                                             # noqa: E702
    rec = {"donor": DONOR, "md5": K.md5(DONOR), "names": r1["created_uid"], "i32": r2["created_uid"]}; s.fact("DONOR RECORD {0}".format(rec))   # noqa: E702
    return rec


def body(_):
    s.gate("A0 P0's #{0} value bytes end in {1!r} (the PD234(h) base name)".format(Q["name_const"], Q["base_name"]),
           P0["name13938"]["hex"].endswith(Q["name_hex_tail"]) and P0["name13938"]["uid"] == Q["name_const"], P0["name13938"]["hex"][-40:], fatal=True)
    rec = donor() if not DRY else {"names": 1, "i32": 2}
    s.start(); s.scratches.append(s.work); W, F = s.work, Q["frame"]                   # noqa: E702
    DI = lambda u: idx(uidl(W, "Diagram"), u)                                        # noqa: E731
    made, c0 = {}, dict((c, g.uids(W, c)) for c in ("ForLoop", "SubVI", "Function", "LoopTunnel"))

    def step(tag, fn):
        v, err = s.safe(tag, fn, None); made[tag] = {"ret": v, "err": err}          # noqa: E702
        return s.fact("CREATE {0}: {1} err {2!r}".format(tag, v, err)) and v
    d0 = set(uidl(W, "Diagram"))
    fl = step("for", lambda: g.loop_in("for", W, DI(F), tuple(POS["for"])))
    nb = sorted(set(uidl(W, "Diagram")) - d0)
    s.gate("B1a For loop #{0} on #{1} with ONE body {2}".format(fl, F, nb), bool(fl) and len(nb) == 1 and not made["for"]["err"], (fl, nb), fatal=True)
    bd = nb[0] if nb else fl
    sv0 = set(uidl(W, "SubVI"))
    step("imaq", lambda: g.drop_subvi(W, PA["imaq_create"], DI(bd), tuple(POS["imaq"])))
    im = (sorted(set(uidl(W, "SubVI")) - sv0) or [0])[0]
    dn = {"donor": DONOR, "uid": rec["names"]}
    step("names", lambda: g.create_primitive_nested(W, F, "pool_names", tuple(POS["names"]), donor=dn))
    for k in ("c20a", "c20b"):
        step(k, lambda k=k: g.create_primitive_nested(W, F, "i32_20", tuple(POS[k]), donor={"donor": DONOR, "uid": rec["i32"]}))
    step("ring", lambda: g.create_primitive_nested(W, bd, "ring_dup", tuple(POS["ring"]), donor={"donor": W, "uid": Q["ring"]}))
    for k in ("obt_free", "obt_work"):
        step(k, lambda k=k: g.queue_node("obtain", W, "SubVI", idx(uidl(W, "SubVI"), Q["imaq"]), T["imaq_out"], DI(F), tuple(POS[k])))
    of = (made["obt_free"]["ret"] or [0])[0]
    step("enq", lambda: g.queue_node("enqueue", W, "Function", idx(uidl(W, "Function"), of), T["q_out"], DI(bd), tuple(POS["enq"])))
    dc = dict((c, sorted(g.uids(W, c) - c0[c])) for c in c0)
    s.fact("NEW OBJECTS by class {0}; IMAQ #{1}; body #{2}".format(dc, im, bd))
    s.gate("B1 every create returned without error", all(not v["err"] for v in made.values()), dict((k, v["err"]) for k, v in made.items()))
    s.gate("B1b census: ForLoop +1, SubVI +1 (IMAQ), Function +3 (2 Obtain + Enqueue), LoopTunnel +1 (the Enqueue's)",
           [len(dc[c]) for c in ("ForLoop", "SubVI", "Function", "LoopTunnel")] == [1, 1, 3, 1], dict((c, len(v)) for c, v in dc.items()))
    lv = {"terminals": G0["terminals"]} if DRY else K.mod("wiki_build").read_live(W, fs_pairs=G0["fs_tunnel_pairs"])
    L, old = lv["terminals"], dict((int(r["term_uid"]), r) for r in G0["terminals"])
    new = [r for r in L if int(r["term_uid"]) not in old]
    chg = [(r["term_uid"], old[int(r["term_uid"])]["wire_uid"], r["wire_uid"]) for r in L if int(r["term_uid"]) in old and r["wire_uid"] != old[int(r["term_uid"])]["wire_uid"]]
    for r in new:
        s.fact("NEWROW {0}".format(json.dumps(r)))
    s.fact("CHANGED OLD ROWS (term, wire before, wire now) {0}".format(chg))
    row = lambda u, n, src=False: next((r for r in L if int(r["owner_uid"]) == int(u) and r["term_name"] == n and bool(r["is_source"]) == src), {})   # noqa: E731
    rd = P0M.read_num(W, Q["ring"]), P0M.read_num(W, made["ring"]["ret"] or 0)
    s.fact("RING #{0} {1} | dup {2}".format(Q["ring"], json.dumps(rd[0], default=str)[:LN], json.dumps(rd[1], default=str)[:LN]))
    hx = lambda r: (r.get("RingConstant") or {}).get("hex") if isinstance(r.get("RingConstant"), dict) else None   # noqa: E731
    r0 = next((r for r in L if int(r["owner_uid"]) == Q["ring"]), {})
    s.gate("B2 ring dup bytes == #{0}'s (RingConstant route), #{0} still on #{1} on its old wire".format(Q["ring"], F),
           hx(rd[0]) and hx(rd[0]) == hx(rd[1]) and r0.get("frame_diagram") == F and r0.get("wire_uid") == old.get(int(r0.get("term_uid") or 0), {}).get("wire_uid"),
           (hx(rd[0]), hx(rd[1]), r0))
    nm = P0M.read_str(W, made["names"]["ret"] or 0)
    s.fact("NAMES const read {0}".format(json.dumps(nm)[:LN]))
    s.fact("I32 reads {0}".format([json.dumps(P0M.read_num(W, made[k]["ret"] or 0), default=str)[:LN] for k in ("c20a", "c20b")]))
    s.gate("B2b the scratch names constant bytes end in the flattened Cam_pool00..19", nm.get("hex", "").endswith(FLAT), nm.get("hex", "")[-LN // 7:])
    ni = row(Q["imaq"], T["imaq_out"], True).get("wire_uid")
    obs = [row(u, T["obt_type"]).get("wire_uid") for u in (made["obt_free"]["ret"] or []) + (made["obt_work"]["ret"] or [])]
    s.gate("B3 both Obtain 'element data type' on #{0}.New Image's wire w{1} (the PD234(d) branch); no old row changed its wire".format(Q["imaq"], ni),
           bool(ni) and obs == [ni, ni] and not chg, (obs, chg[:10]))
    eq = (made["enq"]["ret"] or [0])[0]
    qw = row(eq, T["enq_queue"]).get("wire_uid")
    tin = [r for r in new if r["owner_class"] == "LoopTunnel" and r["wire_uid"] == qw and r["is_source"]]
    s.gate("B3b Enqueue #{0} 'queue' wired (w{1}) from a NEW LoopTunnel's inner face".format(eq, qw), bool(qw) and len(tin) == 1, tin)
    tun = [g.tunnels(W, i) for i, u in enumerate(uidl(W, "LoopTunnel")) if u in dc["LoopTunnel"]] if not DRY else []
    s.fact("NEW TUNNEL(S) {0}".format(json.dumps(tun, default=str)[:LN]))
    s.R["p1"] = {"made": made, "new_by_class": dc, "imaq": im, "body": bd, "new_rows": new, "changed_old_rows": chg, "ring": rd,
                 "names_read": nm, "donor": rec, "tunnels": tun}
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
