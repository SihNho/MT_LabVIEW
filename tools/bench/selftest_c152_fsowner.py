# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_152-a2-1.md
# ---
r"""selftest_c152_fsowner - card 152-a2-1 (docs/d1/ring-p4d.md PD368(c)): stagesim.fs_measured_state takes the THIRD measured owner
link, graph['fs_owner_read'] = {fs uid: ["Diagram", uid]} with graph['fs_owner_read_cite']['echo'] = ["FlatSequence", fs uid],
into fs_parent - for an FS with NO border outer face only; where faces exist they must be one outer frame equal to the read, else
UNMEASURED; a read whose class is not exactly 'Diagram', whose uid is 0, or whose echo is missing / names another uid / another
class makes the FS UNMEASURED. OFFLINE (no COM, nothing written).
FIXTURES: small mutations (deepcopy) of the REAL derived graph graph_ring_p4s08_20261009_033522_fsowner.json (e26b4d90; FS #29721
has one frame #29869 and 0 border tunnels, read = Diagram #23166, echo FlatSequence #29721, diag_c152_a1_1_owner.log:25,29) and of
the original graph graph_ring_p4s08_20261009_033522.json (44858dbf, no fs_owner_read key) - the style of selftest_c134_4_owners O6.
EXISTING checked first: selftest_c134_4_owners.py (the 2 border-face links, 7 cases, not edited), selftest_c134_1_fsmap.py,
diag_c152_a2_1_ident.py (before-dump of the two key-less graphs).
PREDICTION: R1 derived: 29721 in fs_parent == 23166, owners['29721'] == ['Diagram', 23166], fs_unmeasured [2499, 14682, 43914];
R2 a faced FS whose read disagrees with its faces -> UNMEASURED, no owner entry; R3 class 'TopLevelDiagram' -> UNMEASURED;
R4 uid 0 -> UNMEASURED; R5a no echo / R5b echo uid 29722 / R5c echo class 'Diagram' / R5d no cite -> UNMEASURED; R6 a faced FS
whose read agrees -> resolved to its face diagram; R7 derived minus the two keys gives fs_measured_state + base_state identical
to the original graph's and to diag_c152_a2_1_ident_before.json; R8 original graph fs_unmeasured [2499, 14682, 29721, 43914];
R9 _diag_chain from frame #29869 on the derived graph reaches Diagram #23166 (then 23166's own tree parents); R10 on the original
graph it raises SimError naming FS #29721; R11 a read naming a uid that is not a measured FS changes nothing; R12 a faced FS with
an invalid read (class not Diagram) -> UNMEASURED (PD368(c) literal: 'else UNMEASURED')."""
import copy, json, os, sys                                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS, protocol as P                                                         # noqa: E401,E402
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def dump(x):
    return json.dumps(x, sort_keys=True, default=repr)


D = json.load(open(os.path.join(HERE, "graph_ring_p4s08_20261009_033522_fsowner.json"), encoding="utf-8"))
O = json.load(open(os.path.join(HERE, "graph_ring_p4s08_20261009_033522.json"), encoding="utf-8"))
FS, FR, DG = 29721, 29869, 23166
print("  FACT  derived fs_owner_read {0}; cite echo {1}".format(D.get("fs_owner_read"), (D.get("fs_owner_read_cite") or {}).get("echo")))


def um(g):
    st = SS.base_state(g)
    return st, st["fs_unmeasured"]


# R1 the real derived graph
m = SS.fs_measured_state(D)
st, u = um(D)
gate("R1 derived: 29721 -> fs_parent 23166, owners ['Diagram', 23166], fs_unmeasured [2499, 14682, 43914]",
     m["fs_parent"].get(FS) == DG and st["owners"].get(str(FS)) == ["Diagram", DG] and u == [2499, 14682, 43914],
     {"fs_parent": m["fs_parent"].get(FS), "owner": st["owners"].get(str(FS)), "unmeasured": u, "read": m.get("fs_owner_read")})
mo = SS.fs_measured_state(O)
faced = sorted(fs for fs in mo["fs_parent"])
f1 = faced[0]
p1 = mo["fs_parent"][f1]
print("  FACT  original graph: {0} faced FS with one agreeing outer diagram; test FS #{1} on #{2}".format(len(faced), f1, p1), flush=True)


def with_read(entry_fs, entry, echo="same", cite=True):
    g = copy.deepcopy(D)
    g["fs_owner_read"] = {str(entry_fs): entry}
    if not cite:
        g.pop("fs_owner_read_cite", None)
    elif echo is None:
        g["fs_owner_read_cite"].pop("echo", None)
    else:
        g["fs_owner_read_cite"]["echo"] = ["FlatSequence", entry_fs] if echo == "same" else echo
    return g


g = with_read(f1, ["Diagram", p1 + 1000000])
st2, u2 = um(g)
gate("R2 faced FS #{0}: read Diagram #{1} != faces #{2} -> UNMEASURED, no owner entry".format(f1, p1 + 1000000, p1),
     f1 in u2 and str(f1) not in st2["owners"] and FS in u2, {"unmeasured": u2, "owner": st2["owners"].get(str(f1))})
for lab, entry, echo, cite in (("R3 class 'TopLevelDiagram'", ["TopLevelDiagram", DG], "same", True),
                               ("R4 uid 0", ["Diagram", 0], "same", True),
                               ("R5a echo missing", ["Diagram", DG], None, True),
                               ("R5b echo uid 29722 != FS", ["Diagram", DG], ["FlatSequence", FS + 1], True),
                               ("R5c echo class 'Diagram'", ["Diagram", DG], ["Diagram", FS], True),
                               ("R5d no fs_owner_read_cite", ["Diagram", DG], "same", False)):
    g = with_read(FS, entry, echo, cite)
    stx, ux = um(g)
    mx = SS.fs_measured_state(g)
    gate("{0} -> FS #29721 UNMEASURED, no owner entry".format(lab), FS in ux and str(FS) not in stx["owners"] and FS not in mx["fs_parent"],
         {"unmeasured": ux, "owner": stx["owners"].get(str(FS)), "read": mx.get("fs_owner_read")})
g = with_read(f1, ["Diagram", p1])
st6, u6 = um(g)
gate("R6 faced FS #{0}: read agrees with faces #{1} -> resolved".format(f1, p1),
     f1 not in u6 and st6["owners"].get(str(f1)) == ["Diagram", p1], {"unmeasured": u6, "owner": st6["owners"].get(str(f1))})
g = copy.deepcopy(D)
g.pop("fs_owner_read")
g.pop("fs_owner_read_cite")
before = json.load(open(os.path.join(HERE, "diag_c152_a2_1_ident_before.json"), encoding="utf-8"))
K = "graph_ring_p4s08_20261009_033522.json|"
same = (dump(SS.fs_measured_state(g)) == dump(mo) == before[K + "fs_measured_state"]
        and dump(SS.base_state(g)) == dump(SS.base_state(O)) == before[K + "base_state"])
gate("R7 derived minus fs_owner_read(+cite) == original graph == before-dump (fs_measured_state + base_state)", same)
sto, uo = um(O)
gate("R8 original graph fs_unmeasured [2499, 14682, 29721, 43914], no owner for 29721", uo == [2499, 14682, 29721, 43914]
     and str(FS) not in sto["owners"], uo)
par = dict((int(k), int(v)) for k, v in SS.graph(st)["tree"]["parent"].items() if v is not None)
ch = SS._diag_chain(st, FR, par)
print("  FACT  _diag_chain(derived, #29869) = {0}".format(ch), flush=True)
gate("R9 _diag_chain from frame #29869 reaches Diagram #23166", len(ch) >= 2 and ch[0] == FR and ch[1] == DG, ch)
paro = dict((int(k), int(v)) for k, v in SS.graph(sto)["tree"]["parent"].items() if v is not None)
try:
    SS._diag_chain(sto, FR, paro)
    r10 = (False, "no error")
except SS.SimError as e:
    r10 = ("29721" in str(e) and "UNMEASURED" in str(e), str(e))
gate("R10 original graph: _diag_chain from #29869 raises SimError naming FS #29721", *r10)
g = with_read(99999999, ["Diagram", DG])
g["fs_owner_read"][str(FS)] = ["Diagram", DG]            # keep the real entry beside it
g["fs_owner_read_cite"]["echo"] = ["FlatSequence", FS]
m11 = SS.fs_measured_state(g)
gate("R11 a read naming uid 99999999 (not a measured FS) adds nothing; 29721 still resolved",
     99999999 not in m11["fs_parent"] and m11["fs_parent"].get(FS) == DG, m11.get("fs_owner_read"))
g = with_read(f1, ["TopLevelDiagram", p1])
st12, u12 = um(g)
gate("R12 faced FS #{0} with read class 'TopLevelDiagram' -> UNMEASURED (literal PD368(c))".format(f1), f1 in u12
     and str(f1) not in st12["owners"], u12)
nf = res.count(False)
print(P.result_line(P.make_result(res.count(True), nf, None if not nf else "selftest_c152_fsowner")), flush=True)
sys.exit(1 if nf else 0)
