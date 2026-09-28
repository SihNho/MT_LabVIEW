r"""diag_c120_parsecheck - OFFLINE (no LabVIEW): re-parse the bytes diag_c120_types.py run 1 recorded (facts_c120_types.json) with the
fixed gscript.parse_type_descriptors (Array/Cluster TDs hold INDICES into the TD list, diag_c120_types.log:45-50) and print each canon.
PREDICTION: K_DBL Array1D<DBL>, K_I32 Array1D<I32>, F3 I32, R0 Array1D<DBL>, F5 Cluster{Array1D<DBL>,Array1D<DBL>}.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c120_parsecheck.log -- py -u tools/bench/diag_c120_parsecheck.py"""
import json, os, sys                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(HERE)), "tools"))  # noqa: E702
import ast                                                                          # noqa: E402
src = open(os.path.join(os.path.dirname(HERE), "gscript.py"), encoding="utf-8").read()
ns = {}
for n in ast.parse(src).body:                                                       # only the pure parser, never the COM module
    if (isinstance(n, ast.FunctionDef) and n.name in ("parse_type_descriptors", "_td_canon")) or \
            (isinstance(n, ast.Assign) and any(getattr(t, "id", "") in ("TD_NAMES", "_TD_PLAIN") for t in n.targets)):
        exec(compile(ast.Module(body=[n], type_ignores=[]), "gscript-parse", "exec"), ns)
F = json.load(open(os.path.join(HERE, "facts_c120_types.json"), encoding="utf-8"))
want = {"K_DBL": "Array1D<DBL>", "K_I32": "Array1D<I32>", "F3": "I32", "R0": "Array1D<DBL>"}
bad = 0
for k, t in F["terms"].items():
    ty = ns["parse_type_descriptors"](bytes.fromhex(t["bytes_hex"]))
    ok = k not in want or ty.get("canon") == want[k]
    bad += not ok
    print("  {0}  {1} t{2}: canon {3!r}".format("PASS" if ok else "FAIL", k, t["term"], ty.get("canon") or ty.get("err")), flush=True)
print('RESULT {{"schema":"result-line/1","status":"{0}","gates":{{"pass":{1},"fail":{2}}},"first_fail":null,"artefacts":[]}}'.format(
    "PASS" if not bad else "FAIL", len(F["terms"]) - bad, bad), flush=True)
sys.exit(1 if bad else 0)
