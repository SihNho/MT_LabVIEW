r"""diag_c98_fgate - card 98-1 (PD206(h)): READ why the gated S1 copy breaks. FACTS ONLY. Runs stage_d1_fgate.body UNCHANGED
(imported: same plan rows plans/plan_fgate_97.json, same acts) and STOPS at E3; hooks only RECORD (_op case uids, junk_purge
'move_into_frame' = after move A/B, es E1/E3). FOUND FIRST, no new op: allterms read_terms(OpAllTerms_v1)/all_wire_uids/join_wires,
Stage.save(broken_ok)->gui_save, Stage.broken_wire_count (RBW), errorlist_check --vi, build_d1_v0.owner_of. PREDICTION: ExecState
E1 1, after A 0, after B 0, E3 0 (fgate_97_stage2.log:287,394); BROKEN md5 == copy. LIMITS: no read-only Is Broken? op (NAMES.md
:1081) -> broken = removed by RBW on a SCRATCH; Error List uids unreadable (errorlist_check.py:10-12).  Run: MATERIAL=1 bgrun 45."""
import collections, json, os, shutil, subprocess, sys, time                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); TOOLS = os.path.dirname(HERE); sys.path[:0] = [TOOLS, HERE]  # noqa: E702
import stagekit as K, gscript as g, allterms as AT, stage_d1_fgate as F                         # noqa: E401,E402
PLAN = "plans/plan_fgate_97.json"; P, U, DRY, W, V1 = F.P, F.P["uids"], F.DRY, g.MOVE_DST, AT.OP_ALLTERMS_V1   # noqa: E702
TS = time.strftime("%Y%m%d_%H%M%S"); OUT = os.path.join(K.BENCH, "diag_c98_fgate_{0}.json".format(TS))  # noqa: E702
BROKEN, RB = (os.path.join(K.CLAUDEDEV, n.format(TS)) for n in ("D1_s1_fgate_BROKEN_{0}.vi", "scratch_c98_rbw_{0}.vi"))
end = lambda c, u, t: "{0}#{1}:{2}".format(c, u, t) if u else "none"                              # noqa: E731
Done = type("Done", (Exception,), {})


class Dg(K.Stage):
    def _op(self, verb, fn, detail=""):
        r = K.Stage._op(self, verb, fn, detail)
        _x = verb == "case_in" and isinstance(r.get("result"), dict) and self.R.setdefault("cases", {}).update({detail: r["result"].get("case")})  # noqa: F841
        return r
    def junk_purge(self, tag="", hints=()):
        out = K.Stage.junk_purge(self, tag, hints)
        if tag == "move_into_frame":
            self.nmv = getattr(self, "nmv", 0) + 1; self.checkpoint("after move " + "AB?"[min(self.nmv, 3) - 1])  # noqa: E702
        return out
    def es(self, tag, target=None):
        v = K.Stage.es(self, tag, target)
        _x = tag in ("E1", "E3") and self.checkpoint(tag, v)                                          # noqa: F841
        if tag == "E3":
            self.finish(); raise Done()                                                               # noqa: E702
        return v
    def dmap(self):
        m = {int(U["for_body"]): "for_body", int(U["loop_body"]): "loop_body"}
        for t, c in sorted((self.R.get("cases") or {}).items()):
            fr = g.case_frames(W, c); m.update((int(f), "{0}_{1}".format(t, str(n).strip())) for n, f in zip(fr["names"], fr["frames"]))  # noqa: E702
        self.R["diagram_labels"] = m; return m                                                       # noqa: E702
    def wires(self, target):
        rows, wu = AT.read_terms(target, op=V1)[0], AT.all_wire_uids(target)[0]; dg = {}              # noqa: E702
        [dg.setdefault(int(r["wire_uid"]), set()).add(int(r.get("frame_diagram") or 0)) for r in rows if r["wire_uid"]]
        lab = lambda w: "/".join(sorted(self.dm.get(d, "d{0}".format(d)) for d in dg.get(w, ()))) or "none"   # noqa: E731
        return dict((int(w["wire_uid"]), dict(w, diag=lab(int(w["wire_uid"])), src=end(w["src_class"], w["src_uid"], w["src_term"]),
                    sink=end(w["sink_class"], w["sink_uid"], w["sink_term"]))) for w in AT.join_wires(rows, wu))
    def checkpoint(self, tag, v=None):
        v = self.es(tag) if v is None else v
        res, err = self.safe("checkpoint " + tag, lambda: self._cp(tag, v))
        self.R.setdefault("cp", {})[tag] = res or {"err": err}; self.dump()                           # noqa: E702
    def _cp(self, tag, v):
        self.dm = getattr(self, "dm", None) or self.dmap(); J = self.wires(W); prev = getattr(self, "prev", None)   # noqa: E702
        per = collections.Counter(w["diag"] for w in J.values()); keep = dict((k, per.get(k, 0)) for k in sorted(set(self.dm.values())))  # noqa: E702
        odd = [w for w in J.values() if w["termless"] or w["n_src"] != 1 or w["n_sink"] == 0]
        new, gone = (sorted(set(J) - prev), sorted(prev - set(J))) if prev is not None else ([], [])
        self.prev = set(J)
        rec = {"exec_state": v, "wires": len(J), "per_diagram": keep, "other": len(J) - sum(keep.values()), "odd": odd,
               "new": [J[u] for u in new], "gone": gone, "mb": round((K.private_bytes() or 0) / 1e6, 1)}
        self.fact("CP {0}: ExecState {1} wires {2} per-diagram {3} other {4} MB {5}".format(tag, v, len(J), keep, rec["other"], rec["mb"]))
        self.fact("CP {0}: new {1} gone {2} {3}; odd (termless / n_src!=1 / no sink) {4}".format(tag, len(new), len(gone), gone, [
            (w["wire_uid"], w["diag"], w["n_src"], w["n_sink"], w["src"], w["sink"]) for w in odd]))
        [self.fact("CP {0} NEW w{1} [{2}] {3} -> {4} (src {5}, sinks {6})".format(tag, w["wire_uid"], w["diag"], w["src"], w["sink"], w["n_src"], w["n_sink"])) for w in rec["new"]]
        for w in [w for w in odd if w["termless"] and tag == "E3"]:
            w["owner"] = self.safe("owner_of w{0}".format(w["wire_uid"]), lambda u=w["wire_uid"]: K.mod("build_d1_v0").owner_of(W, u, strict=False))[0]
            self.fact("CP E3 termless w{0} owner {1}".format(w["wire_uid"], w["owner"]))
        return rec
    def finish(self):
        self.census(tag="E3")
        shot = lambda n: DRY or g._lv_gui("-Action", "shot", "-Out", '"{0}"'.format(os.path.join(K.BENCH, "diag_c98_fgate_{0}_{1}.png".format(TS, n))))  # noqa: E731
        m = (shot("before_save"), self.save(broken_ok=True), shot("after_save"))[1]; _x = m and not DRY and shutil.copyfile(W, BROKEN)  # noqa: E702,F841
        self.gate("B1 {0} saved (route {1}) == the saved bytes".format(os.path.basename(BROKEN), self.R["saves"].get("route")),
                  DRY or (m and K.md5(BROKEN) == m), m, fatal=True)
        self.R["broken"] = {"path": BROKEN, "md5": m, "bytes": os.path.exists(BROKEN) and os.path.getsize(BROKEN)}
        if DRY:
            return
        shutil.copyfile(BROKEN, RB); self.gate("SC scratch == BROKEN bytes", K.md5(RB) == m, RB, fatal=True)   # noqa: E702
        self.safe("ensure_loaded(scratch)", lambda: g.ensure_loaded(RB)); self.es("scratch before RBW", RB)   # noqa: E702
        J = self.wires(RB); b = self.broken_wire_count(target=RB, tag="RBW"); w1 = set(AT.all_wire_uids(RB)[0])   # noqa: E702
        oddE3 = set(w["wire_uid"] for w in (self.R.get("cp", {}).get("E3") or {}).get("odd", []))
        rm = [dict(wire=u, is_broken_rbw=True, diag=J[u]["diag"], src=J[u]["src"], sink=J[u]["sink"], n_src=J[u]["n_src"],
                   n_sink=J[u]["n_sink"], in_E3_odd=u in oddE3) for u in sorted(set(J) - w1)]
        [self.fact("RBW REMOVED w{wire} [{diag}] {src} -> {sink} (src {n_src}, sinks {n_sink}) in E3-odd {in_E3_odd}".format(**x)) for x in rm]
        es2 = self.es("scratch after RBW", RB); self.R["rbw"] = dict(b, removed=rm, exec_state_after=es2)   # noqa: E702
        self.fact("RBW on scratch: {0} removed ({1} were in the E3 odd list of {2}); ExecState after {3}".format(len(rm), sum(x["in_E3_odd"] for x in rm), len(oddE3), es2))
        self.safe("save scratch after RBW", lambda: g.save(RB, allow_broken=(es2 != 1))); self.safe("close scratch", lambda: g.close_panel(RB))  # noqa: E702
    def close(self, expect_files=None):
        return K.Stage.close(self, [os.path.basename(p) for p in (BROKEN, RB) if os.path.exists(p)])

def body(s):
    s.gate("P0 {0} is the plan stage_d1_fgate.body reads".format(PLAN), F.P == F.J(K.BENCH, PLAN), fatal=True)
    try:
        F.body(s); s.gate("E3 stop reached", False)                                                   # noqa: E702
    except Done:
        s.fact("STOPPED AT E3 by design (card 98-1): nothing after E3 ran")

def errorlist(st, tag, p):
    r = subprocess.run([sys.executable, "-u", os.path.join(TOOLS, "errorlist_check.py"), "--vi", p], capture_output=True, timeout=900,
                       cwd=os.path.dirname(TOOLS), env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    txt = r.stdout.decode("utf-8", "replace"); print(txt[-3000:], flush=True)                          # noqa: E702
    jp = ([ln.split(None, 2)[-1] for ln in txt.splitlines() if ln.startswith("ERRORLIST-VERDICT:")] or [""])[-1]
    d = json.load(open(jp, encoding="utf-8")) if jp and os.path.exists(jp) else {}; gt = d.get("gates") or {}   # noqa: E702
    st.R.setdefault("errorlist", {})[tag] = {"json": jp, "n": d.get("n_reported"), "items": [(i.get("index"), i.get("object"), i.get("raw")) for i in d.get("items") or []]}
    st.gate("EL {0}: Error List read, items == window N ({1}), file md5 unchanged".format(tag, d.get("n_reported")), gt.get("all_items_read") and gt.get("bed_md5_unchanged"), jp)
    [st.fact("EL {0} item {1}: object {2!r} | {3!r} | uid None (unreadable)".format(tag, *x)) for x in st.R["errorlist"][tag]["items"]]

if __name__ == "__main__":
    g.restore_move_fixtures(); FXL = K.fixture_listing()                                              # noqa: E702
    st = Dg(os.path.join(K.CLAUDEDEV, P["input"]["vi"]), P["input"]["md5"], "diag_c98_fgate", preload=False, deadline_min=40,
            work_dir=os.path.dirname(W), work_name=os.path.basename(W), task="card 98-1", out_json=OUT)
    rc = K.run(body, st)
    if not DRY:
        K.mod("bench_prep").restart_labview(); g.reset(); g.restore_move_fixtures()                   # noqa: E702
        st.gate("FX Moving-Objects fixtures restored", K.fixtures_check((st.input_md5,), FXL))
        [errorlist(st, t, p) for t, p in (("BROKEN", BROKEN), ("RBW", RB)) if os.path.exists(p)]
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, timeout=60); time.sleep(4.0)   # noqa: E702
        _x = os.path.exists(RB) and os.remove(RB); st.gate("H4 scratch deleted {0}".format(os.path.basename(RB)), not os.path.exists(RB))  # noqa: E702,F841
        st.gate("K9 S1 md5 unchanged", K.md5(st.input_vi) == st.input_md5, K.md5(st.input_vi))
        st.gate("LabVIEW gone at exit", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
        st.dump(); rc = st.summary()                                                                  # noqa: E702
    sys.exit(rc)
