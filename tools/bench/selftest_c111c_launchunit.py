r"""selftest_c111c_launchunit - card 111-3 D3/D4 (docs/violation-decisions.md device-failed 2026-09-27 20:20 (2)): ONE
launch-unit helper, tools/launchunit.py, on the three command paths - stage_prerun.launched_py (launch gate),
stop_record.segment_class (stop record), guard_card -> protocol._launched_scripts (card flags). OFFLINE, no LabVIEW; nothing
is launched - every case is a string handed to the gates' own functions. HEAD versions (git show) are loaded to show each
positive case was refused before (the test discriminates).
LITERALS: C371 = the command card 110-1 was refused at guard_card.log:371 (agent aa721f52 transcript, tool_use at 16:11:5x);
M2434 = material_marker.log:2434 verbatim.
PREDICTION: D4 C371 and M2434 pass all three paths NOW and were refused by HEAD on the path the log names; `py -u
tools/recipes/stage_x.py` (bare and under bgrun) is a launch on all three; NEGATIVES stay refused (lint && launch, runner
module pdb, `-m tools.recipes.<stage>`, PYTHONPATH prefix, cd away, pipe into py, pytest, smuggled second occurrence);
D3 the three paths call launchunit and RUNNER_MODULES is defined once.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c111c_launchunit.log -- py -u tools/bench/selftest_c111c_launchunit.py"""
import importlib.util, json, os, re, subprocess, sys, tempfile                 # noqa: E401
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path[:0] = [TOOLS, os.path.join(TOOLS, "hooks")]
import launchunit as LU, stage_prerun as SP, stop_record as SR, protocol as PR, guard_card as GC   # noqa: E401,E402
print(__doc__, flush=True)
G = []


def gate(lab, ok, det=""):
    G.append((lab, bool(ok))); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:400]), flush=True)   # noqa: E702


TMP = tempfile.mkdtemp(prefix="c111c_lu_")


def head(rel, name):
    p = os.path.join(TMP, name + ".py")
    open(p, "wb").write(subprocess.run(["git", "show", "HEAD:" + rel], cwd=ROOT, capture_output=True, check=True).stdout)
    sp = importlib.util.spec_from_file_location(name, p); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m)   # noqa: E702
    return m


H_SP, H_SR = head("tools/stage_prerun.py", "stage_prerun_head"), head("tools/stop_record.py", "stop_record_head")
H_SP.ROOT, H_SR.ROOT, H_SR.HERE = ROOT, ROOT, TOOLS
R = "tools/recipes/stage_d1_l2b1.py"
CD = 'cd "{0}"'.format(ROOT.replace("\\", "/"))
C371 = CD + ' && wc -l {0} && py -m pyflakes {0} 2>&1 | head; echo "pyflakes rc done"'.format(R)
M2434 = 'cd "/g/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop" && py -m pyflakes {0}; echo "pyflakes rc=$?"'.format(R)
CARD_READ = json.load(open(os.path.join(TOOLS, "bench", "cards", "task_110-1.json"), encoding="utf-8"))   # labview 'read'
CARD_NONE = json.load(open(os.path.join(TOOLS, "bench", "cards", "task_111-3.json"), encoding="utf-8"))  # labview 'none'
for _c in (CARD_READ, CARD_NONE):          # the flag logic only: requires_110-1.json is stale by now (the card was edited)
    _c.pop("requires", None)
ORIG = PR._launched_scripts
card = lambda c, cmd: PR.check_command(c, cmd)                                     # noqa: E731


def card_head(c, cmd):
    PR._launched_scripts = ORIG
    try:
        return PR.check_command(c, cmd)
    finally:
        GC._install_launch_units(PR)


def sr_build(cmd, mod=SR):
    k = mod.command_keys(cmd)
    return any(v == "build" for kk, v in k.items() if "stage_" in str(kk))


GC._install_launch_units(PR)
gate("D3a guard_card installs the launchunit filter on protocol._launched_scripts", getattr(PR._launched_scripts, "_launchunit", False))
# ---------------------------------------------------------------- D4 the two literals pass all three paths; HEAD refused them
for tag, cmd in (("C371", C371), ("M2434", M2434)):
    gate("D4 {0} launch gate: no launch unit (stage_prerun.launched_py)".format(tag), SP.launched_py(cmd) == [] and SP.launched_stage_scripts(cmd) == [], SP.launched_py(cmd))
    gate("D4 {0} stop record: the recipe is not 'build' (stop_record.command_keys)".format(tag), not sr_build(cmd), SR.command_keys(cmd))
    gate("D4 {0} card flags labview 'read' AND 'none': allowed".format(tag), card(CARD_READ, cmd) is None and card(CARD_NONE, cmd) is None,
         (card(CARD_READ, cmd), card(CARD_NONE, cmd)))
gate("D4h C371 card flags on HEAD's detector: refused 'recipes are refused' (guard_card.log:371)", "recipes are refused" in (card_head(CARD_READ, C371) or ""), card_head(CARD_READ, C371))
gate("D4h M2434 stop record on HEAD: 'build' (material_marker.log:2434)", sr_build(M2434, H_SR), H_SR.command_keys(M2434))
# ---------------------------------------------------------------- launches stay launches on all three paths
for tag, cmd in (("bare", "py -u tools/recipes/stage_x.py"), ("bgrun", "py tools/bgrun.py --material --max-min 5 --log x.log -- py -u tools/recipes/stage_x.py")):
    gate("D4 {0} `py -u tools/recipes/stage_x.py` is a launch unit (launch gate)".format(tag),
         [os.path.basename(p) for p in SP.launched_stage_scripts(cmd)] == ["stage_x.py"], SP.launched_py(cmd))
    gate("D4 {0} ... is 'build' for the stop record".format(tag), sr_build(cmd), SR.command_keys(cmd))
    real = cmd.replace("tools/recipes/stage_x.py", R)
    gate("D4 {0} ... on an existing recipe is refused by card flags 'read'".format(tag), "recipes are refused" in (card(CARD_READ, real) or ""), card(CARD_READ, real))
# ---------------------------------------------------------------- negatives (fail closed)
NEG = [("lint && launch", "py -m pyflakes {0} && py -u {0}".format(R), "all"),
       ("runner module pdb", "py -m pdb {0}".format(R), "all"),
       ("runner module trace", "py -m trace --count {0}".format(R), "all"),
       ("unlisted runner mprof (review c111c-regress s64-78)", "py -m mprof run {0}".format(R), "all"),
       ("unlisted runner streamlit", "py -m streamlit run {0}".format(R), "all"),
       ("unknown module (c103d S7 shape)", "py -m mymod {0}".format(R), "all"),
       ("-m tools.recipes.<stage> (module is a project file)", "py -m tools.recipes.stage_d1_l2b1", "lpcard"),
       ("PYTHONPATH prefix", "PYTHONPATH=tools/bench py -m pyflakes {0}".format(R), "sr"),
       ("cd away then lint", "cd tools/bench && py -m pyflakes ../../{0}".format(R), "sr"),
       ("pipe into py", "py -m pyflakes {0} | py -".format(R), "sr"),
       ("pytest -m pyflakes", "pytest -m pyflakes {0}".format(R), "sr"),
       ("smuggled 2nd occurrence (quoted, after &)", 'py -m pyflakes {0} & cmd /c "py {0}"'.format(R), "srcard"),
       ("& then a bare launch", "py -m pyflakes {0} & py -u {0}".format(R), "all"),
       ("module arg with a quote/redirect", 'py -m pyflakes {0} "x" > {0}'.format(R), "sr")]
for tag, cmd, where in NEG:
    lp = bool(SP.launched_py(cmd)); sr = sr_build(cmd); cd = "recipes are refused" in (card(CARD_READ, cmd) or "")   # noqa: E702
    ok = {"all": lp and sr and cd, "lpcard": lp and cd, "srcard": sr and cd, "sr": sr, "card": cd}[where]
    gate("NEG {0}: still refused ({1})".format(tag, where), ok, {"launch_gate": lp, "stop_record_build": sr, "card": cd})
# ---------------------------------------------------------------- D3 one helper, no copies
src = dict((n, open(os.path.join(TOOLS, n), encoding="utf-8").read()) for n in ("stage_prerun.py", "stop_record.py", os.path.join("hooks", "guard_card.py")))
lp_src = src["stage_prerun.py"].split("def launched_py(cmd):", 1)[1].split("\ndef ", 1)[0]
gate("D3b stage_prerun.launched_py delegates to launchunit (no own -m parse)", "LU.launched_py" in lp_src and '"-m"' not in lp_src, len(lp_src))
gate("D3c stop_record and guard_card import launchunit", all("import launchunit" in s for s in src.values()), [n for n, s in src.items() if "import launchunit" not in s])
defs = [n for n in os.listdir(TOOLS) if n.endswith(".py") and re.search(r"^READONLY_MODULES\s*=", open(os.path.join(TOOLS, n), encoding="utf-8", errors="replace").read(), re.M)]
gate("D3d READONLY_MODULES defined once (tools/launchunit.py)", defs == ["launchunit.py"], defs)
CORPUS = [C371, M2434, "py -u tools/recipes/stage_x.py", "py -m pdb " + R, "py -V\npy -u tools/recipes/stage_d1_disp.py"]
gate("D3e launch gate == launchunit on the corpus", all(SP.launched_py(c) == LU.launched_py(c, SP.ROOT) for c in CORPUS))
npass = sum(1 for _l, ok in G if ok); nfail = len(G) - npass
first = next((lab for lab, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(npass, nfail), flush=True)
print(PR.result_line(PR.make_result(npass, nfail, first, status="PASS" if not nfail else "FAIL")), flush=True)
sys.exit(0 if not nfail else 1)
