r"""diag_c111b_b1graph - card 111-2 A2/A3: the SAVED L2-B1 file's graph, READ-ONLY on a SCRATCH byte copy
(claudeDev\scratch_c111b_b1_<ts>.vi, deleted), no VI run, LabVIEW killed at the end; then an OFFLINE diff against the L2-A3 bed
graph (tools/bench/graph_l2a3_bed_20260927.json, md5 f01e719d) by term_uid.
PRIOR ART (copied, not rebuilt): tools/bench/diag_c110_bedgraph.py (read_live + mloops + owner_of on a byte copy, 8/0) - only the
input, pins and the offline part change. No new op, no new verb.
OUTPUT tools/bench/graph_l2b1_<date>.json (same shape as graph_l2a3_bed) + tools/bench/graph_l2b1_diff_<date>.json.
PREDICTION: K1 B1 md5 b705728a; K0 no LabVIEW before; K2 byte copy; O every Diagram owned; N the 2 add_shift_reg pairs of
stage_d1_l2b1_c110d.log:498 (9603/10544, 25545/25582) are objects in B1 and NOT in L2-A3; H LabVIEW gone, input md5 unchanged,
scratch deleted. STRUCTURAL read.
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c111b_b1graph.log -- py -u tools/bench/diag_c111b_b1graph.py"""
import hashlib, json, os, subprocess, shutil, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, bench_prep, stagekit as K, vigraph as V        # noqa: E401,E402
B1, B1_MD5 = os.path.join(g.CLAUDEDEV, "D1_l2_b1_20260927_193100.vi"), "b705728ab0714dc8179fc955283800f9"
SCR = os.path.join(g.CLAUDEDEV, "scratch_c111b_b1_{0}.vi".format(time.strftime("%Y%m%d_%H%M%S")))
OUT = os.path.join(HERE, "graph_l2b1_{0}.json".format(time.strftime("%Y%m%d")))
DOUT = os.path.join(HERE, "graph_l2b1_diff_{0}.json".format(time.strftime("%Y%m%d")))
BASE = json.load(open(os.path.join(HERE, "graph_l2a3_bed_20260927.json"), encoding="utf-8"))
NEW_SR = [9603, 10544, 25545, 25582]
EXTRA_OWN = [9018, 9025, 29505, 29512, 637, 10170, 23032, 23041, 1359, 29874, 8741, 30331, 6104, 9833] + NEW_SR
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
    return {"vi": B1, "md5": B1_MD5, "source": "tools/bench/diag_c111b_b1graph.py (read_live + mloops + owner_of, byte copy)",
            "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": BASE["fs_tunnel_pairs"],
            "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}


def chain(gr, uid):
    """uid -> [(class, uid), ...] up to a loop in LOOPS or the top. objs carry only the owner CLASS, so a node's diagram is
    the frame_diagram of its terminal rows (or its owners entry), and a structure's diagram is its owners entry."""
    own = dict((int(k), v) for k, v in gr["owners"].items())
    fd = gr.setdefault("_fd", {})
    if not fd:
        for r in gr["terminals"]:
            fd.setdefault(int(r["owner_uid"]), int(r.get("frame_diagram") or 0))
    d = fd.get(uid) or (int(own[uid][1]) if uid in own and own[uid][0] == "Diagram" else 0)
    out = []
    for _ in range(30):
        if not d or d not in own:
            break
        s = own[d]
        out.append((s[0], int(s[1] or 0)))
        su = int(s[1] or 0)
        if su in LOOPS or not su:
            break
        d = fd.get(su) or (int(own[su][1]) if su in own and own[su][0] == "Diagram" else 0)
    return out


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
    for t in sorted(set(a) & set(b)):
        (wa, sa, ra), (wb, sb, rb) = a[t], b[t]
        if (wa, sa) != (wb, sb):
            diff.append({"term_uid": t, "owner_uid": rb["owner_uid"], "owner_class": rb["owner_class"], "term_name": rb["term_name"],
                         "is_source": rb["is_source"], "l2a3": [wa, sa], "b1": [wb, sb], "chain_b1": chain(gr, int(rb["owner_uid"])),
                         "chain_l2a3": chain(BASE, int(rb["owner_uid"]))})
    ua, ub = set(int(o["uid"]) for o in BASE["objs"]), set(int(o["uid"]) for o in gr["objs"])
    new = [{"uid": int(o["uid"]), "class": o["class"], "chain": chain(gr, int(o["uid"]))} for o in gr["objs"] if int(o["uid"]) not in ua]
    gone = [{"uid": int(o["uid"]), "class": o["class"]} for o in BASE["objs"] if int(o["uid"]) not in ub]
    for d in diff:
        if any(f in d["owner_class"] for f in FOCUS) and not d["is_source"]:
            print("  FACT DIFF {0}".format(json.dumps(d, default=str)), flush=True)
    print("  FACT DIFF classes {0}".format(sorted(set((d["owner_class"], d["is_source"]) for d in diff))), flush=True)
    for n in new:
        print("  FACT NEW OBJ {0}".format(n), flush=True)
    print("  FACT GONE OBJ {0}".format(gone[:60]), flush=True)
    srs = dict((u, [(r["term_uid"], r["term_class"], r["is_source"], r["wire_uid"]) for r in gr["terminals"] if int(r["owner_uid"]) == u])
               for u in NEW_SR + [9018, 9025, 29505, 29512])
    for u, rows in srs.items():
        print("  FACT SR #{0} chain {1} terms {2}".format(u, chain(gr, u), rows), flush=True)
    gate("N the 4 add_shift_reg uids are B1 objects not in L2-A3", all(u in ub and u not in ua for u in NEW_SR),
         [(u, u in ub, u in ua) for u in NEW_SR])
    json.dump({"diff": diff, "new": new, "gone": gone, "srs": srs}, open(DOUT, "w", encoding="utf-8"), default=str, indent=0)
    print("  FACT WROTE {0} md5 {1} ({2} diff rows)".format(DOUT, md5(DOUT), len(diff)), flush=True)


def main():
    gate("K1 B1 md5 == pin", md5(B1) == B1_MD5, md5(B1))
    if sys.argv[1:2] == ["offline"]:                                               # re-run the diff on the saved read, no LabVIEW
        gr = json.load(open(OUT, encoding="utf-8"))
        offline(gr)
        return finish(gr)
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running or md5(B1) != B1_MD5:
        return finish(None)
    shutil.copyfile(B1, SCR)
    gate("K2 scratch is a byte copy", md5(SCR) == B1_MD5, SCR)
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
        gate("H LabVIEW gone; input md5 unchanged; scratch deleted", gone and md5(B1) == B1_MD5 and not os.path.exists(SCR),
             (gone, md5(B1), os.path.exists(SCR)))
    if gr:
        json.dump(gr, open(OUT, "w", encoding="utf-8"))
        print("  FACT WROTE {0} md5 {1}".format(OUT, md5(OUT)), flush=True)
        offline(gr)
    return finish(gr)


def finish(gr):
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    arts = [{"path": p, "md5": md5(p)} for p in (OUT, DOUT) if gr and os.path.exists(p)]
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=arts)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
