# ---
# labview: none
# hardware: none
# ---
r"""diag_c145_a2_1_table - card 145-a2-1 step 5 (OFFLINE, read-only): the input table of RingPickSlot_v0 (6fcf153f) and RingSeqCheck_v0
(0295a8d3) at their real s04 drops PS1 #29719 / SQ1 #29724, from the graph read of the ADOPTED file (graph_ring_p4s04_*.json carrying md5
95e408ff): every terminal row owned by the two nodes, its name, is_source, wire_uid. Pane index per input = the build logs' read-back
(build_ringpickslot_v2.log:128, build_ringseqcheck_v0.log:216). Requiredness is NOT read here (no WiringRules[] reader exists; reported UNREAD).
PREDICTION: the graph file exists with md5 95e408ff; PS1 has 2 input rows (Num, last), SQ1 has 5 (n1, n2, last, Latest, discards);
  PS1 inputs all wired; SQ1 n1 + last wired, n2 / Latest / discards unwired (plan_ring_p4_s04v18.json wires only new:PS1.Num/.last, new:SQ1.n1/.last).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c145_a2_1_table.log -- py -u tools/bench/diag_c145_a2_1_table.py"""
import glob, json, os, sys                                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
VIM = "95e408ff14a406edd3f16b32ba7324f1"
PANE = {29719: ("RingPickSlot_v0", "build_ringpickslot_v2.log:128", {"Num": 11, "last": 10, "min Num": 3, "min slot": 2, "found": 1}),
        29724: ("RingSeqCheck_v0", "build_ringseqcheck_v0.log:216", {"n1": 11, "n2": 10, "last": 9, "Latest": 8, "discards": 7,
                                                                       "next last": 3, "next discards": 2, "valid": 1})}
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


gs = [p for p in sorted(glob.glob(os.path.join(B, "graph_ring_p4s04_*.json")), key=os.path.getmtime)
      if json.load(open(p, encoding="utf-8")).get("md5") == VIM]
gate("graph file of the adopted file (md5 95e408ff) exists", bool(gs), gs)
if gs:
    gr = json.load(open(gs[-1], encoding="utf-8"))
    print("FACT graph {0}".format(os.path.relpath(gs[-1], ROOT)), flush=True)
    unw = {}
    for nu, (vi, cite, pane) in PANE.items():
        rows = [r for r in gr["terminals"] if int(r.get("owner_uid") or 0) == nu]
        print("FACT #{0} {1}: {2} terminal rows".format(nu, vi, len(rows)), flush=True)
        for r in rows:
            nm = r.get("term_name")
            print("ROW | {0} | {1} | pane {2} ({3}) | {4} | wired {5} (wire {6}) | term #{7} | requiredness UNREAD".format(
                vi, nm, pane.get(nm, "-"), cite, "output" if r.get("is_source") else "input", bool(r.get("wire_uid")), r.get("wire_uid"),
                r.get("term_uid")), flush=True)
        ins = [r for r in rows if not r.get("is_source") and r.get("term_name") in pane]
        unw[vi] = sorted(r["term_name"] for r in ins if not r.get("wire_uid"))
        print("FACT {0} inputs {1}; unwired {2}".format(vi, sorted(r["term_name"] for r in ins), unw[vi]), flush=True)
    gate("PS1 inputs Num, last both wired", unw.get("RingPickSlot_v0") == [], unw.get("RingPickSlot_v0"))
    gate("SQ1 unwired inputs == Latest, discards, n2", unw.get("RingSeqCheck_v0") == ["Latest", "discards", "n2"], unw.get("RingSeqCheck_v0"))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
