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

Card 169-a1-1 added fs3_check / tunnels_read / fs4_check (extracted from diag_c168_a1_2_rbwdel.py:138-150) and cdiff_rowset_diff (PD406(b),
new); self-tests T7-T10 replay the recorded 168 scratch (diag_c168_a1_2_rbwdel.json + graph 57f33e7c).
Self-test (offline, `--selftest`, replays recorded data; PREDICTION 10/0; T7-T10 below the original six):
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
G168 = os.path.join(HERE, "graph_ring_p6rbwd_20261012_205248.json")             # 57f33e7c, the 168 scratch graph (PD406(b) S-5 reference)


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


# ---- card 169-a1-1 (brief_169-a1-1.md step 2): the 168 save-gate comparisons, extracted from diag_c168_a1_2_rbwdel.py:138-150 (inline
# copy left there as the record of what ran) + the PD406(b) row-set compare (new; no copy existed). Self-tests T7-T10.
def fs3_check(base, gr, uid, n_inputs=4):
    """S-3 / F-S3 (diag_c168_a1_2_rbwdel.py:138-142): node #uid has `n_inputs` sink terminals in `gr`, each wired and sourced, and the
    (term, source owners) list equals the one in `base`. Returns (ok, evidence text, {"base": [...], "got": [...]}). Pure. Self-test: T7."""
    i_b, i_s = inputs_of(base, uid), inputs_of(gr, uid)
    sb = [(r["term_uid"], [x[0] for x in r["sources"]]) for r in i_b]
    ss = [(r["term_uid"], r["wire_uid"], [x[0] for x in r["sources"]]) for r in i_s]
    ok = len(i_s) == n_inputs and all(r["wire_uid"] and r["sources"] for r in i_s) and [(a, c) for a, _b, c in ss] == sb
    return ok, "#{0} inputs got (term, wire, src owners) {1} vs base (term, src owners) {2}".format(uid, ss, sb), {"base": sb, "got": ss}


def tunnels_read(s, g, W, plan):
    """tunnel_read of every LoopTunnel in `plan` ({uid: {"outer_term": t, ...}}, diag_c166_a1_1_tun_plan.json tunnels) in uid order, one
    `TUN #uid` fact each (diag_c168_a1_2_rbwdel.py:143-147). Returns {uid str: tunnel_read dict}. Read-only (LabVIEW via `g`). Self-test:
    none offline; the recorded case is diag_c168_a1_2_rbwdel.json tunnels (checked by T8 through fs4_check)."""
    tr = {}
    for u, exp in sorted(plan.items(), key=lambda kv: int(kv[0])):
        tr[u] = tunnel_read(s, g, W, int(u), exp["outer_term"])
        s.fact("TUN #{0}: {1}".format(u, json.dumps(tr[u], sort_keys=True)))
    return tr


def fs4_check(tr, stored):
    """S-4 / F-S4 (diag_c168_a1_2_rbwdel.py:148-150): per tunnel (IndexMode, canon, sig) read == stored (diag_c166_a1_1_tun.json
    tunnels.p5s01 = 7f2582ae); every IndexMode read and every sig non-empty; the uid sets equal and non-empty (stricter than 168, which
    compared tr's keys only). Returns (ok, evidence text, cmp {uid: (read 3, stored 3)}). Pure. Self-test: T8."""
    cmp4 = dict((u, (tr[u].get("index_mode"), tr[u].get("canon"), tr[u].get("sig"), (stored.get(u) or {}).get("index_mode"),
                     (stored.get(u) or {}).get("canon"), (stored.get(u) or {}).get("sig"))) for u in tr)
    ok = bool(tr) and set(tr) == set(stored) and all(
        c[0] is not None and c[2] and c[:3] == c[3:] for c in cmp4.values())
    return ok, "#uid (IndexMode, canon, sig) read vs stored 7f2582ae (diag_c166_a1_1_tun.json tunnels.p5s01): {0}".format(cmp4), cmp4


def _row_key(r):
    return json.dumps([r.get("node"), r.get("class"), str(r.get("sink")), r.get("before"), r.get("after")], sort_keys=True, default=str)


def cdiff_rowset_diff(cd_a, cd_b):
    """PD406(b) S-5: two frame-keyed computation_diff results compared ROW FOR ROW (node, class, sink, before sources, after sources).
    Returns {rows_a, rows_b, only_a, only_b (full rows, sorted), sinks_only_a, sinks_only_b (sink keys), ok (both full-row differences
    empty)}. Pure. Self-test: T9 (57f33e7c vs itself: 30 rows, empty) and T10 (57f33e7c vs 7815af09: the 168 sink differences)."""
    ka = dict((_row_key(r), r) for r in cd_a["rows"])
    kb = dict((_row_key(r), r) for r in cd_b["rows"])
    sa, sb = set(str(r["sink"]) for r in cd_a["rows"]), set(str(r["sink"]) for r in cd_b["rows"])
    oa, ob = sorted(set(ka) - set(kb)), sorted(set(kb) - set(ka))
    return {"rows_a": len(cd_a["rows"]), "rows_b": len(cd_b["rows"]), "only_a": oa, "only_b": ob,
            "sinks_only_a": sorted(sa - sb), "sinks_only_b": sorted(sb - sa), "ok": not oa and not ob}


def selftest():
    """T1..T10 on recorded data (docstring above + T7-T10 of card 169-a1-1). Prints GATE lines + the C6 RESULT line; returns rc."""
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
    # ---- T7-T10 (card 169-a1-1): replay of the recorded 168 scratch (diag_c168_a1_2_rbwdel.json, graph 57f33e7c)
    g168 = json.load(open(G168, encoding="utf-8"))
    r168 = json.load(open(os.path.join(HERE, "diag_c168_a1_2_rbwdel.json"), encoding="utf-8"))
    ok7, ev7, _d7 = fs3_check(base, g168, 2626)
    nb7 = fs3_check(base, base, 11261, n_inputs=2)[0]
    gate("T7 fs3_check(7815af09, 57f33e7c, #2626) PASS == recorded F-S3 {0}; #11261 (unwired in 7815af09) not ok".format(
        r168["save_gates"]["F-S3"]["pass"]), ok7 is True and r168["save_gates"]["F-S3"]["pass"] is True and nb7 is False, ev7)
    t7f = json.load(open(os.path.join(HERE, "diag_c166_a1_1_tun.json"), encoding="utf-8"))["tunnels"]["p5s01"]
    ok8, ev8, _c8 = fs4_check(r168["tunnels"], t7f)
    bad = json.loads(json.dumps(r168["tunnels"]))
    bad["5204"]["index_mode"] = 1
    gate("T8 fs4_check(168 tunnels, stored 7f2582ae) PASS == recorded F-S4 {0}; IndexMode altered -> not ok; {{}} -> not ok".format(
        r168["save_gates"]["F-S4"]["pass"]), ok8 is True and r168["save_gates"]["F-S4"]["pass"] is True and fs4_check(bad, t7f)[0] is False
        and fs4_check({}, t7f)[0] is False, ev8)
    c168 = frame_cdiff(g168)
    d9 = cdiff_rowset_diff(c168, frame_cdiff(g168))
    gate("T9 cdiff_rowset_diff(57f33e7c, 57f33e7c): 30 rows (= recorded fs5.diff_rows {0}), both differences empty".format(
        r168["fs5"]["diff_rows"]), d9["ok"] and d9["rows_a"] == 30 == r168["fs5"]["diff_rows"], {k: d9[k] for k in ("rows_a", "rows_b")})
    d10 = cdiff_rowset_diff(c168, cd)
    gate("T10 cdiff_rowset_diff(57f33e7c, 7815af09): not ok; 57f33e7c-only sinks include t8323's row; 7815af09-only include #11261's",
         not d10["ok"] and "8323|ControlTerminal|Force (pN) vs Extension (nm) |0" in d10["sinks_only_a"]
         and any(x.startswith("11261|") for x in d10["sinks_only_b"]),
         {"sinks_only_a": d10["sinks_only_a"], "sinks_only_b": d10["sinks_only_b"], "rows": (d10["rows_a"], d10["rows_b"])})
    print(PR.result_line(PR.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
    return 1 if G["fail"] else 0


if __name__ == "__main__" and "--selftest" in sys.argv:
    sys.exit(selftest())
