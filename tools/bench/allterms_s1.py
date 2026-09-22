r"""allterms_s1 - STEP 1 / sub-step S1: the SCAFFOLD artefact for `OpAllTerms_v0.vi`.

PRIOR ART CHECKED BEFORE A LINE WAS WRITTEN (CLAUDE.md "check what exists first"):
  * `tools/gscript.py` already owns every verb used here (`report`, `count`, `exec_state`, `fp_labels`,
    `save`); NOTHING NEW is written and no new op VI is built.
  * `tools/recipes/build_opreportall_v1.py` is the construction the brief names. Its PRODUCT,
    `claudeDev\OpReportAll_v0.vi` (md5 ffcec2c7..., 12,510 B, ExecState 1), IS ALREADY ON DISK and IS
    exactly the scaffold S1 is asked for: Open VI Reference -> Traverse for GObjects (`Class Name` is a
    FRONT-PANEL control, so 'Terminal' is a call-time input) -> a For loop fed by `References` through an
    AUTO-INDEXED input tunnel -> 4 auto-indexed output tunnels with indicators.

DEVIATION FROM THE BRIEF, STATED OUT LOUD (reported to judgement, not decided here):
  the brief's S1 says "body contents: NOTHING but the loop with the auto-indexed input tunnel". That is
  not constructible: `for_loop` (gscript:1250) creates an EMPTY loop, and the input tunnel is made only by
  WIRING `Traverse.References` to a sink INSIDE the body (build_opreportall_v1.py step 6). So the body
  keeps the donor's two property nodes, and they are not dead weight - they carry 2 of the 6 deliverable
  columns WITH NO CAST AT ALL, because Traverse yields GObject refs:
      PN1 `VI Server:GObject` [Position, UID 632A813, ClassName 6327803, Owner 6327806]  -> term_uid
      PN2 `VI Server:Generic` [ClassName 6327803] <- PN1.Owner                           -> owner_class
  Only `Name`/`Is Source?`/`Connected Wire` (Terminal-class) and `owner_uid` (GObject.UID on a Generic
  wire) still need a `To More Specific Class`, which is S2's GUI act.

PREDICTION CONTRACT (every number from `tools/bench/diag_allwires_probe.log`'s census of this donor):
  A1 the work copy is byte-identical to `OpReportAll_v0.vi`                     (Stage K3)
  A2 census ForLoop 1 / LoopTunnel 5 / Property 2 / SubVI 1
  A3 ExecState 1 warm
  A4 exactly one Diagram whose owner is a ForLoop  = the body
  A5 the 4 indicator labels are Array / Array 2 / Array 3 / Array 4, and `Class Name` is a control
  A6 the save is the SCRIPTED route (ExecState 1) and the cold re-read is 1

NOTHING IS RUN (34(f)); the only writable surface is `claudeDev\OpAllTerms_v0_s1.vi`. No restart
(`fresh=False`): a parallel material session owns LabVIEW's GUI window state. No motor, ASI or camera.
  MATERIAL=1 py tools/bgrun.py --max-min 15 --log tools/bench/allterms_s1.log -- py -u tools/bench/allterms_s1.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                               # noqa: E402
import gscript as g                                                                # noqa: E402

SRC = os.path.join(K.CLAUDEDEV, "OpReportAll_v0.vi")
SRC_MD5 = "ffcec2c75e92dcad514299ba20e66054"      # the donor's bytes, read off disk 2026-09-23
OUT = "OpAllTerms_v0_s1.vi"


def main(s):
    s.start()
    p = s.work

    s.head("[A2] the scaffold census - the donor already IS the scaffold")
    cen = dict((c, s.count(c)) for c in ("ForLoop", "LoopTunnel", "Property", "SubVI", "Wire",
                                         "ControlTerminal", "IndexArray"))
    s.R["census"] = cen
    s.fact("census {0!r}".format(cen))
    s.gate("A2 ForLoop 1 / LoopTunnel 5 / Property 2 / SubVI 1",
           cen["ForLoop"] == 1 and cen["LoopTunnel"] == 5 and cen["Property"] == 2 and cen["SubVI"] == 1,
           repr(cen), fatal=True)

    s.head("[A3] ExecState warm")
    es = s.es("scaffold, warm")
    s.gate("A3 ExecState 1 warm", es == 1, "ExecState {0!r}".format(es), fatal=True)

    s.head("[A4] the body diagram, and the GEOMETRY S2's GUI drop needs")
    dias, _e = s.safe("report(Diagram)", lambda: g.report(p, "Diagram"), [])
    body = [i for i, d in enumerate(dias or []) if "For" in str(d.get("owner"))]
    s.gate("A4 exactly one Diagram owned by a ForLoop", len(body) == 1,
           "indices {0!r}".format(body), fatal=True)
    loops, _e = s.safe("report(ForLoop)", lambda: g.report(p, "ForLoop"), [])
    props, _e = s.safe("report(Property)", lambda: g.report(p, "Property"), [])
    geo = {"body_diagram_index": body[0],
           "body_diagram_uid": dias[body[0]]["uid"],
           "forloop": {"uid": loops[0]["uid"], "pos": loops[0]["pos"]} if loops else None,
           "property_nodes": [{"uid": o["uid"], "pos": o["pos"], "owner": o["owner"]} for o in props],
           "root_objects": []}
    for cls in ("SubVI", "IndexArray", "ControlTerminal", "LoopTunnel"):
        rows, _e2 = s.safe("report({0})".format(cls), lambda c=cls: g.report(p, c), [])
        for o in (rows or []):
            geo["root_objects"].append({"class": cls, "uid": o["uid"], "pos": o["pos"],
                                        "owner": o["owner"]})
    s.R["geometry"] = geo
    s.fact("body diagram index {0} uid {1}; ForLoop {2!r}".format(
        geo["body_diagram_index"], geo["body_diagram_uid"], geo["forloop"]))
    for o in geo["property_nodes"]:
        s.fact("body Property uid {0} pos {1!r} owner {2!r}".format(o["uid"], o["pos"], o["owner"]))

    s.head("[A5] the front panel - the call-time inputs and the four existing outputs")
    labs, _e = s.safe("fp_labels", lambda: g.fp_labels(p), [])
    s.R["fp_labels"] = labs
    s.fact("fp_labels {0!r}".format(labs))
    inds = [l for _i, l, is_ind in (labs or []) if is_ind and l]
    ctls = [l for _i, l, is_ind in (labs or []) if not is_ind and l]
    s.gate("A5 the 4 donor indicators and the `Class Name` control are present",
           inds[:4] == ["Array", "Array 2", "Array 3", "Array 4"] and "Class Name" in ctls,
           "indicators {0!r} controls {1!r}".format(inds, ctls))

    s.head("[A6] SAVE the scaffold artefact")
    s.save(broken_ok=False)


S = K.Stage(SRC, SRC_MD5, "allterms_s1", fresh=False, preload=False, work_name=OUT,
            deadline_min=12.0, reserve_s=120.0,
            out_json=os.path.join(K.BENCH, "allterms_s1.json"),
            task="S1 of OpAllTerms_v0: save the SCAFFOLD (Open VI Ref -> Traverse -> For loop with the "
                 "auto-indexed input tunnel + the cast-free GObject/Generic reads) as "
                 "claudeDev\\OpAllTerms_v0_s1.vi, and record the geometry S2's GUI Quick Drop needs.")
sys.exit(K.run(main, S))
