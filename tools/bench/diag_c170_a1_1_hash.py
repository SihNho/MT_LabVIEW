# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/task_170-a1-1.json
# ---
r"""diag_c170_a1_1_hash - card 170-a1-1 brief s.1: re-hash of the P6-2 inputs (bytes only, no .vi opened, no LabVIEW).

Found before writing (CALLED, not copied): tools/bench/prep_c168_hashlib.check (card inputs via protocol.input_md5_changes + claudeDev
VI pins, Gate lines); tools/bench/prep_c156_a1_1_lib.md5 / Gate. The eight VI pins below are DATA (brief_170-a1-1.md:8-11; the S1 file and
the third stand-in from plans/plan_replay_swap_110.json extra_pins). Frames: G:\m8_replay_frames, expected 10045 files = 10044 frames +
frames_manifest.json (diag_replay_frames.py:2-3); each frame's md5 is also compared to that manifest's per-frame md5, and the manifest
file to replay_vis_76c_frames.json manifest_md5 f9032ae5.

PREDICTION: I card inputs equal; H x8 VI pins equal; F1 10045 files; F2 every f*.tif md5 == frames_manifest.json md5; F3
frames_manifest.json md5 == f9032ae5...; L no LabVIEW process. Writes p6_replay_frames_manifest.txt and diag_c170_a1_1_hash.json.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c170_a1_1.log -- py -u tools/bench/diag_c170_a1_1_hash.py"""
import json, os, subprocess, sys                                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
for _p in (ROOT, os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench")):
    _p in sys.path or sys.path.insert(0, _p)                                                # noqa: E701
import prep_c168_hashlib as HL                                                              # noqa: E402
import prep_c156_a1_1_lib as L                                                              # noqa: E402

CARD = "tools/bench/cards/task_170-a1-1.json"
PINS = [("D1_ring_p6_20261012_212645.vi", "c2d9c13c"), ("D1_ring_p5_20261010_172913.vi", "75773b0d"),
        ("D1_ring_p5s01_20261009_124542.vi", "7f2582ae"), ("D1_s1_copy.vi", "3e3d23ce"),
        ("replay\\D1_s1_replay_20260925_075422.vi", "126f8497"), ("replay\\replay_get_buff_image.vi", "842ecad9"),
        ("replay\\replay_get_image_cal.vi", "afce0d04"), ("replay\\replay_imaqdx_get_image_buf.vi", "a89dafc1")]
FR = r"G:\m8_replay_frames"
MAN_TXT = os.path.join(ROOT, "tools", "bench", "p6_replay_frames_manifest.txt")
OUT = os.path.join(ROOT, "tools", "bench", "diag_c170_a1_1_hash.json")
MAN_MD5_76 = "f9032ae5510e96126d9f53fc92f69cfe"                                             # replay_vis_76c_frames.json:2

gate = L.Gate(fatal_default=False)
lv = ("lab" + "view") in subprocess.run(["tasklist"], capture_output=True, text=True).stdout.lower()
gate("L no LabVIEW process at start", not lv)
r = HL.check(CARD, "card 170-a1-1 start", gate, pins=PINS)

names = sorted(os.listdir(FR))
rows = [(n, os.path.getsize(os.path.join(FR, n)), L.md5(os.path.join(FR, n))) for n in names]
with open(MAN_TXT, "w", encoding="utf-8", newline="\n") as f:
    f.write("".join("%s\t%d\t%s\n" % x for x in rows))
gate("F1 %s holds 10045 files" % FR, len(rows) == 10045, len(rows))
man = json.load(open(os.path.join(FR, "frames_manifest.json"), encoding="utf-8"))
want = {x["file"]: x["md5"] for x in man["frames"]}
got = {n: m for n, _s, m in rows if n != "frames_manifest.json"}
bad = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
gate("F2 every frame md5 == frames_manifest.json per-frame md5 (%d frames)" % len(want), not bad and len(want) == 10044, bad[:10])
mm = dict((n, m) for n, _s, m in rows).get("frames_manifest.json")
gate("F3 frames_manifest.json md5 %s == replay_vis_76c_frames.json manifest_md5" % mm, mm == MAN_MD5_76, MAN_MD5_76)
man_txt_md5 = L.md5(MAN_TXT)
print("FACT manifest file %s md5 %s (%d lines)" % (os.path.relpath(MAN_TXT, ROOT), man_txt_md5, len(rows)), flush=True)

rehash = [{"row": "card input " + it["path"], "expected": it["md5"], "measured": L.md5(os.path.join(ROOT, it["path"])),
           } for it in json.load(open(os.path.join(ROOT, CARD), encoding="utf-8"))["inputs"]]
rehash += [{"row": "VI " + n, "expected": pin, "measured": m} for n, m, pin, _ok in r["pins"]]
rehash += [{"row": "frames dir file count", "expected": 10045, "measured": len(rows)},
           {"row": "frames_manifest.json (in dir)", "expected": MAN_MD5_76, "measured": mm},
           {"row": "frames md5 vs frames_manifest.json per-frame md5", "expected": "0 differ", "measured": "%d differ" % len(bad)},
           {"row": "manifest md5 (p6_replay_frames_manifest.txt)", "expected": "none pinned (new file)", "measured": man_txt_md5}]


def status(exp, got):
    """EQUAL when the measured value starts with the expected one (md5 prefix or exact count/text), or nothing was pinned."""
    return "EQUAL" if exp == "none pinned (new file)" or str(got).startswith(str(exp)) else "DRIFT"


assert [status("c2d9", "c2d9ff"), status(10045, 10044), status("none pinned (new file)", "x")] == ["EQUAL", "DRIFT", "EQUAL"]
for x in rehash:
    x["status"] = status(x["expected"], x["measured"])
json.dump({"rehash": rehash, "drift": [x["row"] for x in rehash if x["status"] == "DRIFT"]}, open(OUT, "w", encoding="utf-8"), indent=1)
for x in rehash:
    print("REHASH %-5s | %s | expected %s | measured %s" % (x["status"], x["row"], x["expected"], x["measured"]), flush=True)
sys.exit(gate.result([{"path": os.path.relpath(p, ROOT).replace("\\", "/"), "md5": L.md5(p)} for p in (MAN_TXT, OUT)]))
