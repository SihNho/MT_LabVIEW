"""READ-ONLY: why did node_labels() on the 'Finding and Modifying Objects' examples return 1055 instantly? Load one
example the plain way (exec_state, report_all Diagram/Property counts, node_labels on diagram 0 with the error text).
  py tools/bgrun.py --max-min 5 --log tools/bench/diag_example_load.log -- py -u tools/bench/diag_example_load.py"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

D = os.path.join(g.CLAUDEDEV, "NIScriptingExamples")
for f in ("Finding and Modifying Objects\\Tagging.vi", "Structures\\VI Scripting with Structures - Case Structure.vi",
          "Creating Objects\\Adding Objects.vi"):
    p = os.path.join(D, f)
    print(f"\n{f}: exists {os.path.exists(p)}", flush=True)
    g._lv = None
    for step, fn in (("exec_state", lambda: g.exec_state(p)),
                     ("Diagram count", lambda: len(g.report_all(p, "Diagram"))),
                     ("Property count", lambda: len(g.report_all(p, "Property"))),
                     ("node_labels d0", lambda: len(g.node_labels(p, 0)))):
        try:
            print(f"   {step}: {fn()}", flush=True)
        except Exception as e:
            print(f"   {step}: EXC {str(e)[:160]}", flush=True)
