# ---
# labview: build
# hardware: none
# offline-args: --selftest
# evidence: tools/bench/cards/task_168-a1-2.json
# ---
r"""prep_c168_a1_2_lib - blocks card 168-a1-2 needs that lived INLINE in earlier diagnostics, extracted ONCE (docs/script-writing.md rule 4).

Found before writing (grep "def el_read|def mem|computation_diff(" tools/bench/*.py, docs/toolkit-capabilities.md): no shared function
holds these; the inline copies are (they stay as the record of what ran):
  - Meter.mem      = diag_c167_a1_1_rbw.py:44-49 (the `mem` meter, MEMS list)
  - el_read        = diag_c167_a1_1_rbw.py:52-84 (Error List of an IN-MEMORY VI with errorlist_check's functions; no save needed);
                     only the output path and the `source` text became arguments
  - tunnel_read    = diag_c166_a1_1_tun.py:42-50 (gscript._uid_index + gscript.tunnels + gscript.read_term_type of ONE LoopTunnel)
  - frame_cdiff    = diag_c167_a1_3_closure.py:144-147 (S1 frame graph via stagekit.s1_frame_graph, P5 build4(frame_keyed=True),
                     vigraph.computation_diff) - the computation p6_closure.json was built from
New pure helpers (no copy existed): inputs_of (sink terminals of one node + the source on each wire, from a stored graph dict);
closure_rd_diff (frame cdiff row set vs p6_closure.json rows classed R / DISP, both differences).
el_read / tunnel_read / Meter call LabVIEW only through the caller's `g` / Stage `s` (this module opens nothing at import).

Self-test (offline, `--selftest`, replays recorded data; PREDICTION 6/0):
  T1 errorlist_check.class_counts on the stored items of errorlist_D1_ring_p6rbw_20261012_191349.json == its stored class_counts
  T2 frame_cdiff(7815af09 graph) has 31 rows and equals p6_closure.json's cdiff row set (closure gate E3)
  T3 inputs_of(7815af09, 2626): t2832<-#30300, t4160<-#30119, t4165<-#30216, t4168<-#4594 (diag_c168_a1_1_facts.md:20)
  T4 closure_rd_diff(frame_cdiff(7815af09), p6_closure): every R/DISP row that has a cdiff sink is in the diff (only_closure_cdiff == [])
  T5 Meter on a stub stage: lines recorded, peak = max
  T6 gone_and_count on a stub g: absent + count equal -> ok; present -> not ok
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c168_a1_2_lib_selftest.log -- py -u tools/bench/prep_c168_a1_2_lib.py --selftest"""
import json, os, sys, time                                                                    # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "recipes"), HERE):
    _p in sys.path or sys.path.insert(0, _p)                                                  # noqa: E701

BASE_GRAPH = os.path.join(HERE, "graph_ring_p5s02e_20261012_173009.json")       # 7815af09, graph of 75773b0d
CLOSURE = os.path.join(HERE, "p6_closure.json")


class Meter(object):
    """Private-bytes meter of a Stage run (diag_c167_a1_1_rbw.py:44-49): mem(tag) -> MB, prints `METER`, records a Stage fact;
    .lines = [(tag, MB)], .peak(). `pb` = the private-bytes reader (stagekit.private_bytes). Self-test: T5."""

    def __init__(self, s, pb):
        self.s, self.pb, self.lines = s, pb, []

    def mem(self, tag):
        v = round((self.pb() or 0) / 1e6, 1)
        self.lines.append((tag, v))
        print("METER {0} k {1} private {2} MB".format(tag, len(self.lines), v), flush=True)
        self.s.fact("MEM {0}: {1} MB private".format(tag, v))
        return v

    def peak(self):
        return max(v for _t, v in self.lines) if self.lines else None


def el_read(g, W, out, source):
    """Full Error List read of the in-memory VI W with errorlist_check's functions (diag_c167_a1_1_rbw.py:52-84); writes `out`
    (+ `_raw.json`). Returns (out, R) with item_count, class_counts, details[], n_reported, exec_state, errors. GUI through
    errorlist_check (-Exception Approved / -Evidence EC.EVID). Self-test: T1 covers its class_counts step on recorded items."""
    import errorlist_check as EC
    EC._lv_imports()
    R = {"vi": W, "errors": [], "gui_acts_outer": [], "no_vi_was_run": True, "evidence": EC.EVID, "source": source, "uid_route": EC.UID_ROUTE}
    try:
        g.open_panel(W)
        time.sleep(1.0)
        R["exec_state"] = g.exec_state(W)
        R["block_diagram_open"] = EC.open_diagram(W, R)
        r = EC.E.read(W, out.replace(".json", "_raw.json"), log=lambda t: print(t, flush=True), on_item=EC.make_on_item(W, R))
        R.update({k: r.get(k) for k in ("method", "n_reported", "n_reported_from", "items", "categories", "gui_acts",
                                        "closed_with_esc", "window", "ocr_engine")})
        R["errors"] += r.get("errors") or []
        if not R.get("items"):
            n0, line, cap = EC.count_zero(R)
            R["n_reported"] = R["n_reported"] if R.get("n_reported") is not None else n0
            R["n_reported_from"], R["zero_capture"] = line, cap
    except Exception as e:                                                         # noqa: BLE001
        R["errors"].append("{0}: {1}".format(type(e).__name__, str(e)[:160]))
    items = R.get("items") or []
    R["item_count"] = len(items)
    R["class_counts"] = EC.class_counts(items)
    R["dclicked"] = sum(1 for i in items if i.get("show_error"))
    R["show_error_ok"] = sum(1 for i in items if (i.get("show_error") or {}).get("diagram_fronted"))
    R["details"] = [{"index": i.get("index"), "raw": i.get("raw"), "detail": i.get("detail"), "object": i.get("object"), "reason": i.get("reason"),
                     "uid": i.get("uid", "unread")} for i in items]
    with open(out, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, ensure_ascii=False, default=str)
    return out, R


def tunnel_read(s, g, W, uid, outer_term):
    """IndexMode + outer face type of LoopTunnel #uid in the loaded VI W (diag_c166_a1_1_tun.py:42-50): gscript._uid_index ->
    gscript.tunnels -> gscript.read_term_type(outer_term). Returns the same dict keys as diag_c166_a1_1_tun.json tunnels.*.*.
    Read-only. Self-test: none offline (LabVIEW calls); the recorded case is diag_c166_a1_1_tun.log:44-47."""
    i = s.safe("LoopTunnel index of #{0}".format(uid), lambda: g._uid_index(W, "LoopTunnel", uid), None)[0]
    t = s.safe("gscript.tunnels #{0}".format(uid), lambda: g.tunnels(W, i), None)[0] if i is not None else None
    ty = s.safe("gscript.read_term_type t{0}".format(outer_term), lambda: g.read_term_type(W, outer_term), None)[0]
    tt = (ty or {}).get("types") or {}
    return {"index": i, "echo": (t or {}).get("uid"), "index_mode": (t or {}).get("index_mode"), "out_name": (t or {}).get("out_name"),
            "out_is_source": (t or {}).get("out_is_source"), "out_wire": (t or {}).get("out_wire"), "in_wires": (t or {}).get("in_wires"),
            "term_echo": (ty or {}).get("echo"), "type_err": (ty or {}).get("err"), "canon": tt.get("canon"), "sig": tt.get("sig"),
            "top_name": tt.get("top_name")}


def gone_and_count(g, W, cls, uid, wires_want, rec, fact):
    """(ok, detail) after a node delete: #uid not in g.uids(W, cls) AND g.count(W, "Wire") == wires_want. Writes rec["wires_after_delete"],
    rec["deleted_present"] and one fact line. Read-only. Called INSIDE the gate statement so a dry run sees the reads (gate-fp fp-100).
    Self-test: T6 (stub g)."""
    left, nw = g.uids(W, cls), g.count(W, "Wire")
    pres = uid in left
    rec["wires_after_delete"], rec["deleted_present"] = nw, pres
    fact("AFTER DELETE: Wire objects {0}; {1} #{2} in the {1} list {3}".format(nw, cls, uid, pres))
    return (not pres) and nw == wires_want, {"present": pres, "wires": nw}


def frame_cdiff(gr):
    """vigraph.computation_diff(S1 frame graph, build4(gr, frame_keyed=True)) of a graph dict `gr` - the call of
    diag_c167_a1_3_closure.py:144-147 (S1 = stagekit.s1_frame_graph = docs/wiki/subvi/D1_s1_copy.json). Returns the cdiff dict
    (rows[].sink ...). Pure. Self-test: T2."""
    import stagekit as K, vigraph as V, jev_candidates as JC                               # noqa: E401
    lab = JC.node_labels_default()
    S1f = K.s1_frame_graph(lab)
    Gf = V.build4(gr["terminals"], gr["objs"], gr["loops"], lab, gr["fs_tunnel_pairs"], frame_keyed=True)
    return V.computation_diff_frame(S1f, Gf)


def inputs_of(gr, uid):
    """[{term_uid, term_name, wire_uid, sources: [(owner_uid, owner_class, term_uid)]}] for every NON-source terminal of node #uid
    in graph dict `gr` (rows deduped by vigraph.dedupe_rows), sorted by term_uid. Pure. Self-test: T3."""
    import vigraph as V
    terms = V.dedupe_rows(gr["terminals"])[0]
    by_wire = {}
    for t in terms:
        if t.get("wire_uid"):
            by_wire.setdefault(int(t["wire_uid"]), []).append(t)
    out = []
    for t in terms:
        if int(t["owner_uid"]) == int(uid) and not t["is_source"]:
            w = int(t.get("wire_uid") or 0)
            src = sorted((int(x["owner_uid"]), x["owner_class"], int(x["term_uid"])) for x in by_wire.get(w, []) if x["is_source"]) if w else []
            out.append({"term_uid": int(t["term_uid"]), "term_name": t["term_name"], "wire_uid": w, "sources": src})
    return sorted(out, key=lambda r: r["term_uid"])


def closure_rd_diff(cd, closure):
    """Frame cdiff row set vs the rows of p6_closure.json classed R or DISP. Returns {diff_rows, rd_rows, only_diff (sinks in the diff,
    not an R/DISP row), only_closure_cdiff (R/DISP rows' cdiff sinks absent from the diff), only_closure_no_cdiff (R/DISP row keys
    without a cdiff sink - never comparable to a diff row)}. Pure. Self-test: T4."""
    ds = set(str(r["sink"]) for r in cd["rows"])
    rd = [r for r in closure["rows"] if r.get("class") in ("R", "DISP")]
    rs = set(str(r["cdiff"]["sink"]) for r in rd if r.get("cdiff"))
    return {"diff_rows": len(ds), "rd_rows": len(rd), "only_diff": sorted(ds - rs), "only_closure_cdiff": sorted(rs - ds),
            "only_closure_no_cdiff": sorted("{0} ({1})".format(r["key"], r["class"]) for r in rd if not r.get("cdiff"))}


def selftest():
    """T1..T5 on recorded data (docstring above). Prints GATE lines + the C6 RESULT line; returns rc."""
    import errorlist_check as EC, protocol as PR                                           # noqa: E401
    G = {"pass": 0, "fail": 0, "first": None}

    def gate(label, ok, d=""):
        G["pass" if ok else "fail"] += 1
        G["first"] = G["first"] or (None if ok else label)
        print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:300]), flush=True)
    ea = json.load(open(os.path.join(HERE, "errorlist_D1_ring_p6rbw_20261012_191349.json"), encoding="utf-8"))
    cc = EC.class_counts(ea["items"])
    gate("T1 class_counts(stored items) == stored class_counts", cc == ea["class_counts"], cc)
    base = json.load(open(BASE_GRAPH, encoding="utf-8"))
    clo = json.load(open(CLOSURE, encoding="utf-8"))
    cd = frame_cdiff(base)
    rk = set(str(r["sink"]) for r in cd["rows"])
    ck = set(str(r["cdiff"]["sink"]) for r in clo["rows"] if r.get("cdiff"))
    gate("T2 frame_cdiff(7815af09) 31 rows == p6_closure cdiff rows", len(rk) == 31 and rk == ck, (len(rk), len(ck), sorted(rk ^ ck)[:6]))
    io = inputs_of(base, 2626)
    got = [(r["term_uid"], [x[0] for x in r["sources"]]) for r in io]
    want = [(2832, [30300]), (4160, [30119]), (4165, [30216]), (4168, [4594])]
    gate("T3 inputs_of(7815af09, #2626) == diag_c168_a1_1_facts.md:20", got == want, got)
    cr = closure_rd_diff(cd, clo)
    gate("T4 closure_rd_diff(7815af09): R/DISP cdiff sinks all in the diff (rd rows {0})".format(cr["rd_rows"]),
         cr["only_closure_cdiff"] == [] and cr["rd_rows"] == 32, {k: (v if not isinstance(v, list) else len(v)) for k, v in cr.items()})

    class _S(object):
        facts = []

        def fact(self, x):
            self.facts.append(x)
    vals = iter([600e6, 612.34e6, 580e6])
    m = Meter(_S(), lambda: next(vals))
    [m.mem(t) for t in ("a", "b", "c")]
    gate("T5 Meter lines + peak", m.lines == [("a", 600.0), ("b", 612.3), ("c", 580.0)] and m.peak() == 612.3 and len(_S.facts) == 3, m.lines)

    class _G(object):
        def __init__(self, u, n):
            self.u, self.n = u, n

        def uids(self, W, cls):
            return set(self.u)

        def count(self, W, cls):
            return self.n
    r1, r2 = {}, {}
    a = gone_and_count(_G([1, 2], 2066), "W", "BuildArray", 11261, 2066, r1, lambda x: None)
    b = gone_and_count(_G([1, 11261], 2066), "W", "BuildArray", 11261, 2066, r2, lambda x: None)
    gate("T6 gone_and_count: absent+2066 -> ok; present -> not ok", a[0] is True and b[0] is False and r2["deleted_present"] is True, (a, b))
    print(PR.result_line(PR.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
    return 1 if G["fail"] else 0


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.exit(selftest())
