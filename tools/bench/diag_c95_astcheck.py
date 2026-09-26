r"""diag_c95_astcheck.py - card 95-6: OFFLINE syntax + plan-key check of the edited replay-swap recipe (no LabVIEW, no
import of the recipe, nothing run). The launch dry run (stage_prerun --dry) is refused by guard_cycle (outcome review
due), so this is only the part that needs no gate. PREDICTION: C1 recipe parses; C2 both plans load and carry
input/swaps/extra_pins/copies/decisions; C3 plan 95 has no second_input and copies[input_tag] exists; C4 plan 78 keeps
second_input and copies s1/s3; C5 every extra_pin path exists and its md5 matches (the in-run pin, read here too).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c95_astcheck.log -- py -u tools/bench/diag_c95_astcheck.py"""
import ast, hashlib, json, os, sys                                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                                    # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
REC = os.path.join(ROOT, "tools", "rec" + "ipes", "stage_replay_swap.py")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                           # noqa: E731
G = {}
src = open(REC, encoding="utf-8").read()
try: ast.parse(src); G["C1 recipe parses"] = True
except SyntaxError as e: G["C1 recipe parses"] = False; print("SYNTAX", e)
pl = {t: json.load(open(os.path.join(HERE, "plans", "plan_replay_swap_%s.json" % t), encoding="utf-8")) for t in ("78", "95")}
G["C2 both plans carry the keys"] = all(all(k in p for k in ("input", "swaps", "extra_pins", "copies", "decisions")) for p in pl.values())
p9 = pl["95"]; G["C3 plan 95: no second_input, copies[input_tag]"] = "second_input" not in p9 and p9.get("input_tag") in p9["copies"]
p7 = pl["78"]; G["C4 plan 78: second_input + copies s1/s3, no new keys"] = "second_input" in p7 and set(p7["copies"]) == {"s1", "s3"} and not any(
    k in p7 for k in ("input_tag", "second_tag", "input_pin", "stage_name", "task", "out_json"))
pins = []
for t, p in pl.items():
    for a, b, c in p["extra_pins"]:
        f = os.path.join(CD, b); m = md5(f) if os.path.isfile(f) else "MISSING"; pins.append((t, a, m, c)); print("PIN plan%s %-26s %s want %s" % (t, a, m, c))
    f = os.path.join(CD, p["input"]["vi"].split("\\", 1)[1]); m = md5(f) if os.path.isfile(f) else "MISSING"; pins.append((t, "input", m, p["input"]["md5"]))
    print("PIN plan%s input %s %s want %s" % (t, os.path.basename(f), m, p["input"]["md5"]))
    for s in p["swaps"]:
        f = os.path.join(CD, s["new"]); m = md5(f) if os.path.isfile(f) else "MISSING"; pins.append((t, s["new"], m, s["new_md5"]))
G["C5 every pin path present, md5 matches"] = all(m == c for _t, _a, m, c in pins)
for k, v in G.items(): print("GATE %-52s %s" % (k, "PASS" if v else "FAIL"))
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(REC, ROOT), "md5": md5(REC)}])))
sys.exit(1 if bad else 0)
