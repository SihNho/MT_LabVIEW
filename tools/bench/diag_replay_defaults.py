r"""diag_replay_defaults - card 76-5, the cheapest discriminator after replay_vis_76d_test.log run 2 (T1-T3: U8 array EMPTY,
no error anywhere, cal Buffer Number Out 0,0,0). READ-ONLY: loads the two saved stand-ins COLD in a fresh LabVIEW and reads
their three hidden controls' values (= the saved defaults: nothing is run). No VI is run, nothing is saved.
E1 (defaults not persisted by gscript.make_default -> For loop N = 0, empty path, ReadFile error swallowed) predicts:
'Control Names' (the N=1 array) EMPTY and/or 'Control Names 2' (frame paths) EMPTY. E2 (defaults persisted; fault inside the
body) predicts: ['1'], 10044 paths with [0] == G:\m8_replay_frames\f00000.tif, y == 10044.
    py tools/bgrun.py --material --max-min 10 --log tools/bench/replay_vis_76d_defaults.log -- py -u tools/bench/diag_replay_defaults.py"""
import os, sys                                                                           # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
s = K.Stage(L.BUF, K.md5(L.BUF), "replay_vis_76d_defaults", fresh=False, preload=False, deadline_min=8, pins=L.pins(),
            task="76-5", out_json=os.path.join(K.BENCH, "replay_vis_76d_defaults.json"))
s.restart()
for tag, p in (("buf", L.BUF), ("cal", L.CAL)):
    md = K.md5(p)
    with g.vi_ref(p) as v:
        vals = {}
        for lab in ("Control Names", "Control Names 2", "y"):
            try:
                x = v.GetControlValue(lab)
                vals[lab] = (len(x), list(x[:2]), x[-1] if len(x) else None) if isinstance(x, (tuple, list)) else x
            except Exception as e:                                                       # noqa: BLE001
                vals[lab] = "ERR {0}".format(str(e)[:120])
        for prop in ("ExecState", "Reentrant", "ReentrancyType", "IsReentrant", "AutoErrorHandling", "EnableAutomaticErrorHandling"):
            try:                                                                         # review 2026-09-25-76-5-t1 s4: reentrancy + AEH
                vals[prop] = getattr(v, prop)
            except Exception as e:                                                       # noqa: BLE001
                vals[prop] = "n/a ({0})".format(type(e).__name__)
    s.fact("{0} md5 {1} saved defaults {2}".format(tag, md, vals)); s.R[tag] = {"md5": md, "defaults": vals}
    s.row("{0} E1 vs E2".format(tag), vals, "E2: ('Control Names' len 1, 'Control Names 2' len 10044, y 10044)")
    s.gate("{0} md5 unchanged by the read".format(tag), K.md5(p) == md)
L.tail(s); sys.exit(s.summary())
