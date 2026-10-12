# ---
# labview: read
# hardware: none
# evidence: tools/bench/diag_c166_a1_1_tun_plan.json
# ---
r"""diag_c166_a1_1_tun - card 166-a1-1 step 4 (rule-1a tunnel check, docs/d1/ring-p5c.md:257-260): LoopTunnels #5204 and #10404 -
IndexMode and the OUTER terminal's data type - in the P5 final claudeDev\D1_ring_p5_20261010_172913.vi (75773b0d) AND in P5-1
claudeDev\D1_ring_p5s01_20261009_124542.vi (7f2582ae), READ-ONLY, each on a NEVER-SAVED byte copy (stagekit.Stage work copy +
Stage.scratch, both deleted at close; nothing is saved).
Found before writing (no new op, no new verb): gscript.tunnels (tools/gscript.py:1270, OpTunnels_v0: uid, index_mode, out_name,
out_is_source, out_wire) and gscript.read_term_type (tools/gscript.py:4646, OpTermDataType_v0: Terminal.Data Type -> TD bytes,
`types.canon` label-free, `types.sig` label-exact); both listed in docs/toolkit-capabilities.md:949,972. The LoopTunnel index is
gscript._uid_index (re-read at the call site). Outer-face terminal uids 9631 (#5204) / 24363 (#10404) from the stored graph reads
graph_ring_p5s01_20261009_125622.json and graph_ring_p5s02d_20261010_154830.json (diag_c166_a1_1_q_*.log); each read echoes the uid.
Memory: the graph read measured 647.8 MB after ONE load (diag_c165_a3_4_graph.log); the first copy is closed and deleted before the
second is opened; if private bytes stay above RESTART_MB the LabVIEW instance is restarted (standing authority) and that is reported.
PREDICTION CONTRACT: RQ the two verbs + two ops found offline (protocol.check_requires); per file and tunnel: echo uid == asked,
out_wire == the graph's outer wire (4337 / 9636), outer term echo == 9631 / 24363, out_is_source True; R1A IndexMode equal in both
files and outer type canon + sig equal in both files; MEM peak < 695 (memstop); X both VI md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c166_a1_1_tun.log -- py -u tools/bench/diag_c166_a1_1_tun.py"""
import json, os, sys                                                                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K, protocol as PR                                                         # noqa: E401,E402
g = K.g
PL = json.load(open(os.path.join(HERE, "diag_c166_a1_1_tun_plan.json"), encoding="utf-8"))
FILES = [tuple(f) for f in PL["files"]]
TUN = dict((int(k), v) for k, v in PL["tunnels"].items())
RESTART_MB, MEMSTOP_MB = PL["restart_mb"], PL["memstop_mb"]
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(FILES[0][1], FILES[0][2], "scratch_c166_a1_1_tun", preload=False, deadline_min=13, reserve_s=120,
            out_json=os.path.join(HERE, "diag_c166_a1_1_tun.json"), task="card 166-a1-1 rule-1a tunnel read")


def mb():
    return round((K.private_bytes() or 0) / 1e6, 1)


def read_file(tag, W):
    out, peak = {}, mb()
    for u, exp in sorted(TUN.items()):
        i = s.safe("LoopTunnel index of #{0} in {1}".format(u, tag), lambda uu=u: g._uid_index(W, "LoopTunnel", uu), None)[0]
        t = s.safe("gscript.tunnels {0} #{1}".format(tag, u), lambda ii=i: g.tunnels(W, ii), None)[0] if i is not None else None
        ty = s.safe("gscript.read_term_type {0} t{1}".format(tag, exp["outer_term"]),
                    lambda: g.read_term_type(W, exp["outer_term"]), None)[0]
        tt = (ty or {}).get("types") or {}
        r = {"index": i, "echo": (t or {}).get("uid"), "index_mode": (t or {}).get("index_mode"), "out_name": (t or {}).get("out_name"),
             "out_is_source": (t or {}).get("out_is_source"), "out_wire": (t or {}).get("out_wire"), "in_wires": (t or {}).get("in_wires"),
             "term_echo": (ty or {}).get("echo"), "type_err": (ty or {}).get("err"), "canon": tt.get("canon"), "sig": tt.get("sig"),
             "top_name": tt.get("top_name"), "bytes_hex": (ty or {}).get("bytes_hex")}
        out[str(u)] = r
        peak = max(peak, mb())
        s.fact("TUN {0} #{1}: {2}".format(tag, u, json.dumps(dict((k, v) for k, v in r.items() if k != "bytes_hex"), sort_keys=True)))
        s.gate("T {0} #{1}: echo #{1}, out_wire w{2}, outer term echo t{3}, type read without error, outer face is a source".format(
            tag, u, exp["out_wire"], exp["outer_term"]),
               r["echo"] == u and r["out_wire"] == exp["out_wire"] and r["term_echo"] == exp["outer_term"] and not r["type_err"]
               and r["canon"] and r["out_is_source"] is True, r)
    s.fact("MEM {0} after reads: {1} MB private (peak seen {2})".format(tag, mb(), peak))
    return out, peak


def body(_):
    req = PR.check_requires({"requires": [{"kind": "verb", "name": "tunnels"}, {"kind": "verb", "name": "read_term_type"},
                                          {"kind": "op", "name": "OpTunnels_v0"}, {"kind": "op", "name": "OpTermDataType_v0"}]})
    s.fact("RQ found {0}".format([(x["name"], x["cite"]) for x in req["found"]]))
    s.gate("RQ the existing verbs gscript.tunnels / read_term_type and ops OpTunnels_v0 / OpTermDataType_v0 found (protocol.check_requires)",
           req["ok"], req["missing"], fatal=True)
    s.start(); s.discard_work(); W = s.work                                                  # noqa: E702
    if DRY:
        return s.dump()
    s.R["mem"] = {"after_load_p5_mb": mb()}
    s.fact("MEM after load (p5 copy): {0} MB private".format(s.R["mem"]["after_load_p5_mb"]))
    R, peaks = {}, [s.R["mem"]["after_load_p5_mb"]]
    R["p5"], pk = read_file("p5", W); peaks.append(pk)                                      # noqa: E702
    s.drop_scratch(W, tag="H4a")
    s.R["mem"]["after_drop_p5_mb"] = m0 = mb()
    s.fact("MEM after closing + deleting the p5 copy: {0} MB private".format(m0))
    if m0 > RESTART_MB:
        s.fact("RESTART: {0} MB > {1} after the close - restarting LabVIEW before the second copy (standing authority)".format(m0, RESTART_MB))
        s.restart()
        s.R["mem"]["restarted"] = True
    P = s.scratch("p5s01", source=FILES[1][1])
    s.R["mem"]["after_load_p5s01_mb"] = mb(); peaks.append(s.R["mem"]["after_load_p5s01_mb"])   # noqa: E702
    s.fact("MEM after load (p5s01 copy): {0} MB private".format(s.R["mem"]["after_load_p5s01_mb"]))
    R["p5s01"], pk = read_file("p5s01", P); peaks.append(pk)                                # noqa: E702
    s.drop_scratch(P, tag="H4b")
    s.R["tunnels"] = R
    for u in sorted(TUN):
        a, b = R["p5"][str(u)], R["p5s01"][str(u)]
        s.gate("R1A #{0}: IndexMode equal in 75773b0d and 7f2582ae ({1} vs {2})".format(u, a["index_mode"], b["index_mode"]),
               a["index_mode"] is not None and a["index_mode"] == b["index_mode"], (a["index_mode"], b["index_mode"]))
        s.gate("R1A #{0}: outer type equal in 75773b0d and 7f2582ae (canon {1} vs {2}; label-exact sig equal {3})".format(
            u, a["canon"], b["canon"], a["sig"] == b["sig"]), a["canon"] and a["canon"] == b["canon"] and a["sig"] == b["sig"],
               {"p5": (a["canon"], a["sig"]), "p5s01": (b["canon"], b["sig"])})
    s.R["mem"]["peak_mb"] = max(p for p in peaks if p is not None)
    s.gate("MEM peak {0} MB < memstop {1}".format(s.R["mem"]["peak_mb"], MEMSTOP_MB), s.R["mem"]["peak_mb"] < MEMSTOP_MB, s.R["mem"])
    s.gate("X both VI md5 unchanged", all(K.md5(p) == m for _t, p, m in FILES), [K.md5(p) for _t, p, _m in FILES])
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
