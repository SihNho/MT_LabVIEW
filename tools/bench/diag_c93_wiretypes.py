"""diag_c93_wiretypes.py - card 93-1 part B, OFFLINE: the input wire of each of the 12 stamp CLFNs in the t0at copy.

Found before writing: no op reads a terminal's data type. `Terminal.Data Type` 634A008 resolves (docs/NAMES.md:470-474)
but its VALUE needs a new op wired to a Terminal ref (docs/NAMES.md:478-485); claudeDev has OpCLFNThread_v0 (thread
flag) and OpNodeTerms_v0 (Name/IsSource/WireUID only), nothing for types. Card 93-1 flags forbid building one
(labview read, no claudeDev write). So this script does what is measurable offline and marks the type column UNREAD.

Sources: CLFN uid <-> wire uid from the step-3c build record (tools/bench/t0_sites_s1_step3c_r2.json ops, the
connect_from_wire read-backs `UID 2`); source node/terminal from the S1 offline graph (docs/wiki/subvi/D1_s1_copy.json
`wires`). t0at is a byte copy of t0 + 12 AnyThread flags (plan PD199(a)), so the wire uids carry over.

PREDICTION: 12 rows; every wire uid found in the S1 graph with one source; t0at md5 30a15c67...; type-reader gate
FAILS (no reader) -> the table's type column is `declared` (build tag) + `terminal_expectation` (vendor terminal name),
level INFERRED, never READ.
"""
import hashlib, json, os, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import protocol  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
BUILD = os.path.join(ROOT, "tools", "bench", "t0_sites_s1_step3c_r2.json")
GRAPH = os.path.join(ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json")
T0AT = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_t0at_20260926_090833.vi"
T0AT_MD5 = "30a15c6772d5ef3336ed274abc4c2f40"
OUT = os.path.join(ROOT, "tools", "bench", "t0at_stamp_wiretypes_93.json")

# vendor-terminal expectation, INFERRED from the source terminal's identity, not read from LabVIEW
EXPECT = {
    "i": "I32 scalar (loop iteration terminal)",
    "Bead is good? array out": "1D Boolean array (n beads)",
    "Image Pixels (U8)": "2D U8 array (full frame; IMAQ ImageToArray)",
    "image data": "cluster (NI picture 'image data': image type, depth, 1D U8 image, 1D U32 colors, rect)",
    "new picture": "picture (flattened-string type, grows with drawn content)",
    "error out": "error cluster (status, code, source string)",
}

gates, facts = [], []
def gate(name, ok, detail=""):
    gates.append((name, bool(ok), detail)); print(("PASS  " if ok else "FAIL  ") + name + "  " + str(detail), flush=True)

build = json.load(open(BUILD, encoding="utf-8"))
graph = json.load(open(GRAPH, encoding="utf-8"))
wires = {}
for w in graph["wires"]:
    wires.setdefault(w["wire_uid"], []).append(w)

tags = [re.match(r"after (S\d\d) \[(.*)\]", e["tag"]) for e in build["es_timeline"]]
tags = [(m.group(1), m.group(2)) for m in tags if m]
ops = build["ops"]
rows, k = [], 0
for i, op in enumerate(ops):
    if op["verb"] != "move_in":
        continue
    clfn = int(op["detail"].split()[0].lstrip("#"))
    conn = ops[i + 1]
    m = re.search(r"sink D\[(\d+)\]\.N\[(\d+)\]\.t(\d+) <- w(\d+)", conn["detail"])
    wuid = int(m.group(4)); rb = conn["result"][3]
    recs = wires.get(wuid, [])
    srcs = sorted({(r["src_uid"], r["src_class"], r["src_term"]) for r in recs})
    sinks = sorted({(r["sink_uid"], r["sink_class"], r["sink_term"]) for r in recs})
    site, decl = tags[k] if k < len(tags) else ("?", "?"); k += 1
    term = srcs[0][2] if srcs else None
    exp = EXPECT.get(term) or ("I32 scalar (loop iteration terminal)" if decl.startswith("i I32") else None)
    rows.append({"clfn_uid": clfn, "site": site, "clfn_diagram_index": int(m.group(1)), "clfn_terminal": rb.get("Name"),
                 "wire_uid": wuid, "wire_readback_uid": rb.get("UID 2"), "wire_broken_at_build": rb.get("Is Broken?"),
                 "sources": [{"uid": s[0], "class": s[1], "terminal": s[2]} for s in srcs],
                 "other_sinks_in_S1": [{"uid": s[0], "class": s[1], "terminal": s[2]} for s in sinks],
                 "type_declared_by_build": decl, "type_terminal_expectation": exp,
                 "type_level": "INFERRED - no Terminal.Data Type reader op exists (docs/NAMES.md:478-485)"})

gate("G1 12 stamp CLFN rows", len(rows) == 12, len(rows))
gate("G2 every wire uid found in the S1 graph with exactly one source",
     all(len(r["sources"]) == 1 for r in rows), [r["wire_uid"] for r in rows if len(r["sources"]) != 1])
gate("G3 build read-back uid == wire uid, not broken, sink terminal 'any'",
     all(r["wire_readback_uid"] == r["wire_uid"] and r["wire_broken_at_build"] is False and r["clfn_terminal"] == "any"
         for r in rows))
md5 = hashlib.md5(open(T0AT, "rb").read()).hexdigest()
gate("G4 t0at md5 unchanged", md5 == T0AT_MD5, md5)
gate("G5 type reader verified on a known-type wire (loop i = I32)", False,
     "no reader: Terminal.Data Type 634A008 value needs a new op (docs/NAMES.md:478-485); card flags labview=read, no claudeDev write")

out = {"schema": "t0at-stamp-wiretypes/1", "card": "93-1", "vi": T0AT, "vi_md5": md5, "labview_launched": False,
       "sources": [os.path.relpath(BUILD, ROOT), os.path.relpath(GRAPH, ROOT)], "rows": rows,
       "gates": {g[0]: g[1] for g in gates}}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
for r in rows:
    s = r["sources"][0] if r["sources"] else {}
    print("%s clfn#%d w%d <- %s#%s '%s' | declared [%s] | expect %s" % (r["site"], r["clfn_uid"], r["wire_uid"],
          s.get("class"), s.get("uid"), s.get("terminal"), r["type_declared_by_build"], r["type_terminal_expectation"]))
npass = sum(g[1] for g in gates); nfail = len(gates) - npass
first = next((g[0] for g in gates if not g[1]), None)
md5o = hashlib.md5(open(OUT, "rb").read()).hexdigest()
print(protocol.result_line({"status": "PASS" if nfail == 0 else "FAIL", "gates": {"pass": npass, "fail": nfail},
                            "first_fail": first, "artefacts": [{"path": os.path.relpath(OUT, ROOT), "md5": md5o}]}))
