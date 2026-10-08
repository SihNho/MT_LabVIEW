# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_150-a3-3.md
# ---
"""Card 150-a3-3 self-test (OFFLINE, stdlib, no LabVIEW): the disposition-heading parser at the three wired sites, run on the
OLD code and on the NEW code.

OLD code = byte copies taken before any edit by `prep_c150_a3_3.py snapshot` (tools/bench/prep_c150_a3_3_old_*.txt; md5 checked
against the card inputs 7482e9b7 / 72ab9def / c57668a5). NEW code = tools/violations.py, tools/cycle_runner.py,
tools/audit_cycle.py as they are now. Each is exec'd as a module with __file__ = the real tools/<name>.py path.
Sites: V = violations.scan() (PEER pointed at a temp dir); R = cycle_runner.retro_undisposed(temp dir); A4 = the A4 loop body of
audit_cycle.main(), exec'd from each file's own source text (block `blank = []` .. `say("A4`); A9 = audit_cycle.a9_unlanded(root=tmp).
Inputs: copies of archive/peer/2026-10-08-retrospective-cycle149.md and -cycle148.md (as-is and with their real disposition
replaced by the placeholder), synthetic bodies S1 inline quote + real heading, S2 inline quote and no heading, S3 heading +
placeholder only.
Census: every archive/peer/*.md, old cut index `body.find(H)` vs new `dispo.heading_index(body)`; a file whose cut differs must
quote the heading inline (an occurrence not at a column-0 heading line) or carry more than one column-0 heading (reported).
Outputs: old vs new module on the REAL archive - V slugs per retrospective, R decision per retrospective, A4 blank set over
every archive/peer/*.md, A9 (absent, n) - a changed output on a file that does NOT quote the heading inline is a FAIL.
PREDICTION (card 150-a3-4, two-heading cases V6-V8, R7-R12, A4-7..12 added): OLD 22 pass / 15 fail (fails V1-V4, R1-R4,
A4-1..A4-4, A4-7, A4-10, A9-1); NEW 34/0; census cut differs on the 8 pattern-A + 38 inline files, pattern B cut == old;
output changes == EXP_OUT exactly. RESULT: PASS iff NEW all pass, OLD fails at V, R, A4, census and outputs as expected.
    py tools/bgrun.py --material --max-min 4 --log tools/bench/selftest_c150_a3_3.log -- py -u tools/bench/selftest_c150_a3_3.py"""
import glob
import hashlib
import json
import os
import re
import sys
import tempfile
import textwrap
import types

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
TOOLS = os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS)
import dispo  # noqa: E402

H = "## What was done with it"
ANCH = re.compile(r"^## What was done with it[ \t\r]*$", re.M)
OLD_MD5 = {"violations": "7482e9b73b0b6e85b932ac7ea7638d2f", "cycle_runner": "72ab9defc2c677ba6504d3d7f68ffdab",
           "audit_cycle": "c57668a5c6dd5df27ba21cd57cec6d61"}
TOTAL = {"P": 0, "F": 0, "first": None}


def gate(label, ok, extra=""):
    TOTAL["P" if ok else "F"] += 1
    if not ok and TOTAL["first"] is None:
        TOTAL["first"] = label
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(extra)[:260]), flush=True)
    return ok


def load(name, src):
    m = types.ModuleType("c150a33_" + name)
    m.__file__ = os.path.join(TOOLS, name + ".py")
    exec(compile(src, m.__file__, "exec"), m.__dict__)
    return m


def srcs(kind):
    out = {}
    for n in OLD_MD5:
        p = (os.path.join(ROOT, "tools", "bench", "prep_c150_a3_3_old_%s.txt" % n) if kind == "old"
             else os.path.join(TOOLS, n + ".py"))
        out[n] = open(p, encoding="utf-8").read()
        if kind == "old":
            gate("OLD source %s md5 == card input %s" % (n, OLD_MD5[n][:8]),
                 hashlib.md5(open(p, "rb").read()).hexdigest() == OLD_MD5[n], p)
    return out


def placeholder_variant(body):
    last = [m.start() for m in ANCH.finditer(body)][-1]
    return body[:last] + H + "\n\n(Claude fills in)\n"


R149 = open(os.path.join(ROOT, "archive", "peer", "2026-10-08-retrospective-cycle149.md"), encoding="utf-8").read()
R148 = open(os.path.join(ROOT, "archive", "peer", "2026-10-08-retrospective-cycle148.md"), encoding="utf-8").read()
QUOTE = "- the check reads the first `## What was done with it` string, which this answer quotes.\n"
S1 = ("# retrospective\n\n## Answer\n" + QUOTE + "VIOLATION: wrong-ordering | loss_min=5 | loss_usd=? | evidence=x.py:1\n\n"
      + H + "\n\nDisposed: wrong-ordering ACCEPTED; a quoted slug follows and must not be counted.\n"
      + "VIOLATION: scope-creep\n" + "- more disposition text so that it is long enough to count as written, really.\n")
S2 = "# retrospective\n\n## Answer\n" + QUOTE + "VIOLATION: tool-not-built | loss_min=3 | loss_usd=? | evidence=x.py:1\n" + "x" * 200 + "\n"
S3 = "# retrospective\n\n## Answer\nVIOLATION: rule-evaded\n\n" + H + "\n\n(Claude fills in)\n"
# card 150-a3-4: two column-0 headings. Pattern A = placeholder first, real text second; pattern B = real text first,
# placeholder left under the last; SP = both placeholder.
ARCH = lambda n: open(os.path.join(ROOT, "archive", "peer", n), encoding="utf-8").read()  # noqa: E731
PA1 = ARCH("2026-09-17-d1-s1-diagram-count.md")             # :64 placeholder, :68 real
PB1 = ARCH("2026-09-16-load-vs-editmode-23c-r2.md")         # :52 real, :87 placeholder
PB2 = ARCH("2026-09-18-retrospective-cycle17.md")           # :12 real, :281 placeholder
REAL = ("Disposed: finding ACCEPTED, fix landed in x.py:1; a quoted slug follows and must not be counted.\n"
        "VIOLATION: scope-creep\n- more disposition text so that it is long enough to count as written, really.\n")
SA = ("# review\n\n## Answer\nVIOLATION: premature-build\n\n## Sources\n\n(extract)\n\n" + H + "\n\n(Claude fills in)\n\n"
      + H + "\n\n" + REAL)
SB = ("# review\n\n## Answer\nVIOLATION: premature-build\n\n" + H + "\n\n" + REAL + "\n## Sources\n\n(extract)\n\n"
      + H + "\n\n(Claude fills in)\n")
SP = ("# review\n\n## Answer\nVIOLATION: premature-build\n\n" + H + "\n\n(Claude fills in)\n\n## Sources\n\n(x)\n\n"
      + H + "\n\n(Claude fills in)\n")
EXP_A = {"2026-09-15-retrospective-cycle7.md", "2026-09-17-d0-bandpass-click-was-delivered-hwnd-token.md",
         "2026-09-17-d0-bandpass-hwnd-token-agy.md", "2026-09-17-d1-s1-diagram-count.md", "2026-09-17-d1-s1-stale-in-memory-copy.md",
         "2026-09-17-d1-s3-stale-traverse-index.md", "2026-09-17-d1-s3b-uid-reuse-after-delete.md", "2026-09-17-moveinto-p1-execstate0.md"}
EXP_B = {"2026-09-16-load-vs-editmode-23c-r2.md", "2026-09-18-retrospective-cycle17.md"}
EXP_OUT = {   # diag_c150_a3_3_facts.md:24 (inline-quote files) + pattern A under A4 (old blank -> new annotated)
    "V": {"2026-09-20-retrospective-cycle49.md", "2026-10-08-retrospective-cycle148.md", "2026-10-08-retrospective-cycle149.md"},
    "R": {"2026-09-17-retrospective-cycle16.md", "2026-09-17-retrospective-cycle16b.md", "2026-09-18-retrospective-cycle26.md"},
    "A4": {"2026-09-17-priorart-d1-op-exitwhile-node.md", "2026-09-17-priorart-d1-op-stopfromnode.md",
           "2026-09-17-priorart-d1-op-streamwrite.md", "2026-09-17-priorart-prior-art.md", "2026-09-17-retrospective-cycle16.md",
           "2026-09-17-retrospective-cycle16b.md", "2026-09-18-retrospective-cycle26.md", "2026-09-19-stoprecord-release-deadlock-opus.md"}
    | (EXP_A - {"2026-09-15-retrospective-cycle7.md"})}


def scenario(kind):
    """Gates for one implementation; returns {site: n_fail}."""
    print("=== %s code" % kind.upper(), flush=True)
    s = srcs(kind)
    V = load("violations", s["violations"])
    CR = load("cycle_runner", s["cycle_runner"])
    AC = load("audit_cycle", s["audit_cycle"])
    fails = {"V": 0, "R": 0, "A4": 0, "A9": 0}

    def g(site, label, ok, extra=""):
        if not gate("%s %s %s" % (kind, site, label), ok, extra):
            fails[site] += 1

    # --- V: violations.scan() over a temp peer dir
    with tempfile.TemporaryDirectory(prefix="c150a33_v_") as d:
        for fn, body in (("2026-10-08-retrospective-cycle149.md", R149), ("2026-10-08-retrospective-cycle148.md", R148),
                         ("2026-10-08-retrospective-s1.md", S1), ("2026-10-08-retrospective-s2.md", S2),
                         ("2026-10-08-retrospective-s3.md", S3), ("2026-09-18-retrospective-cycle17.md", PB2),
                         ("2026-10-08-retrospective-sa.md", SA), ("2026-10-08-retrospective-sb.md", SB)):
            open(os.path.join(d, fn), "w", encoding="utf-8").write(body)
        V.PEER = d
        hits, _ = V.scan()
        by = {}
        for slug, files in hits.items():
            for f in files:
                by.setdefault(f, set()).add(slug)
        g("V", "V1 retro-149 slugs == {inference-over-measurement, device-failed}",
          by.get("2026-10-08-retrospective-cycle149.md", set()) == {"inference-over-measurement", "device-failed"},
          sorted(by.get("2026-10-08-retrospective-cycle149.md", set())))
        g("V", "V2 retro-148 slugs == {repeated-failure-class}",
          by.get("2026-10-08-retrospective-cycle148.md", set()) == {"repeated-failure-class"},
          sorted(by.get("2026-10-08-retrospective-cycle148.md", set())))
        g("V", "V3 S1 inline quote + heading: {wrong-ordering}, quoted scope-creep not counted",
          by.get("2026-10-08-retrospective-s1.md", set()) == {"wrong-ordering"}, sorted(by.get("2026-10-08-retrospective-s1.md", set())))
        g("V", "V4 S2 inline quote, no heading: {tool-not-built}",
          by.get("2026-10-08-retrospective-s2.md", set()) == {"tool-not-built"}, sorted(by.get("2026-10-08-retrospective-s2.md", set())))
        g("V", "V5 (same) S3 heading + placeholder: {rule-evaded}",
          by.get("2026-10-08-retrospective-s3.md", set()) == {"rule-evaded"}, sorted(by.get("2026-10-08-retrospective-s3.md", set())))
        g("V", "V6 (same) pattern B copy retro-cycle17: no slug (its old tally)",
          by.get("2026-09-18-retrospective-cycle17.md", set()) == set(), sorted(by.get("2026-09-18-retrospective-cycle17.md", set())))
        g("V", "V7 (same) pattern A synthetic SA: {premature-build}",
          by.get("2026-10-08-retrospective-sa.md", set()) == {"premature-build"}, sorted(by.get("2026-10-08-retrospective-sa.md", set())))
        g("V", "V8 (same) pattern B synthetic SB: {premature-build}, quoted scope-creep not counted",
          by.get("2026-10-08-retrospective-sb.md", set()) == {"premature-build"}, sorted(by.get("2026-10-08-retrospective-sb.md", set())))

    # --- R: cycle_runner.retro_undisposed(dir) on a dir holding ONE file each
    cases = (("R1 retro-149 with placeholder disposition -> undisposed", placeholder_variant(R149), True),
             ("R2 retro-148 with placeholder disposition -> undisposed", placeholder_variant(R148), True),
             ("R3 S1 with placeholder disposition -> undisposed", placeholder_variant(S1), True),
             ("R4 S2 no heading (inline quote only) -> undisposed", S2, True),
             ("R5 (same) S3 heading + placeholder -> undisposed", S3, True),
             ("R6 (same) retro-149 as archived -> disposed", R149, False),
             ("R7 pattern A copy d1-s1-diagram-count -> disposed", PA1, False),
             ("R8 pattern B copy 23c-r2 -> disposed", PB1, False),
             ("R9 pattern B copy retro-cycle17 -> disposed", PB2, False),
             ("R10 pattern A synthetic SA -> disposed", SA, False),
             ("R11 pattern B synthetic SB -> disposed", SB, False),
             ("R12 two headings, both placeholder -> undisposed", SP, True))
    for label, body, want in cases:
        with tempfile.TemporaryDirectory(prefix="c150a33_r_") as d:
            p = os.path.join(d, "2026-10-08-retrospective-x.md")
            open(p, "w", encoding="utf-8").write(body)
            got = CR.retro_undisposed(d)
            g("R", label, (got is not None) == want, "returned %s" % (os.path.basename(got) if got else None))

    # --- A4: the loop body of audit_cycle.main() taken from the file's own text
    src = s["audit_cycle"]
    a = src.index("    blank = []\n", src.index("# A4 - reviews are annotated"))
    b = src.index('    say("A4', a)
    a4 = compile(textwrap.dedent(src[a:b]), "audit_cycle.py:A4", "exec")
    for label, body, want in [(c[0].replace("R", "A4-", 1).replace("undisposed", "blank").replace("disposed", "annotated"), c[1], c[2])
                              for c in cases]:
        with tempfile.TemporaryDirectory(prefix="c150a33_a_") as d:
            p = os.path.join(d, "2026-10-08-review-x.md")
            open(p, "w", encoding="utf-8").write(body)
            ns = dict(AC.__dict__)
            ns["reviews"] = [p]
            exec(a4, ns)
            g("A4", label, bool(ns["blank"]) == want, "blank %s" % ns["blank"])

    # --- A9: a9_unlanded(root=tmp): an inline quote followed by ACCEPTED + 'not built' in the ANSWER, real disposition clean
    with tempfile.TemporaryDirectory(prefix="c150a33_9_") as d:
        os.makedirs(os.path.join(d, "archive", "peer"))
        q = ("# review\n\n## Answer\nthe `## What was done with it` section must say: finding ACCEPTED, fix not built.\n\n"
             + H + "\n\n- finding 1 NOT ACCEPTED: nothing to build.\n")
        open(os.path.join(d, "archive", "peer", "2026-09-26-q.md"), "w", encoding="utf-8").write(q)
        n_q = AC.a9_unlanded(root=d)[1]
        g("A9", "A9-1 inline quote in the answer is not a candidate (n == 0)", n_q == 0, "n_candidates %s" % n_q)
        os.remove(os.path.join(d, "archive", "peer", "2026-09-26-q.md"))
        c = "# review\n\n## Answer\nx\n\n" + H + "\n\n- finding 1 ACCEPTED, fix not built yet (left open).\n"
        open(os.path.join(d, "archive", "peer", "2026-09-26-c.md"), "w", encoding="utf-8").write(c)
        absent, n_c = AC.a9_unlanded(root=d)
        g("A9", "A9-2 (same) one column-0 heading, ACCEPTED + not built: candidate, absent", n_c == 1 and absent == ["2026-09-26-c"],
          "n %s absent %s" % (n_c, absent))
    print("SITE-FAILS %s %s" % (kind, json.dumps(fails)), flush=True)
    MODS[kind] = (V, CR, AC, a4)
    return fails


MODS = {}


old = scenario("old")
p_after_old = (TOTAL["P"], TOTAL["F"])
TOTAL.update(P=0, F=0, first=None)
new = scenario("new")
new_counts = (TOTAL["P"], TOTAL["F"], TOTAL["first"])

# --- census over the archive: old cut vs new cut
diff_inline, diff_other, same, with_h = [], [], 0, 0
for p in sorted(glob.glob(os.path.join(ROOT, "archive", "peer", "*.md"))):
    body = open(p, encoding="utf-8", errors="replace").read()
    if H not in body:
        continue
    with_h += 1
    i_old, i_new = body.find(H), dispo.heading_index(body)
    if i_old == i_new:
        same += 1
        continue
    anchored = {m.start() for m in ANCH.finditer(body)}
    inline = [m.start() for m in re.finditer(re.escape(H), body) if m.start() not in anchored]
    (diff_inline if inline else diff_other).append(os.path.basename(p))
print("CENSUS archive/peer files with the heading string %d; same cut %d; differ+inline quote %d; differ other %d"
      % (with_h, same, len(diff_inline), len(diff_other)), flush=True)
print("CENSUS differ+inline: %s" % diff_inline, flush=True)
print("CENSUS differ other (more than one column-0 heading): %s" % diff_other, flush=True)

# --- OUTPUTS on the real archive, old module vs new module, per site; a changed output must be on an inline-quoting file
PEER = os.path.join(ROOT, "archive", "peer")
out_diff = {"V": [], "R": [], "A4": [], "A9": []}
hv = {}
for k in ("old", "new"):
    V, CR, AC, a4 = MODS[k]
    V.PEER = PEER
    hits, _ = V.scan()
    per = {}
    for slug, files in hits.items():
        for f in files:
            per.setdefault(f, []).append(slug)
    hv[k] = {f: sorted(v) for f, v in per.items()}
for f in sorted(set(hv["old"]) | set(hv["new"])):
    if hv["old"].get(f) != hv["new"].get(f):
        out_diff["V"].append((f, hv["old"].get(f), hv["new"].get(f)))
retros = sorted(glob.glob(os.path.join(PEER, "*retrospective*.md")))
allmd = sorted(glob.glob(os.path.join(PEER, "*.md")))
for p in retros:                          # R: the same test retro_undisposed applies to the newest file, on every file
    dec = []
    for k in ("old", "new"):
        with tempfile.TemporaryDirectory(prefix="c150a33_c_") as d:
            q = os.path.join(d, os.path.basename(p))
            open(q, "w", encoding="utf-8").write(open(p, encoding="utf-8", errors="replace").read())
            dec.append(MODS[k][1].retro_undisposed(d) is not None)
    if dec[0] != dec[1]:
        out_diff["R"].append((os.path.basename(p), dec[0], dec[1]))
bl = {}
for k in ("old", "new"):
    ns = dict(MODS[k][2].__dict__)
    ns["reviews"] = allmd
    exec(MODS[k][3], ns)
    bl[k] = set(ns["blank"])
out_diff["A4"] = sorted(bl["old"] ^ bl["new"])
a9 = {}
for k in ("old", "new"):
    det = {}
    ab, n9 = MODS[k][2].a9_unlanded(detail=det)
    a9[k] = (sorted(ab), n9, sorted(det))
if a9["old"] != a9["new"]:
    out_diff["A9"] = [a9["old"], a9["new"]]
print("OUTPUT A4 blank old %d / new %d of %d files; R undisposed-if-newest differs on %d of %d retrospectives; A9 old %s new %s"
      % (len(bl["old"]), len(bl["new"]), len(allmd), len(out_diff["R"]), len(retros), a9["old"][:2], a9["new"][:2]), flush=True)
unexplained = []
for site, rows in out_diff.items():
    for r in rows if site != "A9" else []:
        f = r[0] if isinstance(r, tuple) else r
        tag = ("inline" if f in diff_inline else "pattern-A" if f in EXP_A else "pattern-B" if f in EXP_B
               else "multi-heading" if f in diff_other else "SAME-CUT?")
        print("OUTDIFF %s | %s | %s | %s" % (site, tag, f, r[1:] if isinstance(r, tuple) else ""), flush=True)
        if site == "A4" and tag == "pattern-A" and not (f in bl["old"] and f not in bl["new"]):
            unexplained.append((site, f, "pattern A not old-blank -> new-annotated"))
got = {s: {(r[0] if isinstance(r, tuple) else r) for r in out_diff[s]} for s in ("V", "R", "A4")}
for s in ("V", "R", "A4"):
    for f in sorted(got[s] ^ EXP_OUT[s]):
        unexplained.append((s, f, "unexpected" if f in got[s] else "expected change missing"))
if out_diff["A9"]:
    print("OUTDIFF A9 | %s" % out_diff["A9"], flush=True)
    unexplained.append(("A9", "candidates"))
print("PATTERN A cut differs %d/8 %s | pattern B same cut as old %s" % (len(set(diff_other) & EXP_A), sorted(set(diff_other) - EXP_A),
      sorted(EXP_B - set(diff_other) - set(diff_inline))), flush=True)
census_ok = set(diff_other) == EXP_A and not (EXP_B & (set(diff_other) | set(diff_inline))) and len(diff_inline) == 38

TOTAL.update(P=0, F=0, first=None)
gate("census: cut differs on exactly the 8 pattern-A files + 38 inline-quote files; pattern B cut == old", census_ok,
     "other %s inline %d" % (sorted(set(diff_other) ^ EXP_A), len(diff_inline)))
gate("NEW code all site gates pass", new_counts[1] == 0, "new %d pass / %d fail, first %s" % new_counts)
gate("OLD code fails at V, R and A4 (A9 reported)", old["V"] > 0 and old["R"] > 0 and old["A4"] > 0,
     "old %d pass / %d fail, per site %s" % (p_after_old[0], p_after_old[1], old))
gate("archive outputs (V slugs, R decision, A4 blank, A9 candidates): changes == the expected inline-quote + pattern-A list",
     not unexplained, unexplained[:8])
print("COUNTS old %d pass / %d fail | new %d pass / %d fail" % (p_after_old[0], p_after_old[1], new_counts[0], new_counts[1]), flush=True)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if TOTAL["F"] == 0 else "FAIL",
                              "gates": {"pass": TOTAL["P"], "fail": TOTAL["F"]}, "first_fail": TOTAL["first"], "artefacts": []}),
      flush=True)
sys.exit(1 if TOTAL["F"] else 0)
