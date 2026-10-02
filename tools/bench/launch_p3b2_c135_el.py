r"""launch_p3b2_c135_el - child 4 of tools/bench/launch_p3b2_c135.py (card 134-P1, PD290(d)): the FULL Error List read (--role final,
per-item double-click) of P3b-2's FINAL file saved by session b in this chain (launch_p3b2_c135_state.json `b_file`/`b_md5`).
Reader = tools/errorlist_check.py main() UNCHANGED; the only wrap is max_steps 180 on its E.read, exactly as
tools/bench/stage_d1_ring_p3b1_el.py:93-97 (card 131-6, 53 items). --expected = the errorlist_expected_<stem>.json recipe b wrote
(predicted_total 53, a placeholder: the class range is tools/bench/errorlist_expect_p3b2ab.json 49..52). The RANGE and PER-CLASS
lo..hi gates are the runner's (it reads the reader's JSON); this child prints the reader's verdict and its JSON path only.
NEEDS flags.gui (GUI reader, Ctrl+E/Ctrl+L, Esc). Never saves or runs a VI; scratch copy made and deleted by the reader.
    (child of the runner)  py tools/bgrun.py --material --max-min 40 --log tools/bench/launch_p3b2_c135_el.log -- py -u tools/bench/launch_p3b2_c135_el.py"""
import json, os, sys                                                                 # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC                                                         # noqa: E402
STATE = os.path.join(ROOT, "tools", "bench", "launch_p3b2_c135_state.json")

if __name__ == "__main__":
    st = json.load(open(STATE, encoding="utf-8")) if os.path.exists(STATE) else {}
    NEW, PIN = st.get("b_file"), st.get("b_md5")
    if not (NEW and os.path.exists(NEW) and EC.md5(NEW) == PIN):
        print("NO FINAL: state b_file {0!r} md5 {1!r} missing or changed; nothing opened".format(NEW, PIN), flush=True)
        sys.exit(2)
    EXP = os.path.join(ROOT, "tools", "bench", "errorlist_expected_%s.json" % os.path.splitext(os.path.basename(NEW))[0])
    EC._lv_imports()
    E, _orig = EC.E, EC.E.read

    def _read(*a, **k):
        k["max_steps"] = 180
        return _orig(*a, **k)
    E.read, sys.argv = _read, [sys.argv[0], "--vi", NEW, "--expected", EXP, "--role", "final"]
    sys.exit(EC.main())
