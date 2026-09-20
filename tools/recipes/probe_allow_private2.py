"""probe_allow_private2.py - fix the probe first, then answer the private-member question.

RUN 1 WAS INVALID AND ITS CONTROL SAID SO. All three candidates reported "node not found by net_map" - including
`Terminal.Create Indicator` (6349C02), a method known to attach and used successfully in several built ops. So
the finding was about my READER, not about private methods, and the Branch-B verdict it printed is void.

That control is the only reason this is not now recorded as "private members are unreachable by script". The same
mistake shape has already cost this project twice today: a failure's appearance taken for its cause (an op wired
to itself looked like "LabVIEW rejects GObject references"; the wrong Index Array deleted while every step still
reported `ok`).

SO THIS RUN LOCATES THE NODE THREE INDEPENDENT WAYS before asking anything about privacy:

  1. `report_all(S, "Invoke")`  - does the object exist at all, and on which owner?
  2. `net_map` over EVERY diagram, not just index 0 - `net_map(S, 0)` assumes diagram 0 is the top level, which
     is an assumption, not a fact (the main VI's diagram 0 holds exactly one node, so the indexing clearly does
     not mean what it looks like).
  3. the uid returned by `build_invoke` itself, compared against both.

Only once a node is reliably found does the privacy question get asked, and the PUBLIC control must pass first -
if it does not, the run prints INVALID and concludes nothing.

SAFETY: scratch VI, created and deleted in the same run.
  py tools/bgrun.py --max-min 12 --log tools/bench/probe_allow_private2.log -- py -u tools/recipes/probe_allow_private2.py
"""
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
S = os.path.join(g.CLAUDEDEV, "SCRATCH_allow_private2.vi")
GENERIC = {"reference", "reference out", "error in (no error)", "error out", "error in"}
g._run.__defaults__ = (6.0, 120.0)


def find_everywhere(uid, n_diagrams=6):
    """(diagram_index, terminals) for `uid`, searching every diagram rather than assuming index 0."""
    for d in range(n_diagrams):
        try:
            nodes, _w = g.net_map(S, d, max_nodes=80, max_terms=24)
        except Exception:
            continue
        for _i, (u, _lbl, terms) in nodes.items():
            if u == uid:
                return d, [t for _ti, t, _w2 in terms if t]
    return None, None


def probe(cls, mid, label):
    print(f"\n== {label}\n   class={cls} id={mid}", flush=True)
    before = set(g.uids(S, "Invoke"))
    try:
        new = g.build_invoke(S, cls, mid, (600, 900))
    except Exception as e:
        print(f"   build_invoke EXC {str(e)[:200]}", flush=True)
        return (label, "exception", "")
    after = g.report_all(S, "Invoke")
    fresh = [o for o in after if o["uid"] not in before]
    print(f"   build_invoke returned: {[(o['uid'], o['pos']) for o in (new or [])]}", flush=True)
    print(f"   report_all sees {len(after)} Invoke object(s); new: "
          f"{[(o['uid'], o['pos'], o['owner']) for o in fresh]}", flush=True)
    if not fresh:
        return (label, "NO OBJECT CREATED", "")
    uid = fresh[-1]["uid"]
    d, terms = find_everywhere(uid)
    if terms is None:
        print(f"   uid {uid} exists per report_all but net_map found it on NO diagram (0..5)", flush=True)
        return (label, "object exists, reader cannot see it", "")
    extra = [t for t in terms if t not in GENERIC]
    print(f"   found on diagram {d}; terminals = {terms}", flush=True)
    verdict = "ATTACHED" if extra else "NOT ATTACHED"
    print(f"   -> {verdict}; method-specific: {extra}", flush=True)
    return (label, verdict, ", ".join(extra))


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
    try:
        dl = g.report_all(S, "Diagram")
        print(f"diagrams: {[(i, d['owner']) for i, d in enumerate(dl)]}", flush=True)
    except Exception as e:
        print(f"diagram list EXC {str(e)[:120]}", flush=True)

    # The CONTROL runs FIRST. If a known-good public method does not attach, everything after it is noise.
    control = probe("VI Server:Terminal", "6349C02", "CONTROL - Terminal.Create Indicator (known good)")
    if not control[1].startswith("ATTACHED"):
        print("\n################ INVALID ################", flush=True)
        print("The control did not attach, so the reader is still wrong and NOTHING about private", flush=True)
        print("members can be concluded from this run. Fix the reader before asking again.", flush=True)
        cleanup()
        return 2

    rows = [control]
    rows.append(probe("VI Server:Invoke", "6370003", "Invoke.Set Method (Allow Private)"))
    rows.append(probe("VI Server:Property", "636F406", "Property.Set Properties[] (Allow Private)"))

    print("\n################ SUMMARY ################", flush=True)
    for label, verdict, extra in rows:
        print(f"  {label:48} {verdict:34} {extra}", flush=True)
    priv_ok = any(v.startswith("ATTACHED") for _l, v, _e in rows[1:])
    print("\nVERDICT:", "BRANCH A - an Allow-Private setter attaches; a private-capable creator can be built."
          if priv_ok else
          "BRANCH B - the Allow-Private setters do not attach either, so the route is circular and the only\n"
          "  remaining scripted option is a donor node copied with `Create from Reference`. Creating that donor\n"
          "  needs one gated GUI action - NOT to be taken unattended.", flush=True)
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
