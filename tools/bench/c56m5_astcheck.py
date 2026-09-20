"""c56m5_astcheck - offline syntax + resource check for tools/bench/diag_s56_transport3.py. No LabVIEW, no COM."""
import ast
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
TGT = os.path.join(HERE, "diag_s56_transport3.py")
src = open(TGT, encoding="utf-8").read()
ast.parse(src)
print("AST OK  %s  %d lines, %d gate sites" % (os.path.basename(TGT), len(src.splitlines()), src.count("gate(")))

import json
for f in ("opconnectnested_v1_labels.json", "opmovebyindex_labels.json", "oppanelwiring_labels.json",
          "main_vi_panel_wiring.json"):
    p = os.path.join(HERE, f)
    ok = os.path.exists(p)
    if ok:
        json.load(open(p, encoding="utf-8"))
    print("  [%s]  %s" % ("ok" if ok else "MISSING", f))
for f in ("diag_s2_scaffold.py", "bench_prep.py"):
    print("  [%s]  tools/bench/%s" % ("ok" if os.path.exists(os.path.join(HERE, f)) else "MISSING", f))
for rel in ("tools/gscript.py", "tools/hash_probe.py", "tools/recipes/build_d1_v0.py",
            "tools/recipes/build_opconnectnested_v1.py", "docs/vi-server-ids.json"):
    print("  [%s]  %s" % ("ok" if os.path.exists(os.path.join(ROOT, rel)) else "MISSING", rel))
for f in ("D1_s2_loops.vi", "D1_s1_copy.vi", "OpWireInd_v0.vi", "OpBuildIA_v0.vi", "OpCreateIndicator_v0.vi",
          "OpDelete_v0.vi", "OpMoveByIndex_v0.vi", "OpMoveIn_v0.vi", "OpConnectNested_v1.vi", "OpNodeInfo_v0.vi",
          "OpPanelWiring_v0.vi", "OpFPLabels_v0.vi", "OpRemoveBadWires_v0.vi", "OpReportAll_v0.vi",
          "DIAG_s56_wireind_20260920_214454.vi", "DIAG_s56_localvar_20260920_214454.vi"):
    print("  [%s]  claudeDev\\%s" % ("ok" if os.path.exists(os.path.join(CLAUDEDEV, f)) else "MISSING", f))
for f in ("NIScriptingExamples/Moving Objects/Test - Moving Objects Source.vi",
          "NIScriptingExamples/Moving Objects/Test - Moving Objects Target.vi",
          "NIScriptingExamples/Moving Objects/Test - Moving Objects Source.vi.ORIG.bak",
          "NIScriptingExamples/Moving Objects/Test - Moving Objects Target.vi.ORIG.bak"):
    print("  [%s]  claudeDev\\%s" % ("ok" if os.path.exists(os.path.join(CLAUDEDEV, *f.split("/"))) else "MISSING", f))
# the imported names this diagnostic depends on, checked against the sources OFFLINE
for rel, names in (("tools/gscript.py", ("def wire_indicators", "def build_index_array", "def create_indicator",
                                         "def delete_object", "def copy_by_index", "def node_info",
                                         "def node_terms_uid", "def panel_wiring", "def fp_labels",
                                         "def report_all", "def remove_bad_wires_scripted", "def exec_state",
                                         "def save", "MOVE_SRC =", "MOVE_DST =")),
                   ("tools/recipes/build_d1_v0.py", ("def move_in", "def owner_of", "def diag_index")),
                   ("tools/recipes/build_opconnectnested_v1.py", ("def connect_nested_v1",)),
                   ("tools/bench/diag_s2_scaffold.py", ("def fresh", "class Preload", "def file_facts",
                                                        "ORIGINAL =", "ORIG_MD5 =", "S1_ARTEFACT ="))):
    txt = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    for n in names:
        print("  [%s]  %s :: %s" % ("ok" if n in txt else "MISSING", rel, n))
