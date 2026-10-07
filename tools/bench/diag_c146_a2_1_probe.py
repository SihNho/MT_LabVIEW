# ---
# labview: none
# hardware: none
# ---
r"""diag_c146_a2_1_probe - card 146-a3-1 (OFFLINE, read-only): what each P4 session's START state holds that could name the base's
still-open input items without a uid list: base-doc keys, the requiredness table's VIs, and per session s01..s05 the NON-created
nodes with an unwired non-control sink at start, and which of those have every such sink wired at the end (would be debited
under a 'base nodes count like created' rule). PREDICTION CONTRACT: none (a census; RESULT 0/0 unless a file is unreadable).
  py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c146_a2_1_probe.log -- py -u tools/bench/diag_c146_a2_1_probe.py"""
import collections, json, os, sys                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
from tools import elrule as ELR  # noqa: E402
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
tab = ELR.load_requiredness()
print("TABLE vis {0}".format({k: [(t.get("name"), t.get("rule")) for t in v.get("terminals") or []] for k, v in (tab.get("vis") or {}).items()}), flush=True)
PL = [("s01", "tools/bench/plan_ring_p4_s01.json"), ("s02", "tools/bench/plan_ring_p4_s02v18.json"), ("s03", "tools/bench/plan_ring_p4_s03v18.json"),
      ("s04", "tools/bench/plan_ring_p4_s04v18.json"), ("s05", "tools/bench/plan_ring_p4_s05v18.json")]
for nm, pp in PL:
    p = J(pp)
    fz = p.get("finalized") or {}
    bp = fz.get("base") or p.get("base") or {}
    sf = fz["step_files"]
    st0, last = J(sf[0]["path"])["state"], J(sf[-1]["path"])["state"]
    made = set(int(u) for u in (last.get("sym") or {}).values() if isinstance(u, int)) - \
        set(int(u) for u in (st0.get("sym") or {}).values() if isinstance(u, int))
    try:
        b = J(bp["path"]) if bp.get("path") else {}
    except Exception as e:                                                                   # noqa: BLE001
        b = {"_err": str(e)}
    print("SESSION {0} base {1} keys {2}; st0 keys {3}".format(nm, bp.get("path"), sorted(b.keys())[:30], sorted(st0.keys())), flush=True)
    r0 = collections.defaultdict(list)
    r1 = collections.defaultdict(list)
    for r in st0.get("terminals") or []:
        r0[int(r["owner_uid"])].append(r)
    for r in last.get("terminals") or []:
        r1[int(r["owner_uid"])].append(r)
    unw = lambda rs: [x.get("term_name") for x in rs if not x.get("is_source") and not x.get("wire_uid") and x.get("term_class") != "ControlTerminal"]  # noqa: E731
    open0 = dict((u, unw(rs)) for u, rs in r0.items() if u not in made and unw(rs) and rs[0].get("owner_class") not in ("Local", "Diagram", "RightShiftRegister"))
    closing = dict((u, (r0[u][0].get("owner_class"), open0[u], unw(r1.get(u, [])))) for u in open0 if len(unw(r1.get(u, []))) < len(open0[u]))
    print("SESSION {0} base nodes with unwired sinks at start: {1}; by class {2}".format(nm, len(open0), dict(collections.Counter(r0[u][0].get("owner_class") for u in open0))), flush=True)
    print("SESSION {0} of those, sinks wired during the session (uid: class, start unwired, end unwired): {1}".format(nm, closing), flush=True)
print(protocol.result_line(protocol.make_result(0, 0, None, [])), flush=True)
