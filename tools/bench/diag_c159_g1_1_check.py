# ---
# labview: none
# hardware: none
# ---
"""Card 159-g1-1 (PD389(f)): call the retro-undisposed gate's OWN parser on the cycle-158 retrospective; no re-implementation.

Prior art: the gate is cycle_runner.retro_undisposed (tools/cycle_runner.py:1031-1052), which calls dispo.disposition_len
(tools/dispo.py:59-64); the hook copy is guard_peer.undisposed (tools/hooks/guard_peer.py:838-855). This script only calls them.
Prediction: heading at line 517; disposition_len >= 80 (real text); retro_undisposed('archive/peer') returns None.
"""
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)
import dispo          # noqa: E402
import cycle_runner   # noqa: E402
import protocol       # noqa: E402

F = os.path.join("archive", "peer", "2026-10-10-retrospective-cycle158.md")
body = open(F, encoding="utf-8", errors="replace").read()
i = dispo.heading_index(body)
line = body[:i].count("\n") + 1 if i >= 0 else None
n_lines = body.count("\n") + (0 if body.endswith("\n") else 1)
left = dispo.disposition_len(body)
verdict = "placeholder" if (left is None or left < 80) else "real text"
peer_dir = os.path.join(ROOT, "archive", "peer")
gate = cycle_runner.retro_undisposed(peer_dir)
files = [os.path.join(peer_dir, x) for x in os.listdir(peer_dir)
         if "retrospective" in x.lower() and x.lower().endswith(".md")]
newest = max(files, key=os.path.getmtime)
print("heading_index", i, "line", line, "file_lines", n_lines)
print("disposition_len", left, "verdict", verdict)
print("newest_retrospective_by_mtime", os.path.relpath(newest, ROOT))
print("retro_undisposed", gate)
ok = [line == 517, verdict == "real text", gate is None]
print(protocol.result_line({"status": "PASS" if all(ok) else "FAIL",
                            "gates": {"pass": sum(ok), "fail": len(ok) - sum(ok)},
                            "first_fail": None if all(ok) else "prediction mismatch", "artefacts": []}))
