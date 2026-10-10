# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_163-a1-3.md
# ---
r"""diag_c163_a1_3_inspect - card 163-a1-3 (OFFLINE, read-only): prints the shape of plan_ring_p5s02c.json, the 163-a1-2 session table and the
53-row expected Error List so the makers are written against real keys. Writes nothing.
PREDICTION CONTRACT: the three files load; 12 actions; 53 expected rows.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c163_a1_3_inspect.log -- py -u tools/bench/diag_c163_a1_3_inspect.py"""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                              # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda n: json.load(open(os.path.join(B, n), encoding="utf-8"))                          # noqa: E731
p = J("plan_ring_p5s02c.json")
print("PLAN keys", list(p.keys()))
print("PLAN base", json.dumps(p.get("base"))[:600])
fz = p["finalized"]
print("FZ keys", list(fz.keys()))
print("FZ", json.dumps(dict((k, v) for k, v in fz.items() if k not in ("step_files", "end_cdiff_rows")))[:2500])
print("STEP FILES", len(fz.get("step_files") or []), json.dumps((fz.get("step_files") or [])[:2]))
for a in p["actions"]:
    print("ACT", json.dumps(a)[:400])
s = J("prep_c163_a1_2_session.json")
print("SESS keys", list(s.keys()))
for k, v in s.items():
    print("SESS", k, json.dumps(v)[:700])
e = J("errorlist_expected_D1_ring_p5s02b_20261010_105511.json")
print("EL keys", list(e.keys()), "total", e.get("total"), "measured_from", e.get("measured_from"), e.get("measured_md5"), "bed", e.get("bed"))
for r in e["expected"]:
    print("ELROW", r.get("item"), r.get("class"), (r.get("object") or {}).get("kind"), (r.get("object") or {}).get("uid"), "clears_by", json.dumps(r.get("clears_by")),
          "keys", sorted(r.keys()))
print("EL base_expected", json.dumps(e.get("base_expected"))[:300], "| format_note", str(e.get("format_note"))[:300])
ok = len(p["actions"]) == 12 and sum(int(r.get("count") or 1) for r in e["expected"]) == int(e["total"]) == 53   # 52 entries, one with count 2
print(protocol.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": 1 if ok else 0, "fail": 0 if ok else 1},
                            "first_fail": None if ok else "shape", "artefacts": []}))
sys.exit(0 if ok else 1)
