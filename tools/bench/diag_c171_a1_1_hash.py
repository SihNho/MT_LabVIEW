# ---
# labview: none
# hardware: none
# ---
"""Step 0 re-hash for card 171-a1-1 (reads files only; opens nothing in LabVIEW).

Prediction: every listed file exists and its md5 starts with the brief's 8-hex value; 7f2582ae is found
under claudeDev. Prior art: tools/protocol.py hashes card inputs only; no shared multi-path hash table
helper was found, so this one-off reads the brief's own list.
"""
import glob
import hashlib
import os

R = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop"
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
WANT = [
    (CD + r"\D1_ring_p6_20261012_212645.vi", "c2d9c13c"),
    (CD + r"\D1_ring_p5_20261010_172913.vi", "75773b0d"),
    (R + r"\tools\bench\graph_ring_p6_20261012_212645.json", "fbc7b7ee"),
    (CD + r"\D1_s1_copy.vi", "3e3d23ce"),
    (CD + r"\replay\D1_s1_replay_20260925_075422.vi", "126f8497"),
    (CD + r"\replay\replay_imaqdx_get_image_buf.vi", "a89dafc1"),
    (CD + r"\replay\replay_get_image_cal.vi", "afce0d04"),
    (CD + r"\replay\replay_get_buff_image.vi", "842ecad9"),
    (CD + r"\replay\replay_imaqdx_get_image_buf_paced60.vi", "e40ec867"),
    (CD + r"\replay\replay_get_buff_image_paced60.vi", "59ec66b6"),
    (R + r"\tools\bench\p6_replay_frames_manifest.txt", "9055d98a"),
    (R + r"\tools\bench\m8b_replay_compare.py", "82443af9"),
    (R + r"\tools\bench\plans\plan_replay_swap_170.json", "01c21526"),
    (R + r"\tools\recipes\stage_replay" + "_swap.py", "fa94e80c"),
    (R + r"\tools\stage_prerun.py", "db81a1d3"),
    (R + r"\tools\bench\plans\plan_replay_swap_78.json", "cdc14e32"),
    (R + r"\tools\bench\plans\plan_replay_swap_95.json", "ea7cf810"),
    (R + r"\tools\bench\plans\plan_replay_swap_110.json", "6b5ef7e5"),
    (R + r"\tools\bench\diag_c171_a1_2_patch.diff", "f8f1fd95"),
]


def md5(path):
    with open(path, "rb") as fh:
        return hashlib.md5(fh.read()).hexdigest()


def main():
    bad = 0
    for path, want in WANT:
        if not os.path.exists(path):
            print("MISSING", path)
            bad += 1
            continue
        got = md5(path)
        ok = got.startswith(want)
        bad += not ok
        print("OK  " if ok else "DIFF", got[:8], want, os.path.basename(path))
    found = [p for p in glob.glob(CD + r"\**\*.vi", recursive=True) if md5(p).startswith("7f2582ae")]
    print("7f2582ae ->", found or "NOT FOUND")
    bad += not found
    print('RESULT {"schema":"result-line/1","status":"%s","gates":{"pass":%d,"fail":%d}}'
          % ("PASS" if bad == 0 else "FAIL", len(WANT) + 1 - bad, bad))


if __name__ == "__main__":
    main()
