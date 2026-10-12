# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_166-a1-3.md
# ---
r"""diag_c166_a1_3_replay - card 166-a1-3 (OFFLINE, json only): the stored ring-step PREDICTED Error Lists re-made with the shared predictor
tools/elpredict.py (rules 1 + 2, PD403(d)(2)) from their stored inputs, written ONLY under tools/bench/diag_c166_a1_3_replay/ and compared with
the stored files (never overwritten). Inputs are the makers' CFG values, restated as data (the makers run on import):
  s02b <- prep_c160_c3_1_el.py:33-37 (inline MERGE flow, not the lib)   s02c <- prep_c163_a1_3_el.py:33-38 (inline flow)
  s02d <- prep_c164_a3_6_el.py:16-28 (lib flow)                         s02e <- elpredict.STEP5_CFG == prep_c165_a3_3_el.py:17-40 (lib flow)
  p5s01a / p5s01b / p5s02a: their preds carry errorlist.item_file None (no item-wise prediction was stored) - listed, not re-made.
Per step: byte-equal, or every differing item listed (item, uid, class, old -> new, reason) + the top-level keys whose values differ; a
difference that moves the total AWAY from the adopted read of that step is a RETURN (gate fails). Step 5: the literal acceptance - total 47,
compare(the adopted read 0c0664d8, the re-made entries) missing 0 extra 0 (and against the P5 final's expected file if card 166-a1-2 wrote it).
PREDICTION CONTRACT: s02d byte-equal; s02e differs only by items 4 / 49 CLEARED (rule 1, tunnel-linked too), total 49 -> 47, 0/0 vs the read;
s02b / s02c (other flows) item sets equal to the stored files (format keys differ); every stored file md5 unchanged.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c166_a1_3_replay.log -- py -u tools/bench/diag_c166_a1_3_replay.py"""
import copy, glob, json, os, sys                                                           # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import elpredict as EP                                                                      # noqa: E402
import errorlist_check as EC                                                                # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402
md5, rel, J = L.md5, L.rel, L.J
B = os.path.join(ROOT, "tools", "bench")
OUTD = os.path.join(B, "diag_c166_a1_3_replay")
os.makedirs(OUTD, exist_ok=True)
b = lambda n: os.path.join(B, n)                                                            # noqa: E731
g = L.Gate(width=900, fatal_default=False)
S02B_SESS = J(b("prep_c160_b3_1_session.json"))
_pos = dict((e["id"], e["pos"]) for e in (S02B_SESS.get("merge") or []) + (S02B_SESS.get("stubs") or []))
_acts = [a["id"] for a in J(b("plan_ring_p5s02b.json"))["actions"]]
A0B = sorted(set(_pos[i] - _acts.index(i) for i in _pos if i in _acts))
print("FACT s02b A0 from the session table positions: {0} (not A0 + index; min used - A labels only, items unaffected)".format(A0B), flush=True)
CFGS = [
    ("s02b", b("errorlist_predicted_D1_ring_p5s02b_end.json"), b("errorlist_expected_D1_ring_p5s02b_20261010_105511.json"),
     {"PLAN": b("plan_ring_p5s02b.json"), "SESS": b("prep_c160_b3_1_session.json"), "EXPF": b("errorlist_expected_D1_ring_p5s02a_20261010_023239.json"),
      "PINS": {b("errorlist_expected_D1_ring_p5s02a_20261010_023239.json"): "1fd016bf", b("plan_ring_p5s02b.json"): "f4520b10",
               b("prep_c160_b3_1_session.json"): "e5279899", b("graph_ring_p5s02a_20261010_032547.json"): "7ac24924"},
      "A0": min(A0B), "N_REB": 2, "STEP_TXT": "P5-2 step 2, plan_ring_p5s02b.json", "CARD": "160-c3-1 (docs/d1/ring-p5b.md PD389(d), PD391(d)(e))",
      "MAKER": "tools/bench/prep_c160_c3_1_el.py", "ELR_SPAN": "step_00 -> step_20",
      "UNPRED_WHY": {"reb": "PD391(c)(e) new structure class (re-made by elpredict; the stored maker kept only the groups onto a BASE RightShiftRegister)",
                     "delobj": "no delete_object row in this plan"}}),
    ("s02c", b("errorlist_predicted_D1_ring_p5s02c_end.json"), b("errorlist_expected_D1_ring_p5s02c_20261010_125755.json"),
     {"PLAN": b("plan_ring_p5s02c.json"), "SESS": b("prep_c163_a1_2_session.json"), "EXPF": b("errorlist_expected_D1_ring_p5s02b_20261010_105511.json"),
      "PINS": {b("errorlist_expected_D1_ring_p5s02b_20261010_105511.json"): "60e02787", b("plan_ring_p5s02c.json"): "930699ec",
               b("prep_c163_a1_2_session.json"): "e8daf1fe", b("graph_ring_p5s02b_20261010_111905.json"): "431cfd83"},
      "A0": 41, "N_REB": 2, "STEP_TXT": "P5-2 step 3, plan_ring_p5s02c.json, group I A41..A52", "CARD": "163-a1-3 (docs/d1/ring-p5b.md PD396(d))",
      "MAKER": "tools/bench/prep_c163_a1_3_el.py", "ELR_SPAN": "step_00 -> step_12",
      "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR CS7): on step 2 the same verb "
                            "(A32 / A39) left +2 'Wire has loose ends.' items the read cannot attribute by uid (diag_c162_a1_2_facts.md; PD396(a)(2)); "
                            "whether this group leaves one is not decidable offline - the step-3 scratch measures it",
                     "delobj": "no delete_object row in this plan"}}),
    ("s02d", b("errorlist_predicted_D1_ring_p5s02d_end.json"), b("errorlist_expected_D1_ring_p5s02d_20261010_152518.json"),
     {"PLAN": b("plan_ring_p5s02d.json"), "SESS": b("prep_c164_a3_6_session.json"), "EXPF": b("errorlist_expected_D1_ring_p5s02c_20261010_125755.json"),
      "PINS": {b("errorlist_expected_D1_ring_p5s02c_20261010_125755.json"): "26d45c71", b("plan_ring_p5s02d.json"): "97837e2a",
               b("graph_ring_p5s02c_20261010_131658.json"): "3d5196ab"}, "A0": 53, "N_REB": 2,
      "STEP_TXT": "P5-2 step 4, groups J (P4 delete form) + K3 A53..A71", "CARD": "164-3-6 (docs/d1/ring-p5c.md PD397(d), PD398, PD399)",
      "MAKER": "tools/bench/prep_c164_a3_6_el.py", "ELR_SPAN": "step_00 -> step_19 of tools/bench/sim/ring_p5s02d",
      "UNPRED_WHY": {"reb": "connect_term_uid register_end_case_border (tunnel + register face through the case border, new SR SK3): step 2's same verb "
                            "left +2 'Wire has loose ends.' items (diag_c162_a1_2_facts.md), step 3's left none (diag_c163_a2_2_facts.md:31); not "
                            "decidable offline - the step-4 scratch measures it",
                     "delobj": "delete_object of an object that still carries a wire in the sim pre-state (PD399(a): w23519 keeps its source t8494 and "
                               "sinks t23450 / t23241 / t7606; the next row wire_remove_loose_ends w23519 removes the stub): whether LabVIEW leaves a "
                               "loose-end item at step end is outside tools/elrule.py's classes (L / C / SR / A); the step-4 scratch measures it"}}),
    ("s02e", b("errorlist_predicted_D1_ring_p5s02e_end.json"), None, dict(EP.STEP5_CFG)),
]
READ5 = b("errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")
STORED = [c[1] for c in CFGS] + [READ5] + [b("plan_ring_%s_pred.json" % s) for s in ("p5s01a", "p5s01b", "p5s02a")]
before = dict((p, md5(p)) for p in STORED)


def adopted_total(nexp):
    """Total of the adopted read of a step = the next bed's expected file's read (its measured_from), or the stored step-5 read."""
    if nexp is None:
        return len(J(READ5)["items"]), rel(READ5)
    ex = J(nexp)
    return len(J(ex["measured_from"])["items"]), ex["measured_from"]


def status(d):
    """{item: 'CLEARED by <action> (<how>)' | 'STANDING'} over the base expected rows of a predicted file."""
    cl = dict((e["item"], e) for e in d.get("cleared") or [])
    return dict((r.get("item"), "CLEARED by {0} ({1})".format(cl[r.get("item")]["action"], cl[r.get("item")]["how"]) if r.get("item") in cl else "STANDING")
                for r in J(d["base_expected"]["path"])["expected"])


for tag, stored, nexp, cfg in CFGS:
    out_path = os.path.join(OUTD, os.path.basename(stored))
    cfg = dict(cfg, OUT=out_path)
    print("=== {0}: re-make {1} -> {2}".format(tag, rel(stored), rel(out_path)), flush=True)
    rc, new, _t = EP.predict(cfg, L.Gate(width=600, fatal_default=False))
    old = J(stored)
    same = md5(out_path) == md5(stored)
    ot, nt = old.get("total"), new.get("total")
    adt, adf = adopted_total(nexp)
    so, sn = status(old), status(new)
    diff_items = sorted((k for k in set(so) | set(sn) if (so.get(k) or "").split(" ")[0] != (sn.get(k) or "").split(" ")[0]), key=str)
    rows = dict((r.get("item"), r) for r in J(old["base_expected"]["path"])["expected"])
    oset = sorted((r.get("item") for r in old["expected"]), key=str)
    nset = sorted((r.get("item") for r in new["expected"]), key=str)
    keys = sorted(k for k in set(old) | set(new) if old.get(k) != new.get(k))
    print("FACT {0}: predict rc {1}; bytes {2} (stored {3} / re-made {4}); total stored {5} re-made {6}; adopted read {7} = {8} items; "
          "entries equal {9}; top-level keys that differ {10}".format(tag, rc, "EQUAL" if same else "DIFFER", md5(stored)[:8], md5(out_path)[:8], ot, nt, adf, adt,
                                                                       oset == nset, keys), flush=True)
    for k in diff_items:
        r = rows.get(k) or {}
        print("FACT {0} ITEM {1} uid {2} class {3}: {4} -> {5}".format(tag, k, (r.get("object") or {}).get("uid"), r.get("class"), so.get(k), sn.get(k)), flush=True)
    away = abs(nt - adt) > abs(ot - adt)
    g("{0} re-made: rc {1}; bytes {2} or every differing item listed ({3} item(s): {4}); total {5} -> {6} vs adopted {7}: {8}".format(
      tag, rc, "EQUAL" if same else "DIFFER", len(diff_items), diff_items, ot, nt, adt, "AWAY (RETURN)" if away else "not away"),
      rc == 0 and not away and (same or oset != nset or diff_items or keys), {"keys": keys})
    if tag == "s02e":
        items = [dict((k, v) for k, v in it.items() if k != "licensed_by") for it in J(READ5)["items"]]
        x, m, _u = EC.compare(copy.deepcopy(items), new["expected"])
        print("FACT ACCEPTANCE step-5 replay: total {0}, compare(read {1} {2} items, re-made entries) extra {3} missing {4}".format(nt, rel(READ5), len(items), len(x), len(m)), flush=True)
        g("ACC step-5 replay from stored inputs: total {0} == 47, missing {1} == 0, extra {2} == 0 (read 0c0664d8)".format(nt, len(m), len(x)),
          nt == 47 and not x and not m and md5(READ5).startswith("0c0664d8"), (x, m))
        fin = sorted(glob.glob(b("errorlist_expected_D1_ring_p5_2*.json")) + glob.glob(b("errorlist_expected_D1_ring_p5s02e_*.json")))
        print("FACT P5 final expected file (card 166-a1-2): {0}".format([rel(p) for p in fin] or "none exists - compared with the read only"), flush=True)
        for p in fin:
            ef = J(p)
            print("FACT  {0}: total {1}, measured_from {2}, entries {3}".format(rel(p), ef.get("total"), ef.get("measured_from"),
                  sum(int(r.get("count") or 1) for r in ef.get("expected") or [])), flush=True)
            fi = sorted((r.get("item") for r in ef.get("expected") or []), key=str)
            ni = sorted((r.get("item") for r in new["expected"]), key=str)
            fc = sorted((e.get("item") for e in ef.get("cleared") or []), key=str)
            nc4 = sorted((e["item"] for e in new["cleared"] if e.get("rule")), key=str)
            g("ACC2 re-made entries == the P5 final expected file's entries by item ({0} vs {1}); its dropped items {2} == the items the new rules clear {3}".format(
              len(ni), len(fi), fc, nc4), fi == ni and fc == nc4, {"only_final": sorted(set(map(str, fi)) - set(map(str, ni))), "only_new": sorted(set(map(str, ni)) - set(map(str, fi)))})
for s in ("p5s01a", "p5s01b", "p5s02a"):
    pr = J(b("plan_ring_%s_pred.json" % s))
    e = pr.get("errorlist") or {}
    print("FACT {0}: pred {1} errorlist item_file {2}, predicted_total {3}, keys {4} - no stored item-wise prediction to re-make".format(
          s, md5(b("plan_ring_%s_pred.json" % s))[:8], e.get("item_file"), e.get("predicted_total"), sorted(e)[:12]), flush=True)
after = dict((p, md5(p)) for p in STORED)
g("U stored predicted files, the read and the three step-1..3 preds unchanged ({0} files)".format(len(STORED)), after == before,
  [os.path.basename(p) for p in STORED if after[p] != before[p]])
for p in sorted(glob.glob(os.path.join(OUTD, "*.json"))):
    print("FACT OUT {0} {1}".format(rel(p), md5(p)), flush=True)
sys.exit(g.result([{"path": rel(p), "md5": md5(p)} for p in sorted(glob.glob(os.path.join(OUTD, "*.json")))]))
