r"""diag_replay_measure - card 76-1, the two MEASURED-FIRST pass lines (m8 plan PD14(b)/PD15). Nothing saved except
the run's own JSON/log; both edits happen on dated SCRATCH byte copies that are deleted in the same run. NO VI IS RUN
(only reader/editor op VIs execute).
PRIOR ART: pattern = tools/bench/diag_m8b_replay_prep.py (75-3); readers gscript.node_info/node_labels/subvis/conpane
/exec_state/report_all/delete_object (gscript.py:2580/611/549/2865/2017/512/2358); IMAQdx.llb is a FOLDER on this
install (75-3 run 1), so the vi.lib callee is byte-copyable; fixture map = tools/gpu/fixture.py:15 + read_image.
PREDICTION (each can fail):
 F1 fixture dir holds img%05d.tif for EVERY k in 0..10043 (10,044 files, no gaps), img00005.tif is 1280x1024 mode L.
 F2 the image feeding S1 #6810 'Image In' traces back (offline, wiki wires) to an 'IMAQ Create' subVI; its
    'Image Type' input source is reported (unwired => default Grayscale U8).
 G1 IMAQdx Get Image.vi byte copy: diagram readable (node_info non-empty) and a delete on the scratch removes 1 node
    (=> not locked). G2 its qualified VI name is reported (library claim => name clash hazard with vi.lib).
 B1 get buff scratch: Nodes[] listing reported (does it contain panel terminals?); deleting #529 removes it.
 H  pins S1/S3/gb/GI unchanged; refs opened == closed; LabVIEW gone at exit.
    MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/replay_vis_76_measure.log -- py -u tools/bench/diag_replay_measure.py"""
import os, sys, json, time, shutil, subprocess                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
g = K.g
GB = os.path.join(K.CLAUDEDEV, "background VIs_COPY", "get buff image-lost frames.vi")
GB_ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs\get buff image-lost frames.vi"
GI = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Get Image.vi"
S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); S3 = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi")
sys.path.insert(0, os.path.join(K.HERE, "gpu")); import fixture as FX                   # noqa: E402,E401
s = K.Stage(GB, "9aaaef21e8426035f64a04ec816491d0", "replay_measure_76", fresh=False, preload=False, deadline_min=13,
            out_json=os.path.join(K.BENCH, "replay_vis_76_measure.json"), task="76-1")
PIN = {k: K.md5(p) for k, p in (("S1", S1), ("S3", S3), ("gb", GB), ("gb_orig", GB_ORIG), ("GI", GI))}
s.R["pins_before"] = PIN
s.head("[F1] fixture index -> file map (tools/gpu/fixture.py:15, read_image)")
names = sorted(f for f in os.listdir(FX.DATA) if f.lower().endswith(".tif"))
idx = sorted(int(f[3:8]) for f in names if f.startswith("img") and f[3:8].isdigit())
s.fact("tif files {0}; first {1} last {2}".format(len(names), names[:2], names[-2:]))
s.gate("F1a img%05d.tif for every k in 0..10043, no gaps", idx == list(range(10044)), (len(idx), idx[:2], idx[-2:]))
gaps = [(a, b) for a, b in zip(idx, idx[1:]) if b - a > 1]
s.R["fixture_map"] = {"n": len(idx), "first": idx[:6], "last": idx[-3:], "n_gaps": len(gaps), "gaps_head": gaps[:8],
                      "has_5": 5 in idx, "sorted_index_of_first": idx[0]}
s.fact("fixture numbers: n {0}, first {1}, last {2}, gaps {3} (head {4}), 5 present {5}".format(
    len(idx), idx[:6], idx[-3:], len(gaps), gaps[:8], 5 in idx))
from PIL import Image                                                                    # noqa: E402
im = Image.open(os.path.join(FX.DATA, names[0]))
s.R["frame_first"] = {"file": names[0], "mode": im.mode, "size": im.size}
s.gate("F1b {0} is 1280x1024 mode L (8-bit)".format(names[0]), im.size == (1280, 1024) and im.mode == "L", (im.mode, im.size))
s.head("[F2] caller Image In source (offline, docs/wiki/subvi/D1_s1_copy.json)")
W = json.load(open(os.path.join(K.ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json"), encoding="utf-8"))
calls = {c["node_uid"]: c["subvi_name"] for c in W["graph_summary"]["subvi_calls"]}
into = {}
for w in W["wires"]:
    into.setdefault((w["sink_uid"], w["sink_term"]), []).append(w)
cur, trail = (6810, "Image In"), []
for _hop in range(12):
    ws = into.get(cur, [])
    if not ws:
        trail.append(("no wire into", cur)); break
    w = ws[0]; trail.append((w["wire_uid"], w["src_class"], w["src_uid"], w["src_term"], calls.get(w["src_uid"], "")))
    if "IMAQ Create" in calls.get(w["src_uid"], ""):
        break
    nxt = [k for k in into if k[0] == w["src_uid"]]
    if not nxt:
        break
    cur = nxt[0]
s.fact("trail {0}".format(trail)); s.R["image_trail"] = trail
cr = trail[-1][2] if trail and len(trail[-1]) == 5 else None
s.gate("F2a Image In traces to an IMAQ Create subVI", bool(cr) and "IMAQ Create" in calls.get(cr, ""), cr)
if cr:
    it = [w for k, ws in into.items() if k[0] == cr for w in ws]
    s.fact("IMAQ Create #{0} inputs: {1}".format(cr, [(w["sink_term"], w["src_class"], w["src_uid"]) for w in it]))
    s.R["imaq_create_inputs"] = [(w["sink_term"], w["src_class"], w["src_uid"]) for w in it]
s.head("[1] RESTART LabVIEW")
s.restart()
def probe(tag, src, del_uid_cls):
    p = s.scratch(tag, source=src)
    s.R[tag] = rec = {}
    rec["es"] = s.safe(tag + " exec_state", lambda: g.exec_state(p))[0]
    rec["node_info"] = s.safe(tag + " node_info", lambda: g.node_info(p, max_n=60), [])[0]
    rec["labels"] = s.safe(tag + " node_labels d0", lambda: g.node_labels(p, 0), [])[0]
    rec["subvis"] = s.safe(tag + " subvis d0", lambda: g.subvis(p, 0), [])[0]
    rec["conpane"] = s.safe(tag + " conpane", lambda: g.conpane(p), {})[0]
    def qname():
        with g.vi_ref(p) as v:
            return str(v.Name)
    rec["vi_name"] = s.safe(tag + " VI.Name", qname)[0]
    for k in ("es", "node_info", "labels", "subvis", "conpane", "vi_name"):
        s.fact("{0} {1}: {2}".format(tag, k, rec[k]))
    cls, uid = del_uid_cls(rec)
    if uid:
        us = s.safe(tag + " uids " + cls, lambda: g.uids(p, cls), [])[0]
        i = us.index(uid) if uid in us else -1
        gone, err = s.safe("{0} delete {1}#{2} (index {3})".format(tag, cls, uid, i), lambda: g.delete_object(p, cls, i))
        rec["delete"] = {"cls": cls, "uid": uid, "index": i, "gone": sorted(gone or []), "err": err}
        s.gate("{0} edit test: delete {1}#{2} removed exactly it".format(tag, cls, uid), list(gone or []) == [uid], rec["delete"])
        rec["es_after_delete"] = s.safe(tag + " es after", lambda: g.exec_state(p))[0]
    s.drop_scratch(p, tag)
    return rec
def gi_target(rec):
    subs = [x["uid"] for x in (rec["subvis"] or [])]
    return ("SubVI", subs[0]) if subs else ("Node", None)
s.head("[G] IMAQdx Get Image.vi byte copy (vi.lib never written)")
rg = probe("GI", GI, gi_target)
s.gate("G1a diagram readable: node_info non-empty", bool(rg["node_info"]), len(rg["node_info"] or []))
s.head("[B] get buff scratch copy")
rb = probe("GB", GB, lambda rec: ("SubVI", 529))
s.head("[H] hygiene")
s.R["ref_counts"] = g.ref_counts(); s.fact("ref_counts {0}".format(s.R["ref_counts"]))
PIN2 = {k: K.md5(p) for k, p in (("S1", S1), ("S3", S3), ("gb", GB), ("gb_orig", GB_ORIG), ("GI", GI))}
s.gate("H1 pins unchanged", PIN2 == PIN, [k for k in PIN if PIN[k] != PIN2[k]])
g.reset()
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6)
tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True, errors="replace").stdout
s.gate("H2 LabVIEW gone at exit", "LabVIEW.exe" not in tl, tl.strip()[-80:])
s.dump()
sys.exit(s.summary())
