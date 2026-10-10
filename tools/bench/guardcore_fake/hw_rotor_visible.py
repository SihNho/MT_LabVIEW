# ---
# labview: none
# hardware: none
# ---
"""SENTINEL (card chat-X2): has the file name of a motion-capable rotor script (guard_bash MOTOR_BLOCKED_RE matches by
name) but opens no port and moves nothing - it only writes marker_hw_rotor_visible.txt beside itself."""
import os
import time

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marker_hw_rotor_visible.txt")
with open(p, "w", encoding="utf-8") as f:
    f.write("sentinel motor ran %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
