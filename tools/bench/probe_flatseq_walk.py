r"""probe_flatseq_walk.py - cycle 19, MEASUREMENT ONLY. One runner, one bgrun, three machine questions.

  M1  can the backward walk cross a FLAT-SEQUENCE frame?  (property census + the hypothesised ids, MEASURED)
  M2  how far does a backward wire walk get from ONE in-scope site (d10 uid 44036, ASI Move Axis to Position)?
  M3  where do the limits live - the motion subVIs' OWN block diagrams, read-only.

READ-ONLY on every pre-existing .vi (CLAUDE.md rule 1). Nothing is saved. No motor moves, no serial port opened,
motor_gate.py --execute is NOT called (cycle19 Pre-decided 1). md5 of both originals AND of every instr.lib /
lab motion subVI is taken BEFORE and AFTER, and printed either way.

WHAT ALREADY EXISTED AND IS REUSED (checked before writing a line):
  gscript.report_all / node_labels / node_terms / count / uids / open_panel / close_panel / build_property
  tools/bench/census_dnc_property_ids.py     - the "attach a property id, read the data terminal name" pattern
  tools/recipes/build_opwiresource_v5.py     - OpWireSource_v5 + its labels json (wire uid -> source owner)
  tools/recipes/build_opownerchain_v1.py     - OpOwnerChain_v1 (any uid -> owner class/uid + self echo)
  tools/bench/main_vi_nodeterms.json         - the cached 170-diagram node/terminal census of the V6 copy
  docs/vi-server-ids.json, docs/NAMES.md:215 - short-name registry
NO NEW OP VI IS BUILT. The only thing created is ONE scratch VI in user.lib\claudeDev, deleted in the same run.

PREDICTION CONTRACT (each line is machine-checked and printed as PASS/FAIL):
  C1 no LabVIEW process exists at start; both originals' md5 unchanged at the end.
  C2 report_all(V6, "FlatSequenceInnerTunnel") returns >= 14 objects  [if 0, the class is not Traverse-visible,
     which is what d1-build-plan.md:735 asserts]
  C3 build_property(scratch, "VI Server:FlatSequenceInnerTunnel", [("632A813",False)]) SUCCEEDS - i.e. the class
     STRING itself resolves. If this fails, every later id failure is uninformative about the id.
  C4 1C3A9000 and 1C3A9001 both attach and their data terminals carry a short name.
  C5 the walk from d10/node1/uid 44036 terminal 8 ('Position [internal units]', wire 44089) makes >= 1 hop and
     terminates with a NAMED reason.
  C6 every motion subVI in the M3 list opens and reports >= 1 diagram.

RUN 1 (tools/bench/probe_flatseq_walk.log, BGRUN END rc=0 after 43s) - 4/6, and BOTH failures were wrong
CONSTANTS in this file, not machine facts:
  * V6 pointed inside the project folder; the working copy is one level up in "2. Tracking" -> every V6 read
    returned "error 7: Open VI Reference", so C2 and C5 were never actually tested.
  * MOV/VEL/GOH were tested with os.path.exists on an LLB-INTERNAL path, which is always False.
C3/C4 DID run and passed on run 1: 1C3A9000 -> 'LeftTerm', 1C3A9001 -> 'RightTerm', 1C3A9002 -> 'LeftFrame',
1C3A9003 -> 'RightFrame', 1C3A9004/5 and the two Tunnel ids -> error 1077. Run 2 repeats them (a partial run is
a non-result, CLAUDE.md usage-limit rule 3) and adds what run 1 could not reach.

RUN-2 CHANGES DEMANDED BY THE MANDATORY DUAL REVIEW of run 1
(archive/peer/2026-09-18-walk-run1-path-constants-{codex,opus}.md, both ANSWERED). Both arms REFUSED the claim
"two wrong constants, nothing else implicated" and named the same fix, so run 2 is instrumented, not merely
re-pathed:
  1. md5() failure no longer compares equal to itself -> C1 can no longer pass on files it never hashed.
  2. C6 counts filtered-out entries as failures (run 1's filter excluded exactly the failures).
  3. wire_source() appends and PRINTS every iteration including the breaking one, with all eight stage error
     clusters - "NO terminals at all" was the probe's default for five different causes, not a measurement.
  4. an isfile + md5 preflight (C0a/C0b) and an open control count(V6,'Diagram') (C2a), so a later error 7 is
     attributable to the class name and not to the path.
  5. THREE constants were wrong, not two: `Max Trans Pos.vi` had `zz_LabView VI` DOUBLED. All M3 paths in this
     file are resolved by Glob against the disk (the census stores callee NAMES, not paths) - the earlier
     docstring claim that they came from the census was wrong.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid  # noqa: E402

PROJ = os.path.dirname(os.path.dirname(HERE))
TRACKING = os.path.dirname(PROJ)
ORIG_3STATE = os.path.join(TRACKING, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
# RUN 1 BUG, fixed here: the V6 working copy sits BESIDE the original in "2. Tracking", not inside the project
# folder. Run 1 pointed at PROJ and every V6 read died with "error 7: Open VI Reference" (file not found),
# which is what failed C2/C5 - a wrong constant in this probe, not a fact about LabVIEW. Path confirmed from
# tools/bench/main_vi_nodeterms.json:2 and motor_census_v6-workingcopy.json target.vi.
V6 = os.path.join(TRACKING, "Min_Track N beads V6_ParallelLoop.vi")
SCR = os.path.join(g.CLAUDEDEV, "OpFsitProbe_scratch_c19.vi")
SRC_FOR_SCRATCH = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
WS_OP = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
WS_LABELS = os.path.join(HERE, "opwiresource_v5_labels.json")
OC_OP = os.path.join(g.CLAUDEDEV, "OpOwnerChain_v1.vi")
OC_LABELS = WS_LABELS   # build_opownerchain_v1.py:165 - the v1 op reuses OpWireSource_v5's label map
NODETERMS = os.path.join(HERE, "main_vi_nodeterms.json")
OUT = os.path.join(HERE, "probe_flatseq_walk.json")

LV = r"C:\Program Files\National Instruments\LabVIEW 2026"
MERC = os.path.join(LV, r"instr.lib\Mercury\GCS_LabVIEW\Low Level")
LAB = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI"
# (name, vi path LabVIEW opens, the FILE on disk whose md5 is the rule-1 evidence). MOV/VEL/GOH live INSIDE an
# .llb, which is one file - os.path.exists on an llb-internal path is always False (run 1's second bug), so the
# container is what gets hashed and the existence test is on the container.
M3_VIS = [
    ("MOV.vi (PI)", os.path.join(MERC, r"General command.llb\MOV.vi"), os.path.join(MERC, "General command.llb")),
    ("VEL.vi (PI)", os.path.join(MERC, r"General command.llb\VEL.vi"), os.path.join(MERC, "General command.llb")),
    ("GOH.vi (PI)", os.path.join(MERC, r"Limits.llb\GOH.vi"), os.path.join(MERC, "Limits.llb")),
    ("TMX?.vi (PI, the 40.94 limit query)", os.path.join(MERC, r"Limits.llb\TMX?.vi"), os.path.join(MERC, "Limits.llb")),
    ("ASI Move Axis to Position.vi", os.path.join(LV, r"instr.lib\ASI TG-1000\Public\Action\Move Axis to Position.vi"), None),
    ("ASI Move Axis Relative.vi", os.path.join(LV, r"instr.lib\ASI TG-1000\Public\Action\Move Axis Relative.vi"), None),
    ("Autonics SetCommand.vi (rotor)", os.path.join(LV, r"instr.lib\Autonics Motor\SetCommand.vi"), None),
    ("Max Trans Pos.vi (lab)", os.path.join(LAB, r"DY\Background VIs\Max Trans Pos.vi"), None),
    ("Motor control v5_No Recording.vi (lab)", os.path.join(LAB, r"SiHyeong Modified\Motor control v5_No Recording.vi"), None),
    ("ASI_adjust focus-subvi.vi (lab, FRAME LOOP)", os.path.join(LAB, r"Madcity\ASI_adjust focus-subvi.vi"), None),
]
M3_VIS = [(n, p, (c or p)) for n, p, c in M3_VIS]
# SetCommand_signed.vi: MEASURED ABSENT by Glob before this run - nowhere under G:\...\MinLab and not in
# instr.lib\Autonics Motor (which holds only Close.vi, Configure.vi, SetCommand.vi).
SIGNED_HINTS = [os.path.join(LV, r"instr.lib\Autonics Motor\SetCommand_signed.vi")]

# Node labels that MEAN "a value is being limited". Matched case-insensitively as substrings, the same way
# tools/motor_census.py recognises a VISA Write by its node label (docs/motor-call-site-census.md "How a serial
# write is recognised"). Comparison/select primitives are included because a comparison+select IS a limit.
LIMIT_PAT = ["in range and coerce", "coerce", "max & min", "max&min", "min & max", "clip",
             "greater", "less", "select", "maximum", "minimum", "limit"]

RESULTS = {"gates": [], "m1": {}, "m2": {}, "m3": {}, "md5": {}}


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {detail[:200]}" if detail else ""), flush=True)
    RESULTS["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    return ok


_ERRSEQ = [0]


def md5(p):
    """A FAILURE NEVER COMPARES EQUAL TO ITSELF. Run 1's md5() returned the same 'ERR [Errno 2] ...' string
    before and after, so gate C1 ('every pre-existing .vi md5 unchanged') PASSED for four files it had never
    hashed - review archive/peer/2026-09-18-walk-run1-path-constants-opus.md section 1. The sequence number
    makes an unhashable file a LOUD failure instead of a silent pass."""
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        _ERRSEQ[0] += 1
        return f"ERR#{_ERRSEQ[0]} {e}"


ALL_FILES = [ORIG_3STATE, V6] + sorted({c for _n, _v, c in M3_VIS})


def snapshot(tag):
    d = {}
    for p in ALL_FILES:
        d[p] = md5(p)
    RESULTS["md5"][tag] = d
    print(f"\n-- md5 {tag} --", flush=True)
    for p, h in d.items():
        print(f"   {h}  {os.path.basename(p)}", flush=True)
    return d


V6_EXPECTED_MD5 = "2a78e17c449cacdaf5da389818526859"   # motor_census_v6-workingcopy.json, 2026-09-17 23:49


def preflight():
    """Review step 0 (both arms): prove on disk, in seconds and with no COM, that every path this probe will
    hand to LabVIEW is real - and that the V6 copy is the file the cached census was taken from."""
    print("\n-- preflight (no LabVIEW) --", flush=True)
    ok = True
    for p in ALL_FILES:
        e = os.path.isfile(p)
        ok = ok and e
        print(f"   isfile={e}  {p}", flush=True)
    h = md5(V6)
    print(f"   md5(V6)={h}  expected {V6_EXPECTED_MD5}", flush=True)
    must("C0a every target path is a real file", ok)
    must("C0b the V6 working copy is the file the cached census was taken from", h == V6_EXPECTED_MD5, h)
    return ok


# ---------------------------------------------------------------- M1
FSIT_CLASS = "VI Server:FlatSequenceInnerTunnel"
# bounded candidate set, NOT a blind sweep:
#  - 632A813 GObject.UID           = positive control: proves the CLASS STRING resolves
#  - 6327803 Generic.Class Name    = second positive control
#  - 1C3A9000 / 1C3A9001           = the peer's hypothesis under test (archive/peer/2026-09-17-flatseq-tunnel-
#                                    source-addressing-r3.md:57-62)
#  - 1C3A9002..1C3A9005            = the remaining slots of the SAME class id block, so "which short names does
#                                    this class actually expose" is answered, not assumed
#  - 6356001 / 6356000             = Tunnel.Outside Terminal / Inside Terminals[]: does FSIT inherit from Tunnel?
M1_IDS = [("632A813", "CONTROL GObject.UID"), ("6327803", "CONTROL Generic.Class Name"),
          ("1C3A9000", "HYPOTHESIS Left Terminal"), ("1C3A9001", "HYPOTHESIS Right Terminal"),
          ("1C3A9002", "block census"), ("1C3A9003", "block census"), ("1C3A9004", "block census"),
          ("1C3A9005", "block census"),
          ("6356001", "Tunnel.Outside Terminal (inheritance test)"),
          ("6356000", "Tunnel.Inside Terminals[] (inheritance test)")]
SKIP = ("reference", "reference out", "error in (no error)", "error out")


def m1():
    print("\n================ M1 ================", flush=True)
    # OPEN CONTROL (both review arms asked for it): a cheap read on V6 that MUST succeed, so a later error 7 is
    # attributable to the class name rather than to the path or to loading.
    try:
        nd = g.count(V6, "Diagram")
        print(f"   OPEN CONTROL count(V6,'Diagram') = {nd}", flush=True)
        RESULTS["m1"]["open_control_diagrams"] = nd
    except Exception as e:
        RESULTS["m1"]["open_control_diagrams"] = f"EXC {str(e)[:200]}"
        print(f"   OPEN CONTROL count(V6,'Diagram') RAISED {str(e)[:200]}", flush=True)
    must("C2a the open control on V6 succeeds (so a later error 7 is not about the path)",
         isinstance(RESULTS["m1"].get("open_control_diagrams"), int)
         and RESULTS["m1"]["open_control_diagrams"] >= 100,
         str(RESULTS["m1"].get("open_control_diagrams")))
    # M1.0 - is the class visible to Traverse at all?
    try:
        objs = g.report_all(V6, "FlatSequenceInnerTunnel")
        print(f"   report_all(V6,'FlatSequenceInnerTunnel') -> {len(objs)} objects", flush=True)
        RESULTS["m1"]["traverse_count"] = len(objs)
        RESULTS["m1"]["traverse_sample"] = objs[:6]
        for o in objs[:6]:
            print(f"      uid={o['uid']} class={o['class']!r} owner={o['owner']!r} pos={o['pos']}", flush=True)
    except Exception as e:
        print(f"   report_all(V6,'FlatSequenceInnerTunnel') RAISED: {str(e)[:220]}", flush=True)
        RESULTS["m1"]["traverse_count"] = f"EXC {str(e)[:200]}"
    must("C2 FlatSequenceInnerTunnel is Traverse-visible (>=14)",
         isinstance(RESULTS["m1"].get("traverse_count"), int) and RESULTS["m1"]["traverse_count"] >= 14,
         str(RESULTS["m1"].get("traverse_count")))

    # M1.1 - the property census, on a SCRATCH VI in claudeDev (never on an original)
    if os.path.exists(SCR):
        os.remove(SCR)
    shutil.copyfile(SRC_FOR_SCRATCH, SCR)
    time.sleep(0.4)
    rows = []
    try:
        g.open_panel(SCR)
        time.sleep(0.8)
        y = 260
        for pid, why in M1_IDS:
            before = g.uids(SCR, "Property")
            rec = {"id": pid, "why": why}
            try:
                g.build_property(SCR, FSIT_CLASS, [(pid, False)], (1500, y))
                y += 110
                new = [u for u in g.uids(SCR, "Property") if u not in before]
                if len(new) != 1:
                    rec["outcome"] = f"{len(new)} new property nodes (expected 1)"
                else:
                    # read the new node's terminal names by locating it among diagram-0 nodes
                    names = []
                    labs = g.node_labels(SCR, 0)
                    idx = [i for i, r in enumerate(labs) if r["uid"] == new[0]]
                    if idx:
                        tr = g.node_terms(SCR, 0, idx[0])
                        names = [r["name"] for r in tr if r["name"] not in SKIP]
                    rec["outcome"] = "ATTACHED"
                    rec["short_names"] = names
                    rec["uid"] = new[0]
            except Exception as e:
                rec["outcome"] = f"REFUSED {str(e)[:200]}"
            print(f"   {pid} [{why}] -> {rec['outcome']}"
                  + (f"  short names {rec.get('short_names')}" if rec.get("short_names") is not None else ""),
                  flush=True)
            rows.append(rec)
    finally:
        try:
            g.close_panel(SCR)
        except Exception as e:
            print(f"   close_panel EXC {str(e)[:100]}", flush=True)
        time.sleep(0.5)
        if os.path.exists(SCR):
            os.remove(SCR)
            print("   scratch VI deleted (never saved over anything)", flush=True)
    RESULTS["m1"]["property_census"] = rows
    by = {r["id"]: r for r in rows}
    must("C3 the class string 'VI Server:FlatSequenceInnerTunnel' itself resolves (632A813 control)",
         by.get("632A813", {}).get("outcome") == "ATTACHED", str(by.get("632A813")))
    must("C4 1C3A9000 and 1C3A9001 both ATTACH",
         by.get("1C3A9000", {}).get("outcome") == "ATTACHED" and by.get("1C3A9001", {}).get("outcome") == "ATTACHED",
         f"{by.get('1C3A9000', {}).get('outcome')} / {by.get('1C3A9001', {}).get('outcome')}")

    # M1.2 - the 14 REAL instances: do their uids resolve, and what does the existing owner-chain op say?
    try:
        with open(os.path.join(HERE, "probe_flatseq_instances.json"), encoding="utf-8") as f:
            inst = json.load(f)
    except Exception:
        inst = []
    oc_rows = []
    if os.path.exists(OC_OP) and os.path.exists(OC_LABELS) and inst:
        with open(OC_LABELS, encoding="utf-8") as f:
            lab = json.load(f)
        vi = g.op(OC_OP)
        for rec in inst[:14]:
            u = rec["fsit_uid"]
            r = {"fsit_uid": u}
            try:
                for k in (lab["ownercls"], lab["cls_back"], lab["cast_class"]):
                    vi.SetControlValue(k, "POISON")
                for k in (lab["owner_uid"], lab["uid_back"]):
                    vi.SetControlValue(k, 0)
                vi.SetControlValue("vi path", V6)
                vi.SetControlValue(lab["uid_in"], int(u))
                vi.SetControlValue(lab["term_index"], 0)
                g._run(vi)
                r["uid_back"] = int(vi.GetControlValue(lab["uid_back"]))
                r["cls_back"] = vi.GetControlValue(lab["cls_back"])
                r["owner_class"] = vi.GetControlValue(lab["ownercls"])
                r["owner_uid"] = int(vi.GetControlValue(lab["owner_uid"]))
                r["cast_class"] = vi.GetControlValue(lab["cast_class"])
                r["err"] = g._err(vi, "error out") or ""
                r["errs"] = " ".join(x for x in (g._err(vi, lab[k]) or ""
                                                 for k in ("errL", "errT", "errO", "errU", "errG")) if x)[:160]
            except Exception as e:
                r["err"] = f"EXC {str(e)[:150]}"
            print(f"      FSIT uid {u} -> self {r.get('uid_back')}/{r.get('cls_back')!r} "
                  f"owner {r.get('owner_class')!r} uid {r.get('owner_uid')} "
                  f"cast {r.get('cast_class')!r} {('ERR ' + str(r.get('err'))[:60]) if r.get('err') else ''} "
                  f"{str(r.get('errs', ''))[:80]}", flush=True)
            oc_rows.append(r)
    else:
        print(f"   OpOwnerChain_v1 present={os.path.exists(OC_OP)} labels={os.path.exists(OC_LABELS)} "
              f"instances={len(inst)} - instance read SKIPPED", flush=True)
    RESULTS["m1"]["ownerchain_on_instances"] = oc_rows


# ---------------------------------------------------------------- M2
def load_uid_index():
    with open(NODETERMS, encoding="utf-8") as f:
        d = json.load(f)
    idx = {}
    for dk, v in d["diagrams"].items():
        for nd in v.get("nodes", []):
            idx[nd["uid"]] = {"diagram": int(dk), "n": nd["n"], "owner": v.get("owner"),
                              "terms": nd.get("terms", [])}
    return d, idx


def m2():
    print("\n================ M2 ================", flush=True)
    d, idx = load_uid_index()
    print(f"   cached census: {d['vi']}  ({len(idx)} nodes over {len(d['diagrams'])} diagrams)", flush=True)
    if not (os.path.exists(WS_OP) and os.path.exists(WS_LABELS)):
        must("C5 OpWireSource_v5 + labels are on disk", False, f"{WS_OP} / {WS_LABELS}")
        return
    with open(WS_LABELS, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(WS_OP)
    labels_by_uid = {}

    def label_of(uid):
        if uid in labels_by_uid:
            return labels_by_uid[uid]
        info = idx.get(uid)
        if not info:
            return ""
        try:
            rows = g.node_labels(V6, info["diagram"])
            for r in rows:
                labels_by_uid[r["uid"]] = r["label"]
        except Exception:
            pass
        return labels_by_uid.get(uid, "")

    def wire_source(wire_uid):
        """The single SOURCE terminal of `wire_uid`: owner class + owner uid. Walks Terms[] until 1055.

        RUN-1 DEFECT, fixed here (both review arms, 2026-09-18): the break discarded `r` INCLUDING its error,
        so five mutually exclusive causes (path missing / empty Terminals[] / uid not a Wire / property read
        failed / label mismatch) all printed the identical string 'returned NO terminals at all'. Every
        iteration is now appended and every stage error cluster is printed, so the breaking iteration REPORTS
        its own cause."""
        out = []
        for i in range(8):
            for k in ("ownercls", "cls_back"):
                try:
                    vi.SetControlValue(lab[k], "POISON")
                except Exception:
                    pass
            for k in ("uid_back", "owner_uid", "recip_wire"):
                try:
                    vi.SetControlValue(lab[k], 0)
                except Exception:
                    pass
            try:
                vi.SetControlValue(lab["is_source"], False)
                vi.SetControlValue(lab["cast_class"], "POISON")
            except Exception:
                pass
            vi.SetControlValue("vi path", V6)
            vi.SetControlValue(lab["uid_in"], int(wire_uid))
            vi.SetControlValue(lab["term_index"], i)
            try:
                g._run(vi)
                err = g._err(vi, "error out") or ""
            except Exception as e:
                err = f"EXC {str(e)[:90]}"
            stage = {}
            for k in ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO"):
                try:
                    stage[k] = g._err(vi, lab[k]) or ""
                except Exception:
                    stage[k] = ""
            r = {"i": i, "is_source": bool(vi.GetControlValue(lab["is_source"])),
                 "owner_class": vi.GetControlValue(lab["ownercls"]),
                 "owner_uid": int(vi.GetControlValue(lab["owner_uid"])),
                 "uid_back": int(vi.GetControlValue(lab["uid_back"])),
                 "wire_class": vi.GetControlValue(lab["cls_back"]),
                 "cast_class": vi.GetControlValue(lab["cast_class"]),
                 "recip_wire": int(vi.GetControlValue(lab["recip_wire"])), "err": err,
                 "stage_errs": {k: v for k, v in stage.items() if v}}
            out.append(r)      # APPEND FIRST - run 1 threw the breaking iteration away with its error in it
            print(f"         Terms[{i}] src={r['is_source']} owner {r['owner_class']!r:.24} uid {r['owner_uid']} "
                  f"uid_back={r['uid_back']} wireclass={r['wire_class']!r:.20} recip={r['recip_wire']} "
                  f"err={r['err'][:70]!r} stage={ {k: v[:48] for k, v in r['stage_errs'].items()} }", flush=True)
            if r["owner_uid"] == 0 and not r["is_source"] and r["owner_class"] in ("POISON", ""):
                break
        srcs = [r for r in out if r["is_source"] and r["recip_wire"] == int(wire_uid)]
        return (srcs[0] if srcs else None), out

    start = {"diagram": 10, "node_index": 1, "uid": 44036,
             "callee": "ASI TG-1000.lvlib:Move Axis to Position.vi"}
    seeds = [(8, "Position [internal units]", 44089), (9, "Axis", 44104), (10, "VISA in", 44107)]
    walks = []
    for term_i, term_name, wire0 in seeds:
        print(f"\n   --- backward walk from d10 Nodes[1] (uid 44036) T[{term_i}] {term_name!r}, wire {wire0} ---",
              flush=True)
        chain = []
        wire = wire0
        cur_uid = 44036
        stop = ""
        for hop in range(1, 13):
            src, allterms = wire_source(wire)
            if src is None:
                first = allterms[0] if allterms else {}
                stop = (f"hop {hop}: wire {wire} has NO terminal that is a source pointing back at it. "
                        f"{len(allterms)} iteration(s) read; Terms[0] err={first.get('err', '')!r} "
                        f"stage={first.get('stage_errs', {})} uid_back={first.get('uid_back')} "
                        f"wire_class={first.get('wire_class')!r}")
                chain.append({"hop": hop, "wire": wire, "terms_read": allterms})
                break
            oc, ou = src["owner_class"], src["owner_uid"]
            lbl = label_of(ou)
            chain.append({"hop": hop, "wire": wire, "owner_class": oc, "owner_uid": ou, "label": lbl,
                          "is_source": src["is_source"], "err": src["err"]})
            print(f"      hop {hop}: wire {wire} <- {oc} uid {ou} {('label ' + repr(lbl)) if lbl else ''} "
                  f"{('ERR ' + src['err'][:60]) if src['err'] else ''}", flush=True)
            if not src["is_source"]:
                stop = f"hop {hop}: no terminal of wire {wire} reports Is Source? TRUE (net broken or unreadable)"
                break
            info = idx.get(ou)
            if info is None:
                stop = (f"hop {hop}: owner uid {ou} of class {oc!r} is NOT a node on any of the 170 cached "
                        f"diagrams - the walk cannot address it as Diagram[d].Nodes[n]")
                break
            ins = [t for t in info["terms"] if not t["is_source"] and t["wire"]]
            if not ins:
                stop = (f"hop {hop}: {oc} uid {ou} (d{info['diagram']} Nodes[{info['n']}]) has no wired INPUT "
                        f"terminal - the walk reached a source node")
                break
            nxt = ins[0]
            print(f"         -> continuing through its input T[{nxt['i']}] {nxt['name']!r} wire {nxt['wire']}",
                  flush=True)
            wire = nxt["wire"]
            cur_uid = ou
        else:
            stop = "hop limit 12 reached without terminating"
        print(f"      STOP: {stop}", flush=True)
        walks.append({"from_terminal": term_i, "terminal_name": term_name, "hops": chain, "stop": stop})
    RESULTS["m2"] = {"start": start, "walks": walks}
    n0 = len(walks[0]["hops"]) if walks else 0
    must("C5 the walk from T[8] made >=1 hop and named its stop reason",
         n0 >= 1 and bool(walks[0]["stop"]), f"{n0} hops; stop={walks[0]['stop'][:120] if walks else ''}")


# ---------------------------------------------------------------- M3
def m3():
    print("\n================ M3 ================", flush=True)
    found_any = 0
    for name, path, container in M3_VIS:
        rec = {"path": path, "container": container, "exists": os.path.exists(container)}
        print(f"\n   --- {name}\n       {path}", flush=True)
        if not rec["exists"]:
            print(f"       CONTAINER NOT ON DISK: {container}", flush=True)
            RESULTS["m3"][name] = rec
            continue
        try:
            nd = g.count(path, "Diagram")
            rec["diagrams"] = nd
            print(f"       diagrams={nd}", flush=True)
        except Exception as e:
            rec["diagrams"] = f"EXC {str(e)[:160]}"
            print(f"       count(Diagram) RAISED {str(e)[:160]}", flush=True)
            RESULTS["m3"][name] = rec
            continue
        hits = []
        alllabels = []
        for di in range(int(nd)):
            try:
                rows = g.node_labels(path, di)
            except Exception as e:
                print(f"       d{di}: node_labels RAISED {str(e)[:120]}", flush=True)
                continue
            for r in rows:
                alllabels.append({"d": di, "uid": r["uid"], "label": r["label"]})
                lo = (r["label"] or "").lower()
                if any(p in lo for p in LIMIT_PAT):
                    hits.append({"d": di, "uid": r["uid"], "label": r["label"]})
        rec["n_labels"] = len(alllabels)
        rec["limit_nodes"] = hits
        print(f"       nodes with a label read: {len(alllabels)}; LIMITING-construct matches: {len(hits)}",
              flush=True)
        for h in hits:
            print(f"         HIT d{h['d']} uid {h['uid']} label {h['label']!r}", flush=True)
        found_any += len(hits)
        # for each hit, where is each input fed from?
        if hits:
            try:
                with open(WS_LABELS, encoding="utf-8") as f:
                    lab = json.load(f)
                vi = g.op(WS_OP)
            except Exception:
                lab, vi = None, None
            for h in hits[:8]:
                try:
                    rows = g.node_labels(path, h["d"])
                    ni = [i for i, r in enumerate(rows) if r["uid"] == h["uid"]]
                    if not ni:
                        continue
                    tr = g.node_terms(path, h["d"], ni[0])
                    h["terms"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                                   "wire": t["wire"]} for t in tr]
                    for t in tr:
                        if t["is_source"] or not t["wire"] or lab is None:
                            continue
                        vi.SetControlValue("vi path", path)
                        vi.SetControlValue(lab["uid_in"], int(t["wire"]))
                        src = None
                        for k in range(6):
                            vi.SetControlValue(lab["term_index"], k)
                            try:
                                g._run(vi)
                            except Exception:
                                break
                            if bool(vi.GetControlValue(lab["is_source"])):
                                src = {"owner_class": vi.GetControlValue(lab["ownercls"]),
                                       "owner_uid": int(vi.GetControlValue(lab["owner_uid"]))}
                                break
                        lbl = ""
                        if src:
                            for r2 in rows:
                                if r2["uid"] == src["owner_uid"]:
                                    lbl = r2["label"]
                        print(f"           input T[{t['i']}] {t['name']!r} wire {t['wire']} <- "
                              f"{src if src else 'NO SOURCE READ'} label {lbl!r}", flush=True)
                        t_rec = {"term": t["i"], "name": t["name"], "wire": t["wire"], "src": src, "src_label": lbl}
                        h.setdefault("feeds", []).append(t_rec)
                except Exception as e:
                    print(f"         feed read RAISED {str(e)[:140]}", flush=True)
        RESULTS["m3"][name] = rec
    for p in SIGNED_HINTS:
        print(f"   SetCommand_signed candidate exists={os.path.exists(p)}  {p}", flush=True)
    # C6 counts a FILTERED-OUT entry as a failure. Run 1's version excluded exactly the rows that failed
    # (`if v.get("exists")`) and passed while printing four Nones - review opus section 1.
    must("C6 EVERY M3 entry (all of them, no filter) opened and reported >= 1 diagram",
         len(RESULTS["m3"]) == len(M3_VIS)
         and all(isinstance(v.get("diagrams"), int) and v["diagrams"] >= 1 for v in RESULTS["m3"].values()),
         str({k: v.get("diagrams") for k, v in RESULTS["m3"].items()}))


def main():
    print("PREDICTION CONTRACT C1..C6 - see this file's docstring.", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    before = snapshot("before")
    preflight()
    try:
        fresh()
        m1()
        m2()
        m3()
    finally:
        try:
            g.reset()          # close/forget every cached VI Server proxy (CLAUDE.md reference hygiene)
        except Exception:
            pass
        after = snapshot("after")
        same = [p for p in before if before[p] == after[p]]
        must("C1 every pre-existing .vi md5 unchanged", len(same) == len(before),
             str([os.path.basename(p) for p in before if before[p] != after[p]]))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RESULTS, f, indent=1, default=str)
        npass = sum(1 for x in RESULTS["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RESULTS['gates'])} pass; failing: "
              f"{[x['label'][:40] for x in RESULTS['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
