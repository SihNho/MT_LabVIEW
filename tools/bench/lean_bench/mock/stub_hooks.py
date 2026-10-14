# ---
# labview: none
# hardware: none
# ---
"""Mock queue stand-in for lean_cycle_hooks.py (no motor, no LabVIEW). Fails when <root>/fail_hook_<which>_<tag> exists.
Usage: py stub_hooks.py start|end --tag <tag> --root <root>"""
import json
import os
import sys
import time


def main(argv):
    which = argv[0]
    tag = argv[argv.index("--tag") + 1]
    root = argv[argv.index("--root") + 1]
    fail = os.path.exists(os.path.join(root, "fail_hook_%s_%s" % (which, tag)))
    with open(os.path.join(root, "queue.log"), "a", encoding="utf-8") as f:
        f.write("CYCLE-HOOK | %s | %s | %s | STUB %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), tag, which,
                                                          "FAIL" if fail else "ok"))
    print("RESULT " + json.dumps({"stub_hook": which, "tag": tag, "status": "FAIL" if fail else "PASS"}))
    return 3 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
