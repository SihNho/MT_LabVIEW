# ---
# labview: none
# hardware: none
# ---
r"""diag_c144_2_cls - card 144-a2-1 (OFFLINE): the class of every object the s03v18 scratch CREATED, for the E5 block of
diag_c144_2_graph_plan.json: plan_ring_p4_s03v18.json create actions (id -> class) joined with the scratch log's
'STEPX nn create acts [..] ids ['<id>'] bound {<sym>: <uid>, ...}' lines (first bound uid of a create = the created object).
v1/v2 of this helper walked the scratch json's dicts and read wrong fields (diag_c144_2_cls.log earlier runs; gate-fp fp-44).
PREDICTION: 9 create actions, each with exactly one STEPX line and a bound uid; the uid -> class map equals the graph plan's
edits.made.  -> RESULT 2/0
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c144_2_cls.log -- py -u tools/bench/diag_c144_2_cls.py"""
import ast, json, os, re, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
plan = json.load(open(os.path.join(B, "plan_ring_p4_s03v18.json"), encoding="utf-8"))
creates = dict((a["id"], a["class"]) for a in plan["actions"] if a.get("op") == "create")
lines = open(os.path.join(B, "diag_c143_p4s03v18_scratch.log"), encoding="utf-8", errors="replace").read().splitlines()
RX = re.compile(r"STEPX\s+\d+\s+create\s+acts \[\d+\] ids \['([^']+)'\] bound (\{[^}]*\})")
got, hits = {}, {}
for i, ln in enumerate(lines, 1):
    m = RX.search(ln)
    if m and m.group(1) in creates:
        b = ast.literal_eval(m.group(2))
        hits.setdefault(m.group(1), []).append(i)
        if b:
            got[str(b[max(b)])] = creates[m.group(1)]       # the create's own symbol is the LEAST negative (-45 W1 before -46 frame)
for k in creates:
    print("FACT create {0} class {1} STEPX lines {2}".format(k, creates[k], hits.get(k)), flush=True)
print("FACT uid->class {0}".format(json.dumps(got, sort_keys=True)), flush=True)
G = [0, 0, None]
ok1 = len(creates) == 9 and all(len(hits.get(k, [])) == 1 for k in creates) and len(got) == 9
print("GATE {0} | 9 creates, one STEPX line each, 9 bound uids".format("PASS" if ok1 else "FAIL"), flush=True)
made = json.load(open(os.path.join(B, "diag_c144_2_graph_plan.json"), encoding="utf-8"))["edits"]["made"]
ok2 = got == made
print("GATE {0} | uid->class == diag_c144_2_graph_plan.json edits.made | {1}".format("PASS" if ok2 else "FAIL", made), flush=True)
n = int(ok1) + int(ok2)
print(protocol.result_line(protocol.make_result(n, 2 - n, None if n == 2 else ("creates" if not ok1 else "made"), [])), flush=True)
sys.exit(0 if n == 2 else 1)
