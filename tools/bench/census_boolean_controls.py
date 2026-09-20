r"""census_boolean_controls.py - which claudeDev harness has a BOOLEAN front-panel control?

Step 0a attempt 4 proved the migration operations (create loop / drop subVI inside / wire a control across the
border / delete the original) but could not answer whether the migrated VI COMPILES: HARNESS_copyloop's only
controls are `Image Name`, `Image Name 2` and `File Path`, so the new While loop's conditional terminal has nothing
to be wired from, and `while_loop` documents that this alone breaks the VI.

`VI:Get Errors` (452) would separate "broken by the unwired conditional" from "broken by the migration", but that
build has FAILED TWICE (toolkit-capabilities.md: the Invoke node comes up with only reference/error terminals).
Grinding on it now would repeat the pattern the cycle-8 retrospective just named. The cheap route instead: run the
probe on a harness that HAS a Boolean, wire the conditional with `exit_while`, and read ExecState directly.

Read-only: each VI is opened by reference and its panel wiring is read. Nothing is created, modified or saved.
  py tools/bgrun.py --max-min 10 --log tools/bench/census_boolean_controls.log -- py -u tools/bench/census_boolean_controls.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
CANDIDATES = ["HARNESS_copyloop.vi", "HARNESS_copyloop0.vi", "HARNESS_copyloopX.vi", "HARNESS_copy0.vi",
              "HARNESS_copy1.vi", "HARNESS_base.vi", "HARNESS_track.vi", "EMPTY_v0.vi", "HARNESS_loadcal.vi"]


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    hits = []
    for name in CANDIDATES:
        p = os.path.join(CLAUDEDEV, name)
        if not os.path.exists(p):
            print(f"{name:28} (missing)", flush=True)
            continue
        try:
            pw = g.panel_wiring(p)
            labels = [c.get("label") for c in pw] if isinstance(pw, list) else []
            try:
                st = g.exec_state(p)
            except Exception:
                st = "?"
            print(f"{name:28} ExecState {st}  controls: {labels}", flush=True)
            # A Boolean is not named in panel_wiring's rows, so the label is the only clue here; report them all
            # and let the caller choose. Names that read Boolean-ish are flagged, never assumed.
            for lab in labels:
                if lab and any(k in lab.lower() for k in ("stop", "bool", "enable", "flag", "done", "run")):
                    hits.append((name, lab))
        except Exception as e:
            print(f"{name:28} panel_wiring raised: {e}", flush=True)
    print(f"\nBoolean-looking candidates (by LABEL only - not verified as Boolean): {hits}", flush=True)
    g._lv = None
    return 0


if __name__ == "__main__":
    sys.exit(main())
