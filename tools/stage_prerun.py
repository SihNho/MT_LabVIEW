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
  X5 wiring ops executed in the dry run == plan wire rows
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
     the dry run built (r7 stopped IN op 41 on it: stage_d1_disp_r7.log:807)
  X10 (card 106-3, retrospective-cycle103 inference-over-measurement) the predicted LabVIEW private-MB peak over the
     dispatched ops, from the RECORDED per-op meter of an earlier run of the same recipe (stagexec.mem_predict), is
     below X10_FAIL_MB 690 (card 106-5, PD219(c): error 2 was seen at 695 MB; MEMSTOP stagexec.MEM_STOP_MB 700 stays
     the run-time guard); no covering record = UNMEASURED: `X10 WARN unmeasured` in the output and the RESULT line, pass.
     Without --graph the dry uses the recipe's plan base graph (find_graph / plan_base_graphs, card 106-5).
     Self-test of X9/X10: tools/bench/selftest_stage_prerun_c106c.py
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
import glob
import hashlib
import io
import json
import os
import re
import shlex
import sys
import time
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
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
        self.mutated = None                  # first mutating call name
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
        self._t()
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


def _graph():
    if D.graph is None:
        p = D.graph_override or (find_graph(D.input_md5, plan_base_graphs(D.recipe) if D.recipe else ())
                                 if D.input_md5 else None)                       # card 106-5: the plan's base graph
        D.graph_path = p
        D.graph_error = None
        if not p and not D.graph_override and FIND_SKIPPED:
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
    real_cands = JC.candidates

    def cands(G, intent, *a, **k):
        D.jev.append({"via": "candidates", "intent": _plain(intent)})
        return real_cands(G, intent, *a, **k)
    JC.candidates = cands
    real_mod = K.mod

    def mod(name):
        m = real_mod(name)
        return m if name in PURE_MODS else wrap_module(m)
    K.mod = mod
    S = K.Stage
    orig = dict((k, getattr(S, k)) for k in ("__init__", "gate", "_op", "address"))

    def init(self, *a, **k):
        orig["__init__"](self, *a, **k)
        self.out_json = os.path.join(SINK, os.path.basename(self.out_json))
        D.input_md5, D.input_vi = self.input_md5, self.input_vi
        D.works.append(self.work)

    def gate(self, label, ok, detail="", fatal=False):
        if isinstance(ok, Fake):
            D.gate_taint = D.taint
            D.unverified.append(label)
            print("  UNVERIFIED  {0}  (dry: stub value)".format(label), flush=True)
            return True
        ok = bool(ok)
        tainted = D.taint != D.gate_taint
        D.gate_taint = D.taint
        if not ok and (D.mutated or tainted):
            D.unverified.append(label)
            print("  UNVERIFIED  {0}  (dry: {1})".format(label, "after mutation " + D.mutated if D.mutated
                                                          else "read stub data"), flush=True)
            return False
        if not ok:
            D.fails.append("GATE " + label)
        return orig["gate"](self, label, ok, detail, fatal)

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

    S.__init__, S.gate, S._op, S.address = init, gate, op, address
    S.start, S.save, S.close, S.scratch, S.discard_work = start, save, close, scratch, discard_work
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
            return tracer
        return None
    t0 = time.time()
    if not D.fails:
        sys.settrace(tracer)
        try:
            runpy.run_path(path, run_name="__main__")
        except SystemExit:
            pass
        except BaseException as e:                                                 # noqa: BLE001
            D.fails.append("PY {0}: {1} (module level)".format(type(e).__name__, str(e)[:160]))
        finally:
            sys.settrace(None)
    status = "PASS" if (D.reached_end and not D.fails) else "FAIL"
    first = D.fails[0] if D.fails else (None if D.reached_end else "STUB-LIMIT: " + str(D.stub_limit)
                                        if D.stub_limit else "body did not reach its end")
    return {"status": status, "first_fail": first, "fails": D.fails, "unverified": D.unverified,
            "stub_limit": D.stub_limit, "reached_end": D.reached_end, "first_mutation": D.mutated,
            "coverage": [len(hit & code_lines), len(code_lines)], "ops": D.ops, "addresses": D.addresses,
            "jev": D.jev, "graph": rel(D.graph_path) if D.graph_path else None, "input_md5": D.input_md5,
            "input_vi": D.input_vi, "blocked": sorted(set(D.blocked)), "secs": round(time.time() - t0, 1),
            "calls": len(D.calls), "works": list(D.works)}


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
    return sorted(set(plans)), sorted(set(named))


SP_WIRING = ("tunnel", "connect", "wire_sr", "branch")     # stagexec compiled-op kinds that make a wire
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
def verb_preconditions(plans, sps, work, move_dst, stop_after=None, from_step=None):
    """X9 (retrospective-cycle102 `wrong-ordering`): every op / row the run DISPATCHES whose verb holds a precondition on
    the stage's own work file (stagexec.ROUTE_PRECONDITIONS: copy_in needs work == gscript.MOVE_DST) is checked OFFLINE
    against the Stage the dry run built. stageplan/1 files are read raw (checked even when stageplan_check refused them);
    decisions-row plans: every `copy` row (stagekit.run_rows -> copy_in). -> list of failure strings."""
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
        else:
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
X10_FAIL_MB = 690.0


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


def prerun(recipe, graph=None, stop_after=None, from_step=None):
    """card 103-2 (PD216(b)): stop_after=k (the recipe's own `--stop-after k`, PART-A mode) makes X5 expect only the
    stageplan wiring real ops 1..k - exactly the ops the run dispatches; the wire-action COVERAGE check stays over the
    whole compiled plan. stop_after=None: X5 unchanged."""
    tr = dry(recipe, graph)
    gates = []

    def gate(label, ok, detail=""):
        gates.append((label, bool(ok), detail))
        print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)
    gate("X1 dry run PASS (whole Python path, COM stubbed)", tr["status"] == "PASS", tr["first_fail"])
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
    wires = [r for r in rows if r.get("action") == "wire"]
    ops = [v for v in tr["ops"] if WIRE_VERB_RE.search(v)]
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
        wk = wo if stop_after is None and from_step is None else [
            o for k, o in enumerate(ops_ or [], 1) if o["kind"] in SP_WIRING and k <= int(stop_after or len(ops_ or []))
            and k > int(from_step or 0)]
        sp_wops, sp_wact = sp_wops + len(wk), sp_wact + len(wa)
        sp_cov += len(wa & set(x for o in wo + so for x in o["acts"]))
    gate("X5 wiring ops executed in the dry run == plan wire rows", plans and not sp_bad and len(ops) == len(wires) + sp_wops
         and sp_cov == sp_wact, "ops {0} vs plan wire rows {1} + stageplan wiring real ops {2}{5} (covering {3}/{4} wire actions)"
         .format(len(ops), len(wires), sp_wops, sp_cov, sp_wact,
                 ("" if stop_after is None else " among ops 1..{0} (PART-A stop_after)".format(int(stop_after))) +
                 ("" if from_step is None else " among ops {0}.. (PART-B from_step)".format(int(from_step) + 1))))
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
    vp = verb_preconditions(plans, sps, wk, mdst, stop_after, from_step)
    gate("X9 every dispatched verb's precondition holds offline (copy_in: work == gscript.MOVE_DST)", plans and not vp,
         vp[:6] or "work {0}".format(wk))
    # card 106-3: X10 memory margin from the recorded per-op meter (retrospective-cycle103 inference-over-measurement)
    mm = mem_margin(recipe, stop_after, from_step)
    tr["mem_margin"] = mm
    # card 106-5 (PD219(c)): fail at a predicted checkpoint >= X10_FAIL_MB (690); no covering record = WARN, pass
    gate("X10 predicted LabVIEW private MB < {0} (error-2 point; MEMSTOP {1}) over the ops this run dispatches ({2})".format(
        round(mm.get("memstop") - mm.get("margin_mb"), 1), mm.get("memstop"),
        "UNMEASURED - no covering record" if mm["ok"] is None else mm.get("how")), mm["ok"] is not False,
        dict((k, mm.get(k)) for k in ("peak_mb", "at", "headroom_mb", "window", "source", "why") if mm.get(k) is not None))
    warn = "X10 WARN unmeasured: {0}".format(mm.get("why")) if mm["ok"] is None else None
    if warn:
        print("  WARN  {0}".format(warn), flush=True)
    npass = sum(1 for g_ in gates if g_[1])
    first = next((g_[0] + ": " + str(g_[2])[:120] for g_ in gates if not g_[1]), None)
    tr["prerun"] = {"status": "PASS" if npass == len(gates) else "FAIL", "gates": [[a, b, str(c)[:600]] for a, b, c in gates],
                    "first_fail": first, "plans": dict((rel(p), md5(p)) for p in plans), "pass": npass,
                    "fail": len(gates) - npass, "warn": warn}
    return tr


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
    is joined first, so a continued command stays one."""
    out = []
    joined = re.sub(r"(?:\\|`)[ \t]*\r?\n", " ", cmd or "")
    segs = re.split(r"\s*(?:&&|\|\||;|\||\r?\n)\s*", joined)
    for seg in segs:
        try:
            toks = shlex.split(seg, posix=False)
        except ValueError:
            toks = seg.split()
        toks = [t.strip("\"'") for t in toks]
        i = 0
        while i < len(toks):
            b = os.path.basename(toks[i]).lower()
            if re.match(r"^py(thon)?[\d.]*(\.exe)?$", b):
                j = i + 1
                while j < len(toks) and toks[j].startswith("-"):
                    j += 2 if toks[j] in ("-X", "-W", "-m") else 1
                if j < len(toks):
                    p = toks[j]
                    ap = p if os.path.isabs(p) else os.path.join(ROOT, p)
                    if p.lower().endswith(".py"):
                        out.append(os.path.normpath(ap))
                    i = j + 1
                    continue
            i += 1
    return out


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


def last_failed_run_after(script, t_min):
    """Newest failing bgrun run of `script` in a log modified after t_min (protocol.run_verdict)."""
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
        out.append(record_stage_run(plan or s, ck, cid, cmdline, by=COUNTED_BY,
                                    extra={"log": rel(log) if log else None, "pid": pid,
                                           "retry_card_path": m.group(1) if m else None}))
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
        sha, pm = sha256(s), ({rel(plan): md5(plan)} if plan else plan_md5s(s))
        what = rel(plan) if plan else rel(s)             # a plan run is pre-run BY ITS PLAN (card chat-S3)
        ok = {}
        for kind in ("dry", "prerun"):
            m = [r for r in recs if r.get("kind") == kind and r.get("sha256") == sha and r.get("status") == "PASS"
                 and r.get("plan_md5s") == pm and not r.get("replay")]
            ok[kind] = max((r["t"] for r in m), default=None)
        missing = [k for k, v in ok.items() if v is None]
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
    ap.add_argument("--control-lint", help="control_path_lint one stageplan/1 JSON (exit 0 clean / 2 refused)")
    ap.add_argument("--selftest-control-lint", action="store_true")
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
    if a.check_launch is not None:
        ok, why = check_launch(a.check_launch)
        print("ALLOW" if ok else why)
        return 0 if ok else 2
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
            ok = ok and not cpl
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
    tr = prerun(recipe, a.graph, stop_after=sa, from_step=fk) if a.prerun else dry(recipe, a.graph)
    sys.stdout = real_stdout
    import protocol as P
    print("\n=== DRY {0}: first_fail={1} coverage {2}/{3} lines, first mutation {4}, unverified {5}, graph {6}".format(
        tr["status"], tr["first_fail"], tr["coverage"][0], tr["coverage"][1], tr["first_mutation"],
        len(tr["unverified"]), tr["graph"]), flush=True)
    if not a.no_record:
        write_record("dry", recipe, tr["status"], tr["first_fail"], {"input_md5": tr["input_md5"], "graph": tr["graph"]})
    status, npass, nfail, first = tr["status"], int(tr["status"] == "PASS"), int(tr["status"] != "PASS"), tr["first_fail"]
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
