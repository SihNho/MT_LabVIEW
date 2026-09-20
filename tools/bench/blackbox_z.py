"""blackbox_z.py - localize the Z mismatch of the NumPy reference: call the four Z-chain subVIs (SPEC copies) through
script-built harnesses (subvi_harness.build) with the NumPy intermediates as inputs and print the max abs difference per
stage (radial profile <- sub-image + centres; prep I(r) <- radial profile; fit-to-cal; phase <- corkscrew; quad fit).
  py tools/bgrun.py --max-min 20 --log tools/bench/blackbox_z3.log -- py -u tools/bench/blackbox_z.py
"""
import os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "gpu")); sys.path.insert(0, HERE)
import gscript as g
import ref_numpy as r
import subvi_harness as sh
from fixture import read_cal, read_image, read_reference
g._lv = None; g._run.__defaults__ = (6.0, 60.0)
SPEC = os.path.join(g.CLAUDEDEV, "SPEC")
np.set_printoptions(precision=6, suppress=True, linewidth=160)
CORK = "r shifted complex cosine/hilbert filtered intensity profile (aka the corkscrew)"
LIVE = 'complex 1D radial intensity profile post cosine bandpass/hilbert transform aka the "corkscrew"'
CALC = "2D array of complex cal image intensities (aka cal corkscrews) r shifted!"
CALA = "2D array of prepped cal image amplitudes r shifted!"
REAL = "Real portion of hilbert/bandpass filtered r-shifted claibration image"


def pairs(a):
    """complex array -> nested [re, im] pairs (how LabVIEW's ActiveX server marshals CDB arrays, both directions)."""
    a = np.asarray(a, dtype=complex)
    return np.stack([a.real, a.imag], axis=-1).tolist()


def cplx(v):
    a = np.array(v)
    return a[..., 0] + 1j * a[..., 1] if a.ndim >= 1 and a.shape[-1] == 2 and not np.iscomplexobj(a) else a


def main():
    H = {k: sh.build(os.path.join(SPEC, k + ".vi")) for k in ("tracking-calculate radial profile-openv2", "Tracking-prep I of r",
                                                               "Tracking-fit prepped I of r to cal", "tracking-calculate phase in neighborhood",
                                                               "tracking- quadratic fit to phase nghbrd")}
    p = r.Params(); win_rs, win_h, cals = r.load_inputs(); img = read_image(4); cal = read_cal()
    ref = read_reference()["frames"][0]
    for b in (0, 1, 3):
        x, y = cal["xy"][b]; c = cals[b]; forget = int(c["forget_radius"]); xi, yi = r.lv_round(x), r.lv_round(y)
        res = r.track_bead(img, xi, yi, 120, win_rs, win_h, c, p)
        h = r.lv_round(120 * p.k_half); half = 60
        sub = r.sub_image(img, xi, yi, h, p.orient); sx = res["x"] - xi; sy = res["y"] - yi
        print(f"\n=== bead {b}: numpy idx {res['index']} z_index {res['z_index']:.6f}; ref idx {ref['pos'][b]} z_index {ref['ff'][3*b+2]/float(c['z_step']):.6f}", flush=True)
        o = sh.run(H["tracking-calculate radial profile-openv2"], {"Input Image": [[int(v) for v in row] for row in sub], "half cross": half,
                                                                    "x center": float(h + sx), "y center": float(h + sy)}, ["radial intensity profile"])
        rad_lv = np.array(o["radial intensity profile"])
        print(f"  radial: LV len {len(rad_lv)} max|diff| {np.max(np.abs(rad_lv - res['rad'])):.3e}  argmax|diff| {np.argmax(np.abs(rad_lv - res['rad']))}  LV[:4] {rad_lv[:4]}  np[:4] {res['rad'][:4]}", flush=True)
        o = sh.run(H["Tracking-prep I of r"], {"radial intensity profile": [float(v) for v in rad_lv], "cosine bandpass": pairs(c["cosband"]),
                                               "forget radius": forget, "halfcross": half}, ["prepped I(r)", CORK])
        prep_lv = np.array(o["prepped I(r)"]); cork_lv = cplx(o[CORK])
        prep_np, cork_np = r.prep_i_of_r(rad_lv, half, forget, c["cosband"])
        print(f"  prep: LV len {len(prep_lv)} max|diff| {np.max(np.abs(prep_lv - prep_np)):.3e}; cork: LV len {len(cork_lv)} max|diff| {np.max(np.abs(cork_lv - cork_np)):.3e}  LV[:2] {cork_lv[:2]} np[:2] {cork_np[:2]}", flush=True)
        o = sh.run(H["Tracking-fit prepped I of r to cal"], {"prepped I(r)": [float(v) for v in prep_lv], REAL: [[float(v) for v in row] for row in c["real"]]},
                   ["Index of closest cal image slice"])
        idx_lv = int(o["Index of closest cal image slice"]); print(f"  fit to cal: LV {idx_lv} np {r.fit_prep_to_cal(prep_lv, c['real'])}", flush=True)
        o = sh.run(H["tracking-calculate phase in neighborhood"], {"index of best-fit cal image slice": idx_lv, LIVE: pairs(cork_lv),
                                                                    CALC: pairs(c["cork"]), CALA: [[float(v) for v in row] for row in c["ampl"]]},
                   ["neighborhood phases"])
        ph_lv = np.array(o["neighborhood phases"]); ph_np = r.phase_in_neighborhood(cork_lv, idx_lv, c["ampl"], c["cork"])
        print(f"  phases: LV {ph_lv}  np {ph_np}  max|diff| {np.max(np.abs(ph_lv - ph_np)):.3e}", flush=True)
        o = sh.run(H["tracking- quadratic fit to phase nghbrd"], {"neighborhood phases": [float(v) for v in ph_lv], "index of best-fit cal image slice": idx_lv},
                   ["bead z pos as a cal image index"])
        z_lv = float(o["bead z pos as a cal image index"]); z_np = r.quad_fit_phase(ph_lv, idx_lv)
        print(f"  quad fit: LV {z_lv:.6f} np {z_np:.6f} diff {abs(z_lv - z_np):.3e}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
