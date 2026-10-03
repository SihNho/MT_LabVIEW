r"""prep_c142_p1_table - card 142-P1 pass 1 (OFFLINE, no LabVIEW, no COM). Decomposition table of plan v17's NON-repair actions
(id not starting 'p4_rp', 185 of 235) into groups of connected PURE computation vs bed glue, for the user's 2026-10-03 subVI
re-plan (docs/d1/ring-p4b.md:94-103). Facts only; the subVI list is decided by judgement.
Existing tools checked: stagexec.compile_plan (groups actions into LabVIEW ops, not into computations), stagesim (graph replay),
prep_c141_p1_mk.py (v17 maker) - none groups a plan by data-flow; this is a read-only analysis of the plan's own fields.
METHOD (from the plan's wires only, nothing re-designed):
  node = every created object (`as`) + every bed node moved in (move_in -> 'bed:<uid>').
  GLUE node classes: Local, ControlTerminal, WhileLoop, FlatSequence, prim 'Wait (ms)' and a constant created `on` it; shift
  registers (add_shift_reg; SxxL/SxxR) and tunnels of #10170 or of the plan-made While W1 are glue endpoints. Tunnels of a
  plan-made For loop belong to that For loop (its group). Every other created node is COMPUTE.
  A wire joins two compute nodes into one group when both sit on the same diagram (or it passes a For-loop tunnel); a wire
  from a compute node on one diagram to one on another crosses a structure border -> boundary LINK (groups stay apart).
  Any other wire touching a group is that group's external INPUT / OUTPUT; a wire touching no compute node is glue.
  A constant group of one node whose only wires go to glue (SR init) or that only donates an indicator (born_on) is glue.
  RLE `of` actions follow their wire's category; delete_wire / delete_object / bed-to-bed wires are glue.
PREDICTION CONTRACT: M0 v17 md5 e19d7e14 + graph md5 f697a0b2; C every one of the 185 non-repair actions classified exactly
  once (group | boundary | glue); B 142-1's set {GT1 FMN1 SW1 KMX1 KMX2 AMM1 LT1} lies inside ONE group; every wire across
  that set's boundary is listed (named in brief_142-1 or not); W outputs written (.json + .md).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c142_p1_table.log -- py -u tools/bench/prep_c142_p1_table.py"""
import collections, hashlib, json, os, re, sys                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
V17, GR = os.path.join(B, "plan_ring_p4_v17.json"), os.path.join(B, "graph_ring_p4s01_20261002_234419.json")
OJ, OM = os.path.join(B, "prep_c142_p1_subvi_table.json"), os.path.join(B, "prep_c142_p1_subvi_table.md")
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                                 # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                    # noqa: E731


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and G["first"] is None:
        G["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)
    return ok


def done():
    print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
    sys.exit(0 if not G["fail"] else 1)


gate("M0 input md5 (v17, s01 graph)", md5(V17) == "e19d7e142fef66f9e118ae4061e9e718" and md5(GR) == "f697a0b21c3bdb481207318812a0adad")
if G["fail"]:
    done()
v17, gr = json.load(open(V17, encoding="utf-8")), json.load(open(GR, encoding="utf-8"))
ALL = v17["actions"]
A = [a for a in ALL if not a["id"].startswith("p4_rp")]
pos = dict((a["id"], n) for n, a in enumerate(ALL, 1))
TROW = dict((r["term_uid"], r) for r in gr["terminals"])
OBJ = dict((o["uid"], o) for o in gr["objs"] if isinstance(o, dict))
OWN = collections.defaultdict(list)
for r in gr["terminals"]:
    OWN[r["owner_uid"]].append(r)
TYPE_RE = re.compile(r"\b(I32|U32|I16|U16|DBL|SGL|Boolean|1-D|2-D|refnum|IMAQ)\b")
GLUE_CLASS = {"Local": "local", "ControlTerminal": "panel terminal", "WhileLoop": "plan-made While (W1)", "FlatSequence": "Flat Sequence"}
# ---------------------------------------------------------------- nodes
NODE = collections.OrderedDict()      # key -> {kind, aid, class, prim, diagram, glue}
SR, TUN = {}, {}
for a in A:
    if a["op"] == "create":
        k = a["as"]
        glue = GLUE_CLASS.get(a["class"])
        if a.get("prim") == "Wait (ms)":
            glue = "wait"
        NODE[k] = {"aid": a["id"], "class": a["class"], "prim": a.get("prim") or a.get("label") or "", "diagram": a.get("diagram"), "glue": glue,
                   "label": a.get("label"), "on": a.get("on"), "born_on": (a.get("born_on") or {}).get("uid")}
    elif a["op"] == "add_shift_reg":
        SR[a["as"]] = a
    elif a["op"] == "tunnel":
        TUN[a["as"]] = a
    elif a["op"] == "move_in":
        for u in a["nodes"]:
            o = OBJ.get(u, {})
            NODE["bed:{0}".format(u)] = {"aid": a["id"], "class": o.get("class", "?"), "prim": "bed #{0} (moved in)".format(u),
                                        "diagram": a["dest_diagram"], "glue": None, "label": None, "on": None, "born_on": None}
for k, n in NODE.items():                                              # a constant created ON a glue node is glue (WK2 on WT2)
    on = n.get("on")
    if isinstance(on, str) and on.startswith("new:") and NODE.get(on[4:].split(".")[0], {}).get("glue"):
        n["glue"] = "constant on " + NODE[on[4:].split(".")[0]]["glue"]
MOVED = set(int(k[4:]) for k in NODE if k.startswith("bed:"))


def loop_sym(t):
    lp = t.get("loop")
    return lp[4:] if isinstance(lp, str) and lp.startswith("new:") else lp


def resolve(e):
    """endpoint -> (key, glue-kind or None, diagram, text)."""
    if isinstance(e, str) and e.startswith("new:"):
        sym, term = (e[4:].split(".", 1) + [""])[:2]
        if sym in NODE:
            n = NODE[sym]
            return sym, n["glue"], n["diagram"], "{0}.{1}".format(sym, term)
        if sym[:-1] in SR and sym[-1] in "LR":
            return "SR:" + sym[:-1], "shift register (#10170)", None, "{0}.{1}".format(sym, term)
        if sym in TUN:
            t = TUN[sym]
            ls = loop_sym(t)
            if isinstance(ls, str) and NODE.get(ls, {}).get("class") == "ForLoop":
                return ls, None, NODE[ls]["diagram"], "{0}.{1} (For tunnel)".format(sym, term)
            return "TUN:" + sym, "tunnel of {0}".format("W1" if ls == "W1" else "#{0}".format(ls)), None, "{0}.{1}".format(sym, term)
        if sym == "W1":
            return "W1", "stop/conditional terminal (W1)", None, e[4:]
        return "?" + sym, "unknown", None, e[4:]
    if isinstance(e, dict):
        u = e.get("uid")
        if isinstance(u, str) and u.startswith("new:"):
            return resolve(u)
        if u in MOVED:
            k = "bed:{0}".format(u)
            return k, None, NODE[k]["diagram"], "#{0}.{1}".format(u, e.get("term") or e.get("term_uid"))
        r = TROW.get(e.get("term_uid")) if e.get("term_uid") else next((x for x in OWN.get(u, []) if x["term_name"] == e.get("term")), None)
        o = OBJ.get(u, {})
        nm = (r or {}).get("term_name", e.get("term", ""))
        kind = "bed {0}".format(o.get("class", "?"))
        if u == 10170:
            kind = "stop/conditional terminal (#10170)"
        return "BED:{0}".format(u), kind, (r or {}).get("frame_diagram"), "#{0} {1} t{2} {3!r}".format(u, o.get("class", "?"), e.get("term_uid", "-"), nm)
    return "?", "unknown", None, str(e)


# ---------------------------------------------------------------- union-find over compute nodes
par = dict((k, k) for k, n in NODE.items() if not n["glue"])


def find(x):
    while par[x] != x:
        par[x] = par[par[x]]
        x = par[x]
    return x


WIRES, LINKS = [], []
for a in A:
    if a["op"] != "wire":
        continue
    s, d = resolve(a["src"]), resolve(a["dst"])
    w = {"aid": a["id"], "n": pos[a["id"]], "src": s, "dst": d, "types": TYPE_RE.findall(a.get("why", ""))}
    WIRES.append(w)
    sc, dc = s[0] in par, d[0] in par
    if sc and dc:
        ft = "For tunnel" in s[3] or "For tunnel" in d[3]
        if s[2] == d[2] or ft:
            par[find(s[0])] = find(d[0])
            w["cat"] = "internal"
        else:
            w["cat"] = "link"
            LINKS.append(w)
    elif sc or dc:
        w["cat"] = "output" if sc else "input"
    else:
        w["cat"] = "glue"
for a in A:                                       # For loop body nodes join their For loop (diagram 'new:FMN1.body')
    pass
for k, n in NODE.items():
    dg = n["diagram"]
    if k in par and isinstance(dg, str) and dg.startswith("new:") and dg[4:].split(".")[0] in par:
        par[find(k)] = find(dg[4:].split(".")[0])
groups = collections.defaultdict(list)
for k in par:
    groups[find(k)].append(k)
# single-constant groups that only feed glue / only donate an indicator -> glue
donors = set(n["born_on"][4:] for n in NODE.values() if isinstance(n.get("born_on"), str) and n["born_on"].startswith("new:"))
for r, mem in list(groups.items()):
    if len(mem) == 1 and "Constant" in NODE[mem[0]]["class"]:
        ws = [w for w in WIRES if mem[0] in (w["src"][0], w["dst"][0])]
        if mem[0] in donors and not ws:
            NODE[mem[0]]["glue"] = "indicator donor constant (born_on)"
        elif ws and all(w["cat"] in ("output", "input") for w in ws):
            NODE[mem[0]]["glue"] = "init constant -> " + ", ".join(sorted(set((w["dst"][1] or "") for w in ws)))
        else:
            continue
        del groups[r]
        del par[mem[0]]
        for w in ws:
            w["cat"] = "glue"
gid = {}
order = sorted(groups, key=lambda r: min(pos[NODE[k]["aid"]] for k in groups[r]))
for i, r in enumerate(order, 1):
    for k in groups[r]:
        gid[k] = "G{0}".format(i)
# ---------------------------------------------------------------- classify every action
CAT = collections.OrderedDict()
wire_of = dict((w["aid"], w) for w in WIRES)
for a in A:
    op, i = a["op"], a["id"]
    if op == "create" or op == "move_in":
        ks = [a["as"]] if op == "create" else ["bed:{0}".format(u) for u in a["nodes"]]
        g = gid.get(ks[0])
        CAT[i] = ("group", g) if g else ("glue", NODE[ks[0]]["glue"] or "?")
    elif op == "wire":
        w = wire_of[i]
        if w["cat"] == "internal":
            CAT[i] = ("group", gid[w["src"][0]])
        elif w["cat"] in ("input", "output"):
            g = gid.get(w["dst"][0] if w["cat"] == "input" else w["src"][0])
            CAT[i] = ("boundary", g) if g else ("glue", "wire " + w["cat"])
        elif w["cat"] == "link":
            CAT[i] = ("boundary", "{0}->{1}".format(gid[w["src"][0]], gid[w["dst"][0]]))
        else:
            CAT[i] = ("glue", "bed-to-bed / glue-to-glue wire")
    elif op == "wire_remove_loose_ends" and a.get("of"):
        c = CAT.get(a["of"], ("glue", "?"))
        CAT[i] = (c[0], c[1]) if c[0] != "group" else ("group", c[1])
    elif op == "add_shift_reg":
        CAT[i] = ("glue", "shift register")
    elif op == "tunnel":
        ls = loop_sym(a)
        CAT[i] = ("group", gid[ls]) if ls in gid else ("glue", "tunnel of {0}".format("W1" if ls == "W1" else "#{0}".format(ls)))
    elif op in ("delete_wire", "delete_object"):
        CAT[i] = ("glue", op)
    else:
        CAT[i] = ("glue", op)
gate("C every non-repair action classified once: {0} actions, {1} classified".format(len(A), len(CAT)), len(CAT) == len(A) == 185
     and all(c[1] for c in CAT.values()), [i for i, c in CAT.items() if not c[1]][:6])
# ---------------------------------------------------------------- per-group facts
OUT = {"card": "142-P1", "plan": {"path": rel(V17), "md5": md5(V17)}, "graph": {"path": rel(GR), "md5": md5(GR)}, "groups": [], "glue": [],
       "links": [], "counts": {}}
SET1 = {"GT1", "FMN1", "SW1", "KMX1", "KMX2", "AMM1", "LT1"}
for r in order:
    g = gid[groups[r][0]]
    mem = groups[r]
    acts = [i for i, c in CAT.items() if c == ("group", g)]
    ins = [w for w in WIRES if w["cat"] == "input" and gid.get(w["dst"][0]) == g]
    outs = [w for w in WIRES if w["cat"] == "output" and gid.get(w["src"][0]) == g]
    lk = [w for w in LINKS if g in (gid[w["src"][0]], gid[w["dst"][0]])]
    rle = [i for i, c in CAT.items() if c == ("boundary", g) and i not in wire_of]
    dgs = sorted(set(str(NODE[k]["diagram"]) for k in mem))
    flags = sorted(set(["Flat Sequence frame (node inside FS4.f0)" for k in mem if str(NODE[k]["diagram"]).startswith("new:FS")]
                       + ["IMAQ/refnum passes through" for w in ins + outs if "Image" in w["src"][3] + w["dst"][3] or "TP1" in w["src"][3]]
                       + ["border-crossing wire (RLE)" for _ in rle]))
    rec = {"group": g, "pure": not flags, "flags": flags, "diagrams": dgs,
           "nodes": [{"key": k, "action": NODE[k]["aid"], "class": NODE[k]["class"], "prim": NODE[k]["prim"]} for k in mem],
           "actions": acts, "n_actions": len(acts),
           "inputs": [{"wire": w["aid"], "from": w["src"][3], "from_kind": w["src"][1] or "compute", "to": w["dst"][3], "types": w["types"]} for w in ins],
           "outputs": [{"wire": w["aid"], "from": w["src"][3], "to": w["dst"][3], "to_kind": w["dst"][1] or "compute", "types": w["types"]} for w in outs],
           "links": [{"wire": w["aid"], "from": w["src"][3], "to": w["dst"][3]} for w in lk], "boundary_rle": rle}
    OUT["groups"].append(rec)
    print("GROUP {0} pure={1} flags={2} diagrams={3} actions={4} nodes={5}".format(g, rec["pure"], flags, dgs, len(acts),
          ["{0}:{1}".format(k, NODE[k]["prim"]) for k in mem]), flush=True)
    for w in ins:
        print("   IN  {0}: {1} [{2}] -> {3} types{4}".format(w["aid"], w["src"][3], w["src"][1] or "compute", w["dst"][3], w["types"]))
    for w in outs:
        print("   OUT {0}: {1} -> {2} [{3}] types{4}".format(w["aid"], w["src"][3], w["dst"][3], w["dst"][1] or "compute", w["types"]))
    for w in lk:
        print("   LINK {0}: {1} -> {2}".format(w["aid"], w["src"][3], w["dst"][3]))
glue = [(i, c[1]) for i, c in CAT.items() if c[0] == "glue"]
bnd = [(i, c[1]) for i, c in CAT.items() if c[0] == "boundary"]
OUT["glue"] = [{"action": i, "kind": k} for i, k in glue]
OUT["boundary"] = [{"action": i, "group": k} for i, k in bnd]
OUT["links"] = [{"wire": w["aid"], "from": w["src"][3], "to": w["dst"][3]} for w in LINKS]
gk = collections.Counter(k for _, k in glue)
OUT["counts"] = {"non_repair": len(A), "in_groups": sum(r["n_actions"] for r in OUT["groups"]),
                 "in_pure_groups": sum(r["n_actions"] for r in OUT["groups"] if r["pure"]), "boundary_wires_rle": len(bnd), "glue": len(glue),
                 "groups": len(OUT["groups"]), "pure_groups": sum(1 for r in OUT["groups"] if r["pure"]), "glue_kinds": dict(gk)}
print("COUNTS", json.dumps(OUT["counts"]), flush=True)
# ---------------------------------------------------------------- 142-1 boundary check
g1 = set(gid.get(k) for k in SET1)
gate("B 142-1 set {0} lies in ONE group: {1}".format(sorted(SET1), sorted(g1, key=str)), len(g1) == 1 and None not in g1)
cross = []
for w in WIRES:
    si, di = w["src"][0] in SET1, w["dst"][0] in SET1
    if si != di:
        cross.append({"wire": w["aid"], "dir": "out" if si else "in", "from": w["src"][3], "to": w["dst"][3], "other_kind": (w["dst"] if si else w["src"])[1] or "compute"})
NAMED = {"in": {"p4_w_num_gt", "p4_t_fnum_in", "p4_t_last_out"}, "out": {"p4_t_n1_in", "p4_t_slot_in", "p4_w_lt_or"}}
for c in cross:
    c["named_in_142_1"] = c["wire"] in NAMED[c["dir"]]
    print("SET1 {0} {1}: {2} -> {3} [{4}] named={5}".format(c["dir"].upper(), c["wire"], c["from"], c["to"], c["other_kind"], c["named_in_142_1"]))
extra = sorted(set(k for k in groups[next(r for r in order if gid[groups[r][0]] in g1)] if k not in SET1)) if len(g1) == 1 and None not in g1 else []
OUT["set_142_1"] = {"members": sorted(SET1), "group": sorted(g1, key=str), "group_extra_members": extra, "cross_wires": cross,
                    "unnamed": [c for c in cross if not c["named_in_142_1"]]}
gate("B2 every wire across 142-1's set listed: {0} cross wires, {1} not named in brief_142-1; group extra members {2}".format(
     len(cross), len(OUT["set_142_1"]["unnamed"]), extra), bool(cross))
# ---------------------------------------------------------------- write
json.dump(OUT, open(OJ, "w", encoding="utf-8"), indent=1)
L = ["---", "type: facts", "status: current", "date: 2026-10-03", "---",
     "# Card 142-P1 (1): plan v17 non-repair actions grouped by connected computation (facts; judgement picks the subVIs)",
     "Source `{0}` {1}, graph `{2}`; maker `tools/bench/prep_c142_p1_table.py` -> `prep_c142_p1_table.log`; data `prep_c142_p1_subvi_table.json`.".format(
         rel(V17), md5(V17)[:8], rel(GR)),
     "Method: compute nodes joined by same-diagram wires (For-loop tunnels inside); a wire crossing a structure border is a LINK; locals, "
     "shift registers, W1/#10170 tunnels and stop terminals, FS, Wait, panel terminals = bed glue. PURE = no FS-frame node, no IMAQ/refnum, "
     "no border-crossing wire. Types: only where the plan's `why` states one (graph has no type field).", "",
     "## Counts", "", "| item | n |", "|---|---|"] + ["| {0} | {1} |".format(k, v) for k, v in OUT["counts"].items() if k != "glue_kinds"] + [
     "| glue kinds | {0} |".format("; ".join("{0} {1}".format(k, v) for k, v in sorted(gk.items()))), "", "## Groups", ""]
for r in OUT["groups"]:
    L.append("### {0} - {1} actions - {2}{3}".format(r["group"], r["n_actions"], "PURE" if r["pure"] else "NOT pure: " + "; ".join(r["flags"]),
                                                    " - diagrams " + ", ".join(r["diagrams"])))
    L.append("- nodes: " + ", ".join("`{0}` {1} ({2})".format(n["action"], n["prim"], n["class"]) for n in r["nodes"]))
    L.append("- actions: " + ", ".join(r["actions"]))
    for x in r["inputs"]:
        L.append("- IN `{0}`: {1} [{2}] -> {3}{4}".format(x["wire"], x["from"], x["from_kind"], x["to"], " type " + "/".join(x["types"]) if x["types"] else ""))
    for x in r["outputs"]:
        L.append("- OUT `{0}`: {1} -> {2} [{3}]{4}".format(x["wire"], x["from"], x["to"], x["to_kind"], " type " + "/".join(x["types"]) if x["types"] else ""))
    for x in r["links"]:
        L.append("- LINK `{0}`: {1} -> {2}".format(x["wire"], x["from"], x["to"]))
    L.append("")
L += ["## 142-1's group (RingPickSlot_v0)", "", "Members {0} -> group {1}; other members of that group: {2}.".format(
      sorted(SET1), OUT["set_142_1"]["group"], extra or "none"), "", "| dir | wire | from | to | other side | named in brief_142-1 |", "|---|---|---|---|---|---|"]
L += ["| {dir} | `{wire}` | {from} | {to} | {other_kind} | {named_in_142_1} |".format(**c) for c in cross]
L += ["", "## Bed glue actions", "", "| action | kind |", "|---|---|"] + ["| `{0}` | {1} |".format(i, k) for i, k in glue]
L += ["", "## Boundary wires (bed wires to a group's terminals, after subVI conversion)", "", "| action | group |", "|---|---|"] + [
      "| `{0}` | {1} |".format(i, k) for i, k in bnd]
open(OM, "w", encoding="utf-8").write("\n".join(L) + "\n")
ARTS.extend({"path": rel(p), "md5": md5(p)} for p in (OJ, OM))
gate("W outputs written", os.path.isfile(OJ) and os.path.isfile(OM))
done()
