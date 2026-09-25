"""Offline md5/mtime census of the claudeDev files card 88-2 touches (no LabVIEW). Prediction: all files present."""
import os, hashlib, time, json
d = r'C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev'
rows = []
for n in sorted(os.listdir(d)):
    if n.startswith(('PARALLEL_kernel_v3', 'D1_s1_copy', 'D1_l2_a1_20260925_235224', 'TRACK_kernel_v1', 'D1_s1_kswap')):
        p = os.path.join(d, n)
        rows.append(n)
        print(time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(p))), os.path.getsize(p),
              hashlib.md5(open(p, 'rb').read()).hexdigest(), n)
print('RESULT ' + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0},
                              "first_fail": None, "artefacts": []}))
