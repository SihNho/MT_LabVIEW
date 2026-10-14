"""p6fix_cal - offline: cal001 of two run dirs compared OUTSIDE the date/time field with each side's own field position and length
(m8b_replay_compare.cal_field, the same walk as B2). B2 compares by absolute offset, so a field one byte longer (e.g. '오후 11:55:22' vs
'오후 2:33:18') shifts every later byte and B2 counts them; here: bytes before the field equal, bytes after it equal when aligned.
    py tools/bench/lean_bench/p6fix_cal.py <run dir A> <run dir B>"""
import json, os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import m8b_replay_compare as M                                                            # noqa: E402
a, b = M.cal(sys.argv[1]), M.cal(sys.argv[2])
tds, top = M.cal_type()
fa, fb = M.cal_field(a, tds, top), M.cal_field(b, tds, top)
ea, eb = fa["field_offset"] + fa["field_length"], fb["field_offset"] + fb["field_length"]
r = {"A_field": [fa["field_offset"], fa["field_length"], fa.get("text")], "B_field": [fb["field_offset"], fb["field_length"], fb.get("text")],
     "consumed_exactly": [fa.get("consumed_exactly"), fb.get("consumed_exactly")],
     "before_field_equal": a[:fa["field_offset"]] == b[:fb["field_offset"]], "after_field_equal": a[ea:] == b[eb:],
     "after_field_bytes": [len(a) - ea, len(b) - eb]}
r["outside_field_identical"] = bool(r["before_field_equal"] and r["after_field_equal"] and all(r["consumed_exactly"]))
print(json.dumps(r, ensure_ascii=False))
