r"""selftest_gateclass_s3 - card chat-S3 (PD328): the user's three answers of 2026-10-03
("메모리 낮추고 터널 개수차이로 멈춤은 유지하고 터널 단자행만 다를 경우 기록하자"). OFFLINE, pure functions, no LabVIEW, no COM.
Soft-log writes go to a temp file (GATE_SOFT_LOG), never to tools/bench/gate_soft_log.jsonl.

PREDICTION CONTRACT (each one gate):
 M1 memory_model.json fail_above_mb == 680.0 and memstop_mb == 695.0 (each with a cite)
 M2 stagexec.MEM_STOP_MB == 695.0, stagexec.X10_FAIL_MB == 680.0, stage_prerun.X10_FAIL_MB == 680.0 (one source)
 M3 Meter default stop: 694.9 MB passes, 695.0 MB raises MEMSTOP
 M4 stage_prerun.mem_margin default margin = 695 - 680 = 15: a recorded checkpoint 680.0 -> ok False, 679.9 -> ok True
 T1 every TUNNEL_OBJECT_CLASSES member +1 is a STOP (count_verdict), disjoint from NON_SEMANTIC_CLASSES
 T2 census_verdict with LoopTunnel 3 vs 2 beside Terminal +3 -> overall STOP
 F1 step_face_rows_verdict: an only_real InnerTerminal on a LoopTunnel present on both sides -> 'log'
 F2 face rows on both sides (only_sim + only_real, FlatSequenceOuterTunnel / SelectorTunnel) -> 'log'
 F3 NEGATIVE face row + an extra tunnel OBJECT (owner on the real side only) -> 'stop'
 F4 NEGATIVE face row + a wire diff (only_real_edges) -> 'stop'
 F5 NEGATIVE a row on a non-tunnel owner (Function) -> 'stop'; owner class differs across sides -> 'stop'
 F6 stagexec.compare on real rows: extra unwired face row -> face_rows 'log' and classify_step_diff == ('log', [])
 F7 stagexec.bind_new: a new face row on an EXISTING tunnel is not a new object (no BINDING stop); a new tunnel OBJECT still is
"""
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TMP = tempfile.mkdtemp(prefix="s3gc_")
os.environ["GATE_SOFT_LOG"] = os.path.join(TMP, "soft.jsonl")
os.environ["GATE_CARD"] = "chat-S3-selftest"
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
import gateclass as GC                                                 # noqa: E402
import protocol                                                        # noqa: E402
import stagexec as SX                                                  # noqa: E402
import stage_prerun as SP                                              # noqa: E402

P, F = [], []


def gate(label, ok, detail=""):
    (P if ok else F).append(label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, json.dumps(detail, default=str)[:400]), flush=True)


mm = json.load(open(os.path.join(ROOT, "tools", "bench", "memory_model.json"), encoding="utf-8"))
gate("M1 memory_model fail_above_mb 680 / memstop_mb 695, cited",
     mm["fail_above_mb"]["value"] == 680.0 and mm["memstop_mb"]["value"] == 695.0 and mm["fail_above_mb"]["cite"] and mm["memstop_mb"]["cite"],
     [mm["fail_above_mb"]["value"], mm["memstop_mb"]["value"]])
gate("M2 one source: SX.MEM_STOP_MB 695, SX.X10_FAIL_MB 680, SP.X10_FAIL_MB 680",
     SX.MEM_STOP_MB == 695.0 and SX.X10_FAIL_MB == 680.0 and SP.X10_FAIL_MB == 680.0, [SX.MEM_STOP_MB, SX.X10_FAIL_MB, SP.X10_FAIL_MB])
seq = iter([int(694.9 * 1048576), int(695.0 * 1048576)])
mt = SX.Meter(lambda: (next(seq), 1), log=lambda *_a: None)
mt("op", 1)
try:
    mt("op", 2)
    gate("M3 Meter default stop 695: 694.9 passes, 695.0 raises MEMSTOP", False, "no stop")
except SX.ExecStop as e:
    gate("M3 Meter default stop 695: 694.9 passes, 695.0 raises MEMSTOP", str(e).startswith("MEMSTOP") and len(mt.rows) == 2, str(e)[:120])


def rec(mb):
    rows = [{"tag": "read", "k": 0, "mb": 600.0}] + [{"tag": t, "k": k, "mb": 600.0 + k} for k in range(1, 4) for t in ("op", "read")]
    rows[-1]["mb"] = mb
    return [{"path": os.path.join(TMP, "x.log"), "mtime": 0, "rows": rows, "stop_after": None, "from_step": None}]


m1, m2 = SP.mem_margin("x.py", records=rec(680.0)), SP.mem_margin("x.py", records=rec(679.9))
gate("M4 mem_margin margin 15: checkpoint 680.0 -> ok False, 679.9 -> ok True",
     m1["ok"] is False and m2["ok"] is True and m1["margin_mb"] == 15.0, [m1.get("ok"), m2.get("ok"), m1.get("margin_mb"), m1.get("peak_mb")])

gate("T1 tunnel OBJECT classes +1 STOP, disjoint from NON_SEMANTIC (PD328(b))",
     all(GC.count_verdict(c, 3, 2)[0] == "stop" for c in GC.TUNNEL_OBJECT_CLASSES) and not (GC.TUNNEL_OBJECT_CLASSES & GC.NON_SEMANTIC_CLASSES)
     and {"LoopTunnel", "FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel", "SelectorTunnel", "Tunnel"} <= GC.TUNNEL_OBJECT_CLASSES,
     sorted(GC.TUNNEL_OBJECT_CLASSES))
cv = GC.census_verdict({"LoopTunnel": 3, "Terminal": 12}, {"LoopTunnel": 2, "Terminal": 9})
gate("T2 census LoopTunnel 3 vs 2 beside Terminal +3 -> STOP", cv["verdict"] == "stop", cv)


def row(t, o, oc, tc="InnerTerminal", w=0, src=False, name=""):
    return {"term_uid": t, "term_name": name, "is_source": src, "wire_uid": w, "owner_uid": o, "owner_class": oc,
            "frame_diagram": 0, "term_class": tc}


BASE = [row(1, 100, "LoopTunnel", "OuterTerminal", 9, False), row(2, 100, "LoopTunnel", "InnerTerminal"),
        row(5, 200, "Function", "ParameterTerminal", 9, True, "x"),
        row(11, 300, "FlatSequenceOuterTunnel", "Terminal"), row(12, 400, "SelectorTunnel", "OuterTerminal")]
D0 = dict((k, []) for k in GC.STEP_HARD_KEYS)
v1 = GC.step_face_rows_verdict(dict(D0, only_sim_terms=[], only_real_terms=[3]), BASE, BASE + [row(3, 100, "LoopTunnel")])
gate("F1 only_real face row on a LoopTunnel present on both sides -> log", v1["verdict"] == "log", v1)
v2 = GC.step_face_rows_verdict(dict(D0, only_sim_terms=[13], only_real_terms=[14]), BASE + [row(13, 300, "FlatSequenceOuterTunnel", "Terminal")],
                               BASE + [row(14, 400, "SelectorTunnel", "InnerTerminal")])
gate("F2 face rows on both sides (FSOT sim-only, SelectorTunnel real-only) -> log", v2["verdict"] == "log", v2)
v3 = GC.step_face_rows_verdict(dict(D0, only_real_terms=[3, 21]), BASE, BASE + [row(3, 100, "LoopTunnel"), row(21, 999, "LoopTunnel", "OuterTerminal")])
gate("F3 NEGATIVE face row + an extra tunnel OBJECT #999 -> stop", v3["verdict"] == "stop" and "one side only" in v3["rule"], v3)
v4 = GC.step_face_rows_verdict(dict(D0, only_real_terms=[3], only_real_edges=[[5, 3]]), BASE, BASE + [row(3, 100, "LoopTunnel", w=9)])
gate("F4 NEGATIVE face row + a wire diff -> stop", v4["verdict"] == "stop" and "only_real_edges" in v4["rule"], v4)
v5 = GC.step_face_rows_verdict(dict(D0, only_real_terms=[6]), BASE, BASE + [row(6, 200, "Function", "ParameterTerminal")])
real6 = [dict(r, owner_class="Tunnel") if r["owner_uid"] == 100 else r for r in BASE] + [row(3, 100, "Tunnel")]
v6 = GC.step_face_rows_verdict(dict(D0, only_real_terms=[3]), BASE, real6)
gate("F5 NEGATIVE non-tunnel owner -> stop; owner class LoopTunnel vs Tunnel -> stop",
     v5["verdict"] == "stop" and v6["verdict"] == "stop", [v5["rule"], v6["rule"]])

bind = {"term": {}, "obj": {}}
d7 = SX.compare(BASE, BASE + [row(3, 100, "LoopTunnel")], bind)
gate("F6 stagexec.compare: extra unwired face row -> face_rows log, classify_step_diff ('log', [])",
     (d7.get("face_rows") or {}).get("verdict") == "log" and SX.classify_step_diff({"actions": []}, 0, d7) == ("log", []), d7)
try:
    made = SX.bind_new(BASE, BASE + [row(3, 100, "LoopTunnel")], BASE, BASE, {"term": {}, "obj": {}})
    ok_a = made == {}
except SX.ExecStop as e:
    ok_a, made = False, str(e)[:160]
try:
    SX.bind_new(BASE, BASE + [row(21, 999, "LoopTunnel", "OuterTerminal")], BASE, BASE, {"term": {}, "obj": {}})
    ok_b, eb = False, "no stop"
except SX.ExecStop as e:
    ok_b, eb = str(e).startswith("BINDING"), str(e)[:160]
gate("F7 bind_new: new face row on an existing tunnel binds nothing (no stop); a new tunnel OBJECT -> BINDING stop", ok_a and ok_b, [made, eb])

print("=== GATES: {0} pass / {1} fail".format(len(P), len(F)), flush=True)
print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None)))
sys.exit(0 if not F else 1)
