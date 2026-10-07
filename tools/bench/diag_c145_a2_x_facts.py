# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_x_facts - card 145-a2-X (OFFLINE, read-only, no LabVIEW): facts for X11 (PD351(d)) on Build Array #2626.

Existed first: stagexec.compile_plan (op numbering, the one prep_c145_p1_mk.py:73-75 uses), stage_prerun._base_terms /
pb_licences / buildarray_open_sibling (the X11 gate, stage_prerun.py:1246-1308, 2905-2911). Nothing new is built; this only
calls them and prints. No plan, pred, recipe or tool is written.

PREDICTION CONTRACT: M0 the four card inputs hash to the card md5s; C1 compile_plan(v18) ops 98..124 cover exactly the 33
actions of plan_ring_p4_s05v18.json (p4_t_slot..p4_w_fd_in); F1 ops 118/119 = p4_w_tp_row / p4_w_rp_row; U inputs unchanged
after. Everything else is printed as FACT (no expectation): #2626 terminals in the v18 base and the s05 provisional base, every
v18 action naming uid 2626 (op no., session), X11 flags on v18 / s05 with their licence field.
"""
import collections, hashlib, json, os, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX, stage_prerun as SPR                                                  # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
P = dict(brief=os.path.join(B, "cards", "brief_145-a2-X.md"), v18=os.path.join(B, "plan_ring_p4_v18.json"),
         lic=os.path.join(B, "plan_l2b1_licence.json"), s04=os.path.join(B, "plan_ring_p4_s04v18.json"))
WANT = dict(brief="60af3bf96f29ace5cb8341863be7a07d", v18="2ea6cafa7d368dc7a054346d398daa3e",
            lic="efbc8bcc2208f2673e8f89c9907fd7f3", s04="f349c39a17330531e688ff1f70ce426e")
S05 = os.path.join(B, "plan_ring_p4_s05v18.json")
L2B1 = os.path.join(B, "plan_l2b1.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


def fact(*a):
    print("FACT", *a, flush=True)


gate("M0 card inputs md5 == card", all(md5(P[k]) == WANT[k] for k in P), dict((k, md5(P[k])) for k in P))
v18, s04, s05 = J(P["v18"]), J(P["s04"]), J(S05)
A = v18["actions"]
OPS = SX.compile_plan(v18)
act2op = dict((n, k) for k, o in enumerate(OPS, 1) for n in o["acts"])
fact("v18 actions", len(A), "ops", len(OPS))
s04ids = [a["id"] for a in s04["actions"]]
s05ids = [a["id"] for a in s05["actions"]]
r04 = sorted(set(act2op[i + 1] for i, a in enumerate(A) if a["id"] in s04ids))
fact("s04 actions", len(s04ids), "-> v18 ops", r04[0], "..", r04[-1])
ops5 = [k for k in range(98, 125)]
ids_98_124 = [A[n - 1]["id"] for k in ops5 for n in OPS[k - 1]["acts"]]
gate("C1 v18 ops 98..124 == s05 plan's {0} actions".format(len(s05ids)), ids_98_124 == s05ids, (ids_98_124[:3], ids_98_124[-3:]))
for k in range(115, 122):
    o = OPS[k - 1]
    fact("op", k, o["kind"], [A[n - 1]["id"] for n in o["acts"]])
gate("F1 op 118 = p4_w_tp_row, op 119 = p4_w_rp_row",
     [A[n - 1]["id"] for n in OPS[117]["acts"]] == ["p4_w_tp_row"] and [A[n - 1]["id"] for n in OPS[118]["acts"]] == ["p4_w_rp_row"])


def names_2626(a):
    s = json.dumps(a)
    return '"uid": 2626' in s or "2626" in json.dumps(a.get("nodes", []))


for i, a in enumerate(A):
    if names_2626(a) or (isinstance(a.get("src"), dict) and a["src"].get("uid") == 2626):
        side = "src" if isinstance(a.get("src"), dict) and a["src"].get("uid") == 2626 else "dst/other"
        fact("v18 action #{0} id {1} op {2} kind {3} side {4} src {5} dst {6}".format(
            i + 1, a.get("id"), act2op.get(i + 1), a.get("op"), side, json.dumps(a.get("src")), json.dumps(a.get("dst"))))
consume = [a.get("id") for a in A if isinstance(a.get("src"), dict) and a["src"].get("uid") == 2626]
fact("v18 actions with src uid 2626 (consume #2626 output):", consume or "NONE")
fin = v18.get("finalized") or {}
fact("v18 finalized open_rows contains (2626,'array'):", [2626, "array"] in fin.get("open_rows", []), "final:", v18.get("final"),
     "last_step:", (fin.get("last_step") or {}).get("path"))
for tag, pl in (("v18 base", v18), ("s05 provisional base", s05)):
    cls, by = SPR._base_terms(pl)
    fact(tag, (pl.get("base") or {}).get("path"), "class(2626) =", cls.get(2626))
    for t in sorted(by.get(2626, []), key=lambda t: int(t.get("term_uid") or 0)):
        fact("  #2626 t{0} name {1!r} is_source {2} wired {3}".format(t.get("term_uid"), t.get("term_name"), t.get("is_source"),
                                                                     t.get("wired", t.get("is_wired"))))
for tag, path in (("v18", P["v18"]), ("s05", S05), ("l2b1", L2B1)):
    lic = SPR.pb_licences(path)
    fact("pb_licences({0}) =".format(tag), lic or "{}")
    fl = SPR.buildarray_open_sibling(J(path), licences=lic)
    for x in fl:
        fact("X11 flag {0}: row {1} node {2} wired {3!r} open {4} licensed {5}".format(tag, x["row"], x["node"], x["wired"], x["open"], x["licensed"]))
    fact("X11 {0}: flags {1}, unlicensed {2}".format(tag, len(fl), len([x for x in fl if not x["licensed"]])))
gate("U card inputs unchanged after", all(md5(P[k]) == WANT[k] for k in P))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
