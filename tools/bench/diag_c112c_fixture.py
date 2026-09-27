r"""diag_c112c_fixture - card 112-3 W0 part 1: the T1/T2 SCRATCH FIXTURES and their base graphs, READ-ONLY in LabVIEW.
RUN 1 (diag_c112c_fixture.log) measured: exp-ref management.vi holds its registers on FOR loops (#184 -> #205, #45 -> #270), its
WhileLoop #74 has none, and stagexec.LVBackend.wire_sr addresses WhileLoop registers only (tools/stagexec.py:1805) -> not a T1
fixture; the script then died on close_panel of an unopened panel (fixed: no close_panel). RUN 2 reads:
  ct  = background VIs_COPY\fit WLC-plot KK.vi (case-selector Tunnel #727 outer t731 <- CT #786 'Mag Direction' w701) -> T2 ctltun
  sr* = WhileLoop-register candidates, in order (subVIs resolve from claudeDev root or not - measured by ExecState):
        choose bandpass v2.vi, check N bead pos v2.vi -> T1 wire_sr (the first with a WhileLoop register whose R.inner is fed
        by one body source and whose L.inner wire has exactly ONE sink)
Fixtures are byte copies kept as claudeDev\scratch_c112c_<key>.vi; each is READ on a second dated byte copy (deleted), never
edited, never saved, no VI run. PRIOR ART: tools/bench/diag_c108b_graph.py (read_live + k_contract_79.mloops + owner_of).
OUTPUT tools/bench/graph_scratch_c112c_<key>.json {vi = the fixture, md5, terminals, objs, loops, fs_tunnel_pairs [], owners}.
PREDICTION: K byte copies; E ExecState 1; R ct row as stated, #727's inner frames owned by ONE CaseStructure; W >= 1 sr candidate
has a usable WhileLoop register (printed as ROWS-SR); H LabVIEW gone, sources unchanged, read copies deleted.
    py tools/bgrun.py --material --max-min 12 --log tools/bench/diag_c112c_fixture2.log -- py -u tools/bench/diag_c112c_fixture.py"""
import hashlib, json, os, shutil, subprocess, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P, gscript as g, stagekit as K, vigraph as V                     # noqa: E401,E402
SRC = os.path.join(g.CLAUDEDEV, "background VIs_COPY")
FIX = [("ct", "fit WLC-plot KK.vi"), ("sr_cb", "choose bandpass v2.vi"), ("sr_nb", "check N bead pos v2.vi")]
TS = time.strftime("%Y%m%d_%H%M%S")
gates, arts, srok = [], [], []


class S(object):                                                                   # k_contract_79.mloops needs .safe only
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


def row(T, tu):
    r = [x for x in T if int(x["term_uid"]) == tu]
    return r[0] if len(r) == 1 else None


def read(key, fix, scr):
    t0 = time.time()
    lv = K.mod("wiki_build").read_live(scr, fs_pairs=[])
    es = g.exec_state(scr)
    print("  FACT {0}: LIVE {1} terminal rows, {2} objs, ExecState {3}, {4:.0f}s".format(key, len(lv["terminals"]), len(lv["objs"]), es, time.time() - t0), flush=True)
    loops = K.mod("k_contract_79").mloops(S(), scr)
    print("  FACT {0}: LOOPS {1}".format(key, [(L["class"], L["loop_uid"], L["right_uids"], L["left_of"]) for L in loops]), flush=True)
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo, BD = {}, list(diags), K.mod("build_d1_v0")
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        try:
            v = BD.owner_of(scr, u, strict=False)
        except Exception as e:                                                     # noqa: BLE001
            v = ("?", 0); print("  FACT owner_of #{0} raised {1}".format(u, str(e)[:120]), flush=True)   # noqa: E702
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    print("  FACT {0}: owners {1}".format(key, sorted(O.items())), flush=True)
    gate("O {0}: every Diagram ({1}) has a resolved owner".format(key, len(diags)), all(O[d][0] != "?" for d in diags),
         sorted(d for d in diags if O[d][0] == "?"))
    if key == "ct":                                    # an sr candidate's ExecState is a FACT; gate W picks among them
        gate("E {0}: ExecState 1 on the read copy".format(key), es == 1, es)
    return es, {"vi": fix, "md5": md5(fix), "source": "tools/bench/diag_c112c_fixture.py (read_live + mloops + owner_of, byte copy)",
                "terminals": lv["terminals"], "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": [], "graph_summary": {},
                "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}


def peers(T, r):
    return [x for x in T if r["wire_uid"] and x["wire_uid"] == r["wire_uid"] and x is not r]


def check(key, gr):
    T = gr["terminals"]
    if key == "ct":
        a, b = row(T, 731), row(T, 786)
        inner = sorted(int(x["frame_diagram"]) for x in T if int(x["owner_uid"]) == 727 and x["term_class"] == "InnerTerminal")
        own = set(tuple(gr["owners"].get(str(f), ("?", 0))) for f in inner)
        gate("R ct: t731 (Tunnel #727 outer) <- CT t786 on w701; #727 inner frames owned by ONE CaseStructure",
             a and b and a["wire_uid"] == b["wire_uid"] == 701 and len(own) == 1 and list(own)[0][0] == "CaseStructure", (a, b, inner, own))
        return
    for L in gr["loops"]:
        for ru, lus in (L["left_of"] or {}).items() if L["class"] == "WhileLoop" else []:
            ri = [x for x in T if int(x["owner_uid"]) == int(ru) and x["term_class"] == "InnerTerminal"]
            li = [x for x in T if int(x["owner_uid"]) == int(lus[0]) and x["term_class"] == "InnerTerminal"]
            if len(ri) != 1 or len(li) != 1 or not ri[0]["wire_uid"] or not li[0]["wire_uid"]:
                continue
            rs, ls = [x for x in peers(T, ri[0]) if x["is_source"]], [x for x in peers(T, li[0]) if not x["is_source"]]
            fine = len(rs) == 1 and len(ls) == 1 and len(peers(T, ri[0])) == 1
            print("  FACT ROWS-SR {0} loop #{1} R #{2} inner t{3} w{4} <- {5}; L #{6} inner t{7} w{8} -> {9}; usable {10}".format(
                key, L["loop_uid"], ru, ri[0]["term_uid"], ri[0]["wire_uid"], [(x["owner_uid"], x["owner_class"], x["term_uid"], x["term_name"]) for x in rs],
                lus[0], li[0]["term_uid"], li[0]["wire_uid"], [(x["owner_uid"], x["owner_class"], x["term_uid"], x["term_name"]) for x in ls], fine), flush=True)
            if fine:
                srok.append((key, L["loop_uid"], int(ru), int(lus[0])))


def main():
    running = "labview.exe" in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    gate("K0 no LabVIEW process before the read", not running, running)
    if running:
        return finish()
    scrs, srcmd5 = [], {}
    old = os.path.join(g.CLAUDEDEV, "scratch_c112c_sr.vi")                        # run 1's exp-ref copy: not a T1 fixture
    if os.path.exists(old):
        os.remove(old)
    try:
        K.mod("bench_prep").restart_labview(); g.reset(); time.sleep(3)             # noqa: E702
        for key, name in FIX:
            src = os.path.join(SRC, name)
            srcmd5[src] = md5(src)
            fix = os.path.join(g.CLAUDEDEV, "scratch_c112c_{0}.vi".format(key))
            if not os.path.exists(fix):
                shutil.copyfile(src, fix)
            gate("K {0}: fixture {1} is a byte copy of {2}".format(key, os.path.basename(fix), name), md5(fix) == srcmd5[src], md5(fix))
            scr = os.path.join(g.CLAUDEDEV, "scratch_c112c_read_{0}_{1}.vi".format(key, TS))
            shutil.copyfile(fix, scr); scrs.append(scr)                            # noqa: E702
            es, gr = read(key, fix, scr)
            out = os.path.join(HERE, "graph_scratch_c112c_{0}.json".format(key))
            json.dump(gr, open(out, "w", encoding="utf-8"))
            arts.append({"path": out, "md5": md5(out)}); arts.append({"path": fix, "md5": md5(fix)})   # noqa: E702
            print("  FACT WROTE {0} md5 {1}".format(out, md5(out)), flush=True)
            check(key, gr)
            if key != "ct" and srok and es == 1:
                break
        gate("W at least one sr candidate has a usable WhileLoop register (ExecState 1)", bool(srok), srok)
    finally:
        g.reset()
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
        time.sleep(4)
        gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
        for p in scrs:
            try:
                os.remove(p)
            except OSError as e:
                print("  FACT read copy not removed: {0}".format(e), flush=True)
        gate("H LabVIEW gone; sources unchanged; read copies deleted", gone and all(md5(s) == m for s, m in srcmd5.items())
             and not any(os.path.exists(p) for p in scrs), (gone, [os.path.exists(p) for p in scrs]))
    return finish()


def finish():
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff, artefacts=arts)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
