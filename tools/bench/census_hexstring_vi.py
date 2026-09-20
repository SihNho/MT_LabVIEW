r"""census_hexstring_vi.py - can vi.lib\Bit Manipulation\Bytes to Lowercase Hex String.vi turn Flatten's binary `data string`
into pure-ASCII hex inside OpConstValue (peer ...-opconstvalue-v1b-bstr-codepage: the BSTR path is code-page lossy; a
hex/U8 route is the fix; no String-To-Byte-Array creator exists in the Erdos Miller library)?

On a SCRATCH copy of OpConstValue_v1.vi: drop the VI, print its terminals, wire Flatten.'data string' (branch) to its
first non-error input, gate the wire uid on both ends and ExecState.
predict: the input is named like 'Bytes'/'bytes' and is a U8 ARRAY -> the string wire is declined or breaks the VI
(ExecState 0); the alternative prediction (string input) gives ExecState 1 and the recipe can use it directly.
The scratch VI is saved (so close_panel raises no dialog) and deleted at the end.

  py tools/bgrun.py --max-min 8 --log tools/bench/census_hexstring_vi.log -- py -u tools/bench/census_hexstring_vi.py
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

walk, term = B.walk, B.term
HEXVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Bit Manipulation\Bytes to Lowercase Hex String.vi"
SCR = os.path.join(g.CLAUDEDEV, "OpConstValue_scratch.vi")


def main():
    g.reset(); com_preflight()
    if os.path.exists(SCR):
        os.remove(SCR)
    shutil.copyfile(OP, SCR); time.sleep(0.3)
    try:
        g.open_panel(SCR); time.sleep(0.8)
        w = walk(SCR, 0)
        fl = next(u for u, v in w.items() if v[1] == "Flatten To String" or any(r["name"] == "anything" for r in v[2]))
        w_data = term(w[fl][2], "data string", True)["wire"]
        print(f"   Flatten uid {fl}, data string wire {w_data}", flush=True)
        before = g.uids(SCR, "SubVI")
        g.drop_subvi(SCR, HEXVI, 0, (2300, 700))
        new = [u for u in g.uids(SCR, "SubVI") if u not in before]
        print(f"   dropped SubVI uids {new}", flush=True)
        w = walk(SCR, 0); hv = new[0]
        print(f"   hex VI label {w[hv][1]!r}; terminals {[(r['i'], r['name'], 'src' if r['is_source'] else 'sink') for r in w[hv][2]]}", flush=True)
        ins = [r for r in w[hv][2] if not r["is_source"] and not r["name"].lower().startswith("error")]
        outs = [r for r in w[hv][2] if r["is_source"] and not r["name"].lower().startswith("error")]
        print(f"   candidate input {ins[0]['name']!r}; outputs {[o['name'] for o in outs]}", flush=True)
        fi = lambda cls, u: [o["uid"] for o in g.report_all(SCR, cls)].index(u)
        try:
            g.wire(SCR, "FlattenString", fi("FlattenString", fl), "data string", "SubVI", fi("SubVI", hv), ins[0]["name"], branch=True)
        except Exception as e:
            print(f"   wire EXC {str(e)[:160]}", flush=True)
        w = walk(SCR, 0)
        a = term(w[fl][2], "data string", True)["wire"]; b = term(w[hv][2], ins[0]["name"], False)["wire"]
        es = g.exec_state(SCR)
        print(f"OBSERVED: data string wire {a}, input wire {b}, same={a == b and a != 0}; ExecState {es}", flush=True)
        if a == b and a != 0 and es == 1:
            print("   VERDICT: STRING input - Flatten.data string -> hex VI is legal; the recipe can use it directly", flush=True)
        else:
            print("   VERDICT: not a plain string input (U8[] likely) - fall back to Unflatten(size?=F) with a U8[] seed", flush=True)
        g.save(SCR); g.close_panel(SCR)
    finally:
        try:
            g.close_panel(SCR)
        except Exception:
            pass
        time.sleep(0.5)
        if os.path.exists(SCR):
            os.remove(SCR); print("   scratch deleted", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
