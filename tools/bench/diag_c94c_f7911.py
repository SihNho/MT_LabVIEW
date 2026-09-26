r"""diag_c94c_f7911.py - card 94-3 part (3): READ-ONLY facts about For #7911 (the For loop whose body diagram is
uid 7911, on #637's body diagram 639) on a unique scratch BYTE COPY of D1_s1_copy.vi (never the file itself).
Existing ops only (checked docs/toolkit-capabilities.md rows 23-27, 62-65): OpOwnerChain_v1 (build_d1_v0.owner_of),
OpLoopCast_v1 (g.loop_cast: loop uid, N wire, Shift Registers[], parallel enabled, static P), OpTunnels_v0
(g.tunnels: IndexMode per LoopTunnel), OpWireSource_v5 (Stage.net_sources), OpConstValueN_v1 (numeric constant).
Offline already known (tools/bench/f7911_facts_94_offline.log): tunnels with an inner terminal on d7911 =
7922(Tunnel) 9087 9227 9503 10004 10177 11363 28370 31051 31137; 9087 outer <- LeftSR#9025, 9227 outer -> RightSR#9018.
PREDICTION CONTRACT: owner_of(7911) = ForLoop X (X on report_all('ForLoop')); owner_of(X) = Diagram 639;
every listed LoopTunnel's owner = X; owner_of(9025) and owner_of(9018) = WhileLoop 637; consts 8775/8795 read
back with their own uid echo. Unreadable -> NOT READABLE (fact), no new op. Nothing saved; no VI run.
"""
import json, os, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K
g = K.g
from build_d1_v0 import owner_of

S1 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"); S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"
TUNNELS = [9087, 9227, 9503, 10004, 10177, 11363, 28370, 31051, 31137]
s = K.Stage(S1, S1_MD5, "diag_c94c_f7911", work_name="scratch_c94c_%s.vi" % time.strftime("%Y%m%d_%H%M%S"),
            deadline_min=18, reserve_s=180, task="94-3")


def own(uid):
    v, err = s.safe("owner_of(%d)" % uid, lambda: owner_of(s.work, uid, strict=True))
    s.fact("OWNER #%d -> %s" % (uid, "NOT READABLE (%s)" % err[:120] if err else "%s#%s" % v))
    return v


def read_const(uid):
    lab = json.load(open(os.path.join(HERE, "opconstvaluen_v1_labels.json"), encoding="utf-8"))
    idx = s.uid_index("DigitalNumericConstant", uid)
    if idx is None:
        return s.fact("CONST #%d NOT READABLE: not in DigitalNumericConstant traverse" % uid)
    vi = g.op(os.path.join(g.CLAUDEDEV, "OpConstValueN_v1.vi"))
    vi.SetControlValue(lab["text"], "POISON"); vi.SetControlValue(lab["wire"], -1); vi.SetControlValue("UID", 0)
    vi.SetControlValue(lab["size"], False); vi.SetControlValue("vi path", s.work)
    vi.SetControlValue("Class Name", "DigitalNumericConstant"); vi.SetControlValue("index", idx)
    g._run(vi)
    r = dict(uid_back=int(vi.GetControlValue("UID")), text=vi.GetControlValue(lab["text"]),
             repr=vi.GetControlValue(lab["repr"]), wire=int(vi.GetControlValue(lab["wire"])), err=g._err(vi, "error out") or "")
    s.gate("C #%d const read, uid echo" % uid, r["uid_back"] == uid and not r["err"], repr(r))
    s.fact("CONST #%d text=%r repr=%r drives w%d" % (uid, r["text"], r["repr"], r["wire"]))
    s.R.setdefault("consts", {})[uid] = r


def body(_):
    s.start(); s.scratches.append(s.work)   # the work copy IS the scratch: close() deletes it (read-only run)
    bp = K.mod("bench_prep"); s.fact("HANDLES before reads: %r" % bp.labview_handles())
    loop = own(7911)
    s.gate("A owner of diagram 7911 is a ForLoop", bool(loop) and loop[0] == "ForLoop", repr(loop))
    L = int(loop[1]); s.R["loop_uid"] = L
    up = own(L); s.gate("A2 ForLoop's owner is Diagram 639", bool(up) and int(up[1]) == 639, repr(up))
    fl = [o["uid"] for o in g.report_all(s.work, "ForLoop")]; li = fl.index(L) if L in fl else None
    s.gate("A3 ForLoop uid on report_all('ForLoop')", li is not None, "index %r of %d" % (li, len(fl)))
    lc, err = s.safe("loop_cast", lambda: g.loop_cast(s.work, li, "ForLoop"))
    s.R["loop_cast"] = lc
    s.gate("B loop_cast echo == loop uid", bool(lc) and lc["loop_uid"] == L, repr(lc))
    if lc:
        s.fact("LOOP #%d: N wire w%s ; shift registers %d %r ; parallel_enabled %s ; static P %s ; errors %r" % (
            L, lc["n_wire_uid"], len(lc["shift_reg_uids"]), lc["shift_reg_uids"], lc.get("parallel_enabled", "NOT READABLE"),
            lc.get("static_instances", "NOT READABLE"), lc["errors"]))
        if lc["n_wire_uid"]:
            s.net_sources(lc["n_wire_uid"], tag="N-wire")
        else:
            s.fact("LOOP #%d: N terminal UNWIRED (N set by auto-indexed input(s))" % L)
    lt = [o["uid"] for o in g.report_all(s.work, "LoopTunnel")]; s.R["tunnels"] = {}
    for t in TUNNELS:
        o = own(t)
        tr, err = s.safe("tunnels(%d)" % t, lambda: g.tunnels(s.work, lt.index(t))) if t in lt else (None, "not in traverse")
        s.R["tunnels"][t] = {"owner": o, "tun": tr, "err": err}
        s.gate("T #%d owned by loop #%d" % (t, L), bool(o) and int(o[1]) == L, repr(o))
        s.fact("TUNNEL #%d index_mode=%s out_src=%s out_w%s in_w%s uid_echo=%s" % (t, tr and tr["index_mode"], tr and tr["out_is_source"],
               tr and tr["out_wire"], tr and tr["in_wires"], tr and tr["uid"]) if tr else "TUNNEL #%d NOT READABLE %s" % (t, err))
    for sr in (9025, 9018):
        o = own(sr); s.gate("S SR #%d owned by WhileLoop 637" % sr, bool(o) and int(o[1]) == 637, repr(o))
    for w, tag in ((9097, "9087-outer"), (9215, "9227-outer"), (10166, "8634-index-inner"), (10187, "10177-outer")):
        s.net_sources(w, tag=tag)
    for c in (8775, 8795):
        s.safe("read_const(%d)" % c, lambda c=c: read_const(c))
    s.fact("HANDLES after reads: %r" % bp.labview_handles())


rc = K.run(body, s)
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(4)
gone = "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True).stdout
s.gate("Z LabVIEW gone after the run", gone); s.dump(); rc = s.summary()
sys.exit(rc)
