import sys, os; sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))); import gscript as g
g._lv = None
V = r'C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision'
for llb, name in (('Basics.llb', 'IMAQ GetImagePixelPtr'), ('Basics.llb', 'IMAQ GetImageInfo'), ('Basics.llb', 'IMAQ GetImageSize')):
    p = os.path.join(V, llb, name)
    try: print(name, '->', g.fp_labels(p), flush=True)
    except Exception as e: print(name, 'EXC', str(e)[:160], flush=True)
