r"""prep_c143_6_probe - card 143-6 (OFFLINE, read-only): which terminal rows the simulated wires of s03 actions 7/8 (p4_w_b_arr src
'new:LRB1.value', p4_w_b_out dst 'new:LWB1.value') landed on in sim/ring_p4_s03v18 step files - name 'BufDiff' or something else.
PREDICTION: each of LRB1 / LWB1 owns exactly one terminal row, named 'BufDiff', and after step 8 that row carries a wire uid."""
import json, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
S = os.path.join(ROOT, "tools", "bench", "sim", "ring_p4_s03v18")
G = {"pass": 0, "fail": 0, "first": None}
ok = True
for fn, key, sym in (("step_07_wire.json", "src_term_uid", "LRB1"), ("step_08_wire.json", "dst_term_uid", "LWB1")):
    d = json.load(open(os.path.join(S, fn), encoding="utf-8"))
    st, tu = d["state"], d["effect"][key]          # the Local end of the simulated wire, from the step's own effect record
    hit = [r for r in st.get("terminals") or [] if r.get("term_uid") == tu]
    own = hit and int(hit[0]["owner_uid"])
    rows = [r for r in st.get("terminals") or [] if own is not None and int(r["owner_uid"]) == own]
    print("FACT", fn, sym, d["action"].get("src") if key == "src_term_uid" else d["action"].get("dst"), "-> term_uid", tu, "owner", own,
          "owner rows", [(r.get("term_uid"), r.get("term_name"), r.get("is_source"), r.get("wire_uid"), r.get("owner_class")) for r in rows],
          "sym keys with", sym, [k for k in (st.get("sym") or {}) if sym in str(k)][:6])
    ok = ok and len(rows) == 1 and rows[0].get("term_name") == "BufDiff" and rows[0].get("owner_class") == "Local" and bool(rows[0].get("wire_uid"))
G["pass" if ok else "fail"] += 1
G["first"] = None if ok else "LRB1/LWB1 '.value' end = the Local's one row 'BufDiff', wired"
print("GATE {0} | LRB1/LWB1 '.value' end = the Local's one row named 'BufDiff', wired (steps 7/8)".format("PASS" if ok else "FAIL"))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
