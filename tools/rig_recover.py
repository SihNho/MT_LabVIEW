# ---
# labview: read
# hardware: motor
# ---
# labview = close-only (cycle_runner.labview_close_hook) and a tasklist check; never opens or edits a VI.
# hardware = motor_gate.py --session end only (limits RELEASED + readback; no motion); nothing else is sent.
"""rig_recover.py - recover the shared rig lock from a holder that died without cleaning up (user 2026-10-21, debate
riglock-v6 item 11). ONLY on the user's word; the user's words go to the lock log as the reason.

  1. riglock acquire --take-stale (refused if the holder is alive, or in the experiment state - then the user is told
     a stale lock is waiting and nothing is touched; no recovery during an experiment)
     -> the lock is held in the RECOVERING state: permitted() is False, so no measurement or motion can run
  2. checks, each written to its own log:  devices_closed  = LabVIEW closed and verified gone (tasklist)
                                           limits_released = motor_gate --session end (PI / ASI limits released and
                                                             read back; the PI POS / ERR read is in that log)
     The rotor carries no controller limit, so there is nothing to release for it (its position is not read here).
  3. riglock recovered(evidence) - a STRUCTURAL check (every item present, its file exists); it cannot judge content
  4. release the lock. A failed check keeps the lock in RECOVERING and exits 3 - the user must look.
Run backgrounded:  py tools/bgrun.py --max-min 15 --log tools/bench/rig_recover.log -- py -u tools/rig_recover.py --order "<the user's words>"
Exit: 0 recovered and released; 2 refused (nothing touched); 3 a check failed (lock kept, recovering). RESULT line last.
"""
import argparse
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rig_session as RS                                     # noqa: E402  (gate_session, close_labview, riglock)

riglock = RS.riglock


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--order", required=True, help="the user's words ordering the recovery")
    a = ap.parse_args(argv)
    res = {"order": a.order}
    if len(a.order.strip()) < 4:
        res.update(status="REFUSED", why="--order needs the user's words")
        print("RESULT " + json.dumps(res, ensure_ascii=False))
        return 2
    st = riglock.status()
    res["before"] = {"state": (st.get("rig_state") or {}).get("value"), "holder": st.get("holder"),
                     "holder_alive": st.get("holder_alive")}
    try:
        token = riglock.acquire("V6-recover", "recovery: " + a.order, pid=os.getpid(), take_stale=True,
                                reason="user: " + a.order)
    except (riglock.Refused, OSError, RuntimeError, TimeoutError) as e:
        res.update(status="REFUSED", why=str(e))
        RS.say("recovery refused - nothing touched: %s" % e)
        print("RESULT " + json.dumps(res, ensure_ascii=False))
        return 2
    RS.say("lock taken over in RECOVERING (holder V6-recover, pid %d)" % os.getpid())
    stamp = time.strftime("%Y%m%d_%H%M%S")
    env = dict(os.environ, RIGLOCK_TOKEN=token)

    lv_log = os.path.join(RS.LOGDIR, "rig_recover_labview_%s.log" % stamp)
    # B4 (user 2026-10-21 "승인"): only the LabVIEW the dead holder's job started (COM-launched after it began) is
    # closed; any other LabVIEW may be a user's - left running, and the lock stays RECOVERING for the user to look
    lv_ok, lv_why = RS.close_labview(lv_log, (st.get("holder") or {}).get("created") or 0)
    tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True,
                        errors="replace").stdout
    gone = "LabVIEW.exe" not in tl
    with open(lv_log, "a", encoding="utf-8") as f:
        f.write("close: %s %s\ntasklist after:\n%s\nLABVIEW GONE: %s\n" % (lv_ok, lv_why, tl, gone))
    RS.say("devices_closed: LabVIEW gone = %s (%s)" % (gone, lv_why))

    end_log = os.path.join(RS.LOGDIR, "rig_recover_end_%s.log" % stamp)
    end_ok, tail = RS.gate_session("end", env, end_log)
    RS.say("limits_released: %s %s" % ("OK" if end_ok else "FAILED", " / ".join(tail)))

    evidence = {}
    if lv_ok and gone:
        evidence["devices_closed"] = lv_log
    if end_ok:
        evidence["limits_released"] = end_log
    res["evidence"] = evidence
    try:
        riglock.recovered(token, evidence)
    except riglock.Refused as e:
        res.update(status="CHECK-FAILED", why=str(e), lock="KEPT (recovering)")
        RS.say("recovery NOT complete - lock kept in RECOVERING: %s" % e)
        print("RESULT " + json.dumps(res, ensure_ascii=False))
        return 3
    riglock.release(token)
    RS.say("recovered (structural check: every item recorded) and released")
    res.update(status="PASS", lock="released")
    print("RESULT " + json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
