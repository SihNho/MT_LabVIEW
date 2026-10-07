# ---
# labview: none
# hardware: none
# ---
r"""prep_c146_a1_2_hy - card 146-a1-2 step 7 (OFFLINE, housekeeping, PD352(f)). Byte-copies tools/bench/build_opwiringrules_v0_hygiene.json
(57e3bf4d) into tools/bench/op_hygiene/ (directory created if missing; nothing else is created there); the original stays.
PREDICTION CONTRACT: S0 source on its pin; C copy md5 == source; O original still present and unchanged; D op_hygiene lists only files that
  were there before plus this copy.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/prep_c146_a1_2_hy.log -- py -u tools/bench/prep_c146_a1_2_hy.py"""
import hashlib, os, shutil, sys                                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
SRC = os.path.join(ROOT, "tools", "bench", "build_opwiringrules_v0_hygiene.json")
DD = os.path.join(ROOT, "tools", "bench", "op_hygiene")
DST = os.path.join(DD, os.path.basename(SRC))
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, d), flush=True)


gate("S0 source md5 == pin 57e3bf4d", md5(SRC) == "57e3bf4da3f590d2b06dc2a179c37acc", md5(SRC))
before = sorted(os.listdir(DD)) if os.path.isdir(DD) else None
print("FACT op_hygiene before: {0}".format(before), flush=True)
os.makedirs(DD, exist_ok=True)
shutil.copyfile(SRC, DST)
gate("C copy md5 == source", md5(DST) == md5(SRC), (md5(SRC), md5(DST)))
gate("O original present, unchanged", os.path.isfile(SRC) and md5(SRC) == "57e3bf4da3f590d2b06dc2a179c37acc")
after = sorted(os.listdir(DD))
gate("D op_hygiene lists before + this copy only: {0}".format(after), set(after) == set(before or []) | {os.path.basename(SRC)}, after)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [{"path": "tools/bench/op_hygiene/" + os.path.basename(SRC), "md5": md5(DST)}])),
      flush=True)
sys.exit(1 if G["fail"] else 0)
