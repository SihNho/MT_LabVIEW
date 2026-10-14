r"""p64p1_fcdonor - a First Call? DONOR file for the wrapper build (no donor exists in the bed, the background-VI copies or the
NI examples / vi.lib scanned by p64p1_lvprobe). Two steps around ONE Quick Drop placed through tools/lv_gui.ps1:
    py tools/bench/lean_bench/p64p1_fcdonor.py open   -> byte copy of EMPTY_v0 = claudeDev\bench\lean\FirstCallDonor_<ts>.vi,
                                                         fresh LabVIEW, its front panel opened (LabVIEW is LEFT RUNNING)
    (GUI: Ctrl+E, Quick Drop `First Call?`, one click on the diagram)
    py tools/bench/lean_bench/p64p1_fcdonor.py save   -> exactly one new node whose only terminal is `first call?` (output),
                                                         ExecState 1, saved (claudeDev only), md5 + uid -> p64p1_fcdonor.json;
                                                         LabVIEW killed and verified gone
Nothing else is edited; the donor is only READ by p64p1_build (GObject.Move duplicate from a scratch byte copy of it)."""
import json, os, shutil, subprocess, sys, time                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
EMPTY, EMPTY_MD5 = L.EMPTY, "6544be40470e80763764089fd2767f2a"
REC = os.path.join(HERE, "p64p1_fcdonor.json")


def main(step):
    if step == "open":
        dst = os.path.join(LEAN, "FirstCallDonor_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
        assert K.md5(EMPTY) == EMPTY_MD5, "EMPTY_v0 md5"
        shutil.copyfile(EMPTY, dst)
        assert K.md5(dst) == EMPTY_MD5
        K.mod("bench_prep").restart_labview(); g.reset(); time.sleep(3)                    # noqa: E702
        lv0 = WB.read_live(dst, fs_pairs=[])
        g.open_panel(dst, activate=True)
        json.dump({"path": dst, "owners_before": sorted(set(int(r["owner_uid"]) for r in lv0["terminals"])),
                   "objs_before": len(lv0["objs"])}, open(REC, "w"), indent=1)
        print("OPEN %s (panel open, LabVIEW left running); owners before %r" % (dst, sorted(set(int(r["owner_uid"]) for r in lv0["terminals"]))))
        return 0
    rec = json.load(open(REC))
    dst = rec["path"]
    lv = WB.read_live(dst, fs_pairs=[])
    own = {}
    for r in lv["terminals"]:
        own.setdefault(int(r["owner_uid"]), []).append(r)
    new = dict((u, rs) for u, rs in own.items() if u not in rec["owners_before"])
    print("NEW owners %r" % dict((u, [(r["owner_class"], r["term_name"], r["is_source"]) for r in rs]) for u, rs in new.items()))
    fc = [u for u, rs in new.items() if [(str(r["term_name"]).lower(), bool(r["is_source"])) for r in rs] == [("first call?", True)]]
    ok = len(new) == 1 and len(fc) == 1
    es = g.exec_state(dst)
    print("CHECK one new node, only terminal `first call?` (output): %s; ExecState %s" % (ok, es))
    if ok and es == 1:
        g.save(dst)
        rec.update({"uid": fc[0], "md5": K.md5(dst), "class": new[fc[0]][0]["owner_class"], "saved": True})
        print("SAVED %s md5 %s uid %d" % (dst, rec["md5"], fc[0]))
    else:
        rec.update({"saved": False})
    json.dump(rec, open(REC, "w"), indent=1)
    g.reset()
    subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
    time.sleep(6)
    gone = "LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
    print("LabVIEW gone: %s" % gone)
    print("RESULT %s" % json.dumps({"fcdonor": "PASS" if rec.get("saved") and gone else "FAIL", "uid": rec.get("uid"), "md5": rec.get("md5")}))
    return 0 if rec.get("saved") else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
