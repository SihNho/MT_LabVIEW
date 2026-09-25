r"""diag_c91_step4_click1.py - review archive/peer/2026-09-26-c91-smoke-k1.md section 4's cheapest test, no LabVIEW:
was the pick loop (#15173, site 10) iterating at click 1 of the smoke run, and does a gap >= 350 ms span it?
Anchor: the last site-10 stamp = the Done press; click k is at the wall-clock offset read from the v5 click file.
Also syntax-checks the step-4 scripts (ast.parse) and prints hwndCapture per pick click from the clicks json.
    py tools/bench/diag_c91_step4_click1.py [smoke_dir] [clicks_json]
"""
import ast, json, os, statistics, struct, sys
HERE = os.path.dirname(os.path.abspath(__file__))
D = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "t0_legs", "smoke_20260926_060544")
CJ = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, "m8_v5_replay_s1_r30_clicks.json")
for f in ("diag_c91_step4.py", "diag_c91_step4_leg.py", "diag_c91_step4_stats.py"):
    ast.parse(open(os.path.join(HERE, f)).read()); print("AST OK", f)
p = [x for x in os.listdir(D) if x.startswith("t0_site10_")][0]
b = open(os.path.join(D, p), "rb").read(); v = struct.unpack("<%dq" % (len(b) // 8), b); f, t = v[0], v[1:]
end = t[-1]; rel = [(x - end) / f for x in t]; gaps = [(t[i + 1] - t[i]) / f for i in range(len(t) - 1)]
print("site10 n=%d span=%.2fs first_rel=%.2fs gap median=%.2fms max=%.1fms" % (len(t), (t[-1] - t[0]) / f, rel[0], statistics.median(gaps) * 1e3, max(gaps) * 1e3))
print("gaps>100ms (t_rel_s, ms):", [(round(rel[i], 2), round(g * 1e3, 1)) for i, g in enumerate(gaps) if g > 0.1][:40])
# click times from the clicks json: entries with 't' (epoch) and 'why' containing 'bead'
try:
    cj = json.load(open(CJ)); ents = cj if isinstance(cj, list) else cj.get("clicks") or cj.get("probes") or list(cj.values())
    print("clicks json keys:", list(cj.keys())[:20] if isinstance(cj, dict) else "list %d" % len(cj))
except Exception as e:                                                         # noqa: BLE001
    print("clicks json read failed", repr(e)); ents = []
txt = open(CJ, encoding="utf-8", errors="replace").read()
import re
for m in re.finditer(r'"hwndCapture":\s*(\d+)', txt): pass
caps = re.findall(r'"hwndCapture":\s*(\d+)', txt); print("hwndCapture values in order:", caps)
whys = re.findall(r'"why":\s*"([^"]{0,60})', txt); print("whys:", whys[:12])
ts = re.findall(r'"t(?:_press|_down|ime)?":\s*([0-9]{10}\.[0-9]+)', txt); print("epoch stamps found:", len(ts), ts[:6])
for click, name in ((-15.12, "click1 (review: 15.12 s before Done)"), (-12.6, "click2 ~"), (-10.1, "click3 ~")):
    around = [(round(rel[i], 3), round(gaps[i] * 1e3, 1)) for i in range(len(gaps)) if abs(rel[i] - click) < 0.5]
    print(name, "ITERATING" if around else "NO STAMPS", "max gap ms within +-0.5 s:", max([g for _, g in around] or [0]), "n stamps:", len(around))
