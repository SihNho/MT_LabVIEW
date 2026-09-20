"""c57d4_astcheck - offline syntax + resource check for tools/bench/diag_s57_typepair.py. No LabVIEW, no COM."""
import ast
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
TGT = os.path.join(HERE, "diag_s57_typepair.py")
src = open(TGT, encoding="utf-8").read()
tree = ast.parse(src)
print("AST OK  %s  %d lines, %d gate sites" % (os.path.basename(TGT), len(src.splitlines()), src.count("gate(")))

# --- the guard assertions this brief cares about, checked OFFLINE on the source text
guards = [
    ("no recipe path is written", "tools/recipes/stage_d1_s3a_focus_ind.py" in src
     and "open(" not in src.split("recipe_file_reported_not_touched")[1][:400]),
    ("allow_broken is never set True", "allow_broken=True" not in src and "allow_broken = True" not in src),
    ("gui_save is never called", "gui_save(" not in src),
    ("no VI is run (no g.run / RunVI)", ".run_vi(" not in src and "g.run(" not in src),
    ("no motor / ASI / camera import", "motor_gate" not in src and "camera_contract" not in src),
    ("no GUI action (lv_gui)", "lv_gui" not in src),
    ("the ORIGINAL is never saved", "g.save(ORIGINAL)" not in src),
    ("Is Broken? only via the ordered second pass (CONNECT_V1)", src.count("CONNECT_V1(") == 1),
    ("wire_indicators is called at most once", src.count("g.wire_indicators(") == 1),
    ("create_indicator is called at most once", src.count("g.create_indicator(") == 1),
    ("move_in is called at most once", src.count("move_in(target,") == 1),
    ("two distinct artefact paths", "D1_s3a_ind_placed_" in src and "D1_s3a_num_ind_" in src),
    ("the primary artefact is kept when saved", "deleting a saved artefact is forbidden" in src),
]
for name, ok in guards:
    print("  [%s]  guard: %s" % ("ok" if ok else "VIOLATION", name))

for f in ("opconnectnested_v1_labels.json",):
    p = os.path.join(HERE, f)
    ok = os.path.exists(p)
    if ok:
        json.load(open(p, encoding="utf-8"))
    print("  [%s]  tools/bench/%s" % ("ok" if ok else "MISSING", f))
for f in ("diag_s2_scaffold.py", "bench_prep.py", "diag_s57_ctmove_wire.py"):
    print("  [%s]  tools/bench/%s" % ("ok" if os.path.exists(os.path.join(HERE, f)) else "MISSING", f))
for rel in ("tools/gscript.py", "tools/hash_probe.py", "tools/recipes/build_d1_v0.py",
            "tools/recipes/build_opconnectnested_v1.py", "docs/vi-server-ids.json"):
    print("  [%s]  %s" % ("ok" if os.path.exists(os.path.join(ROOT, rel)) else "MISSING", rel))
print("  [%s]  tools/recipes/stage_d1_s3a_focus_ind.py (MUST be absent this cycle)"
      % ("absent-ok" if not os.path.exists(os.path.join(ROOT, "tools", "recipes", "stage_d1_s3a_focus_ind.py"))
         else "PRESENT"))
for f in ("D1_s2_loops.vi", "D1_s1_copy.vi", "OpWireInd_v0.vi", "OpBuildIA_v0.vi", "OpCreateIndicator_v0.vi",
          "OpDelete_v0.vi", "OpMoveIn_v0.vi", "OpConnectNested_v1.vi", "OpNodeInfo_v0.vi", "OpNodeTerms_v0.vi",
          "OpPanelWiring_v0.vi", "OpFPLabels_v0.vi", "OpReportAll_v0.vi"):
    print("  [%s]  claudeDev\\%s" % ("ok" if os.path.exists(os.path.join(CLAUDEDEV, f)) else "MISSING", f))
for rel, names in (("tools/gscript.py", ("def wire_indicators", "def build_index_array", "def create_indicator",
                                         "def delete_object", "def node_info", "def node_terms_uid",
                                         "def panel_wiring", "def fp_labels", "def report_all", "def exec_state",
                                         "def save", "def count", "def uids", "def open_panel",
                                         "def close_panel", "def ref_counts")),
                   ("tools/recipes/build_d1_v0.py", ("def move_in", "def owner_of", "def diag_index")),
                   ("tools/recipes/build_opconnectnested_v1.py", ("def connect_nested_v1",)),
                   ("tools/bench/diag_s2_scaffold.py", ("def fresh", "class Preload", "def file_facts",
                                                        "ORIGINAL =", "ORIG_MD5 =", "S1_ARTEFACT ="))):
    txt = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    for n in names:
        print("  [%s]  %s :: %s" % ("ok" if n in txt else "MISSING", rel, n))
print("phases defined: %s" % [n.name for n in tree.body if isinstance(n, ast.FunctionDef)])
