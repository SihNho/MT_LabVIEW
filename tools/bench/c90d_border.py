r"""c90d_border - the TWO border-object terminal readers for diag_c90d_outstanding (the <=120-line split).

A shift register is NOT in any `Diagram.Nodes[]`, so `wmap` / `node_view` cannot address one; both readers
below are uid-anchored walks over ops that already exist: `gscript.loop_cast`:650 (`Loop.Shift Registers[]`
-> every right register's uid, with the loop's own uid echoed back), `gscript.shift_reg_left`:826
(`OpShiftRegs_v1`: the right register's outside/inside terminals + `RightShiftRegister.Left Registers[]`
and the left_index-th left's own two faces - `Terminal.Name` 634A004, `Terminal.Is Source?` 634A003,
`Terminal.Connected Wire` 634A000), and `gscript.tunnels`:981 (`OpTunnels_v0`: a LoopTunnel's outside
terminal + one inside terminal per frame). NOTHING IS WRITTEN; every call is a property read.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import gscript as g                                                                # noqa: E402
import c90d_reads as C                                                             # noqa: E402
from c90d_reads import own, census, srl, tok                                       # noqa: E402


def borders(s, p, art, R):
    """MEASUREMENT 2 (BED) and 3 (CLEAN): the four old border objects - owner, every terminal's wire, and
    each such wire's other endpoints. Nothing is classified; a skipped read says so with its reason."""
    R["borders"][art] = {}
    for uid, cls, old in C.BORDERS:
        if s.left_s() < 140:
            R["borders"][art][str(uid)] = {"unread": "deadline: {0:.0f} s left".format(s.left_s())}
            s.fact("M2/M3 {0} #{1} SKIPPED - {2:.0f} s left".format(art, uid, s.left_s()))
            continue
        rec = (sr_terms(s, p, art, uid, cls, R) if "ShiftRegister" in cls
               else lt_terms(s, p, art, uid, R))
        rec["briefed_class"], rec["severed_stub_wire"] = cls, old
        wires = []
        for t in rec["terms"]:
            w = int(t.get("wire") or 0)
            wires.append(w)
            t["src_tok"] = tok(s, R, "RB|{0}|{1}|{2}|".format(art, uid, t.get("face")),
                               "name={0!r} is_source={1!r} wire={2!r} errs={3!r}".format(
                                   t.get("name"), t.get("is_source"), w, t.get("errs")))
            t["net"] = C.net(s, p, art, w, R, "M2") if w else "none - this terminal carries no wire"
        rec["wires_besides_the_severed_stub"] = sorted({w for w in wires if w and w != old}) or "none"
        tok(s, R, "RBSUM|{0}|{1}|".format(art, uid),
            "found_at={0!r} terminals={1} wires={2!r} besides_stub={3!r}".format(
                rec.get("found_at"), len(rec["terms"]), wires, rec["wires_besides_the_severed_stub"]))
        R["borders"][art][str(uid)] = rec


def sr_terms(s, p, art, uid, cls, R):
    """A shift register's OWN terminals, found by walking `Loop.Shift Registers[]` until the uid matches.

    The owner's OWN class is tried first (a seed casts only its own class - `gscript.loop_cast`:650), then
    the other loop class, so a register on a `ForLoop` is not silently missed."""
    o = own(s, R, art, p, uid, "M2")
    rec = {"owner": o, "route": "gscript.loop_cast + shift_reg_left (OpShiftRegs_v1)", "found_at": None,
           "terms": [], "scanned": []}
    order = [c for c in (str(o.get("owner_class") or ""),) if c in ("WhileLoop", "ForLoop")]
    order += [c for c in ("WhileLoop", "ForLoop") if c not in order]
    for lcls in order:
        loops = census(s, p, art, lcls)
        idxs = [L["i"] for L in loops if L["uid"] == o.get("owner_uid")]
        idxs += [L["i"] for L in loops if L["i"] not in idxs]
        for li in idxs:
            if s.left_s() < 110:
                rec["scan_stopped"] = "deadline: {0:.0f} s left".format(s.left_s())
                return rec
            lc, e = s.safe("{0} loop_cast({1} index {2})".format(art, lcls, li),
                           lambda k=li, c=lcls: g.loop_cast(p, k, c), {})
            regs = [int(u) for u in ((lc or {}).get("shift_reg_uids") or [])]
            rec["scanned"].append({"class": lcls, "index": li, "regs": len(regs)})
            tok(s, R, "RL|{0}|{1}|{2}|".format(art, lcls, li),
                "loop_uid={0!r} census_uid={1!r} regs={2!r} err={3!r}".format(
                    (lc or {}).get("loop_uid"), next((L["uid"] for L in loops if L["i"] == li), None),
                    regs, e))
            for ri in range(len(regs)):
                r = srl(s, p, art, li, ri, 0, lcls)
                lefts = [int(x) for x in (r.get("left_uids") or [])]
                if cls == "RightShiftRegister" and regs[ri] == uid:
                    rec["found_at"] = {"loop_class": lcls, "loop_index": li, "reg_index": ri,
                                       "uid_echo": r.get("uid"), "class_echo": r.get("class"),
                                       "errors": r.get("errors")}
                    rec["terms"] = [dict(r.get("out") or {}, face="RIGHT outside")] + \
                                   [dict(t, face="RIGHT inside") for t in (r.get("inside") or [])]
                elif cls == "LeftShiftRegister" and uid in lefts:
                    lfi = lefts.index(uid)
                    r2 = r if lfi == 0 else srl(s, p, art, li, ri, lfi, lcls)
                    L = r2.get("left") or {}
                    rec["found_at"] = {"loop_class": lcls, "loop_index": li, "reg_index": ri,
                                       "left_index": lfi, "uid_echo": L.get("uid"),
                                       "class_echo": L.get("class"), "right_uid": regs[ri],
                                       "errors": r2.get("errors")}
                    rec["terms"] = [dict(L.get("out") or {}, face="LEFT outside")] + \
                                   [dict(t, face="LEFT inside") for t in (L.get("inside") or [])]
                if rec["found_at"]:
                    return rec
    return rec


def lt_terms(s, p, art, uid, R):
    """A LoopTunnel's two faces: `gscript.tunnels` (OpTunnels_v0), addressed by the LoopTunnel census index."""
    o = own(s, R, art, p, uid, "M2")
    rows = census(s, p, art, "LoopTunnel")
    idx = next((r["i"] for r in rows if r["uid"] == uid), None)
    rec = {"owner": o, "route": "gscript.tunnels (OpTunnels_v0)", "found_at": None, "terms": []}
    if idx is None:
        rec["found_at"] = "unread: #{0} is not in the {1} LoopTunnel census row(s)".format(uid, len(rows))
        return rec
    t, e = s.safe("{0} tunnels(index {1})".format(art, idx), lambda: g.tunnels(p, idx), {})
    t = t or {}
    rec["found_at"] = {"looptunnel_index": idx, "uid_echo": t.get("uid"),
                       "index_mode": t.get("index_mode"), "err_verbatim": e}
    rec["terms"] = [{"face": "outside", "name": t.get("out_name"), "is_source": t.get("out_is_source"),
                     "wire": t.get("out_wire"), "errs": [t.get("out_conn_err"), t.get("out_wire_err")]}]
    rec["terms"] += [{"face": "inside", "name": n, "is_source": b, "wire": w}
                     for n, b, w in zip(t.get("in_names") or [], t.get("in_is_source") or [],
                                        t.get("in_wires") or [])]
    return rec
