r"""diag_replay_frames - card 76-4 pass line 2 (m8 plan PD16(a) as amended by PD17(a'')). NO LabVIEW.
Builds G:\m8_replay_frames\f00000.tif .. f10043.tif as HARDLINKS of the SORTED fixture list (tools/gpu/fixture.py:15 DATA;
sort = numeric img number, the order 76-1 measured: 4,7,8,11,..,11825) + frames_manifest.json (index -> source -> md5).
Nothing is written through a link; the fixture folder is only read. PRIOR ART: none (76-1 built nothing).
PREDICTION (each can fail):
 P1 fixture holds exactly 10044 img*.tif (76-1: replay_vis_76_measure.log:17); dest folder new or already == manifest.
 P2 10044 links made, each os.path.samefile(link, source); link count of a source >= 2.
 P3 20 random indices: md5(link) == manifest md5 == md5(source) AND U8 pixel-array md5 (PIL) of link == of source,
    and f00005 is the 6th sorted fixture file (PD16(a) test meaning).
 P4 fixture md5 of 5 sampled files unchanged before/after (read-only proof).
    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/replay_vis_76c_frames.log -- py -u tools/bench/diag_replay_frames.py"""
import os, sys, json, random, hashlib, time                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "gpu"))
import fixture as FX, protocol                                                             # noqa: E402,E401
import numpy as np                                                                         # noqa: E402
from PIL import Image                                                                      # noqa: E402
DEST = r"G:\m8_replay_frames"; MAN = os.path.join(DEST, "frames_manifest.json")
OUT = os.path.join(HERE, "replay_vis_76c_frames.json")
P, F, R = [0], [], {}


def gate(label, ok, detail=""):
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)
    if ok:
        P[0] += 1
    else:
        F.append(label)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 22), b""):
            h.update(b)
    return h.hexdigest()


def pix_md5(p):
    a = np.asarray(Image.open(p)); return hashlib.md5(np.ascontiguousarray(a).tobytes()).hexdigest(), a.dtype.str, a.shape


t0 = time.time()
names = sorted((f for f in os.listdir(FX.DATA) if f.lower().startswith("img") and f.lower().endswith(".tif")),
               key=lambda f: int(f[3:8]))
gate("P1a fixture holds 10044 img*.tif", len(names) == 10044, (len(names), names[:3], names[-2:]))
if len(names) != 10044:
    print(protocol.result_line(protocol.make_result(P[0], len(F), F[0]))); sys.exit(1)
samp = random.Random(76).sample(range(10044), 5)
pin0 = {names[i]: md5(os.path.join(FX.DATA, names[i])) for i in samp}
os.makedirs(DEST, exist_ok=True)
pre = sorted(os.listdir(DEST))
gate("P1b dest new/empty or holds only a previous build of this script", all(x.startswith("f") or x == "frames_manifest.json" for x in pre), len(pre))
made = 0
for i, n in enumerate(names):
    src, dst = os.path.join(FX.DATA, n), os.path.join(DEST, "f%05d.tif" % i)
    if os.path.exists(dst):
        if not os.path.samefile(src, dst):
            gate("P2 existing %s is not a link of %s" % (dst, n), False); break
        continue
    os.link(src, dst); made += 1
same = sum(os.path.samefile(os.path.join(FX.DATA, n), os.path.join(DEST, "f%05d.tif" % i)) for i, n in enumerate(names))
gate("P2a 10044 links, every one samefile(link, source)", same == 10044, (same, "new links", made))
extra = sorted(set(os.listdir(DEST)) - set("f%05d.tif" % i for i in range(10044)) - {"frames_manifest.json"})
gate("P2b no extra files in dest", not extra, extra[:5])
st = os.stat(os.path.join(FX.DATA, names[0]))
gate("P2c source link count >= 2 (hardlink, 0 bytes extra)", st.st_nlink >= 2, st.st_nlink)
print("  FACT  hashing 10044 files for the manifest ...", flush=True)
man = {"schema": "replay-frames/1", "dest": DEST, "source_dir": FX.DATA, "n": 10044,
       "rule": "frame index i = position in the fixture list sorted by img number; stand-in frame = f((n - n0) mod 10044)",
       "frames": [{"i": i, "file": "f%05d.tif" % i, "source": n, "md5": md5(os.path.join(FX.DATA, n))} for i, n in enumerate(names)]}
with open(MAN, "w", encoding="utf-8") as f:
    json.dump(man, f, indent=0)
R["manifest_md5"] = md5(MAN)
chk = sorted(set(random.Random(7604).sample(range(10044), 18) + [0, 5]))
bad = []
for i in chk:
    L, S = os.path.join(DEST, "f%05d.tif" % i), os.path.join(FX.DATA, names[i])
    ok = md5(L) == man["frames"][i]["md5"] == md5(S) and pix_md5(L) == pix_md5(S)
    if not ok:
        bad.append(i)
R["checked"] = chk; R["pix_f00000"] = pix_md5(os.path.join(DEST, "f00000.tif")); R["pix_f00005"] = pix_md5(os.path.join(DEST, "f00005.tif"))
gate("P3a %d random indices: file md5 + U8 pixel-array md5 link == source == manifest" % len(chk), not bad, bad)
gate("P3b f00005 is the 6th sorted fixture file (%s)" % names[5], man["frames"][5]["source"] == names[5] == "img00013.tif", names[5])
gate("P4 fixture sample md5 unchanged", {n: md5(os.path.join(FX.DATA, n)) for n in pin0} == pin0, samp)
R.update({"n_pass": P[0], "fail": F, "minutes": round((time.time() - t0) / 60, 1), "first_sources": names[:6],
          "pixel_md5": {"f00000": R["pix_f00000"][0], "f00001": pix_md5(os.path.join(DEST, "f00001.tif"))[0],
                        "f00002": pix_md5(os.path.join(DEST, "f00002.tif"))[0], "f00005": R["pix_f00005"][0]}})
json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
print("  FACT  %s" % json.dumps(R, default=str)[:900], flush=True)
print(protocol.result_line(protocol.make_result(P[0], len(F), F[0] if F else None,
                                                artefacts=[{"path": MAN, "md5": R["manifest_md5"]}])), flush=True)
sys.exit(1 if F else 0)
