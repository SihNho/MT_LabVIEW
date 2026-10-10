# ---
# labview: build
# hardware: none
# ---
"""SENTINEL (card chat-X2): stands in for a LabVIEW-touching recipe. It touches NO LabVIEW, opens no port, moves no
motor - it only writes marker_sentinel_lv.txt beside itself. A marker on disk = a guard let it run."""
import os
import time

p = os.path.join(os.path.dirname(os.path.abspath(__file__)), "marker_sentinel_lv.txt")
with open(p, "w", encoding="utf-8") as f:
    f.write("sentinel_lv ran %s\n" % time.strftime("%Y-%m-%d %H:%M:%S"))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
