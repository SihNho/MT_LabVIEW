# ---
# labview: none
# hardware: none
# ---
r"""selftest_t5_termclass - card chat-T5 (PD349(b), OFFLINE, no LabVIEW): the simulator gives a created node the terminal class
LabVIEW reports (tools/stagesim.py measured_term_class over tools/bench/termclass_table.json); stagexec.bind_new still compares
classes EXACTLY.
The op-2 case: bench arms A13 and B, s04v18 op 2 'p4_wait' (Wait (ms), plan declared 'Terminal'), stopped with
  BINDING: Function terminal keys sim {('Terminal', False, 'milliseconds to wait'): 1, ('Terminal', True, 'millisecond timer
  value'): 1} vs real {('ParameterTerminal', True, 'millisecond timer value'): 1, ('ParameterTerminal', False, 'milliseconds to
  wait'): 1}   (V6_bench/B/tools/bench/diag_c144_p4s04v18_scratch.log:197; A13: real node #11081, diag_c145_a3_6)
PREDICTION CONTRACT:
  K1 stagesim.op_create on the arm's own p4_wait action (declared 'Terminal') emits both rows as ParameterTerminal + a note;
  K2 bind_new binds that sim node to the real #11081 rows (the op-2 case binds);
  K3 the OLD sim rows ('Terminal', as the arms simulated) against the same real rows -> ExecStop BINDING (the arms' failure kept);
  K4 a genuinely different real class (OverridableParameterTerminal on 'milliseconds to wait') -> ExecStop BINDING;
  K5 Increment (x -> x+1) gets ParameterTerminal on 'x' and OverridableParameterTerminal on 'x+1' (per row, measured);
  K6 an unmeasured Function terminal set keeps its declared class (no SimError: the Dequeue route and stagesim's synthetic
     selftest nodes are unmeasured by design; X16 + the scratch run guard them);
  K7 an owner class never measured keeps its declared class; Local / DigitalNumericConstant 'Terminal' unchanged; no table ->
     declared class (behaviour before PD349).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_t5_termclass.log -- py -u tools/bench/selftest_t5_termclass.py"""
import copy, os, sys                                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as S        # noqa: E402
import stagexec as X        # noqa: E402
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)


def row(t, name, src, owner, tc, ocls="Function", w=0, fd=29699):
    return {"term_uid": t, "term_name": name, "is_source": src, "wire_uid": w, "owner_uid": owner, "owner_class": ocls,
            "frame_diagram": fd, "term_class": tc}


# the arm A13 plan's action, verbatim in every field the simulator reads (V6_bench/A13/tools/bench/plan_ring_p4_s04v18.json)
ACT = {"op": "create", "id": "p4_wait", "class": "Function", "diagram": 29699, "as": "WT2", "prim": "Wait (ms)",
       "donor": {"donor": r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\OpWaitDonor_v0.vi", "uid": 163},
       "terminals": [{"name": "milliseconds to wait", "is_source": False, "term_class": "Terminal"},
                     {"name": "millisecond timer value", "is_source": True, "term_class": "Terminal"}]}
BASE = [row(500, "x", False, 400, "ParameterTerminal", w=7)]
st = {"objs": [], "terminals": copy.deepcopy(BASE), "sym": {}, "neg": -1, "diagrams": {}, "owners": {}, "loops": []}
sim_prev = copy.deepcopy(st["terminals"])
eff = S.op_create(st, copy.deepcopy(ACT), {}, {}, {})
new = [r for r in st["terminals"] if r["owner_uid"] < 0]
gate("K1 op_create on the arm's p4_wait (declared Terminal) emits ParameterTerminal on both rows + a note",
     sorted((r["term_name"], r["term_class"]) for r in new) == [("millisecond timer value", "ParameterTerminal"),
                                                                 ("milliseconds to wait", "ParameterTerminal")]
     and len((eff if isinstance(eff, dict) else (eff[0] if isinstance(eff, tuple) else {})).get("termclass_measured") or []) == 2,
     [new, eff])
REAL = BASE + [row(11090, "milliseconds to wait", False, 11081, "ParameterTerminal"),
               row(11091, "millisecond timer value", True, 11081, "ParameterTerminal")]


def bind(sim_now, real):
    b = {"obj": {}, "term": {}}
    try:
        return X.bind_new(copy.deepcopy(BASE), real, sim_prev, sim_now, b), b
    except X.ExecStop as e:
        return "STOP: " + str(e), b


made, b = bind(st["terminals"], REAL)
gate("K2 the op-2 case binds: sim node -> real #11081, both terminals mapped",
     isinstance(made, dict) and list(made.values()) == [11081] and sorted(b["term"].values()) == [11090, 11091], [made, b])
old = [dict(r, term_class="Terminal") if r["owner_uid"] < 0 else r for r in st["terminals"]]
made3, _b = bind(old, REAL)
gate("K3 the arms' sim rows ('Terminal') against the same real rows still stop at BINDING",
     isinstance(made3, str) and "BINDING" in made3, made3)
real4 = BASE + [row(11090, "milliseconds to wait", False, 11081, "OverridableParameterTerminal"),
                row(11091, "millisecond timer value", True, 11081, "ParameterTerminal")]
made4, _b = bind(st["terminals"], real4)
gate("K4 a genuinely different real class still refuses (ExecStop BINDING)", isinstance(made4, str) and "BINDING" in made4, made4)
inc = [{"name": "x", "is_source": False}, {"name": "x+1", "is_source": True}]
k5 = [S.measured_term_class("Function", inc, t)[0] for t in inc]
gate("K5 Increment: 'x' ParameterTerminal, 'x+1' OverridableParameterTerminal (measured per row)",
     k5 == ["ParameterTerminal", "OverridableParameterTerminal"], k5)
odd = [{"name": "never measured in", "is_source": False, "term_class": "Terminal"}]
k6a = S.measured_term_class("Function", odd, odd[0])
k6b = S.measured_term_class("Function", [dict(odd[0], term_class="ParameterTerminal")], dict(odd[0], term_class="ParameterTerminal"))
gate("K6 unmeasured Function terminal set keeps its declared class (Terminal / ParameterTerminal), no note",
     k6a == ("Terminal", None) and k6b == ("ParameterTerminal", None), [k6a, k6b])
loc = {"name": "Num", "is_source": True}
k7 = [S.measured_term_class("NoSuchOwnerClass", [loc], dict(loc, term_class="Whatever")),
      S.measured_term_class("Local", [loc], loc), S.measured_term_class("DigitalNumericConstant", [loc], loc),
      S.measured_term_class("Function", ACT["terminals"], ACT["terminals"][0], table={})]
gate("K7 unmeasured owner keeps its class; Local / constant stay Terminal; no table -> declared",
     k7 == [("Whatever", None), ("Terminal", None), ("Terminal", None), ("Terminal", None)], k7)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
