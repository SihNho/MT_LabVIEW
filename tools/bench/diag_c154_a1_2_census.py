# ---
# labview: none
# hardware: none
# ---
"""Card 154-a1-2 (PD374(g), docs/d1/ring-p5.md:71-74): offline consumer census of the frame counter.
Reads STORED json only (no LabVIEW, no VI opened): S1 graph docs/wiki/subvi/D1_s1_copy.json (S1 = byte copy of the
original, 3e3d23ce) and s09 graph tools/bench/graph_ring_p4s09_20261009_062044.json (22f967b5).
Prior art: diag_c153_a1_1_census{,2,3,4}.py (same s09 json, one-hop rows), diag_c153_a2_6_orig_read (8 sinks on the
CURRENT original, live read). This script adds: per-sink full terminal list + downstream walk through tunnels /
structure borders (<= 4 hops), the owner chain to the enclosing While loop, subVI names, and every 'FrameIdx' local.
Prediction contract:
  P1 S1 w3268 has exactly 8 sink rows, owners {376,1114,2136,2213,3045,10068,12195,29240}; source term 644 on Diagram 639
  P2 s09 w29454 has 6 sink owners {29440,12195,1114,3045,2136,2213} (p5_facts.md:19)
  P3 s09 #30240 element w30278 sinks {29240,10068}; #6859 output -> FrameIdx local write (census3.log:16)
  P4 md5 of pinned inputs unchanged before == after
Output: tools/bench/diag_c154_a1_2_census.json + log lines; ends with a RESULT line."""
import json, hashlib, sys
from pathlib import Path
from collections import defaultdict
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import protocol

PINS = {"docs/d1/ring-p5.md": "58f168cb38ff033273b699e8f68303c6",
        "tools/bench/graph_ring_p4s09_20261009_062044.json": "22f967b513726a01c9d8f63269f689e6",
        "tools/bench/p5_facts.md": "1df5c37d7e214af604bcd079df218912",
        "tools/bench/cards/brief_154-a1-2.md": "0a16d9d67752f25363bdae839703d22c"}
VI_S09 = Path(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p4s09_20261009_060515.vi")
TOOLS = ["tools/stagekit.py", "tools/stagexec.py", "tools/stagesim.py", "tools/vigraph.py", "tools/stage_prerun.py",
         "tools/gscript.py"]
gates = []


def md5(p):
    return hashlib.md5(Path(p).read_bytes()).hexdigest()


def snap():
    d = {k: md5(ROOT / k) for k in list(PINS) + TOOLS}
    d["s09_vi"] = md5(VI_S09) if VI_S09.exists() else "absent"
    return d


def gate(name, ok, val=""):
    gates.append((name, bool(ok)))
    print(f"  {'PASS' if ok else 'FAIL'}  {name}  {val}")


before = snap()
for k, v in PINS.items():
    gate(f"PIN {k}", before[k] == v, before[k])
print("  FACT tool md5s before", json.dumps({k: before[k][:8] for k in TOOLS + ['s09_vi']}))

s1 = json.loads((ROOT / "docs/wiki/subvi/D1_s1_copy.json").read_text(encoding="utf-8"))
s9 = json.loads((ROOT / "tools/bench/graph_ring_p4s09_20261009_062044.json").read_text(encoding="utf-8"))
subvi = {c["node_uid"]: c["subvi_name"] for c in s1["graph_summary"]["subvi_calls"]}
owners9 = {int(k): v for k, v in s9["owners"].items()}
cls9 = {o["uid"]: o["class"] for o in s9["objs"]}
LOOPNAME = {637: "1.1 frame loop #637"}
for L in s9["loops"]:
    LOOPNAME.setdefault(L["loop_uid"], f"{L['class']} #{L['loop_uid']} (index {L['index']})")


def index(g):
    by_w, by_o = defaultdict(list), defaultdict(list)
    for t in g["terminals"]:
        by_w[t["wire_uid"]].append(t)
        by_o[t["owner_uid"]].append(t)
    return by_w, by_o


IDX = {"S1": index(s1), "s09": index(s9)}


def chain(diag):
    """owner chain of a diagram uid in the s09 owners map (S1 json carries no owner table)."""
    out, cur, seen = [], diag, set()
    while cur in owners9 and cur not in seen:
        seen.add(cur)
        c, u = owners9[cur]
        out.append(f"{c}#{u}")
        cur = u
    return out


def loop_of(diag):
    ch = chain(diag)
    loops = [x for x in ch if x.startswith(("WhileLoop", "ForLoop"))]
    return loops


def node_desc(sysname, uid, cls):
    n = subvi.get(uid)
    return f"#{uid} {cls}" + (f" '{n}'" if n else "")


def dump_node(sysname, uid, depth=0, seen=None, maxd=4):
    by_w, by_o = IDX[sysname]
    seen = seen if seen is not None else set()
    if uid in seen or depth > maxd:
        return
    seen.add(uid)
    rows = by_o.get(uid, [])
    cls = rows[0]["owner_class"] if rows else cls9.get(uid, "?")
    pad = "    " * depth
    diags = sorted({r["frame_diagram"] for r in rows})
    print(f"{pad}NODE[{sysname}] {node_desc(sysname, uid, cls)} diagrams {diags} loops {[loop_of(d) for d in diags]}")
    uniq = {}
    for r in rows:
        uniq[(r["term_uid"], r["wire_uid"])] = r
    for r in uniq.values():
        sinks = [s for s in by_w.get(r["wire_uid"], []) if s["owner_uid"] != uid] if r["wire_uid"] else []
        sink_s = sorted({(s["owner_uid"], s["owner_class"], s["term_name"], s["is_source"], s["frame_diagram"]) for s in sinks})
        print(f"{pad}  t{r['term_uid']} '{r['term_name']}' src={r['is_source']} w{r['wire_uid']} d{r['frame_diagram']} -> {sink_s}")
        follow = r["is_source"] or "Tunnel" in cls or cls in ("Diagram",)
        if follow and r["wire_uid"]:
            for s in sinks:
                if not s["is_source"]:
                    dump_node(sysname, s["owner_uid"], depth + 1, seen, maxd)


out = {}
# ---- S1 (original) w3268
by_w, by_o = IDX["S1"]
w = by_w[3268]
srcs = sorted({(t["term_uid"], t["owner_uid"], t["owner_class"]) for t in w if t["is_source"]})
sinks = sorted({t["owner_uid"] for t in w if not t["is_source"]})
print("FACT S1 w3268 sources", srcs, "sink owners", sinks, "sink rows", len([t for t in w if not t["is_source"]]))
gate("P1 S1 w3268 8 sink owners", set(sinks) == {376, 1114, 2136, 2213, 3045, 10068, 12195, 29240}, sinks)
out["S1_w3268"] = {"sources": srcs, "sinks": sinks}
print("== S1 walk from each w3268 sink")
for u in sinks:
    dump_node("S1", u, 0, set([639]))
# ---- s09
by_w9, by_o9 = IDX["s09"]
w = by_w9[29454]
sinks9 = sorted({t["owner_uid"] for t in w if not t["is_source"]})
print("FACT s09 w29454 sources", sorted({(t["term_uid"], t["owner_uid"]) for t in w if t["is_source"]}), "sink owners", sinks9)
gate("P2 s09 w29454 6 sink owners", set(sinks9) == {29440, 12195, 1114, 3045, 2136, 2213}, sinks9)
print("FACT s09 w3268 rows", len(by_w9.get(3268, [])))
print("FACT s09 #644 rows", sorted({(t["term_uid"], t["wire_uid"], t["is_source"]) for t in by_o9.get(639, []) if t["term_uid"] == 644}))
print("== s09 walk from each w29454 sink")
for u in sinks9:
    dump_node("s09", u, 0, set([639]))
print("== s09 FrameIdx locals")
fl = sorted({(t["owner_uid"], t["owner_class"], t["is_source"], t["wire_uid"], t["frame_diagram"]) for t in s9["terminals"]
             if t["term_name"] == "FrameIdx"})
print("FACT FrameIdx terminals", fl)
for (u, c, s, wi, d) in fl:
    print(f"  local #{u} {'READ' if s else 'WRITE'} d{d} loops {loop_of(d)}")
    dump_node("s09", u, 0, set(), 3)
print("== s09 #6859 / #30240 / #10068 / #29240 / #2136")
for u in (6859, 30240, 10068, 29240, 2136):
    dump_node("s09", u, 0, set(), 2)
el = [t for t in by_w9.get(30278, []) if not t["is_source"]]
gate("P3 s09 w30278 sinks {29240,10068}", {t["owner_uid"] for t in el} == {29240, 10068}, sorted({t["owner_uid"] for t in el}))
print("== S1 same uids for pairing: 10068 / 29240 / 2136 in S1")
for u in (10068, 29240, 2136):
    dump_node("S1", u, 0, set(), 2)
print("FACT loop chains", {u: chain(u) for u in (639, 23166, 32464, 27219, 23405)})
after = snap()
gate("P4 pinned md5s before == after", after == before)
outp = ROOT / "tools/bench/diag_c154_a1_2_census.json"
out["md5_before"] = before
out["md5_after"] = after
outp.write_text(json.dumps(out, indent=1), encoding="utf-8")
npass = sum(1 for _, ok in gates if ok)
nfail = len(gates) - npass
ff = next((n for n, ok in gates if not ok), None)
print(protocol.result_line({"status": "PASS" if nfail == 0 else "FAIL", "gates": {"pass": npass, "fail": nfail},
                            "first_fail": ff, "artefacts": [{"path": "tools/bench/diag_c154_a1_2_census.json",
                                                             "md5": md5(outp)}]}))
