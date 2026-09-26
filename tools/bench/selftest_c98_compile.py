"""selftest_c98_compile - card 98-3: byte-compile the files the card edits (no import, no LabVIEW, nothing written under
the project: the .pyc goes to %TEMP%). The stage dry run (tools/stage_prerun.py --dry) REPLACES gscript with a fake
module, so a syntax error in tools/gscript.py would reach the real run first - this closes that gap. Prints one gate per
file and a C6 RESULT line.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/selftest_c98_compile.log -- py -u tools/bench/selftest_c98_compile.py"""
import os
import py_compile
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
import protocol                                                                        # noqa: E402

FILES = ["tools/gscript.py", "tools/recipes/stage_d1_fgate.py", "tools/bench/selftest_c98_rbw.py"]
npass, fails = 0, []
for f in FILES:
    p = os.path.join(ROOT, *f.split("/"))
    c = os.path.join(tempfile.gettempdir(), "compilecheck_" + os.path.basename(f) + "c")
    try:
        py_compile.compile(p, doraise=True, cfile=c)
        npass += 1
        print("  PASS  compiles: {0}".format(f), flush=True)
    except (py_compile.PyCompileError, OSError) as e:
        fails.append(f)
        print("  FAIL  compiles: {0}  {1}".format(f, str(e)[:400]), flush=True)
    finally:
        if os.path.exists(c):
            os.remove(c)
print(protocol.result_line(protocol.make_result(npass, len(fails), fails[0] if fails else None)), flush=True)
sys.exit(1 if fails else 0)
