"""diag_c135_3_plandiff - card 135-3 pass 0/0b: review r2's discriminating test (offline, no LabVIEW, no COM).

Prior art checked: launch_p3b2_resume_c135_compare.py compares GRAPHS (graph_key), not plans; diag_c135_2_resim
re-simulated ae6b6111 on 102553. Nothing diffs the plan finalized on 123012 (fae25fb3) against ae6b6111 -> this file.

A. plan_ring_p3b2b_c135_1_fail.json (fae25fb3, finalized on 123012) vs plan_ring_p3b2b.json (ae6b6111, on 102553):
   full recursive diff; a differing JSON path is IGNORABLE only if one of its keys is in {base, md5, path, goal, at}.
B. sim/ring_p3b2b_c135_1_fail/step_*.json vs sim/ring_p3b2b/step_*.json: the 'state' object of each step,
   same rule; also the full files (reported, not gated).
PREDICTION (card 0b): A non-ignorable diffs = 0 and B state diffs = 0 on all 19 steps. Anything else -> FAIL.
"""
import glob, hashlib, json, os, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402

IGN = {"base", "md5", "path", "goal", "at"}
B = os.path.join(ROOT, "tools", "bench")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def diff(a, b, pre=()):
    out = []
    if isinstance(a, dict) and isinstance(b, dict):
        for k in sorted(set(a) | set(b), key=str):
            if k not in a:
                out.append((pre + (k,), "<absent>", b[k]))
            elif k not in b:
                out.append((pre + (k,), a[k], "<absent>"))
            else:
                out += diff(a[k], b[k], pre + (k,))
    elif isinstance(a, list) and isinstance(b, list):
        if len(a) != len(b):
            out.append((pre + ("len",), len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            out += diff(x, y, pre + (i,))
    elif a != b:
        out.append((pre, a, b))
    return out


def split(ds):
    ign = [d for d in ds if any(isinstance(k, str) and k in IGN for k in d[0])]
    real = [d for d in ds if d not in ign]
    return ign, real


def show(d):
    s = "/".join(str(k) for k in d[0]) + " : " + json.dumps(d[1], default=str)[:120] + " -> " + json.dumps(d[2], default=str)[:120]
    return s


fail_p = os.path.join(B, "plan_ring_p3b2b_c135_1_fail.json")
good_p = os.path.join(B, "plan_ring_p3b2b.json")
print("A files: fail %s md5 %s | b %s md5 %s" % (os.path.basename(fail_p), md5(fail_p), os.path.basename(good_p), md5(good_p)))
pa, pb = json.load(open(fail_p, encoding="utf-8")), json.load(open(good_p, encoding="utf-8"))
print("A top keys fail:", sorted(pa) if isinstance(pa, dict) else type(pa))
ign, real = split(diff(pa, pb))
print("A ignorable diffs: %d" % len(ign))
for d in ign[:40]:
    print("  IGN  " + show(d))
print("A NON-ignorable diffs: %d" % len(real))
for d in real[:60]:
    print("  REAL " + show(d))

sf = sorted(glob.glob(os.path.join(B, "sim", "ring_p3b2b_c135_1_fail", "step_*.json")))
sg = sorted(glob.glob(os.path.join(B, "sim", "ring_p3b2b", "step_*.json")))
print("B step files: fail %d, b %d; names equal %s" % (len(sf), len(sg), [os.path.basename(x) for x in sf] == [os.path.basename(x) for x in sg]))
n_state_real = n_state_steps = 0
for f, g in zip(sf, sg):
    jf, jg = json.load(open(f, encoding="utf-8")), json.load(open(g, encoding="utf-8"))
    st_f, st_g = (jf.get("state") if isinstance(jf, dict) else None), (jg.get("state") if isinstance(jg, dict) else None)
    si, sr = split(diff(st_f, st_g))
    fi, fr = split(diff(jf, jg))
    flag = "" if not sr else "  <-- STATE DIFF"
    print("  %s state=%s md5 %s/%s state ign %d real %d | file ign %d real %d%s" % (
        os.path.basename(f), "present" if st_f is not None else "ABSENT", md5(f)[:8], md5(g)[:8], len(si), len(sr), len(fi), len(fr), flag))
    for d in sr[:10]:
        print("      SREAL " + show(d))
    for d in [x for x in fr if x not in sr][:5]:
        print("      FREAL " + show(d))
    for d in si[:3]:
        print("      SIGN  " + show(d))
    if sr:
        n_state_steps += 1
        n_state_real += len(sr)
for nm in ("summary.json", "candidates.json"):
    f, g = os.path.join(B, "sim", "ring_p3b2b_c135_1_fail", nm), os.path.join(B, "sim", "ring_p3b2b", nm)
    if os.path.exists(f) and os.path.exists(g):
        i2, r2 = split(diff(json.load(open(f, encoding="utf-8")), json.load(open(g, encoding="utf-8"))))
        print("  %s md5 %s/%s ign %d real %d (reported, not gated)" % (nm, md5(f)[:8], md5(g)[:8], len(i2), len(r2)))
        for d in r2[:8]:
            print("      REAL " + show(d))

gates = [("A plan non-ignorable diffs == 0", len(real) == 0),
         ("B step count 19 == 19", len(sf) == len(sg) == 19),
         ("B state non-ignorable diffs == 0 on every step", n_state_real == 0)]
for lab, ok in gates:
    print("GATE %s %s" % ("PASS" if ok else "FAIL", lab))
npass = sum(1 for _, ok in gates if ok)
ff = next((lab for lab, ok in gates if not ok), None)
print("SUMMARY A real %d ign %d | B steps with state diff %d (rows %d)" % (len(real), len(ign), n_state_steps, n_state_real))
print(protocol.result_line(protocol.make_result(npass, len(gates) - npass, ff)))
