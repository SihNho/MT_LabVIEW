# ---
# labview: none
# hardware: none
# ---
r"""termclass_table - card chat-T5 (PD349(b), OFFLINE, no LabVIEW): the MEASURED terminal-class table the simulator uses for a
created node's terminal rows (tools/stagesim.py measured_term_class).

Why: the simulator gave a created Function node's terminals the declared class, and a plan that declared (or defaulted) 'Terminal'
stopped the real run at the first BINDING (bench arms B and A13, s04v18 op 2 'p4_wait': sim ('Terminal', ...) vs real
('ParameterTerminal', ...), V6_bench/B/tools/bench/diag_c144_p4s04v18_scratch.log:197). LabVIEW reports the class; nothing here
guesses it.
Existed first (checked): stage_prerun X16 (a create must DECLARE term_class - it never checks the value), stagesim QUEUE_TERM_TABLE
(names/directions of Dequeue only), tools/bench/diag_c124_p3a_termclass.py (one-off P3a read). None is a table over all reads.
Source: every tools/bench/graph_*.json and diag_*scratch*.json whose top-level `terminals` rows carry term_class (all read_live on
real LabVIEW byte copies; one file per distinct md5).
Output tools/bench/termclass_table.json:
  owner      {owner_class: {term_class: rows}}                  - every class LabVIEW reported for that owner class
  signature  {owner_class: {sig: {"name|src": {term_class: n}}}} - only owner classes with a Parameter-type class; sig = the
             node's sorted (name, is_source) list as JSON, i.e. one primitive's terminal set
PREDICTION CONTRACT: T1 >= 20 source files; T2 owner 'Function' classes subset of {ParameterTerminal, OverridableParameterTerminal}
  and no 'Terminal'; T3 the Wait (ms) signature gives ParameterTerminal on both rows, no other class; T4 Local / DigitalNumericConstant
  are 'Terminal' only (X16's exemptions agree); T5 table written.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/termclass_table.log -- py -u tools/bench/termclass_table.py"""
import collections, glob, hashlib, json, os, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
OUT = os.path.join(ROOT, "tools", "bench", "termclass_table.json")
PARAM = ("ParameterTerminal", "OverridableParameterTerminal")
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:600]), flush=True)


def sig_of(rows):
    return json.dumps(sorted([r.get("term_name") or "", bool(r.get("is_source"))] for r in rows))


owner = collections.defaultdict(collections.Counter)
by_node = []                                     # (owner_class, rows) per node, over all files
srcs, seen = [], set()
for f in sorted(set(glob.glob(os.path.join(ROOT, "tools", "bench", "graph_*.json"))
                    + glob.glob(os.path.join(ROOT, "tools", "bench", "diag_*scratch*.json")))):
    h = hashlib.md5(open(f, "rb").read()).hexdigest()
    if h in seen:
        continue
    try:
        g = json.load(open(f, encoding="utf-8"))
    except ValueError:
        continue
    ts = g.get("terminals") if isinstance(g, dict) else None
    if not isinstance(ts, list) or not ts or not isinstance(ts[0], dict) or "term_class" not in ts[0]:
        continue
    seen.add(h)
    srcs.append({"path": os.path.relpath(f, ROOT).replace("\\", "/"), "md5": h})
    nodes = collections.defaultdict(list)
    for r in ts:
        owner[r.get("owner_class")][r.get("term_class")] += 1
        nodes[(r.get("owner_class"), r.get("owner_uid"))].append(r)
    by_node += [(k[0], rs) for k, rs in nodes.items()]
pclasses = set(oc for oc, c in owner.items() if any(k in PARAM for k in c))
sig = collections.defaultdict(lambda: collections.defaultdict(lambda: collections.defaultdict(collections.Counter)))
for oc, rs in by_node:
    if oc in pclasses:
        s = sig_of(rs)
        for r in rs:
            sig[oc][s]["{0}|{1}".format(r.get("term_name") or "", int(bool(r.get("is_source"))))][r.get("term_class")] += 1
gate("T1 >= 20 distinct real graph reads", len(srcs) >= 20, len(srcs))
fc = set(owner.get("Function") or {})
gate("T2 Function rows are Parameter-type only (no 'Terminal')", fc and fc <= set(PARAM), dict(owner.get("Function") or {}))
ws = sig["Function"].get(sig_of([{"term_name": "milliseconds to wait", "is_source": False},
                                 {"term_name": "millisecond timer value", "is_source": True}])) or {}
gate("T3 Wait (ms): both rows ParameterTerminal only", ws and all(set(v) == {"ParameterTerminal"} for v in ws.values()),
     dict((k, dict(v)) for k, v in ws.items()))
gate("T4 Local and DigitalNumericConstant rows are 'Terminal' only (X16 exemptions agree)",
     set(owner.get("Local") or {}) == {"Terminal"} and set(owner.get("DigitalNumericConstant") or {}) == {"Terminal"},
     [dict(owner.get("Local") or {}), dict(owner.get("DigitalNumericConstant") or {})])
tab = {"schema": "termclass_table/1", "card": "chat-T5", "pd": "PD349(b)", "sources": srcs,
       "owner": dict((k, dict(v)) for k, v in sorted(owner.items(), key=lambda x: str(x[0]))),
       "signature": dict((oc, dict((s, dict((k, dict(c)) for k, c in d.items())) for s, d in sorted(v.items())))
                         for oc, v in sorted(sig.items()))}
json.dump(tab, open(OUT, "w", encoding="utf-8"), indent=1, sort_keys=True)
gate("T5 table written", os.path.exists(OUT), "{0} owner classes, {1} signatures".format(
    len(tab["owner"]), sum(len(v) for v in tab["signature"].values())))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": os.path.relpath(OUT, ROOT),
      "md5": hashlib.md5(open(OUT, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if G["fail"] else 0)
