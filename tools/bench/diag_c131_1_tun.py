"""card 131-1 Part A helper: print every 'tunnels {...}' record (the connect ops' read-back) in the recorded crossing logs.
Read-only, no LabVIEW. PREDICTION: B1/B2/B3 in diag_c126_6_cross.log; A_* in diag_c127_1_fsinner.log; Q* in diag_c126_4_fs.log."""
import json, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
B = os.path.dirname(os.path.abspath(__file__))
n_rec = 0
for fn in ["diag_c126_6_cross.log", "diag_c127_1_fsinner.log", "diag_c126_4_fs.log", "stage_d1_ring_p3b1_scratch_pin2.log",
           "stage_d1_ring_p3b1_scratch_pin3.log"]:
    print("####", fn)
    L = open(os.path.join(B, fn), encoding="utf-8", errors="replace").read().splitlines()
    for n, s in enumerate(L, 1):
        if "; tunnels {" in s:
            j, end = json.JSONDecoder().raw_decode(s[s.index("; tunnels ") + 10:])
            print("   tail:", s[s.index("; tunnels ") + 10 + end:][:300])
            n_rec += 1
            print("==", n, s[:70].strip())
            for k, v in j.items():
                faces = v["faces"] if isinstance(v, dict) else v
                print("  ", k, faces[0][0] if faces else "?", v.get("owner") if isinstance(v, dict) else "",
                      [(f[2], f[3], f[4], f[5]) for f in faces])
import protocol
print(protocol.result_line(protocol.make_result(1 if n_rec else 0, 0 if n_rec else 1, None if n_rec else "no tunnel records")))
