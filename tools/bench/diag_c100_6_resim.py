r"""diag_c100_6_resim - card 100-6 (ii)->(iii), PD213(f)3 "if they differ, re-simulate". Pure Python, no LabVIEW.
MEASURED (facts_c100_maxmin.json, diag_c100_6_maxmin.log): the donor Max & Min node #43 has terminals x, y (sinks),
max(x,y), min(x,y) (sources, NO space) and owner_class 'Comparison'. plan r3_open says 'max(x, y)', 'min(x, y)' and
class 'Function'. This writes stageplan_disp_r4_open.json = r3_open with ONLY those strings replaced (r7_max terminals +
class, and every 'new:MAX1.<old name>' end), re-simulates it (stagesim, same call as diag_c100_plan.py:119) and gates:
R1 r4 validates; R2 only the MAX1 strings differ from r3_open; R3 simulates FINAL; R4 end cdiff rows == r3_open's
declared open_rows (the same 21). plan_disp.json is re-written by the simulation (md5 reported).
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c100_6_resim.log -- py -u tools/bench/diag_c100_6_resim.py"""
import copy, json, os, sys                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol           # noqa: E402
import stagesim as SS     # noqa: E402

DISP = os.path.join(HERE, "sim", "disp")
R3O, R4O = os.path.join(DISP, "stageplan_disp_r3_open.json"), os.path.join(DISP, "stageplan_disp_r4_open.json")
MM = json.load(open(os.path.join(HERE, "facts_c100_maxmin.json"), encoding="utf-8"))
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)


r3 = json.load(open(R3O, encoding="utf-8"))
mx = next(a for a in r3["actions"] if a.get("id") == "r7_max")
alias = "new:" + mx["as"] + "."
read = dict((n, s) for n, s in MM["names"])                     # measured name -> is_source
ren = {}
for t in mx["terminals"]:                                       # plan name -> measured name (same direction, same name
    cand = [n for n, s in read.items() if s == t["is_source"] and n.replace(" ", "") == t["name"].replace(" ", "")]
    gate("M {0!r} -> exactly one measured terminal of the same direction, equal up to spaces".format(t["name"]),
         len(cand) == 1, cand)
    if len(cand) == 1 and cand[0] != t["name"]:
        ren[t["name"]] = cand[0]
cls = MM["owner_class"][0] if len(MM["owner_class"]) == 1 else None
gate("M class read as one value", cls is not None, MM["owner_class"])
r4 = copy.deepcopy(r3)
for a in r4["actions"]:
    if a.get("id") == "r7_max":
        a["class"] = cls
        for t in a["terminals"]:
            t["name"] = ren.get(t["name"], t["name"])
        a["why"] += " | card 100-6: terminal names + class MEASURED on the donor (facts_c100_maxmin.json)"
    for k in ("src", "dst", "on", "at", "born_on"):
        v = a.get(k)
        if isinstance(v, str) and v.startswith(alias) and v[len(alias):] in ren:
            a[k] = alias + ren[v[len(alias):]]
json.dump(r4, open(R4O, "w", encoding="utf-8"), indent=1)
diff = [(i, k) for i, (a, b) in enumerate(zip(r3["actions"], r4["actions"])) for k in set(a) | set(b) if a.get(k) != b.get(k)]
gate("R2 only r7_max (class/terminals/why) and MAX1 ends changed: renames {0}".format(ren),
     len(r3["actions"]) == len(r4["actions"]) and all(r4["actions"][i].get("id") == "r7_max" and k in ("class", "terminals", "why")
                                                      or k in ("src", "dst", "on", "at", "born_on") for i, k in diff), diff)
ok, why = protocol.validate_obj(r4)
gate("R1 r4 validates under the installed schema", ok, why)
S = SS.simulate(R4O, os.path.join(ROOT, r4["base"]["path"]), out_root=os.path.join(HERE, "sim"), plan_out_dir=DISP,
                log=lambda *_a: None)
gate("R3 r4 simulates FINAL", S["final"], (S["failed"], S["undecided"], S["first_divergent"]))
want = sorted((int(r["node"]), r["term"]) for r in r4["open_rows"])
got = sorted(set((int(k.split("|")[0]), k.split("|")[2]) for k in S["end_cdiff_rows"] or []))
gate("R4 end cdiff rows == the {0} declared open_rows".format(len(want)), got == sorted(set(want)),
     {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))})
po = S.get("plan_out")                                          # run 1: a {path, md5} dict, not a path (TypeError)
po = os.path.join(ROOT, po["path"]) if isinstance(po, dict) and not os.path.isabs(po["path"]) else (po["path"] if isinstance(po, dict) else po)
print("  FACT plan_out {0} md5 {1}".format(po, po and SS.md5_file(po)), flush=True)
n = sum(1 for _l, g_ in gates if g_)
ff = next((l for l, g_ in gates if not g_), None)
arts = [{"path": os.path.relpath(p, ROOT), "md5": SS.md5_file(p)} for p in (R4O, po) if p and os.path.exists(p)]
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
