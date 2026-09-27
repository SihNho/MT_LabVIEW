r"""diag_c114_b2bgraph - card 114-1 P1: the SAVED L2-B2b file's graph, READ-ONLY on a SCRATCH byte copy
(claudeDev\scratch_c114_b2b_<ts>.vi, deleted), no VI run, no save, LabVIEW killed at the end; then an OFFLINE diff against the
B2a graph (tools/bench/graph_l2b2a_20260928.json, md5 42fb5993) by term_uid.
PRIOR ART (copied, not rebuilt): tools/bench/diag_c113a_b2agraph.py (read_live + mloops + owner_of on a byte copy) - only the
input pin, the output name and the N gates change. No new op, no new verb.
OUTPUT tools/bench/graph_l2b2b_20260928.json (same shape as graph_l2b2a) + tools/bench/graph_l2b2b_diff_20260928.json.
PREDICTION: K1 B2b md5 4f51fd4c; K0 no LabVIEW before; K2 byte copy; O every Diagram owned; N the B2b diff touches ONLY the
nodes of plan_l2b2b.json's 8 rows + their wires/terminals (reported, gated only on "no non-Wire object removed"); B3's six
endpoints (#27605 t27635, #28370, #5183 t5186, #2992, #5669 t5671, #3176) are present; H LabVIEW gone, input md5 unchanged,
scratch deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c114_b2bgraph.log -- py -u tools/bench/diag_c114_b2bgraph.py"""
import collections, hashlib, json, os, subprocess, shutil, sys, time               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V        # noqa: E401,E402
BED, BED_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_b2b_20260928_015450.vi"), "4f51fd4cb93e9116dee1bc0b07281f12"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c114_b2b_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_l2b2b_20260928.json")
DOUT = os.path.join(HERE, "graph_l2b2b_diff_20260928.json")
BASE = json.load(open(os.path.join(HERE, "graph_l2b2a_20260928.json"), encoding="utf-8"))
SR = [9603, 10544, 25545, 25582]
EXTRA_OWN = [9018, 9025, 29505, 29512, 637, 10170, 23032, 23041, 1359, 29874, 8741, 30331, 6104, 9833, 2222, 2276, 29172,
             27605, 28370, 5183, 2992, 5669, 3176, 28343, 5129, 5328] + SR
B3_ENDS = [(27605, None), (28370, None), (5183, 5186), (2992, None), (5669, 5671), (3176, None)]
gates = []


class S(object):
    def safe(self, label, fn, default=None):
        try:
            return fn(), ""
        except Exception as e:                                                     # noqa: BLE001
            print("  FACT {0} raised {1}".format(label, str(e)[:200]), flush=True)
            return default, str(e)


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def read():
    lv = K.mod("wiki_build").read_live(SCR, fs_pairs=BASE["fs_tunnel_pairs"])
    print("  FACT LIVE {0} terminal rows, {1} objs, secs {2}".format(len(lv["terminals"]), len(lv["objs"]), lv["secs"]), flush=True)
    loops = K.mod("k_contract_79").mloops(S(), SCR)
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo, BD = {}, diags + EXTRA_OWN, K.mod("build_d1_v0")
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        try:
            v = BD.owner_of(SCR, u, strict=False)
        except Exception as e:                                                     # noqa: BLE001
            v = ("?", 0); print("  FACT owner_of #{0} raised {1}".format(u, str(e)[:120]), flush=True)   # noqa: E702
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    gate("O every live Diagram uid ({0}) has a resolved owner".format(len(diags)), all(O[d][0] != "?" for d in diags),
         sorted(d for d in diags if O[d][0] == "?")[:20])
    return {"vi": BED, "md5": BED_MD5, "source": "tools/bench/diag_c114_b2bgraph.py (read_live + mloops + owner_of, byte copy)",
            "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": BASE["fs_tunnel_pairs"],
            "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}


def state(gr):
    byw = {}
    for r in gr["terminals"]:
        if int(r["wire_uid"] or 0):
            byw.setdefault(int(r["wire_uid"]), []).append(r)
    st = {}
    for r in gr["terminals"]:
        w = int(r["wire_uid"] or 0)
        srcs = sorted((int(x["owner_uid"]), x["term_name"]) for x in byw.get(w, []) if x["is_source"] and x is not r) if w else []
        st[int(r["term_uid"])] = (bool(w), srcs, r)
    return st


def offline(gr):
    a, b = state(BASE), state(gr)
    diff = []
    for t in sorted(set(a) | set(b)):
        ra, rb = a.get(t), b.get(t)
        if ra and rb and (ra[0], ra[1], ra[2]["term_name"]) == (rb[0], rb[1], rb[2]["term_name"]):
            continue
        r = (rb or ra)[2]
        diff.append({"term_uid": t, "owner_uid": r["owner_uid"], "owner_class": r["owner_class"], "is_source": r["is_source"],
                     "b2a": ra and [ra[0], ra[1], ra[2]["term_name"]], "b2b": rb and [rb[0], rb[1], rb[2]["term_name"]]})
    ua, ub = set(int(o["uid"]) for o in BASE["objs"]), set(int(o["uid"]) for o in gr["objs"])
    new = [{"uid": int(o["uid"]), "class": o["class"]} for o in gr["objs"] if int(o["uid"]) not in ua]
    gone = [{"uid": int(o["uid"]), "class": o["class"]} for o in BASE["objs"] if int(o["uid"]) not in ub]
    for d in diff:
        print("  FACT DIFF {0}".format(json.dumps(d, default=str)), flush=True)
    print("  FACT NEW OBJ {0}".format(new[:80]), flush=True)
    print("  FACT GONE OBJ {0}".format(gone[:80]), flush=True)
    ca = collections.Counter(o["class"] for o in BASE["objs"])
    cb = collections.Counter(o["class"] for o in gr["objs"])
    print("  FACT CLASS COUNT DELTA {0}".format(dict((k, cb[k] - ca[k]) for k in set(ca) | set(cb) if cb[k] != ca[k])), flush=True)
    gate("N no non-Wire object of B2a is gone in B2b", not [x for x in gone if x["class"] != "Wire"],
         [x for x in gone if x["class"] != "Wire"][:20])
    rows = dict((int(r["term_uid"]), r) for r in gr["terminals"])
    cls = dict((int(o["uid"]), o["class"]) for o in gr["objs"])
    miss = [(u, t) for u, t in B3_ENDS if u not in cls or (t and t not in rows)]
    gate("N2 B3 endpoints present (#27605, #28370, #5183 t5186, #2992, #5669 t5671, #3176)", not miss, miss)
    for u, _t in B3_ENDS:
        for r in [x for x in gr["terminals"] if int(x["owner_uid"]) == u]:
            print("  FACT B3END #{0} {1} t{2} {3!r} src={4} w{5} fd{6}".format(u, cls.get(u), r["term_uid"], r["term_name"],
                                                                           r["is_source"], r["wire_uid"], r.get("frame_diagram")),
                  flush=True)
    json.dump({"diff": diff, "new": new, "gone": gone}, open(DOUT, "w", encoding="utf-8"), default=str, indent=0)
    print("  FACT WROTE {0} md5 {1} ({2} diff rows)".format(DOUT, md5(DOUT), len(diff)), flush=True)


def main():
    gate("K1 B2b md5 == pin", md5(BED) == BED_MD5, md5(BED))
    if sys.argv[1:2] == ["offline"]:                                               # re-run the diff on the saved read, no LabVIEW
        gr = json.load(open(OUT, encoding="utf-8"))
        offline(gr)
        return finish(gr)
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or md5(BED) != BED_MD5:
        return finish(None)
    shutil.copyfile(BED, SCR)
    gate("K2 scratch is a byte copy", md5(SCR) == BED_MD5, SCR)
    gr = None
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        gr = read()
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        try:
            os.remove(SCR)
        except OSError as e:
            print("  FACT scratch not removed: {0}".format(e), flush=True)
        gate("H LabVIEW gone; input md5 unchanged; scratch deleted", gone and md5(BED) == BED_MD5 and not os.path.exists(SCR),
             (gone, md5(BED), os.path.exists(SCR)))
    if gr:
        json.dump(gr, open(OUT, "w", encoding="utf-8"))
        print("  FACT WROTE {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
        try:
            offline(gr)
        except Exception as e:                                                     # noqa: BLE001
            gate("OFFLINE diff ran", False, repr(e)[:300])
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    arts = [{"path": p, "md5": md5(p)} for p in (OUT, DOUT) if gr and os.path.exists(p)]
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=arts)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
