r"""probe_migrate_v2.py - step 0a attempt 4, built on the calls the queue core actually used.

Attempts 1-3 all failed on ADDRESSING, never on capability, and each time I invented a way to turn a new object
into a Traverse index instead of using the one the fleet already had:

    attempt 1,2  count("Diagram") - 1          -> "the newest is last". It is not.
    attempt 3    list(uids(...)).index(uid)    -> uids() is a SET COMPREHENSION; that was hash order.
    correct      fidx(uid, cls) = [o["uid"] for o in report_all(target, cls)].index(uid)

`fidx` is lifted verbatim from tools/recipes/build_track_v6_queue.py, the recipe that built the 162/162 queue core,
and `report_all` returns an ORDERED list. The border wire likewise uses that recipe's call - `wire_control`, with
the gate from its `indexed_in`: exactly one new LoopTunnel, and the sink terminal's wire appears among the tunnel's
inner wires. Attempt 3 used `g.wire(..., "LoopTunnel", ...)` and got error 1057; that was never the right tool.

PREDICTION CONTRACT:
  K1 the new body is identified by UID and its contents are LISTED: it holds StrToPath.vi and nothing else
  K2 wire_control("File Path" -> StrToPath.string) creates exactly ONE new LoopTunnel
  K3 that tunnel's inner wire IS the wire on StrToPath's `string` terminal   <- the migration wiring, proven or not
  K4 ExecState is reported. It is EXPECTED to be 0: HARNESS_copyloop has no Boolean control, so the new While
     loop's conditional terminal cannot be wired, and gscript.while_loop documents that this alone breaks the VI.
     K4 is therefore a RECORD, not a gate - deciding "is the migrated state otherwise legal" needs VI.Get Errors
     (method 452), which the fleet has never built and which the cycle-7 retrospective already named.

Scratch only, unique name per run, deleted at the end. No original; no hardware.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_migrate_v2.log -- py -u tools/recipes/probe_migrate_v2.py
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
DONOR = os.path.join(CLAUDEDEV, "HARNESS_copyloop.vi")
DROPPEE = os.path.join(CLAUDEDEV, "StrToPath.vi")
SCRATCH = os.path.join(CLAUDEDEV, f"SCRATCH_mig2_{int(time.time())}.vi")
SINK = "string"
SRC_CONTROL = "File Path"

passes, fails = [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)


def fidx(uid, cls):
    """uid -> Traverse index, via the ORDERED report_all list. build_track_v6_queue.py's helper, verbatim."""
    return [o["uid"] for o in g.report_all(SCRATCH, cls)].index(uid)


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    shutil.copy2(DONOR, SCRATCH)
    print(f"scratch = {os.path.basename(SCRATCH)}   start ExecState = {g.exec_state(SCRATCH)}", flush=True)
    try:
        # the destination loop, with NO tunnel - the border wire is what this probe is about
        dg0 = g.uids(SCRATCH, "Diagram")
        g.while_loop(SCRATCH, (40, 400))
        new_dg = g.new_since(SCRATCH, "Diagram", dg0)
        if len(new_dg) != 1:
            raise RuntimeError(f"expected one new Diagram, got {[d['uid'] for d in new_dg]}")
        body_uid = new_dg[0]["uid"]
        body_i = fidx(body_uid, "Diagram")
        print(f"  new body uid {body_uid}, Traverse index {body_i} "
              f"(new_since reported i={new_dg[0]['i']})", flush=True)

        # drop, then LIST the body - the check attempts 1-3 never made
        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, DROPPEE, body_i, (60, 40))
        listing = g.subvis(SCRATCH, body_i)
        names = sorted(o.get("name", "?") for o in listing)
        gate("K1 the new body holds StrToPath.vi and nothing else", names == ["StrToPath.vi"], str(names))
        new_sub = g.new_since(SCRATCH, "SubVI", sv0)
        if len(new_sub) != 1:
            raise RuntimeError(f"expected one new SubVI, got {[o['uid'] for o in new_sub]}")
        sub_uid = new_sub[0]["uid"]

        # the border wire, with build_track_v6_queue.py's own gate
        tun0 = {o["uid"] for o in g.report_all(SCRATCH, "LoopTunnel")}
        try:
            g.wire_control(SCRATCH, [SRC_CONTROL], "SubVI", fidx(sub_uid, "SubVI"), [SINK])
            print("  wire_control returned", flush=True)
        except Exception as e:
            print(f"  wire_control raised: {e}", flush=True)
        new_t = [o for o in g.report_all(SCRATCH, "LoopTunnel") if o["uid"] not in tun0]
        gate("K2 exactly one new LoopTunnel", len(new_t) == 1, f"{len(new_t)} new")

        inner_ok, detail = False, "no tunnel to inspect"
        if len(new_t) == 1:
            t = g.tunnels(SCRATCH, new_t[0]["i"])
            nodes, _ = g.net_map(SCRATCH, diagram_index=body_i, max_nodes=40, max_terms=30)
            sink_wire = None
            for _k, (uid, _lbl, terms) in nodes.items():
                if uid == sub_uid:
                    for _i, nm, w in terms:
                        if nm == SINK:
                            sink_wire = w
            inner_ok = bool(sink_wire) and sink_wire in list(t.get("in_wires", []))
            detail = f"sink wire {sink_wire}, tunnel in_wires {list(t.get('in_wires', []))}, " \
                     f"index_mode {t.get('index_mode')}"
        gate("K3 the tunnel's inner wire IS StrToPath's `string` wire", inner_ok, detail)

        print(f"\n  K4 RECORD (not a gate): ExecState = {g.exec_state(SCRATCH)} "
              f"- expected 0, the While loop's conditional terminal has no Boolean control to wire "
              f"(HARNESS_copyloop's only controls are Image Name, Image Name 2, File Path). Deciding whether the "
              f"MIGRATED part is otherwise legal needs VI.Get Errors (452), which is not built.", flush=True)
    finally:
        g._lv = None
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                print("scratch deleted", flush=True)
            except Exception as e:
                print(f"scratch NOT deleted: {e}", flush=True)

    print(f"\n=== 0a attempt 4: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + " ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
