r"""stage_d1_ring_p3b1_scratch - card 129-2: SCRATCH RUN of RING P3b-1 BEFORE the one launch (brief_129-2.md step 3, D-2026-10-01-01, PD264(c)(e)).
Runs the stage recipe's OWN body (tools/recipes/stage_d1_ring_p3b1.py, imported UNCHANGED) on a dated byte copy
claudeDev\scratch_c129_ring_p3b1_<ts>.vi of the P3a bed (md5 4dfa44aa) - same Executor, LVBackend and every recipe gate
(L0 L1 E1 FS RB D CEN2 TD FU PB HB PS EL). No VI is run; the bed is never opened for edit.
MODE (argv[1]):
  nosave : SAVE off - structural verification only, NO GUI; the work copy is dropped by the Stage hygiene.
  pin    : SAVE on (rule-6 gui_save of the SCRATCH) so stage_d1_ring_p3b1_el.py scratch can pin its Error List (that script deletes it).
Observation only (wrapper-side, the recipe is not touched): Executor.run's real terminal rows are kept and, at CEN2, every NEW object
uid is printed with its class and (for terminals) its owner uid/class and frame (NEWOBJ lines); the FULL-class census before/after is
printed (CENSUS-ALL lines) - the pred's census is EMPTY (all 31 rows CENSUS-UNPREDICTED), so CEN2 is vacuous here and these lines are
the measurement PD264(c) writes into plan_ring_p3b1_pred.json.
PRIOR ART: tools/bench/stage_d1_ring_p3a_scratch.py (card 124-7/124-8; this is its cut - recipe module, plan, stage name, record key).
FS/FU are the recipe's own gates (R.body, PD269(c) per-frame counts vs the plan's simulated end state) - no copy here to drift.
PREDICTION: L1 31 actions; E1 every checkpoint == sim; FS 1 FlatSequence with 3 frames on 27219, per-frame terminals == sim end state
(f0 0 / f1 16 / f2 18); FU base + 2 filled frames; RB reads `status`; D == sim; TD; PB cdiff 16; peak memory <= 663.4 MB (pred memory_pred);
HB <= +700; PS saved (scratch only); CEN2 vacuous PASS; LabVIEW gone; PASS writes tools/bench/scratch_verify/stagexec.ring_p3b1_fs_<mode>_<ts>.json.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/stage_d1_ring_p3b1_scratch_pin3.log -- py -u tools/bench/stage_d1_ring_p3b1_scratch.py pin"""
import json, os, sys, time                                                          # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "recipes"))
import stagekit as K, stagexec as SX                                                # noqa: E401,E402
import stage_d1_ring_p3b1 as R                                                      # noqa: E402
REC = os.path.join(K.BENCH, "scratch_verify")
PLAN = os.path.join(K.BENCH, "plan_ring_p3b1.json")                                 # the recipe's plan (stage_prerun.plan_files reads it)
MODE = "pin" if "pin" in sys.argv[1:] else "nosave"                                # stage_prerun passes its own flags in argv
CARD, LOGTAG = "130-6", {"pin": "pin3"}.get(MODE, MODE)                             # card 129-4: _pin2.log; 129-8/130-6: the 31-action cut -> _pin3.log
R.SAVE = MODE == "pin"
OBS = {"rows": None, "snaps": []}
_run, _snap, _cg = SX.Executor.run, K.Stage.census_snapshot, K.Stage.census_gate


def run_keep(self, *a, **k):
    r = _run(self, *a, **k); OBS["rows"] = r; return r                             # noqa: E702


def snap_keep(self, target=None):
    d = _snap(self, target); OBS["snaps"].append(dict(d)); return d                 # noqa: E702


def cg_print(self, label, before, after, declared):
    got = _cg(self, label, before, after, declared)
    if isinstance(before, dict) and isinstance(after, dict) and len(OBS["snaps"]) >= 2:
        b, a = OBS["snaps"][0], OBS["snaps"][-1]
        cnt = lambda d: dict((c, sum(1 for v in d.values() if v == c)) for c in set(d.values()))   # noqa: E731
        cb, ca = cnt(b), cnt(a)
        delta = dict((c, ca.get(c, 0) - cb.get(c, 0)) for c in sorted(set(cb) | set(ca)) if ca.get(c, 0) != cb.get(c, 0))
        newall = dict((u, a[u]) for u in set(a) - set(b))
        nb = {}
        for c in newall.values():
            nb[c] = nb.get(c, 0) + 1
        print("  CENSUS-ALL net delta (every class) {0}".format(json.dumps(delta, sort_keys=True)), flush=True)
        print("  CENSUS-ALL new uids by class (every class) {0}".format(json.dumps(nb, sort_keys=True)), flush=True)
        print("  CENSUS-ALL lost uids {0}".format(len(set(b) - set(a))), flush=True)
        self.R["census_all"] = {"net_delta": delta, "new_by_class": nb, "lost": len(set(b) - set(a))}
        by = dict((int(r["term_uid"]), r) for r in (OBS["rows"] or []) if r.get("term_uid"))
        for u in sorted(newall):
            r = by.get(u)
            print("  NEWOBJ uid {0} class {1} | {2}".format(u, newall[u], "owner #{0} {1} frame {2} term {3!r} src {4} wire {5}".format(
                r["owner_uid"], r["owner_class"], r.get("frame_diagram"), r.get("term_name"), r.get("is_source"), r.get("wire_uid"))
                if r else "not a terminal row"), flush=True)
    return got


SX.Executor.run, K.Stage.census_snapshot, K.Stage.census_gate = run_keep, snap_keep, cg_print


def body(s):
    print(__doc__, flush=True)
    print("MODE {0} (SAVE {1})".format(MODE, R.SAVE), flush=True)
    return R.body(s)


if __name__ == "__main__":
    st = K.Stage(R.BASE["vi"], R.BASE["md5"], "scratch_c129_ring_p3b1", preload=False, deadline_min=40,
                 out_json=os.path.join(K.BENCH, "stage_d1_ring_p3b1_scratch_{0}.json".format(MODE)), task="card " + CARD + " scratch " + MODE)
    rc = K.run(body, st)
    gone = R.DRY or SX.kill_labview_at_exit()
    if rc == 0 and gone and not R.DRY:
        os.makedirs(REC, exist_ok=True)
        json.dump({"status": "PASS", "t": time.time(), "card": CARD, "mode": MODE, "function": "stagexec.ring_p3b1_fs",
                   "op": "stagexec create FS/frames/Local/RAS/IndexArray/SubVI/vilib_donor Unbundler+Select + connect + connect_term_uid + "
                         "wire_remove_loose_ends -> the RING P3b-1 recipe",
                   "fixture": "scratch byte copy of " + R.BASE["vi"] + (" (saved for the Error List read, then deleted)" if R.SAVE else " (not saved)"),
                   "plan": {"path": os.path.relpath(PLAN, K.ROOT), "md5": K.md5(PLAN)},
                   "recipe": {"path": "tools/recipes/stage_d1_ring_p3b1.py", "md5": K.md5(R.__file__)},
                   "facts": st.R.get("ring_p3b1"), "census_all": st.R.get("census_all"),
                   "log": "tools/bench/stage_d1_ring_p3b1_scratch_{0}.log".format(LOGTAG)},
                  open(os.path.join(REC, "stagexec.ring_p3b1_fs_{0}_{1}.json".format(MODE, st.stamp)), "w", encoding="utf-8"), indent=1, default=str)
    sys.exit(rc if gone else 1)
