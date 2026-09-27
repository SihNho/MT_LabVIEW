r"""selftest_d4_l2b2a - card 112-4 R0: the offline test of rule D4 (stagekit.d4_load / d4_e1 / d4_pb / d4_form). No LabVIEW,
no COM call, no .vi read; stagekit is imported only for its pure D4 functions.

PREDICTION (every case is a gate):
  T0  d4_load reads S1's graph docs/wiki/subvi/D1_s1_copy.json (md5 5de014fe...) and finds names on all 8 scope nodes; S1's
      #8741 and #30331 carry 'disabled index (col)' (review c112c-b2a-e1 s2(C)); a WRONG md5 pin leaves `names` empty.
  T1  112-3's REAL diffs, parsed from tools/bench/stage_d1_l2b2a.log (md5 c5e5e81c, the RECORD STEP-DIFF lines :96/:119):
      ck4 (#8741 x2) and ck7 (#8741 x2 + #30331 x2) PASS D4, 6 accepted terms, 0 bad.
  T2  the same ck4 diff with the name set to 'index (col)' (a name S1's #8741 does not have) FAILS.
  T2b/T9b COUNT (prior-art c112d): a THIRD 'disabled index (col)' on #8741 (S1 has 2) FAILS at E1 and at PB.
  T3  a real-only term on #2626 'array' (off scope; S1 has 'array' there) FAILS.
  T4  a real-lost term (only_sim_terms) FAILS; T5 an edge difference FAILS; T5b a dangling-only difference FAILS.
  T6  PB, S1-form end built from the base graph's #8741/#30331 rows (renames index->index (row), element->subarray, +2
      'disabled index (col)' each) with the planned open pairs of those nodes CLOSED: PASS, closed == those pairs.
  T7  PB with one NEW pair FAILS; T8 a closed pair off scope FAILS; T9 a grown non-S1 name on #8741 FAILS; T10 a real-lost
      uid FAILS; T11 the unchanged end (got == want, real == sim) PASSES with nothing closed or grown.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_d4_l2b2a.log -- py -u tools/bench/selftest_d4_l2b2a.py"""
import copy
import importlib
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)
K = importlib.import_module("stagekit")
import protocol as PR                                                               # noqa: E402

LOG, LOG_MD5 = os.path.join(HERE, "stage_d1_l2b2a.log"), "c5e5e81c3dc2f22c9476687ede27b7e2"   # card 112-4 inputs[3]
D4P = os.path.join(HERE, "plan_l2b2a_d4.json")
passes, fails = [], []


def mask(x):
    return str(x).replace("===", "---").replace("FAIL", "F&IL").replace("fail", "f&il")


def gate(label, ok, detail=""):
    (passes if ok else fails).append(label)
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, mask(detail)[:400]), flush=True)


D4 = K.d4_load(D4P)
gate("T0a S1 md5 matches the pin and names were read on all 8 scope nodes", D4["s1_md5_got"] == D4["s1"]["md5"]
     and sorted(D4["names"]) == sorted(D4["scope"]) and len(D4["scope"]) == 8, (D4["s1_md5_got"], sorted(D4["names"])))
for n in sorted(D4["scope"]):
    print("  FACT  S1 names on #{0}: {1}".format(n, sorted(D4["names"].get(n, {}).items())), flush=True)
gate("T0b S1's #8741 and #30331 carry 'disabled index (col)', and #8741 has no 'index (col)'",
     all("disabled index (col)" in D4["names"].get(n, {}) for n in (8741, 30331)) and "index (col)" not in D4["names"].get(8741, {}))
bad_pin = os.path.join(os.environ.get("TEMP", HERE), "d4_badpin_selftest.json")
dd = json.load(open(D4P, encoding="utf-8"))
dd["s1"]["md5"] = "0" * 32
json.dump(dd, open(bad_pin, "w", encoding="utf-8"))
wrong = K.d4_load(bad_pin)
os.remove(bad_pin)
gate("T0c a WRONG S1 md5 pin leaves names EMPTY (the recipe's L0b then refuses)", wrong["names"] == {} and wrong["s1_md5_got"] != "0" * 32)

# ---- T1: the recorded 112-3 diffs, parsed from the log (never re-typed)
got_md5 = K.md5(LOG)
diffs, info = [], {}
if got_md5 == LOG_MD5:
    for m in re.finditer(r"RECORD STEP-DIFF STEP-DIFF after real op (\d+) \(connect, plan actions \[\d+\] \[[^\]]*\]\): (\{.*\})\s*$",
                         open(LOG, encoding="utf-8").read(), re.M):
        d = json.loads(m.group(2))
        diffs.append((int(m.group(1)), d))
        info.update((int(t), (int(w[0]), w[2])) for t, w in d.get("who", {}).items())
gate("T1a the 112-3 log is the recorded one (md5 {0}) and holds 2 step diffs at ck 4 and 7".format(LOG_MD5), got_md5 == LOG_MD5
     and [k for k, _d in diffs] == [4, 7], (got_md5, [k for k, _d in diffs]))
ok, acc, bad = K.d4_e1(diffs, info, D4)
for k, t, n, nm in acc:
    print("  FACT  D4-ACCEPT ck {0} term t{1} node #{2} name {3!r} in-S1 yes".format(k, t, n, nm), flush=True)
gate("T1b 112-3's ck4/ck7 diffs PASS D4: 6 accepted (#8741 x2 at ck4; #8741 x2 + #30331 x2 at ck7), 0 bad",
     ok and len(acc) == 6 and not bad and sorted(set(a[2] for a in acc)) == [8741, 30331], (ok, len(acc), bad))


def e1(d, inf):
    return K.d4_e1([(4, d)], inf, D4)


d4c = copy.deepcopy(diffs[0][1]) if diffs else {"only_real_terms": [25829]}
i2 = dict(info)
i2[25829] = (8741, "index (col)")
gate("T2 a real-only term whose (node, name) S1 lacks ('index (col)' on #8741) FAILS", not e1(d4c, i2)[0], e1(d4c, i2)[2])
i3 = dict(info)
i3[99002] = (8741, "disabled index (col)")
d7 = copy.deepcopy(diffs[-1][1]) if diffs else {"only_real_terms": []}
d7["only_real_terms"] = list(d7["only_real_terms"]) + [99002]
gate("T2b COUNT (prior-art c112d discriminating test): ck7's diff plus a THIRD 'disabled index (col)' on #8741 (S1 has 2) FAILS",
     not e1(d7, i3)[0], e1(d7, i3)[2])
gate("T3 a real-only term off scope (#2626 'array') FAILS", not e1({"only_real_terms": [99001]}, {99001: (2626, "array")})[0])
gate("T4 a real-lost term (only_sim_terms) FAILS", not e1({"only_sim_terms": [25829]}, info)[0])
gate("T5 an edge difference FAILS", not e1({"only_real_edges": [[1, 2]]}, info)[0])
gate("T5b a dangling-only difference FAILS (D4: anything else fails)", not e1({"dangling_real_only": [25829]}, info)[0])

# ---- T6..T11: PB on rows taken from the base graph (the B1 bed), transformed to S1 form for #8741/#30331
P = json.load(open(os.path.join(HERE, "plan_l2b2a.json"), encoding="utf-8"))
BASE = json.load(open(os.path.join(ROOT, P["finalized"]["base"]["path"]), encoding="utf-8"))
sim = [r for r in BASE["terminals"]]
want = set((int(y["node"]), y["term"]) for y in P["open_rows"])
REN = {"index": "index (row)", "element": "subarray"}
real, nid = [], 990000
for r in sim:
    x = dict(r)
    if int(r["owner_uid"]) in (8741, 30331) and r["term_name"] in REN:
        x["term_name"] = REN[r["term_name"]]
    real.append(x)
for n in (8741, 30331):
    for _i in range(2):
        nid += 1
        real.append({"term_uid": nid, "term_name": "disabled index (col)", "is_source": False, "wire_uid": 0, "owner_uid": n,
                     "owner_class": "IndexArray", "frame_diagram": 0, "term_class": "Terminal"})
print("  FACT  base #8741 names {0}".format(sorted(r["term_name"] for r in sim if int(r["owner_uid"]) == 8741)), flush=True)
cl = set(p for p in want if p[0] in (8741, 30331))
got = want - cl
ok, closed, grown, bad = K.d4_pb(got, want, real, sim, D4)
for p, c in grown:
    print("  FACT  D4-PB-GROWN #{0} {1!r} x{2}".format(p[0], p[1], c), flush=True)
for n, v in sorted(K.d4_form(real, D4).items()):
    print("  FACT  S1-FORM #{0}: {1}".format(n, v), flush=True)
gate("T6 PB: S1-form #8741/#30331 with their {0} planned pairs CLOSED PASSES, closed == those pairs".format(len(cl)),
     ok and set(closed) == cl and len(cl) == 6 and grown, (ok, closed, bad))
gate("T6b d4_form calls #8741 and #30331 'equal to S1' in that constructed end (the facts-only reading)",
     all(K.d4_form(real, D4)[n].startswith("equal to S1") for n in (8741, 30331)), K.d4_form(real, D4))
gate("T7 PB with one NEW pair FAILS", not K.d4_pb(got | {(8741, "array")}, want, real, sim, D4)[0])
gate("T8 PB with a closed pair OFF scope (#2626 'array') FAILS", not K.d4_pb(got - {(2626, "array")}, want, real, sim, D4)[0])
r9 = real + [{"term_uid": 995001, "term_name": "index (col)", "owner_uid": 8741}]
gate("T9 PB with a grown non-S1 name on #8741 ('index (col)') FAILS", not K.d4_pb(got, want, r9, sim, D4)[0], K.d4_pb(got, want, r9, sim, D4)[3])
r9b = real + [{"term_uid": 995002, "term_name": "disabled index (col)", "owner_uid": 8741}]
gate("T9b COUNT: PB with a THIRD 'disabled index (col)' on #8741 (S1 has 2) FAILS", not K.d4_pb(got, want, r9b, sim, D4)[0],
     K.d4_pb(got, want, r9b, sim, D4)[3])
r10 = [r for r in real if int(r["term_uid"]) != int(next(r["term_uid"] for r in sim if int(r["owner_uid"]) == 8741))]
gate("T10 PB with a real-lost uid on #8741 FAILS", not K.d4_pb(got, want, r10, sim, D4)[0])
ok11 = K.d4_pb(want, want, sim, sim, D4)
gate("T11 PB unchanged end (got == want, real == sim) PASSES with nothing closed or grown", ok11[0] and not ok11[1] and not ok11[2], ok11[3])

print("\n" + "=" * 90)
print("=== GATES: {0} pass / {1} fail".format(len(passes), len(fails)))
print(PR.result_line(PR.make_result(len(passes), len(fails), fails[0] if fails else None)), flush=True)
sys.exit(1 if fails else 0)
