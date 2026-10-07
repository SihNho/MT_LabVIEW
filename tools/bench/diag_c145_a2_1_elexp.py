# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_1_elexp - card 145-a2-1 step 3 (OFFLINE, no LabVIEW; PD351(b)(e)): the EXPECTED Error List file of P4 session 4's adopted
file claudeDev\D1_ring_p4s04_20261007_215031.vi (95e408ff), FROM its full measured read errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json
(58 items, --role final, diag_c145_2_el.log, md5 5e53096a), in the form of errorlist_expected_D1_ring_p4s03_20261007_202957.json.
COPIED from tools/bench/diag_c144_2_elexp.py (card 144-a2-1) with names/pins/entries changed; unlike it, the pred is NOT written (card rule:
plan / pred unchanged). Entries: s03's 55 entries, minus the While-cond entry (pred closed [cond 29699]), the Local entry re-labelled to the
two new session-4 locals (pred new [local -51 -> #30001], [local -32 -> #30016]; one row reads with raw '' and the local/global detail text,
item 3), + 1 entry for the 3 'Index Array: Contains unwired or bad terminal' items (pred new [input -26 -> #29843], [-34 -> #29879],
[-53 -> #30002]). The 2 SubVI drops PS1 #29719 (-1) / SQ1 #29724 (-38) have NO item in the read (PD351(b)): no entry.
PREDICTION CONTRACT: R read has 58 items == n_reported, md5 5e53096a; V adopted file md5 95e408ff; X compare(read items, new expected)
  -> extra [] missing []; T total 58 == sum(counts); P pred/plan md5 unchanged.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c145_a2_1_elexp.log -- py -u tools/bench/diag_c145_a2_1_elexp.py"""
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
READ = os.path.join(B, "errorlist_D1_ring_p4s04_20261007_215031_20261007_220024.json")
OLD = os.path.join(B, "errorlist_expected_D1_ring_p4s03_20261007_202957.json")
NEW = os.path.join(B, "errorlist_expected_D1_ring_p4s04_20261007_215031.json")
PINS = {os.path.join(B, "plan_ring_p4_s04v18_pred.json"): "a2bbc8bf22da2892556dbcf94ef0b601",
        os.path.join(B, "plan_ring_p4_s04v18.json"): "f349c39a17330531e688ff1f70ce426e"}
VI = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_ring_p4s04_20261007_215031.vi"
VIM = "95e408ff14a406edd3f16b32ba7324f1"
LOGC = "diag_c144_p4s04v18_scratch.log"
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
gate("R read has 58 items == n_reported; read file md5 5e53096a", len(items) == 58 == rd.get("n_reported")
     and md5(READ) == "5e53096a3dd25d25141d111dbe2177b8", (len(items), rd.get("n_reported"), md5(READ)))
gate("V adopted file md5 95e408ff", md5(VI) == VIM, md5(VI))
exp, dropped, n_re = [], [], 0
for e in copy.deepcopy(old["expected"]):
    na = e.get("norm_all") or []
    if na and na[0] == "whileloop":
        dropped.append(e.get("label"))
        continue
    if na and na[0] == "localvariable":
        e.update({"label": "Local Variable: This variable is not connected to anything. (one of the two session-4 Local reads #30001 "
                           "(p4_lr_latest) / #30016 (p4_lr_num_b), output unwired by design; s03's #29720 is wired by s04 - which of the "
                           "two reads with this raw text is not measured)",
                  "cite": "PD349 rule, plan_ring_p4_s04v18_pred.json errorlist.fixed new [local -51] [local -32], closed [local 29720]; bound "
                          "-51 -> 30001, -32 -> 30016 ({0}:275,207)".format(LOGC)})
        n_re += 1
    exp.append(e)
gate("E s03 While-cond entry dropped (closed cond 29699), s03 Local entry re-labelled", len(dropped) == 1 and n_re == 1, (dropped, n_re))
exp.append({"norm_all": ["localorglobalvariableisnotwiredtoanything"], "count": 1,
            "label": "(raw '' on OCR) This local or global variable is not wired to anything - the OTHER session-4 Local read of #30001 / #30016 "
                     "(read item 3, empty row text, detail text only)",
            "cite": "PD349 rule, pred errorlist.fixed new [local -51] [local -32]; read item 3 of {0}".format(rel(READ))})
exp.append({"norm_all": ["indexarray", "containsunwiredorbadterminal"], "count": 3,
            "label": "Index Array 'Index Array': Contains unwired or bad terminal (IA #29843 p4_ia_img, #29879 p4_ia_n2, #30002 p4_ia_n2sink, "
                     "created by s04; index/array input wired in a later session)",
            "cite": "PD349 input class, pred errorlist.fixed new [input -26] [input -34] [input -53]; bound -26 -> 29843, -34 -> 29879, "
                    "-53 -> 30002 ({0}:169,223,291); read items 5, 6, 9".format(LOGC)})
total = sum(int(e["count"]) for e in exp)
ex, mi, usage = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read items, new expected): extra [] missing []", not ex and not mi, {"extra": ex, "missing": mi})
gate("T total 58 == sum(counts)", total == 58, total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 145-a2-1 (PD351(b)(e), PD349): s03's entries; While-cond entry dropped (closed); Local entry re-labelled to the "
                     "session-4 locals + 1 empty-raw local row; + 3 Index Array items. No entry for SubVI PS1 #29719 / SQ1 #29724 (no item read; "
                     "requiredness table tools/bench/diag_c145_a2_1_facts.md)",
       "measured_from": rel(READ), "measured_md5": md5(READ), "base_expected": rel(OLD), "total": total, "expected": exp,
       "format_note": old.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1)
ARTS.append({"path": rel(NEW), "md5": md5(NEW)})
gate("P plan / pred md5 unchanged", all(md5(p) == m for p, m in PINS.items()), dict((rel(p), md5(p)) for p in PINS))
print("FACT wrote {0} md5 {1} total {2} entries {3}".format(rel(NEW), md5(NEW), total, len(exp)), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], ARTS)), flush=True)
