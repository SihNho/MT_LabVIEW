r"""census_unflatten_terms.py - exact terminal list of the Unflatten From String node placed by the fleet creator
OpBuildUnflatten_v0 (needed for the U8/hex route of OpConstValue: does it expose `data includes array or string size?`
and `little-endian?`?). On a SCRATCH copy of OpConstValue_v1.vi; nothing saved; scratch deleted.
predict: 4 sinks (binary string, type, data includes array or string size?, little-endian?) + error in; sources value, error out.

  py tools/bgrun.py --max-min 6 --log tools/bench/census_unflatten_terms.log -- py -u tools/bench/census_unflatten_terms.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402
from build_opconstvalue_v1 import OP, com_preflight  # noqa: E402

walk = B.walk
OP_UNFLAT = os.path.join(g.CLAUDEDEV, "OpBuildUnflatten_v0.vi")
SCR = os.path.join(g.CLAUDEDEV, "OpConstValue_scratch.vi")


def main():
    g.reset(); com_preflight()
    if os.path.exists(SCR):
        os.remove(SCR)
    shutil.copyfile(OP, SCR); time.sleep(0.3)
    try:
        g.open_panel(SCR); time.sleep(0.8)
        inv0 = g.uids(SCR, "Invoke"); before = g.uids(SCR, "FlattenUnflattenString")
        vi = g.op(OP_UNFLAT); vi.SetControlValue("vi path", SCR); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0)
        vi.SetControlValue("location (0, 0)", [2300, 900]); g._run(vi)
        print(f"   creator error: {g._err(vi, 'error out')!r}", flush=True)
        new = [u for u in g.uids(SCR, "FlattenUnflattenString") if u not in before]
        junk = [u for u in g.uids(SCR, "Invoke") if u not in inv0]
        print(f"   new FlattenUnflattenString {new}; junk Invoke {junk}", flush=True)
        w = walk(SCR, 0)
        for u in new:
            print(f"OBSERVED: Unflatten uid {u} label {w[u][1]!r} terminals {[(r['i'], r['name'], 'src' if r['is_source'] else 'sink') for r in w[u][2]]}", flush=True)
    finally:
        try:
            g.close_panel(SCR)
        except Exception as e:
            print(f"   close_panel EXC {str(e)[:100]}", flush=True)
        time.sleep(0.5)
        if os.path.exists(SCR):
            os.remove(SCR); print("   scratch deleted", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
