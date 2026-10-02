"""card 133-5: keep byte copies of the PROVISIONAL session-b plan + pred before `--rebase` rewrites them (the launch card rebases
again onto the REAL a-file graph); print md5s. No LabVIEW."""
import hashlib, os, shutil
B = os.path.dirname(os.path.abspath(__file__))
for src, dst in (("plan_ring_p3b2b.json", "plan_ring_p3b2b_provisional_c133_5.json"),
                 ("plan_ring_p3b2b_pred.json", "plan_ring_p3b2b_pred_provisional_c133_5.json")):
    s, d = os.path.join(B, src), os.path.join(B, dst)
    if not os.path.exists(d):
        shutil.copyfile(s, d)
    for p in (s, d):
        print(hashlib.md5(open(p, "rb").read()).hexdigest(), os.path.basename(p))
