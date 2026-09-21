"""c74_gate10_report - run the WIDENED gate 10 of `tools/bench/c60c_astcheck.py` over named files and
REPORT the counts. Touches no LabVIEW, opens no COM, reads files only.

WHY IT IS A REPORT AND NOT A GATE. `c60c_astcheck.py` is a LAUNCH CLEARANCE: its `  FAIL  ` rows mean "do
not launch this file", and `guard_peer.py` reads the newest such row as a failed prediction owing a peer
review. The files below are NOT being launched - two of them are finished recipes whose runs are already
on the record - so a finding on them is a MEASUREMENT (plan item 63: a negative measurement is a FACT
line and does not make the log fail), not a refusal to launch. Printing it through the clearance gate
would say something the run does not mean. So this file calls the SAME function, `percent_format_sites`,
and prints its counts with a neutral prefix.

NOTHING NEW IS BUILT: no new checker, no second copy of the grammar, no new device. `SPEC_RE`,
`_spec_count` and `percent_format_sites` are imported from `c60c_astcheck.py` - the one definition.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
# c60c_astcheck parses sys.argv at IMPORT time (its ARGS is module-level), so give it a harmless one.
_SAVED = sys.argv[:]
sys.argv = [os.path.join(HERE, "c60c_astcheck.py"), "diag_s3b_l0_localname_v2.py"]
import c60c_astcheck as A                                                          # noqa: E402
sys.argv = _SAVED

import ast                                                                         # noqa: E402

TARGETS = [os.path.join(ROOT, "tools", "recipes", n) for n in
           ("build_d1_m3a2.py", "build_d1_m3a1.py", "build_d1_routeb_v0.py")]


# The widening is MEASURED before its verdicts on real files are quoted (CLAUDE.md: structural is not
# functional, and a checker that has never fired on its own fixture is an assumption). Each row is
# (source line, what CPython does with it, what the widened gate must say).
FIXTURE = [
    ('x = "%d%" % (1,)', "ValueError: incomplete format", "INVALID"),
    ('x = "50% (of rows): %s" % (n,)', "ValueError: unsupported format character ' '", "INVALID"),
    ('x = "%d%% done" % (n,)', "legal - %% consumes nothing", "clean"),
    ('x = b"%b" % (blob,)', "legal under PEP 461", "bytes-reported, NEVER failed"),
    ('x = "%02d %s %r %.1f %.2f" % (a, b, c, d)', "TypeError: not enough arguments", "MISMATCH"),
    ('x = "%s and %s" % (a, b)', "legal", "clean"),
]


def fixture():
    print("\n--- FIXTURE: what the widened gate says about literals whose CPython behaviour is known",
          flush=True)
    for src, cpython, want in FIXTURE:
        mism, unres, verified, assumed, invalid, byt = A.percent_format_sites(ast.parse(src), "fixture.py")
        got = []
        if mism:
            got.append("MISMATCH")
        if invalid:
            got.append("INVALID")
        if byt:
            got.append("bytes-reported")
        if verified:
            got.append("verified")
        if assumed:
            got.append("assumed")
        if unres:
            got.append("unresolved")
        print("  FIX  %-44s CPython: %-42s -> %-24s (expected %s)"
              % (src, cpython, ",".join(got) or "nothing", want), flush=True)


def main():
    print("=== c74_gate10_report - the WIDENED gate 10 as a MEASUREMENT, not a launch clearance",
          flush=True)
    print("=== source of the check: tools/bench/c60c_astcheck.py percent_format_sites()", flush=True)
    fixture()
    print("", flush=True)
    worst = 0
    for path in TARGETS:
        name = os.path.basename(path)
        if not os.path.exists(path):
            print("  G10  %-26s NOT ON DISK" % name, flush=True)
            continue
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
        mism, unres, verified, assumed, invalid, byt = A.percent_format_sites(tree, path)
        print("  G10  %-26s %4d lines | %3d VERIFIED | %3d ASSUMED | %d MISMATCH | %d INVALID | "
              "%d bytes-reported | %d unresolved"
              % (name, len(src.splitlines()), verified, assumed, len(mism), len(invalid), len(byt),
                 len(unres)), flush=True)
        for m in mism:
            print("       G10 MISMATCH   %s" % m, flush=True)
        for v in invalid:
            print("       G10 INVALID    %s" % v, flush=True)
        for b in byt:
            print("       G10 BYTES      %s" % b, flush=True)
        for u in unres:
            print("       G10 UNRESOLVED %s" % u, flush=True)
        worst += len(mism) + len(invalid)
    print("\n=== G10 REPORT DONE: %d definite defect(s) across %d file(s). This is a measurement; the "
          "launch clearance for any of these files is a separate c60c_astcheck run."
          % (worst, len(TARGETS)), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
