# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_170-a2-1.json
# ---
r"""diag_c170_a2_1_hash - card 170-a2-1 brief step 1: re-hash of the P6-2 inputs as BYTES (no .vi opened, no LabVIEW).

Found before writing (CALLED): prep_c168_hashlib.check (card inputs via protocol.input_md5_changes + claudeDev VI pins, GATE lines) and
prep_c156_a1_1_lib.md5 / Gate. The eight VI pins are DATA (brief_170-a2-1.md:9-11). The frames manifest is regenerated in the SAME format
as diag_c170_a1_1_hash.py:37-40 ("name\tsize\tmd5\n", sorted os.listdir) into a NEW file; that block is module-level code in a script
(importing it would re-run it and overwrite p6_replay_frames_manifest.txt), so it is written here once more - reported as a duplicate.

PREDICTION: L no LabVIEW; I card inputs equal (graph fbc7b7ee + manifest 9055d98a are card inputs); H x8 VI pins equal; F1 10045 files;
M new manifest md5 == p6_replay_frames_manifest.txt md5 9055d98a. Any difference = DRIFT -> the card returns.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c170_a2_1_hash.log -- py -u tools/bench/diag_c170_a2_1_hash.py"""
import os, subprocess, sys                                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    _p in sys.path or sys.path.insert(0, _p)                                                # noqa: E701
import prep_c168_hashlib as HL                                                              # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402

CARD = "tools/bench/cards/task_170-a2-1.json"
PINS = [("D1_ring_p6_20261012_212645.vi", "c2d9c13c"), ("D1_ring_p5_20261010_172913.vi", "75773b0d"),
        ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"), ("D1_s1_copy.vi", "3e3d23ce"),
        ("replay\\D1_s1_replay_20260925_075422.vi", "126f8497"), ("replay\\replay_get_buff_image.vi", "842ecad9"),
        ("replay\\replay_get_image_cal.vi", "afce0d04"), ("replay\\replay_imaqdx_get_image_buf.vi", "a89dafc1")]
FR = r"G:\m8_replay_frames"
REF = os.path.join(ROOT, "tools", "bench", "p6_replay_frames_manifest.txt")
NEW = os.path.join(ROOT, "tools", "bench", "diag_c170_a2_1_manifest.txt")

gate = L.Gate(fatal_default=False)
lv = ("lab" + "view") in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
gate("L no LabVIEW process at start", not lv)
r = HL.check(CARD, "card 170-a2-1 start", gate, pins=PINS)
for it in __import__("json").load(open(os.path.join(ROOT, CARD), encoding="utf-8"))["inputs"]:
    print("REHASH | card input %s | expected %s | measured %s" % (it["path"], it["md5"], L.md5(os.path.join(ROOT, it["path"]))), flush=True)
for n, m, pin, ok in r["pins"]:
    print("REHASH | VI %s | expected %s | measured %s | %s" % (n, pin, m, "EQUAL" if ok else "DRIFT"), flush=True)

names = sorted(os.listdir(FR))
rows = [(n, os.path.getsize(os.path.join(FR, n)), L.md5(os.path.join(FR, n))) for n in names]
with open(NEW, "w", encoding="utf-8", newline="\n") as f:
    f.write("".join("%s\t%d\t%s\n" % x for x in rows))
gate("F1 %s holds 10045 files" % FR, len(rows) == 10045, len(rows))
mn, mr = L.md5(NEW), L.md5(REF)
print("REHASH | frames manifest (regenerated %s) | expected %s (p6_replay_frames_manifest.txt) | measured %s | %s"
      % (os.path.relpath(NEW, ROOT), mr, mn, "EQUAL" if mn == mr else "DRIFT"), flush=True)
gate("M regenerated manifest md5 %s == p6_replay_frames_manifest.txt md5 %s (pin 9055d98a)" % (mn, mr),
     mn == mr and mr.startswith("9055d98a"), "%d lines" % len(rows))
sys.exit(gate.result([{"path": os.path.relpath(NEW, ROOT).replace("\\", "/"), "md5": mn}]))
