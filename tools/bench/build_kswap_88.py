r"""build_kswap_88 - card 88-2 (PD194(d)): byte copy D1_s1_copy.vi -> claudeDev\D1_s1_kswap_<ts>.vi, then ONE callee
swap: the four-fold kernel call #5058 (diagram uid 639; swap_verb_75.log:14 lists it) -> PARALLEL_kernel_v3.vi.
FOUND FIRST: the verb exists - gscript.replace_object / OpReplaceGObj_v0 (docs/toolkit-capabilities.md:36, measured on a
scratch of this same VI, swap_verb_75.log 13/0); this file is tools/bench/diag_swap_measure.py re-aimed, no new verb.
Rule-1a citations (card PRECONDITION): archive/benchmarks/INDEX.md:33 (row 12, v3 == four-fold bit-for-bit, 10,043
frames), :38 (row 17, PARALLEL_kernel_v3 has the kernel's own connector pane, REPORT.md:18-20,36), :61 (row 40,
v3clean == current PARALLEL_kernel_v3 md5 87d5b3e4, bit-identical on the fixture).
PREDICTION: K1 pins (S1 3e3d23ce, L2-A1 bed 51d9b8a3, kernel 87d5b3e4) hold before; K2 before: #5058 calls
'Track N beads four-fold over-kernel-v3.vi', ExecState 1; K3 replace_object no error, new uid; K4 callee read back ==
PARALLEL_kernel_v3.vi; K5 name-keyed wire-edge diff (node remapped) == EMPTY (same terminals, same wires); K6 callee
census diff == that node only; K7 ExecState 1; K8 saved by script; K9 ExecState 1 COLD after restart; K10 pins after;
K11 LabVIEW gone. No VI is run.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/build_kswap_88.log -- py -u tools/bench/build_kswap_88.py"""
import os, sys, json, time, shutil, subprocess                                        # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                 # noqa: E402
g, J = K.g, (lambda p: json.load(open(os.path.join(K.ROOT, p), encoding="utf-8")))  # noqa: E731
S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); BED = os.path.join(K.CLAUDEDEV, "D1_l2_a1_20260925_235224.vi")
KER = os.path.join(K.CLAUDEDEV, "PARALLEL_kernel_v3.vi"); OLD_UID, DIAG_UID = 5058, 639
PINS = (("S1", S1, "3e3d23cefd3a334001aa9d6156bf1aee"), ("bedL2A1", BED, "51d9b8a3af5b4240cdc2ad193d9b4f41"),
        ("kernel", KER, "87d5b3e4290d5d288849988eea187e53"))
TS = time.strftime("%Y%m%d_%H%M%S")
s = K.Stage(S1, PINS[0][2], "build_kswap_88", fresh=False, preload=False, deadline_min=22, pins=PINS,
            work_name="D1_s1_kswap_{0}.vi".format(TS), task="88-2", out_json=os.path.join(K.BENCH, "build_kswap_88.json"))
T = s.work; W1 = J("docs/wiki/subvi/D1_s1_copy.json"); FS = W1["fs_tunnel_pairs"]
WB, bp = K.mod("wiki_build"), K.mod("bench_prep")


def edges(live, remap):
    own = lambda r: remap.get(r["owner_uid"], r["owner_uid"])                    # noqa: E731
    by = {}
    for r in live["terminals"]:
        if r["wire_uid"]:
            by.setdefault(r["wire_uid"], []).append(r)
    return set((own(a), a["term_name"], own(b), b["term_name"]) for rs in by.values() for a in rs if a["is_source"]
               for b in rs if not b["is_source"])


def node_terms(live, uid):
    return sorted((r["term_name"], r["is_source"], bool(r["wire_uid"])) for r in live["terminals"] if r["owner_uid"] == uid)


def main(s):
    s.head("[0] files"); s.gate("K1 pins hold before", s.pin_check("BEFORE"), "", fatal=True)
    shutil.copyfile(S1, T); s.gate("K1b work is a byte copy of S1", K.md5(T) == PINS[0][2], K.md5(T), fatal=True)
    s.head("[1] restart; BEFORE reads"); s.restart(); g.ensure_loaded(T)
    es0 = g.exec_state(T); d = [int(o["uid"]) for o in g.report_all(T, "Diagram")].index(DIAG_UID)
    c0 = dict((int(x["uid"]), x["path"]) for x in g.subvis(T, d))
    s.gate("K2 #5058 calls the four-fold kernel, ExecState 1", es0 == 1 and str(c0.get(OLD_UID, "")).endswith(
        "Track N beads four-fold over-kernel-v3.vi"), (es0, c0.get(OLD_UID)), fatal=True)
    L0 = WB.read_live(T, fs_pairs=FS); E0 = edges(L0, {}); t0 = node_terms(L0, OLD_UID)
    s.fact("before: {0} terms, {1} edges; old node terminals {2}".format(len(L0["terminals"]), len(E0), t0))
    s.head("[2] SWAP #5058 -> PARALLEL_kernel_v3.vi"); r = g.replace_object(T, OLD_UID, KER); s.R["swap"] = r
    s.gate("K3 replace_object: no error, a new-object uid", not r["err_replace"] and not r["err"] and r["new_uid"] > 0, r, fatal=True)
    nu = r["new_uid"]; c1 = dict((int(x["uid"]), x["path"]) for x in g.subvis(T, d))
    s.gate("K4 callee read back == PARALLEL_kernel_v3.vi", os.path.normcase(str(c1.get(nu))) == os.path.normcase(KER), c1.get(nu))
    L1 = WB.read_live(T, fs_pairs=FS); E1 = edges(L1, {nu: OLD_UID}); t1 = node_terms(L1, nu)
    s.fact("new node #{0} terminals {1}".format(nu, t1)); s.R["terms_old"], s.R["terms_new"] = t0, t1
    s.gate("K5 wire-edge diff(before, after) == EMPTY (node remapped)", E0 == E1,
           {"removed": sorted(E0 - E1)[:12], "added": sorted(E1 - E0)[:12]})
    s.gate("K5b every WIRED old terminal exists wired on the new node", set((a, b) for a, b, w in t0 if w) ==
           set((a, b) for a, b, w in t1 if w), "")
    dd = dict((k, (c0.get(k), c1.get(k))) for k in set(c0) | set(c1) if c0.get(k) != c1.get(k))
    s.gate("K6 callee census diff == that node only", set(dd) <= {OLD_UID, nu} and len(dd) >= 1, dd)
    es1 = g.exec_state(T); s.gate("K7 ExecState 1 after the swap", es1 == 1, es1, fatal=True)
    s.head("[3] save"); g.save(T); g.reset(); s.R["saved"] = {"path": T, "md5": K.md5(T), "bytes": os.path.getsize(T)}
    s.gate("K8 saved by script, bytes differ from S1", os.path.exists(T) and K.md5(T) != PINS[0][2], s.R["saved"])
    s.head("[4] cold"); s.restart(); g.ensure_loaded(T); es2 = g.exec_state(T)
    s.gate("K9 ExecState 1 COLD", es2 == 1, es2); s.R["final_node_uid"] = nu


try:
    main(s)
except K.Stop as e:
    s.gate("STOP at gate: {0}".format(e), False)
except Exception as e:                                                               # noqa: BLE001
    import traceback; traceback.print_exc(); s.gate("the run completed without an unhandled exception", False, str(e)[:200])  # noqa: E702
s.R["ref_counts"] = g.ref_counts(); s.fact("ref_counts {0}".format(s.R["ref_counts"])); g.reset()  # noqa: E702
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6); s.gate("K10 pins unchanged after", s.pin_check("AFTER"))  # noqa: E702
s.gate("K11 LabVIEW gone at exit", "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout)
if os.path.exists(T): s.fact("DELIVERABLE {0} md5 {1} bytes {2}".format(T, K.md5(T), os.path.getsize(T)))
s.dump(); sys.exit(s.summary())
