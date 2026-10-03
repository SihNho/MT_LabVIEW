r"""jev_addr_measure_s5 - card chat-S5 (PD337(b)): MEASURE tier (b) (Jev "same terminal?") on the labelled set
tools/bench/addrcheck_labelled.json BEFORE it is switched on (standing Jev rule). Writes tools/bench/addrcheck_jev_measure.json;
addrcheck.jev_switched_on() reads it. Advisory only either way - the answer never binds a terminal. No LabVIEW.
PREDICTION CONTRACT: 18 items answered; accuracy reported (no threshold assumed in advance; switch-on iff >= 0.85).
    py tools/bgrun.py --material --max-min 10 --log tools/bench/jev_addr_measure_s5.log -- py -u tools/bench/jev_addr_measure_s5.py"""
import os, sys                                                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import addrcheck as AC, protocol as PR                                                    # noqa: E401,E402
rec = AC.measure(n=int(os.environ.get("JEV_SAMPLES_S5", "3")), log=lambda s: print(s, flush=True))
answered = sum(1 for r in rec["rows"] if r["p"] is not None)
print("FACT accuracy {0} on {1} items ({2} answered, {3} unknown), switched_on={4}".format(
      rec["accuracy"], rec["n_items"], answered, rec["unknown"], rec["switched_on"]), flush=True)
ok = answered == rec["n_items"]
print(PR.result_line(PR.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "Jev answered {0}/{1}".format(answered, rec["n_items"]),
      [{"path": "tools/bench/addrcheck_jev_measure.json", "md5": PR._md5(AC.MEASURE)}])), flush=True)
