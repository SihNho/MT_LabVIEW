r"""diag_c135_2_restore - card 135-2 pass 1 (PD294(c)): OFFLINE, no LabVIEW. Restore plan_ring_p3b2b.json / _in / _pred from the
snapshots launch_p3b2_c135.py wrote BEFORE its failed finalize (launch_p3b2_c135_pre_*.json, launch_p3b2_c135.log:44).
WHAT EXISTED: the snapshots themselves (written by json.dump indent=1 from the original files, launch_p3b2_c135.py:233-235), so
the bytes are a re-serialisation; the md5 contract is on plan b only (ae6b6111, pinned in launch_p3b2_c135.py:42).
PREDICTION: R1 pre plan b md5 == ae6b6111; R2 after copy plan b md5 == ae6b6111; R3 _in and _pred restored byte-equal to their
snapshots and their JSON loads; R4 the failed finalize's copies kept as *_c135_1_fail.json (never deleted).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c135_2_restore.log -- py -u tools/bench/diag_c135_2_restore.py"""
import hashlib, json, os, shutil, sys                                              # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(B)))
import protocol as P                                                               # noqa: E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                      # noqa: E731
ok, arts = [], []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("  {0}  {1}  {2}".format("PASS" if c else "FAIL", n, d), flush=True)
    return bool(c)


PB_MD5 = "ae6b6111d766a4ba27d0695f29958c23"
names = ("plan_ring_p3b2b.json", "plan_ring_p3b2b_in.json", "plan_ring_p3b2b_pred.json")
src = dict((n, os.path.join(B, "launch_p3b2_c135_pre_" + n)) for n in names)
if gate("R1 snapshot plan b md5 == ae6b6111", md5(src[names[0]]) == PB_MD5, md5(src[names[0]])):
    for n in names:
        dst = os.path.join(B, n)
        fail = dst.replace(".json", "_c135_1_fail.json")
        if not os.path.exists(fail):
            shutil.copyfile(dst, fail)
        print("  FACT  {0}: was {1}, failed copy kept {2} ({3})".format(n, md5(dst), os.path.basename(fail), md5(fail)), flush=True)
        shutil.copyfile(src[n], dst)
        json.load(open(dst, encoding="utf-8"))
        arts.append({"path": "tools/bench/" + n, "md5": md5(dst)})
    gate("R2 plan b restored, md5 == ae6b6111", md5(os.path.join(B, names[0])) == PB_MD5)
    gate("R3 _in and _pred byte-equal to their snapshots", all(md5(os.path.join(B, n)) == md5(src[n]) for n in names[1:]),
         dict((n, md5(os.path.join(B, n))) for n in names[1:]))
    gate("R4 failed copies kept", all(os.path.exists(os.path.join(B, n.replace(".json", "_c135_1_fail.json"))) for n in names))
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), arts)), flush=True)
sys.exit(1 if nf else 0)
