# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_166-a1-2.md
# ---
r"""diag_c166_a1_2_elexp - card 166-a1-2 (OFFLINE, json only, no LabVIEW; PD354(a) record-only, PD403(a)): the Error List EXPECTED file of the
P5 final claudeDev\D1_ring_p5_20261010_172913.vi (75773b0d, byte-equal to D1_ring_p5s02e_20261010_172913.vi), written MECHANICALLY from its full
--role final read errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json (0c0664d8, 47 items), ITEM BY ITEM: every read item is cited to
its index in the read, through the predicted step-5 end errorlist_predicted_D1_ring_p5s02e_end.json (2a8e2984, 49) whose entries it licenses.
Found before writing: diag_c165_a3_4_elexp.py (card 165-3-4, never run) and diag_c164_a3_5_elexp.py do the same job; both carry inline copies
of norm_ocr (c165:43-47, c164:43-47 == tools/errorlist_check.py:331 norm_ocr) and elcls (c165:50-57, c164:50-57; no shared copy exists). This
script CALLS errorlist_check.compare / norm / class_counts (tools/errorlist_check.py:415,315,471) and prep_c156_a1_1_lib.Gate; it needs no
norm_ocr / elcls (no per-class prediction record here). The per-item citation is computed by calling compare() on growing prefixes of the read
(compare assigns items in order, first matching entry with count left, so prefix n's usage minus prefix n-1's names item n's entry): no matcher
logic is re-implemented.
Predicted entries licensing no read item are DROPPED and recorded with their clears_by (expected: item 4 w4337 'has no source', item 49 w9636
'While Loop to SubVI'; the plan's A70/A80 are A73/A84 in the predicted file's own cleared[] list, joined by action name).
PREDICTION CONTRACT: R items == n_reported == 47; V both VI names md5 75773b0d and the read's bed is the s02e name at that md5; S predicted md5
2a8e2984; D dropped predicted entries == items [4, 49] -> A73 w_k3f / A84 w_k4f; C every read item cited exactly once; X compare(read, new)
extra [] missing []; T total == 47. RECORD (no gate, PD354(a)): compare(read, predicted) extra 0 missing 2.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c166_a1_2_elexp.log -- py -u tools/bench/diag_c166_a1_2_elexp.py"""
import copy, json, os, sys                                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
import errorlist_check as EC                                                                # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
READ = os.path.join(B, "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")     # 0c0664d8
PRED = os.path.join(B, "errorlist_predicted_D1_ring_p5s02e_end.json")                       # 2a8e2984
VI = os.path.join(CD, "D1_ring_p5_20261010_172913.vi")                                      # the P5 final (bed name)
VI_READ = os.path.join(CD, "D1_ring_p5s02e_20261010_172913.vi")                             # its byte twin, the file the read opened
VIM = "75773b0ded2a08586bb1a542ddda5af6"
DROP_WANT = {4: 73, 49: 84}                                                                 # brief_166-a1-2.md:16 (item -> A)
NEW = os.path.join(B, "errorlist_expected_{0}.json".format(os.path.splitext(os.path.basename(VI))[0]))
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                                 # noqa: E731
gate = L.Gate(fatal_default=True)
print("FACT old {0}: {1}".format(rel(NEW), L.md5(NEW) if os.path.exists(NEW) else "absent"), flush=True)
rd, pr = L.J(READ), L.J(PRED)
items = rd["items"]
gate("R read {0}: items {1} == n_reported {2} == 47".format(rel(READ), len(items), rd.get("n_reported")),
     len(items) == rd.get("n_reported") == 47)
gate("V {0} and {1} md5 == {2}; read bed == the s02e name at that md5".format(os.path.basename(VI), os.path.basename(VI_READ), VIM[:8]),
     L.md5(VI) == L.md5(VI_READ) == VIM and os.path.basename(str(rd.get("bed"))) == os.path.basename(VI_READ) and rd.get("bed_md5_before") == VIM,
     (L.md5(VI), L.md5(VI_READ), rd.get("bed"), rd.get("bed_md5_before")))
gate("S predicted md5 2a8e2984, read md5 0c0664d8", L.md5(PRED).startswith("2a8e2984") and L.md5(READ).startswith("0c0664d8"),
     (L.md5(PRED), L.md5(READ)))
pexp = pr["expected"]
ext, mis, usage = EC.compare(copy.deepcopy(items), pexp)
print("RECORD compare(read 0c0664d8, predicted 2a8e2984): extra {0} {1} | missing {2} (PD354(a): record, not a gate)".format(
      len(ext), ext, len(mis)), flush=True)
# per-item citation: entry index of item n = the entry whose usage grows from prefix n-1 to prefix n
cite_of, prev = {}, [0] * len(pexp)
for n in range(1, len(items) + 1):
    _e, _m, u = EC.compare(copy.deepcopy(items[:n]), pexp)
    cur = [x["used"] for x in u[:len(pexp)]]
    grew = [k for k in range(len(pexp)) if cur[k] != prev[k]]
    if grew:
        cite_of[items[n - 1].get("index", n - 1)] = grew[0] if len(grew) == 1 else None
    prev = cur
full = copy.deepcopy(items)
EC.compare(full, pexp)
headers = [it.get("index") for it in full if str(it.get("licensed_by") or "").startswith("header-of")]
# predicted-file line numbers, read mechanically for the citations
plines = open(PRED, encoding="utf-8").read().splitlines()
pname = rel(PRED)


def line_of(text, start=0):
    return next((i + 1 for i in range(start, len(plines)) if text in plines[i]), None)


a_by_action = {}
for c in pr.get("cleared") or []:
    a_by_action.setdefault(c.get("action"), []).append(c.get("A"))
exp, dropped = [], []
for k, (e, u) in enumerate(zip(pexp, usage)):
    idx = sorted(i for i, kk in cite_of.items() if kk == k)
    if u["used"] == 0:
        cb = e.get("clears_by") or {}
        act = str(cb.get("action") or "")
        name = act.split()[-1] if act else None
        li = line_of('"item": {0},'.format(e.get("item")), line_of('"expected": [') or 0)
        la = line_of('"action": "{0}"'.format(act), li or 0) if act else None
        lc = line_of('"action": "{0}"'.format(name)) if name else None
        dropped.append({"item": e.get("item"), "class": e.get("class"), "label": e.get("label"), "object": e.get("object"),
                        "plan_action": act, "cleared_by_A": a_by_action.get(name), "action": name,
                        "cite": "{0}:{1} (entry), :{2} (clears_by.action {3!r}), :{4} (cleared[] action {5!r} -> A{6}); PD403(a)".format(
                            pname, li, la, act, lc, name, a_by_action.get(name))})
        continue
    ne = copy.deepcopy(e)
    ne["count"] = u["used"]
    ne["read_index"] = idx
    ne["cite"] = "read {0} item(s) {1} (licensed by predicted entry item {2}); predicted: {3}".format(rel(READ), idx, e.get("item"), e.get("cite"))
    exp.append(ne)
for raw in ext:                                                                             # read items no predicted entry licenses (expected none)
    it = next((i for i in items if i.get("raw") == raw), {})
    exp.append({"norm_all": [EC.norm(raw) or EC.norm(it.get("detail"))], "count": 1, "read_index": [it.get("index")],
                "label": "{0} (measured, not predicted)".format(raw), "cite": "read {0} item {1}; no predicted entry licenses it".format(rel(READ), it.get("index"))})
for d in dropped:
    print("FACT dropped predicted item {0} ({1}) {2!r}: {3}".format(d["item"], d["class"], d["label"], d["cite"]), flush=True)
got = dict((d["item"], (d["cleared_by_A"] or [None])[0]) for d in dropped)
gate("D dropped predicted entries == items [4, 49] cleared by A73 / A84 (cleared[] by action name)",
     got == DROP_WANT and all(len(d["cleared_by_A"] or []) == 1 for d in dropped), got)
cited = sorted(i for e in exp for i in e["read_index"]) + sorted(headers)
gate("C every read item cited exactly once (47 indices 0..46; headers {0})".format(headers),
     cited == sorted(it.get("index") for it in items) and len(set(cited)) == len(items) and None not in cite_of.values(),
     {"cited": len(cited), "ambiguous": [i for i, k in cite_of.items() if k is None]})
ex2, mi2, _ = EC.compare(copy.deepcopy(items), exp)
gate("X compare(read, new expected): extra [] missing []", not ex2 and not mi2, {"extra": ex2, "missing": mi2})
total = sum(int(e["count"]) for e in exp)
gate("T total {0} == 47 read items".format(total), total == len(items) == 47, total)
out = {"schema": "errorlist-expected/1", "bed": VI, "bed_md5": VIM,
       "decided_by": "card 166-a1-2 (docs/d1/ring-p5c.md PD403(a), PD354(a)): the predicted P5-2 step-5 end's entries, each with the read items it "
                     "licenses (read_index); predicted entries licensing none dropped (see cleared); written by tools/bench/diag_c166_a1_2_elexp.py",
       "measured_from": rel(READ), "measured_md5": L.md5(READ), "measured_bed": rd.get("bed"),
       "base_expected": {"path": pname, "md5": L.md5(PRED), "total": pr.get("total")},
       "compare_with_base": {"extra": len(ext), "missing": len(mis), "note": "record only (PD354(a)); missing = the dropped entries below"},
       "cleared": dropped, "total": total, "expected": exp, "format_note": pr.get("format_note")}
json.dump(out, open(NEW, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("FACT wrote {0} md5 {1} total {2} entries {3} dropped {4}".format(rel(NEW), L.md5(NEW), total, len(exp), len(dropped)), flush=True)
print("RECORD class counts of the read: {0}".format(json.dumps(EC.class_counts(items))), flush=True)
sys.exit(gate.result([{"path": rel(NEW), "md5": L.md5(NEW)}]))
