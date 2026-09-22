r"""c90d_reads - the READERS for diag_c90d_outstanding (split out only to keep each file <=120 lines).

Every function is a thin caller of something already on disk: `Stage.net_sources`:364 / `safe`:204 /
`scratch`:406 (tools/stagekit.py), `gscript.report_all`:512 / `loop_cast`:650 / `shift_reg_left`:826 /
`tunnels`:981, `build_d1_v0.owner_of`:338 (STRICT uid echo - it RAISES when the echo mismatches).
`tok` / `linemap` / `cite` / `controls` are IMPORTED from `tools/bench/c90c_rows.py` - the same citation
machinery that built `m3a4_row_table.json`, never a second copy. NOTHING NEW IS BUILT, nothing is written
to any VI: every call below is a property read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
from c90c_rows import tok, linemap, cite, controls, NEG                            # noqa: E402,F401

# the four UNREAD wires on the BED -> (wire, struct uid, terminal index, name, the CLEAN row it replaces)
BEDW = ((23985, 48, 3, "VISA resource name", 1731), (24002, 48, 4, "In position", 3947),
        (24009, 10407, 1, "# slices in stack", 9635), (23952, 10407, 4, "VISA out", 7337))
# the four OLD border objects that still hold one live endpoint of a severed wire
BORDERS = ((4344, "LeftShiftRegister", 1731), (4274, "LeftShiftRegister", 3947),
           (9641, "LoopTunnel", 9635), (4334, "RightShiftRegister", 7337))
# every CLEAN row -> the replacement wire measured on its own terminal index (m3a4_row_table.json)
REPL = {1731: 23985, 1893: 23820, 2819: 23811, 3947: 24002, 4833: 23804, 7337: 23952,
        7388: 23838, 9635: 24009, 11232: 23829, 23502: 23847, 23540: 23856}
BORDERISH = ("Tunnel", "ShiftRegister")
CACHE = {}


def own(s, R, art, p, uid, tag):
    """`Generic.Owner` 6327806 -> GObject UID, strict: a uid that does not echo yields `unread` + its error."""
    V = K.mod("build_d1_v0")
    (oc, ou), e = s.safe("{0} owner_of(#{1})".format(tag, uid),
                         lambda: V.owner_of(p, uid, strict=True), (None, None))
    t = tok(s, R, "RO|{0}|{1}|".format(art, uid),
            "owner_class={0!r} owner_uid={1!r} uid_echo={2} err={3!r}".format(
                oc, ou, "OK" if not e else "NOT AN ANSWER", e))
    return {"owner_class": oc if not e else "unread", "owner_uid": ou if not e else "unread",
            "err_verbatim": e, "src_tok": t}


def census(s, p, art, cls):
    key = ("cen", art, cls)
    if key not in CACHE:
        rows, _e = s.safe("{0} report_all({1!r})".format(art, cls), lambda: g.report_all(p, cls), [])
        CACHE[key] = rows or []
    return CACHE[key]


def net(s, p, art, w, R, tag):
    """One CACHED `Stage.net_sources` read (n=8) - every terminal row of the wire, error columns verbatim."""
    key = ("net", art, int(w))
    if key in CACHE:
        return CACHE[key]
    out = s.net_sources(int(w), n=8, target=p, tag="{0}-{1}-w{2}".format(tag, art, w))
    eps = []
    for r in (out.get("walk") or []):
        t = tok(s, R, "RN|{0}|w{1}|r{2}|".format(art, w, r.get("i")), "row={0!r}".format(r))
        eps.append({"owner_class": r.get("owner_class"), "owner_uid": r.get("owner_uid"),
                    "terms_index": r.get("i"), "is_source": r.get("is_source"), "recip": r.get("recip"),
                    "err_verbatim": r.get("err", ""), "src_tok": t})
    rec = {"wire": int(w), "rows": len(out.get("walk") or []), "endpoints": eps,
           "real_owner_rows": sorted({(str(e["owner_class"]), int(e["owner_uid"]))
                                      for e in eps if e["owner_uid"]}),
           "err": out.get("err") or "", "pd85_violations": out.get("pd85_violations")}
    tok(s, R, "RNSUM|{0}|w{1}|".format(art, w), "rows={0} real_owners={1!r} err={2!r}".format(
        rec["rows"], rec["real_owner_rows"], rec["err"]))
    CACHE[key] = rec
    return rec


def srl(s, p, art, li, ri, lfi, cls="WhileLoop"):
    key = ("srl", art, cls, li, ri, lfi)
    if key not in CACHE:
        r, e = s.safe("{0} shift_reg_left({1} {2}, reg {3}, left {4})".format(art, cls, li, ri, lfi),
                      lambda: g.shift_reg_left(p, li, ri, lfi, class_name=cls), {})
        r = dict(r or {})
        r["wrapper_err"] = e
        CACHE[key] = r
    return CACHE[key]


def m1(s, p, R):
    """MEASUREMENT 1: the four UNREAD wires on the BED, every terminal row, plus `Generic.Owner` on every
    owner that is a tunnel or a shift register."""
    for w, u, ti, nm, old in BEDW:
        rec = net(s, p, "BED", w, R, "M1")
        rec["on_terminal"] = {"struct_uid": u, "terminal_index": ti, "terminal_name": nm}
        rec["replaces_clean_wire"] = old
        for e in rec["endpoints"]:
            oc = str(e.get("owner_class") or "")
            if e.get("owner_uid") and any(k in oc for k in BORDERISH):
                e["owner_of"] = own(s, R, "BED", p, int(e["owner_uid"]), "M1 w{0}".format(w))
        R["m1"][str(w)] = rec


# The border-object terminal readers live in `tools/bench/c90d_border.py` (the <=120-line split), and the
# v2 row-table assembly in `tools/bench/c90d_table.py`.
