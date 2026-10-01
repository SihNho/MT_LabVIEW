r"""diag_c132_1_m1 - card 132-1: full per-key diff of selftest_namegate_c132_1 M1 (pin4 NEWOBJ tunnel rows vs ring_p3b1 sim
step_00 -> step_31), plus which real tunnel owners' uids are NOT new (< the first created uid). Offline, read-only."""
import json, os, re, sys                                                             # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(B)), "tools"))
import stagexec as SX                                                                # noqa: E402
NEWOBJ = re.compile(r"NEWOBJ uid (\d+) class (\w+) \| owner #(\d+) (\w+) frame (\d+) term '(.*)' src (True|False) wire (\d+)")
real = []
for ln in open(os.path.join(B, "stage_d1_ring_p3b1_scratch_pin4.log"), encoding="utf-8", errors="replace"):
    m = NEWOBJ.search(ln)
    if m:
        real.append(dict(term_uid=int(m.group(1)), term_class=m.group(2), owner_uid=int(m.group(3)), owner_class=m.group(4),
                         frame=int(m.group(5)), term_name=m.group(6), is_source=m.group(7) == "True", wire=int(m.group(8))))
sim = lambda n: json.load(open(os.path.join(B, "sim", "ring_p3b1", n), encoding="utf-8"))["state"]["terminals"]   # noqa: E731
s0, s31 = sim("step_00_base.json"), sim("step_31_wire_remove_loose_ends.json")
ok, det = SX.tunnel_name_check(s0, s31, [], real)
for k in sorted(set(det["sim"]) | set(det["real"])):
    print(("  " if k not in det["mismatch"] else "XX"), k, "sim", det["sim"].get(k), "real", det["real"].get(k))
seen = set(int(r["term_uid"]) for r in s0)
for r in s31:
    if int(r["term_uid"]) not in seen and str(r.get("owner_class")).endswith("Tunnel"):
        print("SIMNEW", r["term_uid"], r["owner_uid"], r["owner_class"], r["term_class"], r["is_source"], repr(r["term_name"]), r.get("frame_diagram"), r.get("wire_uid"))
for r in real:
    if r["owner_class"].endswith("Tunnel"):
        print("REALNEW", r["term_uid"], r["owner_uid"], r["owner_class"], r["term_class"], r["is_source"], repr(r["term_name"]), r["frame"], r["wire"])
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":0,"fail":0},"first_fail":null,"artefacts":[]}')
