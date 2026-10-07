# ---
# labview: none
# hardware: none
# ---
r"""diag_c144_2_elexp - card 144-a2-1 step 4 (OFFLINE, no LabVIEW; PD336(a), PD349): the EXPECTED Error List file of P4 session 3's adopted
file claudeDev\D1_ring_p4s03_20261007_202957.vi (282301ca), from its full measured read errorlist_D1_ring_p4s03_20261007_202957_20261007_203956.json
(55 items, --role final, diag_c144_2_el.log), in the form of errorlist_expected_D1_ring_p4s02_20261003_110001.json: its 51 P3b-2b entries
unchanged + the 2 session-boundary entries re-labelled to session 3's nodes (pred errorlist.fixed.detail_end: Local -49 'Num' = LRN4 #29720,
While cond -46 = W1 #16483) + 1 entry for the 2 new 'Shift Register: unwired from inside the loop' items (SR -27 = SL1 #29403, -36 = SD1
#29648). Also records the measured total in plan_ring_p4_s03v18_pred.json's errorlist block (measured_total, measured_from, expected_file,
checked), every other key unchanged. COPIED from tools/bench/prep_c143_3_s02.py (card 143-3) with names/pins/entries changed.
PREDICTION CONTRACT: R read has 55 items == n_reported; X compare(read items, new expected) -> extra [] missing []; T total 55 ==
  sum(counts) == pred predicted_total; P pred errorlist measured_total 55 recorded, other pred keys unchanged.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c144_2_elexp.log -- py -u tools/bench/diag_c144_2_elexp.py"""
import copy, hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                          # noqa: E731
READ = os.path.join(B, "errorlist_D1_ring_p4s03_20261007_202957_20261007_203956.json")
OLD = os.path.join(B, "errorlist_expected_D1_ring_p4s02_20261003_110001.json")
NEW = os.path.join(B, "errorlist_expected_D1_ring_p4s03_20261007_202957.json")
PP = os.path.join(B, "plan_ring_p4_s03v18_pred.json")
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p4s03_20261007_202957.vi"
VIM = "282301caba152e4d16640dae0611972e"
G, ARTS = {"pass": 0, "fail": 0, "first": None}, []


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)
    if not ok:
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
        sys.exit(1)


rd, old = J(READ), J(OLD)
items = rd["items"]
gate("R read has 55 items == n_reported; read file md5 488c6866", len(items) == 55 == rd.get("n_reported") and md5(READ) == "488c68660a0f68f3fb2792fab6463832",
     (len(items), rd.get("n_reported"), md5(READ)))
gate("V adopted file md5 282301ca", md5(VI) == VIM, md5(VI))
exp = []
relabel = {"localvariable": {"label": "Local Variable: This variable is not connected to anything. (LRN4 Local read #29720 'Num', created by s03 "
                                      "p4_lr_num_a, output unwired by design; replaces s02's #6902 which s03 action 1 wired)",
                             "cite": "PD349 rule, plan_ring_p4_s03v18_pred.json errorlist.fixed.detail_end local [-49 'Num']; bound -49 -> 29720 "
                                     "(diag_c143_p4s03v18_scratch.log:303)"},
           "whileloop": {"label": "While Loop: Conditional terminal is not wired (W1 While #16483 body #29699, created by s03 p4_w1; replaces s02's "
                                  "While #10170 cond #23246 which s03 action 1 wired)",
                         "cite": "PD349 rule, pred errorlist.fixed.detail_end cond [-46, -45, -48]; bound -45 -> 16483, -46 -> 29699 "
                                 "(diag_c143_p4s03v18_scratch.log:274)"}}
n_re = 0
for e in copy.deepcopy(old["expected"]):
    na = e.get("norm_all") or []
    if na and na[0] in relabel and "PD333(a)" in str(e.get("cite", "")):
        e.update(relabel[na[0]])
        n_re += 1
    exp.append(e)
gate("E the 2 session-boundary entries of s02 re-labelled (cite PD333(a))", n_re == 2, n_re)
exp.append({"norm_all": ["shiftregister", "unwiredfrominsidetheloop"], "count": 2,
            "label": "Shift Register: unwired from inside the loop (SL1 #29403 and SD1 #29648, added by s03 p4_sr_last / p4_sr_disc; inner sink "
                     "wired in a later session)",
            "cite": "PD349 SR class, pred errorlist.fixed.new_items [sr -27], [sr -36]; bound -27 -> 29403, -36 -> 29648 "
                    "(diag_c143_p4s03v18_scratch.log:223,247)"})
total = sum(int(e["count"]) for e in exp)
ex, mi, usage = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
p = J(PP)
gate("T total 55 == sum(counts) == pred predicted_total", total == 55 == p["errorlist"]["predicted_total"], (total, p["errorlist"]["predicted_total"]))
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 144-a2-1 (PD336(a), PD349): s02's 51 P3b-2b entries unchanged; its 2 session-boundary entries re-labelled to the "
                     "session-3 nodes the PD349 rule predicted; + 2 SR items predicted by the PD349 SR class",
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(OLD), "total": total, "expected": exp,
       "format_note": old.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
before = dict((k, json.dumps(v, sort_keys=True)) for k, v in p.items() if k != "errorlist")
el = dict(p["errorlist"])
el.update({"measured_total": 55, "measured_from": rel(READ), "measured_log": "tools/bench/diag_c144_2_el.log", "expected_file": rel(NEW),
           "checked": True, "measured_note": "read vs s02 expected: extra = 2 'Shift Register: unwired from inside the loop', missing 0; "
                                             "the cond/local new items take the licences of the 2 closed ones"})
p["errorlist"] = el
json.dump(p, open(PP, "w", encoding="utf-8"), indent=1)
q = J(PP)
gate("P pred errorlist measured_total 55 recorded, other keys unchanged",
     q["errorlist"]["measured_total"] == 55 and before == dict((k, json.dumps(v, sort_keys=True)) for k, v in q.items() if k != "errorlist"),
     {"plan_md5": q["plan"]["md5"], "pred_md5": md5(PP)})
ARTS.append({"path": rel(PP), "md5": md5(PP)})
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
