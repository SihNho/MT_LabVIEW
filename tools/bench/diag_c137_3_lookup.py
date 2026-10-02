r"""diag_c137_3_lookup - card 137-3 (PD304(a)): scratch-VI check of the per-node LOOKUP that stopped 136-3 and 137-1 at #29466
(const_donor I32 0 made in the NEW While body #29431; on no node_labels row of the 180 Diagram indices, diag_c137_1_routes.log:27,36-48).
FOUND, nothing new built: gscript.node_labels:824 (OpNodeLabels_v0 = Diagram.Nodes[]) and _node_index:3639 (same op); Stage.address
stagekit.py:777 (report_all Diagram + node_labels); allterms.read_terms:68 (OpAllTerms_v1: owner_uid + frame_diagram); creators
gscript.loop_in:1507 and create_primitive_nested:4782 (Node delta, Constant fallback :4834); empty VI = claudeDev\EMPTY_v0.vi
(build_empty_vi.py). Leg A = a byte copy of EMPTY_v0 (a NEW empty VI; loop_in's source is Traverse SubVI[0], absent there, so on a
loop_in error leg A falls back to gscript.while_loop:1543 and says so). Leg B = the Stage work copy of the bed (never saved), While on
#23166 as 137-1. Per leg: While -> KS const_donor (DonorSRInit_v0 #248, the 137-1 ks route) in the body -> IAI Index Array (bed #3163,
donor = the B work copy, the 137-1 iai route) in the body. Reads per leg: Diagram count D0/D1/D2; node_labels of EVERY Diagram index (+
the body index's uid list); Traverse Node / Constant membership; read_terms rows by owner uid; Stage.address (self.work swapped to the
leg's VI for leg A). found / not found are ROWs (no prediction on them); records -> scratch_verify/<function>_c137_3_<ts>.json.
PREDICTION (gates): every op err ''; ONE new Diagram per While; both creates return a uid; 4 records written; H2-H6 hygiene; LabVIEW gone.
WHOLE-VI READS on the bed (leg B): D0 D1 D2 Node Constant read_terms + address x2 (report_all Diagram) = 8; N 3 ops (+3 on leg A, tiny VI)
-> 606.1 + 9*2.53 + 6*1.38 + 17.4 = 654.5 MB <= 690 (X10 model terms of diag_c137_1_prerun.log:99).
py tools/bgrun.py --material --max-min 22 --log tools/bench/diag_c137_3_lookup.log -- py -u tools/bench/diag_c137_3_lookup.py"""
import json, os, sys, time                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes")); import stagekit as K; g = K.g   # noqa: E402,E702
PL = json.load(open(os.path.join(HERE, "diag_c137_3_lookup_plan.json"), encoding="utf-8"))
BED, BEDM, P, EMPTY, KD = PL["input"]["vi"], PL["input"]["md5"], PL["parent"], os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi"), PL["donors"]["k_i32_0"]
def pos(leg, k): return tuple(PL["pos"][leg][k])                                            # noqa: E704
DRY, OUT, AT = bool(getattr(g.report_all, "_dry", False)), {}, K.mod("allterms")
s = K.Stage(BED, BEDM, "scratch_c137_3_lookup", preload=False, deadline_min=20, reserve_s=150, out_json=os.path.join(HERE, "diag_c137_3_lookup.json"), task="card 137-3")
def diags(W): return [] if DRY else [int(r["uid"]) for r in g.report_all(W, "Diagram")]   # Traverse 'Diagram' order = index    # noqa: E704
def create(tag, W, dg, prim, pos, donor):
    u = s._op("create_primitive_nested", lambda: g.create_primitive_nested(W, dg, prim, pos, donor=donor), "%s %s in #%s" % (tag, prim, dg))["result"]
    s.gate("C %s op err '' and a node uid" % tag, DRY or u, u); return 0 if DRY else int(u or 0)   # noqa: E702
def addr(W, end, src):                                                                      # Stage.address reads self.work
    w0 = s.work; s.work = W                                                                 # noqa: E702
    try: return "found", str(s.address(end, src))                                           # noqa: E701
    except Exception as e: return ("not found" if "not in Diagram" in str(e) else "error"), "%s: %s" % (type(e).__name__, str(e)[:160])   # noqa: E701
    finally: s.work = w0                                                                    # noqa: E701
def leg(tag, W, pidx, pws, pks, pia):
    o = OUT[tag] = {"vi": os.path.basename(W)}; D0 = diags(W); pi = pidx(D0); o["D0_n"], o["parent_index"] = len(D0), pi   # noqa: E702
    r = s._op("loop_in", lambda: g.loop_in("while", W, pi, pws), "%s while on Diagram[%s]" % (tag, pi)); o["while_route"] = "loop_in"   # noqa: E702
    if r["err"] and tag == "A":
        o["loop_in_err"], o["while_route"] = r["err"], "while_loop (loop_in err)"; r = s._op("while_loop", lambda: g.while_loop(W, pws), "A while on top level")   # noqa: E702
    ws, D1 = r["result"], diags(W); new = [u for u in D1 if u not in D0]; wb = new[0] if len(new) == 1 else 0   # noqa: E702
    s.gate("%s1 While #%s err '' with ONE new body Diagram %s" % (tag, ws, new), DRY or (ws and not r["err"] and len(new) == 1), r["err"])
    ks = create(tag + " ks", W, wb, "const_donor", pks, KD); ia = create(tag + " iai", W, wb, "Index Array", pia, {"donor": s.work, "uid": PL["donors"]["ia"]["uid"]})   # noqa: E702
    D2 = diags(W); bi = D2.index(wb) if wb in D2 else None                                  # noqa: E702
    o.update({"while": ws, "body": wb, "ks": ks, "iai": ia, "D1_n": len(D1), "D2_n": len(D2), "body_index_D1": D1.index(wb) if wb in D1 else None, "body_index_D2": bi})
    s.fact("%s DIAGRAM COUNT before While %s, after While %s, after creates %s; body #%s at index %s (D1) / %s (D2)" % (tag, len(D0), len(D1), len(D2), wb, o["body_index_D1"], bi))
    if DRY: return o                                                                        # noqa: E701
    nl, errs = {}, []
    for d in range(len(D2)):
        rows, e = g.node_labels(W, d, strict=False); nl[d] = [int(x["uid"]) for x in rows]; e and errs.append((d, e))   # noqa: E702
    o["node_labels_errors"], o["body_index_uids"] = errs[:5], nl.get(bi)
    s.fact("%s node_labels: %d indices read, %d with error %s; body index %s uids %s" % (tag, len(nl), len(errs), errs[:3], bi, nl.get(bi)))
    Nn, Cc = g.uids(W, "Node"), g.uids(W, "Constant"); rt = AT.read_terms(W, op=AT.OP_ALLTERMS_V1)[0]   # noqa: E702
    for nm, u, term, src in (("const", ks, None, True), ("prim", ia, PL["names"]["ia_idx"], False)):
        hit = [d for d, us in nl.items() if u in us]; tr = [(x["term_uid"], x["term_name"], x["is_source"], x["wire_uid"], x.get("frame_diagram")) for x in rt if x["owner_uid"] == u]
        if term is None: term = ([x[1] for x in tr if x[2]] or [""])[0]                     # noqa: E701
        ad = addr(W, {"uid": u, "diagram": wb, "owner_class": "Node", "term_class": "", "term": term}, src)
        m = o[nm] = {"uid": u, "node_labels_indices": hit, "traverse_Node": u in Nn, "traverse_Constant": u in Cc, "read_terms_rows": tr, "address": ad}
        for meth, v in (("node_labels per Diagram index", "found on %s" % hit if hit else "not found"), ("Traverse Node", m["traverse_Node"]), ("Traverse Constant", m["traverse_Constant"]),
                        ("read_terms by owner uid", "found %d row(s) %s" % (len(tr), tr[:3]) if tr else "not found"), ("Stage.address", "%s %s" % ad)):
            s.row("%s %s #%s %s" % (tag, nm, u, meth), v)
    return o
def body(_):
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    for tag, fn in (("B", lambda: leg("B", W, lambda D: D.index(P) if P in D else 0, pos("B", "ws"), pos("B", "ks"), pos("B", "iai"))),
                    ("A", lambda: leg("A", s.scratch("A", source=EMPTY), lambda D: 0, pos("A", "ws"), pos("A", "ks"), pos("A", "iai")))):
        try: fn(); s.gate("%s leg completed" % tag, True)                                   # noqa: E701,E702
        except Exception as e: OUT.setdefault(tag, {})["exc"] = "%s: %s" % (type(e).__name__, str(e)[:200]); s.gate("%s leg completed" % tag, False, OUT[tag]["exc"])   # noqa: E701,E702
    if DRY: return                                                                          # noqa: E701
    legs = [OUT.get(t, {}) for t in ("A", "B")]
    def ok(fn): return all(fn(o.get("const") or {}) and fn(o.get("prim") or {}) for o in legs)   # noqa: E704
    recs = {"gscript.node_labels": ok(lambda m: m.get("node_labels_indices")), "allterms.read_terms": ok(lambda m: m.get("read_terms_rows")),
            "stagekit.address": ok(lambda m: (m.get("address") or ("",))[0] == "found"),
            "gscript.report_all": all(o.get("D1_n", 0) == o.get("D0_n", -9) + 1 == o.get("D2_n", -9) for o in legs)}
    n = 0
    for fn, st in recs.items():
        p = os.path.join(HERE, "scratch_verify", "%s_c137_3_%s.json" % (fn, s.stamp))
        json.dump({"function": fn, "variant": "c137-3 lookup of a const + a primitive in a NEW While body (A empty VI, B bed copy)", "status": "PASS" if st else "FAIL",
                   "t": time.time(), "card": "137-3", "log": "tools/bench/diag_c137_3_lookup.log", "out": OUT}, open(p, "w", encoding="utf-8"), default=str, indent=1); n += 1   # noqa: E702
        s.fact("RECORD %s %s -> %s" % (fn, "PASS" if st else "FAIL", os.path.basename(p)))
    s.gate("R 4 scratch_verify records written", n == 4, n)
    json.dump(OUT, open(os.path.join(HERE, "diag_c137_3_lookup_out.json"), "w", encoding="utf-8"), default=str, indent=1)
if __name__ == "__main__":
    rc = K.run(body, s); DRY or K.mod("stagexec").kill_labview_at_exit(); sys.exit(rc)     # noqa: E702
