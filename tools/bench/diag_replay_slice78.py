"""diag_replay_slice78 - OFFLINE (no LabVIEW). replay_test78.log T1-T3 read a 1024-element U8 array from the harness
(shape (1024,)) instead of the 1024x1280 frame, while call k returns the SAME md5 in get-buff and cal
(b55bee61 / 23816f00 / 4c3aa3a9 for k = 0, 1, 2). Question: which 1024-element slice of source frame f0000k does that
md5 equal? Prediction: at least one named slice matches all three (then the replay VIs return the right frame and
the harness read is at fault); none matching leaves the question open. Ends with a RESULT line."""
import hashlib
import json
import os
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402

GOT = ["b55bee61da7eedcfc526c5016db30d3b", "23816f003e6e014076b6ee84a694d71d", "4c3aa3a9fd11e2e24f82c2ee335128ea"]
M = json.load(open("G:/m8_replay_frames/frames_manifest.json", encoding="utf-8"))
h = lambda a: hashlib.md5(np.ascontiguousarray(a).tobytes()).hexdigest()  # noqa: E731
hits = {}
for i in range(3):
    a = np.asarray(Image.open(os.path.join(M["source_dir"], M["frames"][i]["source"])))
    print("frame", i, a.shape, a.dtype, "min", a.min(), "max", a.max(), flush=True)
    cand = {}
    for j in range(a.shape[1]):
        cand["col%d" % j] = a[:, j]
    for j in range(a.shape[0]):
        cand["row%d" % j] = a[j]
    for n, f in (("mean1", lambda x: x.mean(1)), ("max1", lambda x: x.max(1)), ("min1", lambda x: x.min(1)),
                 ("sum1", lambda x: x.sum(1))):
        cand[n] = f(a)
    for n, x in cand.items():
        for dt in (np.uint8,):
            if h(np.asarray(x).astype(dt)) == GOT[i] or h(np.asarray(x)) == GOT[i]:
                hits.setdefault(i, []).append(n)
    print("frame", i, "matching slices:", hits.get(i, [])[:10], flush=True)
common = set(hits.get(0, [])) & set(hits.get(1, [])) & set(hits.get(2, []))
print("common slice for all three:", sorted(common), flush=True)
print(P.result_line(P.make_result(1 if common else 0, 0 if common else 1,
                                  None if common else "no 1024-element slice of the source frames matches")), flush=True)
