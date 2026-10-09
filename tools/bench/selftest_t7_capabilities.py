# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_chat-T7.md
# ---
r"""selftest_t7_capabilities - card chat-T7 item 6 (user 2026-10-09 "전부 적용", "갱신은 훅으로"): the function LIST of
docs/toolkit-capabilities.md chosen by the IMPORT GRAPH (tools/gen_capabilities.py shared_files / module_functions / render_list), its
DETACHED regeneration from tools/hooks/guard_write.py (capabilities_regen + gen_capabilities --hook-run) and the cycle-end line of
tools/cycle_runner.py (capabilities_hook). No LabVIEW; every write goes to a temp copy of the doc (the shared-set cache is the real one).
PREDICTION: G1 a temp tree's shared set = the two imported files (static import + K.mod("x") string form), never a self-import or an
un-imported file; G2 public functions / class methods / docstring first line / named self-test per row, `_private` absent; G3 the real tree:
stagekit, gscript, protocol, stage_prerun and >= 30 bench files shared, the scan < 20 s, the cache lists them; G4 write() twice is a no-op
the second time and keeps one fn-table and one fn-list block;
H1 a write to a SHARED file -> 'started', the detached run regenerates the temp doc (fn-list block present), lock released;
H2 a write to a NON-shared file -> 'not-shared', no lock, no new log line; H3 two writes in a row -> 'started' + 'rerun-flagged',
then exactly one run + one re-run in the log, lock released, flag cleared;
C1 cycle_runner.capabilities_hook logs ONE 'CAPABILITIES | ... | regenerated ... | drift ...' line on the temp doc; C2 a broken generator
-> a FAILED line, no exception."""
import importlib.util, json, os, shutil, subprocess, sys, tempfile, time       # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, "tools")
sys.path[:0] = [TOOLS]
GATES = []


def gate(label, ok, detail=""):
    GATES.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def put(root, rel, text):
    p = os.path.join(root, rel.replace("/", os.sep))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(text)


def tree_cases(GC, tmp):
    r = os.path.join(tmp, "tree")
    put(r, "tools/a.py", 'import os\nimport a\n\n\ndef f(x, y=2):\n    """Adds. Self-test: selftest_a.py."""\n    return x\n\n\n'
                         'def _hidden():\n    return 1\n\n\nclass Box(object):\n    """A box."""\n    def put(self, v):\n        """Put v."""\n\n    def _p(self):\n        pass\n')
    put(r, "tools/b.py", "import os, a as AA  # uses a\n")
    put(r, "tools/bench/c.py", '"""c"""\n\n\ndef g():\n    pass\n')
    put(r, "tools/recipes/d.py", "import stagekit as K\nC = K.mod(\"c\")\n")
    put(r, "tools/e.py", "def lonely():\n    pass\n")
    sh = GC.shared_files(r)
    gate("G1 temp tree: shared = {tools/a.py: [tools/b.py], tools/bench/c.py: [tools/recipes/d.py]} (self-import and un-imported e.py excluded)",
         sh == {"tools/a.py": ["tools/b.py"], "tools/bench/c.py": ["tools/recipes/d.py"]}, sh)
    fa = GC.module_functions(os.path.join(r, "tools", "a.py"))
    gate("G2 module_functions: f(x, y=2) 'Adds. Self-test: selftest_a.py.' selftest_a.py; Box (class); Box.put; no _hidden / Box._p",
         [x[:4] for x in fa] == [("f", "x, y=2", "Adds. Self-test: selftest_a.py.", "selftest_a.py"), ("Box", "(class)", "A box.", ""),
                                 ("Box.put", "v", "Put v.", "")], fa)
    txt = GC.render_list(r)
    gate("G2b render_list: TOC row per shared file, a section per file, bench file marked, 'no docstring' counted",
         txt.startswith(GC.LIST_BEGIN) and txt.rstrip().endswith(GC.LIST_END) and "### tools/a.py" in txt and "### tools/bench/c.py" in txt
         and "move to tools/ later" in txt and "| `g` |  | (no docstring) |" in txt, txt[:400])


def real_cases(GC, tmp):
    t0 = time.time()
    sh = GC.shared_files()
    dt = time.time() - t0
    tools_n = sum(1 for p in sh if p.startswith("tools/") and p.count("/") == 1)
    bench_n = sum(1 for p in sh if p.startswith("tools/bench/"))
    need = ["tools/stagekit.py", "tools/gscript.py", "tools/protocol.py", "tools/stage_prerun.py"]
    gate("G3 real tree: {0} shared files ({1} tools/, {2} bench), scan {3:.1f} s; stagekit/gscript/protocol/stage_prerun shared".format(len(sh), tools_n, bench_n, dt),
         all(p in sh for p in need) and bench_n >= 30 and tools_n >= 30 and dt < 20, sorted(p for p in need if p not in sh))
    doc = os.path.join(tmp, "caps.md")
    shutil.copyfile(GC.DOC, doc)
    GC.write(doc)
    a = open(doc, encoding="utf-8").read()
    w2 = GC.write(doc)
    b = open(doc, encoding="utf-8").read()
    with open(GC.SHARED_CACHE, encoding="utf-8") as f:
        cache = json.load(f)
    gate("G4 write() twice: second is a no-op ({0}); one fn-table + one fn-list block; cache lists stagekit ({1} files)".format(not w2, len(cache["files"])),
         not w2 and a == b and b.count(GC.BEGIN) == 1 and b.count(GC.LIST_BEGIN) == 1 and "tools/stagekit.py" in cache["files"])
    return doc


def wait_unlocked(state, t=120):
    end = time.time() + t
    while time.time() < end:
        if not os.path.exists(os.path.join(state, "capabilities_regen.lock")):
            return True
        time.sleep(0.5)
    return False


def runs(state):
    p = os.path.join(state, "capabilities_regen.log")
    return [ln for ln in open(p, encoding="utf-8", errors="replace").read().splitlines() if ln.startswith("CAPREGEN |")] if os.path.exists(p) else []


def hook_cases(tmp, doc_src):
    state = os.path.join(tmp, "state")
    os.makedirs(state)
    doc = os.path.join(tmp, "hookdoc.md")
    shutil.copyfile(doc_src, doc)
    with open(doc, encoding="utf-8") as f:
        txt = f.read()
    import gen_capabilities as GC
    b, _l, a = GC.split_list(txt)
    with open(doc, "w", encoding="utf-8", newline="") as f:
        f.write(b + a)                                                            # the list block removed: H1 must put it back
    cache = os.path.join(tmp, "cache.json")
    with open(cache, "w", encoding="utf-8") as f:
        json.dump({"schema": "capabilities-shared/1", "files": ["tools/stagekit.py"]}, f)
    os.environ.update(GUARD_WRITE_CAP_CACHE=cache, GUARD_WRITE_CAP_STATE=state, GUARD_WRITE_CAP_DOC=doc)
    spec = importlib.util.spec_from_file_location("guard_write_t7", os.path.join(TOOLS, "hooks", "guard_write.py"))
    GW = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(GW)
    r1 = GW.capabilities_regen(os.path.join(TOOLS, "stagekit.py"))
    done = wait_unlocked(state)
    has = GC.LIST_BEGIN in open(doc, encoding="utf-8").read()
    gate("H1 write to a SHARED file -> {0}; the detached run regenerated the temp doc (fn-list back: {1}); lock released {2}; log {3}".format(
        r1, has, done, runs(state)[-1:]), r1 == "started" and done and has and len(runs(state)) == 1)
    n0 = len(runs(state))
    r2 = GW.capabilities_regen(os.path.join(TOOLS, "bench", "selftest_t7_capabilities.py"))
    time.sleep(2)
    gate("H2 write to a NON-shared file -> {0}; no lock, no new run".format(r2),
         r2 == "not-shared" and not os.path.exists(os.path.join(state, "capabilities_regen.lock")) and len(runs(state)) == n0)
    r3 = GW.capabilities_regen(os.path.join(TOOLS, "stagekit.py"))
    time.sleep(4)          # the second write lands DURING run 1 (a write before the run starts is covered by that run: it clears the flag first)
    r4 = GW.capabilities_regen(os.path.join(TOOLS, "stagekit.py"))
    done = wait_unlocked(state)
    new = runs(state)[n0:]
    gate("H3 two writes in a row -> {0} + {1}; then exactly 1 run + 1 re-run {2}; lock released {3}; flag cleared".format(r3, r4, [x.split(" | ")[2] for x in new], done),
         r3 == "started" and r4 == "rerun-flagged" and done and len(new) == 2 and "re-run" in new[1] and "re-run" not in new[0]
         and not os.path.exists(os.path.join(state, "capabilities_regen.rerun")), new)
    for k in ("GUARD_WRITE_CAP_CACHE", "GUARD_WRITE_CAP_STATE", "GUARD_WRITE_CAP_DOC"):
        os.environ.pop(k, None)
    return doc


def runner_cases(tmp, doc):
    import cycle_runner as CR
    rl = os.path.join(tmp, "runner.log")
    line = CR.capabilities_hook(999, rl, doc=doc)
    logged = open(rl, encoding="utf-8").read().splitlines()
    gate("C1 capabilities_hook logs ONE line 'CAPABILITIES | ... | cycle 999 | regenerated (rewrote|unchanged) fn-table ... | drift ...'",
         len(logged) == 1 and logged[0].startswith("CAPABILITIES | ") and "| cycle 999 | regenerated " in logged[0] and " fn-list " in logged[0]
         and "| drift " in logged[0], line)
    bad = CR.capabilities_hook(998, rl, doc=doc, gen=os.path.join(tmp, "no_such_generator.py"))
    gate("C2 a broken generator -> a FAILED line, no exception", "regenerated FAILED" in bad, bad)


def main():
    import gen_capabilities as GC
    tmp = tempfile.mkdtemp(prefix="t7caps_")
    try:
        tree_cases(GC, tmp)
        doc = real_cases(GC, tmp)
        doc = hook_cases(tmp, doc)
        runner_cases(tmp, doc)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    import protocol
    main()
    fails = [g for g, ok in GATES if not ok]
    print(protocol.result_line({"status": "PASS" if not fails else "FAIL", "gates": {"pass": len(GATES) - len(fails), "fail": len(fails)},
                                "first_fail": (fails[0][:180] if fails else None), "artefacts": []}), flush=True)
    sys.exit(0 if not fails else 1)
