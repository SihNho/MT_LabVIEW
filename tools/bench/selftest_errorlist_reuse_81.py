r"""selftest_errorlist_reuse_81 - card 81-1 (retrospective-cycle80 device-failed): cycle_runner.errorlist_hook
re-verdicts the saved raw JSON OFFLINE when the bed md5 is unchanged, and does the GUI read only otherwise; the
cycle card carries the bed; guard_card exempts `stagexec.py selftest` by command.

No LabVIEW: the GUI branch (subprocess.run of errorlist_check.py) is replaced by a fake that counts calls.
Existing tests checked first: selftest_errorlist_retry.py covers the GUI FAIL/retry branch only (no bed in its
STATUS text -> it never reaches REUSE); selftest_errorlist_check_header.py covers compare(); neither covers reuse.

PREDICTION CONTRACT:
  R1 real D1_k bed + real saved read 113500 (bed md5 6cf5b077 == read md5)  -> REUSE, verdict OK, 22 items, 0 GUI runs
  R2 fake bed, newest read taken on ANOTHER md5                              -> GUI-READ, 1 GUI run, no REUSE line
  R3 fake bed, same md5, no plan licences in that bench                      -> REUSE, verdict MISMATCH (current checker,
                                                                                not the stored 'OK'), 0 GUI runs
  R4 fake bed, same md5, newest read has a False gate                        -> GUI-READ, 1 GUI run
  R5 newest read on another md5, an OLDER read on this md5                   -> GUI-READ (no fallback to older)
  R6 nothing LabVIEW-side imported by the offline path
  C1 write_cycle_card with no bed.json                                       -> bed = {D1_k path, md5 6cf5b077...}
  N1c real L2-A1 read + 1 extra loose-ends item, OLD rule (explicit+derived)  -> extra [] (control: test discriminates)
  N1  same through reverdict() with the explicit file (PD195(b), card 88-4)  -> MISMATCH, extra 1, no derived licence
  K1..K7 guard_card: the stagexec self-test command (3 forms) is allowed on a labview:none card; dry/compound/
     foreign-path/other-refusal forms are still refused; baseline = protocol alone refuses the plain form.
"""
import hashlib, json, os, shutil, sys, tempfile, types

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import cycle_runner as C                                                            # noqa: E402
import errorlist_check as EC                                                        # noqa: E402
import protocol                                                                     # noqa: E402
import guard_card as GC                                                             # noqa: E402

SRC = os.path.join(HERE, "errorlist_D1_k_20260925_100155_20260925_113500.json")
RAW = SRC[:-5] + "_raw.json"
K_MD5 = "6cf5b0777aafa12112d8a786a9eed1ed"
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def md5b(b):
    return hashlib.md5(b).hexdigest()


def run_hook(status_text, bench, out):
    calls = []

    def fake_run(cmd, **kw):
        log = cmd[cmd.index("--log") + 1]
        calls.append(log)
        with open(log, "w", encoding="utf-8") as f:
            f.write("ERRORLIST-VERDICT: OK %s\nBGRUN END rc=0 after 1s\n" % os.path.join(out, "gui.json"))
        return types.SimpleNamespace(stdout="", returncode=0)

    orig = C.subprocess.run
    C.subprocess.run, C.ERRORLIST_REUSE_OUT = fake_run, out
    rl = os.path.join(out, "runner.log")
    try:
        a = types.SimpleNamespace(dry_run=False, dry_cmd=None, no_errorlist_hook=False)
        v, js, why = C.errorlist_hook(81, a, bench, rl, status_text)
    finally:
        C.subprocess.run, C.ERRORLIST_REUSE_OUT = orig, None
    log = open(rl, encoding="utf-8").read() if os.path.exists(rl) else ""
    return v, js, calls, log


def fake_bench(tmp, bed, reads):
    """reads = [(stamp, md5_recorded, gates_override)] -> main + raw json per read, for bed `bed`."""
    b = os.path.join(tmp, "bench")
    os.makedirs(b, exist_ok=True)
    stem = os.path.splitext(os.path.basename(bed))[0]
    for stamp, m, gov in reads:
        d = json.load(open(SRC, encoding="utf-8"))
        d.update(bed=bed, bed_md5_before=m, bed_md5_after=m, stamp=stamp)
        d["gates"].update(gov or {})
        p = os.path.join(b, "errorlist_%s_%s.json" % (stem, stamp))
        json.dump(d, open(p, "w", encoding="utf-8"))
        shutil.copyfile(RAW, p[:-5] + "_raw.json")
    return b


def main():
    tmp = tempfile.mkdtemp(prefix="elreuse81_")
    # STALE PIN FIXED (card 88-3): R1 and C1 read the LIVE STATUS.md, which named D1_k as the bed when this test was
    # written; Pre-decided 195(a) moved the bed to D1_l2_a1_20260925_235224.vi, so both gates followed STATUS to a bed
    # they do not describe. The fixture is D1_k, so the status text is pinned to it (`current-bed:` wins,
    # errorlist_check.py:166).
    status = "current-bed: D1_k_20260925_100155.vi\n"
    # R1 real data
    o1 = os.path.join(tmp, "r1"); os.makedirs(o1)
    v, js, calls, log = run_hook(status, HERE, o1)
    j = json.load(open(js, encoding="utf-8")) if js and os.path.exists(js) else {}
    # STALE PIN FIXED (card chat-L2): R1 pinned the raw md5 of read 113500 (432f7297...), the newest D1_k read when
    # this test was written. A later real read on the SAME bed md5 (172834, raw 839ac213...) is now the newest one,
    # and the hook correctly reuses the NEWEST read (R5 pins "no fallback to older"). The expectation is therefore
    # the raw file of the newest main read for this bed, by stamp - the fixture, not the hook, was out of date.
    import glob as _glob
    _mains = sorted(p for p in _glob.glob(os.path.join(HERE, "errorlist_D1_k_20260925_100155_*.json"))
                    if not p.endswith(("_raw.json", "_reuse.json")))
    want_raw = md5b(open(_mains[-1][:-5] + "_raw.json", "rb").read()) if _mains else None
    gate("R1 real bed D1_k, unchanged md5 -> REUSE, OK, 22 items, 0 GUI runs",
         v == "OK" and not calls and "| REUSE | OK |" in log and j.get("item_count") == 22 and j.get("extra") == []
         and j.get("bed_md5") == K_MD5 and j.get("reused_raw_md5") == want_raw,
         (v, len(calls), j.get("item_count"), j.get("extra"), j.get("licence_usage"), log[-300:]))
    # fake bed in a fake claudeDev
    cd = os.path.join(tmp, "claudeDev"); os.makedirs(cd)
    bed = os.path.join(cd, "D1_zz_selftest81.vi")
    open(bed, "wb").write(b"bed-A")
    ma, mb = md5b(b"bed-A"), md5b(b"bed-B")
    st = "bed is D1_zz_selftest81.vi\n"
    orig_cd = EC.CLAUDEDEV
    EC.CLAUDEDEV = cd
    try:
        b2 = fake_bench(os.path.join(tmp, "r2"), bed, [("20260925_120000", mb, None)])
        v, js, calls, log = run_hook(st, b2, b2)
        gate("R2 changed md5 -> GUI-READ, 1 GUI run, no REUSE", v == "OK" and len(calls) == 1 and "REUSE" not in log
             and "GUI-READ" in log, (v, len(calls), log[-300:]))
        b3 = fake_bench(os.path.join(tmp, "r3"), bed, [("20260925_120000", ma, None)])
        v, js, calls, log = run_hook(st, b3, b3)
        j = json.load(open(js, encoding="utf-8")) if js and os.path.exists(js) else {}
        gate("R3 same md5, no licences -> REUSE MISMATCH (current checker, source said OK), 0 GUI runs",
             v == "MISMATCH" and not calls and "| REUSE | MISMATCH |" in log and j.get("source_verdict") == "OK"
             and len(j.get("extra") or []) == 22, (v, len(calls), j.get("source_verdict"), len(j.get("extra") or [])))
        b4 = fake_bench(os.path.join(tmp, "r4"), bed, [("20260925_120000", ma, {"all_items_read": False})])
        v, js, calls, log = run_hook(st, b4, b4)
        gate("R4 same md5, incomplete newest read -> GUI-READ", len(calls) == 1 and "REUSE" not in log and
             "incomplete" in log, (v, len(calls), log[-300:]))
        b5 = fake_bench(os.path.join(tmp, "r5"), bed, [("20260925_110000", ma, None), ("20260925_120000", mb, None)])
        v, js, calls, log = run_hook(st, b5, b5)
        gate("R5 newest read on another md5, older on this md5 -> GUI-READ (no fallback)",
             len(calls) == 1 and "REUSE" not in log, (v, len(calls), log[-300:]))
    finally:
        EC.CLAUDEDEV = orig_cd
    lvmods = [m for m in ("gscript", "win32com", "pythoncom", "lv_errorlist", "stagekit") if m in sys.modules]
    gate("R6 nothing LabVIEW-side imported by the offline path", not lvmods, lvmods)
    # C1 cycle card bed
    cb = os.path.join(tmp, "c1"); os.makedirs(cb)
    a = types.SimpleNamespace(max_min=60)
    p, why = C.write_cycle_card(cb, 999, status, "claude-opus-5-5", "medium", None, None, a)
    card = json.load(open(p, encoding="utf-8")) if p else {}
    gate("C1 cycle card carries the bed {path, md5} with no bed.json", (card.get("bed") or {}).get("md5") == K_MD5
         and os.path.basename((card.get("bed") or {}).get("path", "")) == "D1_k_20260925_100155.vi",
         (why, card.get("bed")))
    # N1 (card 88-4, PD195(b)): explicit expected file + ONE extra loose-ends item -> MISMATCH. Real bench, so
    # plan_for_bed DOES find sim/l2a1's open_rows; the control N1c shows the OLD rule (derived licences added) would
    # have absorbed the item (review archive/peer/2026-09-26-c88-reuse-stalepin.md:92: the test must discriminate).
    l2 = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_l2_a1_20260925_235224.vi"
    l2main = os.path.join(HERE, "errorlist_D1_l2_a1_20260925_235224_20260926_001456.json")
    l2exp = os.path.join(HERE, "errorlist_expected_D1_l2_a1_20260925_235224.json")
    raw = json.load(open(l2main[:-5] + "_raw.json", encoding="utf-8"))
    loose = next(i for i in raw["items"] if "wirehaslooseends" in EC.norm("%s %s" % (i.get("raw"), i.get("detail"))))
    raw["items"].append(dict(loose, index=len(raw["items"])))
    n1raw = os.path.join(tmp, "n1_raw.json")
    json.dump(raw, open(n1raw, "w", encoding="utf-8"))
    _sp, _pp, plan = EC.plan_for_bed(l2, HERE)
    items = [dict(i) for i in raw["items"]]
    old_extra = EC.compare(items, json.load(open(l2exp, encoding="utf-8"))["expected"], EC.derive_expected(plan))[0]
    gate("N1c control: OLD rule (explicit + derived) absorbs the extra loose-ends item -> extra []",
         bool(plan) and old_extra == [], (_pp, old_extra))
    v, out = EC.reverdict(l2, l2main, n1raw, HERE, tmp, l2exp)
    jn = json.load(open(out, encoding="utf-8"))
    gate("N1 explicit file + 1 extra loose-ends item -> MISMATCH, extra 1, no derived licence",
         v == "MISMATCH" and len(jn["extra"]) == 1 and "loose" in (jn["extra"][0] or "").lower()
         and all(u["kind"] in ("explicit", "header_of_next") for u in jn["licence_usage"]),
         (v, jn["extra"], [u["kind"] for u in jn["licence_usage"]][-3:]))
    # K guard_card exemption, bound to this very card (labview: none)
    card_path = os.path.join(HERE, "cards", "task_81-1.json")
    orig_b = protocol.binding
    protocol.binding = lambda aid: {"card": card_path}

    def dec(cmd):
        return GC.decide({"agent_id": "selftest81", "agent_type": "material", "tool_name": "Bash",
                          "tool_input": {"command": cmd}})
    try:
        base_ok, base_msg = protocol.hook_decision({"agent_id": "selftest81", "agent_type": "material",
                                                    "tool_name": "Bash",
                                                    "tool_input": {"command": "py tools/stagexec.py selftest"}})
        gate("K0 baseline: protocol alone refuses the self-test on labview:none", not base_ok and
             "flags.labview" in (base_msg or ""), base_msg)
        allow = ["py tools/stagexec.py selftest",
                 'cd "%s" && py -u tools/stagexec.py selftest' % ROOT,
                 "MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/x.log -- py -u tools/stagexec.py selftest"]
        for i, c in enumerate(allow, 1):
            rc, msg = dec(c)
            gate("K%d allowed: %s" % (i, c[:70]), rc == 0, msg)
        refuse = ["py tools/stagexec.py dry tools/bench/plan_x.json",
                  "py tools/stagexec.py selftest; py tools/stagexec.py run p.json",
                  "git commit -m x"]
        for i, c in enumerate(refuse, 4):
            rc, msg = dec(c)
            gate("K%d refused: %s" % (i, c[:70]), rc == 2, msg)
        # a foreign stagexec.py does not exist, so protocol has no source to refuse; the matcher itself must say no
        gate("K8 the exemption matcher rejects a foreign path and accepts this project's absolute path",
             not GC.pure_selftest("py C:/elsewhere/tools/stagexec.py selftest") and
             GC.pure_selftest('py "%s" selftest' % os.path.join(TOOLS, "stagexec.py")))
        # K9 = the discriminating test of review hyp-selftest-elreuse-81 (archive/peer/2026-09-25-hyp-selftest-elreuse-81.md):
        # the reviewer predicted the cd-prefixed foreign form is exempted (rc 0) - a guard_card hole, measured by card 81-3.
        # RE-PINNED by card 116-3 D2 (the one pin change allowed): guard_card.py now accepts `cd` only to the project
        # root, so the foreign form must be REFUSED (rc 2); K2 above still allows `cd "<ROOT>" && ...`.
        rc9, msg9 = dec('cd "C:/elsewhere" && py tools/stagexec.py selftest')
        gate("K9 cd <foreign dir> && py tools/stagexec.py selftest is REFUSED (rc 2, hole closed by card 116-3)",
             rc9 == 2, (rc9, msg9))
    finally:
        protocol.binding = orig_b
    shutil.rmtree(tmp, ignore_errors=True)
    n_pass = sum(1 for _l, ok in gates if ok)
    n_fail = len(gates) - n_pass
    first = next((l for l, ok in gates if not ok), None)
    print("=== GATES: %d pass / %d fail%s" % (n_pass, n_fail, "; failing: " + first if first else ""))
    print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, [],
                                                    status="PASS" if not n_fail else "FAIL")))
    return 0 if not n_fail else 1


if __name__ == "__main__":
    sys.exit(main())
