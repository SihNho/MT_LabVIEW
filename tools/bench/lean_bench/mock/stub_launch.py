# ---
# labview: none
# hardware: none
# ---
"""Mock queue stand-in for launch_lean.ps1 (no model, no LabVIEW): writes lean_report_<tag>.md with the RESULT the
scenario (fake.json "launch": {"<tag>": ["PASS", "FAIL", ...]}) gives for this attempt, and a session log.
Usage: py stub_launch.py --task <file> --tag <tag> --root <root>"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))


def main(argv):
    tag = argv[argv.index("--tag") + 1]
    root = argv[argv.index("--root") + 1]
    sc = json.load(open(os.path.join(HERE, "fake.json"), encoding="utf-8"))
    sp = os.path.join(root, "fake_state.json")
    st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
    i = st.get("%s/launch" % tag, 0)
    st["%s/launch" % tag] = i + 1
    json.dump(st, open(sp, "w", encoding="utf-8"))
    seq = (sc.get("launch") or {}).get(tag) or ["PASS"]
    res = seq[min(i, len(seq) - 1)]
    with open(os.path.join(root, "lean_report_%s.md" % tag), "w", encoding="utf-8") as f:
        f.write("# stub report %s attempt %d\n\nRESULT %s\n" % (tag, i + 1, json.dumps({tag: res, "minutes": 0})))
    with open(os.path.join(root, "session_%s.log" % tag), "w", encoding="utf-8") as f:
        f.write("BGRUN START %s stub\nBGRUN END rc=0 after 0s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("RESULT " + json.dumps({"stub_launch": tag, "attempt": i + 1, "result": res}))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
