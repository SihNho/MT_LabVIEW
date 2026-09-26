r"""selftest_c106d_tools - card 106-4 pass lines H1, H2, H4, H5 (H3 is selftest_guard_bash_jev.py). No LabVIEW, no model,
no network, no peer dispatch.

H1 gscript's broken-VI GUI save: every authorised GUI act in it carries -Evidence == 'user 2026-09-22 broken-intermediate
   save' (CLAUDE.md split rule 6). Read from gscript.py's AST; the function is never called.
H2 guard_bash.stop_gate against the REAL stop_record with a planted undisposed record in a temp store: read-only commands
   on the stopped recipe pass, launches are refused, and the `wc -l \"x<NL>py -u R<NL>\"` twin
   (archive/peer/2026-09-27-c103d-hooks-before.md s1) is refused.
H4 peer.ps1 ConvertTo-VerdictNulls, extracted from peer.ps1 by the PowerShell AST and run on two archived answers whose
   verdict failed on "?" and on synthetic lines; the result is parsed by protocol.parse_verdict (verdict/1 schema).
H5 audit_cycle: tools/bench/jev_gate.log is not a build log for A1/A3; a real bypass and a real unreviewed failure are
   still reported (negative cases).

    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_c106d_tools.log -- py -u tools/bench/selftest_c106d_tools.py
    ... -- py -u tools/bench/selftest_c106d_tools.py --old <dir holding the pre-106-4 gscript/guard_bash/peer.ps1/audit_cycle>
The --old run must FAIL H1/H2-twin/H4/H5 (the test sees the defect); the plain run must pass everything.
Prior art checked: selftest_c103d_hooks.py (S/N rows, stand-in check_command - here the real one), no gui_save or
peer.ps1 verdict test exists (grep selftest_* for gui_save / parse-verdict: none).
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
os.chdir(ROOT)
import protocol  # noqa: E402
import stop_record as SR  # noqa: E402

OLD = sys.argv[sys.argv.index("--old") + 1] if "--old" in sys.argv else None
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def load(name, rel):
    path = os.path.join(OLD, os.path.basename(rel)) if OLD else os.path.join(ROOT, rel)
    spec = importlib.util.spec_from_file_location(name + ("_old" if OLD else ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


print("=== selftest_c106d_tools (%s code)" % ("OLD " + OLD if OLD else "current"), flush=True)
EV = "user 2026-09-22 broken-intermediate save"

# ---------------------------------------------------------------- H1 (static: the card's gui flag is false, so the save
# function is READ by the AST, never called - not even stubbed; a stubbed call was refused by the card guard)
import ast  # noqa: E402
with open(os.path.join(OLD, "gscript.py") if OLD else os.path.join(ROOT, "tools", "gscript.py"), encoding="utf-8") as fh:
    tree = ast.parse(fh.read())
consts = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
          for t in n.targets if isinstance(t, ast.Name)}
fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "gui_save")
acts = []
for c in ast.walk(fn):
    if isinstance(c, ast.Call) and getattr(c.func, "id", None) == "_lv_gui":
        vals = [a.value if isinstance(a, ast.Constant) else ("NAME:" + a.id if isinstance(a, ast.Name) else "?")
                for a in c.args]
        if "-Exception" in vals:
            ev = vals[vals.index("-Evidence") + 1] if "-Evidence" in vals else None
            acts.append((vals[1] if len(vals) > 1 else "?", vals[vals.index("-Exception") + 1],
                         consts.get(ev[5:]) if isinstance(ev, str) and ev.startswith("NAME:") else ev))
gate("H1a gui_save's authorised GUI acts found (clickprobe, Ctrl+E, Ctrl+S)", len(acts) == 3, acts)
gate("H1b every one carries -Evidence == the user's approval wording", acts and all(a[2] == EV for a in acts),
     sorted(set(str(a[2]) for a in acts)))
gate("H1c every one is -Exception Approved", acts and all(a[1] == "Approved" for a in acts))

# ---------------------------------------------------------------- H2
gb = load("guard_bash", "tools/hooks/guard_bash.py")
gb.note = lambda *a, **k: None
store = os.path.join(tempfile.mkdtemp(prefix="c106d_h2_"), "stop_records.json")
R = "tools/recipes/stage_d1_disp.py"
with open(store, "w", encoding="utf-8") as fh:
    json.dump([{"recipe_path": R, "reviewed_sha256": "0" * 64, "review_file": "archive/peer/c106d-nonexistent.md",
                "verdict": ["already-built"], "created_utc": "2026-09-27T00:00:00Z", "released": None}], fh)
SR.STORE = store


def sg(cmd, shell="Bash"):
    try:
        return gb.stop_gate(cmd, shell)
    except TypeError:                                   # the pre-106-4 hook has no shell argument
        return gb.stop_gate(cmd)


for lab, cmd, shell, want in (
        ("H2a wc -l on the stopped recipe passes (read-only)", "wc -l %s" % R, "Bash", 0),
        ("H2b NEGATIVE direct launch refused", "py -u %s" % R, "Bash", 2),
        ("H2c NEGATIVE bgrun launch refused", "py tools/bgrun.py --material --max-min 5 --log x.log -- py -u %s" % R, "Bash", 2),
        ("H2d NEGATIVE the wc -l twin (escaped quote + newline) refused", 'wc -l \\"x\npy -u %s\n\\"' % R, "Bash", 2),
        ("H2e NEGATIVE the pyflakes twin N1 still refused", 'py -m pyflakes \\"x\npy -u %s\n\\"' % R, "Bash", 2),
        ("H2f escaped quotes INSIDE a double-quoted grep pattern: read-only, passes", 'grep -n "a \\"q\\" b" %s' % R, "Bash", 0),
        ("H2g NEGATIVE backslash inside single quotes does not escape: launch refused", "wc -l 'a\\' ; py -u %s" % R, "Bash", 2),
        ("H2h NEGATIVE escaped backslash closes the quote: launch refused", 'sed -n 1,5p %s && echo "x \\\\" && py -u %s' % (R, R), "Bash", 2),
        ("H2i PowerShell Get-Content passes (no bash escapes applied)", "Get-Content %s" % R, "PowerShell", 0),
        ("H2j NEGATIVE PowerShell launch refused", "py -u %s" % R, "PowerShell", 2)):
    got = sg(cmd, shell)
    gate(lab, got == want, "code %s want %s" % (got, want))

# ---------------------------------------------------------------- H4
PS1 = os.path.join(OLD, "peer.ps1") if OLD else os.path.join(ROOT, "tools", "peer.ps1")
PS = (r"$ErrorActionPreference='Stop';"
      r"$ast=[System.Management.Automation.Language.Parser]::ParseFile($env:C106_PS1,[ref]$null,[ref]$null);"
      r"$f=$ast.FindAll({param($n) $n -is [System.Management.Automation.Language.FunctionDefinitionAst] -and "
      r"$n.Name -eq 'ConvertTo-VerdictNulls'},$true) | Select-Object -First 1;"
      r"if(-not $f){Write-Output 'NOFUNC'; exit 3};"
      r". ([scriptblock]::Create($f.Extent.Text));"
      r"$t=[IO.File]::ReadAllText($env:C106_IN,[Text.Encoding]::UTF8);"
      r"[IO.File]::WriteAllText($env:C106_OUT,(ConvertTo-VerdictNulls $t),(New-Object Text.UTF8Encoding $false));"
      r"Write-Output 'OK'")


def convert(text):
    d = tempfile.mkdtemp(prefix="c106d_h4_")
    fi, fo = os.path.join(d, "in.txt"), os.path.join(d, "out.txt")
    with open(fi, "w", encoding="utf-8") as fh:
        fh.write(text)
    env = dict(os.environ, C106_PS1=PS1, C106_IN=fi, C106_OUT=fo)
    r = subprocess.run(["powershell", "-NoProfile", "-NonInteractive", "-Command", PS], env=env,
                       capture_output=True, text=True, timeout=60)
    if "OK" not in r.stdout:
        return None, (r.stdout + r.stderr).strip()[:200]
    with open(fo, encoding="utf-8") as fh:
        return fh.read(), None


def vline(loss):
    return ('prose line "loss_usd":"?" outside the verdict stays\nVERDICT {"schema":"verdict/1","id":"c106d-x",'
            '"verdict":"refuted","violations":[{"slug":"wrong-ordering","loss_min":12,"loss_usd":%s,'
            '"evidence":"a.log:1"}],"sources":[],"note":""}\n' % loss)


for lab, src, want_id, check in (
        ("H4a archived retrospective-cycle74 (loss_usd \"?\" x2) now validates, loss_usd null",
         "archive/peer/2026-09-25-retrospective-cycle74.md", "retrospective-cycle74",
         lambda d: all(v.get("loss_usd") is None for v in d["violations"])),
        ("H4b archived hyp-meter86b-prefix (loss_min AND loss_usd \"?\") validates, both null",
         "archive/peer/2026-09-25-hyp-meter86b-prefix.md", "hyp-meter86b-prefix",
         lambda d: all(v.get("loss_usd") is None and v.get("loss_min") is None for v in d["violations"]))):
    with open(os.path.join(ROOT, src), encoding="utf-8", errors="replace") as fh:
        raw = fh.read()
    before, why0 = protocol.parse_verdict(raw, want_id)
    out, err = convert(raw)
    d, why = protocol.parse_verdict(out or "", want_id)
    gate(lab, before is None and d is not None and check(d),
         "before: %s | after: %s" % (why0, err or why or "valid, violations %s" % d["violations"]))
out, err = convert(vline("1.5"))
d, why = protocol.parse_verdict(out or "", "c106d-x")
gate("H4c a numeric loss_usd is untouched and validates (1.5)", d is not None and d["violations"][0]["loss_usd"] == 1.5,
     err or why or d["violations"][0])
gate("H4d prose outside the VERDICT line keeps its \"?\"", out is not None and 'prose line "loss_usd":"?"' in out, err)
out, err = convert(vline('"about 3"'))
d, why = protocol.parse_verdict(out or "", "c106d-x")
gate("H4e NEGATIVE any other string still fails verdict/1", out is not None and d is None and "got str" in (why or ""),
     err or why)

# ---------------------------------------------------------------- H5
ac = load("audit_cycle", "tools/audit_cycle.py")
bench = tempfile.mkdtemp(prefix="c106d_h5_")
peer = os.path.join(bench, "peer")
os.makedirs(os.path.join(bench, "sub"))
os.makedirs(peer)
files = {
    "jev_gate.log": "2026-09-27 06:00:00 | JEV-LADDER | stage_x.log | new-problem p=0.9 | NEXT-ACTION: review\n"
                    "JEV-GATEROW | FAIL  E3 cdiff 6/21 | BGRUN END rc=1 after 3s\n",
    "diag_bypass.log": "ran without bgrun\n",
    "diag_fail.log": "BGRUN START 2026-09-27 06:00:00 limit 3.0 min: py -u tools/bench/diag_fail.py\nFAIL x\n"
                     "BGRUN END rc=1 after 3s\n",
    "diag_ok.log": "BGRUN START 2026-09-27 06:00:00 limit 3.0 min: py -u tools/bench/diag_ok.py\nBGRUN END rc=0 after 3s\n",
    os.path.join("sub", "jev_gate.log"): "no bgrun here\n"}
for n, body in files.items():
    with open(os.path.join(bench, n), "w", encoding="utf-8") as fh:
        fh.write(body)
paths = [os.path.join(bench, n) for n in files]
try:
    kept, dropped = ac.drop_jev_ledgers(paths, bench=bench)
    names_k = sorted(os.path.relpath(p, bench) for p in kept)
    gate("H5a jev_gate.log directly in BENCH is dropped, nothing else",
         [os.path.basename(p) for p in dropped] == ["jev_gate.log"] and len(kept) == 4, "kept %s" % names_k)
    gate("H5b NEGATIVE a jev_gate.log in a SUBDIRECTORY is kept (path rule, not name only)",
         os.path.join("sub", "jev_gate.log") in names_k)
    byp = ac.a1_bypass(kept)
    gate("H5c A1: jev_gate.log no longer a bypass; NEGATIVE the real bypass diag_bypass.log still reported",
         "diag_bypass.log" in byp and os.path.join(bench, "jev_gate.log") not in kept, byp)
    failing, unrev = ac.a3_unreviewed(kept, reviews_glob=os.path.join(peer, "*.md"))
    gate("H5d A3: NEGATIVE the failing diag_fail.log is still unreviewed; the dropped ledger is not counted",
         "diag_fail.log" in unrev and "diag_ok.log" not in unrev, unrev)
    gate("H5e the old reading WOULD have flagged the ledger (A1 over the undropped list)",
         "jev_gate.log" in ac.a1_bypass(paths[:1]))
except AttributeError as e:
    gate("H5 audit_cycle has drop_jev_ledgers / a1_bypass / a3_unreviewed", False, e)

n = sum(ok for _, ok in G)
print("\n=== %d PASS / %d FAIL" % (n, len(G) - n), flush=True)
print(protocol.result_line(protocol.make_result(n, len(G) - n, next((lab for lab, ok in G if not ok), None))))
sys.exit(0 if n == len(G) else 1)
