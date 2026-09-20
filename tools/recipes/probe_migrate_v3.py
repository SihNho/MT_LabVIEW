r"""probe_migrate_v3.py - step 0a attempt 5: does the MIGRATED state actually compile?

Attempt 4 proved the operations (create a loop in an existing VI, drop a subVI onto its body verified by listing,
wire a control across the border with exactly one tunnel whose inner wire is the sink's). It could NOT prove the
result is legal, and while writing it up two competing explanations for its ExecState 0 turned up:

  (1) the While loop's conditional terminal was unwired - HARNESS_copyloop has no Boolean control (measured,
      tools/bench/census_boolean_controls.log: NONE of the nine harnesses has one);
  (2) **the border wire itself may be broken**: the source was `File Path` (a Path) and the sink is
      `StrToPath.vi`'s `string` (a String). docs/NAMES.md: "a wire-uid gate does not prove a wire is GOOD
      (a type-mismatched wire reads equal at both ends)" - which is precisely the gate attempt 4 used.

This run removes BOTH. It uses `HARNESS_track`, which has array controls, so:
  * a **For loop with an AUTO-INDEXED array tunnel** is complete without any `N` and without a conditional
    terminal, so explanation (1) cannot arise;
  * the border wire is **String -> String** (`Image Name` -> `StrToPath.string`), so explanation (2) cannot arise.
Then ExecState is a real verdict rather than a shrug.

PREDICTION CONTRACT:
  M1 HARNESS_track starts at ExecState 1                       (measured 2026-09-15: it does)
  M2 a For loop is created with ONE auto-indexed tunnel from `Bead is good? array in` (IndexMode 1)
  M3 the new body holds `StrToPath.vi` and nothing else        (listed, not counted)
  M4 `Image Name` -> `string` makes exactly one more tunnel, inner wire == the sink's wire
  M5 **ExecState == 1**  <- the whole point. If this fails, the in-copy migration produces illegal code and the
     method needs rethinking rather than another repair.

Scratch only, unique name, deleted at the end. No original; no hardware.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_migrate_v3.log -- py -u tools/recipes/probe_migrate_v3.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import gscript as g  # noqa: E402

CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
DONOR = os.path.join(CLAUDEDEV, "HARNESS_track.vi")
DROPPEE = os.path.join(CLAUDEDEV, "StrToPath.vi")
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_mig3_{int(time.time())}.vi")
ARRAY_CONTROL = "Bead is good? array in"      # an ARRAY -> can auto-index, so the For loop needs no N
STRING_CONTROL = "Image Name"                 # a String -> type-matches StrToPath's `string`
SINK = "string"

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def fidx(uid, cls):
    return [o["uid"] for o in g.report_all(SCRATCH, cls)].index(uid)


def sink_wire_of(sub_uid, body_i):
    nodes, _ = g.net_map(SCRATCH, diagram_index=body_i, max_nodes=40, max_terms=30)
    for _k, (uid, _lbl, terms) in nodes.items():
        if uid == sub_uid:
            for _i, nm, w in terms:
                if nm == SINK:
                    return w
    return None


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    shutil.copy2(DONOR, SCRATCH)
    st0 = g.exec_state(SCRATCH)
    print(f"scratch = {os.path.basename(SCRATCH)}   start ExecState = {st0}", flush=True)
    gate("M1 the donor starts legal", st0 == 1, str(st0))
    try:
        dg0 = g.uids(SCRATCH, "Diagram")
        tun0 = {o["uid"] for o in g.report_all(SCRATCH, "LoopTunnel")}
        g.for_loop(SCRATCH, (60, 700), tunnels=[ARRAY_CONTROL], indexing=[True])
        new_dg = g.new_since(SCRATCH, "Diagram", dg0)
        new_t1 = [o for o in g.report_all(SCRATCH, "LoopTunnel") if o["uid"] not in tun0]
        modes = []
        for o in new_t1:
            try:
                modes.append(g.tunnels(SCRATCH, o["i"]).get("index_mode"))
            except Exception as e:
                modes.append(f"err {e}")
        gate("M2 one For loop with one AUTO-INDEXED tunnel",
             len(new_dg) == 1 and len(new_t1) == 1 and modes == [1],
             f"diagrams {[d['uid'] for d in new_dg]}, tunnels {len(new_t1)}, index_mode {modes}")
        if len(new_dg) != 1:
            raise RuntimeError("cannot identify the new body")
        body_i = fidx(new_dg[0]["uid"], "Diagram")
        print(f"  body uid {new_dg[0]['uid']} at Traverse index {body_i}", flush=True)

        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, DROPPEE, body_i, (60, 40))
        names = sorted(o.get("name", "?") for o in g.subvis(SCRATCH, body_i))
        gate("M3 the body holds StrToPath.vi and nothing else", names == ["StrToPath.vi"], str(names))
        new_sub = g.new_since(SCRATCH, "SubVI", sv0)
        sub_uid = new_sub[0]["uid"] if len(new_sub) == 1 else None

        tun1 = {o["uid"] for o in g.report_all(SCRATCH, "LoopTunnel")}
        try:
            g.wire_control(SCRATCH, [STRING_CONTROL], "SubVI", fidx(sub_uid, "SubVI"), [SINK])
            print("  wire_control returned", flush=True)
        except Exception as e:
            print(f"  wire_control raised: {e}", flush=True)
        new_t2 = [o for o in g.report_all(SCRATCH, "LoopTunnel") if o["uid"] not in tun1]
        w = sink_wire_of(sub_uid, body_i)
        ok2 = False
        if len(new_t2) == 1:
            t = g.tunnels(SCRATCH, new_t2[0]["i"])
            ok2 = bool(w) and w in list(t.get("in_wires", []))
            det = f"sink wire {w}, in_wires {list(t.get('in_wires', []))}, index_mode {t.get('index_mode')}"
        else:
            det = f"{len(new_t2)} new tunnels, sink wire {w}"
        gate("M4 String -> string crosses the border on one tunnel", ok2, det)

        final = g.exec_state(SCRATCH)
        gate("M5 THE MIGRATED STATE COMPILES (ExecState == 1)", final == 1, str(final))
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("scratch deleted", flush=True)
            except Exception as e:
                print(f"scratch NOT deleted: {e}", flush=True)

    print(f"\n=== 0a attempt 5: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
