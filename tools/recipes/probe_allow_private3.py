"""probe_allow_private3.py - the creator SPRAYS ~67 nodes on a private ID. Is one of them correct?

WHAT RUN 2 ACTUALLY SHOWED (its control passed, so the reader is trustworthy this time):

    control  Terminal.Create Indicator 6349C02  ->   1 Invoke object,  terminals include 'Create Indicator'
    private  Invoke.Set Method (Allow Private)  ->  68 Invoke objects
    private  Property.Set Properties[] 636F406  -> 135 Invoke objects   (another ~67)

So a private ID does not produce "no node". It produces about **67 nodes from one call**. That is the same
signature recorded for `Control.Value` on 2026-09-12 ("Node count 8 -> 224") and it was mis-summarised then, as
it was again in run 2: my verdict line printed "does not attach" when the observation was only "my reader could
not find the ONE uid I expected among the flood".

THOSE ARE DIFFERENT CLAIMS AND THE DIFFERENCE DECIDES THE PROJECT'S DIRECTION:
  * if none of the ~67 carries method-specific terminals -> the private route really is closed by script;
  * if ONE of them does -> the method attaches fine and the creator is merely messy, so the fix is to find the
    right node and delete the rest - no GUI, no donor, no circularity.

This run therefore inspects EVERY node the call created, instead of the single uid `build_invoke` happened to
return. `max_nodes` is raised well past the flood; run 2 used 80, which is itself below the object count and
would have hidden a correct node even if one existed.

The control runs first again and the run aborts as INVALID if it fails.

SAFETY: scratch VI, created and deleted in the same run.
  py tools/bgrun.py --max-min 15 --log tools/bench/probe_allow_private3.log -- py -u tools/recipes/probe_allow_private3.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_allow_private3.vi")
GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
g._run.__defaults__ = (6.0, 240.0)


def all_terminals(max_nodes=400):
    """{uid: [terminal names]} across every diagram, sized past the flood."""
    out = {}
    for d in range(4):
        try:
            nodes, _w = g.net_map(S, d, max_nodes=max_nodes, max_terms=24)
        except Exception:
            continue
        for _i, (u, _lbl, terms) in nodes.items():
            out[u] = [t for _ti, t, _w2 in terms if t]
    return out


def probe(cls, mid, label):
    print(f"\n== {label}\n   class={cls} id={mid}", flush=True)
    before = {o["uid"] for o in g.report_all(S, "Invoke")}
    try:
        g.build_invoke(S, cls, mid, (600, 900))
    except Exception as e:
        print(f"   build_invoke EXC {str(e)[:200]}", flush=True)
        return (label, "exception", "")
    after = g.report_all(S, "Invoke")
    fresh = [o["uid"] for o in after if o["uid"] not in before]
    print(f"   objects created by ONE call: {len(fresh)}", flush=True)

    terms_by_uid = all_terminals()
    seen, attached = 0, []
    for uid in fresh:
        terms = terms_by_uid.get(uid)
        if terms is None:
            continue
        seen += 1
        extra = [t for t in terms if t not in GENERIC]
        if extra:
            attached.append((uid, extra))
    print(f"   of those, {seen} were readable; {len(attached)} carry method-specific terminals", flush=True)
    for uid, extra in attached[:5]:
        print(f"      uid={uid} -> {extra}", flush=True)
    if attached:
        return (label, f"ATTACHED on {len(attached)}/{len(fresh)}", str(attached[0][1]))
    if seen == 0:
        return (label, f"UNREADABLE ({len(fresh)} objects, none visible)", "")
    return (label, f"NOT ATTACHED ({seen} read, 0 attached)", "")


def main():
    g._lv = None
    try:
        g.close_panel(S)
        time.sleep(0.3)
    except Exception:
        pass
    if os.path.exists(S):
        try:
            os.remove(S)
        except OSError:
            pass
    shutil.copyfile(SRC, S)
    g.open_panel(S)
    time.sleep(0.9)
    print(f"scratch ready, ExecState {g.exec_state(S)}", flush=True)

    control = probe("VI Server:Terminal", "6349C02", "CONTROL - Terminal.Create Indicator (known good)")
    if not control[1].startswith("ATTACHED"):
        print("\n################ INVALID - control failed, concluding nothing ################", flush=True)
        cleanup()
        return 2

    rows = [control,
            probe("VI Server:Invoke", "6370003", "Invoke.Set Method (Allow Private)"),
            probe("VI Server:Property", "636F406", "Property.Set Properties[] (Allow Private)")]

    print("\n################ SUMMARY ################", flush=True)
    for label, verdict, extra in rows:
        print(f"  {label:48} {verdict:34} {extra}", flush=True)

    priv = rows[1:]
    if any(v.startswith("ATTACHED") for _l, v, _e in priv):
        print("\nVERDICT: BRANCH A - the method DOES attach; the creator merely also sprays junk nodes.",
              flush=True)
        print("  Fix = keep the node that carries the method terminals, delete the rest. No GUI needed.",
              flush=True)
    elif all(v.startswith("NOT ATTACHED") for _l, v, _e in priv):
        print("\nVERDICT: BRANCH B - readable nodes exist and NONE carries the method. The scripted route is",
              flush=True)
        print("  closed; the remaining option is a donor copied with `Create from Reference`, which needs one",
              flush=True)
        print("  gated GUI action. NOT to be taken unattended.", flush=True)
    else:
        print("\nVERDICT: STILL INCONCLUSIVE - the nodes exist but cannot be read. That is a READER problem,",
              flush=True)
        print("  not a statement about private members, and must not be recorded as one.", flush=True)
    cleanup()
    return 0


def cleanup():
    try:
        g.close_panel(S)
        time.sleep(0.3)
        os.remove(S)
        print("\nscratch deleted", flush=True)
    except Exception as e:
        print("\ncleanup:", str(e)[:100], flush=True)


if __name__ == "__main__":
    sys.exit(main())
