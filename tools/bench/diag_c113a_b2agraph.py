r"""diag_c113a_b2agraph - card 113-1 P0: the SAVED L2-B2a file's graph, READ-ONLY on a SCRATCH byte copy
(claudeDev\scratch_c113a_b2a_<ts>.vi, deleted), no VI run, no save, LabVIEW killed at the end; then an OFFLINE diff against the
B1 graph (tools/bench/graph_l2b1_20260927.json, md5 8327f974) by term_uid.
PRIOR ART (copied, not rebuilt): tools/bench/diag_c111b_b1graph.py (read_live + mloops + owner_of on a byte copy, card 111-2) - only
the input pin, the output name and the N gate change. No new op, no new verb.
OUTPUT tools/bench/graph_l2b2a_<date>.json (same shape as graph_l2b1) + tools/bench/graph_l2b2a_diff_<date>.json.
PREDICTION: K1 B2a md5 107a3ef1; K0 no LabVIEW before; K2 byte copy; O every Diagram owned; N B2a added no object and removed
none (7 wire rows only); H LabVIEW gone, input md5 unchanged, scratch deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c113a_b2agraph.log -- py -u tools/bench/diag_c113a_b2agraph.py"""
import collections, hashlib, json, os, subprocess, shutil, sys, time               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V        # noqa: E401,E402
B2A, B2A_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_b2a_20260928_001426.vi"), "107a3ef12da41b25d533f8a4c761aae8"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c113a_b2a_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_l2b2a_20260928.json")
DOUT = os.path.join(HERE, "graph_l2b2a_diff_20260928.json")
BASE = json.load(open(os.path.join(HERE, "graph_l2b1_20260927.json"), encoding="utf-8"))
SR = [9603, 10544, 25545, 25582]
EXTRA_OWN = [9018, 9025, 29505, 29512, 637, 10170, 23032, 23041, 1359, 29874, 8741, 30331, 6104, 9833, 2222, 2276, 29172] + SR
LOOPS = {637: "1.1", 10170: "1.2", 23041: "1.7", 23032: "1.5"}
FOCUS = ("IndexArray", "Case", "Selector", "ShiftRegister", "BuildArray", "GrowableFunction", "LoopTunnel")
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
    return {"vi": B2A, "md5": B2A_MD5, "source": "tools/bench/diag_c113a_b2agraph.py (read_live + mloops + owner_of, byte copy)",
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
                     "b1": ra and [ra[0], ra[1], ra[2]["term_name"]], "b2a": rb and [rb[0], rb[1], rb[2]["term_name"]]})
    ua, ub = set(int(o["uid"]) for o in BASE["objs"]), set(int(o["uid"]) for o in gr["objs"])
    new = [{"uid": int(o["uid"]), "class": o["class"]} for o in gr["objs"] if int(o["uid"]) not in ua]
    gone = [{"uid": int(o["uid"]), "class": o["class"]} for o in BASE["objs"] if int(o["uid"]) not in ub]
    for d in diff:
        print("  FACT DIFF {0}".format(json.dumps(d, default=str)), flush=True)
    print("  FACT NEW OBJ {0}".format(new[:60]), flush=True)
    print("  FACT GONE OBJ {0}".format(gone[:60]), flush=True)
    # prediction corrected after run 1 (diag_c113a_b2agraph.log): the only new non-Wire objects are the 4 terminals D4
    # accepted in 112-4 ('disabled index (col)' on #8741 x2 and #30331 x2, stage_d1_l2b2a_r2.log:119-125)
    rows = dict((int(r["term_uid"]), r) for r in gr["terminals"])
    nw = [n for n in new if n["class"] != "Wire"]
    d4t = sorted((int(rows[n["uid"]]["owner_uid"]), rows[n["uid"]]["term_name"]) for n in nw if n["uid"] in rows)
    gate("N B2a's new non-Wire objects are exactly the 4 D4-accepted terminals ('disabled index (col)' #8741 x2, #30331 x2); none removed",
         d4t == [(8741, "disabled index (col)")] * 2 + [(30331, "disabled index (col)")] * 2 and len(nw) == 4
         and not [x for x in gone if x["class"] != "Wire"], (d4t, [x for x in gone if x["class"] != "Wire"][:20]))
    # review archive/peer/2026-09-28-c113a-graph.md (cheapest test 1-3): pin the uids, the class counts, and the attributes the
    # state() tuple does not compare (is_source / owner / frame_diagram / term_class); only 9089 and 29923 may flip
    gate("N2 the new non-Wire uids == {25829, 25854, 25862, 25961}", set(n["uid"] for n in nw) == {25829, 25854, 25862, 25961},
         sorted(n["uid"] for n in nw))
    ca = collections.Counter(o["class"] for o in BASE["objs"])
    cb = collections.Counter(o["class"] for o in gr["objs"])
    dc = dict((k, cb[k] - ca[k]) for k in set(ca) | set(cb) if cb[k] != ca[k])
    gate("N3 object class counts B2a - B1 == {Terminal: +4, Wire: +5}", dc == {"Terminal": 4, "Wire": 5}, dc)
    at = lambda r: (bool(r["is_source"]), int(r["owner_uid"]), int(r.get("frame_diagram") or 0), r.get("term_class"))   # noqa: E731
    ra, rb = dict((int(r["term_uid"]), r) for r in BASE["terminals"]), rows
    flips = sorted(t for t in set(ra) & set(rb) if at(ra[t]) != at(rb[t]) and t not in set(d["term_uid"] for d in diff))
    for t in flips:
        print("  FACT ATTR-ONLY CHANGE t{0}: {1} -> {2}".format(t, at(ra[t]), at(rb[t])), flush=True)
    gate("N4 terminals whose (is_source, owner, frame_diagram, term_class) changed outside the diff rows == [9089, 29923]",
         flips == [9089, 29923], flips)
    json.dump({"diff": diff, "new": new, "gone": gone}, open(DOUT, "w", encoding="utf-8"), default=str, indent=0)
    print("  FACT WROTE {0} md5 {1} ({2} diff rows)".format(DOUT, md5(DOUT), len(diff)), flush=True)


def main():
    gate("K1 B2a md5 == pin", md5(B2A) == B2A_MD5, md5(B2A))
    if sys.argv[1:2] == ["offline"]:                                               # re-run the diff on the saved read, no LabVIEW
        gr = json.load(open(OUT, encoding="utf-8"))
        offline(gr)
        return finish(gr)
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or md5(B2A) != B2A_MD5:
        return finish(None)
    shutil.copyfile(B2A, SCR)
    gate("K2 scratch is a byte copy", md5(SCR) == B2A_MD5, SCR)
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
        gate("H LabVIEW gone; input md5 unchanged; scratch deleted", gone and md5(B2A) == B2A_MD5 and not os.path.exists(SCR),
             (gone, md5(B2A), os.path.exists(SCR)))
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
