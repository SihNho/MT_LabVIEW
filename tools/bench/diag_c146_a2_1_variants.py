# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a2_1_variants - card 146-a3-1 (OFFLINE, read-only, NO edit of tools/elrule.py): what each candidate `carry` for the
s05 session gives, per class, against the READ s04 -> s05 per-class change (06a59001 vs 5e53096a). Uses the EXISTING
elrule.predict(carry=...) parameter only.
  V0  as the pred (no carry)                                  -> 57 (reproduced in diag_c146_a2_1_repro.log)
  V1  carry = nodes s04 made (uids in the s05 start state absent from the s04 start state: a diff of two graph reads, 13 nodes)
  V2  carry = owners of the s05 plan's declared `open_rows` (sink rows)
  V3  carry = every non-created owner of the s05 start state
  V1+V2 together
  VX  V1+V2 plus a NOT-MEASURED-IN-THE-TABLE requiredness entry for #5058's VI (Image In rule 1, the base EL text's "required
      input 'Image In'") - shows what data the class-exact answer needs; NOT a candidate fix (subvi_requiredness.json has no such VI).
Per-class key: L/C/SR by item class; 'input' items by their owner_class (IndexArray / BuildArray / SubVI ...); read items by text
(Index Array / Build Array / SubVI required input / local / cond / sr). PREDICTION CONTRACT: V0 == 57; read change == {IndexArray 0,
BuildArray 0, SubVI -1, local 0, sr -2, cond 0} (total -3). Also: for V1 and V3, s01..s04 new/closed with that carry rule
(V3 only; V1 needs the previous session's start, given here for s02..s05).
  py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c146_a2_1_variants.log -- py -u tools/bench/diag_c146_a2_1_variants.py"""
import collections, copy, json, os, sys                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
from tools import elrule as ELR  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


def rclass(x):
    t = "{0} {1}".format(x.get("raw", ""), x.get("detail", ""))
    c = ELR.item_class(t)
    if c:
        return c
    s = t.lower().replace(" ", "")
    if "indexarray" in s and "unwired" in s:
        return "IndexArray"
    if "buildarray" in s and "unwired" in s:
        return "BuildArray"
    if ("subvi" in s or "subvl" in s) and ("requiredinput" in s or "reguiredinput" in s):
        return "SubVI"
    return None


def rec(path):
    return collections.Counter(c for c in (rclass(x) for x in J(path).get("items") or []) if c)


r4 = rec("tools/bench/errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json")
r5 = rec("tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_003324.json")
KEYS = ("IndexArray", "BuildArray", "SubVI", "local", "cond", "sr")
READ = dict((k, r5.get(k, 0) - r4.get(k, 0)) for k in KEYS)
print("READ per-class s04 {0} s05 {1} change {2}".format(dict(r4), dict(r5), READ), flush=True)
gate("READ change == {IndexArray 0, BuildArray 0, SubVI -1, local 0, cond 0, sr -2}",
     READ == {"IndexArray": 0, "BuildArray": 0, "SubVI": -1, "local": 0, "cond": 0, "sr": -2}, READ)


def sess(pp):
    p = J(pp)
    fz = p["finalized"]
    sf = fz["step_files"]
    st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
    made = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - \
        set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
    bp = fz.get("base") or p.get("base") or {}
    return p, st0, last, made, J(bp["path"])


def cls_of(st0, last):
    m = {}
    for s in (st0, last):
        for r in s.get("terminals") or []:
            m[int(r["owner_uid"])] = r.get("owner_class")
    return m


def perclass(P, oc):
    out = collections.Counter()
    for k in P["new_items"]:
        out[k[0] if k[0] != "input" else oc.get(k[1], "?")] += 1
    for k in P["closed_items"]:
        out[k[0] if k[0] != "input" else oc.get(k[1], "?")] -= 1
    return dict((k, out.get(k, 0)) for k in sorted(set(KEYS) | set(out)))


own = lambda st: set(int(r["owner_uid"]) for r in st.get("terminals") or [])  # noqa: E731
PL = [("s01", "tools/bench/plan_ring_p4_s01.json", 51), ("s02", "tools/bench/plan_ring_p4_s02v18.json", 51),
      ("s03", "tools/bench/plan_ring_p4_s03v18.json", 53), ("s04", "tools/bench/plan_ring_p4_s04v18.json", 55),
      ("s05", "tools/bench/plan_ring_p4_s05v18.json", 58)]
S = dict((n, sess(pp) + (bt,)) for n, pp, bt in PL)
TAB = ELR.load_requiredness()
prev = None
for n, pp, bt in PL:
    p, st0, last, made, base, bt = S[n]
    oc = cls_of(st0, last)
    sv = ELR.subvis_from_plan(p, st0, last)
    ex = (base,) if n != "s01" else ()
    v0 = ELR.predict(st0, last, bt, made, extra_owner_states=ex, subvis=sv)
    nonc = own(st0) - set(made)
    v3 = ELR.predict(st0, last, bt, made, carry=nonc, extra_owner_states=ex, subvis=sv)
    same3 = v3["new_items"] == v0["new_items"] and v3["closed_items"] == v0["closed_items"]
    line = "{0}: V0 {1} new {2} closed {3} | V3 {4} new {5} closed {6} same-as-V0 {7}; V3 uncertain_subvi nodes {8}".format(
        n, v0["predicted_total"], v0["new_items"], v0["closed_items"], v3["predicted_total"], v3["new_items"], v3["closed_items"], same3,
        len(v3["uncertain_subvi_terminals"]))
    if prev is not None:
        v1c = own(st0) - own(prev)
        v1 = ELR.predict(st0, last, bt, made, carry=v1c, extra_owner_states=ex, subvis=sv)
        line += " | V1 (carry {0} prev-session-made) {1} new {2} closed {3} same-as-V0 {4}".format(
            len(v1c), v1["predicted_total"], v1["new_items"], v1["closed_items"],
            v1["new_items"] == v0["new_items"] and v1["closed_items"] == v0["closed_items"])
    print("SESS " + line, flush=True)
    if n == "s05":
        v1c = own(st0) - own(prev)
        decl = set(int(r["node"]) for r in p.get("open_rows") or [])
        for nm, carry, tab, svx in (("V0", (), TAB, sv), ("V1", v1c, TAB, sv), ("V2", decl, TAB, sv), ("V3", nonc, TAB, sv),
                                    ("V1+V2", v1c | decl, TAB, sv)):
            P = ELR.predict(st0, last, bt, made, carry=carry, extra_owner_states=ex, subvis=svx, table=tab)
            pc = perclass(P, oc)
            print("S05 {0}: total {1}; per-class change {2}; equal-to-read {3}; new {4}; closed {5}; uncertain_subvi {6}".format(
                nm, P["predicted_total"], pc, all(pc.get(k, 0) == READ[k] for k in set(KEYS) | set(pc)), P["new_items"], P["closed_items"],
                [x[:2] for x in P["uncertain_subvi_terminals"] if x[0] in (5058, 29724, 29719)]), flush=True)
        tabx = copy.deepcopy(TAB)
        rs = [r for r in st0.get("terminals") or [] if int(r["owner_uid"]) == 5058]
        tabx["vis"]["X_5058.vi"] = {"terminals": [{"name": r.get("term_name"), "rule": (1 if r.get("term_name") == "Image In" else 0)} for r in rs]}
        svx = dict(sv)
        svx[5058] = "X_5058.vi"
        P = ELR.predict(st0, last, bt, made, carry=v1c | decl, extra_owner_states=ex, subvis=svx, table=tabx)
        pc = perclass(P, oc)
        print("S05 VX (V1+V2 + hypothetical table row 'Image In' rule 1 for #5058, NOT in subvi_requiredness.json): total {0}; per-class change {1}; "
              "equal-to-read {2}; new {3}; closed {4}".format(P["predicted_total"], pc, all(pc.get(k, 0) == READ[k] for k in set(KEYS) | set(pc)),
                                                            P["new_items"], P["closed_items"]), flush=True)
    prev = st0
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
