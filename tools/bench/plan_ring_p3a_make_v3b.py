r"""plan_ring_p3a_make_v3b - card 124-8 STEP 1 (offline, no LabVIEW; brief_124-8.md decision): the v3 plan input with ONE kind of change -
every terminal that a created node DECLARES gets an explicit term_class taken from a MEASURED terminal table, cited in the action's
`why`. Cause it fixes: 124-7's scratch stopped at op 1 on BINDING sim ('Terminal', ...) vs real ('ParameterTerminal', ...) for
Wait (ms) (stage_d1_ring_p3a_scratch_pin.log:65-71) because plan_ring_p3a_in_v3.json:28-37 left term_class undeclared and
stagesim.py:1317 defaults it to 'Terminal'. stagesim.py is NOT edited (other plans rely on its default).
The output keeps the NAME plan_ring_p3a_in_v3.json (the recipe's L0 gate keys on that name, stage_d1_ring_p3a.py:32 - not edited);
the v3 file as written by plan_ring_p3a_make_v3.py is first copied to plan_ring_p3a_in_v3_pre124_8.json (md5 65a6c3ba).
MEASURED SOURCES (no class is assumed):
  Wait (ms)  : the real table of the node 124-7 created from the same donor (OpWaitDonor_v0 #163) - parsed from the FAIL line of
               stage_d1_ring_p3a_scratch_pin.log ('vs real {...}'), both ParameterTerminal.
  Equal? / Increment / Quotient & Remainder : the rows of their $work donors #10019 / #1978 / #2136 in the plan's own base graph
               tools/bench/graph_ring_p2b_20261001_154542.json (LabVIEW-read, md5 69b23e08), matched by (name, direction).
  const_donor DigitalNumericConstant (KP1/KC1/K20): every DigitalNumericConstant row of that base graph (one class, else FAIL).
PRIOR ART: plan_ring_p3a_make_v3.py (v3 itself), stagexec.bind_new:756-764 (the BINDING key this feeds).
PREDICTION: 7 created actions with declared terminals, 14 terminals classed (first run said 6/13: an arithmetic slip, M5's per-action list held) (Wait 2 P, Equal? 3 P, Inc 1 OverridableP + 1 P, Q&R 4 P,
3 constants Terminal); v3b == v3 except those term_class keys and their why; pred file untouched (md5 152bd4d6).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/plan_ring_p3a_make_v3b.log -- py -u tools/bench/plan_ring_p3a_make_v3b.py"""
import ast, copy, hashlib, json, os, shutil, sys                                    # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()  # noqa: E731
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:900]), flush=True)


V3, PRE = os.path.join(B, "plan_ring_p3a_in_v3.json"), os.path.join(B, "plan_ring_p3a_in_v3_pre124_8.json")
PRED, PINLOG = os.path.join(B, "plan_ring_p3a_pred.json"), os.path.join(B, "stage_d1_ring_p3a_scratch_pin.log")
V3_MD5, PRED_MD5 = "65a6c3baee706bbd0b3bb886efe9d72f", "152bd4d66cfc426e32219d3711d2917e"
if not os.path.exists(PRE) and md5(V3) == V3_MD5:
    shutil.copyfile(V3, PRE)
gate("M0 inputs: pre-124-8 v3 md5 65a6c3ba, pred md5 152bd4d6, scratch pin log md5 df268b51",
     os.path.exists(PRE) and md5(PRE) == V3_MD5 and md5(PRED) == PRED_MD5 and md5(PINLOG) == "df268b51756ef874d181f394042c067e",
     (os.path.exists(PRE) and md5(PRE), md5(PRED), md5(PINLOG)))
v3 = json.load(open(PRE, encoding="utf-8"))
GF = os.path.join(ROOT, v3["base"]["path"])
gate("M1 base graph md5 == plan base md5", md5(GF) == v3["base"]["md5"], (v3["base"], md5(GF)))
rows = json.load(open(GF, encoding="utf-8"))["terminals"]

# --- measured tables -------------------------------------------------------------------------------------------------
lines = open(PINLOG, encoding="utf-8", errors="replace").read().splitlines()
fl = [(i + 1, ln) for i, ln in enumerate(lines) if ln.startswith("  FAIL  E1") and "vs real " in ln]
wait = {}
if fl:
    real = ast.literal_eval(fl[0][1].split("vs real ", 1)[1].strip())
    wait = dict(((n, s), c) for (c, s, n) in real)
gate("M2 Wait (ms) real table parsed from the scratch pin log FAIL line", len(wait) == 2, {"line": fl and fl[0][0], "table": wait})
MEAS = {"Wait (ms)": (wait, "stage_d1_ring_p3a_scratch_pin.log:{0} (real #26747, same donor)".format(fl and fl[0][0]))}
for prim, du in (("Equal?", 10019), ("Increment", 1978), ("Quotient & Remainder", 2136)):
    t = dict(((r["term_name"], bool(r["is_source"])), r["term_class"]) for r in rows if r["owner_uid"] == du)
    MEAS[prim] = (t, "{0} donor #{1} rows (term_uids {2})".format(os.path.basename(GF), du,
                                                                  sorted(r["term_uid"] for r in rows if r["owner_uid"] == du)))
dnc = sorted(set(r["term_class"] for r in rows if r["owner_class"] == "DigitalNumericConstant"))
ndnc = sum(1 for r in rows if r["owner_class"] == "DigitalNumericConstant")
gate("M3 base graph DigitalNumericConstant rows carry ONE term_class", len(dnc) == 1, {"classes": dnc, "rows": ndnc})
CONST = (dnc[0] if len(dnc) == 1 else None, "{0}: all {1} DigitalNumericConstant rows {2}".format(os.path.basename(GF), ndnc, dnc))

# --- apply -----------------------------------------------------------------------------------------------------------
v3b = copy.deepcopy(v3)
done, miss = [], []
for a in v3b["actions"]:
    if a.get("op") != "create" or not a.get("terminals"):
        continue
    if a.get("prim") == "const_donor" and a.get("class") == "DigitalNumericConstant":
        tab, cite = dict(((t["name"], bool(t["is_source"])), CONST[0]) for t in a["terminals"]), CONST[1]
    elif a.get("prim") in MEAS:
        tab, cite = MEAS[a["prim"]]
    else:
        miss.append((a["id"], a.get("prim"), "no measured table"))
        continue
    cls = []
    for t in a["terminals"]:
        c = tab.get((t["name"], bool(t["is_source"])))
        if not c:
            miss.append((a["id"], t["name"], t["is_source"]))
            continue
        t["term_class"] = c
        cls.append(c)
        done.append((a["id"], t["name"], c))
    if len(tab) != len(a["terminals"]):
        miss.append((a["id"], "declared {0} vs measured {1} terminals".format(len(a["terminals"]), len(tab))))
    a["why"] = (a["why"] + " | term_class (card 124-8): " + cite)[:300]
gate("M4 every declared terminal of every created node classed from a measured table, counts equal", not miss and len(done) == 14,
     {"done": done, "miss": miss})
want = {"p3a_wait": ["ParameterTerminal"] * 2, "p3a_eq": ["ParameterTerminal"] * 3,
        "p3a_inc": ["OverridableParameterTerminal", "ParameterTerminal"], "p3a_qr": ["ParameterTerminal"] * 4,
        "p3a_k_prev": ["Terminal"], "p3a_k_cnt": ["Terminal"], "p3a_k20": ["Terminal"]}
got = dict((a["id"], [t.get("term_class") for t in a["terminals"]]) for a in v3b["actions"] if a.get("op") == "create" and a.get("terminals"))
gate("M5 classes per action == the prediction", got == want, got)
strip = lambda p: [dict((k, ([dict((kk, vv) for kk, vv in t.items() if kk != "term_class") for t in v] if k == "terminals" else v))  # noqa: E731
                        for k, v in a.items() if k != "why") for a in p["actions"]]
gate("M6 v3b == v3 except term_class keys and why; 25 actions; base/open_rows identical",
     strip(v3b) == strip(v3) and len(v3b["actions"]) == 25 and v3b["base"] == v3["base"] and v3b["open_rows"] == v3["open_rows"]
     and max(len(a["why"]) for a in v3b["actions"]) <= 300, [len(a["why"]) for a in v3b["actions"]])
if all(c for _n, c in ok):
    json.dump(v3b, open(V3, "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_ring_p3a_in_v3.json md5 {0} (pre-124-8 copy {1})".format(md5(V3), os.path.basename(PRE)), flush=True)
gate("M7 pred file untouched", md5(PRED) == PRED_MD5, md5(PRED))
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
