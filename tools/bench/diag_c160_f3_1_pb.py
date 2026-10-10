# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_160-f3-1.md
# ---
r"""diag_c160_f3_1_pb - card 160-f3-1 (PD391(g)), OFFLINE measurement before selftest_c134_1_dry is edited. Pure functions only.
EXISTING used, nothing re-written: stagekit.s1_frame_graph / pred_end_graph / pb_check (the PD370(b) converter pos_convert /
pos_convert_open_rows, stagekit.py:1774-1802), vigraph.computation_diff_frame; the end state L = the plan's finalized end step file
(as selftest_t6_poskey.load does). In a dry run DryPlanBE's real end is the sim end, so G1 = the pred end graph here.
PREDICTION:
  M1 recipe stage_d1_ring_p3b2a.py full-file md5 (what T2a computes) = 0d1f0c15...; with its trailing scope header removed = bb5ba064...
  M2 name-keyed cdiff(S1f, sim end) vs the stored 16 pred rows: missing = the four '2626|Terminal|array|0..3' rows, extra = none
  M3 pb_check(S1f, Gend, Gend, stored rows, plan open rows) ok (converted slots equal, converted open pairs == cdiff pairs)
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c160_f3_1_pb.log -- py -u tools/bench/diag_c160_f3_1_pb.py"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                  # noqa: E402
import stagekit as K, vigraph as V, jev_candidates as JC                         # noqa: E401,E402  pure functions only

res = []


def gate(label, ok, detail=""):
    res.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


J = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))               # noqa: E731
rec = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b2a.py")
b = open(rec, "rb").read()
full = hashlib.md5(b).hexdigest()
nl = b"\r\n" if b"\r\n" in b else b"\n"
hdr = nl.join([b"# ---", b"# labview: build", b"# hardware: none", b"# ---", b""])
cands = dict((k, hashlib.md5(x).hexdigest()) for k, x in (("strip_header", b[:-len(hdr)] if b.endswith(hdr) else b""),
                                                           ("strip_header_and_nl", b[:-len(hdr)].rstrip(nl) if b.endswith(hdr) else b"")))
print("FACT recipe full md5", full, "ends with scope header:", b.endswith(hdr), "header-stripped:", cands, flush=True)
gate("M1 full md5 == 0d1f0c15 and the bytes without the scope header == bb5ba064", full.startswith("0d1f0c15")
     and any(v.startswith("bb5ba064") for v in cands.values()), (full, cands))

P = J(K.BENCH, "plan_ring_p3b2a.json")
PRED = J(K.BENCH, "plan_ring_p3b2a_pred.json")
BASE = J(K.ROOT, P["finalized"]["base"]["path"])
sf = P["finalized"]["step_files"][len(P["actions"])]
sp = sf["path"] if os.path.isabs(sf["path"]) else os.path.join(ROOT, sf["path"])
print("FACT end step file", sf["path"], "md5 pin ok:", K.md5(sp) == sf["md5"], flush=True)
L = J(sp)["state"]
LAB = JC.node_labels_default()
FSP = BASE.get("fs_tunnel_pairs", BASE.get("fs_pairs"))
S1f = K.s1_frame_graph(LAB)
Gend = K.pred_end_graph(L, LAB, FSP)
cd = V.computation_diff_frame(S1f, Gend)
rk = sorted(str(y["sink"]) for y in cd["rows"])
miss, extra = sorted(set(PRED["cdiff_rows"]) - set(rk)), sorted(set(rk) - set(PRED["cdiff_rows"]))
print("FACT stored pred rows", len(PRED["cdiff_rows"]), "name-keyed cdiff rows", len(rk), "open_rows", len(P["open_rows"]), flush=True)
print("FACT missing", miss, flush=True)
print("FACT extra", extra, flush=True)
pg = set((int(y["node"]), str(y["sink"]).split("|")[2]) for y in cd["rows"])
pw = set((int(y["node"]), y["term"]) for y in P["open_rows"])
print("FACT open pairs not in cdiff", sorted(pw - pg, key=str), "cdiff pairs not open", sorted(pg - pw, key=str), flush=True)
gate("M2 missing == the four 2626|Terminal|array rows, extra none", not extra and len(miss) == 4
     and all(m.startswith("2626|Terminal|array|") for m in miss), (miss, extra))
r = K.pb_check(S1f, Gend, Gend, PRED["cdiff_rows"], P["open_rows"])
print("FACT pb_check", dict((k, v) for k, v in r.items() if k not in ("cd", "rows", "open_rows")), flush=True)
gate("M3 pb_check (converted stored rows + open pairs) ok", r["ok"], (r["slots_want"], r["slots_got"], r["pairs_want"], r["pairs_got"]))
nf = sum(1 for _l, ok in res if not ok)
print(protocol.result_line({"status": "PASS" if not nf else "FAIL", "gates": {"pass": len(res) - nf, "fail": nf},
                            "first_fail": next((l for l, ok in res if not ok), None), "artefacts": []}), flush=True)
sys.exit(1 if nf else 0)
