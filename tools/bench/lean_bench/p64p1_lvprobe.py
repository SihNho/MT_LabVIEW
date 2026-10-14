r"""p64p1_lvprobe - lean task p64p1, READ-ONLY LabVIEW probe (nothing is saved; no camera, no motor).
  [A] the claudeDev byte copy of `get buff image-lost frames.vi` (9aaaef21 == the original's md5): every object, every terminal
      (owner, name, direction, wire), the wire edges, the connector pane (slot -> label, direction), execution properties
      (ReentrancyType / IsReentrant / ExecPriority / PreferredExecSystem), and the type of each pane terminal.
  [B] donor scan: the claudeDev copies `background VIs_COPY\*.vi` (smallest first, time-boxed) for any node with a terminal
      named `first call?` or `(0,1)` (First Call? / Boolean To (0,1) donors for the wrapper's log-once branch).
    py tools/bgrun.py --material --max-min 25 --log tools/bench/lean_bench/p64p1_lvprobe.log -- py -u tools/bench/lean_bench/p64p1_lvprobe.py"""
import json, os, sys, time                                                               # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)
import diag_replay_lib as L                                                              # noqa: E402
K, g = L.K, L.g
WB = K.mod("wiki_build")
LEAN = os.path.join(K.CLAUDEDEV, "bench", "lean")
GB, GB_MD5 = L.GB, "9aaaef21e8426035f64a04ec816491d0"
BGC = os.path.join(K.CLAUDEDEV, "background VIs_COPY")
SCAN_S = float(os.environ.get("P64P1_SCAN_S", "600"))
if "--scan2" in sys.argv:                 # scan 2: the glob list in p64p1_scan2_globs.txt (one pattern per line)
    os.environ["P64P1_SCAN_GLOBS"] = ";".join(l.strip() for l in open(os.path.join(HERE, "p64p1_scan2_globs.txt"), encoding="utf-8") if l.strip())
    SCAN_S = 540.0


def live(p):
    return WB.read_live(p, fs_pairs=[])


def scan_files():
    """P64P1_SCAN_GLOBS = ';'-separated glob patterns (scan 2); default = every .vi of background VIs_COPY"""
    import glob
    pats = os.environ.get("P64P1_SCAN_GLOBS")
    if pats:
        fs = sorted(set(os.path.normpath(f) for p in pats.split(";") for f in glob.glob(p, recursive=True) if f.lower().endswith(".vi")))
    else:
        fs = [os.path.join(dp, f) for dp, _dn, ff in os.walk(BGC) for f in ff if f.lower().endswith(".vi")]
    return sorted(fs, key=os.path.getsize)


def body(s):
    s.start(); R = s.R
    if os.environ.get("P64P1_SCAN_GLOBS"):
        return scan(s, R)
    t = s.work
    s.head("[A] get buff copy (scratch byte copy %s)" % os.path.basename(t))
    s.gate("A0 work copy md5 == 9aaaef21", K.md5(t) == GB_MD5, fatal=True)
    s.gate("A1 ExecState", s.es("gb", t) in (1, 0), fatal=False)
    lv = live(t)
    R["objs"] = lv["objs"]
    R["terminals"] = lv["terminals"]
    for o in lv["objs"]:
        s.fact("OBJ %r" % (o,))
    by = {}
    for r in lv["terminals"]:
        by.setdefault(int(r["owner_uid"]), []).append(r)
    for u, rs in sorted(by.items()):
        s.fact("OWNER #%d %s: %r" % (u, rs[0]["owner_class"], [(r["term_name"], "OUT" if r["is_source"] else "IN", r["wire_uid"], r["term_uid"]) for r in rs]))
    E = L.edges(lv, {})
    R["edges"] = sorted(E)
    for e in sorted(E):
        s.fact("EDGE %r" % (e,))
    R["census"] = dict((str(k), v) for k, v in L.census(t).items())
    s.fact("CENSUS %r" % R["census"])
    R["pane"] = L.pane_dirs(t)
    s.fact("PANE %r" % R["pane"])
    props = {}
    with g.vi_ref(t) as vi:
        for p in ("ReentrancyType", "IsReentrant", "ExecPriority", "PreferredExecSystem", "ExecState", "AllowDebugging",
                  "ShowFPOnCall", "CloseFPAfterCall", "RunOnOpen", "SuspendOnCall"):
            try:
                v = getattr(vi, p)
                props[p] = v if isinstance(v, (int, float, str, bool)) else str(v)
            except Exception as e:                                                     # noqa: BLE001
                props[p] = "ERR %s" % str(e)[:80]
    R["props"] = props
    s.fact("PROPS %r" % props)
    types = {}
    for r in lv["terminals"]:
        if r["owner_class"] in ("TopLevelDiagram",) or "Terminal" in str(r["owner_class"]):
            try:
                types[r["term_name"]] = str(g.read_term_type(t, int(r["term_uid"])))[:200]
            except Exception as e:                                                     # noqa: BLE001
                types[r["term_name"]] = "ERR %s" % str(e)[:80]
    R["types"] = types
    s.fact("TYPES %r" % types)
    s.dump()
    g.reset()
    s.restart()
    return scan(s, R)


def scan(s, R):
    s.head("[B] donor scan (First Call? / Boolean To (0,1)), %d s budget" % SCAN_S)
    files = scan_files()
    s.fact("%d candidate files" % len(files))
    t0, hits, done = time.time(), [], []
    for k, p in enumerate(files):
        if time.time() - t0 > SCAN_S:
            s.fact("scan budget reached after %d of %d files" % (k, len(files)))
            break
        try:
            lvp = live(p)
        except Exception as e:                                                         # noqa: BLE001
            s.fact("SCAN %s ERR %s" % (os.path.basename(p), str(e)[:100]))
            continue
        done.append(os.path.basename(p))
        own = {}
        for r in lvp["terminals"]:
            own.setdefault(int(r["owner_uid"]), []).append(r)
        for u, rs in own.items():
            names = [str(r["term_name"]) for r in rs]
            if any(n.lower() == "first call?" or "(0,1)" in n for n in names):
                h = {"file": p, "md5": K.md5(p), "uid": u, "class": rs[0]["owner_class"], "diagram": rs[0]["frame_diagram"],
                     "terms": [(r["term_name"], r["is_source"], r["wire_uid"]) for r in rs]}
                hits.append(h)
                s.fact("HIT %r" % (h,))
        if (k + 1) % 8 == 0:
            g.reset(); s.restart()
    R["scan"] = {"done": done, "hits": hits, "n_files": len(files)}
    s.fact("scanned %d files; hits %d" % (len(done), len(hits)))
    s.dump()


class St(K.Stage):
    def close(self, expect_files=None):
        return K.Stage.close(self, [])

    def summary(self):
        L.tail(self, None); return K.Stage.summary(self)


if __name__ == "__main__":
    pins = tuple(K.DEFAULT_PINS[:1]) + (("get buff copy", GB, GB_MD5), ("get buff orig", L.GB_ORIG, GB_MD5))
    st = St(GB, GB_MD5, "p64p1_lvprobe", preload=False, deadline_min=24, work_dir=LEAN,
            work_name="scratch_p64p1_probe_gb_%s.vi" % time.strftime("%Y%m%d_%H%M%S"), pins=pins,
            task="lean-p64p1", out_json=os.path.join(HERE, "p64p1_lvprobe%s.json" % ("_scan2" if os.environ.get("P64P1_SCAN_GLOBS") else "")))
    sys.exit(K.run(body, st))
