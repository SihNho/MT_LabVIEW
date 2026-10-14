"""p6fix_sum - print the key numbers of p6fix_align json files (offline).  py tools/bench/lean_bench/p6fix_sum.py <json> [...]"""
import json, sys                                                                         # noqa: E401
for p in sys.argv[1:]:
    r = json.load(open(p, encoding="utf-8"))
    a, c, t = r.get("align", {}), r.get("col0", {}), r.get("transrot", {})
    print(p, "| rows B %s matched %s damaged %s incr %s span %s..%s lost %s gaps %s" % (
        a.get("rows_B"), a.get("matched"), a.get("damaged"), a.get("strictly_increasing"), a.get("first_A"), a.get("last_A"),
        a.get("lost_in_span"), a.get("gap_hist")))
    print("   col0 own %s / %s (not own %s, first %s) incr %s lost_from_col0 %s s1gap %s" % (
        c.get("col0_own"), c.get("rows"), c.get("col0_not_own"), c.get("first_not_own", [])[:4], c.get("col0_strictly_increasing"),
        c.get("lost_from_col0"), c.get("s1gap_crosscheck")))
    print("   trans/rot: boundary %s post %s differ %s | init rows %s equal %s first %s last %s range %s nonfinite %s" % (
        t.get("A_init_boundary_row"), t.get("post_init_rows"), t.get("post_init_differ"), t.get("init_rows"),
        t.get("init_rows_equal_A_same_frame"), t.get("init_first"), t.get("init_last"), t.get("B_init_trans_range"), t.get("B_init_nonfinite")))
