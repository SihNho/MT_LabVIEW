"""camconfig_chain.py - restart LabVIEW (clearing the camera error dialog), then read the camera config from the main VI.
  py tools/bgrun.py --max-min 20 --log tools/bench/read_camera_config.log -- py -u tools/bench/camconfig_chain.py
"""
import os, subprocess, sys
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)
for tag, args, to in (("lv_restart", [os.path.join(TOOLS, "lv_restart.py")], 400),
                      ("read_config", ["-u", os.path.join(TOOLS, "bench", "read_camera_config.py")], 900)):
    try:
        rc = subprocess.run([sys.executable] + args, timeout=to, cwd=ROOT).returncode
    except subprocess.TimeoutExpired:
        rc = "TIMEOUT"
    print(f"#### {tag} rc {rc}", flush=True)
