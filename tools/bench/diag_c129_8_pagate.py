r"""diag_c129_8_pagate - card 129-8 P4: ask guard_cycle.premature_build() OFFLINE whether the edited P3b-1 recipe's launch
command would be refused for want of a prior-art review on its new bytes. Calls the function only; launches nothing.
    py -u tools/bench/diag_c129_8_pagate.py"""
import os, sys                                                                      # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks")); sys.path.insert(0, os.path.join(ROOT, "tools"))   # noqa: E702
import guard_cycle as GC, protocol as PR                                            # noqa: E401,E402
CMD = "py tools/bgrun.py --material --max-min 50 --log tools/bench/stage_d1_ring_p3b1.log -- py -u tools/recipes/stage_d1_ring_p3b1.py"
r = GC.premature_build(CMD)
print("PAGATE premature_build -> {0}".format("ALLOWED (None)" if r is None else "REFUSED: " + r.replace("\n", " | ")[:600]), flush=True)
print(PR.result_line(PR.make_result(1, 0, None if r is None else "prior-art demanded: " + r.splitlines()[0][:150])), flush=True)
