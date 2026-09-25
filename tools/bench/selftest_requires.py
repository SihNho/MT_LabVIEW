r"""selftest_requires - card chat-N1 (4a): task/1 `requires`, checked OFFLINE by `py tools/protocol.py requires <card>`,
and the launch refusal in protocol.check_command (reached from guard_bash via guard_card). No LabVIEW: the op dir and
the wiki dir are %TEMP% fixtures (REQUIRES_CLAUDEDEV / REQUIRES_WIKI_DIR), cards live in the sandbox.

PREDICTION CONTRACT (all PASS):
  Q1 all present (op / verb / file / terminal): CLI exit 0, requires_<id>.json ok, each found item cited; launch ALLOWED
  Q2 one missing op: CLI exit 1, listed in missing; RESULT line FAIL; bgrun launch REFUSED naming it
  Q3 card without `requires`: launch ALLOWED, no file needed (unchanged)
  Q4 card with `requires` but no requires_<id>.json: launch REFUSED ("absent")
  Q5 card edited after the check: REFUSED ("stale")
  Q6 a non-launch command (cat) under a missing-requires card: ALLOWED
  Q7 schema: unknown kind rejected; every tools/bench/cards/task_88-*/89-*/90-* still validates
    py tools/bgrun.py --max-min 3 --log tools/bench/selftest_requires.log -- py -u tools/bench/selftest_requires.py
"""
import glob, json, os, shutil, subprocess, sys                                      # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
SAND = os.path.join(os.environ.get("TEMP", "."), "requires_selftest_%d" % os.getpid())
OPS, WIKI = os.path.join(SAND, "claudeDev"), os.path.join(SAND, "wiki")
for d in (os.path.join(OPS, "ops"), WIKI):
    os.makedirs(d, exist_ok=True)
open(os.path.join(OPS, "ops", "OpFake_v0.vi"), "wb").write(b"RSRC")
json.dump({"terminals": [{"term_uid": 7, "term_name": "fake term", "owner_class": "IndexArray"}],
           "connector_pane": []}, open(os.path.join(WIKI, "fakevi.json"), "w", encoding="utf-8"))
os.environ["REQUIRES_CLAUDEDEV"], os.environ["REQUIRES_WIKI_DIR"] = OPS, WIKI
sys.path.insert(0, TOOLS)
import protocol as P   # noqa: E402
P.CARDS_DIR = SAND
G = []
LAUNCH = "py tools/bgrun.py --max-min 5 --log tools/bench/x.log -- py -u tools/bench/x.py"


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("ok " if ok else "BAD", label, str(detail)[:300]), flush=True)


def card(cid, requires=None):
    c = {"schema": "task/1", "id": cid, "kind": "build", "goal": "selftest", "unblocks": "M8",
         "flags": {"labview": "build", "gui": False, "hardware": "none", "run_vi": False, "write": [],
                   "status_edit": False, "git_commit": False, "peers": []}, "budget": {"failures": 2, "minutes": 5}}
    if requires is not None:
        c["requires"] = requires
    p = os.path.join(SAND, "task_%s.json" % cid)
    json.dump(c, open(p, "w", encoding="utf-8"), indent=1)
    return p


def cli(p):
    env = dict(os.environ)
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "protocol.py"), "requires", p, "--cards-dir", SAND],
                       text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=60, env=env)
    return r.returncode, r.stdout + r.stderr


def loaded(p):
    c = P.load_card(p, None)
    c["_md5"] = P._md5(p)
    return c


ALL = [{"kind": "op", "name": "OpFake_v0"}, {"kind": "verb", "name": "move_in", "where": "tools/stagekit.py"},
       {"kind": "file", "name": "tools/stagekit.py"}, {"kind": "terminal", "name": "fake term", "where": "fakevi"}]
p1 = card("st-q1", ALL)
rc, out = cli(p1)
d = json.load(open(os.path.join(SAND, "requires_st-q1.json"), encoding="utf-8"))
gate("Q1 all present: exit 0, ok, 4 cited; launch allowed",
     rc == 0 and d["ok"] and len(d["found"]) == 4 and all(x.get("cite") for x in d["found"])
     and P.check_command(loaded(p1), LAUNCH) is None, [rc, [x.get("cite") for x in d["found"]]])
p2 = card("st-q2", ALL + [{"kind": "op", "name": "OpDoesNotExist_v9"}])
rc, out = cli(p2)
d = json.load(open(os.path.join(SAND, "requires_st-q2.json"), encoding="utf-8"))
why = P.check_command(loaded(p2), LAUNCH)
gate("Q2 missing op: exit 1, listed, RESULT FAIL, launch refused naming it",
     rc == 1 and [m["name"] for m in d["missing"]] == ["OpDoesNotExist_v9"] and '"status":"FAIL"' in out
     and why and "OpDoesNotExist_v9" in why, [rc, why])
p3 = card("st-q3")
gate("Q3 card without requires: launch allowed", P.check_command(loaded(p3), LAUNCH) is None)
p4 = card("st-q4", ALL)
why = P.check_command(loaded(p4), LAUNCH)
gate("Q4 requires but no file: refused (absent)", why and "absent" in why, why)
p5 = card("st-q5", ALL)
cli(p5)
card("st-q5", ALL + [{"kind": "file", "name": "tools/protocol.py"}])
why = P.check_command(loaded(p5), LAUNCH)
gate("Q5 card changed after the check: refused (stale)", why and "stale" in why, why)
gate("Q6 non-launch command under a missing-requires card allowed",
     P.check_command(loaded(p2), "cat tools/bench/x.log") is None)
bad = json.load(open(p3, encoding="utf-8"))
bad["requires"] = [{"kind": "donor", "name": "x"}]
ok_bad, _w = P.validate_obj(bad)
olds = sorted(glob.glob(os.path.join(HERE, "cards", "task_8[89]-*.json")) + glob.glob(os.path.join(HERE, "cards", "task_90-*.json")))
res = [(os.path.basename(f), P.validate_obj(json.load(open(f, encoding="utf-8")))[0]) for f in olds]
gate("Q7 unknown kind rejected; %d old task cards (88/89/90) validate" % len(res),
     not ok_bad and res and all(v for _, v in res), [r for r in res if not r[1]])
shutil.rmtree(SAND, ignore_errors=True)
npass = sum(1 for _, o in G if o)
print("SUMMARY %d/%d gates pass" % (npass, len(G)), flush=True)
first = next((l for l, o in G if not o), None)
print(P.result_line(P.make_result(npass, len(G) - npass, first)), flush=True)
sys.exit(0 if first is None else 1)
