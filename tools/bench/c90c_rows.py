r"""c90c_rows - the READERS for diag_c90c_rowtable (split out only to keep each file <=120 lines).

Every function is a thin caller of something that exists: `Stage.net_sources`:364 / `wired_terminals`:354
(tools/stagekit.py), `build_d1_m3a1.term_state`:524, `build_d1_v0.owner_of`:338 (strict uid echo),
`gscript.report_all`:512. NOTHING NEW IS BUILT; every call below is a property read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

WIRES = [1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]
STRUCTS = (48, 10407)
TUNNELS = (10429, 10978, 11220, 11348)
NEG = 999983

def tok(s, R, t, text):                    # one FACT line + a unique token `linemap` can cite as log:line
    R["tokens"].append(t)
    s.fact("{0} {1}".format(t, text))
    return t

def t1_wires(s, p, census, R):
    """TASK 1: each of the 11 read WHOLE (n=8); the row dict prints VERBATIM, error columns included."""
    for w in WIRES:
        out = s.net_sources(w, n=8, target=p, tag="T1w{0}".format(w))
        walk = out.get("walk") or []
        rec = {"in_clean_wire_census": w in census, "rows": len(walk), "walk": walk,
               "err": out.get("err") or "", "pd85_violations": out.get("pd85_violations"),
               "real_rows": sum(1 for r in walk if r.get("owner_uid")), "endpoints": []}
        for r in walk:
            t = tok(s, R, "RT1|CLEAN|w{0}|r{1}|".format(w, r.get("i")), "row={0!r}".format(r))
            rec["endpoints"].append({"owner_class": r.get("owner_class"), "owner_uid": r.get("owner_uid"),
                                     "terms_index": r.get("i"), "is_source": r.get("is_source"),
                                     "recip": r.get("recip"), "err_verbatim": r.get("err", ""),
                                     "src_tok": t})
        tok(s, R, "RT1SUM|w{0}|".format(w), "rows={0} real_owner_rows={1} in_census={2} err={3!r}".format(
            rec["rows"], rec["real_rows"], rec["in_clean_wire_census"], rec["err"]))
        R["task1"][str(w)] = rec

def t2_terms(s, p, art, R):
    """TASK 2: index -> (Terminal.Name, Terminal.Connected Wire, WIRED/BARE/UNREAD) for #48 and #10407."""
    M = K.mod("build_d1_m3a1")
    R["task2"][art] = {}
    for u in STRUCTS:
        loc, rows = s.wired_terminals(u, hints=(), target=p, tag="T2-{0}-{1}".format(art, u))
        tab = {}
        for r in rows:
            st = M.term_state(r)
            t = tok(s, R, "RT2|{0}|{1}|t{2}|".format(art, u, r.get("i")),
                    "name={0!r} is_source={1!r} connected_wire={2!r} state={3} errs={4!r}".format(
                        r.get("name"), r.get("is_source"), r.get("wire"), st, r.get("errs")))
            tab[str(r.get("i"))] = {"name": r.get("name"), "wire": r.get("wire") or 0, "state": st,
                                    "is_source": r.get("is_source"), "bare": st == "BARE",
                                    "errs": r.get("errs"), "src_tok": t}
        f = (loc or {}).get("found") or {}
        tok(s, R, "RT2SUM|{0}|{1}|".format(art, u), "terminals={0} uid_echo={1!r} found={2!r}".format(
            len(rows), (loc or {}).get("uid_echo"), f))
        R["task2"][art][str(u)] = {"terminal_count": len(rows), "uid_echo": (loc or {}).get("uid_echo"),
                                   "found": f, "terminals": tab}

def t3_owners(s, p, R):
    """TASK 3: `Generic.Owner` 6327806 -> GObject UID on the four tunnels, plus each one's own class."""
    V = K.mod("build_d1_v0")
    rows, _e = s.safe("T3 report_all('Tunnel')", lambda: g.report_all(p, "Tunnel"), [])
    by = {r["uid"]: r for r in (rows or [])}
    for u in TUNNELS:
        (oc, ou), e = s.safe("T3 owner_of(#{0})".format(u), lambda uu=u: V.owner_of(p, uu, strict=True),
                             (None, None))
        c = by.get(u, {})
        t = tok(s, R, "RT3|{0}|".format(u), "owner_class={0!r} owner_uid={1!r} uid_echo={2} "
                "census_class={3!r} census_owner={4!r} err={5!r}".format(
                    oc, ou, "OK" if not e else "NOT AN ANSWER", c.get("class"), c.get("owner"), e))
        R["task3"][str(u)] = {"owner_class": oc if not e else "unread", "tunnel_class": c.get("class"),
                              "owner_uid": ou if not e else "unread", "census_owner": c.get("owner"),
                              "err_verbatim": e, "src_tok": t}

def controls(s, p, art, census, pos, R):
    """The two mandatory controls as VALUES: the negative uid must not echo; one intact wire must read."""
    (oc, ou), e = s.safe("CTL negative owner_of(#{0}) on {1}".format(NEG, art),
                         lambda: K.mod("build_d1_v0").owner_of(p, NEG, strict=True), (None, None))
    tok(s, R, "RTC|NEG|{0}|".format(art), "owner_of({0}) -> {1!r} #{2!r} ; RAISED={3!r}".format(
        NEG, oc, ou, e))
    s.gate("G2 {0}: the NEGATIVE uid {1} does NOT echo back (strict owner_of refuses it)".format(art, NEG),
           bool(e), "raised {0!r}".format(e)[:200])
    out = s.net_sources(pos, n=8, target=p, tag="CTLpos-{0}-w{1}".format(art, pos))
    real = [r for r in (out.get("walk") or []) if r.get("owner_uid")]
    tok(s, R, "RTC|POS|{0}|".format(art), "intact wire {0}: rows={1} real={2} owners={3!r} PD85={4}".format(
        pos, len(out.get("walk") or []), len(real), out.get("all_owners"), out.get("pd85_violations")))
    s.gate("G3 {0}: the intact POSITIVE control wire {1} yields >=1 real owner row, PD85 0".format(art, pos),
           len(real) >= 1 and out.get("pd85_violations") == 0,
           "{0} real row(s), PD85 {1}".format(len(real), out.get("pd85_violations")))
    R["controls"][art] = {"negative_uid": NEG, "negative_raised": e, "positive_wire": pos,
                          "positive_real_rows": len(real), "positive_owners": out.get("all_owners"),
                          "positive_pd85": out.get("pd85_violations"), "wire_census": len(census)}

def linemap(R, logp):
    """Each token's own line number in THIS run's log, so every cell of the table cites `log:line`."""
    sys.stdout.flush()
    try:
        with open(logp, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except Exception as e:                                                         # noqa: BLE001
        return {}, "log unreadable: {0}".format(e)
    m = {}
    for i, ln in enumerate(lines, 1):
        for t in R["tokens"]:
            if t not in m and t in ln:
                m[t] = "{0}:{1}".format(os.path.basename(logp), i)
    return m, ""

def cite(n, m):
    """Replace every `src_tok` by its `log:line`; a token the log never carried becomes `unread`."""
    if isinstance(n, dict):
        t = n.pop("src_tok", None)
        if t:
            n["src"] = m.get(t, "unread (token {0} never reached the log)".format(t))
    for v in (n.values() if isinstance(n, dict) else n if isinstance(n, list) else ()):
        cite(v, m)
