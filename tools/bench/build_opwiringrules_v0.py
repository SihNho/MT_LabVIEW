# ---
# labview: build
# hardware: none
# ---
r"""build_opwiringrules_v0.py - card 145-a2-3 (PD351(b)): READ-ONLY op OpWiringRules_v0.vi = the connector-pane wiring rule
(Required / Recommended / Optional) of every terminal of a VI, plus the label on terminal `index`.
FOUND FIRST: no op carries ConnectorPane.WiringRules[] (grep WiringRule|239A8405|239A8007 over tools/docs = 0,
tools/bench/diag_c145_a2_1_facts.md:36); OpConPane_v0 (tools/recipes/build_opconpane.py, docs/NAMES.md:531-545) already is
VI -> Connector Pane:Reference 23E ('ConPane') -> ConnectorPane[Ctrls[], Number of Connection Terminals] -> IA -> Label -> 'Text'.
This build = byte copy of OpConPane_v0 + ADDITIVE PN ConnectorPane[WiringRules[] 239A8405] branched off 'ConPane' + indicators on
its data output and error out (build_opstopmode_v0.py B-class pattern). API: archive/peer/2026-10-07-c145-a2-1-conpane-required-claude.md:37-57
(1 Required, 2 Recommended, 3 Optional, 4 Dynamic) - a hypothesis, measured here.
PREDICTION (GATE lines): donor ES 1; new PN censused to ONE data terminal; assembled ES 1; saved; COLD ES 1 in a fresh LabVIEW.
Positive control on a scratch BYTE COPY of RingSeqCheck_v0 (panel open) with a scratch setter (= reader copy + Invoke
ConnectorPane.Wiring Rule:Set 239A8001, never saved): read defaults; set t11=1,t10=2,t9=3 -> read back [1,2,3]; set t11=3,t10=1,t9=2
-> read back [3,1,2]; every other entry unchanged. Hygiene: gscript.hygiene_run 2,000 calls on recycled copies, 0 errors,
h_closed +-100 (covers the card's 20-call bar). RingSeqCheck_v0 md5 unchanged; scratch files deleted; LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_opwiringrules_v0.log -- py -u tools/bench/build_opwiringrules_v0.py
"""
import hashlib, json, os, subprocess, sys, time, traceback                                 # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep                                                                         # noqa: E402
from build_opstopmode_v0 import B, STD                                                    # noqa: E402  (verified builder class)
CD = g.CLAUDEDEV; TS = time.strftime("%H%M%S")                                            # noqa: E702
OP = os.path.join(CD, "OpWiringRules_v0.vi"); RSC = os.path.join(CD, "RingSeqCheck_v0.vi")  # noqa: E702
RSC_MD5 = "0295a8d3"
TGT = os.path.join(CD, "scratch_c145a23_tgt_%s.vi" % TS); SETN = "scratch_c145a23_set_%s.vi" % TS  # noqa: E702
LAB_P = os.path.join(HERE, "build_opwiringrules_v0_labels.json"); HYG_P = os.path.join(HERE, "build_opwiringrules_v0_hygiene.json")
P_WR, M_SET = "239A8405", "239A8001"
REUSE_MD5 = "02beb55feba53feed1acbeb570010e60"                                            # reader built by 145-a2-3 (log:38-39)
g._run.__defaults__ = (6.0, 120.0)
G, LAB, SCR = {}, {}, [TGT, os.path.join(CD, SETN)]


class Stop(Exception):
    pass


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d="", need=True):
    G[k] = bool(ok); print("  GATE %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:600]), flush=True)  # noqa: E702
    if need and not ok:
        raise Stop(k)


def fact(k, v): print("  FACT  %s: %s" % (k, str(v)[:900]), flush=True)


def build():
    b = B("OpConPane_v0.vi", "OpWiringRules_v0.vi")
    gate("D donor copy ExecState 1", g.exec_state(b.op) == 1)
    nodes, _n = g.net_map(b.op, 0, max_nodes=60, max_terms=24); fact("donor net_map", nodes)   # noqa: E702
    pn1 = b.node_with("ConPane")[0]; fact("PN1 (VI.ConPane) uid", pn1)                    # noqa: E702
    p = b.pn("VI Server:ConnectorPane", [(P_WR, False)], (520, 520)); d = b.data(p, True)  # noqa: E702
    gate("L3 ConnectorPane[%s] censused to ONE data terminal" % P_WR, len(d) == 1, d)
    b.w(pn1, "ConPane", p, "reference", branch=True)
    gate("L4 new PN accepts PN1 'ConPane' (branch), ES 1", g.exec_state(b.op) == 1)
    lab = {"data": d[0], "pn": p, "pn1": pn1}
    lab["Rules"] = b.ind(p, d[0]); lab["RErr"] = b.ind(p, "error out")                    # noqa: E702
    g.set_auto_error_handling(b.op, False); b.purge()                                     # noqa: E702
    gate("A assembled ExecState 1", g.exec_state(b.op) == 1)
    lab["controls"] = [r["label"] for r in g.panel_wiring(b.op) if not r["indicator"]]
    lab["indicators"] = [r["label"] for r in g.panel_wiring(b.op) if r["indicator"]]
    LAB["reader"] = lab; fact("reader labels", lab)                                       # noqa: E702
    g.save(b.op); gate("V saved by script", os.path.getsize(OP) > 0, (os.path.getsize(OP), md5(OP)))  # noqa: E702


def build_setter():                                  # scratch only: never saved, deleted at exit
    b = B("OpWiringRules_v0.vi", SETN); la = LAB["reader"]                                # noqa: E702
    inv = int(g.build_invoke(b.op, "VI Server:ConnectorPane", M_SET, (520, 760))[0]["uid"])
    b.inv0 = list(b.inv0) + [inv]; b.purge()                                              # noqa: E702
    b.w(la["pn1"], "ConPane", inv, "reference", dc="Invoke", branch=True)
    raw = b.data(inv, False); sinks = [s for s in raw if s != "SetWireRule"]; fact("Wiring Rule:Set data sinks (raw)", raw)  # noqa: E702
    gate("W setter Invoke has 2 data sinks besides the method-header row 'SetWireRule' (card 145-a2-4)", len(sinks) == 2, sinks)
    lab = {"sinks": {s: b.ctl(inv, s) for s in sinks}, "WErr": b.ind(inv, "error out")}
    g.set_auto_error_handling(b.op, False); b.purge()                                     # noqa: E702
    gate("W setter ExecState 1", g.exec_state(b.op) == 1)
    LAB["setter"] = lab; fact("setter labels", lab)                                       # noqa: E702
    return b.op


def call(path, target, idx, extra=None, werr=None):
    la = LAB["reader"]; vi = g.op(path); ctl = set(la["controls"])                        # noqa: E702
    vi.SetControlValue("vi path", target); vi.SetControlValue("index", int(idx))          # noqa: E702
    for k, v in (("Names", []), ("Names 2", []), ("Class Name", ""), ("Class Name 2", "")):
        if k in ctl:
            vi.SetControlValue(k, v)
    for k, v in (extra or {}).items():
        vi.SetControlValue(k, v)
    g._run(vi)
    errs = " | ".join(e for e in (g._err(vi, la["RErr"]), g._err(vi, werr) if werr else "") if e)
    return {"rules": [int(x) for x in (vi.GetControlValue(la["Rules"]) or ())], "text": vi.GetControlValue("Text"),
            "n": int(vi.GetControlValue("Number of Connection Terminals")), "err": errs}


def rd(target, idx=0):
    with g.hygiene_probe(OP):
        return call(OP, target, idx)


def setrule(spath, target, term, rule):
    s = LAB["setter"]["sinks"]
    ki = next(k for k in s if k != "WErr" and ("index" in k.lower() or "idx" in k.lower())); kr = next(k for k in s if k != ki)   # noqa: E702
    lt, lr = s[ki], s[kr]
    with g.hygiene_probe(spath):
        return call(spath, target, 0, {lt: int(term), lr: int(rule)}, werr=LAB["setter"]["WErr"])


def main():
    bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = bench_prep.labview_handles()  # noqa: E702
    fact("handles after restart", h0)
    gate("0 RingSeqCheck_v0 md5 before", md5(RSC).startswith(RSC_MD5), md5(RSC))
    if md5(OP) == REUSE_MD5 and "reader" in json.load(open(LAB_P)):                       # card 145-a2-4: build() unchanged -> reuse
        LAB.update(json.load(open(LAB_P))); fact("reader REUSED (md5 %s, labels %s)" % (REUSE_MD5, LAB_P), LAB["reader"])  # noqa: E702
    else:
        build(); json.dump(LAB, open(LAB_P, "w"), indent=1)                               # noqa: E702
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
    gate("C OpWiringRules_v0 COLD ExecState 1 (fresh LabVIEW)", g.exec_state(OP) == 1, md5(OP))
    import shutil; shutil.copyfile(RSC, TGT); g.open_panel(TGT); time.sleep(1.0)         # noqa: E702
    r0 = rd(TGT); fact("P0 scratch RingSeqCheck copy: defaults", r0)                     # noqa: E702
    gate("P0 read: no error, len(rules) == Number of Connection Terminals", not r0["err"] and len(r0["rules"]) == r0["n"] > 0, r0)
    names = {i: rd(TGT, i)["text"] for i in range(r0["n"])}; fact("P0 names per terminal index", names)  # noqa: E702
    gate("P0 pane names 11 n1, 10 n2, 9 last, 8 Latest, 7 discards (build_ringseqcheck_v0.log:216)",
         [names.get(i) for i in (11, 10, 9, 8, 7)] == ["n1", "n2", "last", "Latest", "discards"], names, need=False)
    fact("P0 rule per index (name, rule)", [(i, names[i], r0["rules"][i]) for i in range(r0["n"])])
    sp = build_setter()
    for k, setv in enumerate(({11: 1, 10: 2, 9: 3}, {11: 3, 10: 1, 9: 2})):
        ws = [setrule(sp, TGT, t, v) for t, v in setv.items()]; r = rd(TGT)               # noqa: E702
        fact("P%d set %s -> setter errors %s" % (k + 1, setv, [w["err"] for w in ws]), r["rules"])
        exp = list(r0["rules"]); [exp.__setitem__(t, v) for t, v in setv.items()]         # noqa: E702
        gate("P%d positive control: read back == set, others unchanged" % (k + 1),
             r["rules"] == exp and not any(w["err"] for w in ws) and not r["err"], (r["rules"], exp))
    rec = g.hygiene_run(OP, lambda c: call(OP, c, 0)["err"], RSC, total=2000, per_round=100, card="145-a2-4",
                        log="tools/bench/build_opwiringrules_v0.log", record_path=HYG_P,
                        workload_text="OpWiringRules_v0 on index 0 of a byte copy of RingSeqCheck_v0")
    fact("H handle series (h_closed per round of 100 calls)", rec["handles_per_round"])
    gate("H hygiene PASS (calls %s, errors %s, max_dev %s, refs %s)" % (rec["calls"], rec["errors"], rec["max_dev_closed"],
         rec["refs_live_delta"]), rec["status"] == "PASS", rec["error_samples"][:3])
    fact("handles at end vs after restart", (bench_prep.labview_handles(), h0))


if __name__ == "__main__":
    try:
        main()
    except Stop as e:
        print("STOP at the first unexpected result: %s" % e, flush=True)
    except Exception as e:                                                                # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)  # noqa: E702
    finally:
        json.dump(LAB, open(LAB_P, "w"), indent=1, default=str); g.reset()                # noqa: E702
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)  # noqa: E702
        gate("E LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)
        for p in SCR:
            for _ in range(5):
                try:
                    os.path.exists(p) and os.remove(p); break                             # noqa: E702
                except OSError:
                    time.sleep(2)
        gate("E scratch files deleted", not any(os.path.exists(p) for p in SCR), SCR, need=False)
        gate("E RingSeqCheck_v0 md5 unchanged", md5(RSC).startswith(RSC_MD5), need=False)
        bad = [k for k, v in G.items() if not v]
        arts = [{"path": p, "md5": md5(p)} for p in (OP, HYG_P) if os.path.exists(p)]
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
        sys.exit(1 if bad else 0)
