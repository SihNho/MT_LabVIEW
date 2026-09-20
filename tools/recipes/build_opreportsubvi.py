"""build_opreportsubvi.py - OpReportSubVI_v0.vi: every SubVI call site WITH ITS NAME, as arrays.

WHY THIS IS THE BLOCKING TOOL. The user asked which COM port each instrument actually uses, and the honest answer
was that I did not know - the byte scan sees the strings `M-126.PD1, COM4 9600` and `M-126.PD1, COM5 115200` but
cannot tell which is wired. The user's reply was the correction:

    "모터 COM port 관련해서도 configuration 코드 부분에 상수로 다 잡혀 있는데, 뭐를 확인한건지 모르겠어.
     현재 코드 기준이라고"

Right: the ports are CONSTANTS in the configuration section. They are not a matter for inference, they are a
matter for reading. But to read them I first have to FIND the configuration section, and that means knowing which
SubVI node is `Mercury_GCS_Configuration_Setup.vi`, which is `Configure.vi`, and so on. `report_all` returns
uid/class/pos/owner - no names. Hence this op.

DONOR: OpReportAll_v0 (built 2026-09-13), which already has the whole machine - Traverse -> For Loop -> property
node inside -> auto-indexed output tunnels -> array indicators. Only the property node's CLASS and PROPERTIES
change, plus two more outputs.

    SubVI.VI Name 635E401      SubVI.VI Path 635E403        (docs/vi-server-ids.json, not guessed)

THE ONE REAL RISK, and it is handled rather than hoped away: `Traverse('SubVI')` returns **GObject**-typed
references, and a SubVI-class property node may refuse them without a `To More Specific Class` cast in between.
If that is what happens, the failure is loud (ExecState 0, or error 1057 "cannot be cast to the specified type")
and the recipe refuses to save - it does not leave a half-built op on disk. The fallback is then to copy
OpSetIndexMode_v0's cast chain, which already does exactly this for LoopTunnel.

TERMINAL NAMES are the other known trap - three build cycles were lost to them on 2026-09-13. The expected short
names are below; on a miss the recipe dumps net_map so the real ones can be READ instead of guessed again.

SAFETY: builds a NEW file; OpReportAll_v0 is never modified. Saves only when ExecState == 1.
  py tools/bgrun.py --max-min 25 --log tools/bench/build_opreportsubvi.log -- py -u tools/recipes/build_opreportsubvi.py
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReportAll_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpReportSubVI_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opreportsubvi_labels.json")

P_VINAME = "635E401"        # SubVI.VI Name
P_VIPATH = "635E403"        # SubVI.VI Path
# Terminal SHORT names, read off the machine by net_map on run 1 - `VI Name`/`VI Path` (with spaces) were wrong,
# the same trap that cost three build cycles on 2026-09-13.
T_VINAME, T_VIPATH = "VIName", "VIPath"

g._run.__defaults__ = (6.0, 120.0)
STEPS = []


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    try:
        obs = fn()
        print(f"   OBSERVED: {obs}", flush=True)
        STEPS.append((name, "ok"))
        return obs
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:260]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def snap(tag=""):
    return (f"{tag} ForLoop={g.count(OP,'ForLoop')} LoopTunnel={g.count(OP,'LoopTunnel')} "
            f"Property={g.count(OP,'Property')} CtlTerm={g.count(OP,'ControlTerminal')} "
            f"Wire={g.count(OP,'Wire')} ExecState={g.exec_state(OP)}")


def inds():
    return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def dump_names(why):
    print(f"\n-- net_map ({why}) - read the REAL terminal names here --", flush=True)
    for d in (0, 1):
        try:
            print(f"   diagram {d}:", flush=True)
            for row in g.net_map(OP, d, max_nodes=40, max_terms=24):
                print("     ", row, flush=True)
        except Exception as e:
            print(f"     diagram {d} EXC {str(e)[:160]}", flush=True)


def main():
    g._lv = None
    try:
        g.close_panel(OP)
        time.sleep(0.4)
    except Exception:
        pass
    if os.path.exists(OP):
        try:
            os.remove(OP)
        except OSError as e:
            print(f"cannot replace {OP}: {e}", flush=True)
            return 1
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.open_panel(OP)
    time.sleep(1.0)
    print(snap("start:"), flush=True)

    body = [i for i, d in enumerate(g.report(OP, "Diagram")) if "For" in str(d.get("owner"))]
    if not body:
        print("STOP: no loop body diagram in the donor", flush=True)
        return 2
    body = body[0]
    print(f"loop body diagram = {body}", flush=True)

    # Capture the donor's property nodes BEFORE adding ours. Run 1 read `report(OP,"Property")[0]` AFTER the
    # build and got the NEW node back - report() is not in creation order - so the recipe wired the new node's
    # `reference out` to its own `reference`. ExecState went to 0 and the failure looked like "a SubVI-class node
    # rejects a GObject reference", which it was not. Identify by UID captured up front instead.
    donor_pns = [o["uid"] for o in g.report(OP, "Property")]
    print(f"donor property nodes (by uid): {donor_pns}", flush=True)

    pn = step("1 Property(SubVI.VI Name, VI Path) INSIDE the loop body",
              "Property 2->3",
              lambda: g.build_property(OP, "VI Server:SubVI",
                                       [(P_VINAME, False), (P_VIPATH, False)],
                                       (1450, 1350), diagram_index=body))
    if not pn:
        print("\nSTOP: no property node. Nothing saved.", flush=True)
        return 3
    pn_uid = pn[-1]["uid"]

    def pidx(uid):
        return [o["uid"] for o in g.report(OP, "Property")].index(uid)

    # Feed it from the EXISTING GObject property node's `reference out`, which is already the per-iteration
    # object - that also orders the two nodes. If a SubVI-class node refuses a GObject reference, this is where
    # it shows up, as a broken wire rather than a silent wrong answer.
    # uid 114 is the donor's GObject node (Position/UID/ClassName/Owner); 115 reads the owner's ClassName.
    first_pn = donor_pns[0] if donor_pns else None
    for uid in donor_pns:                      # prefer the node that actually carries `Owner`, i.e. the GObject one
        if uid == 114:
            first_pn = uid
    print(f"feeding from property node uid {first_pn}", flush=True)
    step("2 wire the existing node's `reference out` -> the new node's `reference`",
         "Wire +1, and ExecState stays 1 IF a SubVI-class node accepts a GObject reference",
         lambda: (g.wire(OP, "Property", pidx(first_pn), "reference out",
                         "Property", pidx(pn_uid), "reference"), snap("after"))[1])

    es_after_wire = g.exec_state(OP)
    if es_after_wire != 1:
        dump_names("BROKEN after wiring - a cast to SubVI is probably required")
        print("\nSTOP: the SubVI-class property node did not accept the GObject reference.", flush=True)
        print("Fallback: copy OpSetIndexMode_v0's `To More Specific Class` chain. NOTHING SAVED.", flush=True)
        return 4

    before_tun = g.count(OP, "LoopTunnel")
    step("3 exit_loop: auto-indexed OUTPUT tunnels for VI Name and VI Path",
         f"LoopTunnel {before_tun}->{before_tun + 2}",
         lambda: (g.exit_loop(OP, pidx(pn_uid), [T_VINAME, T_VIPATH], body, node_class="Property"),
                  snap("after"))[1])

    if any(k == "exc" for _, k in STEPS):
        dump_names("a step missed its prediction - names are the usual cause")

    n_tun = g.count(OP, "LoopTunnel")
    label_map = {}
    meanings = ["VI Name", "VI Path"]
    print(f"\n== 4. adding array indicators to the {n_tun - before_tun} new tunnel(s)", flush=True)
    for k, tun in enumerate(range(before_tun, n_tun)):
        before_labels = set(inds())
        try:
            g.set_index_mode(OP, tun, 1)
        except Exception as e:
            print(f"   tunnel {tun}: set_index_mode {str(e)[:120]}", flush=True)
        try:
            g.tunnel_indicator(OP, tun)
        except Exception as e:
            print(f"   tunnel {tun}: tunnel_indicator FAILED {str(e)[:180]}", flush=True)
            continue
        new_labels = [l for l in inds() if l not in before_labels]
        meaning = meanings[k] if k < len(meanings) else f"tunnel {tun}"
        print(f"   tunnel {tun} -> {new_labels}  ({meaning})", flush=True)
        for l in new_labels:
            label_map[l] = meaning

    es = g.exec_state(OP)
    print("\n" + snap("assembled:"), flush=True)
    print("steps:", STEPS, flush=True)
    print("label map:", json.dumps(label_map, indent=2), flush=True)
    if es != 1:
        dump_names("BROKEN at the end")
        print("\nVERDICT: BROKEN - NOT SAVING. OpReportAll_v0 is untouched.", flush=True)
        return 5

    step("5 COM save", "written to disk", lambda: g.save(OP))
    try:
        with open(MAP_OUT, "w", encoding="utf-8") as f:
            json.dump(label_map, f, indent=2)
        print("label map written:", MAP_OUT, flush=True)
    except OSError as e:
        print("could not write the label map:", e, flush=True)

    print("\nVERDICT: OpReportSubVI_v0 assembled and saved - STRUCTURAL, not yet called.", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
