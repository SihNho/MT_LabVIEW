# ---
# labview: build
# hardware: none
# ---
r"""diag_c154_a2_1_donor - card 154-a2-1 (brief_154-a2-1.md, docs/d1/ring-p5.md PD375(a)): build claudeDev\DonorQueue_v0.vi BY SCRIPT.
EXISTING FIRST: donor build form = EMPTY_v0 copied to the donor path, open_panel, create, ExecState 1, g.save (diag_c140_5_run.py:29-73,
diag_c139_3_run.py:26-35); queue nodes ONLY via gscript.queue_node (gscript.py:1480) as diag_c153_a2_8_queue_hygiene.py:78-90 (src 'Node'
named output for Obtain, then 'Function' Obtain 'queue out' for the others); 1-D DBL constant = DonorRingConst_v0 uid 101 (DBL[20] 0.0,
docs/d1-loop12-17-split-plan.md:2352) copied by create_primitive_nested (gscript.py:4790; PD375(a) names it). A Constant is not a Node, so
Get Outputs cannot take it as queue_node's src (docs/d1-build-plan.md:1069-1075): Obtain is typed first from a TEMPORARY Replace Array
Subset (DonorRAS1D_v0 uid 175 'output array'), the temp node is deleted + Remove Bad Wires (c122 donor form, diag_c122_hyg.py:40), then
the DBL constant is wired to 'element data type' and branched to Enqueue 'element' by connect_term_uid (gscript.py:5141). Reader: OpAllTerms_v1
(allterms.py:68) + node_terms_uid / node_labels. No new op. Enqueue/Dequeue/Release ARE wired from Obtain 'queue out' (queue_node always wires).
PREDICTION: P pins == brief md5s; S donor path absent; C1 const = 1 ArrayConstant; T1 temp RAS 1 node; O1 obtain 1 new Function; X temp gone;
W1 const->'element data type' err '' not broken; E/D/R 1 new Function each; W2 const->Enqueue.element ok; ES 1; SV saved by COM, md5;
H |h_after - h_before| <= 100 (before = after op preload + a warm read on a scratch EMPTY copy); CR cold read in a fresh LabVIEW: the 5 uids
+ classes == json; X LabVIEW gone, scratch gone, pins unchanged.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c154_a2_1_donor.log -- py -u tools/bench/diag_c154_a2_1_donor.py"""
import glob, hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path[:0] = [TOOLS, HERE]   # noqa: E702
import gscript as g, bench_prep, protocol as P, allterms as AT                                  # noqa: E401,E402
CD, TS, G, OUT = g.CLAUDEDEV, time.strftime("%Y%m%d_%H%M%S"), {}, {}
DON, EMPTY = os.path.join(CD, "DonorQueue_v0.vi"), os.path.join(CD, "EMPTY_v0.vi")
RC, RAS, WARM = os.path.join(CD, "DonorRingConst_v0.vi"), os.path.join(CD, "DonorRAS1D_v0.vi"), os.path.join(CD, "scratch_c154_a2_1_warm_%s.vi" % TS)
JS, FACTS = os.path.join(HERE, "donor_queue_v0.json"), os.path.join(HERE, "diag_c154_a2_1_facts.md")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"   # noqa: E731
WANT = {os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", os.path.join(HERE, "memory_model.json"): "6f2b5687"}
WANT.update((os.path.join(TOOLS, f), m) for f, m in (("stagekit.py", "604529e8"), ("stagexec.py", "1bab9cf9"), ("stagesim.py", "78b8d5a1"),
            ("gscript.py", "1a80236e"), ("stage_prerun.py", "c739eb86"), ("vigraph.py", "a7eb58c7"), ("addrcheck.py", "207beb0d")))
QOPS = [os.path.join(CD, "OpQueue%s_v0.vi" % k) for k in ("Obtain", "Enqueue", "Dequeue", "Release")]
PINS = list(WANT) + QOPS + sorted(p for p in glob.glob(os.path.join(CD, "Donor*.vi")) if p != DON)
PIN0 = dict((p, md5(p)) for p in PINS)
PRE = [g.OP_REPORT_ALL, g.OP_NODE_LABELS, g.OP_NODE_TERMS, g.OP_DELETE, g.OP_REMOVE_BAD_WIRES, AT.OP_ALLTERMS_V1] + QOPS + [
    os.path.join(CD, n) for n in ("OpPrimCopyNested_v0.vi", "OpConnectTermUid_v0.vi")]
def fact(*a): print("  FACT  " + " ".join(str(x) for x in a)[:1500], flush=True)               # noqa: E302,E704
def rows(t=DON): return AT.read_terms(t, op=AT.OP_ALLTERMS_V1)[0]                              # noqa: E704
def gate(label, ok, d=""):                                                                      # noqa: E302
    G[label] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)   # noqa: E702
    if not ok:
        raise RuntimeError("STOP at the first unexpected result: " + label)
    return True
def term(R, uid, src, name=None):                                                               # noqa: E302
    r = [x for x in R if x["owner_uid"] == uid and x["is_source"] == src and (name is None or x["term_name"] == name)]
    gate("T one terminal #%s src=%s name=%r" % (uid, src, name), len(r) == 1, [(x["term_uid"], x["term_name"]) for x in r]); return r[0]   # noqa: E702
def readobj(role, uid, R, labels):                                                              # noqa: E302
    own = [x for x in R if x["owner_uid"] == uid]
    try:
        _u, nt = g.node_terms_uid(DON, 0, g._node_index(DON, 0, uid)); src = "node_terms_uid"   # noqa: E702
        terms = [{"index": int(r["i"]), "name": r["name"], "is_source": bool(r["is_source"])} for r in nt]
    except ValueError as e:                                                                     # not in Diagram.Nodes[] (a Constant)
        src, terms = "allterms order (%s)" % str(e)[:80], [{"index": k, "name": x["term_name"], "is_source": x["is_source"]} for k, x in enumerate(own)]
    for t in terms:
        m = [x for x in own if x["term_name"] == t["name"] and x["is_source"] == t["is_source"]]
        t.update(term_uid=m[0]["term_uid"] if len(m) == 1 else None, wired=bool(m and m[0]["wire_uid"]))
    return {"role": role, "uid": uid, "class": (own[0]["owner_class"] if own else None), "label": labels.get(uid), "terminals": terms, "terminal_source": src}
try:
    fact("md5 BEFORE", dict((os.path.basename(p), m[:8]) for p, m in PIN0.items()))
    gate("P pins == brief md5 prefixes", all(PIN0[p].startswith(w) for p, w in WANT.items()), [os.path.basename(p) for p, w in WANT.items() if not PIN0[p].startswith(w)])
    gate("S DonorQueue_v0.vi does not exist yet (never saved over anything)", not os.path.exists(DON))
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                     # noqa: E702
    [g.op(p) for p in PRE]; shutil.copyfile(EMPTY, WARM); g.open_panel(WARM)                   # noqa: E702
    g.report_all(WARM, "Node"); g.node_labels(WARM, 0); rows(WARM); g.exec_state(WARM); g.close_panel(WARM)   # noqa: E702
    time.sleep(2); OUT["h_before"] = g.lv_counts(); fact("handles BEFORE (ops preloaded, warm read done)", OUT["h_before"])   # noqa: E702
    shutil.copyfile(EMPTY, DON); g.open_panel(DON); top = int(g.report_all(DON, "Diagram")[0]["uid"])   # noqa: E702
    c0 = g.uids(DON, "Constant"); k = int(g.create_primitive_nested(DON, top, "const_donor", (100, 200), donor={"donor": RC, "uid": 101}))   # noqa: E702
    gate("C1 const #%s is an ArrayConstant" % k, k in g.uids(DON, "ArrayConstant"), sorted(set(g.uids(DON, "Constant")) - set(c0)))
    t = int(g.create_primitive_nested(DON, top, "Replace Array Subset", (100, 450), donor={"donor": RAS, "uid": 175})); fact("T1 temp RAS", t)   # noqa: E702
    f0 = g.uids(DON, "Function"); ob = g.queue_node("obtain", DON, "Node", g._uid_index(DON, "Node", t), "output array", 0, (350, 200))   # noqa: E702
    gate("O1 obtain: one new Function", len(ob) == 1, ob); ob = int(ob[0])                      # noqa: E702
    gone = g.delete_object(DON, "Node", g._uid_index(DON, "Node", t)); OUT["rbw"] = g.remove_bad_wires_scripted(DON)   # noqa: E702
    gate("X temp RAS #%s deleted, Obtain #%s kept" % (t, ob), t in (gone or set()) and ob in g.uids(DON, "Function"), (gone, OUT["rbw"]))
    R = rows(); OUT["w1"] = g.connect_term_uid(DON, term(R, ob, False, "element data type")["term_uid"], term(R, k, True)["term_uid"])   # noqa: E702
    gate("W1 const -> Obtain 'element data type' err '' not broken", not OUT["w1"].get("err") and OUT["w1"].get("broken") is False, OUT["w1"])
    Q = {"obtain": ob}
    for n, (kind, xy) in enumerate((("enqueue", (650, 150)), ("dequeue", (650, 300)), ("release", (900, 220)))):
        new = g.queue_node(kind, DON, "Function", g._uid_index(DON, "Function", ob), "queue out", 0, xy)
        gate("Q %s: one new Function" % kind, len(new) == 1, new); Q[kind] = int(new[0])        # noqa: E702
    R = rows(); OUT["w2"] = g.connect_term_uid(DON, term(R, Q["enqueue"], False, "element")["term_uid"], term(R, k, True)["term_uid"])   # noqa: E702
    gate("W2 const -> Enqueue 'element' (branch) err '' not broken", not OUT["w2"].get("err") and OUT["w2"].get("broken") is False, OUT["w2"])
    Q["dbl_const"] = k; es = g.exec_state(DON); fact("ExecState", es); gate("ES DonorQueue_v0 ExecState 1", es == 1, es)   # noqa: E702
    g.save(DON); gate("SV saved by COM SaveInstrument", os.path.getsize(DON) > 0, md5(DON))     # noqa: E702
    R, L = rows(), dict((int(x["uid"]), x["label"]) for x in g.node_labels(DON, 0, strict=False))   # noqa: E702
    objs = [readobj(r, Q[r], R, L) for r in ("obtain", "enqueue", "dequeue", "release", "dbl_const")]
    for o in objs:
        fact("OBJ", json.dumps(o))
    rec = {"file": DON, "md5": md5(DON), "card": "154-a2-1", "log": "tools/bench/diag_c154_a2_1_donor.log", "built_by": "tools/bench/diag_c154_a2_1_donor.py",
           "exec_state": es, "wires": {"element data type": OUT["w1"], "enqueue element": OUT["w2"]}, "objects": objs,
           "note": "E/D/R wired from Obtain 'queue out' by queue_node; DBL const = DonorRingConst_v0 #101 copy (DBL[20] 0.0, not empty)"}
    json.dump(rec, open(JS, "w", encoding="utf-8"), indent=1, default=str)
    gate("J json: 5 objects, every class and terminal list read", all(o["class"] and o["terminals"] for o in objs), [o["role"] for o in objs if not (o["class"] and o["terminals"])])
    g.close_panel(DON); time.sleep(2); OUT["h_after"] = g.lv_counts(); fact("handles AFTER (donor closed, no second save)", OUT["h_after"])   # noqa: E702
    gate("H handles |after - before| <= 100", abs(OUT["h_after"]["handles"] - OUT["h_before"]["handles"]) <= 100, (OUT["h_before"]["handles"], OUT["h_after"]["handles"]))
    g.reset(); fact("ref_counts after reset", g.ref_counts()); m_saved = md5(DON)               # noqa: E702
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                     # noqa: E702
    R2 = dict((x["owner_uid"], x["owner_class"]) for x in rows()); fact("CR cold classes", dict((o["role"], (o["uid"], R2.get(o["uid"]))) for o in objs))   # noqa: E702
    gate("CR cold re-read: the 5 uids + classes == json", all(R2.get(o["uid"]) == o["class"] for o in objs), R2)
    gate("CR donor md5 unchanged by the cold read", md5(DON) == m_saved, md5(DON))
except Exception as e:                                                                          # noqa: BLE001
    traceback.print_exc(); G.setdefault("the run completed without an unexpected result", False); fact("STOP", repr(e)[:400])   # noqa: E702
finally:
    try:
        g.reset(); fact("ref_counts", g.ref_counts())                                            # noqa: E702
    except Exception as e:                                                                      # noqa: BLE001
        fact("close-out read raised", repr(e)[:200])
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)   # noqa: E702
    for _ in range(5):
        try:
            os.path.exists(WARM) and os.remove(WARM); break                                      # noqa: E702
        except OSError:
            time.sleep(2)
    G["X LabVIEW gone (tasklist)"] = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    G["X warm scratch deleted"] = not os.path.exists(WARM)
    PIN1 = dict((p, md5(p)) for p in PINS); G["X pins unchanged"] = PIN1 == PIN0
    fact("pins changed", [os.path.basename(p) for p in PINS if PIN1[p] != PIN0[p]], "donor md5", md5(DON))
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    arts = [{"path": p, "md5": md5(p)} for p in (DON, JS) if os.path.exists(p)]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
