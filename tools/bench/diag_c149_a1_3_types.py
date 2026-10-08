# ---
# labview: read
# hardware: none
# ---
r"""diag_c149_a1_3_types - card 149-a1-3, after diag_c149_a1_3_wire.log: READ the data types of the terminals on the wires session 6 made
around the two moved Quotient&Remainder nodes #10068 / #29240 (new tunnels #30287 '# FD points' / #30290 '# DT points'), in a never-saved
byte copy of claudeDev\D1_ring_p4s06_20261008_174730.vi (569ffbf5). Why: s06 Error List item 6 'source void -> sink long [I32]' (read json
:322) has no s05 counterpart, and its show-error capture (bd_181450_after6.png) highlights a spot at the left edge of a structure near
y=900 while ops 6/7 placed #10068 at (40, 900) and #29240 at (40, 960) (diag_c147_p4s06v18_scratch.log:806,825) - an inference to test.
Same open/close/cleanup as diag_c149_a1_3_wire.py (copied: byte copy, ensure_loaded, gscript.read_term_type only, taskkill, delete copy).
Terminals (from diag_c149_a1_3_cmp.log NEW wires): w30281 t30289 '# FD points' SRC #30287 -> t10080 'y' #10068; w30295 t8936 SRC #686 ->
t30292 #30287 (+ t9662, t10119); w30262 t30293 '# DT points' SRC #30290 -> t29253 'y' #29240; w30304 t28844 SRC #686 -> t30301 #30290;
w30278 t30260 'element' SRC #30240 -> t29256 'x' #29240, t10083 'x' #10068.
PREDICTION CONTRACT: K1/K0/K3 as diag_c149_a1_3_wire; T a type read (bytes) for each listed terminal - the VALUES are the measurement
(not predicted); X input md5 unchanged; G LabVIEW gone; C copy deleted.
    py tools/bgrun.py --material --max-min 8 --log tools/bench/diag_c149_a1_3_types.log -- py -u tools/bench/diag_c149_a1_3_types.py"""
import hashlib, json, os, shutil, subprocess, sys, time                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE); sys.path.insert(0, ROOT)   # noqa: E702
import gscript as g                                                                           # noqa: E402
from tools import protocol                                                                    # noqa: E402
BED = os.path.join(g.CLAUDEDEV, "D1_ring_p4s06_20261008_174730.vi")
BEDM = "569ffbf51eb6051bf0fdb58946f9bb02"
TERMS = (30289, 10080, 8936, 30292, 30293, 29253, 28844, 30301, 30260, 29256, 10083)
COPY = os.path.join(g.CLAUDEDEV, "_c149a13_types_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
OUT = os.path.join(HERE, "diag_c149_a1_3_types.json")
G = {"pass": 0, "fail": 0, "first": None}
R = {"copy": COPY, "types": {}}


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    if not ok and not G["first"]:
        G["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(d)[:700]), flush=True)
    return ok


def lv_running():
    return "LabVIEW.exe" in subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True).stdout


def body():
    gate("K1 input md5 == 569ffbf5", md5(BED) == BEDM, md5(BED))
    if not gate("K0 no LabVIEW running at start", not lv_running()):
        return
    shutil.copyfile(BED, COPY)
    if not gate("K3 byte copy identical", md5(COPY) == BEDM, os.path.basename(COPY)):
        return
    g.ensure_loaded(COPY)
    print("  FACT  ExecState {0}".format(g.exec_state(COPY)), flush=True)
    for u in TERMS:
        try:
            t = g.read_term_type(COPY, u)
        except Exception as e:                                                    # noqa: BLE001
            t = {"err": "%s: %s" % (type(e).__name__, str(e)[:200])}
        ty = t.get("types") or {}
        R["types"][str(u)] = {"hex": t.get("bytes_hex"), "types": ty, "err": t.get("err"), "echo": t.get("echo")}
        tds = [(d.get("name"), d.get("code")) for d in (ty.get("tds") or [])]
        print("  FACT  TYPE t{0}: echo {1} tds {2} top {3!r} sig {4!r} err {5!r}".format(
            u, t.get("echo"), tds, ty.get("top"), str(ty.get("sig"))[:90], t.get("err")), flush=True)
    gate("T a type read for every listed terminal", all(R["types"][str(u)].get("hex") for u in TERMS),
         [u for u in TERMS if not R["types"][str(u)].get("hex")])
    print("  FACT  refs {0}".format(g.ref_counts()), flush=True)


if __name__ == "__main__":
    try:
        body()
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        gate("no exception", False, "%s: %s" % (type(e).__name__, str(e)[:300]))
    finally:
        json.dump(R, open(OUT, "w", encoding="utf-8"), default=str)
        subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True)
        for _ in range(20):
            if not lv_running():
                break
            time.sleep(1)
        gate("G LabVIEW gone", not lv_running())
        if os.path.exists(COPY):
            try:
                os.remove(COPY)
            except OSError as e:
                print("  FACT  copy delete failed: %s" % e, flush=True)
        gate("C copy deleted", not os.path.exists(COPY), os.path.basename(COPY))
        gate("X input md5 unchanged", md5(BED) == BEDM, md5(BED))
        print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                        [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
    sys.exit(1 if G["fail"] else 0)
