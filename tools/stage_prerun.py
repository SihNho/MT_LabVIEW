r"""stage_prerun - DRY RUN + OFFLINE PRE-RUN of a stage script, and the LAUNCH GATE that requires both
(CLAUDE.md §3 "Stages are SIMULATED and PRE-RUN OFFLINE", decisions 1, 2, 3, 4, 8; docs/stage-simulator-plan.md
"Enforcement"; card tools/bench/cards/task_chat-C1.json).

    py tools/stage_prerun.py --dry    <recipe.py> [--graph <graph json>] [--no-record] [--json-out f]
    py tools/stage_prerun.py --prerun <recipe.py> [--graph <graph json>] [--no-record] [--json-out f]
    py tools/stage_prerun.py --check-launch "<command line>"          (what guard_bash asks; exit 0 allow / 2 refuse)

WHAT EXISTED FIRST (checked before writing): tools/bench/dryrun_l7_1b_address.py and dryrun_l7_r_address.py stub
three gscript readers by hand for ONE recipe's `address` calls - this generalises that shape; tools/protocol.py
(run_verdict / segments / result_line - used, not re-written); tools/stop_record.py (the per-path/sha launch refusal
this gate sits next to); tools/jev_candidates.py (RULE-CHAIN-S1 lives there). No dry-run engine, no pre-run and no
records file existed.

DRY RUN (decision 1). The recipe is executed as `__main__` with the COM layer REPLACED, not wrapped: a fake
`gscript` module (constants read from gscript.py's own top-level assignments, never imported), fake
`pythoncom`/`win32com`, and subprocess/os.system blocked - so nothing in the process CAN reach LabVIEW. The
readers that address terminals (report_all, uids, count, node_labels, node_terms_uid, allterms.read_terms,
wiki_build.read_live) answer from the input VI's GRAPH JSON (the `graph_*.json` whose `md5` == the Stage's input
md5, the shape tools/bench/graph_s3_loop15_20260924.json has); every other fleet call returns a permissive Fake and
is logged. Writes outside %TEMP% are redirected into %TEMP%\stage_dry (the recipe's own JSON/decision files are
never overwritten). Verdict rules (they are the contract - see OPEN in the result for the judgement ones):
  * before the first MUTATING call the graph is exact: a failing gate that read no Fake is a real FAIL;
  * after it (no op-effect models yet: build order step 3/4) a gate is UNVERIFIED, never FAIL;
  * an exception is FAIL when it is a code defect (NameError, UnboundLocalError, ImportError, SyntaxError) or when
    it happens before any mutation with no Fake read; otherwise it is STUB-LIMIT (the path could not continue on
    stub data) - the dry run then did NOT run the whole path and is not a PASS.
  * PASS = the recipe body ran to its end, no FAIL. Line coverage of the recipe file is reported.

PRE-RUN (decision 2, 3, 8), all offline, on the same graph JSON + the dry run's trace:
  X1 the dry run PASSes                      X2 a PLAN file exists (a .json the recipe names whose `decisions` rows
  X3 every plan row is decided               carry id+action) - rows come only from it (decision 8)
  X4 every row end / every address() end is addressable offline: node in the graph; the terminal by name +
     direction on the owner's terminal list (unwired: owner node -> terminal list -> uid echo), a structure by its
     border tunnels; a verify_term_uid must name a WIRED terminal of that owner; a term_uid must agree with the name
  X5 wiring ops executed in the dry run == plan wire rows; (card 115-3) delete_object/delete_wire ops are NOT wiring
     ops - they are counted 1:1 per kind against the plan's delete rows (x5_count; selftest_stage_prerun_c115c.py)
  (card 79-6, PD178(g)) a named stageplan/1 counts as the plan ONLY via stageplan_check - final true, finalized.failed
     None, open_rows_match, undecided 0, stagexec.load_final_plan (base + step-file md5s) and compile_plan all pass;
     X3 counts its actions (each compiled exactly once); X5 expects its compiled WIRING real ops (tunnel/connect/
     wire_sr/branch), which must cover every `wire` action; its md5 joins plan_md5s. Decisions-row path unchanged.
     Self-test: tools/bench/selftest_stage_prerun_stageplan.py
  X6 ast lint: no int literal that is a node uid of the input graph, no string literal that is a terminal name of
     such a node (decision 8: a recipe never re-types a uid or a terminal name)
  X7 no Jev row on a RULE-CHAIN-S1 chain terminal (decision 3)
  X8 control_path_lint (CLAUDE.md 1c'', card chat-F1): a stageplan/1 that creates a queue/notifier primitive without
     `data_stream: true` + a non-empty `why` is refused; so is a shift register fed by a local/tunnel whose previous
     value goes only to a compare/logic node that also gets the current value (an edge detector) unless the source is
     a DECLARED non-boolean (`type`) compared by a comparison (a counter reader). Also on --prerun of a plan.
     `--control-lint <plan>` (exit 0/2) · `--selftest-control-lint` (log tools/bench/selftest_control_path_lint.log)
  X9 (card 106-3, retrospective-cycle102 wrong-ordering) every op/row the run dispatches whose verb holds a precondition
     on the stage's work file (stagexec.ROUTE_PRECONDITIONS - copy_in: work == gscript.MOVE_DST) holds for the Stage
     the dry run built (r7 stopped IN op 41 on it: stage_d1_disp_r7.log:807). Card 110-7 (judgement F1): a decisions-row
     `copy` is checked ONLY when the recipe's AST calls run_rows / from_decision (the only dispatchers of a row's `copy`
     to copy_in); a recipe that calls neither (stage_replay_swap: shutil byte copy) dispatches no row. Self-test:
     tools/bench/selftest_stage_prerun_c110g.py
  X10 (card 106-3, retrospective-cycle103 inference-over-measurement) the predicted LabVIEW private-MB peak over the
     dispatched ops, from the RECORDED per-op meter of an earlier run of the same recipe (stagexec.mem_predict), is
     below X10_FAIL_MB 690 (card 106-5, PD219(c): error 2 was seen at 695 MB; MEMSTOP stagexec.MEM_STOP_MB 700 stays
     the run-time guard); no covering record = UNMEASURED: `X10 WARN unmeasured` in the output and the RESULT line, pass.
     REPLACED by card 130-1 (PD267(b)): X10 predicts every stagexec.Executor the dry run builds from its COMPILED plan +
     checkpoint set, peak = start + R*read + N*(edit+other) (tools/bench/memory_model.json, each value cited); FAIL above
     its fail_above_mb (675); FAIL UNMEASURED when nothing compiles and no recorded meter covers the run (x10_gate).
     card 132-1 (PD275(a)(b)): + final_read_mb (17.4, the run's last whole-VI read) and fail_above_mb 690.
     card chat-S3 (PD328(a), user 2026-10-03): fail_above_mb 680 and MEMSTOP 695 (error 2 measured at 704.8 MB); both live
     ONLY in memory_model.json (X10_FAIL_MB and stagexec.MEM_STOP_MB read it). The 690/675 numbers in older comments below
     are history.
    card 132-4 (PD277(a), fp-29): a 0-edit script with no Executor (x10_readonly) is modelled N 0, R 1 + its whole-VI
    read call sites, + final_read_mb; an edit-op script without an Executor stays UNMEASURED = FAIL.
    card 136-2 (fp-33): ... unless its dry trace carries the ops and the opened VI's load is measured (x10_edit): N = dry
    Stage._op ops, R = 1 + executed whole-VI reads, start = load_by_vi[input md5] + op-0. Self-test selftest_x10_c136_2.py
    card 138-2 (PD299(b)): whole-VI reads are counted from the SOURCE (x10_source_reads: call sites x calls of the enclosing
    function; a read in a loop / unbounded = UNMEASURED FAIL). Edit + read-only: R = 1 + max(source, dry); Executor runs:
    R = plan checkpoints + the script's source reads (exec_peak_mb keeps the Executor-only figure). Self-test
    selftest_x10_c138_2.py
     Self-test: tools/bench/selftest_x10_c130_1.py
     card 130-5 (PD268(b)): `--dry` FAILs (EXECUTOR-STOP / EXECUTOR-NOT-RUN, executor_stops) when a stagexec.Executor
     the recipe built ran fewer ops than its window (from_step+1 .. stop_after|last). Self-test:
     tools/bench/selftest_dry_c130_5.py
     Without --graph the dry uses the recipe's plan base graph (find_graph / plan_base_graphs, card 106-5).
     Self-test of X9/X10: tools/bench/selftest_stage_prerun_c106c.py
  X11 (card 114-1 S0, PD227(j)) no stageplan `wire` row into one INPUT of a Build Array while a sibling input of that node
     is an open row at the stage end (the #2626 / #11261 input-rename class), unless a pb-licence/1 file naming the plan
     covers the node. Replay: `--buildarray-check <plan.json> ...`. Self-test: tools/bench/selftest_stage_prerun_c114.py
  X12 (card 114-3 C4) no row names a wire uid an earlier border-crossing connect re-created.
  X13 (card 115-1 A1, PD229(a)) OPMODEL CONFORMANCE: the recorded samples of every model file of the ops a stageplan uses
     replay through stagesim with the in-force params and reproduce the measured wire outcome (source/sink wire fate,
     wire groups, old source wire members); a FAIL names the sample and the field. No model file / no replayer = WARN.
     `--opmodel-conformance [op ...] [--disable cfw_border_rule]` (exit 0/2). Self-test: selftest_stage_prerun_c115a.py
  X16 (card 125-1, PD251(b)) every entry of a create action's declared `terminals` list carries a `term_class` (no
     stagesim default). `prim: "const_donor"` creates are exempt (card 125-3, PD252(a): measured class == default
     `Terminal`, stagesim.py:1317). Both --prerun paths (recipe and stageplan/1). Self-test: selftest_c125_1.py
Records: tools/bench/prerun_records.jsonl, one line per dry/prerun, keyed by the script's sha256 + the plan files'
md5s. Launch gate (decisions 1/2/4): a `tools/recipes/stage_*.py` launch needs a dry PASS and a prerun PASS for the
script's CURRENT sha256 and plan md5s, both newer than the newest failing run of that script (a failed run
invalidates them). Reads, dry/prerun and diagnostics are never refused; the decision is argv-only.
Prediction contract: --dry on a stage recipe prints a RESULT line and exits 0 on PASS, 1 otherwise; --check-launch
exits 0 or 2 and prints the reason.
"""
import argparse
import ast
import builtins
import collections
import copy
import glob
import hashlib
import io
import json
import os
import re
import shlex
import shutil
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import gateclass as _gateclass                                                     # noqa: E402  card chat-S2: STOP vs LOG-only
BENCH = os.path.join(HERE, "bench")
RECORDS = os.environ.get("PRERUN_RECORDS") or os.path.join(BENCH, "prerun_records.jsonl")
LOG_DIR = os.environ.get("PRERUN_LOG_DIR") or BENCH
TEMP = os.environ.get("TEMP") or os.environ.get("TMP") or "."
SINK = os.path.join(TEMP, "stage_dry")
REAL_OPEN = builtins.open
STAGE_RE = re.compile(r"(?:^|[\\/])tools[\\/]recipes[\\/]stage_[^\\/]*\.py$", re.I)
MUT_RE = re.compile(r"connect|delete|^del_|move|wire|create|^add|remove|^set_|save|close|^open|copy|purge|drop|place|"
                    r"^new_|^make|^build|replace|insert|relink|^run$|^_run|invoke|junk|retire", re.I)
WIRE_VERB_RE = re.compile(r"connect|wire|fs_inner", re.I)
STRUCTS = ("WhileLoop", "ForLoop", "CaseStructure", "EventStructure", "FlatSequence", "StackedSequence",
           "TimedLoop", "DisableStructure")
TUNNELS = ("LoopTunnel", "Tunnel", "SelectorTunnel", "LeftShiftRegister", "RightShiftRegister")
CODE_DEFECTS = (NameError, UnboundLocalError, ImportError, SyntaxError)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def md5(path):
    h = hashlib.md5()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def rel(p):
    try:
        return os.path.relpath(os.path.abspath(p), ROOT).replace("\\", "/")
    except ValueError:
        return os.path.abspath(p).replace("\\", "/")


# ---------------------------------------------------------------------------------------------- graph JSON
# Card 95-1: tools/bench holds SEVERAL graph_*.json shapes that carry the same top-level `md5` - the terminal list
# ({terminals, objs}: graph_s3_loop15/graph_k_s4/graph_replay_pane_base/sim graph_k_80_owners) and three that are
# NOT readable by OfflineGraph: the edge graph ({cls, edges, flags, method}: graph_s1_*/graph_bed_*), the loop
# census ({loops, by|errors}: graph_loops_*) and the object census ({objects, n}: graph_objs_*). find_graph used to
# pick the NEWEST header match whatever its shape, so graph_s1_20260924.json (edge graph) and
# graph_loops_k_s4_20260925.json (loop census, 2 s newer than graph_k_s4) crashed the dry run with KeyError
# 'terminals' (prerun_records.jsonl:17,24,33,65). Only the terminal-list shape is ever returned or loaded now.
GRAPH_TERM_KEYS = ("owner_uid", "term_uid", "term_name", "is_source", "wire_uid")
GRAPH_OBJ_KEYS = ("uid", "class")


class GraphShapeError(ValueError):
    """A graph JSON that is not the terminal-list shape OfflineGraph reads."""


def graph_shape_error(d):
    """None when `d` is the terminal-list graph ({md5, terminals:[...], objs:[...]} with the row fields the readers
    use), else a one-line reason naming what is there."""
    if not isinstance(d, dict):
        return "top level is a {0}, not an object".format(type(d).__name__)
    miss = [k for k in ("terminals", "objs") if k not in d]
    if miss:
        return "no {0} key(s) - keys present {1} (not the terminal-list graph shape)".format(
            "/".join(miss), sorted(d))
    for k, need in (("terminals", GRAPH_TERM_KEYS), ("objs", GRAPH_OBJ_KEYS)):
        rows = d[k]
        if not isinstance(rows, list) or not rows:
            return "{0} is {1}, not a non-empty list".format(k, type(rows).__name__ if not isinstance(rows, list)
                                                              else "an empty list")
        for i, r in enumerate(rows):
            if not isinstance(r, dict) or any(f not in r for f in need):
                return "{0}[{1}] lacks {2}".format(k, i, [f for f in need if not isinstance(r, dict) or f not in r])
    return None


FIND_SKIPPED = []                       # (path, reason) of md5-matching graph files find_graph refused, last call


def plan_base_graphs(recipe):
    """card 106-5 (PD219(c)): [(path, md5 pin or None)] of the base graph every plan the recipe names records
    (`base.path` / `finalized.base.path`; plan_disp.json -> tools/bench/par1359_95_graph.json). [] when unreadable."""
    out = []
    try:
        plans = plan_files(recipe)[0]
    except Exception:                                                              # noqa: BLE001
        return out
    for p in plans:
        try:
            d = json.load(REAL_OPEN(p, encoding="utf-8"))
        except Exception:                                                          # noqa: BLE001
            continue
        for b in (d.get("base"), (d.get("finalized") or {}).get("base")):
            if isinstance(b, dict) and isinstance(b.get("path"), str) and b["path"]:
                ap = b["path"] if os.path.isabs(b["path"]) else os.path.join(ROOT, b["path"])
                item = (os.path.normpath(ap), b.get("md5"))
                if item not in out:
                    out.append(item)
    return out


def find_graph(input_md5, plan_graphs=()):
    """The terminal-list graph (graph_shape_error None; card 95-1) whose top-level `md5` is `input_md5`:
    FIRST the plan's own base graph (`plan_graphs` = plan_base_graphs(recipe); card 106-5, PD219(c): the plan was finalized
    against it, so it wins when its header md5 is the input's AND its file md5 equals the plan's pin - the recipe's
    base graph par1359_95_graph.json is not named graph_*, and three X1 failures were the missing `--graph`, review
    archive/peer/2026-09-27-c106c-selftest-x1.md s1); ELSE the newest tools/bench/graph_*.json OR
    tools/bench/sim/<stage>/graph_*.json. The sim/ subtree was
    added by the cycle-87 firefighter (PD194(c)): the L2-A1 graph lives in sim/l2a1/, so every `--prerun` launched
    without `--graph` failed gate X1 in cycles 85 and 86 (prerun_l2a1_85.log:29, prerun_l2a1_86-5.log:29) and was
    re-launched by hand with `--graph`. Header md5 matches of another shape (or a plan base graph whose bytes moved off
    the plan's pin) are listed in FIND_SKIPPED."""
    hits = []
    del FIND_SKIPPED[:]
    for p, pin in plan_graphs or ():
        if not os.path.isfile(p):
            FIND_SKIPPED.append((rel(p), "plan base graph missing"))
            continue
        with REAL_OPEN(p, encoding="utf-8", errors="replace") as f:
            m = re.search(r'"md5"\s*:\s*"([0-9a-f]{32})"', f.read(800))
        if not m or m.group(1) != input_md5:
            continue                                   # the plan's base is another VI (a PART-B input): not a match
        if pin and md5(p) != pin:
            FIND_SKIPPED.append((rel(p), "plan base graph file md5 {0} != the plan's pin {1}".format(md5(p), pin)))
            continue
        try:
            why = graph_shape_error(json.load(REAL_OPEN(p, encoding="utf-8")))
        except ValueError as e:
            why = "not JSON: {0}".format(e)
        if why:
            FIND_SKIPPED.append((rel(p), why))
            continue
        return p
    for p in glob.glob(os.path.join(BENCH, "graph_*.json")) + glob.glob(os.path.join(BENCH, "sim", "*", "graph_*.json")):
        try:
            with open(p, encoding="utf-8", errors="replace") as f:
                head = f.read(800)
        except OSError:
            continue
        m = re.search(r'"md5"\s*:\s*"([0-9a-f]{32})"', head)
        if m and m.group(1) == input_md5:
            try:
                why = graph_shape_error(json.load(open(p, encoding="utf-8")))
            except ValueError as e:
                why = "not JSON: {0}".format(e)
            if why:
                FIND_SKIPPED.append((rel(p), why))
                continue
            hits.append((os.path.getmtime(p), p))
    return sorted(hits)[-1][1] if hits else None


class OfflineGraph(object):
    """The readers stagekit addresses with, answered from one graph JSON ({vi, md5, terminals, objs}). Any other
    shape raises GraphShapeError naming the file and the keys it has (card 95-1), never a bare KeyError."""

    def __init__(self, path):
        try:
            d = json.load(open(path, encoding="utf-8"))
        except ValueError as e:
            raise GraphShapeError("graph {0}: not JSON: {1}".format(rel(path), e))
        why = graph_shape_error(d)
        if why:
            raise GraphShapeError("graph {0}: {1}".format(rel(path), why))
        self.path, self.md5, self.terms, self.objs = path, d.get("md5"), d["terminals"], d["objs"]
        self.cls = dict((int(o["uid"]), o["class"]) for o in self.objs)
        self.by_owner = collections.OrderedDict()
        for r in self.terms:
            self.by_owner.setdefault(int(r["owner_uid"]), []).append(r)
        top = [o for o in self.objs if o["class"] == "TopLevelDiagram"]
        self.diagrams = [int(o["uid"]) for o in top + [o for o in self.objs if o["class"] == "Diagram"]]
        self.node_diag = {}
        for u, rows in self.by_owner.items():
            c = collections.Counter(int(r.get("frame_diagram") or 0) for r in rows if r.get("term_class") == "Terminal")
            if c:
                self.node_diag[u] = c.most_common(1)[0][0]
        self._G = None

    def G(self):
        if self._G is None:
            import jev_candidates as JC
            self._G = JC.from_parts({"terminals": self.terms, "graph_summary": {}}, self.objs, None, {}, None,
                                    os.path.basename(self.path))
        return self._G

    def report_all(self, _t, cls):
        if cls == "Diagram":
            return [{"i": i, "uid": u, "class": self.cls.get(u), "pos": [0, 0], "owner": ""}
                    for i, u in enumerate(self.diagrams)]
        rows = self.objs if cls == "GObject" else [o for o in self.objs if o["class"] == cls]
        return [dict(o, i=i) for i, o in enumerate(rows)]

    def uids(self, _t, cls):
        return set(int(o["uid"]) for o in self.report_all(_t, cls))

    def count(self, _t, cls):
        return len(self.report_all(_t, cls))

    def nodes_in(self, di):
        """Nodes whose terminals sit on diagram `di`, plus EVERY structure (a structure's own diagram is not in the
        graph JSON; listing it everywhere keeps address()'s membership + echo consistent - stub-only)."""
        d = self.diagrams[di] if 0 <= di < len(self.diagrams) else None
        us = [u for u, dd in self.node_diag.items() if dd == d and self.cls.get(u) not in TUNNELS]
        us += [int(o["uid"]) for o in self.objs if o["class"] in STRUCTS]
        return sorted(set(us))

    def node_labels(self, _t, di, *a, **k):
        return [{"uid": u, "label": ""} for u in self.nodes_in(di)]

    def term_rows(self, uid):
        """(rows, how). A structure's terminal list = the OUTER terminals of its border tunnels (jev_candidates
        heuristic); empty when the heuristic finds none."""
        uid = int(uid)
        if self.cls.get(uid) in STRUCTS:
            import jev_candidates as JC
            nodes, how = JC.structure_terminals(self.G(), uid)
            rows = [r for n in nodes for r in self.by_owner.get(n, []) if r.get("term_class") == "OuterTerminal"]
            return rows, "structure: " + how
        return self.by_owner.get(uid, []), "node"

    def node_terms_uid(self, _t, di, ni):
        us = self.nodes_in(di)
        if not 0 <= ni < len(us):
            return 0, []
        u = us[ni]
        rows, _h = self.term_rows(u)
        return u, [{"i": i, "name": r["term_name"], "is_source": bool(r["is_source"]), "wire": int(r["wire_uid"] or 0),
                    "has_wire": bool(r["wire_uid"]), "node_uid": u, "uid": int(r["term_uid"])} for i, r in enumerate(rows)]

    def read_terms(self, *_a, **_k):
        return [dict(r) for r in self.terms], 0.0

    def read_live(self, _path, fs_pairs=None, fs_uids=None):
        wires = []
        try:
            import allterms as A
            wires = A.join_wires([dict(r) for r in self.terms], [int(o["uid"]) for o in self.objs if o["class"] == "Wire"])
        except Exception:                                                          # noqa: BLE001
            pass
        return {"terminals": [dict(r) for r in self.terms], "objs": [dict(o) for o in self.objs], "wires": wires,
                "fs_tunnel_pairs": fs_pairs or [], "secs": {"gobject": 0.0, "terminals": 0.0, "fs": 0.0, "total": 0.0}}


# ---------------------------------------------------------------------------------------------- the stub layer
class DryState(object):
    def __init__(self):
        self.taint = 0
        self.gate_taint = 0
        self.line_taint = None               # card 134-1: taint at the recipe's last line event (dry()'s tracer)
        self.mutated = None                 # first mutating call name
        self.calls = []                      # (name, mutating)
        self.graph = None
        self.graph_path = None
        self.graph_override = None
        self.graph_error = None              # card 95-1: why no graph could be loaded (shape / not found)
        self.input_md5 = None
        self.input_vi = None
        self.ops = []                        # Stage._op verbs
        self.addresses = []                  # (end dict, is_source, mutated_at_call)
        self.jev = []                        # recorded Jev intents
        self.unverified = []
        self.fails = []
        self.stub_limit = None
        self.reached_end = False
        self.blocked = []                    # subprocess / file ops refused
        self.works = []                      # card 106-3: every Stage's work path (X9 verb preconditions)
        self.recipe = None                   # card 106-5: the recipe under dry run (find_graph reads its plans' base)
        self.executors = []                  # card 130-1 (PD267(b)): every stagexec.Executor the recipe built (X10 model)
        self.x10_probe = False               # card 130-1: stop the recipe at its first Executor (self-test probe)
        self.discards = []                   # card chat-M2 (fp-35): every Stage work path the recipe declared a scratch


D = DryState()


class Fake(object):
    """The permissive stand-in for anything the stub cannot know. Every use is counted (taint)."""

    def __init__(self, name="?"):
        object.__setattr__(self, "_n", name)

    def _t(self):
        D.taint += 1
        return self

    def __getattr__(self, k):
        if k.startswith("__"):
            raise AttributeError(k)
        self._t()
        return Fake(self._n + "." + k)

    def __setattr__(self, k, v):
        self._t()

    def __call__(self, *a, **k):
        self._t()
        return Fake(self._n + "()")

    def __getitem__(self, k):
        self._t()
        return Fake(self._n + "[]")

    def __setitem__(self, k, v):
        self._t()

    def __iter__(self):
        """`a, b = fake` -> exactly as many Fakes as the caller's UNPACK_SEQUENCE asks for (read off the calling
        frame's bytecode, CPython 3.10 word offsets); any other iteration (for, list()) sees an empty sequence."""
        self._t()
        try:
            import dis
            f = sys._getframe(1)
            op, arg = f.f_code.co_code[f.f_lasti], f.f_code.co_code[f.f_lasti + 1]      # f_lasti = byte offset
            if dis.opname[op] == "UNPACK_SEQUENCE":
                return iter([Fake(self._n + "[{0}]".format(i)) for i in range(arg)])
        except Exception:                                                          # noqa: BLE001
            pass
        return iter(())

    def __len__(self):
        self._t()
        return 0

    def __bool__(self):
        self._t()
        return True

    def __int__(self):
        self._t()
        return 0

    __index__ = __int__

    def __float__(self):
        self._t()
        return 0.0

    def __str__(self):
        # card 134-1 (review archive/peer/2026-10-02-c134-1-dry-selftest.md:63,109): turning a stub into TEXT (a fact line,
        # a gate's detail) cannot feed a boolean, so it no longer counts as taint
        return "<dry:{0}>".format(self._n)

    __repr__ = __str__

    def __format__(self, spec):
        return str(self)

    def __eq__(self, o):
        self._t()
        return False

    def __ne__(self, o):
        self._t()
        return True

    def __hash__(self):
        return id(self)

    def __contains__(self, x):
        self._t()
        return False

    def _op(self, *a):
        self._t()
        return Fake(self._n + "#")

    __add__ = __radd__ = __sub__ = __rsub__ = __mul__ = __rmul__ = __truediv__ = __floordiv__ = _op
    __and__ = __or__ = __rand__ = __ror__ = __xor__ = __mod__ = _op
    __lt__ = __le__ = __gt__ = __ge__ = lambda self, o: bool(self._t()) and False

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _stub(name):
    def f(*a, **k):
        mut = bool(MUT_RE.search(name.split(".")[-1]))
        D.calls.append((name, mut))
        if mut and D.mutated is None:
            D.mutated = name
        return Fake(name)
    f.__name__ = name.split(".")[-1]
    f._dry = True
    return f


def provisional_dry_graph(recipe):
    """card 132-1 (gate-fp fp-21, PD275(e)): (path | None, error | None). A recipe whose plan base is PROVISIONAL (base =
    {path, md5, provisional: true, sim_of: {plan, md5}}, the simulated END of the previous stage) is dry-run against THAT
    graph, not the graph of the input VI's md5 (the P3a bed the simulated state inherits): the input VI's graph lacks every
    object stage N created, so the dry's step-0 compare was unbound by construction (stage_prerun_c129_1_p3b2_dry.log:19-20).
    Refused (error) when sim_of.plan changed since the base was simulated, or the base file moved off its pin. The launch
    stays refused for a provisional base (provisional_plans, card chat-P1 item 1); --rebase replaces it."""
    try:
        plans = plan_files(recipe)[0]
    except Exception:                                                              # noqa: BLE001
        return None, None
    for p in plans:
        try:
            b = (json.load(REAL_OPEN(p, encoding="utf-8")) or {}).get("base")
        except Exception:                                                          # noqa: BLE001
            continue
        if not (isinstance(b, dict) and b.get("provisional")):
            continue
        so = b.get("sim_of") or {}
        sp = os.path.join(ROOT, so.get("plan") or "")
        bp = b.get("path") if os.path.isabs(b.get("path") or "") else os.path.join(ROOT, b.get("path") or "")
        if not so.get("plan") or not os.path.isfile(sp) or md5(sp) != so.get("md5"):
            return None, "provisional base of {0}: sim_of.plan {1} changed or missing (md5 {2} != {3}) - re-plan".format(
                rel(p), so.get("plan"), md5(sp) if os.path.isfile(sp) else None, so.get("md5"))
        if not os.path.isfile(bp) or md5(bp) != b.get("md5"):
            return None, "provisional base of {0}: {1} missing or off its pin {2}".format(rel(p), b.get("path"), b.get("md5"))
        return os.path.normpath(bp), None
    return None, None


def _graph():
    if D.graph is None:
        pv, pv_err = (None, None) if D.graph_override or not D.recipe else provisional_dry_graph(D.recipe)
        p = D.graph_override or pv or (None if pv_err else (find_graph(D.input_md5, plan_base_graphs(D.recipe) if D.recipe else ())
                                                            if D.input_md5 else None))   # card 106-5: the plan's base graph
        D.graph_path = p
        D.graph_error = pv_err                         # card 132-1 (fp-21): a stale provisional base is named, not guessed
        if not p and not D.graph_override and not pv_err and FIND_SKIPPED:
            D.graph_error = "no terminal-list graph JSON carries md5 {0}; skipped other shapes: {1}".format(
                D.input_md5, "; ".join("{0}: {1}".format(a, b) for a, b in FIND_SKIPPED))
        try:
            D.graph = OfflineGraph(p) if p else False
        except GraphShapeError as e:                   # card 95-1: a wrong-shape --graph is refused, not a crash
            D.graph, D.graph_error = False, str(e)
    return D.graph or None


def _graph_call(meth, default):
    def f(*a, **k):
        G = _graph()
        D.calls.append((meth, False))
        if D.mutated:
            D.taint += 1          # card 134-1: the static base graph read after a mutation is stale = stub data
        if G is None:
            return Fake(meth)
        return getattr(G, meth)(*a, **k)
    f._dry = True
    return f


def fake_gscript():
    """A module named `gscript`: gscript.py's TOP-LEVEL constant assignments evaluated one by one (os / str only),
    graph-backed readers, and a stub for every other attribute. The real gscript (pythoncom) is never imported."""
    m = types.ModuleType("gscript")
    m.__file__ = os.path.join(HERE, "gscript.py")
    ns = {"os": os, "sys": sys, "__file__": m.__file__}
    src = open(m.__file__, encoding="utf-8", errors="replace").read()
    for node in ast.parse(src).body:
        if isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and t.id.isupper() for t in node.targets):
            try:
                exec(compile(ast.Module(body=[node], type_ignores=[]), "gscript-const", "exec"), ns)
            except Exception:                                                      # noqa: BLE001
                pass
    for k, v in ns.items():
        if k.isupper() and isinstance(v, (str, int, float, tuple, dict, list, frozenset)):
            setattr(m, k, v)
    for meth in ("report_all", "uids", "count", "node_labels", "node_terms_uid"):
        setattr(m, meth, _graph_call(meth, None))
    m.ensure_loaded = lambda *a, **k: None

    def ga(name):
        if name.startswith("__"):
            raise AttributeError(name)
        f = _stub("g." + name)
        setattr(m, name, f)
        return f
    m.__getattr__ = ga
    return m


def fake_com():
    out = {}
    for n in ("pythoncom", "win32com", "win32com.client", "win32com.client.dynamic", "win32api", "win32gui", "win32con"):
        mm = types.ModuleType(n)
        mm.__getattr__ = (lambda nn: (lambda a: _stub(nn + "." + a) if not a.startswith("__") else
                                      (_ for _ in ()).throw(AttributeError(a))))(n)
        out[n] = mm
    out["win32com"].client = out["win32com.client"]
    out["win32com.client"].dynamic = out["win32com.client.dynamic"]
    return out


PURE_MODS = ("vigraph", "jev_candidates", "protocol", "stagekit", "allterms", "wiki_build", "jev_pairs", "jev_rowcheck")


def wrap_module(mod):
    """Every function DEFINED in `mod` -> a stub (a LabVIEW-touching fleet module loaded through K.mod)."""
    if getattr(mod, "_dry_wrapped", False):
        return mod
    for k, v in list(vars(mod).items()):
        if isinstance(v, types.FunctionType) and getattr(v, "__module__", None) == mod.__name__:
            setattr(mod, k, _stub(mod.__name__ + "." + k))
    mod._dry_wrapped = True
    return mod


def _outside_temp(p):
    try:
        return not os.path.abspath(str(p)).lower().startswith(os.path.abspath(TEMP).lower())
    except Exception:                                                              # noqa: BLE001
        return True


def install(graph_override=None):
    D.graph_override = graph_override
    os.makedirs(SINK, exist_ok=True)
    real_default = json.JSONEncoder.default
    json.JSONEncoder.default = lambda self, o: str(o) if isinstance(o, Fake) else real_default(self, o)
    for n, m in fake_com().items():
        sys.modules[n] = m
    sys.modules["gscript"] = fake_gscript()
    for p in (HERE, os.path.join(HERE, "recipes"), os.path.join(HERE, "bench")):
        if p not in sys.path:
            sys.path.insert(0, p)
    # side-effect fences: no child process, no file change outside %TEMP%
    import subprocess
    import shutil

    def refuse(name):
        def f(*a, **k):
            D.blocked.append(name)
            raise RuntimeError("dry run: {0} is blocked".format(name))
        return f
    for n in ("run", "Popen", "call", "check_call", "check_output"):
        setattr(subprocess, n, refuse("subprocess." + n))
    os.system = refuse("os.system")
    real_open = builtins.open

    def dry_open(file, mode="r", *a, **k):
        if isinstance(file, (str, bytes, os.PathLike)) and any(c in mode for c in "wax+") and _outside_temp(file):
            D.blocked.append("open-w " + os.path.basename(str(file)))
            file = os.path.join(SINK, os.path.basename(str(file)))
        return real_open(file, mode, *a, **k)
    builtins.open = dry_open

    def noop(name):
        def f(*a, **k):
            if any(_outside_temp(x) for x in a[1:2] or a[:1]):
                D.blocked.append(name)
                return None
            return getattr(shutil, "_real_" + name.split(".")[-1])(*a, **k)
        return f
    for n in ("copyfile", "copy", "copy2", "move"):
        if not hasattr(shutil, "_real_" + n):     # card 128-4: a 2nd in-process install() must not save the wrapper
            setattr(shutil, "_real_" + n, getattr(shutil, n))
        setattr(shutil, n, noop("shutil." + n))
    for n in ("remove", "unlink", "replace", "rename"):
        real = getattr(os, n)

        def f(*a, _real=real, _n=n, **k):
            if any(_outside_temp(x) for x in a[:2]):
                D.blocked.append("os." + _n)
                return None
            return _real(*a, **k)
        setattr(os, n, f)
    patch_stagekit()


def patch_stagekit():
    # stagekit is loaded only AFTER install() has put the fake gscript/pythoncom/win32com into sys.modules, so the
    # module it binds as `g` cannot reach LabVIEW; importlib (not an import statement) because protocol.py's
    # LV_IMPORT_RE reads any `import stagekit` line as a LabVIEW client, which this process provably is not.
    import importlib
    K = importlib.import_module("stagekit")
    import allterms
    import wiki_build
    allterms.read_terms = _graph_call("read_terms", None)
    wiki_build.read_live = _graph_call("read_live", None)
    for modname in ("jev_pairs", "jev_rowcheck"):
        try:
            mm = __import__(modname)
        except Exception:                                                          # noqa: BLE001
            continue
        for k in ("decide", "check_rows", "check_row", "stage_lines"):
            if hasattr(mm, k):
                setattr(mm, k, _jev_stub(modname + "." + k))
    import jev_candidates as JC
    if not hasattr(JC, "_dry_orig_candidates"):     # card 128-4: wrap the real function once per process
        JC._dry_orig_candidates = JC.candidates
    if not hasattr(K, "_dry_orig_mod"):
        K._dry_orig_mod = K.mod
    real_cands = JC._dry_orig_candidates

    def cands(G, intent, *a, **k):
        D.jev.append({"via": "candidates", "intent": _plain(intent)})
        return real_cands(G, intent, *a, **k)
    JC.candidates = cands
    real_mod = K._dry_orig_mod

    def mod(name):
        m = real_mod(name)
        return m if name in PURE_MODS else wrap_module(m)
    K.mod = mod
    S = K.Stage
    # card 128-4 (PD261(b)): a second in-process main() re-ran this and wrapped the WRAPPER (Stage._op depth 1 -> 2,
    # D.ops 63 -> 189, diag_c128_3_x5.log M2). The real methods are kept once on the class and every patch wraps them.
    if not hasattr(S, "_dry_orig"):
        S._dry_orig = dict((k, getattr(S, k)) for k in ("__init__", "gate", "_op", "address"))
    orig = dict(S._dry_orig)

    def init(self, *a, **k):
        orig["__init__"](self, *a, **k)
        self.out_json = os.path.join(SINK, os.path.basename(self.out_json))
        D.input_md5, D.input_vi = self.input_md5, self.input_vi
        D.works.append(self.work)

    def gate(self, label, ok, detail="", fatal=False, kind=None):
        if isinstance(ok, Fake):
            D.gate_taint = D.taint
            D.unverified.append(label)
            print("  UNVERIFIED  {0}  (dry: stub value)".format(label), flush=True)
            return True
        ok = bool(ok)
        # card 134-1 (review archive/peer/2026-10-02-c134-1-dry-selftest.md:62-73,110): taint is scoped to the STATEMENT that
        # calls the gate (snapshot at the recipe's last line event, dry()'s tracer), not "since the previous gate": a stub
        # used by an unrelated statement between two gates (s.es) no longer relabels a FALSE gate on simulated data.
        tainted = D.taint != (D.line_taint if D.line_taint is not None else D.gate_taint)
        D.gate_taint = D.taint
        # card 134-1 (PD287(a), docs/violation-decisions.md repeated-failure-class 2026-10-02 10:10): a gate FALSE on
        # simulated / real-graph (non-stub) data FAILS the dry, whatever op it follows. The old rule relabelled ANY false
        # gate after the first mutation UNVERIFIED (`not ok and (D.mutated or tainted)`) and hid FR three times (133-3).
        # Only a gate whose inputs touched a COM stub (taint moved since the previous gate; a read of the STATIC base
        # graph after a mutation counts as stub data, _graph_call) may stay UNVERIFIED.
        if not ok and tainted:
            D.unverified.append(label)
            print("  UNVERIFIED  {0}  (dry: stub input{1})".format(label, ", after mutation " + D.mutated if D.mutated
                                                                    else ""), flush=True)
            return False
        # card chat-S2 (PD327): a LOG-only mismatch (tools/gateclass.py, the ONE table shared with stagekit.Stage.gate) does not
        # fail the dry either; Stage.gate itself prints it SOFT and writes the soft log line.
        if not ok and _gateclass.classify_gate(label, detail, kind)["verdict"] != "log":
            D.fails.append("GATE " + label)
        return orig["gate"](self, label, ok, detail, fatal, kind) if kind else orig["gate"](self, label, ok, detail, fatal)

    def op(self, verb, fn, detail=""):
        D.ops.append(verb)
        if D.mutated is None:
            D.mutated = "Stage._op " + verb
        return orig["_op"](self, verb, fn, detail)

    def address(self, end, is_source, objs=None):
        D.addresses.append((_plain(end), bool(is_source), D.mutated))
        try:
            return orig["address"](self, end, is_source, objs)
        except RuntimeError as e:
            if not D.mutated:
                raise                     # the input graph is exact before the first mutation: a real failure
            D.unverified.append("address {0}".format(_plain(end)))
            print("  UNVERIFIED  address {0} after mutation {1}: {2}".format(_plain(end), D.mutated, e), flush=True)
            return (Fake("di"), Fake("ni"), Fake("ti")), "dry: unverified after mutation"

    def start(self):
        self.head("[0] FILES ONLY (DRY RUN: no LabVIEW, no copy)")
        self.R["claudedev_before"] = []
        got = md5(self.input_vi) if os.path.exists(self.input_vi) else "MISSING"
        self.R["input_md5_before"] = got
        self.gate("K1 input md5 == {0}".format(self.input_md5), got == self.input_md5, "got {0}".format(got), fatal=True)
        G = _graph()
        self.gate("DRY graph JSON for input md5 {0}".format(self.input_md5), G is not None,
                  getattr(D, "graph_error", None) or D.graph_path or "no tools/bench/graph_*.json carries this md5",
                  fatal=True)
        self.started = True
        return self.work

    def save(self, *a, **k):
        if D.mutated is None:
            D.mutated = "Stage.save"
        D.calls.append(("Stage.save", True))
        return "dry0" * 8

    def close(self, *a, **k):
        print("=== STAGE GATES (dry): {0} pass / {1} fail / {2} unverified".format(
            len(self.passes), len(self.fails), len(D.unverified)), flush=True)
        return 0

    def scratch(self, suffix, source=None):
        p = os.path.join(SINK, "{0}_{1}.vi".format(self.name, suffix))
        self.scratches.append(p)
        return p

    def discard_work(self):
        self.scratches.append(self.work)
        D.discards.append(self.work)                   # card chat-M2 (fp-35): X10 PROBE-EXEMPT evidence

    S.__init__, S.gate, S._op, S.address = init, gate, op, address
    S.start, S.save, S.close, S.scratch, S.discard_work = start, save, close, scratch, discard_work
    # card 136-2 (gate-fp fp-33): count every EXECUTED Stage whole-VI read (X10_RO_READS names) into D.calls, so X10's
    # edit-diagnostic model (x10_edit) has R from the dry trace. Originals kept once on the class (card 128-4 pattern).
    if not hasattr(S, "_dry_orig_reads"):
        S._dry_orig_reads = dict((k, getattr(S, k)) for k in ("uid_index", "census") if hasattr(S, k))
    for k_, f_ in S._dry_orig_reads.items():
        def rd(self, *a, _f=f_, _k=k_, **kw):
            D.calls.append(("Stage." + _k, False))
            return _f(self, *a, **kw)
        setattr(S, k_, rd)
    for k in ("restart", "_preload_enter", "_preload_exit", "drop_scratch", "pin_check"):
        setattr(S, k, lambda self, *a, **kw: None)

    def run(fn, stage):
        try:
            fn(stage)
            D.reached_end = True
        except K.Stop as e:
            pass                                       # the failing gate is already in D.fails
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            tb = traceback.format_exc()
            clean = D.taint == D.gate_taint and not D.mutated
            text = "{0}: {1}".format(type(e).__name__, str(e)[:160])
            if isinstance(e, CODE_DEFECTS) or clean:
                D.fails.append("PY {0}".format(text))
                print("  FAIL  dry: unhandled exception {0}\n{1}".format(text, tb[-1500:]), flush=True)
            else:
                D.stub_limit = text
                D.stub_tb = traceback.format_exc()[-900:]
                print("  STUB-LIMIT  dry path stopped on stub data after {0}: {1}\n{2}".format(D.mutated, text, D.stub_tb),
                      flush=True)
        return 0
    K.run = run


def _plain(x):
    try:
        return json.loads(json.dumps(x, default=lambda o: "<fake>" if isinstance(o, Fake) else str(o)))
    except Exception:                                                              # noqa: BLE001
        return str(x)


def _jev_stub(name):
    def f(*a, **k):
        it = None
        for x in list(a) + list(k.values()):
            if isinstance(x, dict) and "intent" in x:
                it = x["intent"]
        D.jev.append({"via": name, "intent": _plain(it), "line": a[0] if a and isinstance(a[0], str) else None})
        if name.endswith(".decide"):      # a decision dict whose every field is unknown (callers do dict(d, ...))
            return dict((k, Fake(name + "." + k)) for k in ("row_key", "pair_p", "op", "op_p", "risk_p", "action",
                                                            "decided_by", "evidence", "variant", "exec", "calls"))
        return Fake(name)
    return f


UNROUTABLE_RE = re.compile(r"^\s*(?:FACT\s+|FAIL\s+)?UNROUTABLE\s+(?:acts\b|\d+\s+row)")


class _UnroutableTap(object):
    """stdout pass-through that keeps every line an executor/Stage prints as an UNROUTABLE row (stagekit `FACT  UNROUTABLE
    acts ...`, stagexec.dry_run `  UNROUTABLE acts ...`, the ExecStop text `UNROUTABLE n row(s)`), card 108-5."""

    def __init__(self, inner):
        self.inner, self.hits, self._buf = inner, [], ""

    def write(self, s):
        self._buf += s
        while "\n" in self._buf:
            ln, self._buf = self._buf.split("\n", 1)
            if UNROUTABLE_RE.search(ln):
                self.hits.append(ln)
        return self.inner.write(s)

    def flush_tail(self):
        if self._buf and UNROUTABLE_RE.search(self._buf):
            self.hits.append(self._buf)
        self._buf = ""

    def flush(self):
        return self.inner.flush()

    def __getattr__(self, k):
        return getattr(self.inner, k)


def dry(recipe, graph=None):
    """Run in THIS process (the caller is a fresh process: `--dry` / `--prerun`). Returns the trace dict."""
    install(graph)
    import runpy
    path = os.path.abspath(recipe)
    D.recipe = path
    code_lines = set()
    try:
        co = compile(open(path, encoding="utf-8").read(), path, "exec")
        stack = [co]
        while stack:
            c = stack.pop()
            code_lines.update(ln for _s, _e, ln in c.co_lines() if ln)
            stack.extend(x for x in c.co_consts if isinstance(x, types.CodeType))
    except SyntaxError as e:
        D.fails.append("PY SyntaxError: {0}".format(e))
    hit = set()

    def tracer(frame, event, arg):
        if frame.f_code.co_filename == path:
            hit.add(frame.f_lineno)
            if event == "line":
                D.line_taint = D.taint            # card 134-1: the gate's taint is scoped to its statement
            return tracer
        return None
    t0 = time.time()
    if not D.fails:
        tap = _UnroutableTap(sys.stdout)
        sys.stdout = tap
        sys.settrace(tracer)
        unhook = x10_capture_executors()                       # card 130-1 (PD267(b)): record every Executor's set
        try:
            runpy.run_path(path, run_name="__main__")
        except SystemExit:
            pass
        except X10Probe:
            pass                                               # card 130-1: probe mode stops at the first Executor
        except BaseException as e:                                                 # noqa: BLE001
            D.fails.append("PY {0}: {1} (module level)".format(type(e).__name__, str(e)[:160]))
        finally:
            unhook()
            sys.settrace(None)
            tap.flush_tail()
            if sys.stdout is tap:
                sys.stdout = tap.inner
        # card 108-5 (PD222(d), device-failed): ANY UNROUTABLE row is a dry FAIL. diag_c108b_dry.log:39-43 printed
        # `FACT  UNROUTABLE acts [2]` and still ended `DRY PASS` + a PASS record, because the E1 gate that names it runs
        # after the first mutation and is downgraded to UNVERIFIED. An unroutable row is a plan fact, not stub data.
        for ln in tap.hits:
            D.fails.append("UNROUTABLE " + ln.split("UNROUTABLE", 1)[1].strip()[:200])
        # card 130-5 (PD268(b), docs/d1/tooling.md:20-38): an Executor that stopped before its plan's last op made the dry
        # PASS anyway (the recipe's E1 is downgraded to UNVERIFIED in a dry run): c128b stopped at op 48 of 63 and PASSed.
        # A dry that does not cover every op is no evidence for a launch -> FAIL. (Probe mode stops at the first Executor.)
        if not D.x10_probe:
            # card 134-1: the executor stop is the ROOT cause; since PD287(a) the recipe's own FALSE gate after it (E1 via
            # report_stop) FAILs too, so the stop is listed FIRST (first_fail names the cause, selftest_dry_c130_5 T2)
            D.fails[:0] = executor_stops(D.executors)
    status = "PASS" if (D.reached_end and not D.fails) else "FAIL"
    if status == "PASS" and D.unverified:
        status = "PASS-UNVERIFIED"      # card 134-1 (PD287(a)): refused at launch unless the card names each gate
    first = D.fails[0] if D.fails else (None if D.reached_end else "STUB-LIMIT: " + str(D.stub_limit)
                                        if D.stub_limit else "body did not reach its end")
    return {"status": status, "first_fail": first, "fails": D.fails, "unverified": D.unverified,
            "stub_limit": D.stub_limit, "reached_end": D.reached_end, "first_mutation": D.mutated,
            "coverage": [len(hit & code_lines), len(code_lines)], "ops": D.ops, "addresses": D.addresses,
            "jev": D.jev, "graph": rel(D.graph_path) if D.graph_path else None, "input_md5": D.input_md5,
            "input_vi": D.input_vi, "blocked": sorted(set(D.blocked)), "secs": round(time.time() - t0, 1),
            "calls": len(D.calls), "works": list(D.works), "executors": list(D.executors),
            "x10_reads": [n for n, _m in D.calls if n.split(".")[-1] in X10_EDIT_READS],   # card 136-2 (fp-33)
            "discards": list(D.discards),                                                   # card chat-M2 (fp-35)
            "saves": [n for n, _m in D.calls if X10_SAVE_RE.search(n.split(".")[-1])]}


# ---------------------------------------------------------------------------------------------- the pre-run
def plan_files(recipe):
    """(plan paths, every .json the recipe names). A plan = a named .json with a `decisions` list of id+action rows,
    OR (card 79-6, PD178(g)) a named `stageplan/1` file - admitted here by schema so its md5 keys the records; whether it
    may pass X2 is stageplan_check's call (finalized + final PASS), never this function's."""
    tree = ast.parse(open(recipe, encoding="utf-8").read())
    named, plans = [], []
    for n in ast.walk(tree):
        if isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value.lower().endswith(".json"):
            for base in (BENCH, ROOT, os.path.join(ROOT, "docs"), os.path.dirname(os.path.abspath(recipe))):
                p = os.path.join(base, n.value)
                if os.path.isfile(p):
                    named.append(p)
                    try:
                        d = json.load(open(p, encoding="utf-8"))
                    except Exception:                                              # noqa: BLE001
                        break
                    if isinstance(d, dict) and isinstance(d.get("decisions"), list) and \
                            all(isinstance(r, dict) and "id" in r and "action" in r for r in d["decisions"]):
                        plans.append(p)
                    elif isinstance(d, dict) and d.get("schema") == "stageplan/1":
                        plans.append(p)
                    break
    # gate-fp fp-5 (card 121-3): one file reached by two spellings (BENCH\x.json and <recipe dir>\x.json, or
    # ROOT\tools/bench/x.json) was kept twice by set(), so X2 listed the plan twice and X3/X5 doubled the rows.
    return _uniq_paths(plans), _uniq_paths(named)


def _uniq_paths(paths):
    seen = {}
    for p in paths:
        seen.setdefault(os.path.normcase(os.path.abspath(os.path.normpath(p))), p)
    return sorted(seen.values())


SP_WIRING = ("tunnel", "connect", "wire_sr", "branch",     # stagexec compiled-op kinds that make a wire
             "case_frame_wire", "connect_term_uid")       # card 124-6 (PD250(c)): == stagexec.REC_WIRING
# card 100-6: a `wire` action into a While loop's `new:X.cond` compiles to a `stop` op (stagexec compile_plan, self-test
# T36b; OpStopFromNode_v0). It COVERS its wire action, but the dry trace records it as `stop`, not `wire_*`, so it is not
# counted among the wiring ops executed (X5 first failed on plan_disp.json r8_stop: 24/25 covered).
SP_WIRE_OTHER = ("stop",)


def stageplan_check(path):
    """(ok, detail, plan|None, compiled ops|None) for a stageplan/1 a recipe names (card 79-6). ok only when
    final is True, finalized present with failed None, open_rows_match True, undecided 0, stagexec.load_final_plan
    passes (validates, base graph + every step file md5 unchanged) and every action compiles to a real op."""
    import stagexec as SX
    try:
        plan, _paths = SX.load_final_plan(path)
    except Exception as e:                                                         # noqa: BLE001
        return False, "load_final_plan: {0}".format(str(e)[:300]), None, None
    fz, bad = plan.get("finalized"), []
    if plan.get("final") is not True or not isinstance(fz, dict):
        bad.append("final={0!r}, finalized {1}".format(plan.get("final"), type(fz).__name__))
        fz = fz if isinstance(fz, dict) else {}
    if fz.get("failed") is not None:
        bad.append("finalized.failed={0!r}".format(fz.get("failed")))
    if fz.get("open_rows_match") is not True:
        bad.append("finalized.open_rows_match={0!r}".format(fz.get("open_rows_match")))
    if fz.get("undecided") != 0:
        bad.append("finalized.undecided={0!r}".format(fz.get("undecided")))
    try:
        ops = SX.compile_plan(plan)
    except Exception as e:                                                         # noqa: BLE001
        bad.append("compile_plan: {0}".format(str(e)[:200]))
        ops = None
    if bad:
        return False, "; ".join(bad), plan, ops
    return True, "final, finalized PASS, {0} actions -> {1} real ops".format(len(plan["actions"]), len(ops)), plan, ops


# ------------------------------------------------------------------------------ control_path_lint (CLAUDE.md 1c'')
# Card chat-F1, Pre-decided 190(c)(e) (connectivity-map-plan; numbered 148 until card chat-L2). Loop-to-loop CONTROL travels by local variable; queues/notifiers are for
# lossless DATA streams only; no edge detection on a polled boolean. Reads the stageplan/1 JSON STRUCTURALLY (action
# fields, endpoint dicts/symbols, the base graph's classes and terminal names) - no regex over the file text.
# Existed first: gscript.queue_node (obtain/enqueue/dequeue/release, the only queue writer), stagesim OPS (no queue
# op), no lint of either kind anywhere in tools/.
QUEUE_OPS = frozenset(("queue", "queue_node", "obtain_queue", "enqueue", "enqueue_element", "dequeue",
                       "dequeue_element", "release_queue", "notifier", "notifier_node", "obtain_notifier",
                       "send_notification", "wait_on_notification", "release_notifier"))
QUEUE_NAMES = frozenset(n.lower() for n in (
    "Obtain Queue", "Enqueue Element", "Enqueue Element at Opposite End", "Lossy Enqueue Element", "Dequeue Element",
    "Preview Queue Element", "Flush Queue", "Release Queue", "Get Queue Status", "Obtain Notifier",
    "Send Notification", "Wait on Notification", "Wait on Notification from Multiple", "Release Notifier",
    "Get Notifier Status", "Cancel Notification"))
QUEUE_KINDS = frozenset(("obtain", "enqueue", "dequeue", "release", "preview", "flush", "send", "wait"))
QUEUE_TERMS = frozenset(("queue", "queue out", "notifier", "notifier out", "element data type"))
NAME_FIELDS = ("class", "name", "prim", "primitive", "function", "label", "subvi", "vi")
COMPARE_NAMES = frozenset(n.lower() for n in ("Equal?", "Not Equal?", "Greater?", "Less?", "Greater Or Equal?",
                                              "Less Or Equal?"))
LOGIC_NAMES = frozenset(n.lower() for n in ("And", "Or", "Not", "Exclusive Or", "Not Exclusive Or", "Not And",
                                            "Not Or", "Implies"))
COMPARE_TERMS = frozenset(("x = y?", "x != y?", "x > y?", "x < y?", "x >= y?", "x <= y?"))
LOGIC_TERMS = frozenset(("x .and. y?", "x .or. y?", ".not. x?", "x .xor. y?", "x .nxor. y?", ".not. (x .and. y)?",
                         ".not. (x .or. y)?", "x .implies. y?"))
LOCAL_CLASSES = frozenset(("Local", "LocalVariable"))
BOOL_TYPES = frozenset(("bool", "boolean", "tf"))


def _ep(ref):
    """endpoint -> (node key, term). node key: int uid, or 'new:X' for a plan-created object."""
    if isinstance(ref, dict):
        return ref.get("uid"), ref.get("side") or ref.get("term")
    if isinstance(ref, str):
        h, _d, t = ref.partition(".")
        if h.startswith("new:"):
            return h, t
        try:
            return int(h), t
        except ValueError:
            return h, t
    return None, None


def _base_graph(plan):
    """(class by uid, set of terminal names by owner uid) from the plan's base graph JSON; ({}, {}) if unreadable."""
    p = ((plan.get("base") or {}).get("path")) or ""
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    try:
        g = json.load(open(p, encoding="utf-8"))
    except Exception:                                                              # noqa: BLE001
        return {}, {}
    cls = dict((o["uid"], o["class"]) for o in g.get("objs") or [] if isinstance(o, dict) and "uid" in o)
    terms = collections.defaultdict(set)
    for t in g.get("terminals") or []:
        terms[t.get("owner_uid")].add(t.get("term_name") or "")
    return cls, terms


def control_path_lint(plan, base=None):
    """List of refusals (empty = the plan passes). `base` = (cls, terms) for tests; else read from plan['base']."""
    cls, bterms = base if base is not None else _base_graph(plan)
    A = plan.get("actions") or []
    bad = []
    created = {}                                            # 'new:X' -> action (create / tunnel / add_shift_reg)
    for i, a in enumerate(A, 1):
        if not isinstance(a, dict):
            continue
        op = str(a.get("op") or "").lower()
        names = set(str(a.get(f)).strip().lower() for f in NAME_FIELDS if isinstance(a.get(f), str))
        tnames = set(str(t.get("name") or "").strip().lower() for t in a.get("terminals") or [] if isinstance(t, dict))
        qhit = (op in QUEUE_OPS) or bool(names & QUEUE_NAMES) or \
               (op in ("create", "primitive", "primitive_create") and bool(tnames & QUEUE_TERMS)) or \
               (str(a.get("kind") or "").lower() in QUEUE_KINDS and ("queue" in op.split("_") or "notifier" in op.split("_")))
        if qhit:
            why = a.get("why")
            if not (a.get("data_stream") is True and isinstance(why, str) and why.strip()):
                bad.append("Q action {0} ({1}): creates a queue/notifier primitive {2} without data_stream: true + why "
                           "(CLAUDE.md 1c'': control signals between loops are locals)".format(
                               i, a.get("id"), sorted((names & QUEUE_NAMES) or (tnames & QUEUE_TERMS)) or op))
        if a.get("as"):
            if op == "add_shift_reg":
                created["new:" + a["as"] + "R"] = created["new:" + a["as"] + "L"] = a
            created["new:" + a["as"]] = a
    wires = [(i, a) for i, a in enumerate(A, 1) if isinstance(a, dict) and str(a.get("op")).lower() == "wire"]

    def kind_of(node):
        """'compare' | 'logic' | None for a consumer node."""
        if isinstance(node, str) and node in created:
            a = created[node]
            ns = set(str(a.get(f)).strip().lower() for f in NAME_FIELDS if isinstance(a.get(f), str))
            ts = set(str(t.get("name") or "") for t in a.get("terminals") or [] if isinstance(t, dict))
        else:
            ns, ts = set(), bterms.get(node, set())
        if ns & LOGIC_NAMES or ts & LOGIC_TERMS:
            return "logic"
        if ns & COMPARE_NAMES or ts & COMPARE_TERMS:
            return "compare"
        return None

    def crosses(node):
        """the source is a local variable or a tunnel (a value arriving from / published across a loop border)."""
        if isinstance(node, str) and node in created:
            a = created[node]
            return str(a.get("op")).lower() == "tunnel" or a.get("class") in LOCAL_CLASSES
        return cls.get(node) in LOCAL_CLASSES or cls.get(node) in TUNNELS

    def declared_type(*objs):
        for o in objs:
            if isinstance(o, dict):
                for f in ("type", "dtype", "data_type"):
                    if isinstance(o.get(f), str):
                        return o[f].strip().lower()
        return None

    for a in A:
        if not (isinstance(a, dict) and str(a.get("op")).lower() == "add_shift_reg" and a.get("as")):
            continue
        R, L = "new:" + a["as"] + "R", "new:" + a["as"] + "L"
        writers = [(i, w) for i, w in wires if _ep(w.get("dst")) == (R, "inner")]
        readers = [(i, w) for i, w in wires if _ep(w.get("src")) == (L, "inner")]
        if not writers or not readers:
            continue
        for iw, w in writers:
            s_node, s_term = _ep(w.get("src"))
            if not crosses(s_node):
                continue
            cons = [_ep(r.get("dst"))[0] for _i, r in readers]
            kinds = [kind_of(c) for c in cons]
            if any(k is None for k in kinds):
                continue                                    # the previous value feeds something other than a compare
            both = all(any(_ep(x.get("src")) == (s_node, s_term) and _ep(x.get("dst"))[0] == c for _j, x in wires)
                       for c in cons)
            if not both:
                continue                                    # not "current vs previous of the same signal"
            ty = declared_type(w.get("src"), a, created.get(s_node) if isinstance(s_node, str) else None)
            if ty is not None and ty not in BOOL_TYPES and "logic" not in kinds:
                continue                                    # a declared non-boolean (a counter) compared: allowed
            bad.append("E shift register {0} ({1}): {2} {3!r} from a {4} is compared with its previous value by {5} - "
                       "an edge detector on a polled boolean across loops{6} (CLAUDE.md 1c'': publish a counter/value)"
                       .format(a["as"], a.get("id"), s_node, s_term, "local/tunnel", sorted(set(cons), key=str),
                               "" if ty in BOOL_TYPES or "logic" in kinds else
                               "; source type undeclared - declare type (e.g. 'u32') on the wire src to allow a counter"))
    return bad


# ------------------------------------------------------------------ card 114-1 S0: Build Array half-wired vs open sibling
# PD227(j), docs/violation-decisions.md 2026-09-28 02:25 (retrospective-cycle113 `repeated-failure-class`, ACCEPTED): wiring
# ONE input of a Build Array whose other input stays an OPEN row at the stage end made LabVIEW rename inputs - #2626 in
# L2-B1 (stage_d1_l2b1.log:516-522, licensed by plan_l2b1_licence.json) and #11261 in B2b launch 1 (stage_d1_l2b2b.log:
# 187-189,214). Existed first: plan_l2b1_licence.json (pb-licence/1, read only by stage_d1_l2b1.py), control_path_lint
# (_base_graph reused); no check of this class anywhere in tools/. It only ADDS gate X11; no existing gate changes.
BA_CLASSES = frozenset(("BuildArray",))


def _base_terms(plan):
    """(class by uid, [terminal rows] by owner uid) from the plan's base graph; ({}, {}) if unreadable."""
    p = ((plan.get("base") or {}).get("path")) or ""
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    try:
        g = json.load(open(p, encoding="utf-8"))
    except Exception:                                                              # noqa: BLE001
        return {}, {}
    cls = dict((o["uid"], o["class"]) for o in g.get("objs") or [] if isinstance(o, dict) and "uid" in o)
    by = collections.defaultdict(list)
    for t in g.get("terminals") or []:
        by[t.get("owner_uid")].append(t)
    return cls, by


def pb_licences(plan_path, bench=None):
    """{node uid: licence file} from every pb-licence/1 file under tools/bench whose `plan` names plan_path."""
    out = {}
    want = os.path.normcase(os.path.abspath(plan_path)) if plan_path else None
    for f in glob.glob(os.path.join(bench or BENCH, "*licence*.json")):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:                                                          # noqa: BLE001
            continue
        if not isinstance(d, dict) or d.get("schema") != "pb-licence/1" or not want:
            continue
        pp = d.get("plan") or ""
        pp = pp if os.path.isabs(pp) else os.path.join(ROOT, pp)
        if os.path.normcase(os.path.abspath(pp)) != want:
            continue
        for r in d.get("rename_by_uid") or []:
            if isinstance(r, dict) and isinstance(r.get("node"), int):
                out[r["node"]] = rel(f)
    return out


def buildarray_open_sibling(plan, base=None, licences=None):
    """-> [{row, node, wired, open, licensed}] : every `wire` action whose dst is an INPUT of a Build Array node while
    another input of that node is an open row (plan open_rows) at the stage end. licensed = the pb-licence/1 file that
    covers the node, else None. `base` = (cls, terms by owner) for tests; else read from plan['base']."""
    cls, by = base if base is not None else _base_terms(plan)
    lic = licences or {}
    opens = collections.defaultdict(list)
    for r in plan.get("open_rows") or []:
        if isinstance(r, dict) and isinstance(r.get("node"), int):
            opens[r["node"]].append(str(r.get("term") or ""))
    out = []
    for a in plan.get("actions") or []:
        if not (isinstance(a, dict) and str(a.get("op")).lower() == "wire" and isinstance(a.get("dst"), dict)):
            continue
        n = a["dst"].get("uid")
        if not isinstance(n, int) or cls.get(n) not in BA_CLASSES or not opens.get(n):
            continue
        ins = [t for t in by.get(n, []) if not t.get("is_source")]
        tu = a["dst"].get("term_uid")
        me = [t for t in ins if tu is not None and int(t.get("term_uid") or -1) == int(tu)]
        wname = me[0]["term_name"] if me else a["dst"].get("term")
        in_names = collections.Counter(t.get("term_name") or "" for t in ins)
        sib = [o for o in opens[n] if in_names.get(o) and (o != wname or in_names[o] > 1)]
        if sib:
            out.append({"row": a.get("id"), "node": n, "wired": wname, "open": sorted(set(sib)),
                        "licensed": lic.get(n)})
    return out


# card 114-3 C4 (review archive/peer/2026-09-28-c114b-l2b3d.md s3): a tunnel group (a `tunnel` action + the `wire` INTO its
# face, executed by stagexec as ONE connect_from_wire across the border) from an already-WIRED source RE-CREATES that
# source's wire - the old uid is LOST and LabVIEW may re-issue it at once to another object (stage_d1_l2b3.log:74,94: the
# junk Invoke took 5174 twice; opmodels/connect_from_wire.json:10,266; stagesim.cfw_border_rule). A LATER row naming that
# old uid (delete_wire wire_uid, a uid field, anything) would address a different object or nothing. Existed first:
# _base_terms (reused), stagesim.plan_tunnel_face (the same group rule on a sim state); no check of this class in tools/.
# It only ADDS gate X12; no existing gate changes.
def _ints(o, out):
    if isinstance(o, bool):
        return out
    if isinstance(o, int):
        out.add(o)
    elif isinstance(o, dict):
        for v in o.values():
            _ints(v, out)
    elif isinstance(o, (list, tuple)):
        for v in o:
            _ints(v, out)
    return out


def _end_parts(e):
    """(head, term_uid, term name) of a plan endpoint: a dict {uid, term_uid?, term?} or a string '<uid>.<term>'."""
    if isinstance(e, dict):
        return e.get("uid"), e.get("term_uid"), e.get("term")
    if isinstance(e, str) and "." in e:
        h, t = e.split(".", 1)
        return h, None, t
    return None, None, None


def recreated_wire_refs(plan, base=None):
    """-> (recreated, flags). recreated = [{wire, row, idx}]: every `wire` action whose dst is a face of a tunnel an
    EARLIER `tunnel` action of the plan made and whose src is a base-graph terminal on a wire (the border-crossing cfw
    from a wired source). flags = [{row, idx, wire, recreated_by}]: every LATER action (index > the re-creating one)
    that carries that old wire uid anywhere in its fields. `base` = (cls, terms by owner) for tests."""
    _cls, by = base if base is not None else _base_terms(plan)
    wire_of_term, rows_of = {}, collections.defaultdict(list)
    for owner, ts in by.items():
        for t in ts:
            if t.get("term_uid") is not None:
                wire_of_term[int(t["term_uid"])] = int(t.get("wire_uid") or 0)
            rows_of[str(owner)].append(t)
    tunnels, recreated, gone = set(), [], {}
    A = plan.get("actions") or []
    for i, a in enumerate(A, 1):
        if not isinstance(a, dict):
            continue
        op = str(a.get("op")).lower()
        if op == "tunnel" and a.get("as"):
            tunnels.add("new:" + str(a["as"]))
            continue
        if op != "wire":
            continue
        dh, _dt, _dn = _end_parts(a.get("dst"))
        if not (isinstance(dh, str) and dh in tunnels):
            continue
        sh, stu, sname = _end_parts(a.get("src"))
        if isinstance(sh, str) and sh.startswith("new:"):
            continue
        w = 0
        if stu is not None:
            w = wire_of_term.get(int(stu), 0)
        elif sh is not None and sname is not None:
            hit = [t for t in rows_of.get(str(sh), []) if t.get("term_name") == sname and t.get("is_source")]
            w = int(hit[0].get("wire_uid") or 0) if len(hit) == 1 else 0
        if w and w not in gone:
            gone[w] = (a.get("id"), i)
            recreated.append({"wire": w, "row": a.get("id"), "idx": i})
    flags = []
    for j, a in enumerate(A, 1):
        if not isinstance(a, dict):
            continue
        named = _ints(dict((k, v) for k, v in a.items() if k not in ("pos", "checkpoint")), set())   # a position is no uid
        hit = sorted(w for w in named if w in gone and j > gone[w][1])
        for w in hit:
            flags.append({"row": a.get("id"), "idx": j, "wire": w, "recreated_by": gone[w][0]})
    return recreated, flags


# card 115-1 A1 (PD229(a); retrospective-cycle114 `device-failed` ACCEPTED: the prior-art review missed that the measured
# opmodels/connect_from_wire.json:266 already said a border-crossing connect RE-CREATES a wired source's wire, while
# stagesim branched it - nothing compared the simulator against the op's own recorded samples). X13 OPMODEL CONFORMANCE:
# every op a stageplan uses has the recorded samples of its model files (stagesim.MODEL_ALIASES -> opmodels/<op>.json)
# REPLAYED through stagesim's own op functions with the params stagesim.model_for gives the plan's run; a sample whose
# measured WIRE OUTCOME the replay does not reproduce FAILS the gate. An op with no model file, and a model file whose op
# has no replayer here, are WARN lines (a judgement item), never skipped silently and never a PASS of that file.
# Existed first (checked): stagesim.load_models / model_for / OPS / plan_tunnel_face / cfw_border_rule (used, not edited);
# stagesim selftest G68-G71 (toy graph only, not the samples); diag_c114d_replay.py (real plans, not samples). No
# sample-replay check existed in tools/. It only ADDS gate X13; no existing gate changes.
OPMODEL_DIR = os.path.join(BENCH, "opmodels")
# replayer per MODEL FILE op: a sample of these ops is one source -> tunnel -> sink connect across one loop border (the
# measured shape: exactly 1 new tunnel, 2 edges added; connect_from_wire.json:267, tunnel.json:201). stagesim runs it as
# the plan's tunnel group: `tunnel` + the `wire` into its face + the `wire` out of its other face (stagexec compiles that
# group to ONE connect_from_wire, stagesim.plan_tunnel_face).
BORDER_GROUP_OPS = ("connect_from_wire", "tunnel")


def _sample_raw(model_path, sample):
    return json.load(REAL_OPEN(os.path.join(os.path.dirname(model_path), sample["raw"]), encoding="utf-8"))


def _border_group_case(model_path, sample):
    """-> (state, actions, roles, measured) for one border-group sample, all from the sample's raw diff:
    S = the source feeding the new tunnel's sink face, D = the sink its other face feeds, R = the source's other sinks
    (edges_rewired); a terminal's BEFORE wire = terms_changed[wire_uid][0] when its wire changed, else its after wire."""
    tg, raw = sample.get("target") or {}, _sample_raw(model_path, sample)
    D = raw.get("diff") or {}
    nt = (sample.get("checks") or {}).get("new_tunnels") or []
    if len(nt) != 1:
        raise ValueError("sample made {0} tunnels; the border-group replay needs exactly 1".format(len(nt)))
    T = int(nt[0])
    ocls = dict((int(o["uid"]), o["class"]) for o in D.get("objs_added") or [])
    faces = dict((ocls.get(int(t["term_uid"])), int(t["term_uid"])) for t in D.get("terms_added") or []
                 if int(t["owner_uid"]) == T)
    if set(faces) != {"InnerTerminal", "OuterTerminal"}:
        raise ValueError("tunnel #{0} faces by class: {1}".format(T, faces))
    fset = set(faces.values())
    after, owner, before = {}, {}, {}
    for t in D.get("terms_added") or []:
        after[int(t["term_uid"])] = int(t.get("wire_uid") or 0)
    for e in D.get("edges_added") or []:
        after[int(e["src"])], after[int(e["sink"])] = int(e["wire"]), int(e["wire"])
        owner[int(e["src"])], owner[int(e["sink"])] = int(e["src_owner"]), int(e["sink_owner"])
    for e in D.get("edges_rewired") or []:
        after[int(e["src"])], after[int(e["sink"])] = int(e["wire"][1]), int(e["wire"][1])
    for c in D.get("terms_changed") or []:
        owner.setdefault(int(c["term_uid"]), int(c["owner_uid"]))
        w = (c.get("changed") or {}).get("wire_uid")
        if w:
            before[int(c["term_uid"])], after[int(c["term_uid"])] = int(w[0] or 0), int(w[1] or 0)
    into = [e for e in D.get("edges_added") or [] if int(e["sink"]) in fset]
    outof = [e for e in D.get("edges_added") or [] if int(e["src"]) in fset]
    if len(into) != 1 or len(outof) != 1:
        raise ValueError("edges into / out of the tunnel faces: {0} / {1}".format(len(into), len(outof)))
    S, Dt = int(into[0]["src"]), int(outof[0]["sink"])
    din = int(into[0]["sink"]) == faces["OuterTerminal"]
    R = sorted(int(e["sink"]) for e in D.get("edges_rewired") or [] if int(e["src"]) == S)
    bw = lambda t: before.get(t, after.get(t, 0))                                           # noqa: E731
    src_d, dst_d = tg.get("src"), tg.get("dst")
    body = int(dst_d[0]) if din else int(src_d[0])
    parent = (int(src_d[0]) if din else int(dst_d[0])) if isinstance(src_d, list) else -900001   # cfw: src diagram unread
    s_diag, d_diag = (parent, body) if din else (body, parent)
    loop = int(tg.get("setup_result") or -900002)

    def row(t, src, fd):
        return {"term_uid": t, "term_name": "", "is_source": src, "wire_uid": bw(t), "owner_uid": owner.get(t, t),
                "owner_class": tg.get("src_cls") if t == S and tg.get("src_cls") else "Function",
                "frame_diagram": fd, "term_class": "Terminal"}
    terms = [row(S, True, s_diag), row(Dt, False, d_diag)] + [row(r, False, s_diag) for r in R]
    st = {"terminals": terms, "objs": [{"uid": loop, "class": "WhileLoop", "pos": [0, 0], "owner": "Diagram"}],
          "loops": [], "fs_pairs": None, "graph_summary": {}, "sym": {}, "diagrams": {}, "neg": 0, "removed_nodes": [],
          "owners": {}, "dedupe": {}}
    fa, fb = ("new:X.outer", "new:X.inner") if din else ("new:X.inner", "new:X.outer")
    acts = [{"op": "tunnel", "loop": loop, "body": body, "parent": parent, "dir": "in" if din else "out", "as": "X"},
            {"op": "wire", "src": {"uid": owner.get(S, S), "term_uid": S}, "dst": fa},
            {"op": "wire", "src": fb, "dst": {"uid": owner.get(Dt, Dt), "term_uid": Dt}}]
    roles = dict([(S, "src"), (Dt, "dst"), (faces["OuterTerminal"], "T.outer"), (faces["InnerTerminal"], "T.inner")] +
                 [(r, "sink:{0}".format(r)) for r in R])
    meas = _wire_outcome(dict((t, bw(t)) for t in roles), dict((t, after.get(t, 0)) for t in roles), roles, S, Dt)
    return st, acts, roles, meas, faces


def _wire_outcome(bef, aft, roles, S, Dt):
    """The compared fields: source_wire / sink_wire (new | kept | recreated/replaced), groups (which roles share one wire
    after the op, an unwired terminal alone), old_source_wire_members (roles still on the source's BEFORE wire)."""
    def fate(t):
        return "new" if not bef.get(t) else ("kept" if aft.get(t) == bef.get(t) else "recreated")
    g = collections.defaultdict(list)
    for t, r in roles.items():
        g[aft.get(t) or ("unwired", t)].append(r)
    old = bef.get(S)
    return {"source_wire": fate(S), "sink_wire": fate(Dt), "groups": sorted(sorted(x) for x in g.values()),
            "old_source_wire_members": sorted(roles[t] for t in roles if old and aft.get(t) == old)}


def replay_sample(model_path, sample, models):
    """-> (outcome, mismatches, detail): outcome 'PASS' | 'FAIL' | 'ERROR'; mismatches [(field, measured, simulated)]."""
    import stagesim as SS
    try:
        st, acts, roles, meas, faces = _border_group_case(model_path, sample)
    except Exception as e:                                                               # noqa: BLE001
        return "ERROR", [("case", "readable border-group sample", str(e))], None
    bef = dict((r["term_uid"], r["wire_uid"]) for r in st["terminals"])
    effs, sym = [], {}
    try:
        for a in acts:
            P = SS.model_for(a["op"], models)[0]
            eff, _c = SS.OPS[a["op"]](st, a, P, None, {})
            effs.append(eff)
            if a["op"] == "tunnel":
                sym = {eff["outer"]: faces["OuterTerminal"], eff["inner"]: faces["InnerTerminal"]}
    except SS.SimError as e:
        return "FAIL", [("replay", "applies", "SimError: {0}".format(e))], effs
    aft = {}
    for r in st["terminals"]:
        aft[sym.get(r["term_uid"], r["term_uid"])] = r["wire_uid"]
    bef.update((faces[k], 0) for k in faces)
    sim = _wire_outcome(bef, aft, roles, [t for t, r in roles.items() if r == "src"][0],
                        [t for t, r in roles.items() if r == "dst"][0])
    mm = [(k, meas[k], sim[k]) for k in meas if meas[k] != sim[k]]
    return ("PASS" if not mm else "FAIL"), mm, {"measured": meas, "simulated": sim, "hows": [e.get("how") for e in effs[1:]]}


# card 115-2 R0 (additive; X13 used to WARN "not-replayed" for these three files): replayers for the DELETE family. A
# sample's raw diff carries every terminal the op touched (terms_removed, terms_changed, both ends of edges_removed); a
# terminal the op did NOT touch is absent, so a surviving wire that the diff shows with no source or no sink while it is
# NOT in the measured half_wires_before/after gets ONE stand-in row of the missing polarity (it must exist: the measured
# half-wire lists say the wire has both ends). Owner classes come from objs_removed / terms_*; a tunnel's faces get
# opposite Inner/Outer classes (the raw diff carries no term_class). Compared: removed terms, removed nodes, per-terminal
# wire fate (kept / cleared; an `allow_either` terminal of the sim accepts both), and is_source flips.
DELETE_OPS = ("delete_object", "delete_wire", "remove_bad_wires")
DELETE_DISABLE = {"tunnel_flip": ("delete_object", False), "sr_pair": ("delete_object", False),
                  "drop_unconnected_fsit": ("remove_bad_wires", False), "drop_unwired_tunnel": ("delete_wire", False)}


def _delete_case(model_path, sample):
    raw = _sample_raw(model_path, sample)
    D, op, meta = raw.get("diff") or {}, raw.get("op"), raw.get("meta") or {}
    cls = dict((int(o["uid"]), o["class"]) for o in D.get("objs_removed") or [])
    rows, flips_meas, after = {}, set(), {}

    def put(t, owner, src, wire, name=""):
        r = rows.setdefault(int(t), {"term_uid": int(t), "term_name": name, "is_source": src, "wire_uid": int(wire or 0),
                                     "owner_uid": int(owner), "owner_class": "", "frame_diagram": 0, "term_class": "Terminal"})
        if r["is_source"] is None and src is not None:
            r["is_source"] = src
        return r
    for t in D.get("terms_removed") or []:
        put(t["term_uid"], t["owner_uid"], bool(t["is_source"]), t["wire_uid"], t.get("term_name", ""))
        cls[int(t["owner_uid"])] = t["owner_class"]
    for e in D.get("edges_removed") or []:
        put(e["src"], e["src_owner"], True, e["wire"])
        put(e["sink"], e["sink_owner"], False, e["wire"])
    for c in D.get("terms_changed") or []:
        ch = c.get("changed") or {}
        w = ch.get("wire_uid")
        isrc = ch.get("is_source")
        r = put(c["term_uid"], c["owner_uid"], bool(isrc[0]) if isrc else None, w[0] if w else 0)
        if w:
            r["wire_uid"], after[r["term_uid"]] = int(w[0] or 0), int(w[1] or 0)
        if isrc:
            flips_meas.add(r["term_uid"])
        cls[int(c["owner_uid"])] = c["owner_class"]
    half = set(int(x) for x in (D.get("half_wires_before") or []))
    by_w = collections.defaultdict(list)
    for r in rows.values():
        by_w[r["wire_uid"]].append(r)
    for w, rs in by_w.items():                       # a half-wire's unknown polarity = its known rows' polarity
        known = [r["is_source"] for r in rs if r["is_source"] is not None]
        for r in rs:
            if r["is_source"] is None:
                r["is_source"] = bool(known[0]) if (w in half and known) else False
    for r in rows.values():
        r["owner_class"] = cls.get(r["owner_uid"], "Function")
    for u in set(r["owner_uid"] for r in rows.values() if r["owner_class"] in stagesim_tun1()):
        rs = sorted((r for r in rows.values() if r["owner_uid"] == u), key=lambda r: (r["is_source"], r["term_uid"]))
        for k, r in enumerate(rs):
            r["term_class"] = ("OuterTerminal", "InnerTerminal")[min(k, 1)] if len(rs) > 1 else "OuterTerminal"
    gone_w = set(int(o["uid"]) for o in D.get("objs_removed") or [] if o["class"] == "Wire")
    half_a = set(int(x) for x in (D.get("half_wires_after") or []))
    removed_t = set(int(t["term_uid"]) for t in D.get("terms_removed") or [])
    flip_to = dict((int(c["term_uid"]), bool((c.get("changed") or {})["is_source"][1])) for c in D.get("terms_changed") or []
                   if (c.get("changed") or {}).get("is_source"))
    stand, k = [], 0
    for w, rs in sorted(by_w.items()):
        if not w:
            continue
        need = set()
        if w not in half:                            # before the op the wire had both ends
            need |= set(p for p in (True, False) if not any(r["is_source"] == p for r in rs))
        if w not in half_a and w not in gone_w:      # after the op it still has both ends
            ra = [r for r in rs if r["term_uid"] not in removed_t and after.get(r["term_uid"], w) == w]
            need |= set(p for p in (True, False) if not any(flip_to.get(r["term_uid"], r["is_source"]) == p for r in ra))
        for pol in sorted(need):
            k += 1
            stand.append({"term_uid": -910000 - k, "term_name": "", "is_source": pol, "wire_uid": w, "owner_uid": -910000 - k,
                          "owner_class": "Function", "frame_diagram": 0, "term_class": "Terminal"})
    # a removed node = a removed object that OWNS a terminal row of the read (the terminal read files both halves of a
    # FlatSequenceInnerTunnel pair under ONE owner: remove_bad_wires_1 terms 2304/2310 read owner 2283 while objs_removed
    # also lists #2301 - such a paired half owns no row, so it is not a node of the terminal graph stagesim works on)
    owners_read = set(r["owner_uid"] for r in rows.values())
    nodes = set(int(o["uid"]) for o in D.get("objs_removed") or [] if o["class"] != "Wire" and
                int(o["uid"]) not in removed_t and int(o["uid"]) in owners_read)
    act = {"op": op}
    if op == "delete_object":
        act["uid"] = int(meta["uid"])
    elif op == "delete_wire":
        act["wire_uid"] = int(meta["wire"])
    st = {"terminals": [dict(r) for r in rows.values()] + stand, "objs": [], "loops": [], "fs_pairs": None,
          "graph_summary": {}, "sym": {}, "diagrams": {}, "neg": 0, "removed_nodes": [], "owners": {}, "dedupe": {}}
    meas = {"terms_removed": sorted(removed_t), "nodes_removed": sorted(nodes), "flips": sorted(flips_meas),
            "fate": dict((t, _fate(r["wire_uid"], after.get(t, r["wire_uid"]))) for t, r in rows.items() if t not in removed_t)}
    return st, act, meas


def stagesim_tun1():
    import stagesim as SS
    return tuple(SS.TUN_FLIP)


def _fate(b, a):
    return "unwired" if not b and not a else ("kept" if a == b else ("cleared" if not a else "moved"))


def replay_delete_sample(model_path, sample, models, disable=()):
    """-> (outcome, mismatches, detail) for one delete_object / delete_wire / remove_bad_wires sample (card 115-2 R0)."""
    import stagesim as SS
    try:
        st, act, meas = _delete_case(model_path, sample)
    except Exception as e:                                                               # noqa: BLE001
        return "ERROR", [("case", "readable delete-family sample", str(e))], None
    bef = dict((r["term_uid"], (r["wire_uid"], r["is_source"])) for r in st["terminals"] if r["term_uid"] > -900000)
    P = dict(SS.model_for(act["op"], models)[0])
    for d in disable:
        if d in DELETE_DISABLE and DELETE_DISABLE[d][0] == act["op"]:
            P[d] = DELETE_DISABLE[d][1]
    try:
        eff, _c = SS.OPS[act["op"]](st, act, P, None, {})
    except SS.SimError as e:
        return "FAIL", [("replay", "applies", "SimError: {0}".format(e))], None
    now = dict((r["term_uid"], r) for r in st["terminals"])
    either = set((eff or {}).get("allow_either") or [])
    sim = {"terms_removed": sorted(t for t in bef if t not in now),
           "nodes_removed": sorted(set(st["removed_nodes"])),
           "flips": sorted(t for t in bef if t in now and now[t]["is_source"] != bef[t][1]),
           "fate": dict((t, _fate(bef[t][0], now[t]["wire_uid"])) for t in bef if t in now)}
    mm = [(k, meas[k], sim[k]) for k in ("terms_removed", "nodes_removed", "flips") if meas[k] != sim[k]]
    fb = dict((t, (f, sim["fate"].get(t))) for t, f in meas["fate"].items() if sim["fate"].get(t) != f and
              not (t in either and {f, sim["fate"].get(t)} <= {"kept", "cleared"}))
    if fb:
        mm.append(("fate", dict((t, v[0]) for t, v in fb.items()), dict((t, v[1]) for t, v in fb.items())))
    return ("PASS" if not mm else "FAIL"), mm, {"op": act["op"], "measured": meas, "allow_either": sorted(either)}


def opmodel_conformance(ops=None, model_dir=None, disable=(), log=None):
    """X13 core. ops = the stageplan ops to check (None = every model file in model_dir). disable: ('cfw_border_rule',)
    runs with stagesim.cfw_border_rule switched off (card 115-1 A2's negative case). -> {files: {name: {status, samples,
    fails}}, fails: [{file, sample, field, measured, simulated}], warns: [str]}"""
    import stagesim as SS
    md = model_dir or OPMODEL_DIR
    saved = SS.cfw_border_rule
    if "cfw_border_rule" in disable:
        SS.cfw_border_rule = lambda _d: None
    try:
        models = SS.load_models(md)
        by_file = dict((os.path.splitext(os.path.basename(m["path"]))[0], (name, m)) for name, m in models.items())
        if ops is None:
            names, warns = [n for n, _m in sorted(by_file.values(), key=lambda x: x[0])], []
        else:
            names, warns = [], []
            for op in sorted(set(ops)):
                have = [n for n in SS.MODEL_ALIASES.get(op, (op,)) if n in models]
                if not have:
                    warns.append("X13 WARN op {0!r}: no model file in {1} (provisional rule; aliases {2})".format(
                        op, rel(md), list(SS.MODEL_ALIASES.get(op, (op,)))))
                names += [n for n in have if n not in names]
        files, fails = {}, []
        for n in names:
            m = models[n]
            fname = os.path.basename(m["path"])
            smp = [s for s in ((m.get("data") or {}).get("samples") or []) if isinstance(s, dict)]
            if m.get("data") is None or not smp:
                files[fname] = {"status": "no-samples", "samples": 0, "fails": []}
                continue
            if n not in BORDER_GROUP_OPS + DELETE_OPS:
                files[fname] = {"status": "not-replayed", "samples": len(smp), "fails": []}
                warns.append("X13 WARN {0}: {1} sample(s), no replayer for op {2!r} (only {3})".format(
                    fname, len(smp), n, list(BORDER_GROUP_OPS + DELETE_OPS)))
                continue
            ff = []
            for s in smp:
                outc, mm, det = (replay_delete_sample(m["path"], s, models, disable) if n in DELETE_OPS else
                                 replay_sample(m["path"], s, models))
                if log:
                    log("  X13 {0} {1}: {2} {3}".format(fname, s.get("raw"), outc, det if outc == "PASS" else mm))
                for fld, a, b in mm:
                    ff.append({"file": fname, "sample": s.get("raw"), "field": fld, "measured": a, "simulated": b})
            files[fname] = {"status": "FAIL" if ff else "PASS", "samples": len(smp), "fails": ff}
            fails += ff
        return {"files": files, "fails": fails, "warns": warns}
    finally:
        SS.cfw_border_rule = saved


def plan_ops(plan):
    return sorted(set(str(a.get("op")) for a in plan.get("actions") or [] if isinstance(a, dict) and a.get("op")))


def x13_gate(plans):
    """(ok, detail, warns) over stageplan/1 dicts: the union of their ops, one conformance run."""
    ops = sorted(set(o for p in plans for o in plan_ops(p)))
    c = opmodel_conformance(ops)
    det = c["fails"][:6] or "{0} op(s) {1}; files {2}".format(
        len(ops), ops, dict((k, "{0} ({1})".format(v["status"], v["samples"])) for k, v in c["files"].items()))
    return not c["fails"], det, c["warns"]


def _selftest_control_lint():
    """L7 plan passes; a synthetic queue plan refuses (and passes with data_stream+why); a synthetic edge-detector plan
    refuses (and a declared-counter variant passes). Prints gates + a RESULT line; returns rc."""
    import protocol as P
    gates = []

    def gate(label, ok, detail=""):
        gates.append((label, bool(ok), detail))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)
    for nm in ("stageplan_l7_split.json", "stageplan_k_split.json"):
        p = os.path.join(BENCH, nm)
        pl = json.load(open(p, encoding="utf-8"))
        cls, _t = _base_graph(pl)
        b = control_path_lint(pl)
        gate("C{0} real plan {1} (md5 {2}, {3} actions, base graph {4} objs) passes".format(
            1 if "l7" in nm else 2, nm, md5(p), len(pl["actions"]), len(cls)), not b and len(cls) > 0, b)
    q = {"schema": "stageplan/1", "actions": [
        {"op": "create", "id": "q_obt", "class": "Function", "name": "Obtain Queue", "diagram": 10, "as": "Q1"},
        {"op": "create", "id": "q_enq", "class": "Function", "name": "Enqueue Element", "diagram": 10, "as": "Q2"}]}
    b = control_path_lint(q, base=({}, {}))
    gate("C3 synthetic queue plan (Obtain + Enqueue, no data_stream) refuses both", len(b) == 2 and all(x.startswith("Q ") for x in b), b)
    b = control_path_lint({"actions": [{"op": "queue_node", "kind": "dequeue", "id": "qd"}]}, base=({}, {}))
    gate("C4 synthetic queue_node dequeue op refuses", len(b) == 1, b)
    q2 = json.loads(json.dumps(q))
    for a in q2["actions"]:
        a.update(data_stream=True, why="results FIFO to the file writer (master plan 1.7)")
    b = control_path_lint(q2, base=({}, {}))
    gate("C5 same queue plan with data_stream: true + why passes", not b, b)
    q3 = json.loads(json.dumps(q2))
    q3["actions"][0]["why"] = ""
    b = control_path_lint(q3, base=({}, {}))
    gate("C6 data_stream: true with an EMPTY why still refuses", len(b) == 1, b)
    e = {"schema": "stageplan/1", "actions": [
        {"op": "create", "id": "loc", "class": "Local", "name": "Focus Request", "diagram": 20, "as": "LV"},
        {"op": "add_shift_reg", "id": "sr_prev", "loop": 30, "body": 20, "as": "SRP"},
        {"op": "create", "id": "neq", "class": "Function", "name": "Not Equal?", "diagram": 20, "as": "NE",
         "terminals": [{"name": "x", "is_source": False}, {"name": "y", "is_source": False},
                       {"name": "x != y?", "is_source": True}]},
        {"op": "wire", "id": "w1", "src": "new:LV.value", "dst": "new:SRPR.inner"},
        {"op": "wire", "id": "w2", "src": "new:SRPL.inner", "dst": "new:NE.y"},
        {"op": "wire", "id": "w3", "src": "new:LV.value", "dst": "new:NE.x"}]}
    b = control_path_lint(e, base=({}, {}))
    gate("C7 synthetic edge detector (local -> SR, Not Equal?(current, previous)) refuses", len(b) == 1 and b[0].startswith("E "), b)
    e2 = json.loads(json.dumps(e))
    e2["actions"][3]["src"] = {"uid": "new:LV", "term": "value", "type": "u32"}
    e2["actions"][5]["src"] = {"uid": "new:LV", "term": "value", "type": "u32"}
    b = control_path_lint(e2, base=({}, {}))
    gate("C8 same shape on a declared u32 counter passes (the 1c'' prescribed reader)", not b, b)
    e3 = json.loads(json.dumps(e))
    e3["actions"][2].update(name="And", terminals=[{"name": "x", "is_source": False}, {"name": "y", "is_source": False},
                                                     {"name": "x .and. y?", "is_source": True}])
    e3["actions"][3]["src"] = e3["actions"][5]["src"] = {"uid": "new:LV", "term": "value", "type": "u32"}
    b = control_path_lint(e3, base=({}, {}))
    gate("C9 logic consumer (And of current, previous) refuses even when a type is declared", len(b) == 1, b)
    e4 = {"schema": "stageplan/1", "actions": [
        {"op": "add_shift_reg", "id": "sr", "loop": 30, "body": 20, "as": "SRP"},
        {"op": "wire", "id": "w1", "src": {"uid": 501, "term": "Focus Request"}, "dst": "new:SRPR.inner"},
        {"op": "wire", "id": "w2", "src": "new:SRPL.inner", "dst": {"uid": 502, "term": "y"}},
        {"op": "wire", "id": "w3", "src": {"uid": 501, "term": "Focus Request"}, "dst": {"uid": 502, "term": "x"}}]}
    b = control_path_lint(e4, base=({501: "Local", 502: "Comparison"}, {502: {"x", "y", "x != y?"}}))
    gate("C10 edge detector on BASE-graph uids (Local #501, Not Equal? by terminal names) refuses", len(b) == 1, b)
    npass = sum(1 for g_ in gates if g_[1])
    first = next((g_[0] + ": " + str(g_[2])[:120] for g_ in gates if not g_[1]), None)
    st = "PASS" if npass == len(gates) else "FAIL"
    print(P.result_line(P.make_result(npass, len(gates) - npass, first, status=st)), flush=True)
    return 0 if st == "PASS" else 1


def addr_offline(OG, end, is_source):
    """None if addressable offline, else the reason. Unwired terminals: owner node -> terminal list -> uid echo."""
    if not isinstance(end, dict) or not isinstance(end.get("uid"), int):
        return "end has no graph uid ({0!r}) - a created object needs a symbolic plan id".format(end)
    u = end["uid"]
    if u not in OG.cls:
        return "#{0} is not in the input graph (not symbolic: a re-typed or post-mutation uid)".format(u)
    rows, how = OG.term_rows(u)
    if not rows:
        return "#{0} ({1}) has no terminal list offline ({2})".format(u, OG.cls[u], how)
    if end.get("verify_term_uid"):
        r = [x for x in rows if int(x["term_uid"]) == int(end["verify_term_uid"])]
        if len(r) != 1 or not r[0]["wire_uid"]:
            return "verify_term_uid #{0} on #{1}: {2}".format(end["verify_term_uid"], u,
                                                             "absent" if not r else "UNWIRED - the uid path needs a wire")
    hits = [x for x in rows if x["term_name"] == end.get("term") and bool(x["is_source"]) == bool(is_source)]
    if len(hits) > 1:
        hits = [x for x in hits if not x["wire_uid"]]
    if len(hits) != 1:
        return "terminal {0!r} ({1}) on #{2} {3}: {4} matches; list {5}".format(
            end.get("term"), "src" if is_source else "sink", u, OG.cls[u], len(hits),
            sorted(set(x["term_name"] for x in rows))[:12])
    if end.get("term_uid") and int(end["term_uid"]) != int(hits[0]["term_uid"]):
        return "term_uid #{0} disagrees with name {1!r} -> #{2}".format(end["term_uid"], end.get("term"), hits[0]["term_uid"])
    if int(hits[0]["owner_uid"]) != u:
        return "uid echo {0} != #{1}".format(hits[0]["owner_uid"], u)
    return None


def lint(recipe, OG):
    src = open(recipe, encoding="utf-8").read()
    tree = ast.parse(src)
    doc = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Expr) and isinstance(getattr(n, "value", None), ast.Constant):
            doc.add(id(n.value))
    ints = sorted(set((n.value, n.lineno) for n in ast.walk(tree) if isinstance(n, ast.Constant) and
                      type(n.value) is int and n.value >= 100 and n.value in OG.cls))
    names = set()
    for u, _l in ints:
        names.update(r["term_name"] for r in OG.by_owner.get(u, []) if len(r["term_name"] or "") >= 2)
    strs = sorted(set((n.value, n.lineno) for n in ast.walk(tree) if isinstance(n, ast.Constant) and
                      isinstance(n.value, str) and id(n) not in doc and n.value in names))
    return ints, strs


# ------------------------------------------------------------------ card 106-3: X9 verb preconditions, X10 memory margin
ROW_DISPATCHERS = ("run_rows", "from_decision")      # card 110-7: the stagekit calls that turn a row's `copy` into copy_in


def recipe_dispatches_rows(recipe):
    """card 110-7 (F1, decided by judgement): True when the recipe's AST CALLS stagekit.run_rows / from_decision (as an
    attribute `x.run_rows(...)` or a bare name). Only such a recipe dispatches a decisions-row `copy` to copy_in; a recipe
    that calls neither (stage_replay_swap.py makes its byte copy with shutil.copyfile) dispatches no row. Unparsable
    recipe -> True (checked, never exempted)."""
    try:
        tree = ast.parse(REAL_OPEN(recipe, encoding="utf-8", errors="replace").read(), filename=recipe)
    except (OSError, SyntaxError, ValueError):
        return True
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if nm in ROW_DISPATCHERS:
                return True
    return False


def verb_preconditions(plans, sps, work, move_dst, stop_after=None, from_step=None, rows_dispatched=True):
    """X9 (retrospective-cycle102 `wrong-ordering`): every op / row the run DISPATCHES whose verb holds a precondition on
    the stage's own work file (stagexec.ROUTE_PRECONDITIONS: copy_in needs work == gscript.MOVE_DST) is checked OFFLINE
    against the Stage the dry run built. stageplan/1 files are read raw (checked even when stageplan_check refused them);
    decisions-row plans: every `copy` row (stagekit.run_rows -> copy_in) - only when rows_dispatched (card 110-7:
    recipe_dispatches_rows(recipe)); stageplan/1 ops are checked either way. -> list of failure strings."""
    import stagexec as SX
    ctx = {"work": work, "move_dst": move_dst}
    bad = []
    for p in plans:
        try:
            pl = json.load(open(p, encoding="utf-8"))
        except Exception as e:                                                     # noqa: BLE001
            bad.append("{0}: unreadable ({1})".format(rel(p), e))
            continue
        if p in sps:
            try:
                fl = SX.precondition_failures(pl, ctx, stop_after, from_step)
            except Exception as e:                                                 # noqa: BLE001
                bad.append("{0}: compile_plan failed, preconditions not evaluable ({1})".format(rel(p), str(e)[:160]))
                continue
            bad += ["{0}: op {1} {2} acts {3} ids {4}: needs {5}; work = {6}".format(
                os.path.basename(p), f["k"], f["route"], f["acts"], f["ids"], f["needs"], f["work"]) for f in fl]
        elif rows_dispatched:
            need, chk = SX.ROUTE_PRECONDITIONS["copy_in"]
            bad += ["{0}: row {1} copy: needs {2}; work = {3}".format(os.path.basename(p), r.get("id"), need, work)
                    for r in pl.get("decisions") or [] if r.get("action") == "copy" and not chk(ctx)]
    return bad


MODE_SA_RE = re.compile(r"--stop-after[\s=]+(\d+)")
MODE_FS_RE = re.compile(r"--from-step[\s=]+(\d+)")


def meter_records(recipe, log_dir=None):
    """X10's evidence: every run log of THIS recipe that carries a recorded per-op meter (stagexec.Meter's METER lines),
    newest first: [{path, mtime, stop_after, from_step, rows}]. A log is a run of the recipe when its first line is bgrun's
    `BGRUN START ...: <command>` and that command LAUNCHES the recipe (launched_stage_scripts; a dry/prerun names it only
    as an argument)."""
    import stagexec as SX
    base = os.path.basename(recipe).lower()
    out = []
    for p in glob.glob(os.path.join(log_dir or LOG_DIR, "*.log")):
        try:
            with REAL_OPEN(p, encoding="utf-8", errors="replace") as f:
                first = f.readline()
        except OSError:
            continue
        if not first.startswith("BGRUN START") or " min: " not in first:
            continue
        cmd = first.split(" min: ", 1)[1].strip()
        if not any(os.path.basename(x).lower() == base for x in launched_stage_scripts(cmd)):
            continue
        rows = SX.meter_rows_from_log(p)
        if rows:
            sa, fs = MODE_SA_RE.search(cmd), MODE_FS_RE.search(cmd)
            out.append({"path": p, "mtime": os.path.getmtime(p), "rows": rows,
                        "stop_after": int(sa.group(1)) if sa else None, "from_step": int(fs.group(1)) if fs else None})
    return sorted(out, key=lambda r: -r["mtime"])


# card 106-5 (PD219(c) DECIDED): a predicted checkpoint >= 690 MB FAILS X10 - LabVIEW error 2 was seen at 695 MB in cycle
# 85, so margin 0 against MEMSTOP 700 would pass a value above the error-2 point. mem_predict's rule is
# ok = peak < memstop - margin_mb, hence the default margin = MEMSTOP - 690 (700.0 - 10.0 = 690.0 exactly).
# card chat-S3 (PD328(a), user 2026-10-03 "메모리 낮추고"; error 2 measured at 704.8 MB, diag_chat_m1_mem.log:170-173):
# 690 -> 680 and MEMSTOP 700 -> 695 (margin 15). ONE SOURCE: memory_model.json `fail_above_mb` (the same value the X10
# model compares against, and stagexec.X10_FAIL_MB); no literal here.
X10_FAIL_MB = float(json.load(REAL_OPEN(os.path.join(BENCH, "memory_model.json"), encoding="utf-8"))["fail_above_mb"]["value"])


def mem_margin(recipe, stop_after=None, from_step=None, log_dir=None, records=None, margin_mb=None):
    """X10 (retrospective-cycle103 `inference-over-measurement`; PD216(f): 103-2 r1 crossed MEMSTOP 700 at 703.8 MB): the
    predicted private-MB peak of the planned run from the RECORDED per-op meter (stagexec.mem_predict). Evidence order:
    the newest record of the SAME mode (--stop-after / --from-step) that covers the window, recorded values; else the
    newest fresh-start record (no --from-step) that covers it, shifted to that record's own fresh-load read at k 0
    (`transfer`). ok None = no record covers the window (UNMEASURED - reported, not refused)."""
    import stagexec as SX
    if margin_mb is None:
        margin_mb = SX.MEM_STOP_MB - X10_FAIL_MB
    recs = meter_records(recipe, log_dir) if records is None else records
    for r in recs:
        if r["stop_after"] == stop_after and r["from_step"] == from_step:
            pr = SX.mem_predict(r["rows"], stop_after, from_step, None, SX.MEM_STOP_MB, margin_mb)
            if pr.get("covered"):
                return dict(pr, source=rel(r["path"]), how="same mode, recorded values")
    for r in recs:
        if r["from_step"] is None:
            k0 = [x["mb"] for x in r["rows"] if x["k"] == 0 and x["tag"] == "read"]
            pr = SX.mem_predict(r["rows"], stop_after, from_step, k0[0] if (from_step and k0) else None, SX.MEM_STOP_MB, margin_mb)
            if pr.get("covered"):
                return dict(pr, source=rel(r["path"]), how="transfer from a fresh-start record" + (
                    ", shifted to its fresh read k 0" if from_step else ""))
    return {"ok": None, "covered": False, "peak_mb": None, "memstop": SX.MEM_STOP_MB, "margin_mb": margin_mb,
            "why": "UNMEASURED: no recorded meter of {0} covers ops {1}..{2} ({3} record(s))".format(
                os.path.basename(recipe), int(from_step or 0) + 1, stop_after or "end", len(recs))}


# ------------------------------------------------------------------ card 130-1 (PD267(b)): X10 MODEL from the compiled plan
# retrospective-cycle129 device-failed: X10 passed the 40-op P3b-1 as UNMEASURED (stage_prerun_c129_1_p3b1_prerun.log:137)
# because it only read RECORDED meters. X10 now predicts every Executor the recipe builds in its dry run from the compiled
# plan + the checkpoint set it passes: peak = start + R*read + N*(edit + other) (coefficients ONLY from memory_model.json,
# each citing its log line); FAIL above fail_above_mb (675, PD266(b)); FAIL UNMEASURED when no Executor/plan compiles and
# no recorded meter covers the run. A recorded meter (mem_margin) still FAILS on its own >= 690 when it exists.
MEMORY_MODEL = os.path.join(BENCH, "memory_model.json")


class X10Probe(BaseException):
    """card 130-1: raised by the Executor capture in probe mode (D.x10_probe) - not an Exception, so stagekit.run's
    handlers do not swallow it; dry() catches it."""


def load_memory_model(path=None):
    m = json.load(REAL_OPEN(path or MEMORY_MODEL, encoding="utf-8"))
    for k in ("start_mb", "read_mb", "edit_mb", "other_mb", "final_read_mb", "fail_above_mb"):   # final_read_mb: card 132-1
        if not isinstance(m.get(k), dict) or not isinstance(m[k].get("value"), (int, float)) or not m[k].get("cite"):
            raise ValueError("memory_model {0}: needs {{value, cite}}".format(k))
    return m


def x10_capture_executors():
    """card 130-1: wrap stagexec.Executor.__init__ for the dry run - record plan path, compiled op kinds, checkpoints,
    stop_after, from_step (bound through the real signature, defaults applied). Returns the un-hook."""
    import inspect
    try:
        import stagexec as SX
    except Exception:                                                              # noqa: BLE001
        return lambda: None
    orig = SX.Executor.__init__
    sig = inspect.signature(orig)

    def cap(self, *a, **kw):
        rec = {"plan": None, "kinds": None, "checkpoints": None, "stop_after": None, "from_step": None, "error": None}
        try:
            b = sig.bind(self, *a, **kw)
            b.apply_defaults()
            cp = b.arguments.get("checkpoints")
            rec.update(plan=rel(str(b.arguments.get("plan_path"))), stop_after=b.arguments.get("stop_after"),
                       from_step=b.arguments.get("from_step"),
                       checkpoints=None if cp is None else sorted(int(k) for k in cp))
            pl = json.load(REAL_OPEN(os.path.abspath(str(b.arguments.get("plan_path"))), encoding="utf-8"))
            rec["kinds"] = [o["kind"] for o in SX.compile_plan(pl)]
        except Exception as e:                                                     # noqa: BLE001
            rec["error"] = "{0}: {1}".format(type(e).__name__, str(e)[:200])
        D.executors.append(rec)
        if D.x10_probe:
            raise X10Probe(rec["plan"])
        self._prerun_rec = rec                             # card 130-5: run_cap fills rec["run"] (PD268(b))
        return orig(self, *a, **kw)
    orig_run = SX.Executor.run

    def run_cap(self, *a, **kw):
        """card 130-5 (PD268(b)): record how far run() got. A dry run whose Executor stopped before its window's last op
        (ExecStop/SimError inside run, downgraded to UNVERIFIED by the recipe's E1) must FAIL, not PASS (c128b: 48 of 63)."""
        rec = getattr(self, "_prerun_rec", None)
        if rec is None:
            return orig_run(self, *a, **kw)
        first = int(self.from_step or 0)
        last = int(self.stop_after if self.stop_after is not None else len(self.ops))
        rr = {"called": True, "completed": False, "planned": max(0, last - first), "executed": 0, "stopped_in": None,
              "stop": None}
        rec["run"] = rr
        try:
            out = orig_run(self, *a, **kw)
            rr["completed"], rr["executed"] = True, rr["planned"]
            rec["partial"] = sorted(getattr(self, "reads_partial", None) or [])   # card chat-S4 B: per-owner reads, not R
            return out
        except BaseException as e:                                                 # noqa: BLE001 - recorded, re-raised
            rec["partial"] = sorted(getattr(self, "reads_partial", None) or [])
            cur = self.cur or {}
            rr["stopped_in"] = {"k": cur.get("k"), "op": cur.get("op"), "ids": cur.get("ids")}
            rr["executed"] = max(0, int(cur.get("k") or first) - 1 - first) if cur.get("k") else 0
            rr["stop"] = "{0}: {1}".format(type(e).__name__, str(e)[:240])
            raise
    SX.Executor.__init__ = cap
    SX.Executor.run = run_cap

    def unhook():
        SX.Executor.__init__ = orig
        SX.Executor.run = orig_run
    return unhook


def executor_stops(executors):
    """card 130-5 (PD268(b)): one FAIL text per Executor whose run() ended before its window's last op, or that was built
    and never run. [] when every Executor ran its whole window (or none was built)."""
    out = []
    for ex in executors or []:
        rr = ex.get("run")
        if ex.get("error"):
            continue                                       # not compilable: X10 reports it UNMEASURED
        if not rr:
            out.append("EXECUTOR-NOT-RUN {0}: built, run() never called - 0 ops executed".format(ex.get("plan")))
        elif not rr.get("completed"):
            out.append("EXECUTOR-STOP {0}: executed {1} of {2} ops, stopped IN op {3}: {4}".format(
                ex.get("plan"), rr.get("executed"), rr.get("planned"), rr.get("stopped_in"), rr.get("stop")))
    return out


def x10_start(vi_md5, model=None):
    """card 133-3 (PD283(b)(e)): (start_mb, cite) of a run whose INPUT VI has a measured load: load_by_vi[md5] + op0_read_mb
    (memory_model.json, each with its log citation). None when that VI's load was never measured (caller keeps start_mb)."""
    m = model or load_memory_model()
    L = (m.get("load_by_vi") or {}).get(str(vi_md5 or ""))
    op0 = m.get("op0_read_mb")
    if not L or not op0:
        return None
    return round(float(L["value"]) + float(op0["value"]), 1), "{0} + op-0 read {1} ({2}; {3})".format(
        L["value"], op0["value"], L["cite"], op0["cite"])


def x10_plan_start(plan_path, model=None):
    """card 133-3: the measured start of the Executor run of `plan_path`: its (finalized) base graph's `md5` = the input
    VI's md5 -> x10_start. None for a provisional base (its md5 is inherited from an older bed) or an unknown VI."""
    try:
        pl = json.load(REAL_OPEN(plan_path if os.path.isabs(plan_path) else os.path.join(ROOT, plan_path), encoding="utf-8"))
        b = (pl.get("finalized") or {}).get("base") or pl.get("base") or {}
        if (pl.get("base") or {}).get("provisional"):
            return None
        g = json.load(REAL_OPEN(b["path"] if os.path.isabs(b["path"]) else os.path.join(ROOT, b["path"]), encoding="utf-8"))
        return x10_start(g.get("md5"), model)
    except Exception:                                                              # noqa: BLE001
        return None


def x10_base_provisional(plan_path):
    """card 141-1: True when the plan's top-level base is provisional (a simulated graph, no measured VI load)."""
    try:
        pl = json.load(REAL_OPEN(plan_path if os.path.isabs(plan_path) else os.path.join(ROOT, plan_path), encoding="utf-8"))
    except Exception:                                                              # noqa: BLE001
        return False
    return bool((pl.get("base") or {}).get("provisional"))


def x10_model_peak(kinds, checkpoints, stop_after=None, from_step=None, model=None, start_mb=None, partial=None):
    """card 130-1 (PD267(b)): the predicted private-MB peak of ONE Executor run. N = ops dispatched (from_step+1 ..
    stop_after|end); R = whole-VI reads = {from_step|0} + the checkpoints in the window + the ops the Executor forces
    (every BIND_KINDS op and the last op, stagexec.py:1960); checkpoints None = a read after every op (R = N + 1).
    card 132-1 (PD275(a)): + final_read_mb ONCE per run - the run's last whole-VI read cost +17.4 MB measured
    (stage_d1_ring_p3b1_scratch_pin4.log:446-447; launch stage_d1_ring_p3b1.log:429-430) vs ~2.5 for a checkpoint read."""
    import stagexec as SX
    m = model or load_memory_model()
    first, last = int(from_step or 0), int(stop_after or len(kinds))
    win = range(first + 1, last + 1)
    if checkpoints is None:
        reads = set([first]) | set(win)
    else:
        reads = (set([first]) | set(k for k in checkpoints if first < k <= last)
                 | set(k for k in win if kinds[k - 1] in SX.BIND_KINDS) | set([last]))
    # card chat-S4 B (user 2026-10-03): checkpoints the Executor read PER OWNER (Executor(partial_reads=True), its dry run's
    # reads_partial) are not whole-VI reads: R counts only the whole ones; each partial read costs part_read_mb (memory_model,
    # 0.0 until measured). The session start (k = from_step|0) and the last op are always whole (Executor.run).
    part = set(int(k) for k in (partial or ()) if first < int(k) < last) & reads
    reads = reads - part
    N, R = len(win), len(reads)
    v = lambda k: float(m[k]["value"])                                             # noqa: E731
    pv = float((m.get("part_read_mb") or {}).get("value") or 0.0)
    st = float(start_mb) if start_mb is not None else v("start_mb")              # card 133-3: measured start of the input VI
    peak = round(st + R * v("read_mb") + len(part) * pv + N * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)
    return {"N": N, "R": R, "P": len(part), "bind": sum(1 for k in win if kinds[k - 1] in SX.BIND_KINDS), "peak_mb": peak, "start_mb": st,
            "fail_above_mb": v("fail_above_mb"), "ok": peak <= v("fail_above_mb"),
            "checkpoints": "every op" if checkpoints is None else sorted(reads)}


# card 132-4 (PD277(a), gate-fp fp-29): a script with NO Executor plan and 0 edit ops is a READ-ONLY reader; X10 models it as
# N = 0, R = 1 (the load, k 0) + its whole-VI read call sites, + final_read_mb once; FAIL > fail_above_mb (690). A script
# with ANY edit op (dry trace: a Stage._op, a mutating stub call, a wire/delete/RLE verb; source: a MODIFY_VERBS call other
# than discard_work = close without save, or a create/wire/delete/save-named call) and no Executor stays UNMEASURED = FAIL.
X10_RO_READS = frozenset(("read_live", "live_graph", "census", "uid_index"))   # whole-VI reads (wiki_build / stagekit)
X10_RO_EDIT_RE = re.compile(r"create|connect|wire|delete|remove_loose|fs_inner|move_in|loop_in|save|copy_in|add_s|"
                            r"const_row|plan_rows|from_decision|junk|purge|relink|set_(visible|control|default)", re.I)
# (str.replace / list.insert / list.remove are not edit verbs: sys.path.insert is in every bench script)


def x10_readonly(recipe, trace):
    """card 132-4 (PD277(a)): (ok, detail). ok True iff the dry trace shows no Executor, no Stage._op, no mutating stub
    call AND the source (ast) calls no edit verb; detail carries reads (whole-VI read call sites) or the reasons it is not
    read-only. A whole-VI read inside a loop body cannot be counted offline -> not modelled (stays UNMEASURED)."""
    why = []
    tr = trace or {}
    if tr.get("executors"):
        why.append("Executor plan present")
    if tr.get("ops"):
        why.append("dry ran {0} Stage._op edit op(s) {1}".format(len(tr["ops"]), sorted(set(tr["ops"]))[:6]))
    if tr.get("first_mutation"):
        why.append("dry mutation {0}".format(tr["first_mutation"]))
    try:
        tree = ast.parse(REAL_OPEN(recipe, encoding="utf-8", errors="replace").read(), filename=recipe)
    except (OSError, SyntaxError, ValueError) as e:
        return False, {"why": ["source unreadable: {0}".format(e)]}
    edits = set()
    for n in ast.walk(tree):
        if not isinstance(n, ast.Call):
            continue
        f = n.func
        name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
        if not name or name == "discard_work":
            continue
        if name in MODIFY_VERBS or X10_RO_EDIT_RE.search(name) or (WIRE_VERB_RE.search(name)):
            edits.add(name)
    if edits:
        why.append("source calls edit verb(s) {0}".format(sorted(edits)))
    sr = x10_source_reads(recipe)                          # card 138-2 (PD299(b)): call sites x times each site runs
    loop_u = [u for u in sr["unbounded"] if "inside a loop" in u]
    if loop_u:
        why.append("{0} whole-VI read(s) inside a loop body (count not offline): {1}".format(len(loop_u), loop_u[:4]))
    other_u = [u for u in sr["unbounded"] if u not in loop_u]
    if other_u:
        why.append("{0} whole-VI read call site(s) not bounded offline: {1}".format(len(other_u), other_u[:4]))
    return (not why), {"why": why, "reads": sr["reads"], "source": sr}


# card 136-2 (gate-fp fp-33): a stagekit EDIT diagnostic (dry trace: Stage._op edit ops, no stagexec.Executor) is MODELLED
# from its dry trace in the Executor model's terms: N = the dry's Stage._op ops, R = 1 (k 0) + the whole-VI reads the dry
# EXECUTED (X10_EDIT_READS names in D.calls), start = the MEASURED load of the opened VI (input md5 -> x10_start, the
# x10_plan_start rule) + op-0 read; peak = start + R*read + N*(edit + other) + final_read; FAIL > fail_above_mb (690).
# UNMEASURED (FAIL) when the opened VI's load is not in memory_model.json load_by_vi or the trace has no op / read count.
# Reads a script skips in its DRY branch (e.g. census_snapshot / read_terms behind `if DRY`) are not seen by this count.
X10_EDIT_READS = X10_RO_READS | frozenset(("read_terms",))     # + allterms.read_terms: every terminal of the VI

# card 138-2 (PD299(b), retrospective-cycle136 device-failed): R is counted from the recipe SOURCE, not from what the dry
# executes - the dry skips DRY-guarded reads (stagekit.census_snapshot returns {} in a dry, stagekit.py:263-267), so a
# dry-counted R undercounted (3 vs ~50 call sites). Every call site of a whole-VI read (X10_SRC_READS) counts x the number
# of times its enclosing function/lambda is called (summed over THAT function's call sites, recursively; a function passed
# to a known call-once caller counts once: stagekit.run(body), Stage._op(verb, fn) and Stage.safe(label, fn), each calling
# fn exactly once, stagekit.py:298-300, :587-592). A read inside a loop, a lambda/function passed to any OTHER call or used
# as a value, or recursion is UNBOUNDED -> X10 UNMEASURED (FAIL), never counted once. A for loop's `iter` and a
# comprehension's first generator `iter` run once. Both branches of an `if DRY` count (upper bound).
_X10_ONCE_CALLERS = frozenset(("run", "_op", "safe"))
X10_SRC_READS = X10_EDIT_READS | frozenset(("census_snapshot", "report_all"))   # + stagekit census_snapshot / gscript report_all
X10_SESSION_STARTS = frozenset(("start", "restart"))                            # Stage.start (fresh LabVIEW) / Stage.restart
_X10_LOOPS = (ast.For, ast.AsyncFor, ast.While, ast.ListComp, ast.GeneratorExp, ast.SetComp, ast.DictComp)
_X10_ITER_CALLS = frozenset(("map", "filter", "sorted", "min", "max", "reduce", "sum", "any", "all", "list", "tuple", "set",
                             "dict", "zip", "enumerate"))


class _X10Unbounded(Exception):
    pass


def _x10_name(f):
    return f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)


def x10_source_reads(recipe, names=X10_SRC_READS):
    """card 138-2 (PD299(b)): the recipe's whole-VI reads counted from its SOURCE. Returns {"reads": n | None (None = some
    site unbounded), "sites": [{line, read, times}], "unbounded": [text], "sessions": n | None, "session_sites": [...]}.
    `sessions` = Stage.start/restart call sites x times (each a fresh LabVIEW); with more than one session the reads are
    NOT split per session - the total is the per-session upper bound (said in `per_session`)."""
    try:
        tree = ast.parse(REAL_OPEN(recipe, encoding="utf-8", errors="replace").read(), filename=recipe)
    except (OSError, SyntaxError, ValueError) as e:
        return {"reads": None, "sites": [], "unbounded": ["source unreadable: {0}".format(e)], "sessions": None,
                "session_sites": [], "per_session": None}
    parent = {}
    for n in ast.walk(tree):
        for c in ast.iter_child_nodes(n):
            parent[c] = n
    defs = {}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            defs.setdefault(n.name, []).append(n)
        elif (isinstance(n, ast.Assign) and isinstance(n.value, ast.Lambda) and len(n.targets) == 1
              and isinstance(n.targets[0], ast.Name)):
            defs.setdefault(n.targets[0].id, []).append(n.value)
    fn_name = dict((id(d), nm) for nm, ds in defs.items() for d in ds)
    calls_by, refs_by = {}, {}

    def shadowed(nm_node):
        """a Name that an enclosing def/lambda binds as a PARAMETER is that local, not the module function
        (diag_c136_1_routes.py:58-59 `def stop(loop, body, ...)` vs `def body(_)`)."""
        p = parent.get(nm_node)
        while p is not None:
            if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                a = p.args
                names_ = set(x.arg for x in a.posonlyargs + a.args + a.kwonlyargs)
                names_ |= set(x.arg for x in (a.vararg, a.kwarg) if x is not None)
                if nm_node.id in names_:
                    return True
            p = parent.get(p)
        return False
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and _x10_name(n.func) in defs:
            if isinstance(n.func, ast.Name) and shadowed(n.func):
                continue
            calls_by.setdefault(_x10_name(n.func), []).append(n)
        elif isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load) and n.id in defs and not shadowed(n):
            p = parent.get(n)
            if not (isinstance(p, ast.Call) and p.func is n):
                refs_by.setdefault(n.id, []).append(n)
    memo = {}

    def scope(node):
        """(innermost enclosing def/lambda | None, the first loop between them | None). Evaluated ONCE, so not a loop: a
        for loop's `iter` and a comprehension's FIRST generator's `iter` (`dict(... for u in s.census_snapshot()...)`)."""
        loop, c, p, once = None, node, parent.get(node), None
        while p is not None:
            if isinstance(p, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
                return p, loop
            if isinstance(p, ast.comprehension) and c is p.iter:
                once = p                                   # reached the comprehension node next: once iff generators[0]
            elif loop is None and isinstance(p, _X10_LOOPS):
                first_iter = (isinstance(p, (ast.For, ast.AsyncFor)) and c is p.iter) or (
                    not isinstance(p, (ast.For, ast.AsyncFor, ast.While)) and once is not None and c is once
                    and p.generators and p.generators[0] is once)
                if not first_iter:
                    loop = p
            c, p = p, parent.get(p)
        return None, loop

    def site(node, stack):
        sc, loop = scope(node)
        if loop is not None:
            raise _X10Unbounded("line {0}: inside a loop body ({1} at line {2})".format(
                node.lineno, type(loop).__name__, loop.lineno))
        return 1 if sc is None else mult(sc, stack)

    def mult(fn, stack):
        if id(fn) in memo:
            return memo[id(fn)]
        if id(fn) in stack:
            raise _X10Unbounded("line {0}: recursion".format(fn.lineno))
        stack = stack | frozenset([id(fn)])
        name = fn_name.get(id(fn))
        if name is None:                                   # an anonymous lambda: runs where it is passed
            p = parent.get(fn)
            kw = None
            if isinstance(p, ast.keyword):
                kw, p = p.arg, parent.get(p)
            if not isinstance(p, ast.Call) or p.func is fn:
                raise _X10Unbounded("line {0}: lambda used as a value (call count not offline)".format(fn.lineno))
            if kw == "key" or _x10_name(p.func) in _X10_ITER_CALLS:
                raise _X10Unbounded("line {0}: lambda passed to {1}(key={2}) runs per item".format(
                    fn.lineno, _x10_name(p.func), kw))
            if _x10_name(p.func) not in _X10_ONCE_CALLERS:
                raise _X10Unbounded("line {0}: lambda passed to {1}() (not a known call-once caller {2})".format(
                    fn.lineno, _x10_name(p.func), sorted(_X10_ONCE_CALLERS)))
            k = site(p, stack)
        else:
            k, n_sites = 0, 0
            for c in calls_by.get(name, []):
                k += site(c, stack)
                n_sites += 1
            for r in refs_by.get(name, []):
                p = parent.get(r)
                if isinstance(p, ast.Call) and _x10_name(p.func) in _X10_ONCE_CALLERS and r in p.args:
                    k += site(p, stack)                    # K.run(body, st) / s._op(verb, fn) / s.safe(label, fn): once
                    n_sites += 1
                else:
                    raise _X10Unbounded("line {0}: function {1} used as a value (call count not offline)".format(
                        r.lineno, name))
            if not n_sites:
                k = 1                                      # never called in this file: counted once (upper bound)
        memo[id(fn)] = k
        return k

    def count(want, attr_only=False):
        out, unb, total = [], [], 0
        for n in ast.walk(tree):
            if not isinstance(n, ast.Call) or _x10_name(n.func) not in want:
                continue
            if attr_only and not isinstance(n.func, ast.Attribute):
                continue
            try:
                k = site(n, frozenset())
                out.append({"line": n.lineno, "read": _x10_name(n.func), "times": k})
                total += k
            except _X10Unbounded as e:
                unb.append("{0} {1}".format(_x10_name(n.func), e))
        return out, unb, total
    sites, unb, total = count(names)
    ss, sunb, stot = count(X10_SESSION_STARTS, attr_only=True)
    sessions = None if sunb else stot
    return {"reads": None if unb else total, "sites": sorted(sites, key=lambda s: s["line"]), "unbounded": unb,
            "sessions": sessions, "session_sites": ss + [{"unbounded": u} for u in sunb],
            "per_session": None if unb else ("{0} (one session)".format(total) if (sessions or 0) <= 1 else
                                            "<= {0} (total over {1} sessions, not split)".format(total, sessions))}


def x10_reads_line(src, dry_n=None):
    """card 138-2: one printable line - source count (+ sites), dry count, unbounded sites."""
    return "source {0} [{1}]{2}; dry executed {3}; sessions {4}".format(
        src.get("reads") if src.get("reads") is not None else "UNBOUNDED",
        ", ".join("{0}@{1}x{2}".format(s["read"], s["line"], s["times"]) for s in src.get("sites", [])),
        (" unbounded " + "; ".join(src["unbounded"][:4])) if src.get("unbounded") else "",
        dry_n if dry_n is not None else "n/a", src.get("sessions"))


def x10_edit(recipe, trace, model):
    """card 136-2 (fp-33): (run dict | None, why | None). why None = not an edit trace (no ops: the caller's text stands)."""
    tr = trace or {}
    if tr.get("executors") or not tr.get("ops"):
        return None, None
    xs = x10_start(tr.get("input_md5"), model)
    if xs is None:
        return None, "edit model: opened VI load unmeasured (md5 {0} not in memory_model load_by_vi)".format(tr.get("input_md5"))
    if not isinstance(tr.get("x10_reads"), list):
        return None, "edit model: dry trace carries no whole-VI read count (x10_reads)"
    src = x10_source_reads(recipe)                       # card 138-2 (PD299(b)): the SOURCE count, never the smaller one
    if src["reads"] is None:
        return None, "edit model: whole-VI read count not bounded from the source ({0})".format("; ".join(src["unbounded"][:4]))
    v = lambda k: float(model[k]["value"])                                         # noqa: E731
    dry_n = len(tr["x10_reads"])
    used = max(src["reads"], dry_n)
    N, R = len(tr["ops"]), 1 + used
    peak = round(xs[0] + R * v("read_mb") + N * (v("edit_mb") + v("other_mb")) + v("final_read_mb"), 1)
    rc = {}
    for n in tr["x10_reads"]:
        rc[n] = rc.get(n, 0) + 1
    return {"plan": "edit diagnostic " + rel(recipe), "edit": True, "N": N, "R": R, "bind": 0, "peak_mb": peak,
            "start_mb": xs[0], "start_source": xs[1], "fail_above_mb": v("fail_above_mb"), "ok": peak <= v("fail_above_mb"),
            "src_reads": src["reads"], "dry_reads": dry_n, "reads_line": x10_reads_line(src, dry_n),
            "checkpoints": "k 0 + {0} whole-VI read(s) = max(source {1}, dry executed {2} {3})".format(
                used, src["reads"], dry_n, rc)}, None


# card chat-M2 (gate-fp fp-35, user 2026-10-03 option (나)): ONE narrow release. A MEMORY-CEILING PROBE must loop its
# whole-VI reads and is MEANT to cross 690 MB, so no X10 model can pass it (chat-M1 BLOCKED, diag_chat_m1_prerun.log:71-72).
# A script that declares the module-level literal X10_PROBE = X10_PROBE_LITERAL passes X10 as PROBE-EXEMPT ONLY IF its dry
# trace + source show ALL of: no stagexec.Executor (a probe is not a build); the K1 input-md5 gate passed and every Stage work
# path is a dated byte copy in claudeDev (never the input VI); every work path was declared a scratch (Stage.discard_work, so
# Stage.close deletes it); NO save call in the dry trace and NO save-named call in the source (scratch deletion is
# Stage.close's drop_scratch, not a save); a warn-only meter (`<name> = ...Meter(..., stop_mb=None, ...)`) that is CALLED.
# Anything else carrying the literal FAILS X10 (never falls through to the models); no literal = behaviour unchanged.
X10_PROBE_LITERAL = "memory ceiling, scratch only"
X10_SAVE_RE = re.compile(r"save", re.I)


def x10_probe_release(recipe, trace):
    """card chat-M2 (fp-35): (declared, ok, detail). declared False = no X10_PROBE literal (the caller's rules stand)."""
    try:
        tree = ast.parse(REAL_OPEN(recipe, encoding="utf-8", errors="replace").read(), filename=recipe)
    except (OSError, SyntaxError, ValueError):
        return False, False, {}
    declared = any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "X10_PROBE" for t in n.targets)
                   for n in tree.body)
    if not declared:
        return False, False, {}
    why, facts = [], []
    lit = [n.value.value for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)
           and any(isinstance(t, ast.Name) and t.id == "X10_PROBE" for t in n.targets)]
    if lit != [X10_PROBE_LITERAL]:
        why.append("X10_PROBE must be the module-level literal {0!r} (got {1!r})".format(X10_PROBE_LITERAL, lit))
    tr = trace or {}
    if tr.get("executors"):
        why.append("a stagexec.Executor plan is present (a probe is not a build)")
    if not tr.get("input_md5") or not tr.get("input_vi"):
        why.append("dry trace has no Stage input VI/md5 (K1 byte-copy gate not run)")
    if any("K1" in str(f) for f in tr.get("fails") or []):
        why.append("K1 input md5 gate failed in the dry")
    norm = lambda p: os.path.normcase(os.path.abspath(str(p)))                     # noqa: E731
    works = tr.get("works") or []
    if not works:
        why.append("no Stage work copy in the dry trace")
    for w in works:
        if tr.get("input_vi") and norm(w) == norm(tr["input_vi"]):
            why.append("work path IS the input VI {0}".format(w))
        if os.path.basename(os.path.dirname(str(w))).lower() != "claudedev":
            why.append("work path {0} is not a copy in claudeDev".format(w))
        if norm(w) not in set(norm(d) for d in tr.get("discards") or []):
            why.append("work path {0} not declared a scratch (Stage.discard_work not called)".format(w))
    if not isinstance(tr.get("saves"), list):
        why.append("dry trace carries no save-call record")
    elif tr["saves"]:
        why.append("dry executed save call(s) {0}".format(sorted(set(tr["saves"]))[:6]))
    src_saves, meters, called = set(), [], set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            nm = _x10_name(n.func)
            if nm and X10_SAVE_RE.search(nm):
                src_saves.add(nm)
            if isinstance(n.func, ast.Name):
                called.add(n.func.id)
        if (isinstance(n, ast.Assign) and isinstance(n.value, ast.Call) and _x10_name(n.value.func) == "Meter"
                and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)):
            kw = dict((k.arg, k.value) for k in n.value.keywords)
            warn_only = isinstance(kw.get("stop_mb"), ast.Constant) and kw["stop_mb"].value is None
            meters.append((n.targets[0].id, warn_only, n.lineno))
    if src_saves:
        why.append("source calls save-named function(s) {0}".format(sorted(src_saves)))
    live = [m_ for m_ in meters if m_[1] and m_[0] in called]
    if not live:
        why.append("no warn-only meter (`X = ...Meter(..., stop_mb=None)` that is called) in the source {0}".format(meters))
    else:
        facts.append("warn-only meter {0} (line {1}) called".format(live[0][0], live[0][2]))
    facts.append("works {0}, discarded {1}, dry saves {2}, input md5 {3}".format(
        [os.path.basename(str(w)) for w in works], len(tr.get("discards") or []), len(tr.get("saves") or []),
        tr.get("input_md5")))
    return True, not why, {"why": why, "facts": facts}


def x10_gate(recipe, executors, stop_after=None, from_step=None, model=None, trace=None):
    """card 130-1 (PD267(b)): (ok, detail dict). ok False = a predicted peak > fail_above_mb, or UNMEASURED (no Executor
    whose plan compiled AND no covering recorded meter), or a recorded meter >= 690 (mem_margin, kept).
    card 132-4 (PD277(a)): with `trace` (the dry result), a read-only script (x10_readonly) is MODELLED, not UNMEASURED.
    card chat-M2 (fp-35): a declared memory-ceiling probe (x10_probe_release) is PROBE-EXEMPT or FAILS, nothing else."""
    if trace is not None:
        declared, p_ok, p_det = x10_probe_release(recipe, trace)
        if declared:
            if p_ok:
                return True, {"why": "PROBE-EXEMPT: declared memory-ceiling probe, scratch only, no save, warn-only meter ("
                              + "; ".join(p_det["facts"]) + ")", "runs": [], "probe": p_det}
            return False, {"why": "X10_PROBE declared but NOT exempt: " + "; ".join(p_det["why"]), "runs": [],
                           "probe": p_det}
    try:
        m = model or load_memory_model()
    except Exception as e:                                                         # noqa: BLE001
        return False, {"why": "UNMEASURED: memory model unreadable ({0})".format(e)}
    runs, bad, bad_ro = [], [], None
    if not executors and trace is not None:
        ro_ok, ro = x10_readonly(recipe, trace)
        if ro_ok:
            v = lambda k: float(m[k]["value"])                                     # noqa: E731
            dry_n = len(trace["x10_reads"]) if isinstance(trace.get("x10_reads"), list) else 0
            used = max(int(ro["reads"]), dry_n)                   # card 138-2: never the smaller of source / dry
            R = 1 + used
            peak = round(v("start_mb") + R * v("read_mb") + v("final_read_mb"), 1)
            runs.append({"plan": "read-only " + rel(recipe), "N": 0, "R": R, "bind": 0, "peak_mb": peak,
                         "fail_above_mb": v("fail_above_mb"), "ok": peak <= v("fail_above_mb"),
                         "src_reads": ro["reads"], "dry_reads": dry_n, "reads_line": x10_reads_line(ro["source"], dry_n),
                         "checkpoints": "k 0 + {0} whole-VI read call site(s)".format(used)})
        else:
            bad_ro = "not read-only: " + "; ".join(ro["why"])
            er, ewhy = x10_edit(recipe, trace, m)                              # card 136-2 (fp-33): edit diagnostic
            if er:
                runs.append(er)
            elif ewhy:
                bad_ro += "; " + ewhy
    src = x10_source_reads(recipe) if executors else None    # card 138-2 (PD299(b)): the script's own whole-VI reads
    if src is not None and src["reads"] is None:
        bad.append("script whole-VI read count not bounded from the source ({0})".format("; ".join(src["unbounded"][:4])))
    dry_n = len(trace["x10_reads"]) if isinstance((trace or {}).get("x10_reads"), list) else None
    for ex in executors or []:
        if ex.get("error") or not ex.get("kinds"):
            bad.append("{0}: plan/checkpoint set not compilable ({1})".format(ex.get("plan"), ex.get("error")))
            continue
        if ex.get("plan") and x10_base_provisional(ex["plan"]):
            # card 141-1 (review c140-2-failed-logs, retrospective-cycle140): a PROVISIONAL base (stagesim's simulated end of
            # the previous session) has no measured input load - x10_plan_start returns None for it (:1997-1998) and the run
            # used to fall back to the model's start_mb. REFUSED instead: --rebase onto the real graph first.
            bad.append("{0}: base is PROVISIONAL - input VI load not measured; X10 refuses (no fallback to the model start_mb; "
                       "--rebase onto the real graph first)".format(ex.get("plan")))
            continue
        sa = ex.get("stop_after") if ex.get("stop_after") is not None else stop_after
        fs = ex.get("from_step") if ex.get("from_step") is not None else from_step
        xs = x10_plan_start(ex.get("plan"), m) if ex.get("plan") else None     # card 133-3: measured load of the input VI
        r_ = dict(x10_model_peak(ex["kinds"], ex.get("checkpoints"), sa, fs, m, start_mb=xs[0] if xs else None,
                                 partial=ex.get("partial")),
                  plan=ex.get("plan"), start_source=xs[1] if xs else "model start_mb (input VI load not measured)")
        # card 138-2: + the script's source-counted whole-VI reads (around the Executor, same LabVIEW session) at read_mb
        # each. exec_peak_mb keeps the Executor-only figure (what a METER inside the run measures; selftest pins).
        sr = (src or {}).get("reads") or 0
        r_.update(exec_R=r_["R"], exec_peak_mb=r_["peak_mb"], src_reads=(src or {}).get("reads"), dry_reads=dry_n,
                  reads_line=x10_reads_line(src or {}, dry_n), R=r_["R"] + sr,
                  peak_mb=round(r_["peak_mb"] + sr * float(m["read_mb"]["value"]), 1))
        r_["ok"] = r_["peak_mb"] <= r_["fail_above_mb"]
        runs.append(r_)
    mm = mem_margin(recipe, stop_after, from_step)
    det = {"model": rel(MEMORY_MODEL), "runs": runs, "not_compiled": bad,
           "recorded": dict((k, mm.get(k)) for k in ("ok", "peak_mb", "source", "why") if mm.get(k) is not None)}
    if bad or (not runs and mm["ok"] is None):
        det["why"] = "UNMEASURED: " + ("; ".join(bad) if bad else
                                       "no stagexec.Executor plan in the dry run and no recorded meter covers the run"
                                       + (" (" + bad_ro + ")" if bad_ro else ""))
        return False, det
    det["peak_mb"] = max([r["peak_mb"] for r in runs] or [mm.get("peak_mb") or 0])
    return all(r["ok"] for r in runs) and mm["ok"] is not False, det


def x10_probe(recipe, graph=None):
    """card 130-1 self-test helper: dry-run the recipe only up to its first Executor (probe) and return the records."""
    D.__init__()
    D.x10_probe = True
    try:
        dry(recipe, graph)
    finally:
        builtins.open = REAL_OPEN
        D.x10_probe = False
    return list(D.executors)


DELETE_VERB_RE = re.compile(r"^delete_(object|wire)$")    # card 115-3 F1: counted against plan DELETE rows, not wire rows
RLE_VERB_RE = re.compile(r"^wire_remove_loose_ends$")     # card 128-4 (PD261(b)): counted against plan RLE rows


def x5_count(verbs, rows, spc, stop_after=None, from_step=None):
    """X5 (moved out of prerun unchanged, card 115-3 F1): (ok, detail). Wire-making verbs the dry run executed ==
    plan `wire` decision rows + the stageplans' compiled wiring real ops (in the PART-A/PART-B window), and those ops
    cover every `wire` action once. NARROWED by card 115-3 (JUDGEMENT, 115-2 BLOCKED on stage_prerun.py:103, where
    WIRE_VERB_RE matched `delete_wire`): the verbs delete_object / delete_wire leave the wire-making count and are
    counted 1:1, per kind, against the plan's DELETE rows (decision rows with that action + compiled delete ops in the
    same window). An unplanned op of either kind still FAILS."""
    # card 128-4 (PD261(b), gate-fp X5): `wire_remove_loose_ends` matched WIRE_VERB_RE while SP_WIRING (:901) leaves
    # it out, so P3b's 15 RLE ops were counted against 26 wiring rows (41 vs 26, diag_c128_3_x5.log M1). RLE ops now
    # leave the wiring count and are counted 1:1 against the plan's RLE rows (compiled RLE ops in the same window),
    # exactly as DELETE ops are (card 115-3). An unplanned RLE op still FAILS.
    wires = [r for r in rows if r.get("action") == "wire"]
    ops = [v for v in verbs if WIRE_VERB_RE.search(v) and not DELETE_VERB_RE.search(v) and not RLE_VERB_RE.search(v)]
    rgot = sum(1 for v in verbs if RLE_VERB_RE.search(v))
    rwant = sum(1 for r in rows if RLE_VERB_RE.search(str(r.get("action") or "")))
    dgot = collections.Counter(v for v in verbs if DELETE_VERB_RE.search(v))
    dwant = collections.Counter(r["action"] for r in rows if DELETE_VERB_RE.search(str(r.get("action") or "")))
    # card 79-6: a stageplan's wire actions are executed as stagexec real ops (a tunnel op carries its two border
    # wires); expected = compiled wiring ops, AND those ops must cover every `wire` action of the plan exactly once
    sp_wops, sp_wact, sp_cov = 0, 0, 0
    for p, (_ok, _d, pl, ops_) in spc.items():
        A = (pl or {}).get("actions") or []
        wa = set(i for i, a in enumerate(A, 1) if a.get("op") == "wire")
        wo = [o for o in (ops_ or []) if o["kind"] in SP_WIRING]
        so = [o for o in (ops_ or []) if o["kind"] in SP_WIRE_OTHER]
        # card 103-2: PART-A mode expects only the wiring ops the run dispatches (op index k <= stop_after)
        # card 103-4: PART-B mode (`--from-step k`) expects only the wiring ops k+1.. the run dispatches
        win = [o for k, o in enumerate(ops_ or [], 1) if k <= int(stop_after or len(ops_ or []))
               and k > int(from_step or 0)]
        wk = wo if stop_after is None and from_step is None else [o for o in win if o["kind"] in SP_WIRING]
        dwant.update(o["kind"] for o in win if DELETE_VERB_RE.search(o["kind"]))
        rwant += sum(1 for o in win if RLE_VERB_RE.search(o["kind"]))
        sp_wops, sp_wact = sp_wops + len(wk), sp_wact + len(wa)
        sp_cov += len(wa & set(x for o in wo + so for x in o["acts"]))
    ok = len(ops) == len(wires) + sp_wops and sp_cov == sp_wact and dgot == dwant and rgot == rwant
    return ok, ("ops {0} vs plan wire rows {1} + stageplan wiring real ops {2}{5} (covering {3}/{4} wire actions); "
                "delete ops {6} vs plan delete rows {7}; RLE ops {8} vs plan RLE rows {9}").format(
        len(ops), len(wires), sp_wops, sp_cov, sp_wact,
        ("" if stop_after is None else " among ops 1..{0} (PART-A stop_after)".format(int(stop_after))) +
        ("" if from_step is None else " among ops {0}.. (PART-B from_step)".format(int(from_step) + 1)),
        dict(sorted(dgot.items())), dict(sorted(dwant.items())), rgot, rwant)


# card 123-7 (PD247(e), brief_123-5.md STEP 3): the CENSUS hook-in. tools/census_predict.py derives each stageplan row's
# class delta from measured samples (tools/bench/census_samples.json) and compares the sum with the `census` block of the
# plan's prediction file `<plan>_pred.json`. derived != declared -> prerun FAIL (one line: class, derived, declared);
# CENSUS-UNPREDICTED -> an ADVISORY line, prerun verdict unchanged, but --scratch-required exits 3 (an unmeasured census cannot
# skip the scratch run that measures it). No prediction file / no census block -> INFO only.
def census_check(plan_path, pred_path=None, samples_path=None):
    """-> None (no prediction file beside the plan) or {'plan', 'pred', 'overall', 'fails': [(cls, derived, declared)],
    'unpredicted': [rows], 'rep'}."""
    import census_predict as CP
    pred_path = pred_path or (plan_path[:-5] + "_pred.json" if plan_path.endswith(".json") else None)
    if not pred_path or not os.path.isfile(pred_path):
        return None
    with open(plan_path, encoding="utf-8") as f:
        plan = json.load(f)
    with open(pred_path, encoding="utf-8") as f:
        pred = json.load(f)
    with open(samples_path or CP.DEFAULT_SAMPLES, encoding="utf-8") as f:
        samples = json.load(f)
    rep = CP.predict(plan, pred, samples)
    return {"plan": rel(plan_path), "pred": rel(pred_path), "overall": rep["overall"], "rep": rep,
            "fails": [(p["class"], p["derived"], p["declared"]) for p in rep["classes"] if p["verdict"] == "FAIL"],
            "unpredicted": rep["unpredicted"]}


def census_gate(plan_paths, pred_override=None, samples_path=None, out=print):
    """(ok, detail, lines). ok False only on a derived != declared class (CENSUS FAIL). Prints one line per plan:
    'CENSUS FAIL <plan> <class> derived +d declared +x' / 'ADVISORY CENSUS-UNPREDICTED <plan> rows [..]' / 'INFO ...'."""
    ok, det, lines = True, [], []
    for p in plan_paths:
        c = census_check(p, (pred_override or {}).get(p), samples_path)
        if c is None:
            lines.append("INFO  CENSUS no prediction file beside {0}".format(rel(p)))
        elif c["overall"] == "FAIL":
            ok = False
            for cls, d, x in c["fails"]:
                lines.append("CENSUS FAIL {0} {1} derived {2:+d} declared {3:+d}".format(c["plan"], cls, d, x))
            det.append({"plan": c["plan"], "fails": c["fails"]})
        elif c["overall"] == "UNPREDICTED":
            lines.append("ADVISORY CENSUS-UNPREDICTED {0} rows {1} (prerun verdict unchanged; --scratch-required exits 3)".format(
                c["plan"], c["unpredicted"] or "[classes never measured]"))
        else:
            lines.append("INFO  CENSUS {0} {1} ({2})".format(c["overall"], c["plan"], c["pred"]))
        if c is not None:                                # card chat-S2 (PD327): LOG-only classes, recorded, not failures
            for p_ in c["rep"]["classes"]:
                if p_["verdict"] == "SOFT":
                    lines.append("CENSUS SOFT {0} {1} derived {2:+d} declared {3:+d} [LOG-only: {4}]".format(
                        c["plan"], p_["class"], p_["derived"], p_["declared"], p_.get("rule")))
                    _gateclass.soft_record("X15 CENSUS " + c["plan"], p_["class"], p_["declared"], p_["derived"], p_.get("rule"))
    for ln in lines:
        out("  " + ln)
    return ok, det or "no derived != declared class", lines


def census_unpredicted(recipe):
    """card 123-7: the stageplans a recipe names whose census is CENSUS-UNPREDICTED (for --scratch-required)."""
    try:
        plans, _named = plan_files(recipe)
    except Exception:                                                           # noqa: BLE001
        return []
    out = []
    for p in plans:
        if is_stageplan(p):
            c = census_check(p)
            if c is not None and c["overall"] == "UNPREDICTED":
                out.append("{0} rows {1}".format(c["plan"], c["unpredicted"]))
    return out


# card 125-1 (PD251(b)): X16 - a primitive CREATE whose declared terminal list has an entry without `term_class`.
# Cause: archive/peer/2026-10-01-c124-8-p3a-termclass-hyp.md - 124-7 failed at op 1 because created-node terminals took
# stagesim's default class `Terminal` (stagesim.py:1317, `t.get("term_class") or "Terminal"`) while LabVIEW gives
# ParameterTerminal (Increment's `x+1` = OverridableParameterTerminal). The class is declared per terminal from a
# measured donor graph, never defaulted.
# card 125-3 (PD252(a), review archive/peer/2026-10-01-c125-1-x16-hyp.md ACCEPTED): `prim: "const_donor"` creates are
# OUT of scope - a donor constant's measured terminal class IS the default `Terminal` (stage_d1_ring_p2b.log:138-154,
# 5/5), so refusing it was a gate false positive. Every other create (primitives) is still checked.
# card 132-1 (PD275(e), gate-fp fp-20; PD262(c)): a `Local` (local variable) create is OUT of scope for the same reason -
# its measured terminal class IS the default `Terminal` (stage_d1_ring_p3b1_scratch_pin4.log:478,485: Local #27601 'Num'
# and #28037 'Num', class Terminal), so plan_disp r6_lr_ring's undeclared class defaults to what LabVIEW gives.
CREATE_OPS = ("create", "primitive", "primitive_create", "create_primitive")
X16_EXEMPT_PRIMS = ("const_donor",)
X16_EXEMPT_CLASSES = ("Local",)


def x16_in_scope(a):
    """True for a create action with a declared `terminals` list that is not a const_donor constant nor a Local."""
    return (a.get("op") in CREATE_OPS and isinstance(a.get("terminals"), list)
            and a.get("prim") not in X16_EXEMPT_PRIMS and a.get("class") not in X16_EXEMPT_CLASSES)


def termclass_undeclared(plan):
    """X16 core: [{action, terminal}] for every in-scope create action's declared `terminals` entry with no term_class."""
    out = []
    for a in (plan or {}).get("actions") or []:
        if not x16_in_scope(a):
            continue
        for t in a["terminals"]:
            if not (isinstance(t, dict) and str(t.get("term_class") or "").strip()):
                out.append({"action": a.get("id"), "terminal": t.get("name") if isinstance(t, dict) else t})
    return out


def x16_gate(plans):
    """(ok, detail) of X16 over loaded stageplan dicts."""
    bad = [dict(x, stage=(pl or {}).get("stage")) for pl in plans for x in termclass_undeclared(pl)]
    n = sum(1 for pl in plans for a in (pl or {}).get("actions") or [] if x16_in_scope(a))
    return not bad, (bad[:6] if bad else "{0} non-const_donor create action(s) with declared terminals, all classed"
                     .format(n))


# card 141-1 (PD322(d), PD323(b)): the OFFLINE half of the created-node PRIM GATE (X17). A create with a `prim` (not const_donor)
# copies its node from a donor; the donor's LABEL must equal the declared prim BEFORE any LabVIEW run. `$work` donors are nodes
# of the work VI = the original's uids (tools/bench/main_vi_node_labels.json; #29157 there is 'Insert Into Array', :1120 - the
# P3b donor mistake, tools/bench/diag_c140_4_facts.md). A `$work` donor an EARLIER action of the same plan deletes is refused
# (the run-time create would find no donor). External donor VIs are listed below with the label read back on the machine;
# an unlisted external donor is UNMEASURED = refused. The run-time half is stagexec.prim_check.
PRIM_DONOR_LABELS = os.path.join(BENCH, "main_vi_node_labels.json")
PRIM_DONORS = {   # (donor file basename, donor uid): (label, class, md5 of the donor VI, where the label was read back)
    ("DonorRAS1D_v0.vi", 175): ("Replace Array Subset", "GrowableFunction", "e8a9417ce4b75d27e8fd2f172a5dc9cd",
                                "tools/bench/diag_c140_5_run2.log:29-30 (node_labels; diag_c140_5_facts.md:12)"),
    ("DonorErrSel_MergeErrors.vi", 529): ("Select", "Function", None,
                                          "tools/bench/stage_d1_ring_p3b1.log:212 (created #10579 read back label 'Select')"),
    ("OpWaitDonor_v0.vi", 163): ("Wait (ms)", "Function", None,
                                 "tools/bench/stage_d1_ring_p3a.log:54 (created #26747 read back label 'Wait (ms)')"),
}


def prim_donor_labels(path=None):
    """{uid: label} of the original main VI (main_vi_node_labels.json: `diagrams` lists + `explicit` / `implicit` maps)."""
    d = json.load(REAL_OPEN(path or PRIM_DONOR_LABELS, encoding="utf-8"))
    out = {}
    for rows in (d.get("diagrams") or {}).values():
        for r in rows or []:
            if isinstance(r, dict) and r.get("uid") is not None:
                out.setdefault(int(r["uid"]), r.get("label"))
    for k in ("explicit", "implicit"):
        for u, r in (d.get(k) or {}).items():
            if isinstance(r, dict):
                out.setdefault(int(u), r.get("label"))
    return out


def prim_donor_check(plan, labels=None, registry=None, base_uids=None):
    """X17 core: [{action, why}] for every create action with a non-const_donor `prim` whose donor label is not the prim, is
    unknown, or whose `$work` donor an earlier action deletes / the base graph lacks. labels = {uid: label} (default
    prim_donor_labels()); base_uids = the plan base graph's object uids when known (None = not checked)."""
    labels = prim_donor_labels() if labels is None else labels
    reg = PRIM_DONORS if registry is None else registry
    out, deleted = [], set()
    for a in (plan or {}).get("actions") or []:
        if a.get("op") == "delete_object" and a.get("uid") is not None:
            try:
                deleted.add(int(a["uid"]))
            except (TypeError, ValueError):
                pass
        if a.get("op") not in CREATE_OPS or not a.get("prim") or a.get("prim") in X16_EXEMPT_PRIMS:
            continue
        dn = a.get("donor") or {}
        if not isinstance(dn, dict) or dn.get("uid") is None:
            if a.get("donor_uid") is None:
                out.append({"action": a.get("id"), "why": "prim {0!r} with no donor uid - label not checkable".format(a["prim"])})
            continue
        u = int(dn["uid"])
        if dn.get("donor") == "$work":
            lab = labels.get(u)
            if u in deleted:
                out.append({"action": a.get("id"), "why": "$work donor #{0} is deleted by an EARLIER action of this plan".format(u)})
            elif base_uids is not None and u not in base_uids:
                out.append({"action": a.get("id"), "why": "$work donor #{0} is not in the plan's base graph".format(u)})
            elif lab != a["prim"]:
                out.append({"action": a.get("id"), "why": "$work donor #{0} label {1!r} != plan prim {2!r}{3}".format(
                    u, lab, a["prim"], "" if lab is not None else " (uid not in main_vi_node_labels.json: UNMEASURED)")})
            continue
        key = (os.path.basename(str(dn.get("donor"))), u)
        ent = reg.get(key)
        if ent is None:
            out.append({"action": a.get("id"), "why": "external donor {0} uid {1}: label UNMEASURED (not in PRIM_DONORS)".format(*key)})
        elif ent[0] != a["prim"] or (a.get("class") and ent[1] != a.get("class")):
            out.append({"action": a.get("id"), "why": "external donor {0} uid {1} label {2!r} class {3!r} != plan prim {4!r} class {5!r}"
                        .format(key[0], u, ent[0], ent[1], a["prim"], a.get("class"))})
        elif ent[2] and os.path.isfile(str(dn.get("donor"))) and md5(str(dn["donor"])) != ent[2]:
            out.append({"action": a.get("id"), "why": "external donor {0} md5 {1} != the measured {2}".format(
                dn["donor"], md5(str(dn["donor"])), ent[2])})
    return out


def x17_gate(plans, labels=None):
    """(ok, detail) of X17 (card 141-1) over loaded stageplan dicts."""
    try:
        labels = prim_donor_labels() if labels is None else labels
    except Exception as e:                                                         # noqa: BLE001
        return False, "UNMEASURED: main_vi_node_labels.json unreadable ({0})".format(e)
    bad = [dict(x, stage=(pl or {}).get("stage")) for pl in plans for x in prim_donor_check(pl, labels)]
    n = sum(1 for pl in plans for a in (pl or {}).get("actions") or []
            if a.get("op") in CREATE_OPS and a.get("prim") and a.get("prim") not in X16_EXEMPT_PRIMS)
    return not bad, (bad[:6] if bad else "{0} primitive create action(s), every donor label == its prim".format(n))


def prerun(recipe, graph=None, stop_after=None, from_step=None):
    """card 103-2 (PD216(b)): stop_after=k (the recipe's own `--stop-after k`, PART-A mode) makes X5 expect only the
    stageplan wiring real ops 1..k - exactly the ops the run dispatches; the wire-action COVERAGE check stays over the
    whole compiled plan. stop_after=None: X5 unchanged."""
    tr = dry(recipe, graph)
    gates = []

    def gate(label, ok, detail=""):
        gates.append((label, bool(ok), detail))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)
    gate("X1 dry run PASS (whole Python path, COM stubbed)", tr["status"] in ("PASS", "PASS-UNVERIFIED"),
         tr["first_fail"] or (tr["unverified"] and "PASS-UNVERIFIED {0} (launch needs a card naming each)".format(
             tr["unverified"])))
    OG = _graph()
    plans, named = plan_files(recipe)
    sps = [p for p in plans if is_stageplan(p)]                  # card 79-6: stageplan/1 plans, checked, not trusted
    spc = dict((p, stageplan_check(p)) for p in sps)
    sp_bad = ["{0}: {1}".format(rel(p), c[1]) for p, c in spc.items() if not c[0]]
    gate("X2 a finalized plan file (decisions rows, or a final PASS stageplan/1) is named by the recipe",
         plans and not sp_bad, sp_bad or [rel(p) for p in plans] or "none among {0}".format([os.path.basename(p) for p in named]))
    rows = []
    for p in plans:
        if p in spc:
            continue
        rows += [dict(r, _plan=os.path.basename(p)) for r in json.load(open(p, encoding="utf-8"))["decisions"]]
    und = [(r["id"], r.get("action")) for r in rows if r.get("action") in (None, "", "llm", "unknown", "undecided")]
    sp_acts = 0
    for p, (ok_, _d, pl, ops_) in spc.items():
        acts = (pl or {}).get("actions") or []
        sp_acts += len(acts)
        und += [(a.get("id"), a.get("op")) for a in acts if a.get("op") in (None, "", "llm", "unknown", "undecided")]
        covered = sorted(x for o in (ops_ or []) for x in o["acts"])
        if not ok_ or covered != list(range(1, len(acts) + 1)):
            und.append((rel(p), "actions not all compiled exactly once ({0} of {1})".format(len(covered), len(acts))))
    gate("X3 every plan row decided", plans and not und, und or "{0} rows + {1} stageplan actions".format(len(rows), sp_acts))
    cpl = []
    for p, (_ok, _d, pl, _o) in spc.items():
        cpl += ["{0}: {1}".format(rel(p), x) for x in control_path_lint(pl or json.load(open(p, encoding="utf-8")))]
    gate("X8 control_path_lint (CLAUDE.md 1c'': no queue for control, no polled-boolean edge detector)", not cpl,
         cpl[:6] or "{0} stageplan(s)".format(len(spc)))
    # card 114-1 S0 (PD227(j)): a row wiring one Build Array input while a sibling input is an open row -> predicted rename
    bao = []
    for p, (_ok, _d, pl, _o) in spc.items():
        bao += [dict(x, plan=rel(p)) for x in buildarray_open_sibling(pl or json.load(open(p, encoding="utf-8")),
                                                                       licences=pb_licences(p))]
    gate("X11 no row wires one Build Array input while a sibling input is an open row (unless pb-licence/1)",
         not [x for x in bao if not x["licensed"]], bao[:6] or "{0} stageplan(s)".format(len(spc)))
    # card 114-3 C4: a row naming a wire uid an EARLIER border-crossing connect re-created (the uid is lost / re-issued)
    rwr, nrec = [], 0
    for p, (_ok, _d, pl, _o) in spc.items():
        rec_, fl_ = recreated_wire_refs(pl or json.load(open(p, encoding="utf-8")))
        nrec += len(rec_)
        rwr += [dict(x, plan=rel(p)) for x in fl_]
    gate("X12 no row names a wire uid an earlier border-crossing connect re-created (connect_from_wire.json:266)",
         not rwr, rwr[:6] or "{0} stageplan(s), {1} re-created source wire(s), none named later".format(len(spc), nrec))
    # card 115-1 A1 (PD229(a)): the ops the stageplans use reproduce their own recorded opmodel samples in stagesim
    x13_ok, x13_det, x13_w = x13_gate([pl or json.load(open(p, encoding="utf-8")) for p, (_ok, _d, pl, _o) in spc.items()])
    gate("X13 opmodel conformance: every recorded sample of the plan ops' model files replays in stagesim", x13_ok, x13_det)
    for w_ in x13_w:
        print("  WARN  {0}".format(w_), flush=True)
    # card 125-1 (PD251(b)): every declared terminal of a created primitive carries its term_class
    x16_ok, x16_det = x16_gate([pl or json.load(open(p, encoding="utf-8")) for p, (_ok, _d, pl, _o) in spc.items()])
    gate("X16 every declared terminal of a created primitive carries term_class (PD251(b))", x16_ok, x16_det)
    # card 141-1 (PD322(d)/PD323(b)): the offline prim gate - every created primitive's donor label == its declared prim
    x17_ok, x17_det = x17_gate([pl or json.load(open(p, encoding="utf-8")) for p, (_ok, _d, pl, _o) in spc.items()])
    gate("X17 every created primitive's donor label == its declared prim (PD323(b))", x17_ok, x17_det)
    # card 123-7 (PD247(e)): the census of every stageplan that carries a prediction file; a gate only when one does
    cen_plans = [p for p in sps if census_check(p) is not None]
    if cen_plans:
        c_ok, c_det, _c_lines = census_gate(cen_plans, out=lambda s_: print(s_, flush=True))
        gate("X15 census: no class with derived != declared (tools/census_predict.py over census_samples.json)", c_ok, c_det)
    bad = []
    if OG is None:
        gate("X4 every end addressable offline", False, "no graph JSON for input md5 {0}".format(tr["input_md5"]))
    else:
        ends = []
        for r in rows:
            ex = r.get("exec") or {}
            for side, src in (("src", True), ("dst", False)):
                if isinstance(ex.get(side), dict):
                    ends.append(("plan " + r["id"] + "." + side, ex[side], src))
        for e, is_src, mut in tr["addresses"]:
            ends.append(("address()" + (" after " + mut if mut else ""), e, is_src))
        seen = set()
        for lab, e, is_src in ends:
            key = json.dumps([e, is_src], sort_keys=True, default=str)
            if key in seen:
                continue
            seen.add(key)
            why = addr_offline(OG, e, is_src)
            if why:
                bad.append("{0}: {1}".format(lab, why))
        gate("X4 every end addressable offline ({0} ends)".format(len(seen)), not bad, bad[:8])
    x5ok, x5det = x5_count(tr["ops"], rows, spc, stop_after, from_step)
    gate("X5 wiring ops executed in the dry run == plan wire rows", plans and not sp_bad and x5ok, x5det)
    if OG is not None:
        ints, strs = lint(recipe, OG)
        gate("X6 ast lint: no re-typed uid / terminal name", not ints and not strs,
             "uids {0}; names {1}".format(ints[:10], strs[:10]))
    else:
        gate("X6 ast lint: no re-typed uid / terminal name", False, "no graph JSON - the lint needs the input's uids")
    try:
        import jev_candidates as JC
        S1 = JC.load(JC.S1_KEY)
        cand_nodes = set()
        for r in rows:
            for side in ("src", "dst"):
                u = ((r.get("exec") or {}).get(side) or {}).get("uid")
                if isinstance(u, int):
                    cand_nodes.add(u)
        for j in tr["jev"]:
            it = j.get("intent") or {}
            for side in ("src", "dst"):
                v = it.get(side) if isinstance(it, dict) else None
                cand_nodes.update(x for x in ([v] if isinstance(v, int) else (v or {}).get("nodes", []) if isinstance(v, dict) else [])
                                  if isinstance(x, int))
        chains = dict((u, JC.s1_chains(S1, u)) for u in cand_nodes if u in S1["cls"])
        chains = dict((u, c) for u, c in chains.items() if c)
        cterms = JC.chain_terminals(S1, list(chains))
        inits = set(c["init"][0] for cs in chains.values() for c in cs if c["init"])
        hits = []
        for r in rows:
            if not str(r.get("decided_by", "")).lower().startswith("jev"):
                continue
            ex = r.get("exec") or {}
            ends = [(e.get("uid"), e.get("term")) for e in (ex.get("src") or {}, ex.get("dst") or {})]
            if any(x in cterms for x in ends) or any(u in chains for u, _t in ends):
                hits.append("plan " + r["id"])
        for j in tr["jev"]:
            it = j.get("intent") or {}
            if not isinstance(it, dict):
                continue
            us = []
            for side in ("src", "dst"):
                v = it.get(side)
                us += [v] if isinstance(v, int) else (v.get("nodes", []) if isinstance(v, dict) else [])
            if any(u in chains or u in inits for u in us if isinstance(u, int)):
                hits.append("jev {0} intent {1}".format(j["via"], it))
        gate("X7 no Jev row on a RULE-CHAIN-S1 chain terminal (chain nodes {0})".format(sorted(chains)),
             not hits, hits[:6])
    except Exception as e:                                                         # noqa: BLE001
        gate("X7 no Jev row on a RULE-CHAIN-S1 chain terminal", False, "chain check raised {0}".format(e))
    # card 106-3: X9 verb preconditions on the stage's own work file (retrospective-cycle102 wrong-ordering, r7 op 41)
    wk = (tr.get("works") or [None])[-1]
    mdst = getattr(sys.modules.get("gscript"), "MOVE_DST", None)
    rdisp = recipe_dispatches_rows(recipe)                     # card 110-7 F1: row `copy` counts only if rows dispatched
    vp = verb_preconditions(plans, sps, wk, mdst, stop_after, from_step, rows_dispatched=rdisp)
    gate("X9 every dispatched verb's precondition holds offline (copy_in: work == gscript.MOVE_DST)", plans and not vp,
         vp[:6] or "work {0}; decisions rows {1}".format(
             wk, "dispatched (run_rows/from_decision called)" if rdisp else
             "NOT dispatched (recipe calls neither run_rows nor from_decision)"))
    # card 130-1 (PD267(b)): X10 = the MODEL prediction from each Executor's compiled plan + checkpoint set (memory_model.json),
    # FAIL > fail_above_mb (675) and FAIL UNMEASURED; a recorded meter (card 106-3/106-5 mem_margin) still fails at >= 690
    x10_ok, x10_det = x10_gate(recipe, tr.get("executors"), stop_after, from_step, trace=tr)   # trace: card 132-4 PD277(a)
    tr["mem_margin"] = x10_det
    for r_ in x10_det.get("runs", []):
        print("  FACT  X10 {0}: N {1} ops, BIND {2}, R {3} reads, predicted peak {4} MB (fail above {5})".format(
            r_["plan"], r_["N"], r_["bind"], r_["R"], r_["peak_mb"], r_["fail_above_mb"]), flush=True)
        if r_.get("edit"):                                                         # card 136-2 (fp-33)
            print("  FACT  X10 edit model: start {0} MB ({1}); reads {2}".format(r_["start_mb"], r_["start_source"],
                                                                                 r_["checkpoints"]), flush=True)
        if r_.get("reads_line"):                                                   # card 138-2 (PD299(b))
            print("  FACT  X10 whole-VI reads: {0}{1}".format(r_["reads_line"], "; Executor-only peak {0} MB, R {1}".format(
                r_["exec_peak_mb"], r_["exec_R"]) if "exec_peak_mb" in r_ else ""), flush=True)
    if not x10_det.get("runs") and "not bounded" in str(x10_det.get("why")):
        print("  FACT  X10 whole-VI reads UNBOUNDED: {0}".format(x10_det.get("why")), flush=True)
    gate("X10 predicted LabVIEW private MB <= model fail_above_mb, from the compiled plan + checkpoint set ({0})".format(
        x10_det.get("why") or "peak {0} MB".format(x10_det.get("peak_mb"))), x10_ok,
        dict((k, x10_det.get(k)) for k in ("peak_mb", "why", "recorded", "not_compiled", "model") if x10_det.get(k)))
    warn = None
    tr["x14"] = x14_advisory(recipe, len(rows) + sp_acts)      # card chat-P1 item 4: ADVISORY, never a gate
    npass = sum(1 for g_ in gates if g_[1])
    first = next((g_[0] + ": " + str(g_[2])[:120] for g_ in gates if not g_[1]), None)
    tr["prerun"] = {"status": "PASS" if npass == len(gates) else "FAIL", "gates": [[a, b, str(c)[:600]] for a, b, c in gates],
                    "first_fail": first, "plans": dict((rel(p), md5(p)) for p in plans), "pass": npass,
                    "fail": len(gates) - npass, "warn": warn}
    return tr


def x14_advisory(recipe, n_rows, log=None):
    """card chat-P1 item 4 (user 2026-09-28; docs/d1-loop12-17-split-plan.md Pre-decided 'rows per step'): rows per
    build step <= ROWS_DEFAULT (15), up to ~ROWS_PROVEN (25) on a PROVEN pattern (proven_pattern). Prints ONE line,
    `  X14 rows N, budget B (proven: ...)`, prefixed WARN when N > B. Never a gate, never a FAIL, never a pass reason."""
    try:
        ok, stages, _sig = proven_pattern(recipe)
    except Exception as e:                                                         # noqa: BLE001
        ok, stages = False, ["(proven_pattern raised %s)" % type(e).__name__]
    budget = ROWS_PROVEN if ok else ROWS_DEFAULT
    line = "X14 rows {0}, budget {1} (proven: {2})".format(n_rows, budget, ", ".join(stages) if ok else
                                                           "no" + (" - %s" % ", ".join(stages) if stages else ""))
    over = n_rows > budget
    (log or (lambda m: print(m, flush=True)))("  {0}  {1}".format("WARN" if over else "INFO", line))
    return {"rows": n_rows, "budget": budget, "proven": ok, "stages": stages, "warn": over, "line": line}


def result_first(first, warn):
    """card 106-5 (PD219(c)): the RESULT line's first_fail carrying the X10 WARN (result-line/1 has no other free-text
    field, docs/protocol/result-line.json additionalProperties false; protocol.result_failed reads status + gates only,
    so a PASS line that names the WARN stays a PASS). FAIL keeps its failing gate first, the WARN appended in 200."""
    if not warn:
        return first
    if not first:
        return warn[:200]
    tag = " [X10 WARN unmeasured]"
    return str(first)[:200 - len(tag)] + tag


# ---------------------------------------------------------------------------------------------- records + launch gate
def plan_md5s(recipe):
    try:
        return dict((rel(p), md5(p)) for p in plan_files(recipe)[0])
    except Exception:                                                              # noqa: BLE001
        return {}


def write_record(kind, recipe, status, first_fail, extra=None):
    rec = {"t": time.time(), "iso": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "script": rel(recipe),
           "sha256": sha256(recipe), "plan_md5s": plan_md5s(recipe), "status": status, "first_fail": first_fail}
    rec.update(extra or {})
    if kind == "dry":
        rec.setdefault("dry_rule", DRY_RULE)   # card 134-2: a dry written by THIS code ran under this code's rule
    with REAL_OPEN(RECORDS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def launched_stage_scripts(cmd):
    """argv only: every `tools/recipes/stage_*.py` a command RUNS - a python token followed (past flags) by that
    path, directly or after bgrun's `--`. A path that is only an argument (grep, cat, --dry X) is not a launch."""
    return [p for p in launched_py(cmd) if STAGE_RE.search(p.replace("\\", "/"))]


# ------------------------------------------------------------------ card chat-N1 (2): VI-modifying scripts by AST
# Cycle 90: tools/bench/diag_c90_t0_step3*.py (not stage_*) broke a VI 3x on offline-knowable faults. The gate now
# classifies ANY launched .py by STRUCTURE: it imports stagekit AND calls a MUTATING stagekit verb. MODIFY_VERBS is
# the mutating subset of stagekit.Stage's public methods (tools/stagekit.py:466-1097); the read-only ones (es, count,
# census, uid_index, wired_terminals, net_sources, broken_wire_count, fs_inner_tunnel_read, address, resolve,
# live_graph, rule_check, start, close, gate, fact, ...) are not in it. VI_MOD_EXEMPT = the gate's own tooling.
MODIFY_VERBS = frozenset((
    "junk_purge", "delete_wire", "delete_object", "move_in", "connect", "connect_from_wire",
    "fs_inner_tunnel_connect", "wire_indicators", "add_shift_reg", "wire_sr", "create_local_read", "copy_in",
    "add_sr_row", "const_row", "cfw_second_pass", "from_decision", "save", "save_route", "plan_rows",
    "discard_work",
    # card 100-6 (PD213(f)3): the create verbs that edit the VI - stagekit.create_local_write and the gscript creators
    # stagexec's create routes call (CREATE_ROUTES / ROUTE_VERBS), so a script importing stagekit and calling one is gated
    "create_local_write", "create_indicator_nested", "create_control_nested", "create_primitive_nested",
    "set_visible", "set_control_label", "set_default_in_memory", "loop_in"))
VI_MOD_EXEMPT = frozenset(("stage_prerun.py", "stagekit.py", "stagexec.py", "stagesim.py"))


# card 103-4: stagekit's own OFFLINE self-test (docstring: "Nothing here opens COM, touches claudeDev or reads a .vi") calls
# save_route / create_local_read on a fake Stage and was refused as a VI-modifying launch (material_marker.log:2185).
# Exempt BY PROJECT PATH AND BYTES (sha256 pin, archive/peer/2026-09-27-c103d-hooks-before.md s3, accepted): the same bytes
# under any other path, or other bytes at this path, are still classified.
VI_MOD_EXEMPT_PATHS = {"tools/bench/selftest_stagekit.py": "82ab60d432900ae916a6ad67a2aad47951a66a3aca98d85b82d3d271bede8b67"}


def vi_modifying_calls(path):
    """[] or the sorted MODIFY_VERBS names the file calls, when it imports stagekit (ast; never text search)."""
    if os.path.basename(path).lower() in VI_MOD_EXEMPT:
        return []
    pin = VI_MOD_EXEMPT_PATHS.get(rel(os.path.abspath(path)).replace("\\", "/").lower())
    if pin and os.path.isfile(path) and sha256(path) == pin:
        return []
    try:
        tree = ast.parse(REAL_OPEN(path, encoding="utf-8", errors="replace").read(), filename=path)
    except (OSError, SyntaxError, ValueError):
        return []
    imports = False
    calls = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import) and any(a.name.split(".")[0] == "stagekit" for a in n.names):
            imports = True
        elif isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == "stagekit":
            imports = True
        elif isinstance(n, ast.Call):
            f = n.func
            name = f.attr if isinstance(f, ast.Attribute) else (f.id if isinstance(f, ast.Name) else None)
            if name in MODIFY_VERBS:
                calls.add(name)
    return sorted(calls) if imports else []


def is_vi_modifying(path):
    """card chat-N1 (2): True iff the .py imports stagekit AND calls a name in MODIFY_VERBS."""
    return bool(vi_modifying_calls(path))


def launched_vi_modifying(cmd):
    """argv only: launched .py scripts that are NOT tools/recipes/stage_*.py but is_vi_modifying() -> gated alike."""
    return [p for p in launched_py(cmd) if not STAGE_RE.search(p.replace("\\", "/"))
            and p.lower().endswith(".py") and os.path.isfile(p) and is_vi_modifying(p)]


def launched_py(cmd):
    """argv only: every script path a python token RUNS (past interpreter flags), directly or after bgrun's `--`.
    card 106-5 (review archive/peer/2026-09-27-c103d-hooks-before.md s1): a NEWLINE separates commands too (a two-line
    Bash/PowerShell command with the stage on line 2 was not found); a line continuation (bash `\\`, PowerShell backtick)
    is joined first, so a continued command stays one.
    card 111-3 (violation-decisions device-failed 20:20): the rule lives in ONE module, tools/launchunit.py, shared with
    stop_record (segment_class) and the card-flag path (guard_card): `py -m <module>` launches the MODULE; its later
    tokens are arguments only for a READ-ONLY module (launchunit.READONLY_MODULES: pyflakes, pycodestyle, py_compile,
    ...), fail-closed for any other module and for a module that is a project file."""
    import launchunit as LU
    return LU.launched_py(cmd, ROOT)


STAGEXEC = os.path.join(HERE, "stagexec.py")
STAGEXEC_RE = re.compile(r"(?:^|[\\/])tools[\\/]stagexec\.py$", re.I)


def launched_plan_runs(cmd):
    """argv only (card chat-S3): every `tools/stagexec.py run <plan.json>` a command RUNS -> [(stagexec path, plan
    path)]. A stagexec run executes a FINAL plan in LabVIEW, so it is a stage launch under the same gate.
    card 107-1 (review archive/peer/2026-09-27-c106e-oldcode-o1.md side finding 2): the same newline split and
    line-continuation join as launched_py - a plan run on line 2 of a two-line command was not found."""
    out = []
    joined = re.sub(r"(?:\\|`)[ \t]*\r?\n", " ", cmd or "")
    for seg in re.split(r"\s*(?:&&|\|\||;|\||\r?\n)\s*", joined):
        try:
            toks = shlex.split(seg, posix=False)
        except ValueError:
            toks = seg.split()
        toks = [t.strip("\"'") for t in toks]
        for i, t in enumerate(toks):
            if re.match(r"^py(thon)?[\d.]*(\.exe)?$", os.path.basename(t).lower()):
                j = i + 1
                while j < len(toks) and toks[j].startswith("-"):
                    j += 2 if toks[j] in ("-X", "-W", "-m") else 1
                if j + 2 < len(toks) and STAGEXEC_RE.search(toks[j].replace("\\", "/")) and toks[j + 1] == "run":
                    p = toks[j + 2]
                    out.append((STAGEXEC, os.path.normpath(p if os.path.isabs(p) else os.path.join(ROOT, p))))
    return out


def plan_record(kind, plan, status, first_fail, extra=None):
    """A dry/prerun record for a stagexec PLAN: script = tools/stagexec.py (its sha256), plan_md5s = {plan: md5}."""
    rec = {"t": time.time(), "iso": time.strftime("%Y-%m-%d %H:%M:%S"), "kind": kind, "script": rel(STAGEXEC),
           "sha256": sha256(STAGEXEC), "plan_md5s": {rel(plan): md5(plan)}, "status": status, "first_fail": first_fail,
           "plan": rel(plan)}
    rec.update(extra or {})
    if kind == "dry":
        rec.setdefault("dry_rule", DRY_RULE)   # card 134-2: same stamp as write_record (check_launch filters every dry)
    with REAL_OPEN(RECORDS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def is_stageplan(path):
    try:
        return path.lower().endswith(".json") and json.load(open(path, encoding="utf-8")).get("schema") == "stageplan/1"
    except Exception:                                                              # noqa: BLE001
        return False


def read_records():
    out = []
    try:
        with open(RECORDS, encoding="utf-8") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


# gate-fp fp-1/fp-6, card 121-5 (PD238(k), review archive/peer/2026-09-28-c121-3-launch-gate-l4.md ACCEPTED): the
# decision-4 false positives were failed PRE-RUNS (`py -u tools/stage_prerun.py --prerun <stage>`) whose START line
# names the stage, so `base not in line` read them as failed stage runs. A segment is excluded ONLY when its START
# command is ONE plain `py|python [-flags] tools/stage_prerun.py ...` invocation: no shell separator (; && || | &),
# no env prefix, no other script in command position - so a real launch can never hide behind it. The card-121-3
# time filter (segment_ended_by) is REVERTED: it widened decision 4 (clock step, rounding window); the time rule is
# again "any failing segment in a log modified after t_min".
PRERUN_SEG_RE = re.compile(
    r"min:\s*(?:py|python|python3)(?:\.exe)?(?:\s+-[A-Za-z]+)*\s+['\"]?(?:[.\w:/\\-]*[/\\])?tools[/\\]stage_prerun\.py['\"]?"
    r"(?:\s|$)", re.I)
SHELL_SEP_RE = re.compile(r";|&&|\|\||\||&")


def is_prerun_segment(start_line):
    """True when this bgrun START line runs tools/stage_prerun.py itself (a dry/prerun/check, never a stage run)."""
    cmd = (start_line or "").split("min:", 1)[-1]
    return bool(PRERUN_SEG_RE.search(start_line or "")) and not SHELL_SEP_RE.search(cmd)


def last_failed_run_after(script, t_min):
    """Newest failing bgrun run of `script` in a log modified after t_min (protocol.run_verdict).
    Segments that run tools/stage_prerun.py itself are not runs of `script` (is_prerun_segment, card 121-5)."""
    import protocol as P
    base = os.path.basename(script)
    worst = None
    for de in os.scandir(LOG_DIR):
        if not de.name.endswith(".log"):
            continue
        try:
            if de.stat().st_mtime <= t_min:
                continue
            text = open(de.path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for ts, line, seg in P.segments(text):
            if base not in line:
                continue
            if is_prerun_segment(line):
                continue
            v = P.run_verdict(seg)
            if v["failed"]:
                worst = (de.name, ts, v.get("first_fail"))
    return worst


# ---------------------------------------------------------------------------------------------- RETRY CAP
# User 2026-09-24 ("재시도 상한도 동의함. 다만 숫자 … 데이터를 쌓아가면서 조정"; card chat-D): one stage script's LabVIEW
# runs are capped PER CYCLE. Every launch this gate ALLOWS is appended to STAGE_RUNS (when the caller asks it to
# record - guard_bash does, the --check-launch CLI does not), so the number is tuned from data. A run past the cap
# needs a JUDGEMENT card: a task/1 card whose `retry_of` names the stage, carried in the command as
# `RETRY_CARD=<path>`; one card id authorises one run.
STAGE_RUNS = os.environ.get("STAGE_RUNS") or os.path.join(BENCH, "stage_runs.jsonl")
RETRY_CAP = 2
CYCLE_FRESH_S = 6 * 3600          # a cycle card older than this is not "the current cycle" (chat work since)
RETRY_CARD_RE = re.compile(r"(?:\bRETRY_CARD\s*=\s*|(?:^|\s)--retry-card(?:\s+|=))['\"]?([^\s'\";|&]+)")
# RECORDER REPAIR (card 78-2; docs/violation-decisions.md "device-failed - 2026-09-25 07:05"): a run is COUNTED only
# from a line tools/bgrun.py writes at CHILD START (`"by": "bgrun"`). The PreToolUse hook used to write the line
# before later gates and the permission layer decided, so refused launches were counted (stage_runs.jsonl:3-7).
# Those old hook-written lines carry no `by` and are kept in the file but no longer count. The judgement card for a
# run past the cap is `--retry-card <path>` on the bgrun command line (a flag, not an env prefix: the permission
# layer refuses `$env:` / `X=1 cmd` forms under claude -p); `RETRY_CARD=<path>` is still read.
COUNTED_BY = "bgrun"
# card 134-1 (PD287(a)): dry rule 2 = a FALSE gate on non-stub data fails the dry; stub-input gates stay UNVERIFIED and
# the dry ends PASS-UNVERIFIED, which check_launch refuses unless the card on `--unverified-card <path>` names each gate
# in a `rules`/`pass` string "DRY-UNVERIFIED-OK: <label prefix>; <label prefix>".
DRY_RULE = 2
UNVERIFIED_CARD_RE = re.compile(r"(?:^|\s)--unverified-card(?:\s+|=)['\"]?([^\s'\";|&]+)")
UNVERIFIED_OK_RE = re.compile(r"^\s*DRY-UNVERIFIED-OK:\s*(.+)$")


def unverified_card_names(cmd):
    """([label prefixes], why|None) from the task/1 card named by `--unverified-card <path>` in the command."""
    m = UNVERIFIED_CARD_RE.search(cmd or "")
    if not m:
        return [], "no --unverified-card <task card path> in the command"
    p = m.group(1) if os.path.isabs(m.group(1)) else os.path.join(ROOT, m.group(1))
    try:
        card = json.load(open(p, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [], "--unverified-card {0} does not load: {1}".format(rel(p), str(e)[:120])
    if not isinstance(card, dict) or card.get("schema") != "task/1":
        return [], "--unverified-card {0} is not a task/1 card".format(rel(p))
    out = []
    for t in list(card.get("rules") or []) + list(card.get("pass") or []):
        mm = UNVERIFIED_OK_RE.match(str(t))
        if mm:
            out.extend(x.strip() for x in mm.group(1).split(";") if x.strip())
    return out, (None if out else "card {0} names no DRY-UNVERIFIED-OK gate".format(rel(p)))


def stage_key(script):
    return re.sub(r"_v\d+(?=\.py$)", "", os.path.basename(script).lower())


def cycle_key(now=None):
    """'cycle <n>' from the newest tools/bench/cards/cycle_<n>.json written in the last CYCLE_FRESH_S, else
    'chat <date>'. STAGE_RUNS_CYCLE overrides (self-tests)."""
    if os.environ.get("STAGE_RUNS_CYCLE"):
        return os.environ["STAGE_RUNS_CYCLE"]
    now = now or time.time()
    cards = os.environ.get("STAGE_RUNS_CARDS") or os.path.join(BENCH, "cards")
    best = None
    try:
        for fn in os.listdir(cards):
            m = re.match(r"^cycle_(\d+)\.json$", fn)
            if m and (best is None or int(m.group(1)) > best[0]):
                best = (int(m.group(1)), os.path.join(cards, fn))
    except OSError:
        pass
    if best and now - os.path.getmtime(best[1]) <= CYCLE_FRESH_S:
        return "cycle %d" % best[0]
    return "chat " + time.strftime("%Y-%m-%d", time.localtime(now))


def read_stage_runs():
    out = []
    try:
        with open(STAGE_RUNS, encoding="utf-8") as f:
            for ln in f:
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    except OSError:
        pass
    return out


def retry_card(cmd, key, used):
    """(card id, None) when the command carries a valid judgement card for ONE more run of `key`, else (None, why)."""
    m = RETRY_CARD_RE.search(cmd or "")
    if not m:
        return None, "no RETRY_CARD=<task card path> in the command"
    p = m.group(1)
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    import protocol as P
    try:
        card = P.load_card(p, None)
    except (OSError, ValueError) as e:
        return None, "RETRY_CARD %s does not load: %s" % (rel(p), str(e)[:160])
    if card.get("schema") != "task/1" or card.get("retry_of") != key:
        return None, "RETRY_CARD %s is not a task/1 card with retry_of == %r (has %r)" % (rel(p), key, card.get("retry_of"))
    if card["id"] in used:
        return None, "RETRY_CARD id %r already authorised a run of %s this cycle - one card, one run" % (card["id"], key)
    return card["id"], None


def check_cap(cmd, s, runs, ck):
    """(allow, why, card id|None) for ONE stage script against RETRY_CAP in cycle `ck`."""
    key = stage_key(s)
    mine = [r for r in runs if r.get("stage") == key and r.get("cycle") == ck and r.get("by") == COUNTED_BY]
    if len(mine) < RETRY_CAP:
        return True, "", None
    cid, why = retry_card(cmd, key, {r.get("card") for r in mine if r.get("card")})
    if cid:
        return True, "", cid
    return False, ("RETRY CAP (user 2026-09-24): {0} already ran {1} time(s) in {2} (cap {3}; tools/bench/stage_runs.jsonl). "
                   "A further run is a JUDGEMENT decision: a task/1 card with \"retry_of\": \"{0}\", carried as "
                   "RETRY_CARD=<card path> in the launch command ({4}).\n").format(key, len(mine), ck, RETRY_CAP, why), None


# ------------------------------------------------------------------------------------------ PROVEN PATTERN (card chat-P1)
# User 2026-09-28 ("1~4번은 적용하도록", items 2a + 4): a stage whose MECHANISM has already run clean in two other stages
# needs no prior-art review (guard_cycle PROVEN-PATTERN) and may carry up to ROWS_PROVEN rows instead of ROWS_DEFAULT
# (X14, advisory). The mechanism is read from files, never from prose:
#   signature(recipe) = {op:<stageplan action op>, create:<class>, row:<decisions action>} over plan_files(recipe)
#                       UNION {K.<fn>, SX.<fn>} - the stagekit / stagexec functions the recipe CALLS (ast; the import
#                       aliases are read from the recipe, `import stagekit as K, stagexec as SX` being the convention).
#   proven = >= PROVEN_MIN distinct OTHER stage keys in stage_runs.jsonl (by == "bgrun") with a run whose log's LAST
#            segment finished and did not fail (protocol.run_verdict) and whose signature CONTAINS this recipe's.
# A run's signature is its record's `pattern` (written by record_started from this card on). For an older record it is
# recomputed from today's files ONLY when the script's sha256 equals the run's AND the plan md5s equal a prerun PASS
# record of that sha256 - otherwise the run is not counted (fail closed). An empty signature is never proven.
PROVEN_MIN = 2
ROWS_DEFAULT, ROWS_PROVEN = 15, 25


def _call_signature(recipe):
    try:
        tree = ast.parse(REAL_OPEN(recipe, encoding="utf-8", errors="replace").read(), filename=recipe)
    except (OSError, SyntaxError, ValueError):
        return set()
    alias = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                base = a.name.split(".")[0]
                if base in ("stagekit", "stagexec"):
                    alias[a.asname or base] = "K" if base == "stagekit" else "SX"
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) \
                and n.func.value.id in alias:
            out.add("%s.%s" % (alias[n.func.value.id], n.func.attr))
    return out


def _plan_signature(plans):
    out = set()
    for p in plans:
        try:
            d = json.load(REAL_OPEN(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict):
            continue
        for a in d.get("actions") or []:
            if isinstance(a, dict) and a.get("op"):
                out.add("op:%s" % a["op"])
                if a["op"] == "create" and a.get("class"):
                    out.add("create:%s" % a["class"])
        for r in d.get("decisions") or []:
            if isinstance(r, dict) and r.get("action"):
                out.add("row:%s" % r["action"])
    return out


def pattern_signature(recipe):
    """sorted list - see the block comment. [] when the recipe cannot be read."""
    try:
        plans = plan_files(recipe)[0] if recipe.lower().endswith(".py") else [recipe]
    except Exception:                                                              # noqa: BLE001
        plans = []
    return sorted(_plan_signature(plans) | (_call_signature(recipe) if recipe.lower().endswith(".py") else set()))


def _run_pattern(r, recs):
    """The signature of one stage_runs record: its own `pattern`, else recomputed under the md5 conditions, else None."""
    if isinstance(r.get("pattern"), list):
        return set(r["pattern"])
    s = os.path.join(ROOT, r.get("script") or "")
    if not os.path.isfile(s) or sha256(s) != r.get("sha256"):
        return None
    pm = plan_md5s(s)
    if not any(x.get("kind") == "prerun" and x.get("status") == "PASS" and x.get("sha256") == r.get("sha256")
               and x.get("plan_md5s") == pm for x in recs):
        return None
    return set(pattern_signature(s))


def _run_clean(r):
    import protocol as P
    lg = os.path.join(ROOT, r.get("log") or "")
    if not r.get("log") or not os.path.isfile(lg):
        return False
    try:
        text = REAL_OPEN(lg, encoding="utf-8", errors="replace").read()
    except OSError:
        return False
    _ts, _cmd, seg = P.last_segment(text)
    v = P.run_verdict(seg)
    return v.get("source") != "none" and not v.get("failed")


def proven_pattern(recipe, runs=None, recs=None):
    """(proven: bool, stages: [stage keys whose clean run covers this signature], signature: [..])."""
    sig = set(pattern_signature(recipe))
    if not sig:
        return False, [], []
    runs = read_stage_runs() if runs is None else runs
    recs = read_records() if recs is None else recs
    own = stage_key(recipe) if recipe.lower().endswith(".py") else unit_key(recipe)
    hits = []
    for r in runs:
        k = r.get("stage")
        if r.get("by") != COUNTED_BY or not k or k == own or k in hits:
            continue
        pat = _run_pattern(r, recs)
        if pat is None or not sig <= pat:
            continue
        if _run_clean(r):
            hits.append(k)
    return len(hits) >= PROVEN_MIN, sorted(hits), sorted(sig)


def new_structure_classes(recipe, runs=None, recs=None, sig=None):
    """card chat-P2 item 1 (user 2026-09-28): the STRUCTURE elements of this recipe's signature (`op:<kind>` and
    `create:<class>`) that no CLEAN run of ANY other stage carries. Non-empty = the plan introduces a new structure class,
    so it always gets the prior-art review (with the user-rules question). proven_pattern already needs every element
    in >= 2 clean stages, so a new class is never proven; this names WHICH elements are new so guard_cycle's refusal
    says so (and the self-test pins that such a recipe is refused, not skipped)."""
    sig = set(pattern_signature(recipe)) if sig is None else set(sig)
    struct = {s for s in sig if s.startswith(("op:", "create:"))}
    if not struct:
        return []
    runs = read_stage_runs() if runs is None else runs
    recs = read_records() if recs is None else recs
    own = stage_key(recipe) if recipe.lower().endswith(".py") else unit_key(recipe)
    seen = set()
    for r in runs:
        k = r.get("stage")
        if r.get("by") != COUNTED_BY or not k or k == own:
            continue
        pat = _run_pattern(r, recs)
        if pat is None or not (struct - seen) & pat:
            continue
        if _run_clean(r):
            seen |= pat
    return sorted(struct - seen)


# ------------------------------------------------------------------------------ PROVISIONAL BASE + REBASE (card chat-P1)
# Item 1 (pipeline): the prep card plans stage N+1 while stage N runs in LabVIEW, on stagesim's END graph of N
# (tools/bench/sim/<stage N>/...). Its plan says so: base = {path, md5, provisional: true, sim_of: {plan, md5}} (docs/
# protocol/stageplan.json `baseref`). It gets dry / prerun / prior-art on that base offline, but it is NEVER launched on
# it (_check_units refuses). When N's saved artefact exists, `--rebase <plan> --graph <real graph of N's artefact>`:
#   1. refuses when N's plan (sim_of.plan) is not the md5 N+1 was simulated on (N changed -> re-plan N+1);
#   2. binds every object the simulation of N CREATED (negative uids in the provisional base) to the real object that
#      appeared between N's base graph and the real graph - card 132-5 (PD278(c)): by CONNECTIVITY first, then position
#      inside a bound node, then a unique name-free shape; names are LOGGED (LABEL-DIFF), never keyed; a terminal the plan
#      references must bind by connectivity, else REFUSE; wires and new frame diagrams through the bound terminals (an
#      empty FS frame by elimination); a uid LabVIEW re-issued to another object (stagexec.uid_reuse) refuses ONLY when
#      N+1's plan names it (card 143-4, PD334(b)); otherwise it is logged REUSE-NOTED and binding goes by identity;
#   3. rewrites N+1's uid fields through that binding (stagexec.translate's rule, applied to the plan's fields), refuses
#      an unbound negative or a positive uid the real graph does not hold, sets base = the real graph {path, md5} and
#      drops provisional / sim_of / final / finalized;
#   4. re-simulates N+1 on the real base (stagesim.simulate) - its step files were computed on the provisional graph.
# The plan md5 changes, so --dry and --prerun must run again (offline, seconds); the recipe .py is unchanged, so its
# prior-art review stays valid.
UID_FIELDS = ("dest_diagram", "loop", "body", "parent", "uid", "diagram", "wire_uid", "donor_uid")
ADDR_FIELDS = ("at", "src", "dst", "born_on", "on")


def provisional_plans(s, plan=None):
    """[(plan path, sim_of)] for every stageplan this unit would run whose base is provisional."""
    try:
        cands = [plan] if plan else [p for p in plan_files(s)[0] if is_stageplan(p)]
    except Exception:                                                              # noqa: BLE001
        cands = []
    out = []
    for p in cands:
        try:
            d = json.load(REAL_OPEN(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        b = d.get("base") if isinstance(d, dict) else None
        if isinstance(b, dict) and b.get("provisional"):
            out.append((p, b.get("sim_of")))
    return out


def _terms(path):
    d = json.load(REAL_OPEN(path, encoding="utf-8"))
    return d, [dict(r) for r in d.get("terminals") or []]


def _obj_id(doc):
    """{uid: (class, owner)} over a graph doc's objs - an OBJECT's identity across two graphs (card 143-4, PD334(b)): a uid
    LabVIEW re-issued to another object between N's base and the real graph is NEW, never 'already there'."""
    return dict((o["uid"], (o.get("class"), o.get("owner"))) for o in (doc or {}).get("objs") or []
                if isinstance(o, dict) and isinstance(o.get("uid"), int))


def plan_named_uids(plan):
    """Every positive int the plan's actions, open rows or bindings name (stagexec._ints_in over those keys) - the uids a
    re-issue would make the plan act on the wrong object (card 143-4, PD334(b)). Over-inclusive by design (an int field
    that is not a uid can only add a refusal, never hide one)."""
    import stagexec as SX
    out = set()
    for k in ("actions", "open_rows", "bindings", "binding", "bind"):
        SX._ints_in(plan.get(k), out)
    return set(u for u in out if u > 0)


def _reuse_uid(line):
    m = re.search(r"#(\d+)", line)
    return int(m.group(1)) if m else None


def rebind(before, prov, real, prov_doc=None, real_doc=None, before_doc=None, info=None, named=None):
    """(M: {negative uid -> real uid} | None, why). See the block comment, step 2.
    card 143-4 (PD334(b), docs/d1/ring-p4b.md:187): `named` = the uids the plan being rebased names (plan_named_uids; rebase
    passes it). stagexec.uid_reuse is a ONE-OP guard; here N's base and the real graph lie many ops and planned deletes apart,
    where LabVIEW re-issuing freed uids is expected. With `named`: a re-issued uid (uid_reuse hit, or a terminal uid whose
    OWNER changed) is FATAL only when the plan names it; otherwise it is recorded in info['reuse_noted'] (rebase logs
    `REUSE-NOTED <uid> <old>-><new>`) and binding goes by (uid, owner, name). Without `named` (a direct call) every
    uid_reuse hit refuses, as before.
    card 132-5 (PD278(c), docs/d1/ring-p3b.md:87-91): names are NEVER keyed - stagesim labels FS inner tunnels '' (real
    'error out') and the donor Unbundler's outputs 'element' (real code/source/status), diag_c132_4_rebind_keys.log:4-7.
    Order: (A) CONNECTIVITY - a created sim terminal on a wire whose other end is already bound takes the unique real
    terminal of the same node class / term class / direction / frame on that end's real wire; pre-existing terminals are
    bound to themselves; (B) POSITION - inside a bound node, (term_class, direction, frame) groups pair in read order
    (bind_new's convention, stagexec.py:905-911), never against a connectivity pair; (C) SHAPE - a still-unbound node
    pairs with the one real node of the same (class, (term_class, direction) multiset, frames) only when unique;
    (D) FS FRAMES - a created frame with no terminal rows (an empty f0) takes the one new FlatSequenceFrame Diagram left.
    Names are LOGGED (info['labels']); info['mode'] records how each created terminal bound ('conn' | 'pos' | 'shape').
    Every created node must bind; every sim wire's bound ends must land on ONE real wire (else REFUSE)."""
    import stagexec as SX
    import vigraph as V
    info = {} if info is None else info
    info.update({"mode": {}, "labels": [], "nodes": {}, "frames": {}, "how_frame": {}, "unbound_terms": [], "reuse_noted": []})
    ru = SX.uid_reuse(before, real)
    if ru and named is None:
        return None, "UID-REUSE between N's base and the real graph: {0}".format(ru[:6])
    if ru:
        hit = [x for x in ru if _reuse_uid(x) in named]
        if hit:
            return None, "UID-REUSE between N's base and the real graph on uid(s) the plan NAMES: {0}".format(hit[:6])
        info["reuse_noted"] = ru
    if named is not None:                                   # same class, OWNER changed (28004-type re-issue) and named
        ob = dict((r["term_uid"], r.get("owner_uid")) for r in before)
        moved = sorted(set(r["term_uid"] for r in real if r["term_uid"] in ob and r.get("owner_uid") != ob[r["term_uid"]]))
        hit = [u for u in moved if u in named]
        if hit:
            return None, "UID-REUSE between N's base and the real graph: terminal uid(s) the plan NAMES now sit on another owner: {0}".format(hit[:6])
    # card 142-5 (PD330(d), PD325(b)): a terminal is OLD only when its IDENTITY (term uid, owner uid, name) is in N's base -
    # LabVIEW re-issues a deleted terminal's uid to a NEW node of the same class inside one session (s01: 28004/28979 of the
    # deleted #27928/#28916 came back on the new #6942/#6805, prep_c142_5_probe.log), which uid_reuse cannot see (same classes)
    # and a raw-uid key filed as old (prep_c142_p1_rebase.log:3). Same key as stagekit.term_key (not imported: line 689).
    tkey = lambda r: (r["term_uid"], r.get("owner_uid"), str(r.get("term_name") or ""))   # noqa: E731
    old_t = set(tkey(r) for r in before)
    sim_new, real_new = collections.OrderedDict(), collections.OrderedDict()
    for r in prov:
        if V.node_of(r) < 0:
            sim_new.setdefault(V.node_of(r), []).append(r)
    for r in real:
        if tkey(r) not in old_t:
            real_new.setdefault(V.node_of(r), []).append(r)
    info["recycled"] = sorted(r["term_uid"] for rows in real_new.values() for r in rows
                              if r["term_uid"] in set(k[0] for k in old_t))
    dirk = lambda r: (r.get("term_class", ""), bool(r["is_source"]))               # noqa: E731

    def shape(rows):
        return (V.node_class(rows[0]), tuple(sorted(dirk(r) for r in rows)))
    cs = collections.Counter(shape(v) for v in sim_new.values())
    cr = collections.Counter(shape(v) for v in real_new.values())
    if cs != cr:
        bad = ["{0} x{1} simulated vs x{2} real".format(k[0], cs.get(k, 0), cr.get(k, 0))
               for k in sorted(set(cs) | set(cr), key=str) if cs.get(k, 0) != cr.get(k, 0)]
        return None, "BINDING: the created objects differ (name-free shape): {0}".format(bad[:6])
    srow = dict((r["term_uid"], r) for r in prov)
    rrow = dict((r["term_uid"], r) for r in real)
    swire, rwire = collections.defaultdict(list), collections.defaultdict(list)
    for r in prov:
        if r.get("wire_uid"):
            swire[r["wire_uid"]].append(r)
    for r in real:
        if r.get("wire_uid"):
            rwire[r["wire_uid"]].append(r)
    real_new_t = set(r["term_uid"] for rows in real_new.values() for r in rows)
    new_rf = set(r.get("frame_diagram") for r in real) - set(r.get("frame_diagram") for r in before)
    if before_doc and real_doc:                              # card 143-4: a frame uid re-issued to another object is NEW
        bo_, ro_ = _obj_id(before_doc), _obj_id(real_doc)
        new_rf |= set(f for f in set(r.get("frame_diagram") for r in real) if f in bo_ and f in ro_ and bo_[f] != ro_[f])
    T = dict((u, u) for u in srow if u > 0 and u in rrow and u not in real_new_t)   # pre-existing terminals: themselves
    # (card 142-5: a uid the real graph re-issued to a created node is NOT pre-existing - it binds like any created terminal)
    Tinv = dict(T)
    N, Ninv, D, Dinv, mode = {}, {}, {}, {}, info["mode"]

    def frame_ok(sr, rr):
        sf, rf = sr.get("frame_diagram") or 0, rr.get("frame_diagram") or 0
        if isinstance(sf, int) and sf < 0:
            return D[sf] == rf if sf in D else (rf not in Dinv)
        return sf == rf

    def bind_t(st, rt, how):
        sr, rr = srow[st], rrow[rt]
        sn, rn = V.node_of(sr), V.node_of(rr)
        if N.get(sn, rn) != rn or Ninv.get(rn, sn) != sn:
            return "BINDING: node #{0} would map to #{1} and #{2}".format(sn, N.get(sn), rn)
        sf, rf = sr.get("frame_diagram") or 0, rr.get("frame_diagram") or 0
        if isinstance(sf, int) and sf < 0:
            if D.get(sf, rf) != rf or Dinv.get(rf, sf) != sf:
                return "BINDING: frame #{0} would map to #{1} and #{2}".format(sf, D.get(sf), rf)
            if sf not in D:
                info["how_frame"][sf] = "row #{0}".format(st)
            D[sf], Dinv[rf] = rf, sf
        N[sn], Ninv[rn] = rn, sn
        T[st], Tinv[rt], mode[st] = rt, st, how
        return None
    snew_t = [r["term_uid"] for rows in sim_new.values() for r in rows]
    for _round in range(10000):
        progress = False
        for st in snew_t:                                                    # (A) connectivity
            sr = srow[st]
            if st in T or not sr.get("wire_uid"):
                continue
            ends = [T[o["term_uid"]] for o in swire[sr["wire_uid"]] if o["term_uid"] != st and o["term_uid"] in T]
            rws = set(rrow[e].get("wire_uid") for e in ends)
            if len(rws) > 1:
                return None, "CONNECTIVITY: sim wire {0}'s bound ends sit on real wires {1}".format(sr["wire_uid"], sorted(rws))
            if not rws or not next(iter(rws)):
                continue
            sn = V.node_of(sr)
            cand = [x for x in rwire[next(iter(rws))] if x["term_uid"] in real_new_t and x["term_uid"] not in Tinv
                    and V.node_class(x) == V.node_class(sr) and dirk(x) == dirk(sr) and frame_ok(sr, x)
                    and (sn not in N or V.node_of(x) == N[sn]) and Ninv.get(V.node_of(x), sn) == sn]
            if len(cand) == 1:
                e = bind_t(st, cand[0]["term_uid"], "conn")
                if e:
                    return None, e
                progress = True
        if progress:
            continue
        for sn, rn in list(N.items()):                                     # (B) position inside a bound node
            # a row on a created frame not bound yet keys as NEW; it pairs only with a real row on a new real frame not
            # bound yet, and only one-to-one (an FS tunnel's inner face is how its frame binds: the outer face connects)
            groups = collections.defaultdict(lambda: ([], []))
            for r in sim_new[sn]:
                f = r.get("frame_diagram") or 0
                f = D.get(f, "NEW") if isinstance(f, int) and f < 0 else f
                groups[dirk(r) + (f,)][0].append(r["term_uid"])
            for r in real_new.get(rn, []):
                f = r.get("frame_diagram") or 0
                groups[dirk(r) + ("NEW" if f in new_rf and f not in Dinv else f,)][1].append(r["term_uid"])
            for k, (ss, rs) in groups.items():
                if len(ss) != len(rs) or all(s in T for s in ss) or (k[-1] == "NEW" and len(ss) != 1):
                    continue
                if any(s in T and T[s] != r for s, r in zip(ss, rs)) or any(r in Tinv and Tinv[r] != s for s, r in zip(ss, rs)):
                    info.setdefault("pos_conflicts", []).append((sn, rn, k))
                    continue
                for s, r in zip(ss, rs):
                    if s not in T:
                        e = bind_t(s, r, "pos")
                        if e:
                            return None, e
                        progress = True
        if progress:
            continue
        def fkey(rows, sim):                                                    # (C) unique shape among the unbound
            fs = []
            for r in rows:
                f = r.get("frame_diagram") or 0
                fs.append(D.get(f, "?") if sim and isinstance(f, int) and f < 0 else f)
            return shape(rows) + (tuple(sorted(fs, key=str)),)
        us = collections.defaultdict(list)
        ur = collections.defaultdict(list)
        for sn, rows in sim_new.items():
            if sn not in N:
                us[fkey(rows, True)].append(sn)
        for rn, rows in real_new.items():
            if rn not in Ninv:
                ur[fkey(rows, False)].append(rn)
        for k, sl in us.items():
            if len(sl) == 1 and len(ur.get(k, [])) == 1 and "?" not in k[2]:
                N[sl[0]], Ninv[ur[k][0]] = ur[k][0], sl[0]
                info.setdefault("shape_nodes", []).append((sl[0], ur[k][0]))
                progress = True
        if not progress:
            break
    for st in snew_t:
        if st in T and mode.get(st) == "pos" and V.node_of(srow[st]) in dict(info.get("shape_nodes", [])):
            mode[st] = "shape"
    unb_n = [n for n in sim_new if n not in N]
    if unb_n:
        return None, "BINDING: created object(s) not bound by connectivity, position or a unique shape: {0}".format(
            ["#{0} {1}".format(n, V.node_class(sim_new[n][0])) for n in unb_n[:8]])
    if prov_doc and real_doc:                                                 # (D) FS frames without rows
        bo = _obj_id(before_doc)                             # card 143-4: by (uid, class, owner), not raw uid
        newf = [o["uid"] for o in real_doc.get("objs") or [] if isinstance(o, dict)
                and bo.get(o.get("uid")) != (o.get("class"), o.get("owner"))
                and o.get("class") == "Diagram" and o.get("owner") == "FlatSequenceFrame"]
        for _fs, frs in sorted((prov_doc.get("fs_frames") or {}).items()):
            left = [f for f in frs if isinstance(f, int) and f < 0 and f not in D]
            free = [u for u in newf if u not in Dinv]
            if len(left) == 1 and len(free) == 1:
                D[left[0]], Dinv[free[0]] = free[0], left[0]
                info["how_frame"][left[0]] = "only new FlatSequenceFrame Diagram left"
    M = {}
    for sn, rn in N.items():
        M[sn] = rn
    for sf, rf in D.items():
        M[sf] = rf
    for st, rt in T.items():
        if st < 0:
            M[st] = rt
            sn_, rn_ = srow[st].get("term_name", ""), rrow[rt].get("term_name", "")
            if sn_ != rn_:
                info["labels"].append((st, rt, V.node_class(srow[st]), sn_, rn_))
    for st in snew_t:                                                         # wires through bound terminals
        if st not in T:
            info["unbound_terms"].append(st)
            continue
        sv, rv = srow[st].get("wire_uid"), rrow[T[st]].get("wire_uid")
        if isinstance(sv, int) and sv < 0:
            if not rv:
                return None, "CONNECTIVITY: created terminal #{0} is wired in the simulation (w{1}), unwired in the real graph".format(st, sv)
            if M.get(sv, rv) != rv:
                return None, "BINDING: #{0} maps to both {1} and {2}".format(sv, M[sv], rv)
            M[sv] = rv
    for w, rows in swire.items():                                             # every sim wire lands on ONE real wire
        imgs = set(rrow[T[r["term_uid"]]].get("wire_uid") for r in rows if r["term_uid"] in T)
        if len(imgs) > 1:
            return None, "CONNECTIVITY: sim wire {0} lands on real wires {1}".format(w, sorted(imgs, key=str))
    info["nodes"], info["frames"] = dict(N), dict(D)
    return M, None


def _remap_plan(plan, M, known, rename=None):
    """(new plan, unbound negatives, unknown positives) - uid fields only (UID_FIELDS, ADDR_FIELDS, nodes, open_rows).
    rename {(created node uid, sim term name): real term name} - card 132-5: a name address on a created node takes the
    bound terminal's REAL label (rebase checked it binds uniquely)."""
    unb, unk = set(), set()
    rename = rename or {}

    def m(v):
        if isinstance(v, bool) or not isinstance(v, int):
            return v
        if v < 0:
            if v in M:
                return M[v]
            unb.add(v)
            return v
        if v not in known:
            unk.add(v)
        return v

    def addr(a):
        if isinstance(a, dict):
            a = dict(a)
            if "uid" in a:
                if isinstance(a.get("term"), str) and (a["uid"], a["term"]) in rename:
                    a["term"] = rename[(a["uid"], a["term"])]
                a["uid"] = m(a["uid"])
            if "term_uid" in a:
                a["term_uid"] = m(a["term_uid"])
            return a
        if isinstance(a, str):
            mm = re.match(r"^(-?\d+)(\..*)$", a)
            if mm:
                nm = mm.group(2)[1:]
                if (int(mm.group(1)), nm) in rename:
                    nm = rename[(int(mm.group(1)), nm)]
                return "{0}.{1}".format(m(int(mm.group(1))), nm)
        return a
    p = copy.deepcopy(plan)
    for a in p.get("actions") or []:
        for f in UID_FIELDS:
            if f in a:
                a[f] = m(a[f])
        for f in ADDR_FIELDS:
            if f in a:
                a[f] = addr(a[f])
        if isinstance(a.get("nodes"), list):
            a["nodes"] = [m(x) for x in a["nodes"]]
    for r in p.get("open_rows") or []:
        r["node"] = m(r.get("node"))
    return p, sorted(unb), sorted(unk)


FS_CARRY_KEYS = ("fs_frames", "fs_tunnels", "fs_alias", "fs_border_entries", "fs_frame_inferred", "diagrams")


def carry_fs(prov_doc, real_doc, before_doc, M, info=None):
    """card 132-6 (PD279(b), docs/d1/ring-p3b.md:95-100): (augmented real doc | None, why). The provisional base (stagesim's
    END state of stage N) knows the Flat Sequences N created - fs_frames order, fs_tunnels, fs_alias, fs_border_entries,
    fs_frame_inferred, the created frames' parent `diagrams`, owners[frame] = [FlatSequence, FS] - and the real graph read
    does not (no fs_frames key, frame owners ['FlatSequenceFrame', 0]: diag_c132_5_frames.log). Carry them THROUGH THE BINDING
    M: every created uid maps by M; a created FS (no terminal rows, so rebind never binds it) takes the ONE new FlatSequence
    object of the real graph when exactly one is created and one appeared; any created uid left unmapped REFUSES. owners:
    a real entry is replaced only when absent or the reader's [FlatSequenceFrame, 0] gap; any other disagreement REFUSES.
    The real terminals/objs are untouched - the result is the real graph + these keys + fs_carried (provenance)."""
    info = {} if info is None else info
    fsf = prov_doc.get("fs_frames") or {}
    if not fsf:
        return None, None
    M = dict(M)
    bo = _obj_id(before_doc)                                 # card 143-4: by (uid, class, owner), not raw uid
    new_fs = [o["uid"] for o in real_doc.get("objs") or [] if isinstance(o, dict) and o.get("class") == "FlatSequence"
              and bo.get(o.get("uid")) != (o.get("class"), o.get("owner"))]
    sim_fs = [int(k) for k in fsf if int(k) < 0 and int(k) not in M]
    free = [u for u in new_fs if u not in M.values()]
    if sim_fs:
        if len(sim_fs) != 1 or len(free) != 1:
            return None, "FS-CARRY: created Flat Sequence(s) {0} vs new real FlatSequence object(s) {1} - not 1:1".format(sim_fs, free)
        M[sim_fs[0]] = free[0]
        info["fs_bound"] = (sim_fs[0], free[0])
    # the SWAPPED TWIN of a cross-frame FS tunnel (stagesim._fs_frame_wire: a second FSIT object with no rows, one fs_pairs
    # entry with the faces swapped) is a simulator object: LabVIEW files the physical tunnel's four rows under ONE uid
    # (stagexec.bind_fs_tunnel, diag_c125_5_fsscr.log:57), so the twin takes its tunnel's real uid
    twins = {}
    for k, v in (prov_doc.get("fs_tunnels") or {}).items():
        tw = v.get("twin")
        if isinstance(tw, int) and tw < 0 and tw not in M and int(k) in M:
            M[tw] = twins[tw] = M[int(k)]
    info["twins"] = twins
    miss = set()

    def mp(v):
        if isinstance(v, bool) or not isinstance(v, int):
            return v
        if v < 0:
            if v not in M:
                miss.add(v)
                return v
            return M[v]
        return v

    def mk(k):
        return str(mp(int(k)))
    out = {}
    out["fs_frames"] = dict((mk(k), [mp(int(f)) for f in v]) for k, v in fsf.items())
    out["fs_tunnels"] = dict((mk(k), {"fs": mp(v.get("fs")), "twin": mp(v.get("twin")), "frames": [mp(x) for x in v.get("frames") or []],
                                      "link": [mp(x) for x in v.get("link") or []]})
                             for k, v in (prov_doc.get("fs_tunnels") or {}).items())
    out["fs_alias"] = dict((mk(k), v) for k, v in (prov_doc.get("fs_alias") or {}).items())
    be = {}
    for k, v in (prov_doc.get("fs_border_entries") or {}).items():
        t, fd = k.split("|")
        be["{0}|{1}".format(mp(int(t)), mp(int(fd)))] = dict(v, face=mp(v.get("face")))
    out["fs_border_entries"] = be
    out["fs_frame_inferred"] = dict((mk(k), mp(int(v))) for k, v in (prov_doc.get("fs_frame_inferred") or {}).items())
    out["diagrams"] = dict((mk(k), mp(int(v))) for k, v in (prov_doc.get("diagrams") or {}).items() if int(k) < 0)
    own = dict((str(k), list(v)) for k, v in (real_doc.get("owners") or {}).items())
    changed = []
    for k, v in (prov_doc.get("owners") or {}).items():
        if int(k) >= 0:
            continue
        rk, rv = mk(k), [v[0], mp(int(v[1] or 0))]
        cur = own.get(rk)
        if cur is None or (cur[0] == "FlatSequenceFrame" and int(cur[1] or 0) == 0) or (cur[0] == rv[0] and int(cur[1] or 0) == rv[1]):
            if cur != rv:
                changed.append((rk, cur, rv))
            own[rk] = rv
        else:
            return None, "FS-CARRY: owners[{0}] real {1} vs carried {2} (from #{3})".format(rk, cur, rv, k)
    # the created tunnels' fs_pairs entries (stagesim appends them; the real read files none for the new FSIT, diag_c132_6_fspairs.log)
    rpairs = list(real_doc.get("fs_tunnel_pairs") or [])
    have = set((p.get("uid"), p.get("term_a"), p.get("term_b")) for p in rpairs)
    added = []
    for p in prov_doc.get("fs_pairs") or []:
        if isinstance(p.get("uid"), int) and p["uid"] < 0:
            q = dict(p, uid=mp(p["uid"]), term_a=mp(p.get("term_a")), term_b=mp(p.get("term_b")),
                     model="{0} - carried by rebase (card 132-6)".format(p.get("model", "")))
            if (q["uid"], q["term_a"], q["term_b"]) not in have:
                rpairs.append(q)
                added.append(q)
    out["fs_pairs_added"] = len(added)
    if miss:
        return None, "FS-CARRY: created uid(s) in the FS map not bound: {0}".format(sorted(miss)[:12])
    aug = dict(real_doc)
    aug.update(dict((k, v) for k, v in out.items() if k != "fs_pairs_added"))
    aug["fs_tunnel_pairs"] = rpairs
    aug["owners"] = own
    aug["fs_carried"] = {"by": "stage_prerun.carry_fs (card 132-6, PD279(b))", "owners_changed": changed,
                         "fs_bound": info.get("fs_bound"), "twins": dict((str(k), v) for k, v in twins.items()),
                         "fs_pairs_added": added}
    info["owners_changed"] = changed
    info["fs_map"] = out
    return aug, None


def rebase(plan_path, graph_path, log=print, simulate=True, out_root=None, model_dir=None):
    """(ok, detail) - see the block comment. Writes the rebased plan to plan_path only when every check passes.
    card 132-6 (PD279(b)(c)): the provisional base's FS map is CARRIED through the binding into an augmented copy of the
    real graph (`tools/bench/sim/<stage>_base_real_fsmap.json`; carry_fs) which becomes the plan's base when the provisional base
    had a plan-made Flat Sequence; and a re-simulation that is not final NEVER writes plan_path (it simulates a temp copy)."""
    plan = json.load(REAL_OPEN(plan_path, encoding="utf-8"))
    b = plan.get("base") if isinstance(plan.get("base"), dict) else {}
    if not b.get("provisional"):
        return False, "{0}: base is not provisional - nothing to rebase".format(rel(plan_path))
    so = b.get("sim_of") or {}
    pn = so.get("plan") and (so["plan"] if os.path.isabs(so["plan"]) else os.path.join(ROOT, so["plan"]))
    if not pn or not os.path.isfile(pn):
        return False, "base.sim_of.plan {0!r} missing".format(so.get("plan"))
    if md5(pn) != so.get("md5"):
        return False, ("REBASE REFUSED: {0} changed since stage N+1 was simulated on it (md5 {1} != sim_of {2}) - "
                       "re-simulate N+1 on N's new end graph").format(rel(pn), md5(pn), so.get("md5"))
    dn = json.load(REAL_OPEN(pn, encoding="utf-8"))
    bn = (dn.get("finalized") or {}).get("base") or dn.get("base") or {}
    if not bn.get("path"):
        return False, "stage N's plan {0} names no base graph".format(rel(pn))
    _gb, before = _terms(bn["path"] if os.path.isabs(bn["path"]) else os.path.join(ROOT, bn["path"]))
    _gp, prov = _terms(b["path"] if os.path.isabs(b["path"]) else os.path.join(ROOT, b["path"]))
    greal, real = _terms(graph_path)
    info = {}
    M, why = rebind(before, prov, real, prov_doc=_gp, real_doc=greal, before_doc=_gb, info=info, named=plan_named_uids(plan))
    if M is None:
        return False, "REBASE REFUSED: " + why
    for x in info.get("reuse_noted") or []:                  # card 143-4 (PD334(b)): re-issued, not named by the plan
        u = _reuse_uid(x)
        log("REUSE-NOTED {0} {1}".format(u, x.split("#{0} ".format(u), 1)[-1]))
    modes = collections.Counter(info["mode"].values())
    log("REBIND {0} node(s), {1} frame(s), terminals by {2}; unbound created terminals {3}; frames {4}; re-issued uid(s) {5}".format(
        len(info["nodes"]), len(info["frames"]), dict(modes), info["unbound_terms"][:12],
        dict((k, "{0} ({1})".format(v, info["how_frame"].get(k, "?"))) for k, v in sorted(info["frames"].items())),
        info.get("recycled", [])[:12]))
    for st, rt, cls, sn_, rn_ in info["labels"]:
        log("LABEL-DIFF {0} #{1} -> #{2}: sim {3!r} real {4!r} (by {5})".format(cls, st, rt, sn_, rn_, info["mode"].get(st)))
    # PD278(c): a terminal the plan REFERENCES binds by connectivity (or is pre-existing), else REFUSE
    srow = dict((r["term_uid"], r) for r in prov)
    rrow = dict((r["term_uid"], r) for r in real)
    refs, named = set(), []
    for a in plan.get("actions") or []:
        for f in ADDR_FIELDS:
            v = a.get(f)
            if isinstance(v, dict):
                if isinstance(v.get("term_uid"), int) and v["term_uid"] < 0:
                    refs.add(v["term_uid"])
                if isinstance(v.get("uid"), int) and v["uid"] < 0 and isinstance(v.get("term"), str):
                    named.append((v["uid"], v["term"]))
            elif isinstance(v, str):
                mm = re.match(r"^(-\d+)\.(.*)$", v)
                if mm:
                    named.append((int(mm.group(1)), mm.group(2)))
        for f in UID_FIELDS:
            if isinstance(a.get(f), int) and a[f] < 0 and a[f] in srow:
                refs.add(a[f])
    weak = sorted(t for t in refs if t in srow and info["mode"].get(t) != "conn")
    if weak:
        return False, "REBASE REFUSED: plan-referenced terminal(s) not bound by connectivity: {0}".format(
            ["#{0} {1!r} by {2}".format(t, srow[t].get("term_name"), info["mode"].get(t, "unbound")) for t in weak[:8]])
    rename = {}
    for n, nm in named:
        mk = re.match(r"^(.*)#(\d+)$", nm)                  # '<name>#k' = k-th (0-based) same-named row, stagesim.py:471
        base_nm, k = (mk.group(1), int(mk.group(2))) if mk else (nm, None)
        ss = [r for r in prov if r["owner_uid"] == n and r.get("term_name", "") == base_nm]
        st = (ss[0]["term_uid"] if len(ss) == 1 else None) if k is None else (ss[k]["term_uid"] if k < len(ss) else None)
        rt = M.get(st) if st is not None else None
        rn = rrow[rt].get("term_name", "") if rt in rrow else None
        same = [r for r in real if r["owner_uid"] == M.get(n) and r.get("term_name", "") == rn]
        if st is None or rt is None or len(same) != 1 or (rn != base_nm and info["mode"].get(st) != "conn"):
            return False, ("REBASE REFUSED: plan-referenced terminal #{0}.{1!r} does not bind uniquely ({2} sim row(s), "
                           "by {3}, real name {4!r} x{5})").format(n, nm, len(ss), info["mode"].get(st, "unbound"), rn, len(same))
        rename[(n, nm)] = rn
    known = set()
    for r in real:
        known.update(x for x in (r.get("owner_uid"), r.get("term_uid"), r.get("frame_diagram"), r.get("wire_uid"))
                     if isinstance(x, int))
    known.update(int(o["uid"]) for o in greal.get("objs") or [] if isinstance(o, dict) and isinstance(o.get("uid"), int))
    # card 132-6 (PD279(b)): carry the provisional base's FS map through the binding (FS -1 -> the new real FlatSequence)
    aug, why = carry_fs(_gp, greal, _gb, M, info)
    if why:
        return False, "REBASE REFUSED: " + why
    base_path = graph_path
    if aug is not None:
        log("FS-CARRY fs {0}; fs_frames {1}; fs_tunnels {2}; twins {3}; fs_pairs added {4}; owners changed {5}".format(
            info.get("fs_bound"), info["fs_map"]["fs_frames"], sorted(info["fs_map"]["fs_tunnels"]), info.get("twins"),
            info["fs_map"].get("fs_pairs_added"), info["owners_changed"]))
        base_path = os.path.join(out_root or os.path.join(ROOT, "tools", "bench", "sim"),
                                 "{0}_base_real_fsmap.json".format(plan.get("stage") or "plan"))
        aug["fs_carried"].update(real_graph={"path": rel(graph_path).replace("\\", "/"), "md5": md5(graph_path)},
                                 provisional={"path": b.get("path"), "md5": b.get("md5")})
        with REAL_OPEN(base_path, "w", encoding="utf-8") as f:
            json.dump(aug, f, separators=(",", ":"))
        known.update(int(k) for k in aug["owners"] if re.match(r"^-?\d+$", str(k)))
    new, unb, unk = _remap_plan(plan, M, known, rename=rename)
    if unb or unk:
        return False, ("REBASE REFUSED: unbound created uid(s) {0}; uid(s) the real graph does not hold {1}".format(
            unb[:12], unk[:12]))
    new["base"] = {"path": rel(base_path).replace("\\", "/"), "md5": md5(base_path)}
    new.pop("final", None)
    new.pop("finalized", None)
    detail = "rebased {0}: {1} uid(s) bound, base -> {2}".format(rel(plan_path), len(M), new["base"]["path"])
    if not simulate:
        with REAL_OPEN(plan_path, "w", encoding="utf-8") as f:
            json.dump(new, f, indent=1)
        return True, detail + " (not re-simulated)"
    # PD279(c): simulate a TEMP copy; plan_path is written only when the re-simulation is FINAL
    import tempfile
    import stagesim as SS
    # card 135-2 (docs/violation-decisions.md 2026-10-02 12:2x device): (1) base-graph COMPLETENESS gate before any simulation;
    # (2) the stage's sim step files are snapshotted and restored when the re-simulation is not FINAL (the plan file already is
    # written only on success, PD279(c)) - a failed rebase leaves every file it could touch byte-identical.
    cg = SS.completeness_gate(json.load(REAL_OPEN(base_path, encoding="utf-8")), uses={"actions": new.get("actions")})
    if cg["status"] == "FAIL":
        return False, detail + "; REBASE REFUSED: base-graph completeness FAIL {0}".format(
            json.dumps(dict((k, cg[k]) for k in ("bad_owner", "stuck", "inferred", "used") if cg.get(k)))[:600])
    detail += "; completeness {0}".format(cg["status"])
    tmp = tempfile.mkdtemp(prefix="rebase_")
    tp = os.path.join(tmp, os.path.basename(plan_path))
    with REAL_OPEN(tp, "w", encoding="utf-8") as f:
        json.dump(new, f, indent=1)
    kw = {"plan_out_dir": tmp, "log": log}
    if out_root:
        kw["out_root"] = out_root
    if model_dir:
        kw["model_dir"] = model_dir
    wg = SS.WriteGuard(dirs=(os.path.join(kw.get("out_root") or SS.SIM_ROOT, new.get("stage") or "plan"),))
    try:
        S = SS.simulate(tp, base_path, **kw)
        detail += "; re-simulated on the real base: final={0} failed={1}".format(S["final"], S["failed"])
        if not S["final"]:
            return False, detail + "; {0} NOT written (md5 {1} kept); sim step files restored {2}".format(
                rel(plan_path), md5(plan_path), wg.restore())
        outp = S["plan_out"]["path"]
        outp = outp if os.path.isabs(outp) else os.path.join(ROOT, outp)
        # card 133-3 (PD283(e), 133-1 first_fail): stagesim records the TEMP copy it simulated as finalized.plan_in; the
        # recipe's L0 needs the ORIGINAL stage input (`*_in.json`) - record it, and the temp copy's md5 under `rebase`.
        out = json.load(REAL_OPEN(outp, encoding="utf-8"))
        fz = out.setdefault("finalized", {})
        oin = (plan.get("finalized") or {}).get("plan_in") or {}
        op = oin.get("path") or rel(plan_path)
        opa = op if os.path.isabs(op) else os.path.join(ROOT, op)
        fz["rebase"] = {"sim_input": dict(fz.get("plan_in") or {}, path="(temp copy, deleted)"),
                        "from_plan": {"path": rel(plan_path).replace("\\", "/"), "md5": md5(plan_path)},
                        "graph": {"path": rel(graph_path).replace("\\", "/"), "md5": md5(graph_path)}}
        fz["plan_in"] = {"path": op.replace("\\", "/"), "md5": md5(opa) if os.path.isfile(opa) else oin.get("md5")}
        with REAL_OPEN(plan_path, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=1)
        return True, detail + "; plan_in kept = {0}".format(fz["plan_in"]["path"])
    except BaseException:
        wg.restore()                                   # card 135-2: an exception is a failed rebase too
        raise
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def record_stage_run(s, ck, card_id, cmd, by=COUNTED_BY, extra=None):
    rec = {"t": time.time(), "iso": time.strftime("%Y-%m-%d %H:%M:%S"), "cycle": ck, "stage": stage_key(s),
           "script": rel(s), "sha256": sha256(s), "card": card_id, "cap": RETRY_CAP, "by": by}
    rec.update(extra or {})
    with REAL_OPEN(STAGE_RUNS, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def record_started(cmdline, log=None, pid=None):
    """Called by tools/bgrun.py right after its child STARTED (Popen returned). Appends one COUNTED line per stage
    script / stagexec plan the child runs; returns the records ([] for any other command). The card id is the
    `--retry-card` judgement card when this run is past the cap (check_cap decides, as the hook did), else None;
    `retry_card_path` records the flag whenever it was given."""
    units = ([(s, None) for s in launched_stage_scripts(cmdline) + launched_vi_modifying(cmdline)]
             + launched_plan_runs(cmdline))
    if not units:
        return []
    runs, ck, out = read_stage_runs(), cycle_key(), []
    m = RETRY_CARD_RE.search(cmdline or "")
    for s, plan in units:
        _ok, _why, cid = check_cap(cmdline, plan or s, runs, ck)
        try:
            pat = pattern_signature(plan or s)       # card chat-P1 2a: the mechanism this run exercises
        except Exception:                                                          # noqa: BLE001
            pat = None
        out.append(record_stage_run(plan or s, ck, cid, cmdline, by=COUNTED_BY,
                                    extra={"log": rel(log) if log else None, "pid": pid,
                                           "retry_card_path": m.group(1) if m else None, "pattern": pat}))
        runs.append(out[-1])
    return out


# ------------------------------------------------------------------------------------ SCRATCH-VI VERIFICATION
# User 2026-09-27 02:2x ("도구 결함 관련하여 스크래치 vi 검증 부분도 적용"; card chat-N4, brief last section): when a stage's
# LAST TWO runs both failed on the SAME scripting function, the next LabVIEW act is a scratch-VI verification of that
# function, not a third stage run. The function is read from each run's own machine output, never from prose:
#   1. the innermost Python traceback frame inside gscript.py / stagekit.py / stagexec.py (stagekit.run prints the
#      traceback of any exception in the stage) -> "<module>.<function>";
#   2. else a stagexec `STEP-DIFF after real op K (<kind>, ...)` line -> "stagexec.op:<kind>";
#   3. else an op VI named in the C6 RESULT line's first_fail (`Op<Name>.vi`) -> "op:<Name>".
#   (No `"function"` field in the RESULT line: result-line/1 validation rejects extra keys - measured by the self-test.)
# A verification record is tools/bench/scratch_verify/<function>_<ts>.json, {"function": F, "status": "PASS", "t": epoch}
# (written with a RESULT line by a <=120-line stagekit script); it releases the stage only when NEWER than the second
# failure. Runs are grouped by stage key (`_vN` stripped), as the retry cap groups them.
SCRATCH_DIR = os.environ.get("SCRATCH_VERIFY_DIR") or os.path.join(BENCH, "scratch_verify")
SCRATCH_WINDOW_S = 3 * 24 * 3600      # logs older than this are not "the last two runs"
FLEET_MODULES = ("gscript", "stagekit", "stagexec")
TB_FRAME_RE = re.compile(r'File "([^"]+)", line \d+, in ([\w<>]+)')
STEPDIFF_RE = re.compile(r"STEP-DIFF after real op \d+ \((\w+)")
OPVI_RE = re.compile(r"\b(Op\w+)\.vi\b", re.I)
UNIT_TOKEN_RE = re.compile(r"([\w.\-]+\.(?:py|json))\b", re.I)


def unit_key(path):
    """Stage key of a script OR a stagexec plan: basename, lower case, `_vN` stripped (stage_key for .py)."""
    return re.sub(r"_v\d+(?=\.(?:py|json)$)", "", os.path.basename(path).lower())


def failure_function(seg):
    """The scripting function a failed run died in, from that run's own segment (see the block comment), or None."""
    import protocol as P
    res = P.all_result_lines(seg)
    frames = [(os.path.splitext(os.path.basename(f))[0], fn) for f, fn in TB_FRAME_RE.findall(seg or "")]
    fleet = [(m, fn) for m, fn in frames if m in FLEET_MODULES]
    if fleet:
        return "%s.%s" % fleet[-1]
    m = STEPDIFF_RE.search(seg or "")
    if m:
        return "stagexec.op:%s" % m.group(1)
    for d in reversed(res):
        m = OPVI_RE.search(str(d.get("first_fail") or ""))
        if m:
            return "op:%s" % m.group(1)
    return None


def stage_run_segments(key, now=None):
    """[(start_ts, failed, function)] of every bgrun run of stage `key` in LOG_DIR within SCRATCH_WINDOW_S, oldest
    first. A stage_prerun --dry/--prerun of the stage is not a run of it."""
    import protocol as P
    now = now or time.time()
    out = []
    try:
        entries = list(os.scandir(LOG_DIR))
    except OSError:
        return out
    for de in entries:
        if not de.name.endswith(".log"):
            continue
        try:
            if now - de.stat().st_mtime > SCRATCH_WINDOW_S:
                continue
            text = REAL_OPEN(de.path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for ts, line, seg in P.segments(text):
            if ts is None or "stage_prerun" in line:
                continue
            if key not in {unit_key(t) for t in UNIT_TOKEN_RE.findall(line)}:
                continue
            v = P.run_verdict(seg)
            if v["source"] == "none":
                continue                                       # still running: not a finished record
            out.append((ts, bool(v["failed"]), failure_function(seg) if v["failed"] else None))
    return sorted(out, key=lambda r: r[0])


def scratch_pass_after(function, t_after):
    """Newest scratch_verify PASS record for `function` newer than t_after: its path, or None."""
    best = None
    try:
        names = os.listdir(SCRATCH_DIR)
    except OSError:
        return None
    for fn in names:
        if not fn.endswith(".json"):
            continue
        p = os.path.join(SCRATCH_DIR, fn)
        try:
            d = json.load(REAL_OPEN(p, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if not isinstance(d, dict) or d.get("function") != function or d.get("status") != "PASS":
            continue
        t = d.get("t") if isinstance(d.get("t"), (int, float)) else os.path.getmtime(p)
        if t > t_after and (best is None or t > best[0]):
            best = (t, p)
    return best[1] if best else None


def check_scratch(unit, now=None):
    """(allow, why) - refuse a stage run whose last two runs failed on the same function with no newer scratch PASS."""
    key = unit_key(unit)
    runs = stage_run_segments(key, now)
    if len(runs) < 2:
        return True, ""
    (t1, f1, fn1), (t2, f2, fn2) = runs[-2], runs[-1]
    if not (f1 and f2 and fn1 and fn1 == fn2):
        return True, ""
    hit = scratch_pass_after(fn1, t2)
    if hit:
        return True, ""
    return False, ("SCRATCH-VI GATE (user 2026-09-27, card chat-N4): the last two runs of {0} both FAILED in `{1}` "
                   "({2} and {3}). The next LabVIEW act is a scratch-VI verification of `{1}`, not a third stage run: a "
                   "<=120-line stagekit script on a minimal scratch VI that runs `{1}`, reads the graph back and writes "
                   "{4}/<function>_<ts>.json with {{\"function\": \"{1}\", \"status\": \"PASS\", \"t\": <epoch>}}. "
                   "No PASS record newer than the second failure exists.\n").format(
                       key, fn1, time.strftime("%m-%d %H:%M:%S", time.localtime(t1)),
                       time.strftime("%m-%d %H:%M:%S", time.localtime(t2)), rel(SCRATCH_DIR))


# ------------------------------------------------------------- card chat-P2 item 4: REPEATED FUNCTION -> SCRATCH VERIFY
# User 2026-09-28 ("1~4번 적용"; measured: cycle 118 spent 84 min escalating ONE function through Opus max and Fable
# low). When a card's first_fail names the SAME scripting function (gscript/stagekit/stagexec function, a stagexec op
# kind, or an op VI) as the previous failing attempt of that stage, the next card is the SCRATCH-VI VERIFICATION of that
# function at the SAME model rung - not an escalation to material-opus-max / material-fable-low. A model change does not
# fix a tool defect (cycles 95-101). Escalation stays for failures that are NOT a repeated tool function.
# "Previous failing attempt" is read from files only: (a) the result of the card the failed card itself re-issued
# (`retry_of_card`), and (b) the stage's own last two bgrun runs (check_scratch's rule), for every stage recipe the
# failed card names (retry_of, inputs, outputs). A scratch_verify PASS record for the function newer than the failure
# releases the escalation (the tool was verified; the failure is something else).
FF_FUNC_RE = re.compile(r"\b(gscript|stagekit|stagexec)\.((?:op:)?[A-Za-z_]\w*)")


def function_of_text(text):
    """The scripting function a first_fail / fact string names: '<module>.<fn>' | 'stagexec.op:<kind>' | 'op:<OpName>'."""
    m = FF_FUNC_RE.search(text or "")
    if m:
        return "%s.%s" % (m.group(1), m.group(2))
    m = STEPDIFF_RE.search(text or "")
    if m:
        return "stagexec.op:%s" % m.group(1)
    m = OPVI_RE.search(text or "")
    return "op:%s" % m.group(1) if m else None


def _result_of(card_id, cards_dir):
    try:
        d = json.load(REAL_OPEN(os.path.join(cards_dir, "result_%s.json" % card_id), encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def _card_of(card_id, cards_dir):
    try:
        d = json.load(REAL_OPEN(os.path.join(cards_dir, "task_%s.json" % card_id), encoding="utf-8"))
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def _stage_units(card):
    out = []
    for v in [card.get("retry_of")] + [x.get("path") if isinstance(x, dict) else x
                                       for x in (card.get("inputs") or []) + (card.get("outputs") or [])]:
        if isinstance(v, str) and re.search(r"(?:^|[\\/])stage_[\w.-]+\.py$", v.strip(), re.I):
            out.append(v.strip())
    return list(dict.fromkeys(out))


def escalation_route(card, cards_dir=None, now=None):
    """('scratch-verify', function, evidence) or ('escalate', None, why) for an ESCALATION card (`retry_of_card` set).
    Reads result_<retry_of_card>.json's first_fail and the previous failing attempt (see the block comment)."""
    import protocol as P
    cards_dir = cards_dir or P.CARDS_DIR
    old_id = card.get("retry_of_card")
    if not old_id:
        return "escalate", None, "not an escalation card (no retry_of_card)"
    old_res = _result_of(old_id, cards_dir)
    if not old_res or old_res.get("status") == "PASS":
        return "escalate", None, "result_%s.json absent or PASS" % old_id
    fn = function_of_text(str(old_res.get("first_fail") or ""))
    if not fn:
        return "escalate", None, "result_%s first_fail names no scripting function" % old_id
    try:
        t_fail = os.path.getmtime(os.path.join(cards_dir, "result_%s.json" % old_id))
    except OSError:
        t_fail = 0
    if scratch_pass_after(fn, t_fail):
        return "escalate", None, "%s has a scratch_verify PASS newer than result_%s" % (fn, old_id)
    old_card = _card_of(old_id, cards_dir) or {}
    prev_id = old_card.get("retry_of_card")
    if prev_id:
        prev = _result_of(prev_id, cards_dir)
        if prev and prev.get("status") != "PASS" and function_of_text(str(prev.get("first_fail") or "")) == fn:
            return "scratch-verify", fn, "result_%s and result_%s both failed in %s" % (prev_id, old_id, fn)
    for unit in _stage_units(old_card) + _stage_units(card):
        runs = stage_run_segments(unit_key(unit), now)
        if len(runs) >= 2:
            (t1, f1, fn1), (t2, f2, fn2) = runs[-2], runs[-1]
            if f1 and f2 and fn1 == fn2 == fn and not scratch_pass_after(fn, t2):
                return "scratch-verify", fn, "the last two runs of %s both failed in %s" % (unit_key(unit), fn)
    return "escalate", None, "%s failed once in %s; no previous failing attempt in the same function" % (old_id, fn)


# ------------------------------------------------------------- card chat-P3 item A: NO SCRATCH BUILD ON A PROVEN PATTERN
# User 2026-09-28 ("A는 실행"). Before this card every build step ran the recipe once on a byte copy of the bed (a
# tools/bench/stage_<x>_scratch.py wrapper, ~15 min, e.g. stage_d1_qrt_pool_scratch.py) and THEN the one real launch.
# WHERE THAT RULE LIVED (measured, card chat-P3): only in card pass-lines and plan text (task_116-2 P4, task_118-1/-2 P3,
# task_119-4 L2, task_121-2, d1-loop12-17-split-plan.md PD234(g)) - no gate ever refused a launch for a missing scratch
# run; check_scratch above is a different rule (two failures on one function). So the change is a DECISION FUNCTION the
# card writer and the launch gate both read, not a relaxed refusal:
#   scratch NOT required  <=> the recipe is a tools/recipes/stage_*.py AND proven_pattern (>= PROVEN_MIN other clean
#                             stages cover its signature) AND a dry + prerun PASS exist for its CURRENT sha256 + plan md5s
#                             AND no real launch of the stage failed in the SCRATCH_WINDOW_S log window;
#   otherwise required    (a new structure class is never proven; a failed real launch means no second skip).
# check_launch logs `SCRATCH-SKIP-PROVEN | <stage> | proven: <stages>` when it ALLOWS such a launch (stderr + SKIP_LOG);
# `--scratch-required <recipe>` prints the decision (exit 0 skip / 3 required). The Error List of a skipped launch is
# compared with the plan's own predicted new-item count (what the scratch run used to pin; 119-4 pinned 0 == predicted 0).
SKIP_LOG = os.environ.get("SCRATCH_SKIP_LOG") or os.path.join(BENCH, "jev_gate.log")


def scratch_requirement(recipe, runs=None, recs=None, now=None):
    """(required: bool, why: str, proven_stages: [..]) - see the block comment."""
    s = os.path.abspath(recipe)
    if not STAGE_RE.search(s):
        return True, "not a tools/recipes/stage_*.py recipe - the scratch rule is unchanged", []
    cu = census_unpredicted(s)                       # card 123-7 (PD247(e)): an unmeasured census needs the scratch run
    if cu:
        return True, "CENSUS-UNPREDICTED {0} - the scratch run measures the census before the ONE launch".format("; ".join(cu)), []
    key = unit_key(s)
    fails = [ts for ts, failed, _fn in stage_run_segments(key, now) if failed]
    if fails:
        return True, "a real launch of {0} FAILED ({1}) - no second skip".format(
            key, time.strftime("%m-%d %H:%M:%S", time.localtime(fails[-1]))), []
    runs = read_stage_runs() if runs is None else runs
    recs = read_records() if recs is None else recs
    ok, stages, sig = proven_pattern(s, runs, recs)
    if not ok:
        new = new_structure_classes(s, runs, recs, sig)
        return True, ("NEW structure class(es) {0} - no clean stage ran them".format(", ".join(new[:8])) if new else
                      "not a proven pattern ({0} clean other stage(s) {1}; needs {2})".format(
                          len(stages), stages, PROVEN_MIN)), stages
    sha, pm = sha256(s), plan_md5s(s)
    missing = [k for k in ("dry", "prerun") if not any(
        r.get("kind") == k and r.get("status") == "PASS" and r.get("sha256") == sha and r.get("plan_md5s") == pm
        and not r.get("replay") for r in recs)]
    if missing:
        return True, "proven, but no {0} PASS for the current sha256 {1}... / plan md5s".format(
            " + ".join(missing), (sha or "")[:12]), stages
    return False, "proven: " + ", ".join(stages), stages


def scratch_skip_log(line):
    sys.stderr.write(line + "\n")
    try:
        with REAL_OPEN(SKIP_LOG, "a", encoding="utf-8") as fh:
            fh.write(line + "\n")
    except OSError:
        pass


ADOPT_LOG = os.environ.get("ADOPT_LOG") or os.path.join(BENCH, "adopted_scratch.jsonl")   # card chat-S4 A (stagexec.ADOPT_LOG)


def adopted_record(script, pm):
    """card chat-S4 A: stagexec.adopted_launch over ADOPT_LOG (None when nothing is adopted or stagexec cannot load)."""
    if not os.path.exists(ADOPT_LOG):
        return None
    try:
        import stagexec as SX
    except Exception:                                                              # noqa: BLE001
        return None
    return SX.adopted_launch(script, pm, path=ADOPT_LOG)


def check_launch(cmd):
    """(allow, why). Refuses a stage-recipe launch without a dry PASS and a prerun PASS for its CURRENT sha256 and
    plan md5s, both newer than the newest failing run of it (decision 4), and past RETRY_CAP runs in this cycle
    without a judgement card. It RECORDS NOTHING: a run is recorded in ONE place, record_started() called by
    tools/bgrun.py at child start (card 78-2; card chat-L2 removed the old `record=True` path, whose lines carried
    `by: check_launch` and were never counted - a second recorder that looked like the first)."""
    units = ([(s, None) for s in launched_stage_scripts(cmd) + launched_vi_modifying(cmd)]
             + launched_plan_runs(cmd))
    if not units:
        return True, ""
    ok_all, why_all = _check_units(units, cmd)
    if not ok_all:
        cls = [s for s, plan in units if not plan and not STAGE_RE.search(s.replace("\\", "/"))]
        if cls:
            why_all = ("[classifier stage_prerun.is_vi_modifying (card chat-N1): {0} imports stagekit and calls {1} "
                       "- gated like tools/recipes/stage_*.py] ").format(
                           ", ".join(rel(s) for s in cls), ", ".join(vi_modifying_calls(cls[0]))) + why_all
    return ok_all, why_all


def _check_units(units, cmd):
    """check_launch's per-unit decision (dry + prerun records, decision 4, RETRY_CAP), unchanged by card chat-N1."""
    recs = read_records()
    runs, ck = read_stage_runs(), cycle_key()
    for s, plan in units:
        if not os.path.isfile(s) or (plan and not os.path.isfile(plan)):
            return False, "launch gate: {0} does not exist".format(rel(plan or s))
        prov = provisional_plans(s, plan)                 # card chat-P1 item 1: a plan on a SIMULATED base never runs
        if prov:
            return False, ("LAUNCH GATE (card chat-P1 pipeline): {0} is planned on a PROVISIONAL base (stagesim's end graph "
                           "of the previous stage, base.sim_of {1}). Read the previous stage's SAVED artefact into a graph "
                           "and rebase first:\n  py tools/stage_prerun.py --rebase {0} --graph <real graph JSON>\n"
                           "then re-run --dry and --prerun (the plan md5 changes).\n").format(
                               rel(prov[0][0]), prov[0][1])
        sha, pm = sha256(s), ({rel(plan): md5(plan)} if plan else plan_md5s(s))
        what = rel(plan) if plan else rel(s)             # a plan run is pre-run BY ITS PLAN (card chat-S3)
        ad = adopted_record(plan or s, pm)               # card chat-S4 A: an adopted scratch IS the stage result
        if ad:
            return False, ("LAUNCH GATE (card chat-S4 A, user 2026-10-03 \"A 도입\"): {0} was ADOPTED from the scratch run {1} "
                           "({2}): its saved file {3} (md5 {4}) IS this stage's result for plan md5s {5}; a second run of the same "
                           "ops on the bed is refused. To run it again a judgement session marks that line of {6} "
                           "\"revoked\": true with the reason.\n").format(
                               what, ad.get("log"), ad.get("iso"), (ad.get("artefact") or {}).get("path"),
                               (ad.get("artefact") or {}).get("md5"), pm, rel(ADOPT_LOG))
        ok = {}
        named_ok, named_why = unverified_card_names(cmd)
        uv_refused, old_rule = [], []
        for kind in ("dry", "prerun"):
            m = [r for r in recs if r.get("kind") == kind and r.get("sha256") == sha and r.get("plan_md5s") == pm
                 and not r.get("replay") and r.get("status") in (("PASS", "PASS-UNVERIFIED") if kind == "dry" else ("PASS",))]
            if kind == "dry":
                # card 134-2 (PD288(c)): a dry recorded under the OLD rule (before PD287(a): a FALSE gate on simulated data
                # was downgraded to UNVERIFIED and PASSed - the rule that hid FR) is no evidence; only dry_rule == DRY_RULE counts
                old_rule = [r for r in m if r.get("dry_rule") != DRY_RULE]
                m = [r for r in m if r.get("dry_rule") == DRY_RULE]
            if kind == "dry":                       # card 134-1 (PD287(a)): PASS-UNVERIFIED needs the card's naming
                keep = []
                for r in m:
                    left = [u for u in r.get("unverified") or [] if not any(u.startswith(n) for n in named_ok)] \
                        if r.get("status") == "PASS-UNVERIFIED" else []
                    (uv_refused.append((r, left)) if left else keep.append(r))
                m = keep
            ok[kind] = max((r["t"] for r in m), default=None)
        if ok["dry"] is None and uv_refused:
            r, left = max(uv_refused, key=lambda x: x[0]["t"])
            return False, ("LAUNCH GATE (card 134-1, PD287(a)): {0}'s newest dry is PASS-UNVERIFIED ({1}); the gates {2} were "
                           "never evaluated on non-stub data. Name each as expected in the bound card (a `rules`/`pass` "
                           "string 'DRY-UNVERIFIED-OK: <label prefix>; ...') and pass `--unverified-card <card path>` on "
                           "the command{3}.\n").format(rel(s), r.get("iso"), left,
                                                       (" (" + named_why + ")") if named_why else "")
        missing = [k for k, v in ok.items() if v is None]
        if ok["dry"] is None and old_rule:
            return False, ("LAUNCH GATE (card 134-2, PD288(c)): {0}'s dry PASS ({1}) was recorded under dry rule {2}, not "
                           "dry_rule == {3} (a FALSE gate on simulated data now fails the dry). Re-dry (offline, seconds):\n"
                           "  py tools/stage_prerun.py --dry {0}\n").format(
                               what, max(old_rule, key=lambda r: r["t"]).get("iso"),
                               max(old_rule, key=lambda r: r["t"]).get("dry_rule", 1), DRY_RULE)
        if missing:
            return False, ("LAUNCH GATE (CLAUDE.md §3 'Stages are SIMULATED', decisions 1/2): {0} has no {1} PASS "
                           "record for sha256 {2}... and plan md5s {3}. Run first:\n  py tools/stage_prerun.py --dry {0}\n"
                           "  py tools/stage_prerun.py --prerun {0}\n").format(what, " + ".join(missing), sha[:12], pm)
        t_ok = min(ok.values())
        bad = last_failed_run_after(s, t_ok)
        if bad:
            return False, ("LAUNCH GATE (decision 4): {0} FAILED after its pre-run records ({1}: {2}); the records are "
                           "invalid - pre-run it again.\n").format(what, bad[0], bad[2])
        ok_cap, why_cap, _cid = check_cap(cmd, plan or s, runs, ck)
        if not ok_cap:
            return False, why_cap
        ok_sv, why_sv = check_scratch(plan or s)          # card chat-N4: two failures on one function -> scratch VI
        if not ok_sv:
            return False, why_sv
        if not plan and STAGE_RE.search(s):             # card chat-P3 item A: record a skipped scratch build
            try:
                req, _why_r, st_r = scratch_requirement(s, runs=runs, recs=recs)
            except Exception:                                                      # noqa: BLE001 - advisory only
                req, st_r = True, []
            if not req:
                scratch_skip_log("SCRATCH-SKIP-PROVEN | {0} | proven: {1} | {2}".format(
                    stage_key(s), ", ".join(st_r), time.strftime("%Y-%m-%d %H:%M:%S")))
    return True, ""


# ---------------------------------------------------------------------------------------------- CLI
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry")
    ap.add_argument("--prerun")
    ap.add_argument("--graph")
    ap.add_argument("--no-record", action="store_true")
    ap.add_argument("--json-out")
    ap.add_argument("--check-launch")
    ap.add_argument("--scratch-required", help="card chat-P3: is the scratch build required before this stage recipe's "
                                               "one launch? exit 0 = skip (SCRATCH-SKIP-PROVEN) / 3 = required")
    ap.add_argument("--control-lint", help="control_path_lint one stageplan/1 JSON (exit 0 clean / 2 refused)")
    ap.add_argument("--selftest-control-lint", action="store_true")
    ap.add_argument("--buildarray-check", nargs="+", help="card 114-1: X11 replay over stageplan/1 files (exit 0/2)")
    ap.add_argument("--opmodel-conformance", nargs="*", help="card 115-1: X13 over these stageplan ops (none = every "
                                                            "opmodels/*.json); exit 0 / 2 on a FAILED sample")
    ap.add_argument("--disable", help="with --opmodel-conformance: 'cfw_border_rule' = the A2 negative run")
    ap.add_argument("--rebase", help="card chat-P1: re-bind a stageplan planned on a PROVISIONAL base (needs --graph = "
                                     "the real graph read of the previous stage's saved artefact); exit 0 / 2")
    ap.add_argument("--no-sim", action="store_true", help="with --rebase: do not re-simulate (self-tests)")
    # card 103-1: unknown arguments pass through to the recipe's own sys.argv (e.g. stage_d1_disp.py `--stop-after 40`,
    # PART-A mode), so a recipe mode can be dry-run / pre-run exactly as it will be launched; they must follow the recipe.
    a, rest = ap.parse_known_args(argv)
    if rest and not (a.dry or a.prerun):
        ap.error("unrecognized arguments: %s" % " ".join(rest))
    if a.selftest_control_lint:
        return _selftest_control_lint()
    if a.control_lint is not None:
        b = control_path_lint(json.load(open(a.control_lint, encoding="utf-8")))
        print("\n".join(b) or "CLEAN")
        return 2 if b else 0
    if a.opmodel_conformance is not None:
        # card 115-1 A2/A3: X13 over named ops (none = every opmodels/*.json); exit 0 no FAIL / 2 a sample FAILED
        dis = tuple(x for x in (a.disable or "").split(",") if x)
        c = opmodel_conformance(a.opmodel_conformance or None, disable=dis, log=print)
        for fn, v in sorted(c["files"].items()):
            print("FILE {0}: {1} ({2} sample(s)){3}".format(fn, v["status"], v["samples"], "".join(
                " | FAIL(sample {0}, field {1}: measured {2} simulated {3})".format(x["sample"], x["field"], x["measured"],
                                                                                 x["simulated"]) for x in v["fails"])))
        for w_ in c["warns"]:
            print("WARN {0}".format(w_))
        import protocol as P
        nf = len([v for v in c["files"].values() if v["status"] == "FAIL"])
        npf = len([v for v in c["files"].values() if v["status"] == "PASS"])     # no-samples / not-replayed are not a pass
        first = next(("X13 {0} sample {1} field {2}".format(x["file"], x["sample"], x["field"]) for x in c["fails"]), None)
        print(P.result_line(P.make_result(npf, nf, first)), flush=True)
        return 2 if c["fails"] else 0
    if a.buildarray_check:
        # card 114-1 S0b: replay X11 over plan files; prints every flag (licensed ones marked), exit 2 on an unlicensed one
        unl = 0
        for p in a.buildarray_check:
            fl = buildarray_open_sibling(json.load(open(p, encoding="utf-8")), licences=pb_licences(p))
            for x in fl:
                unl += not x["licensed"]
                print("FLAG {0} row {1} node #{2} wired {3!r} open sibling {4} licensed {5}".format(
                    rel(p), x["row"], x["node"], x["wired"], x["open"], x["licensed"]))
            if not fl:
                print("CLEAN {0}".format(rel(p)))
        return 2 if unl else 0
    if a.rebase:
        import protocol as P
        if not a.graph:
            ap.error("--rebase needs --graph <real graph JSON of the previous stage's saved artefact>")
        try:
            ok, why = rebase(os.path.abspath(a.rebase), os.path.abspath(a.graph), simulate=not a.no_sim)
        except Exception as e:                                                     # noqa: BLE001
            ok, why = False, "rebase raised {0}: {1}".format(type(e).__name__, str(e)[:300])
        print(("REBASED " if ok else "") + why, flush=True)
        arts = [{"path": rel(os.path.abspath(a.rebase)), "md5": md5(os.path.abspath(a.rebase))}] if ok else []
        print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else why[:200], arts)), flush=True)
        return 0 if ok else 2
    if a.check_launch is not None:
        ok, why = check_launch(a.check_launch)
        print("ALLOW" if ok else why)
        return 0 if ok else 2
    if a.scratch_required is not None:
        req, why, st_ = scratch_requirement(a.scratch_required)
        print("SCRATCH-REQUIRED | {0} | {1}".format(stage_key(a.scratch_required), why) if req else
              "SCRATCH-SKIP-PROVEN | {0} | proven: {1}".format(stage_key(a.scratch_required), ", ".join(st_)))
        return 3 if req else 0
    recipe = a.dry or a.prerun
    if not recipe:
        ap.error("--dry, --prerun or --check-launch")
    recipe = os.path.abspath(recipe)
    if is_stageplan(recipe):
        # card chat-S3: a FINAL stage plan is launched by tools/stagexec.py; its dry run is the executor on the
        # simulated backend, its pre-run is stagexec.prerun_plan (final, step files intact, compiles, dry PASS)
        import stagexec as SX
        import protocol as P
        if a.dry:
            st, ff, _ex = SX.dry_run(recipe, log=lambda *_x: None)
            npass, nfail = int(st == "PASS"), int(st != "PASS")
        else:
            g_, ok = SX.prerun_plan(recipe)
            cpl = control_path_lint(json.load(open(recipe, encoding="utf-8")))
            g_ = list(g_) + [("X8 control_path_lint (CLAUDE.md 1c'')", not cpl, "; ".join(cpl)[:600] or "clean")]
            bao = [x for x in buildarray_open_sibling(json.load(open(recipe, encoding="utf-8")),
                                                      licences=pb_licences(recipe)) if not x["licensed"]]
            g_ = g_ + [("X11 Build Array half-wired vs open sibling (card 114-1)", not bao, json.dumps(bao)[:600] or "clean")]
            # card 115-1 A1 (PD229(a)): X13 opmodel conformance of the plan's ops; WARN lines printed, never a pass reason
            x13_ok, x13_det, x13_w = x13_gate([json.load(open(recipe, encoding="utf-8"))])
            for w_ in x13_w:
                print("  WARN  {0}".format(w_), flush=True)
            g_ = g_ + [("X13 opmodel conformance (card 115-1)", x13_ok, json.dumps(x13_det, default=str)[:600])]
            print("  {0}  {1}  {2}".format("PASS" if x13_ok else "FAIL", g_[-1][0], g_[-1][2][:400]), flush=True)
            ok = ok and not cpl and not bao and x13_ok
            x16_ok, x16_det = x16_gate([json.load(open(recipe, encoding="utf-8"))])   # card 125-1 (PD251(b))
            g_ = g_ + [("X16 created-primitive terminals carry term_class (card 125-1)", x16_ok,
                        json.dumps(x16_det, default=str)[:600])]
            print("  {0}  {1}  {2}".format("PASS" if x16_ok else "FAIL", g_[-1][0], g_[-1][2][:400]), flush=True)
            ok = ok and x16_ok
            if census_check(recipe) is not None:            # card 123-7 (PD247(e)): census FAIL fails the prerun
                c_ok, c_det, _cl = census_gate([recipe], out=lambda s_: print(s_, flush=True))
                g_ = g_ + [("X15 census derived == declared (card 123-7)", c_ok, json.dumps(c_det, default=str)[:600])]
                ok = ok and c_ok
            # card chat-P1 item 4: X14 rows-per-step ADVISORY on the plan's own actions (never a gate)
            x14_advisory(recipe, len(json.load(open(recipe, encoding="utf-8")).get("actions") or []))
            st = "PASS" if ok else "FAIL"
            npass, nfail = sum(1 for x in g_ if x[1]), sum(1 for x in g_ if not x[1])
            ff = next((x[0] + ": " + x[2] for x in g_ if not x[1]), None)
        print("=== {0} (stagexec plan) {1}: first_fail={2}".format("DRY" if a.dry else "PRERUN", st, ff), flush=True)
        if not a.no_record:
            plan_record("dry" if a.dry else "prerun", recipe, st, ff)
        print(P.result_line(P.make_result(npass, nfail, ff, status=st)), flush=True)
        return 0 if st == "PASS" else 1
    real_stdout = sys.stdout
    sa = int(rest[rest.index("--stop-after") + 1]) if "--stop-after" in rest else None   # card 103-2: PART-A X5
    fk = int(rest[rest.index("--from-step") + 1]) if "--from-step" in rest else None     # card 103-4: PART-B X5
    D.__init__()   # card 128-4 (PD261(b)): D was never reset, so an in-process --dry then --prerun counted ops twice
    try:
        tr = prerun(recipe, a.graph, stop_after=sa, from_step=fk) if a.prerun else dry(recipe, a.graph)
    finally:
        # card 128-3 (result_128-1.json fact 8): install() sets builtins.open = dry_open (:601) and nothing restored it, so a
        # caller that ran main([--dry|--prerun, recipe]) IN-PROCESS had every later write outside %TEMP% redirected to SINK
        builtins.open = REAL_OPEN
    sys.stdout = real_stdout
    import protocol as P
    print("\n=== DRY {0}{7}: first_fail={1} coverage {2}/{3} lines, first mutation {4}, unverified {5}, graph {6}".format(
        tr["status"], tr["first_fail"], tr["coverage"][0], tr["coverage"][1], tr["first_mutation"],
        len(tr["unverified"]), tr["graph"], (" " + "; ".join(tr["unverified"])) if tr["status"] == "PASS-UNVERIFIED"
        else ""), flush=True)
    if not a.no_record:
        write_record("dry", recipe, tr["status"], tr["first_fail"], {"input_md5": tr["input_md5"], "graph": tr["graph"],
                                                                    "unverified": list(tr["unverified"]),
                                                                    "dry_rule": DRY_RULE})
    dpass = tr["status"] in ("PASS", "PASS-UNVERIFIED")
    status, npass, nfail, first = ("PASS" if dpass else tr["status"]), int(dpass), int(not dpass), tr["first_fail"]
    if a.prerun:
        pr = tr["prerun"]
        print("=== PRERUN {0}: {1} pass / {2} fail; first {3}".format(pr["status"], pr["pass"], pr["fail"], pr["first_fail"]))
        if not a.no_record:
            write_record("prerun", recipe, pr["status"], pr["first_fail"], {"input_md5": tr["input_md5"], "graph": tr["graph"],
                                                                         "stop_after": sa, "from_step": fk, "warn": pr.get("warn")})
        status, npass, nfail, first = pr["status"], pr["pass"], pr["fail"], result_first(pr["first_fail"], pr.get("warn"))
    if a.json_out:
        with REAL_OPEN(a.json_out, "w", encoding="utf-8") as f:
            json.dump(tr, f, indent=1, default=str)
    print(P.result_line(P.make_result(npass, nfail, first, status=status)), flush=True)
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    rc = main()
    sys.stdout.flush()
    os._exit(rc)
