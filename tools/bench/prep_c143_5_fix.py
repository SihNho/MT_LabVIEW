r"""prep_c143_5_fix - card 143-5 step 1 (OFFLINE, no LabVIEW; PD335(b)). Lists every s03 action END (src/dst/at/born_on/on) that sits on a
Local of the BASE (plan_ring_p4_s03v18.json base = sim/ring_p4_s03v18_s02end/base_provisional.json) whose terminal name differs from the base
row's name, and rewrites ONLY that term address to the base row's name (read from the base rows by script, never typed). Same rewrite applied to
the stage input plan_ring_p4_s03v18_in.json (finalized.plan_in, the recipe's L0 input) so the two stay one plan. Locals CREATED inside s03
('new:<as>.<term>') have no base row - listed as facts, not rewritten (card scope). Existing tools checked first: stage_prerun.rebase
(:3895-3906 refuses a named term whose name is not on the sim row), prep_c143_4_probe.py (found the one -20 row, 'StopAll').
PREDICTION CONTRACT: exactly 1 end rewritten = p4_w_stop12 src #-20 'value' -> 'StopAll' (prep_c143_4_probe2.log:17-19); 0 Local ends with
  0 or >1 candidate rows; the real graph eda9db40 holds >=1 Local row named 'StopAll' (source); every other action byte-identical.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c143_5_fix.log -- py -u tools/bench/prep_c143_5_fix.py"""
import copy, hashlib, json, os, re, sys                                                 # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR                                                                 # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
PLANS = [os.path.join(B, "plan_ring_p4_s03v18.json"), os.path.join(B, "plan_ring_p4_s03v18_in.json")]
REAL = os.path.join(B, "graph_ring_p4s02_20261003_112505.json")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


def ends(a):
    """(field, uid, term, kind) for every address end of an action; kind 'dict' or 'str'."""
    for f in SPR.ADDR_FIELDS:
        v = a.get(f)
        if isinstance(v, dict) and isinstance(v.get("uid"), int) and isinstance(v.get("term"), str):
            yield f, v["uid"], v["term"], "dict"
        elif isinstance(v, str):
            m = re.match(r"^(-?\d+)\.(.*)$", v)
            if m:
                yield f, int(m.group(1)), m.group(2), "str"


def scan(plan, base, real):
    cls = dict((o["uid"], o.get("class")) for o in base.get("objs") or [] if isinstance(o, dict) and isinstance(o.get("uid"), int))
    for r in base["terminals"]:
        cls.setdefault(r["owner_uid"], r.get("owner_class"))
    out, bad, newloc = [], [], []
    for i, a in enumerate(plan["actions"], 1):
        for f, u, t, kind in ends(a):
            if cls.get(u) != "Local":
                continue
            want_src = f == "src"
            rows = [r for r in base["terminals"] if r["owner_uid"] == u and (f not in ("src", "dst") or bool(r.get("is_source")) == want_src)]
            if len(rows) != 1:
                bad.append((i, a["id"], f, u, t, [(r["term_uid"], r.get("term_name")) for r in rows]))
                continue
            bn = rows[0].get("term_name", "")
            rr = [(r["term_uid"], r.get("term_name"), r.get("is_source")) for r in real["terminals"]
                  if r.get("owner_class") == "Local" and r.get("term_name") == bn]
            out.append({"k": i, "id": a["id"], "field": f, "uid": u, "term": t, "base_term_uid": rows[0]["term_uid"], "base_name": bn,
                        "differs": t != bn, "kind": kind, "real_local_rows_same_name": rr})
        for f in SPR.ADDR_FIELDS:
            v = a.get(f)
            if isinstance(v, str) and v.startswith("new:"):
                newloc.append((a["id"], f, v))
    creates = dict((a.get("as"), [x.get("name") for x in a.get("terminals") or []]) for a in plan["actions"] if a.get("op") == "create" and a.get("class") == "Local")
    newloc = [(i, f, v, creates[v[4:].split(".", 1)[0]]) for i, f, v in newloc if v[4:].split(".", 1)[0] in creates]
    return out, bad, newloc


real = J(REAL)
gate("IN real graph md5 eda9db40", md5(REAL) == "eda9db4088d1be89623e6333268e09ff", md5(REAL))
for P in PLANS:
    m0 = md5(P)
    plan = J(P)
    bp = plan.get("base") or {}
    base = J(bp["path"])
    gate("IN {0} md5 {1}; base {2} provisional, base file md5 == plan's".format(rel(P), m0, bp.get("path")),
         bp.get("provisional") is True and md5(os.path.join(ROOT, bp["path"])) == bp.get("md5"), bp)
    found, bad, newloc = scan(plan, base, real)
    for x in found:
        print("FACT LOCAL-END {0} k{1} {2} {3} #{4}.{5!r} base row #{6} {7!r} differs={8} | real Local rows named so: {9}".format(
            rel(P), x["k"], x["id"], x["field"], x["uid"], x["term"], x["base_term_uid"], x["base_name"], x["differs"], x["real_local_rows_same_name"]), flush=True)
    for x in newloc:
        print("FACT NEW-LOCAL-END (s03-created, no base row, not rewritten) {0} {1} {2!r} declared terminals {3}".format(*x), flush=True)
    gate("no base-Local end with 0 or >1 candidate rows", not bad, bad)
    diff = [x for x in found if x["differs"]]
    gate("prediction: exactly 1 differing end = p4_w_stop12 src #-20 'value' -> 'StopAll'",
         [(x["id"], x["field"], x["uid"], x["term"], x["base_name"]) for x in diff] == [("p4_w_stop12", "src", -20, "value", "StopAll")], diff)
    gate("real graph holds >=1 SOURCE Local row named 'StopAll'", any(s for _u, _n, s in diff[0]["real_local_rows_same_name"]), diff[0]["real_local_rows_same_name"])
    new = copy.deepcopy(plan)
    for x in diff:
        a = new["actions"][x["k"] - 1]
        if x["kind"] == "dict":
            a[x["field"]]["term"] = x["base_name"]
        else:
            a[x["field"]] = "{0}.{1}".format(x["uid"], x["base_name"])
        # `why` is NOT extended: stageplan/1 caps it at 400 chars and this one is at the cap (prep_c143_5_rebase.log, 545 > 400);
        # the change is recorded in prep_c143_5_facts.md instead.
    same = [i for i, (a, b) in enumerate(zip(plan["actions"], new["actions"]), 1) if a != b]
    gate("only the rewritten action(s) changed: {0}".format(same), same == sorted(set(x["k"] for x in diff)), same)
    json.dump(new, open(P, "w", encoding="utf-8"), indent=1)
    gate("re-scan {0}: 0 differing Local ends (md5 {1} -> {2})".format(rel(P), m0, md5(P)), not [x for x in scan(J(P), base, real)[0] if x["differs"]])
    ARTS.append({"path": rel(P), "md5": md5(P)})
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
