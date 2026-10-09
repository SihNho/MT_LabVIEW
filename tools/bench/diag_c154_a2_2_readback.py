# ---
# labview: build
# hardware: none
# ---
r"""diag_c154_a2_2_readback - card 154-a2-2 (brief_154-a2-2.md, retry of 154-a2-1): READ BACK the saved claudeDev\DonorQueue_v0.vi
(md5 81dba822...) and write tools/bench/donor_queue_v0.json. NO rebuild, NO SaveInstrument, NO panel open (read ops take the path).
EXISTING FIRST: the read-back half of diag_c154_a2_1_donor.py:36-55,82-97 copied; its bug was line 82 - g.node_labels(strict=False)
returns (rows, err) (gscript.py:857-858), not rows; rows are dicts {uid,label} (gscript.py:856). node_terms_uid -> (uid, rows
{i,name,is_source,wire,...}) (gscript.py:1153-1217); AT.read_terms rows {term_uid,term_name,is_source,owner_uid,owner_class,wire_uid}.
Shapes are printed once (SH) before use. Not on stagekit: stagekit wraps stage rows/plans, this is a pure reader (same form as 154-a2-1).
PREDICTION: P pins == brief md5s, donor md5 81dba822; SH shapes printed; R five objects: #52 ArrayConstant (element #73
DigitalNumericConstant), #108/#44/#45/#46 Function, each with >=1 terminal; J json written; H |h_after-h_before| <= 100 (before = ops
preloaded + one warm read); CR fresh LabVIEW re-read: same 5 uids + classes; X donor md5 still 81dba822, pins unchanged, LabVIEW gone.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c154_a2_2_readback.log -- py -u tools/bench/diag_c154_a2_2_readback.py"""
import glob, hashlib, json, os, subprocess, sys, time, traceback                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path[:0] = [TOOLS, HERE]   # noqa: E702
import gscript as g, bench_prep, protocol as P, allterms as AT                                  # noqa: E401,E402
CD, G, OUT = g.CLAUDEDEV, {}, {}
DON = os.path.join(CD, "DonorQueue_v0.vi"); DON_MD5 = "81dba822efec5226123b3b88ee4383bc"         # noqa: E702
JS = os.path.join(HERE, "donor_queue_v0.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest() if os.path.exists(p) else "MISSING"   # noqa: E731
WANT = {os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31", os.path.join(HERE, "memory_model.json"): "6f2b5687", DON: DON_MD5}
WANT.update((os.path.join(TOOLS, f), m) for f, m in (("stagekit.py", "604529e8"), ("stagexec.py", "1bab9cf9"), ("stagesim.py", "78b8d5a1"),
            ("gscript.py", "1a80236e"), ("stage_prerun.py", "c739eb86"), ("vigraph.py", "a7eb58c7"), ("addrcheck.py", "207beb0d")))
QOPS = [os.path.join(CD, "OpQueue%s_v0.vi" % k) for k in ("Obtain", "Enqueue", "Dequeue", "Release")]
PINS = list(WANT) + QOPS + sorted(p for p in glob.glob(os.path.join(CD, "Donor*.vi")) if p != DON)
PIN0 = dict((p, md5(p)) for p in PINS)
PRE = [g.OP_REPORT_ALL, g.OP_NODE_LABELS, g.OP_NODE_TERMS, AT.OP_ALLTERMS_V1]
Q = {"obtain": 108, "enqueue": 44, "dequeue": 45, "release": 46, "dbl_const": 52}; ELEM = 73   # log lines C1..Q of 154-a2-1   # noqa: E702
def fact(*a): print("  FACT  " + " ".join(str(x) for x in a)[:1500], flush=True)               # noqa: E302,E704
def rows(): return AT.read_terms(DON, op=AT.OP_ALLTERMS_V1)[0]                                 # noqa: E704
def labels():                                                                                   # noqa: E302
    r, err = g.node_labels(DON, 0, strict=False)
    return dict((int(x["uid"]), x["label"]) for x in r), err
def gate(label, ok, d=""):                                                                      # noqa: E302
    G[label] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)   # noqa: E702
    if not ok:
        raise RuntimeError("STOP at the first unexpected result: " + label)
    return True
def readobj(role, uid, R, L, order):                                                            # noqa: E302
    own = [x for x in R if x["owner_uid"] == uid]
    if uid in order:
        _u, nt = g.node_terms_uid(DON, 0, order.index(uid)); src = "node_terms_uid (node echo %s)" % _u   # noqa: E702
        gate("N node echo #%s" % uid, int(_u) == uid, _u)
        terms = [{"index": int(r["i"]), "name": r["name"], "is_source": bool(r["is_source"])} for r in nt]
    else:                                                                                       # a Constant is not in Diagram.Nodes[]
        src, terms = "allterms order (not in Nodes[])", [{"index": k, "name": x["term_name"], "is_source": x["is_source"]} for k, x in enumerate(own)]
    for t in terms:
        m = [x for x in own if x["term_name"] == t["name"] and x["is_source"] == t["is_source"]]
        t.update(term_uid=m[0]["term_uid"] if len(m) == 1 else None, wire_uid=(m[0]["wire_uid"] or None) if len(m) == 1 else None)
    return {"role": role, "uid": uid, "class": (own[0]["owner_class"] if own else None), "label": L.get(uid), "terminals": terms, "terminal_source": src}
try:
    fact("md5 BEFORE", dict((os.path.basename(p), m[:8]) for p, m in PIN0.items()))
    gate("P pins == brief md5 prefixes (donor 81dba822 included)", all(PIN0[p].startswith(w) for p, w in WANT.items()), [os.path.basename(p) for p, w in WANT.items() if not PIN0[p].startswith(w)])
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                     # noqa: E702
    [g.op(p) for p in PRE]; rows(); labels(); g.report_all(DON, "Constant")                    # noqa: E702  warm read
    time.sleep(2); OUT["h_before"] = g.lv_counts(); fact("handles BEFORE (ops preloaded, warm read done)", OUT["h_before"])   # noqa: E702
    R = rows(); (L, lerr) = labels(); order = [int(r["uid"]) for r in g.node_labels(DON, 0)]   # noqa: E702
    C = dict((int(o["uid"]), o["class"]) for o in g.report_all(DON, "Constant"))
    fact("SH read_terms row keys", sorted(R[0].keys()) if R else None, "n", len(R)); fact("SH node_labels(strict=False) -> (rows, err); row", (list(L.items())[:3], lerr))   # noqa: E702
    fact("SH Nodes[] order", order, "constants", C)
    _u, nt0 = g.node_terms_uid(DON, 0, order.index(108)); fact("SH node_terms_uid -> (uid, rows); row keys", _u, sorted(nt0[0].keys()) if nt0 else None)   # noqa: E702
    objs = [readobj(r, Q[r], R, L, order) for r in ("dbl_const", "obtain", "enqueue", "dequeue", "release")]
    objs[0]["element"] = {"uid": ELEM, "class": C.get(ELEM)}; objs[0]["class_report_all"] = C.get(52)
    for o in objs:
        fact("OBJ", json.dumps(o))
    want_cls = {"dbl_const": "ArrayConstant", "obtain": "Function", "enqueue": "Function", "dequeue": "Function", "release": "Function"}
    gate("R five objects, classes as predicted, every one has terminals, element #73 DigitalNumericConstant",
         all(o["class"] == want_cls[o["role"]] and o["terminals"] for o in objs) and C.get(ELEM) == "DigitalNumericConstant",
         [(o["role"], o["class"], len(o["terminals"])) for o in objs] + [C.get(ELEM)])
    rec = {"file": DON, "md5": md5(DON), "card": "154-a2-2", "built_by_card": "154-a2-1", "built_by": "tools/bench/diag_c154_a2_1_donor.py",
           "build_log": "tools/bench/diag_c154_a2_1_donor.log", "read_by": "tools/bench/diag_c154_a2_2_readback.py", "exec_state_at_build": 1,
           "objects": objs, "note": "E/D/R wired from Obtain 'queue out' by queue_node; DBL const = DonorRingConst_v0 #101 copy (DBL[20] 0.0); "
           "const 'x,y,z array' t51 -> w82 -> Obtain 'element data type' + Enqueue 'element'"}
    json.dump(rec, open(JS, "w", encoding="utf-8"), indent=1, default=str)
    gate("J json written (md5 of VI == 81dba822)", os.path.exists(JS) and rec["md5"] == DON_MD5, md5(JS))
    time.sleep(2); OUT["h_after"] = g.lv_counts(); fact("handles AFTER (read-back done, nothing saved)", OUT["h_after"])   # noqa: E702
    gate("H handles |after - before| <= 100", abs(OUT["h_after"]["handles"] - OUT["h_before"]["handles"]) <= 100, (OUT["h_before"]["handles"], OUT["h_after"]["handles"]))
    g.reset(); fact("ref_counts after reset", g.ref_counts())                                  # noqa: E702
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                     # noqa: E702
    R2 = dict((x["owner_uid"], x["owner_class"]) for x in rows()); C2 = dict((int(o["uid"]), o["class"]) for o in g.report_all(DON, "Constant"))   # noqa: E702
    fact("CR cold classes", dict((o["role"], (o["uid"], R2.get(o["uid"]))) for o in objs), "elem", C2.get(ELEM))
    gate("CR cold re-read: the 5 uids + classes == json, element #73 same", all(R2.get(o["uid"]) == o["class"] for o in objs) and C2.get(ELEM) == C.get(ELEM), R2)
    gate("CR donor md5 unchanged by the cold read", md5(DON) == DON_MD5, md5(DON))
except Exception as e:                                                                          # noqa: BLE001
    traceback.print_exc(); G.setdefault("the run completed without an unexpected result", False); fact("STOP", repr(e)[:400])   # noqa: E702
finally:
    try:
        g.reset(); fact("ref_counts", g.ref_counts())                                            # noqa: E702
    except Exception as e:                                                                      # noqa: BLE001
        fact("close-out read raised", repr(e)[:200])
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)   # noqa: E702
    G["X LabVIEW gone (tasklist)"] = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    PIN1 = dict((p, md5(p)) for p in PINS); G["X pins unchanged (donor 81dba822 included)"] = PIN1 == PIN0
    fact("pins changed", [os.path.basename(p) for p in PINS if PIN1[p] != PIN0[p]], "donor md5", md5(DON))
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    arts = [{"path": p, "md5": md5(p)} for p in (DON, JS) if os.path.exists(p)]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
