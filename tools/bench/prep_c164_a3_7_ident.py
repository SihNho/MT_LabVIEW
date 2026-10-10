# ---
# labview: none
# hardware: none
# evidence: tools/bench/graph_ring_p5s02d_20261010_154830.json
# ---
r"""prep_c164_a3_7_ident - card 164-3-7 (OFFLINE, read-only, no LabVIEW): re-check the plan's deleted nodes of P5-2 step 4 by IDENTITY
(class, owner structure/diagram, position) instead of by uid, on the stored graphs: base graph_ring_p5s02c_20261010_131658.json (3d5196ab) vs
adopted graph_ring_p5s02d_20261010_154830.json (2a5fa0c4, read by diag_c164_a3_5_graph.py from the adopted file 6dcd5c3d). The graphs are the
JSON the E5 check's own reader wrote (wiki_build.read_live objs {uid, class, pos, owner} + terminals + owners); the deleted-node list is the E5
plan's (diag_c164_a3_5_graph_plan.json edits.deleted_nodes). Tunnel owner = the shared stagexec.tunnel_owner (inner frame -> owners); a node's
diagram = frame_diagram of its terminal rows. Then the structural condition of brief_164-3-7.md step 3, each line quoted from its log by search
(no line number typed). Prints facts and gates; writes nothing.
Existing: diag_c164_a3_5_reads.py prints uid rows only (no identity); no identity check by (class, owner, pos) found in tools/*.py
(grep "pos" in stagexec/stagesim: position keys are TERMINAL keys, stagekit.term_identity_pairs, which need a live before/after read).
PREDICTION: I1 #23501 IDENTITY GONE (no LoopTunnel on While with base pos in adopted), I2 #23042 IDENTITY GONE unless the new Comparison #12170
sits at its position (reported, not judged), LoopTunnel uid set base-adopted {23501}, adopted-base {}; S1..S6 PASS; RESULT reports the count.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c164_a3_7_ident.log -- py -u tools/bench/prep_c164_a3_7_ident.py"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagexec as X  # noqa: E402
import protocol  # noqa: E402

B = os.path.dirname(os.path.abspath(__file__))
GB, GA = os.path.join(B, "graph_ring_p5s02c_20261010_131658.json"), os.path.join(B, "graph_ring_p5s02d_20261010_154830.json")
PL = json.load(open(os.path.join(B, "diag_c164_a3_5_graph_plan.json"), encoding="utf-8"))
ED = PL["edits"]
MADE = set(int(k) for k in ED["made"])
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


def load(p):
    g = json.load(open(p, encoding="utf-8"))
    return g, dict((int(o["uid"]), o) for o in g["objs"]), g["terminals"], g.get("owners") or {}


def ident(uid, objs, rows, owners):
    """(class, owner class, owner uid, pos) of object uid; owner uid = tunnel_owner for a tunnel, else the frame_diagram(s) of its rows."""
    o = objs.get(uid)
    if o is None:
        return None
    if str(o["class"]).endswith("Tunnel"):
        try:
            ou = X.tunnel_owner(rows, uid, owners)
        except Exception as e:  # noqa: BLE001
            ou = "?" + str(e)[:80]
    else:
        fd = sorted(set(int(r.get("frame_diagram") or 0) for r in rows if int(r.get("owner_uid") or 0) == uid))
        ou = fd[0] if len(fd) == 1 else tuple(fd)
    return (str(o["class"]), str(o["owner"]), ou, tuple(o["pos"]))


def matches(idb, objs, rows, owners):
    return sorted(u for u, o in objs.items() if str(o["class"]) == idb[0] and str(o["owner"]) == idb[1] and tuple(o["pos"]) == idb[3]
                  and ident(u, objs, rows, owners)[2] == idb[2])


def grep(path, pat):
    out = []
    for i, ln in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        if re.search(pat, ln):
            out.append((i, ln.rstrip()[:260]))
    return out


g0, O0, T0, W0 = load(GB)
g1, O1, T1, W1 = load(GA)
print("  FACT base {0} objs {1} rows {2}; adopted {3} objs {4} rows {5}".format(os.path.basename(GB), len(O0), len(T0), os.path.basename(GA), len(O1), len(T1)))
print("  FACT plan deleted_nodes {0} (diag_c164_a3_5_graph_plan.json:33-36); made {1}".format(ED["deleted_nodes"], sorted(MADE)))
gone = {}
for u in ED["deleted_nodes"]:
    ib = ident(u, O0, T0, W0)
    ia = ident(u, O1, T1, W1)
    rows_a = [dict((k, r.get(k)) for k in ("term_uid", "term_name", "owner_uid", "owner_class", "wire_uid", "term_class"))
              for r in T1 if int(r.get("owner_uid") or 0) == u or int(r.get("term_uid") or 0) == u]
    m = matches(ib, O1, T1, W1) if ib else []
    m_loose = sorted(v for v, o in O1.items() if ib and str(o["class"]) == ib[0] and tuple(o["pos"]) == ib[3])
    gone[u] = not m
    print("  IDENT #{0}: base (class, owner, owner_uid, pos) {1} | adopted at uid {2} rows {3} | adopted objects with base identity {4} "
          "(made among them {5}) | same class+pos any owner {6} | IDENTITY GONE {7}".format(
              u, ib, ia, rows_a, m, sorted(set(m) & MADE), m_loose, "yes" if not m else "no"), flush=True)
# re-used terminal uid 23481: base 'x' of #23042 -> adopted
for tu in (23481, 23501):
    rb = [(r["owner_uid"], r["owner_class"], r["term_name"], r["term_class"], r["wire_uid"]) for r in T0 if int(r.get("term_uid") or 0) == tu]
    ra = [(r["owner_uid"], r["owner_class"], r["term_name"], r["term_class"], r["wire_uid"]) for r in T1 if int(r.get("term_uid") or 0) == tu]
    pb, pa = O0.get(tu), O1.get(tu)
    owner_gone = all(not matches(ident(int(x[0]), O0, T0, W0), O1, T1, W1) for x in rb) if rb else None
    print("  REUSE term uid {0}: base rows {1} obj {2} | adopted rows {3} obj {4} | base owner identity gone {5}".format(
        tu, rb, pb and (pb["class"], pb["owner"], tuple(pb["pos"])), ra, pa and (pa["class"], pa["owner"], tuple(pa["pos"])), owner_gone), flush=True)
lt0 = set(u for u, o in O0.items() if o["class"] == "LoopTunnel")
lt1 = set(u for u, o in O1.items() if o["class"] == "LoopTunnel")
id0 = dict((u, ident(u, O0, T0, W0)) for u in lt0)
id1 = dict((u, ident(u, O1, T1, W1)) for u in lt1)
s0, s1 = set(id0.values()), set(id1.values())
print("  FACT LoopTunnel uid set: base {0} adopted {1}; base-adopted {2}; adopted-base {3}".format(len(lt0), len(lt1), sorted(lt0 - lt1), sorted(lt1 - lt0)))
print("  FACT LoopTunnel identity set: base-adopted {0}; adopted-base {1}".format(sorted(map(str, s0 - s1)), sorted(map(str, s1 - s0))))
gate("I1 every plan-deleted node IDENTITY GONE in the adopted graph (class, owner, owner uid, pos)", all(gone.values()), gone)
gate("I2 LoopTunnel identities base-adopted == {#23501's}, adopted-base empty", s0 - s1 == {id0.get(23501)} and not (s1 - s0), (len(s0 - s1), len(s1 - s0)))
# the structural condition, each line found by search
GL, EL, EX, RD = (os.path.join(B, f) for f in ("diag_c164_a3_5_graph.log", "diag_c164_a3_5_el.log", "diag_c164_a3_5_elexp.log", "diag_c164_a3_5_reads.log"))
for lab in ("G1", "G2", "G3", "FS1", "B", "X"):
    hit = grep(GL, r"^\s+(PASS|FAIL)\s+{0} ".format(re.escape(lab)))
    print("  QUOTE graph.log {0}".format(hit), flush=True)
    gate("S1 graph gate {0} PASS".format(lab), len(hit) == 1 and hit[0][1].strip().startswith("PASS"), hit[:1])
fails = [h for h in grep(GL, r"^\s+FAIL\s") if not re.search(r"\sE5 ", h[1])]
gate("S2 no graph gate other than E5 failed", not fails, fails)
el = grep(EL, r"^RESULT ") + grep(EL, r"^items 53 / window N 53 ; .* extra 0 ; missing 0")
ex = grep(EX, r"compare\(read, predicted 2c1edf78\): extra \[\] \| missing \[\]") + grep(EX, r"GATE PASS \| S predicted step-4 end md5 2c1edf78")
print("  QUOTE el.log {0}\n  QUOTE elexp.log {1}".format(el, ex), flush=True)
gate("S3 Error List 53 == window 53, RESULT PASS, == prediction 2c1edf78 (extra [] missing [])",
     len(el) == 2 and '"status":"PASS"' in el[0][1] and len(ex) == 2, (el, ex))
w460 = [r for r in T1 if int(r.get("wire_uid") or 0) == 23460]
w460o = 23460 in O1
gate("S4 w23460 absent in the adopted graph (0 rows, no object)", not w460 and not w460o, (len(w460), w460o))
w519 = [r for r in T1 if int(r.get("wire_uid") or 0) == 23519]
src = sorted(int(r["term_uid"]) for r in w519 if r.get("is_source"))
snk = sorted(int(r["term_uid"]) for r in w519 if not r.get("is_source"))
print("  FACT w23519 adopted: sources {0}, sinks {1}".format(src, snk))
gate("S5 w23519 source t8494, real sinks == prediction {t23450, t23241, t7606}", src == [8494] and snk == sorted([23450, 23241, 7606]), (src, snk))
hold = all(ok for _l, ok in gates)
print("  FACT STRUCTURAL CONDITION {0}".format("HOLDS" if hold else "DOES NOT HOLD"), flush=True)
n = sum(1 for _l, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, [])), flush=True)
sys.exit(0 if ff is None else 1)
