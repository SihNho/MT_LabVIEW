r"""launch_p3b2_c135_graph - child 2 of tools/bench/launch_p3b2_c135.py (card 134-P1, PD290(d)): READ-ONLY FS graph read of the file
session a saved IN THIS CHAIN. Executes tools/bench/diag_c134_1_graph.py's OWN source (md5-pinned 3bd108c5 since card 134-6, card 134-1, the reader
that wrote graph_ring_p3b2a_fs_20261002_102553.json) with FOUR literal substitutions, each required to occur exactly once:
  plan file  diag_c134_1_graph_plan.json -> launch_p3b2_c135_graph_plan.json (written by the runner: input = the a-file + md5,
             same_rows_as = graph_ring_p3b2a_fs_20261002_102553.json; loop/case/fs_watch ids copied from the card-134-1 plan)
  stage name scratch_c134_1_graph_p3b2a -> scratch_c135_graph_p3b2a      out_json diag_c134_1_graph.json -> launch_p3b2_c135_graph.json
  task       card 134-1 (c) -> launch_p3b2_c135 graph read
No edit of the diag (card rule), no new reader. Never saves: Stage.discard_work, byte copy deleted, LabVIEW killed at exit.
EXPECTED GATE PATTERN (card 134-6, PD291(d); diag source 3bd108c5): G1 G2 G3 FS1 B X PASS, rc 0. Gate B is SCOPED: the 7 nested tunnels
(PD288(b)/PD289(a): UNMEASURED) are LISTED as a FACT and fail the gate only if plan b (uses_plan) uses one. R and FS2 are skipped
(same_rows_as / fs_watch null in the runner's plan): the runner compares the graph itself (compare C).
    (child of the runner)  py tools/bgrun.py --material --max-min 15 --log tools/bench/launch_p3b2_c135_graph.log -- py -u tools/bench/launch_p3b2_c135_graph.py"""
import hashlib, os, sys                                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "diag_c134_1_graph.py")
SRC_MD5 = "3bd108c5e07fc002b0f4aae3d44064b4"                       # card 134-6: gate B scoped (was 6a1b61ab)
SUBS = (('"diag_c134_1_graph_plan.json"', '"launch_p3b2_c135_graph_plan.json"'),
        ('"scratch_c134_1_graph_p3b2a"', '"scratch_c135_graph_p3b2a"'),
        ('"diag_c134_1_graph.json"', '"launch_p3b2_c135_graph.json"'),
        ('"card 134-1 (c)"', '"launch_p3b2_c135 graph read"'))


def patched_source():
    raw = open(SRC, "rb").read()
    if hashlib.md5(raw).hexdigest() != SRC_MD5:
        raise SystemExit("SOURCE PIN: {0} md5 {1} != {2}".format(SRC, hashlib.md5(raw).hexdigest(), SRC_MD5))
    txt = raw.decode("utf-8")
    for old, new in SUBS:
        if txt.count(old) != 1:
            raise SystemExit("SUBSTITUTION {0!r} occurs {1}x, not once".format(old, txt.count(old)))
        txt = txt.replace(old, new)
    return txt


if __name__ == "__main__":
    code = compile(patched_source(), SRC, "exec")                  # filename = the diag: tracebacks point at its lines
    exec(code, {"__name__": "__main__", "__file__": SRC})            # noqa: S102 - the pinned diag, four literals changed
