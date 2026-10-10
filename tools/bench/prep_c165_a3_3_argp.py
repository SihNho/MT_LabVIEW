# ---
# labview: none
# hardware: none
# evidence: tools/bgrun.py:148-166
# ---
r"""prep_c165_a3_3_argp - card 165-3-3 (OFFLINE): does bgrun's argument parser (tools/bgrun.py:148-166: --max-min, --log, --detach, --material,
--retry-card, REMAINDER cmd) accept the brief's scratch form with `--unverified-card <card>` BEFORE `--`? The parser is built inside bgrun.main()
(not importable), so the same add_argument spec is restated here to measure argparse's behaviour; launches nothing.
PREDICTION: none (measurement). Prints ACCEPT/REJECT for the brief form and the step-4 form (flag after the recipe path).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/prep_c165_a3_3_argp.log -- py -u tools/bench/prep_c165_a3_3_argp.py"""
import argparse, shlex                                                                      # noqa: E401
FORMS = {"brief": "--material --max-min 50 --unverified-card tools/bench/cards/task_165-3-4.json --log tools/bench/diag_c165_p5s02e_scratch.log "
                  "-- py -u tools/recipes/stage_d1_ring_p5s02e_scratch.py",
         "step4": "--material --max-min 50 --log tools/bench/diag_c165_p5s02e_scratch.log -- py -u tools/recipes/stage_d1_ring_p5s02e_scratch.py "
                  "--unverified-card tools/bench/cards/task_165-3-4.json"}
ok = 0
for k, s in FORMS.items():
    ap = argparse.ArgumentParser(exit_on_error=False)
    ap.add_argument("--max-min", type=float, required=True)
    ap.add_argument("--log", required=True)
    ap.add_argument("--detach", action="store_true")
    ap.add_argument("--material", action="store_true")
    ap.add_argument("--retry-card", default=None)
    ap.add_argument("cmd", nargs=argparse.REMAINDER)
    try:
        a, extra = ap.parse_known_args(shlex.split(s))
        print("FORM {0}: {1}; cmd {2}; unrecognized {3}".format(k, "REJECT (parse_args errors on unrecognized)" if extra else "ACCEPT", a.cmd, extra), flush=True)
        ok += 1
    except (Exception, SystemExit) as e:                                                    # noqa: BLE001  argparse exits on a missing required arg
        print("FORM {0}: REJECT {1!r}".format(k, e), flush=True)
        ok += 1
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":%d,"fail":0},"first_fail":null,"artefacts":[]}' % ok, flush=True)
