# ---
# labview: none
# hardware: none
# ---
r"""xs_write_less - A/B bench of docs/script-writing.md rules 10-15 ("Write less"), card chat-X13.

    py tools/bgrun.py --material --max-min 45 --log tools/bench/xs_write_less/bench.log -- \
        py -u tools/bench/xs_write_less/run_bench.py --phase all
    py tools/bench/xs_write_less/run_bench.py --phase selftest        (offline: checkers + metrics on fixtures)

PREDICTION CONTRACT: phase `prep` snapshots the real inputs into inputs/ (md5 recorded) and writes the two arm docs
(OLD = `git show 8b4c43f5:docs/script-writing.md`, the parent version of 02bdfa47; NEW = the working-tree file, which
differs from OLD only by rules 10-15). Phase `cells` runs 3 tasks x 2 arms x 2 repeats = 12 `claude.exe -p` cells
(claude-opus-5-5, effort high, stream-json, cell env = matbench.cell_env) each under its own bgrun (--max-min 10), <= 4
at a time; every cell gets its arm doc as <cell>/script-rules.md (same file name in both arms) and may write only
under its own folder (--allowedTools path rules). Phase `check` re-runs every produced script itself (cwd = project
root, 60 s) and scores it against an independent truth computed here; phase `judge` writes judge/mapping.json (random
A/B per pair) BEFORE launching one read-only blind judge per task. Predicted: 12 cells end BGRUN END rc=0, each writes
its script; the RESULT line counts cells with a script as pass.

WHAT EXISTED FIRST: tools/bench/matbench/matbench.py cell_env (the bench-cell env markers) and score.py envelope
(claude -p json envelope parse) - both IMPORTED, not copied; tools/bgrun.py (deadline per cell); protocol.result_line.
No A/B bench of a rules document existed. skipped: worktrees (cells only read real files and write their own folder).
"""
import ast
import collections
import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, os.path.join(MAIN, "tools"))
sys.path.insert(0, os.path.join(MAIN, "tools", "bench", "matbench"))
import protocol  # noqa: E402
import score     # noqa: E402  - envelope(): the claude -p result object out of a bgrun log
from matbench import cell_env  # noqa: E402

OLD_COMMIT = "8b4c43f5"
REL = "tools/bench/xs_write_less"
INP = REL + "/inputs"
EL_A = "errorlist_scratch_c140_3_ring_p4s01_20261002_205117_20261002_205859.json"
EL_B = "errorlist_scratch_c141_p4s01_20261002_230228_20261002_230850.json"
SNAP = {"gate_fp_queue.jsonl": "tools/bench/gate_fp_queue.jsonl", "cycle_runner.log": "tools/bench/cycle_runner.log",
        EL_A: "tools/bench/" + EL_A, EL_B: "tools/bench/" + EL_B}
TASKS = {
    "T1": ("count_gate_fp.py", "Write count_gate_fp.py that reads %s/gate_fp_queue.jsonl and prints the number of OPEN "
           "entries per gate class, then a RESULT line." % INP, []),
    "T2": ("el_diff.py", "Write el_diff.py that takes two Error List JSON files (use the pair %s/%s and %s/%s) and "
           "prints the items in one but not the other, then a RESULT line." % (INP, EL_A, INP, EL_B),
           [INP + "/" + EL_A, INP + "/" + EL_B]),
    "T3": ("cycle_costs.py", "Write cycle_costs.py that reads %s/cycle_runner.log and prints, per cycle, its cost and "
           "whether its assignment rounds ended PURPOSE_MET or HANDBACK, then a RESULT line." % INP, []),
}
ARMS = ("OLD", "NEW")
REPS = (1, 2)
MODEL, EFFORT = "claude-opus-5-5", "high"


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def ab(rel):
    return os.path.join(MAIN, rel.replace("/", os.sep))


def cells():
    return ["%s_%s_r%d" % (a, t, r) for t in TASKS for a in ARMS for r in REPS]


# ---------------------------------------------------------------- prep
def prep():
    os.makedirs(ab(INP), exist_ok=True)
    rec = {}
    for name, src in SNAP.items():
        shutil.copyfile(ab(src), ab(INP + "/" + name))
        rec[name] = {"from": src, "md5": md5(ab(INP + "/" + name))}
    old = subprocess.run(["git", "show", "%s:docs/script-writing.md" % OLD_COMMIT], cwd=MAIN, capture_output=True,
                         check=True).stdout
    os.makedirs(ab(REL + "/arms"), exist_ok=True)
    open(ab(REL + "/arms/OLD.md"), "wb").write(old)
    shutil.copyfile(ab("docs/script-writing.md"), ab(REL + "/arms/NEW.md"))
    rec["arms"] = {a: md5(ab(REL + "/arms/%s.md" % a)) for a in ARMS}
    json.dump(rec, open(ab(INP + "/snapshot.json"), "w", encoding="utf-8"), indent=1)
    print("PREP", json.dumps(rec), flush=True)


# ---------------------------------------------------------------- cells
def cell_prompt(cell):
    arm, t, _ = cell.split("_")
    d = REL + "/" + cell
    return ("%s Put the script at %s/%s and run it once with py. The script rules you must follow are in "
            "%s/script-rules.md (a copy in your scratch folder); read it first. Do not read docs/script-writing.md. "
            "Write only inside %s/. No LabVIEW, no hardware. When done, reply briefly: what you wrote and its output."
            % (TASKS[t][1], d, TASKS[t][0], d, d))


def claude_cmd(prompt, tools):
    return ["claude.exe", "-p", "--model", MODEL, "--effort", EFFORT, "--output-format", "stream-json", "--verbose",
            "--allowedTools"] + tools + ["--", prompt]


def run_pool(jobs, par, max_min):
    """jobs = [(name, logpath, cmd)] -> each under its own bgrun, <= par at a time; returns {name: wall_min}."""
    pending, running, wall = list(jobs), [], {}
    while pending or running:
        while pending and len(running) < par:
            name, log, cmd = pending.pop(0)
            if os.path.exists(log):
                os.remove(log)
            full = [sys.executable, ab("tools/bgrun.py"), "--max-min", str(max_min), "--log", log, "--"] + cmd
            running.append((name, subprocess.Popen(full, cwd=MAIN, env=cell_env(), stdout=subprocess.DEVNULL,
                                                   stderr=subprocess.DEVNULL), time.time()))
            print("START", name, time.strftime("%H:%M:%S"), flush=True)
        for item in list(running):
            if item[1].poll() is not None:
                running.remove(item)
                wall[item[0]] = round((time.time() - item[2]) / 60.0, 2)
                print("END", item[0], "rc", item[1].returncode, "min", wall[item[0]], flush=True)
        time.sleep(5)
    return wall


def run_cells(only=None):
    jobs = []
    for c in cells():
        if only and c not in only:
            continue
        d = ab(REL + "/" + c)
        os.makedirs(d, exist_ok=True)
        shutil.copyfile(ab(REL + "/arms/%s.md" % c.split("_")[0]), os.path.join(d, "script-rules.md"))
        tools = ["Read", "Glob", "Grep", "Write(%s/%s/**)" % (REL, c), "Edit(%s/%s/**)" % (REL, c),
                 "Bash(py *)", "Bash(python *)", "Bash(ls *)", "Bash(wc *)", "Bash(head *)"]
        jobs.append((c, os.path.join(d, "cell.log"), claude_cmd(cell_prompt(c), tools)))
    wall = run_pool(jobs, 4, 10)
    for c, w in wall.items():
        json.dump({"wall_min": w}, open(ab(REL + "/%s/wall.json" % c), "w"))


# ---------------------------------------------------------------- metrics
def code_lines(src):
    """non-blank, non-comment lines, minus docstring lines -> (loc, docstring_lines)."""
    lines = src.splitlines()
    doc = set()
    try:
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)) and n.body:
                b = n.body[0]
                if isinstance(b, ast.Expr) and isinstance(getattr(b, "value", None), ast.Constant) \
                        and isinstance(b.value.value, str):
                    doc.update(range(b.lineno, b.end_lineno + 1))
    except SyntaxError:
        pass
    loc = sum(1 for i, ln in enumerate(lines, 1) if ln.strip() and not ln.strip().startswith("#") and i not in doc)
    return loc, len(doc)


def metrics(src, asked_positionals):
    m = {}
    m["loc"], m["doc_lines"] = code_lines(src)
    tree = ast.parse(src)
    std, other = set(), set()
    for n in ast.walk(tree):
        mods = [a.name for a in n.names] if isinstance(n, ast.Import) else \
            [n.module] if isinstance(n, ast.ImportFrom) and n.module and not n.level else []
        for mod in mods:
            top = mod.split(".")[0]
            (std if top in sys.stdlib_module_names else other).add(top)
    m["non_stdlib_imports"] = sorted(other)
    m["asserts"] = sum(isinstance(n, ast.Assert) for n in ast.walk(tree))
    flags = pos = 0
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and getattr(n.func, "attr", "") == "add_argument":
            names = [a.value for a in n.args if isinstance(a, ast.Constant) and isinstance(a.value, str)]
            if any(x.startswith("-") for x in names):
                flags += 1
            else:
                pos += 1
    argv_idx = {n.slice.value for n in ast.walk(tree) if isinstance(n, ast.Subscript)
                and isinstance(n.value, ast.Attribute) and n.value.attr == "argv"
                and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, int)}
    m["argparse_flags"], m["argparse_positionals"], m["argv_indexes"] = flags, pos, sorted(argv_idx)
    m["unasked_options"] = flags + max(0, pos - asked_positionals) + \
        max(0, len([i for i in argv_idx if i >= 1]) - asked_positionals if not pos else 0)
    m["shortcut_comments"] = len(re.findall(r"#\s*shortcut:", src, re.I))
    m["skipped_in_script"] = bool(re.search(r"skipped:", src, re.I))
    m["result_line"] = "RESULT" in src
    return m


# ---------------------------------------------------------------- truth (independent of the cells)
def truth_t1(path):
    rows = [json.loads(ln) for ln in open(path, encoding="utf-8") if ln.strip()]
    op = [r["gate"] for r in rows if str(r.get("status", "")).lower() == "open"]
    return {"full": collections.Counter(op), "two": collections.Counter(":".join(g.split(":")[:2]) for g in op),
            "one": collections.Counter(g.split(":")[0] for g in op), "total": len(op)}


def check_t1(out, tr):
    lines = out.splitlines()
    ok = {}
    for k in ("full", "two", "one"):
        ok[k] = bool(tr[k]) and all(any(g in ln and re.search(r"(?<![\w.])%d(?![\w.])" % n, ln) for ln in lines)
                    for g, n in tr[k].items())
    return {"correct": any(ok.values()), "grouping_ok": ok, "total_open": tr["total"]}


def truth_t2(pa, pb):
    a = json.load(open(pa, encoding="utf-8"))["items"]
    b = json.load(open(pb, encoding="utf-8"))["items"]
    ra, rb = collections.Counter(x["raw"] for x in a), collections.Counter(x["raw"] for x in b)
    return {"only_a": list((ra - rb).elements()), "only_b": list((rb - ra).elements())}


def check_t2(out, tr):
    keys = ["Insert Into Array", "anvthing", "anything.", "Wire:Wire has loose"]   # 1 real + 3 OCR-noise diffs
    hit = {k: k in out for k in keys}
    n = len(tr["only_a"]) + len(tr["only_b"])
    return {"correct": all(hit.values()) and len(out.splitlines()) <= 4 * n + 15, "hits": hit,
            "out_lines": len(out.splitlines()), "expected_diffs": n}


ASSIGN_RE = re.compile(r"^ASSIGN \| [^|]+\| cycle (\d+) round \d+ \| end [^|]*\| \$([\d.]+) \|[^|]*\|[^|]*\| ([A-Z_]+)")
CYCLE_RE = re.compile(r"^CYCLE (\d+) \|[^|]*\|[^|]*\|[^|]*\| \$([\d.]+)")


def truth_t3(path):
    out = collections.defaultdict(lambda: {"assign_usd": 0.0, "kinds": set(), "cycle_usd": []})
    for ln in open(path, encoding="utf-8", errors="replace"):
        m = ASSIGN_RE.match(ln)
        if m:
            c = out[int(m.group(1))]
            c["assign_usd"] += float(m.group(2))
            c["kinds"].add("PURPOSE_MET" if m.group(3).startswith("PURPOSE") else "HANDBACK")
        m = CYCLE_RE.match(ln)
        if m:
            out[int(m.group(1))]["cycle_usd"].append(float(m.group(2)))
    return dict(out)


def check_t3(out, tr):
    lines = out.splitlines()
    bad_kind, cost_hits, with_assign = [], 0, [c for c in tr if tr[c]["kinds"]]
    for c in with_assign:
        ls = [ln for ln in lines if re.search(r"(?<![\d.$])%d(?![\d.])" % c, ln)]
        if not all(any(k in ln for ln in ls) for k in tr[c]["kinds"]):
            bad_kind.append(c)
        nums = {round(float(x), 2) for ln in ls for x in re.findall(r"\d+\.\d+", ln)}
        cand = {round(tr[c]["assign_usd"], 2), round(sum(tr[c]["cycle_usd"]), 2),
                round(tr[c]["assign_usd"] + sum(tr[c]["cycle_usd"]), 2)} | {round(x, 2) for x in tr[c]["cycle_usd"]}
        cost_hits += bool(nums & cand)
    return {"correct": not bad_kind and cost_hits == len(with_assign), "cycles_with_assign": len(with_assign),
            "kind_wrong": bad_kind[:10], "cost_matched": cost_hits}


# ---------------------------------------------------------------- check
def stream_facts(log_text):
    """tool calls of a stream-json cell: did it read docs/script-writing.md / its rules file; which Bash commands."""
    reads, bashes, writes = [], [], []
    for ln in log_text.splitlines():
        if not ln.startswith("{"):
            continue
        try:
            ev = json.loads(ln)
        except ValueError:
            continue
        if ev.get("type") != "assistant":
            continue
        for part in (ev.get("message") or {}).get("content") or []:
            if isinstance(part, dict) and part.get("type") == "tool_use":
                inp = part.get("input") or {}
                if part.get("name") == "Read":
                    reads.append(inp.get("file_path", ""))
                elif part.get("name") in ("Bash", "PowerShell"):
                    bashes.append(inp.get("command", "")[:200])
                elif part.get("name") in ("Write", "Edit"):
                    writes.append(inp.get("file_path", ""))
    norm = [r.replace("\\", "/") for r in reads]
    return {"read_forbidden_doc": any(r.endswith("docs/script-writing.md") for r in norm),
            "read_rules_copy": any(r.endswith("script-rules.md") for r in norm), "n_reads": len(reads),
            "bash": bashes, "writes": writes}


def run_script(argv):
    p = subprocess.run([sys.executable, "-u"] + argv, cwd=MAIN, capture_output=True, timeout=60)
    dec = lambda b: b.decode("utf-8", errors="replace")   # noqa: E731
    return p.returncode, dec(p.stdout), dec(p.stderr)


def check_all():
    trs = {"T1": truth_t1(ab(INP + "/gate_fp_queue.jsonl")),
           "T2": truth_t2(ab(INP + "/" + EL_A), ab(INP + "/" + EL_B)),
           "T3": truth_t3(ab(INP + "/cycle_runner.log"))}
    open(ab(INP + "/empty.json"), "w").close()
    res = {}
    for c in cells():
        arm, t, rep = c.split("_")
        d = ab(REL + "/" + c)
        log = score.rd(os.path.join(d, "cell.log"))
        env = score.envelope(log) or {}
        r = {"cell": c, "arm": arm, "task": t, "rep": rep, "usd": env.get("total_cost_usd"),
             "min": round((env.get("duration_ms") or 0) / 60000.0, 2), "bgrun_end": "BGRUN END rc=0" in log,
             "reply": (env.get("result") or "")[:1500]}
        try:
            r["wall_min"] = json.load(open(os.path.join(d, "wall.json")))["wall_min"]
        except (OSError, ValueError):
            r["wall_min"] = None
        r.update(stream_facts(log))
        r["skipped_in_reply"] = "skipped:" in r["reply"].lower()
        sp = os.path.join(d, TASKS[t][0])
        r["script"] = os.path.exists(sp)
        if r["script"]:
            src = open(sp, encoding="utf-8", errors="replace").read()
            r["md5"] = md5(sp)
            try:
                r.update(metrics(src, len(TASKS[t][2])))
            except SyntaxError as e:
                r["syntax_error"] = str(e)
            rc, out, err = run_script([sp] + TASKS[t][2])
            r["rc"], r["stdout_tail"], r["stderr_tail"] = rc, out[-1500:], err[-600:]
            r["result_printed"] = bool(re.search(r"^RESULT\b", out, re.M))
            r.update({"T1": check_t1, "T2": check_t2, "T3": check_t3}[t](out, trs[t]))
            if t == "T2":
                for tag, args in (("edge_missing", [INP + "/no_such.json", TASKS[t][2][1]]),
                                  ("edge_empty", [INP + "/empty.json", TASKS[t][2][1]])):
                    rc2, o2, e2 = run_script([sp] + args)
                    r[tag] = {"rc": rc2, "traceback": "Traceback" in e2, "result": "RESULT" in o2}
        res[c] = r
        print("CHECK", c, json.dumps({k: r.get(k) for k in ("script", "correct", "loc", "unasked_options", "asserts",
                                                             "shortcut_comments", "usd", "min")}), flush=True)
    json.dump(res, open(ab(REL + "/results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False,
              default=lambda o: sorted(o) if isinstance(o, set) else str(o))
    return res


# ---------------------------------------------------------------- judge
def judge_prompt(t, jd):
    return ("You are a blind reviewer. Task given to two script writers: \"%s\" Read %s/pair1_A.py, %s/pair1_B.py, "
            "%s/pair2_A.py, %s/pair2_B.py (read-only; you may read the input files too; do not edit or run anything). "
            "For each pair: which script is simpler WITHOUT losing correctness or edge handling (empty input file, "
            "missing input file, one row)? Reply with ONLY one JSON object: {\"pair1\": {\"simpler\": \"A|B|tie\", "
            "\"correct_A\": true, \"correct_B\": true, \"edges_A\": \"...\", \"edges_B\": \"...\", \"reasons\": "
            "\"<=60 words\"}, \"pair2\": {...same...}}" % (TASKS[t][1], jd, jd, jd, jd))


def run_judges():
    rng = random.Random()
    mapping = {}
    jobs = []
    for t in TASKS:
        jd = REL + "/judge_" + t
        os.makedirs(ab(jd), exist_ok=True)
        mapping[t] = {}
        for rep in REPS:
            old_is_a = rng.random() < 0.5
            mapping[t]["pair%d" % rep] = {"A": "OLD" if old_is_a else "NEW", "B": "NEW" if old_is_a else "OLD"}
            for side in "AB":
                src = ab("%s/%s_%s_r%d/%s" % (REL, mapping[t]["pair%d" % rep][side], t, rep, TASKS[t][0]))
                dst = ab("%s/pair%d_%s.py" % (jd, rep, side))
                if os.path.exists(src):
                    shutil.copyfile(src, dst)
                else:
                    open(dst, "w").write("# (no script was produced)\n")
        jobs.append(("judge_" + t, ab(jd + "/judge.log"), claude_cmd(judge_prompt(t, jd), ["Read", "Glob", "Grep"])))
    json.dump({"written": time.strftime("%Y-%m-%d %H:%M:%S"), "mapping": mapping},
              open(ab(REL + "/judge_mapping.json"), "w"), indent=1)   # BEFORE any judge starts
    print("MAPPING", json.dumps(mapping), flush=True)
    run_pool(jobs, 3, 10)
    out = {}
    for t in TASKS:
        env = score.envelope(score.rd(ab(REL + "/judge_%s/judge.log" % t))) or {}
        txt = env.get("result") or ""
        m = re.search(r"\{.*\}", txt, re.S)
        try:
            v = json.loads(m.group(0)) if m else None
        except ValueError:
            v = None
        out[t] = {"usd": env.get("total_cost_usd"), "verdict": v, "raw": txt[:2000]}
        for p in ("pair1", "pair2"):
            if v and p in v:
                s = v[p].get("simpler")
                v[p]["simpler_arm"] = mapping[t][p].get(s, s)
    json.dump(out, open(ab(REL + "/judge_results.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    return out


# ---------------------------------------------------------------- selftest
def selftest():
    src = '"""doc\nline"""\nimport os, json\nimport yaml\n# c\nassert 1\nx = 1  # shortcut: x, later\n' \
          'import argparse\nap = argparse.ArgumentParser()\nap.add_argument("a")\nap.add_argument("--v")\n'
    m = metrics(src, 1)
    assert m["loc"] == 8 and m["doc_lines"] == 2, m
    assert m["non_stdlib_imports"] == ["yaml"] and m["asserts"] == 1 and m["shortcut_comments"] == 1, m
    assert m["argparse_flags"] == 1 and m["unasked_options"] == 1, m
    tr = {"full": collections.Counter({"guard_peer": 2, "checker:a:b": 1}), "two": collections.Counter(),
          "one": collections.Counter(), "total": 3}
    assert check_t1("guard_peer  2\nchecker:a:b 1\n", tr)["correct"]
    assert not check_t1("guard_peer  3\nchecker:a:b 1\n", tr)["correct"]
    t3 = {165: {"assign_usd": 5.98, "kinds": {"HANDBACK"}, "cycle_usd": [1.0]}}
    assert check_t3("cycle 165  $5.98  HANDBACK\n", t3)["correct"]
    assert not check_t3("cycle 165  $5.98  PURPOSE_MET\n", t3)["correct"]
    assert len(cells()) == 12
    return 4


def main():
    phase = sys.argv[sys.argv.index("--phase") + 1] if "--phase" in sys.argv else "selftest"
    st = selftest()
    if phase == "selftest":
        print(protocol.result_line({"status": "PASS", "gates": {"pass": st, "fail": 0}, "first_fail": None,
                                    "artefacts": []}))
        return 0
    if phase in ("prep", "all"):
        prep()
    if phase in ("cells", "all"):
        only = sys.argv[sys.argv.index("--only") + 1].split(",") if "--only" in sys.argv else None
        run_cells(only)
    res = check_all() if phase in ("check", "all", "judge") else {}
    if phase in ("judge", "all"):
        run_judges()
    if not res:   # prep / cells only: the phase ran; scripts are counted by the check phase
        print(protocol.result_line({"status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None,
                                    "artefacts": []}), flush=True)
        return 0
    got = sum(1 for r in res.values() if r.get("script"))
    ok = got == 12
    print(protocol.result_line({"status": "PASS" if ok else "FAIL", "gates": {"pass": got, "fail": 12 - got},
                                "first_fail": None if ok else "%d of 12 cells produced no script" % (12 - got),
                                "artefacts": [{"path": REL + "/results.json", "md5": md5(ab(REL + "/results.json"))}]
                                if res else []}), flush=True)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
