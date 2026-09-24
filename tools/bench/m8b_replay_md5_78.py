"""m8b_replay_md5_78 - card 78-3 S3/R3: md5 of the sources, the replay VIs, the swapped copies and the artefacts AFTER both
replay runs (no LabVIEW). Prediction: S1 3e3d23ce, S3 1a11d92a, get-buff 842ecad9, cal afce0d04, buf a89dafc1."""
import hashlib, os, sys                                                                  # noqa: E401
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); sys.path.insert(0, os.path.join(R, "tools"))
import protocol as P                                                                     # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
W = {"D1_s1_copy.vi": "3e3d23cefd3a334001aa9d6156bf1aee", "D1_s3_loop15.vi": "1a11d92aacabf7ec844d65b8af19f39f",
     r"replay\replay_get_buff_image.vi": "842ecad9a6674a5060ebb3d5522751a9",
     r"replay\replay_get_image_cal.vi": "afce0d04346fc58234d28bcc0fc42e55",
     r"replay\replay_imaqdx_get_image_buf.vi": "a89dafc1db03feef7b528f0dd4fcc692"}
EXTRA = [os.path.join(CD, r"replay\D1_s1_replay_20260925_075422.vi"), os.path.join(CD, r"replay\D1_s3_replay_20260925_075422.vi")] + [
    os.path.join(R, p) for p in ("tools/recipes/stage_replay_swap.py", "tools/bench/m8b_replay_78.json", "tools/bench/m8b_replay_compare.py",
                                 "tools/bench/drive_m8.py", "archive/benchmarks/INDEX.md", "tools/bench/stage_replay_swap_78.log",
                                 "tools/bench/plans/plan_replay_swap_78.json")]
h = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
bad = []
for rel, want in W.items():
    got = h(os.path.join(CD, rel)); print("PIN %-45s %s want %s %s" % (rel, got, want, "OK" if got == want else "DIFFERS"))
    if got != want:
        bad.append(rel)
for p in EXTRA:
    print("MD5 %s  %s" % (h(p), p))
print(P.result_line(P.make_result(len(W) - len(bad), len(bad), bad[0] if bad else None, [])))
