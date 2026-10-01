r"""diag_c123_imgtype - card 123-1 S6 (brief_123-1.md step 6): READ-ONLY on a never-saved byte copy of the SAVED P2b file
claudeDev\D1_ring_p2b_20261001_140658.vi (md5 652b1447...): for every IMAQ Create (a SubVI with terminals 'Image Type' + 'Border Size' +
'New Image') - expected #20436 (the panel IMAQimage writer, PD242(c)), #13938 ('Cam', PD234) and #23099 inside For #23093 (body #23169,
facts_c122_p3.json:1165-1178) - record the SOURCE of its 'Image Type' input (uid + class, or "unwired") and that source's value via
gscript.read_const_value. Writes tools/bench/facts_c123_imgtype.json. A class the reader cannot read: class recorded, value OPEN (no new reader).
PRIOR ART: diag_c122_route.py graph() (read_live with reused fs_tunnel_pairs + build_d1_v0.owner_of strict=False), diag_c118_r1v.py R1b
(read_const_value on RingConstant #13245: value 0, representation 6). OFFLINE PRE-READ diag_c123_imgtype_offline.log (P2a graph): sources
RingConstant #20327 (-> #20436), #13245 (-> #13938), #26846 (-> #23099). No owner_of on #4866. No save, no run, no write op.
PREDICTION: I1 exactly 3 IMAQ Create nodes {20436, 13938, 23099}; I2 each 'Image Type' wired to ONE RingConstant source == the offline
pre-read; I3 owner_of(#23169) == ForLoop #23093; V each ring value read with uid echo and no error; X input md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c123_imgtype.log -- py -u tools/bench/diag_c123_imgtype.py"""
import json, os, sys, time                                                           # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))   # noqa: E702
import stagekit as K                                                                 # noqa: E402
g = K.g
VI, VIM = os.path.join(g.CLAUDEDEV, "D1_ring_p2b_20261001_140658.vi"), "652b1447ebbda761a7d5ba36455a0fa1"
FSP = os.path.join(HERE, "graph_qrt_pool_20260928.json")
OUTJ, OUTF = os.path.join(HERE, "diag_c123_imgtype.json"), os.path.join(HERE, "facts_c123_imgtype.json")
EXP_SRC = {20436: 20327, 13938: 13245, 23099: 26846}                                # offline pre-read (P2a graph)
FOR_UID, FOR_BODY = 23093, 23169
DRY = bool(getattr(g.report_all, "_dry", False))
s = K.Stage(VI, VIM, "scratch_c123_imgtype", preload=False, deadline_min=22, reserve_s=150, out_json=OUTJ, task="card 123-1 S6")
SIG = {"Image Type", "Border Size", "New Image"}


def body(_):
    s.start(); s.scratches.append(s.work); W = s.work                                 # noqa: E702
    fsp = json.load(open(FSP, encoding="utf-8"))["fs_tunnel_pairs"]
    lv = K.mod("wiki_build").read_live(W, fs_pairs=fsp)
    T = lv["terminals"]
    cls_of = dict((int(o["uid"]), o["class"]) for o in lv["objs"])
    byown = {}
    for r in T:
        byown.setdefault(int(r["owner_uid"]), []).append(r)
    creates = sorted(u for u, rs in byown.items() if cls_of.get(u) == "SubVI" and SIG <= set(r["term_name"] for r in rs))
    s.fact("IMAQ Create candidates (SubVI with terminals {0}): {1}".format(sorted(SIG), creates))
    s.gate("I1 IMAQ Create nodes == {0}".format(sorted(EXP_SRC)), DRY or creates == sorted(EXP_SRC), creates)
    src = dict((int(r["wire_uid"]), r) for r in T if r["is_source"] and r["wire_uid"])
    BD, rows, owners = K.mod("build_d1_v0"), [], {}
    for u in creates:
        it = [r for r in byown[u] if r["term_name"] == "Image Type"]
        t = it[0] if len(it) == 1 else None
        w = int(t["wire_uid"] or 0) if t else 0
        sr = src.get(w) if w else None
        fr = int(t["frame_diagram"] or 0) if t else 0
        if fr and fr not in owners and fr == FOR_BODY:
            v = s.safe("owner_of #{0}".format(fr), lambda: BD.owner_of(W, fr, strict=False), ("?", 0))[0] or ("?", 0)
            owners[fr] = [str(v[0]), int(v[1] or 0)]
        row = {"imaq_create": u, "image_type_term": int(t["term_uid"]) if t else None, "frame_diagram": fr, "frame_owner": owners.get(fr),
               "wire": w or None, "source": None, "value": None, "value_status": None}
        if not w or sr is None:
            row["source"], row["value_status"] = "unwired", "n/a (unwired: IMAQ Create default)"
        else:
            row["source"] = {"uid": int(sr["owner_uid"]), "class": sr["owner_class"], "term": sr["term_name"], "frame_diagram": int(sr["frame_diagram"] or 0)}
            cv, err = s.safe("read_const_value #{0}".format(sr["owner_uid"]), lambda: g.read_const_value(W, int(sr["owner_uid"])), {})
            cv = cv or {}
            s.fact("V #{0} -> source #{1} {2}: {3}".format(u, sr["owner_uid"], sr["owner_class"], json.dumps(cv, default=str)[:400]))
            if cv and not cv.get("err") and cv.get("echo") == int(sr["owner_uid"]):
                row["value"], row["type"], row["route"], row["value_status"] = cv.get("value"), cv.get("type"), cv.get("route"), "READ"
            else:
                row["value_status"] = "OPEN (reader: {0})".format(str(err or cv.get("err"))[:200])
        rows.append(row)
        s.gate("I2 #{0} 'Image Type' source == RingConstant #{1} (offline pre-read)".format(u, EXP_SRC.get(u)), DRY or (isinstance(row["source"], dict)
               and row["source"]["uid"] == EXP_SRC.get(u) and row["source"]["class"] == "RingConstant"), row["source"])
        s.gate("V #{0}: source value READ (uid echo, no error)".format(u), DRY or row["value_status"] == "READ", (row["value"], row["value_status"]))
    s.gate("I3 owner_of(#{0}) == ForLoop #{1}".format(FOR_BODY, FOR_UID), DRY or owners.get(FOR_BODY) == ["ForLoop", FOR_UID], owners.get(FOR_BODY))
    if not DRY:
        json.dump({"schema": "facts-imgtype/1", "card": "123-1", "vi": VI, "vi_md5": VIM, "read_on": "never-saved byte copy (deleted)",
                   "log": "tools/bench/diag_c123_imgtype.log", "script": "tools/bench/diag_c123_imgtype.py", "rows": rows,
                   "for_loop": {"uid": FOR_UID, "body": FOR_BODY, "owner_read": owners.get(FOR_BODY)},
                   "note": "IMAQ Create identified by terminal signature {0}; ring value is the numeric item value (enum text not read)".format(sorted(SIG)),
                   "t": time.strftime("%Y-%m-%d %H:%M:%S")}, open(OUTF, "w", encoding="utf-8"), indent=1, default=str)
        s.fact("WROTE {0}".format(OUTF))
    s.dump()


if __name__ == "__main__":
    rc = K.run(body, s)
    DRY or K.mod("stagexec").kill_labview_at_exit()
    sys.exit(rc)
