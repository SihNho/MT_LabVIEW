"""selftest_c134_p1 - card 134-P1 pass 3/4: OFFLINE self-test of tools/bench/launch_p3b2_c135.py. No LabVIEW, no COM, nothing spawned
or killed (the runner's Dry executor), nothing written except this test's stdout.
T1 compare(102553, itself) EQUAL -> reuse plan b; T2 one changed terminal uid -> DIFFERENT -> refinalize; T3 one obj class changed ->
DIFFERENT; T4 fs_frames order swapped -> DIFFERENT; T5..T10 the dry walk of every branch: equal, different, fail-a, fail-graph, fail-b,
fail-el -> the expected child sequence and verdict; T11 the bytes the different branch restores (commit 0b72718d, filtered) == 1451ba90
(read only); T12 the runner and its children import no LabVIEW module at module level except the children's recipe imports (AST);
T13 graph child: the four substitutions apply exactly once on the pinned diag source.
Card 134-6 (PD291(d)): T14 gate B scoped (stagesim.fs_border_gate) on graph 102553 with plan b's uses PASS, 7 UNMEASURED listed; T15 a
use of one FAILS; T16 no NESTED_B / rc=1 acceptance left; T17 graph child rc 1 stops the chain; T18 the graph plan the runner writes."""
import ast, copy, hashlib, io, json, os, subprocess, sys, contextlib           # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, B)
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                         # noqa: E402
import launch_p3b2_c135 as L                                                 # noqa: E402
import launch_p3b2_c135_graph as LG                                          # noqa: E402
res = []


def t(name, ok, det=""):
    res.append((name, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", name, str(det)[:400]), flush=True)


REF = L.J(L.REF_GRAPH)
eq, d = L.compare(copy.deepcopy(REF), REF)
t("T1 compare(102553, itself) EQUAL -> plan b as is", eq and not d, d)
g2 = copy.deepcopy(REF); g2["terminals"][5]["term_uid"] = int(g2["terminals"][5]["term_uid"]) + 100000   # noqa: E702
eq, d = L.compare(g2, REF)
t("T2 one changed terminal uid -> DIFFERENT (terminals listed)", not eq and "terminals" in d, sorted(d))
g3 = copy.deepcopy(REF); g3["objs"][3]["class"] = "Changed"                                            # noqa: E702
eq, d = L.compare(g3, REF)
t("T3 one obj class changed -> DIFFERENT (node_classes)", not eq and list(d) == ["node_classes"], sorted(d))
g4 = copy.deepcopy(REF); g4["fs_measured"]["fs_frames"]["27509"] = list(reversed(g4["fs_measured"]["fs_frames"]["27509"]))   # noqa: E702
eq, d = L.compare(g4, REF)
t("T4 FS 27509 frame order swapped -> DIFFERENT (fs_frames)", not eq and list(d) == ["fs_frames"], sorted(d))
T5 = {"equal": (["gone", "A", "gone", "G", "gone", "B", "gone", "E", "gone"], 0, None),
      "different": (["gone", "A", "gone", "G", "gone", "write:launch_p3b2_c135_pre_plan_ring_p3b2b.json", "restore_pb", "F", "D", "P", "B", "gone", "E", "gone"], 0, None),
      "fail-a": (["gone", "A", "gone"], 1, "A session a"),
      "fail-graph": (["gone", "A", "gone", "G", "gone"], 1, "G graph read"),
      "fail-b": (["gone", "A", "gone", "G", "gone", "B", "gone"], 1, "B session b"),
      "fail-el": (["gone", "A", "gone", "G", "gone", "B", "gone", "E", "gone"], 1, "E2 total")}
for k, (br, (want, nf_min, first)) in enumerate(T5.items(), 5):
    X = L.Dry(br)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        gates, arts, state, ff = L.run(X, br)
    seq = [c for c in X.calls if not c.startswith("write:") or "pre_plan_ring_p3b2b" in c]
    nf = sum(1 for _n, c in gates if not c)
    okseq = all(w in seq for w in want) and [c for c in seq if c in ("A", "G", "B", "E", "F", "D", "P")] == [c for c in want if c in ("A", "G", "B", "E", "F", "D", "P")]
    okv = (nf == 0 and ff is None) if nf_min == 0 else (nf >= 1 and ff and ff.startswith(first))
    t("T{0} dry branch {1}: children {2}, first_fail {3!r}, {4} gates".format(k, br, [c for c in seq if c in "AGBEFDP"], ff, len(gates)),
      okseq and okv and (br != "equal" or state.get("compare") == "EQUAL") and (br != "different" or state.get("compare") == "DIFFERENT"),
      {"seq": seq, "fails": [n for n, c in gates if not c]})
flt = subprocess.run(["git", "cat-file", "--filters", "{0}:{1}".format(L.PB_COMMIT, L.PB)], cwd=ROOT, capture_output=True).stdout
t("T11 commit {0} filtered plan b bytes md5 == {1} (the different branch's restore; read only)".format(L.PB_COMMIT, L.PB_FINALIZE_PIN[:8]),
  hashlib.md5(flt).hexdigest() == L.PB_FINALIZE_PIN, hashlib.md5(flt).hexdigest())
LV = {"stagekit", "gscript", "stagexec", "win32com", "pythoncom"}


def top_imports(path):
    tree = ast.parse(open(path, encoding="utf-8").read())
    out = set()
    for n in tree.body:
        if isinstance(n, ast.Import):
            out |= set(a.name.split(".")[0] for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            out.add((n.module or "").split(".")[0])
    return out


ri = top_imports(os.path.join(B, "launch_p3b2_c135.py"))
t("T12 the runner imports no LabVIEW module at module level ({0})".format(sorted(ri & LV)), not (ri & LV), sorted(ri))
try:
    LG.patched_source(); ok13 = True                                                                  # noqa: E702
except SystemExit as e:
    ok13 = str(e)
t("T13 graph child: diag source pin + 4 substitutions exactly once", ok13 is True, ok13)
# ---- card 134-6 (PD291(d)): gate B scoped in the graph child, the runner's rc=1 special case removed
import stagesim as SS                                                                                 # noqa: E402
pb = L.J(L.PB)
fz = pb.get("finalized") or {}
gb = SS.fs_border_gate(REF, {"actions": pb.get("actions"), "fs_routes": fz.get("fs_routes"),
                             "route_check": (fz.get("route_check") or {}).get("rows"), "carried": REF.get("fs_carried")})
t("T14 gate B scoped on graph 102553 with plan b's uses: PASS, 7 UNMEASURED listed ({0})".format(gb["unmeasured"]),
  gb["status"] == "PASS" and len(gb["unmeasured"]) == 7 and not gb["used"], gb)
gb2 = SS.fs_border_gate(REF, {"actions": [{"op": "wire", "via": gb["unmeasured"][0]}]})
t("T15 gate B FAILS when a plan uses an UNMEASURED tunnel ({0})".format(gb["unmeasured"][0]), gb2["status"] == "FAIL", gb2["used"])
src = open(os.path.join(B, "launch_p3b2_c135.py"), encoding="utf-8").read()
t("T16 runner: no NESTED_B, no rc=1 acceptance", "NESTED_B" not in src and "rc=1 by design" not in src)


class DryRc1(L.Dry):
    """graph child prints all gates PASS but exits rc 1 -> the runner must stop at G (no special case left)."""
    def __init__(self, br):
        L.Dry.__init__(self, br); self.wrote = {}                                                     # noqa: E702

    def child(self, step, extra=None):
        rc, seg = L.Dry.child(self, step, extra)
        return (1, seg) if step == "G" else (rc, seg)

    def write(self, path, data):
        L.Dry.write(self, path, data); self.wrote[os.path.basename(path)] = copy.deepcopy(data)       # noqa: E702


X = DryRc1("equal")
with contextlib.redirect_stdout(io.StringIO()):
    gates, arts, state, ff = L.run(X, "equal")
t("T17 graph child rc 1 with all-PASS lines -> chain stops at G ({0!r})".format(ff), ff and ff.startswith("G graph read") and "B" not in X.calls, X.calls)
gp = X.wrote.get("launch_p3b2_c135_graph_plan.json") or {}
t("T18 runner's graph plan: same_rows_as null, fs_watch null, uses_plan == plan b",
  gp.get("input", {}).get("same_rows_as") is None and "same_rows_as" in gp.get("input", {}) and gp.get("fs_watch") is None
  and gp.get("uses_plan") == L.PB, {k: gp.get(k) for k in ("input", "fs_watch", "uses_plan")})
nf =sum(1 for _n, c in res if not c)
print(P.result_line(P.make_result(len(res) - nf, nf, next((n for n, c in res if not c), None))), flush=True)
sys.exit(1 if nf else 0)
