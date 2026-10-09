# ---
# labview: none
# hardware: none
# offline-args: before
# evidence: tools/bench/cards/brief_156-b2-2.md
# ---
"""Card 156-a2-1's inv config (diag_c156_a2_1_inv.py:5-59) as inputs + one call to tools/invcheck.py (card 156-b2-2). PREDICTION: as that card.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c156_b2_2_inv_c156a21_<mode>.log -- py -u tools/bench/diag_c156_b2_2_inv_c156a21.py <mode>"""
import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import invcheck                                                                                   # noqa: E402
P = lambda r: os.path.join(ROOT, *r.split("/"))                                                   # noqa: E731  (backslash keys, as the copies)
C = lambda n: os.path.join(invcheck.CD, n)                                                        # noqa: E731
T, B = "tools/", "tools/bench/"
PINS = [(C("D1_ring_p5s01_20261009_124542.vi"), "7f2582ae"), (C("D1_ring_p5s01a_20261009_101219.vi"), "2482fe7b"),
        (C("D1_ring_p5s01b_20261009_123319.vi"), "7f2582ae")] + [(P(r), m) for r, m in [
    (T + "stagekit.py", "aec03c6c"), (T + "addrcheck.py", "207beb0d"), (T + "stagexec.py", "25a1494c"), (T + "stagesim.py", "eb99c6ba"),
    (T + "gscript.py", "1a80236e"), (T + "vigraph.py", "a7eb58c7"), (T + "stage_prerun.py", "9decb20f"), (T + "errorlist_check.py", "2b466a89"),
    (T + "elrule.py", "a5ee7d5c"), (B + "fs_tunnel_naming_table.json", "769ae8d0"), (B + "graph_ring_p5s01_20261009_125622.json", "6716c499"),
    (B + "errorlist_expected_D1_ring_p5s01_20261009_124542.json", "ffc4cf66"), (B + "plan_ring_p5s01a.json", "ed62e8d6"),
    (B + "plan_ring_p5s01a_pred.json", "2e84eb2c"), (B + "plan_ring_p5s01a_licence.json", "323ac8e0"),
    ("tools/recipes/stage_d1_ring_p5s01a.py", "aee20128"), ("tools/recipes/stage_d1_ring_p5s01a_scratch.py", "3b02d9a7"),
    (B + "plan_ring_p5s01b.json", "75a77a00"), (B + "plan_ring_p5s01b_pred.json", "2f2cbcc3"), (B + "plan_ring_p5s01b_licence.json", "e592cf7a"),
    ("tools/recipes/stage_d1_ring_p5s01b.py", "6de2378d"), ("tools/recipes/stage_d1_ring_p5s01b_scratch.py", "9233749f"),
    ("docs/d1/ring-p5.md", "742e54c4")]]
CONFIG = dict(pins=PINS, snap_path=P(B + "diag_c156_b2_2_inv_c156a21_snap.json"), card_path=P(B + "cards/task_156-a2-1.json"),
              snap_globs=["tools/recipes/stage_d1_ring_p4*.py", B + "plan_ring_p4*.json", "tools/hooks/**/*"],
              snap_label="P4 recipes / plans / preds + tools/hooks/**",
              exempt={P(B + "memory_model.json"): "c87d170a", P(B + "adopted_scratch.jsonl"): "dd0aa787"},
              main_recipe=P("tools/recipes/stage_d1_ring_p5s02a.py"), listing_glob="D1_ring_p5s0*.vi", scratch_globs=("_elc_*", "scratch_c156_*"))
if __name__ == "__main__":
    sys.exit(invcheck.main_inv(**CONFIG))
