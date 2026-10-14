r"""fr90_c2_check - offline check of task fr90 retry 1 C2 (fr90_locate's display box check). No LabVIEW, no camera.
Runs fr90_locate.locate_image_display on saved v5 "before picks" captures (the panel rect as in the run-1 offline test,
(0, 51, 1920, 1080)) and box_check on synthetic boxes (exact, +-5 edge, +-6 / shifted, None).
    py tools/bench/lean_bench/fr90_c2_check.py <png> [<png> ...]"""
import os, sys                                                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fr90_locate as FL                                                                  # noqa: E402

bad = 0
for png in sys.argv[1:]:
    box, line = FL.locate_image_display(png, (0, 51, 1920, 1080))
    print("CAPTURE %s -> %s" % (os.path.basename(png), "box %s" % (box,) if box else "None (stop before any pick)"), flush=True)
r = FL.REC_RECT
for name, b, want in [("exact recorded rect", r, True), ("every side +5", tuple(x + 5 for x in r), True),
                      ("every side -5", tuple(x - 5 for x in r), True), ("left +6", (r[0] + 6,) + r[1:], False),
                      ("bottom -6", r[:3] + (r[3] - 6,), False), ("shifted 40 px right", (r[0] + 40, r[1], r[2] + 40, r[3]), False),
                      ("run-1 band (678,585,873,587)", (678, 585, 873, 587), False), ("nothing found", None, False)]:
    ok, txt = FL.box_check(b)
    bad += ok != want
    print("SYNTH %-30s ok=%s want=%s %s  %s" % (name, ok, want, "OK" if ok == want else "WRONG", txt), flush=True)
print("C2 SYNTH %s" % ("PASS" if not bad else "FAIL"), flush=True)
sys.exit(1 if bad else 0)
