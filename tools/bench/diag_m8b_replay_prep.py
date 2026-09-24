r"""diag_m8b_replay_prep - card 75-3 (m8 plan PD13(f)). READ-ONLY LabVIEW read of the two callees PD13 swaps.
NO VI IS RUN (only the existing reader op VIs execute), nothing saved, no bed/original opened for write.
PRIOR ART (checked first): connector panes = `gscript.conpane` (OpConPane_v0, docs/NAMES.md:514-534) and `fp_labels`
(OpFPLabels_v0, gscript.py:2558); short-lived counted refs = `gscript.vi_ref` (gscript.py:254); restart =
bench_prep.restart_labview; gates/facts/RESULT line = stagekit.Stage (not start(): no work copy is made). There is
NO data-type reader in gscript/toolkit-capabilities, so type = the Python/COM class of `GetControlValue(label)` on the
idle VI (coarse: bool / int / float / tuple(cluster) / str) plus the COM error text when a refnum does not convert.
The callee of #6810 in both beds is the ORIGINAL background VI (docs/wiki/subvi/D1_s1_copy.json:89813); it is read
through its claudeDev COPY when the md5s match, else not read at all (P2 FAIL).
PREDICTION: P1 S1/S3 md5 = 3e3d23ce... / 1a11d92a... before and after; P2 copy md5 == original md5 == wiki md5
9aaaef21...; P3 conpane(copy) == wiki connector_pane (9 labels at 0,4,5,6,7,8,10,11,15); P4 IMAQdx Get Image.vi:
fp_labels non-empty => NOT polymorphic (a polymorphic VI has no readable panel) and its conpane holds Session In, Image
In, Buffer Number Mode, Buffer Number In, error in, Session Out, Image Out, Buffer Number Out, error out;
P5 LabVIEW process gone at exit.
    MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/m8b_replay_prep_75.log -- py -u tools/bench/diag_m8b_replay_prep.py"""
import os, sys, json, time, subprocess                                                  # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                     # noqa: E402
g = K.g
ROOT = K.ROOT
S1 = os.path.join(K.CLAUDEDEV, "D1_s1_copy.vi"); S3 = os.path.join(K.CLAUDEDEV, "D1_s3_loop15.vi")
S1M, S3M = "3e3d23cefd3a334001aa9d6156bf1aee", "1a11d92aacabf7ec844d65b8af19f39f"
GB_ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs\get buff image-lost frames.vi"
GB_COPY = os.path.join(K.CLAUDEDEV, "background VIs_COPY", "get buff image-lost frames.vi")
GI = r"C:\Program Files\NI\LVAddons\niimaqdx\1\vi.lib\vision\driver\IMAQdx.llb\IMAQdx Get Image.vi"
GI_LLB = GI   # IMAQdx.llb is a DIRECTORY on this install (run 1: PermissionError on open); pin the VI file itself
s_llb = sorted(f for f in os.listdir(os.path.dirname(GI)) if "Get Image" in f)
WIKI = json.load(open(os.path.join(ROOT, "docs", "wiki", "subvi", "get buff image-lost frames.json"), encoding="utf-8"))
s = K.Stage(GB_COPY, None, "m8b_replay_prep_75", fresh=False, preload=False, deadline_min=13,
            out_json=os.path.join(K.BENCH, "m8b_replay_prep_75.json"), task="75-3")
s.R.update({"no_vi_was_run": True, "callees": {}})
s.head("[0] FILES ONLY")
m = {k: (K.md5(p) if os.path.exists(p) else "MISSING") for k, p in (("S1", S1), ("S3", S3), ("gb_orig", GB_ORIG),
                                                                     ("gb_copy", GB_COPY), ("imaqdx_llb", GI_LLB))}
s.R["md5_before"] = m
s.fact("IMAQdx.llb (a folder) 'Get Image' files: {0}".format(s_llb)); s.R["imaqdx_get_image_files"] = s_llb
s.gate("P1a S1/S3 md5 pinned before", m["S1"] == S1M and m["S3"] == S3M, (m["S1"], m["S3"]))
s.gate("P2 get-buff copy == original == wiki md5", m["gb_orig"] == m["gb_copy"] == WIKI["md5"], (m["gb_orig"], m["gb_copy"], WIKI["md5"]))
for k in ("gb_orig", "gb_copy", "imaqdx_llb"):
    s.fact("{0} md5 {1} version bytes {2}".format(k, m[k], K.version_bytes({"gb_orig": GB_ORIG, "gb_copy": GB_COPY, "imaqdx_llb": GI_LLB}[k])))
s.head("[1] RESTART LabVIEW (fresh instance)")
s.restart()
def pytype(v):
    if isinstance(v, bool): return "bool"
    if isinstance(v, int): return "int"
    if isinstance(v, float): return "float"
    if isinstance(v, str): return "str"
    if isinstance(v, (tuple, list)): return "{0}[{1}]({2})".format(type(v).__name__, len(v), ",".join(pytype(x) for x in v))
    return type(v).__name__
def read_callee(tag, path):
    rec = s.R["callees"][tag] = {"path": path}
    labels, e1 = s.safe(tag + " fp_labels", lambda: g.fp_labels(path), [])
    rec["fp_labels"], rec["fp_labels_err"] = labels, e1
    s.fact("{0} fp_labels ({1}): {2}".format(tag, len(labels), labels))
    cp, e2 = s.safe(tag + " conpane", lambda: g.conpane(path), {})
    rec["conpane"], rec["conpane_err"] = cp, e2
    s.fact("{0} conpane {1}".format(tag, cp))
    types = {}
    for _i, lab, ind in labels:
        def rd(l=lab):
            with g.vi_ref(path) as v:
                val = v.GetControlValue(l)
            return val
        val, err = s.safe("{0} GetControlValue({1})".format(tag, lab), rd)
        types[lab] = {"indicator": ind, "pytype": None if err else pytype(val), "default": None if err else repr(val)[:80], "err": err}
        s.fact("{0} '{1}' {2} type={3} default={4} {5}".format(tag, lab, "OUT" if ind else "IN", types[lab]["pytype"],
               types[lab]["default"], err))
    rec["types"] = types
    return rec
s.head("[2] get buff image-lost frames.vi (claudeDev COPY; original never opened)")
if m["gb_orig"] == m["gb_copy"]:
    r = read_callee("get_buff", GB_COPY)
    want = {c["index"]: c["label"] for c in WIKI["connector_pane"]}
    got = {int(k): v for k, v in r["conpane"].items() if v}
    s.gate("P3 conpane(copy) == wiki connector_pane", got == want, (got, want))
s.head("[3] IMAQdx Get Image.vi (vi.lib, read only)")
r = read_callee("imaqdx_get_image", GI)
s.gate("P4a IMAQdx Get Image.vi has a readable front panel (=> not polymorphic)", len(r["fp_labels"]) > 0, len(r["fp_labels"]))
need = {"Session In", "Image In", "Buffer Number In", "error in", "Session Out", "Image Out", "Buffer Number Out", "error out"}
have = set(v for v in r["conpane"].values() if v)
s.gate("P4b IMAQdx Get Image.vi conpane holds the node's 8 named terminals (+ a Buffer Number Mode)",
       need <= have and any(str(v).startswith("Buffer Number Mode") for v in have), sorted(have))
s.head("[H] hygiene: refs, md5s, LabVIEW closed")
s.R["ref_counts"] = g.ref_counts(); s.fact("ref_counts {0}".format(s.R["ref_counts"]))
m2 = {k: K.md5(p) for k, p in (("S1", S1), ("S3", S3), ("gb_orig", GB_ORIG), ("gb_copy", GB_COPY), ("imaqdx_llb", GI_LLB))}
s.R["md5_after"] = m2
s.gate("P1b every md5 unchanged after", m2 == m, [k for k in m if m[k] != m2[k]])
g.reset()
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
time.sleep(6)
tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True, errors="replace").stdout
s.gate("P5 LabVIEW process gone at exit", "LabVIEW.exe" not in tl, tl.strip()[-80:])
s.dump()
sys.exit(s.summary())
