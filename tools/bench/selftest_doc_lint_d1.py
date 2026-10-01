r"""selftest_doc_lint_d1.py - card chat-D1 step 5: doc_lint's line cap (L10), frozen footer (L11) and the INDEX as
the current plan (current_plans). Offline, temp tree under %TEMP%, no LabVIEW.

Prediction contract (7 checks):
 T1 a `status: current` doc of 401 lines FAILs L10
 T2 a `status: frozen` doc of 900 lines is not capped (L10 PASS when it is the only doc)
 T3 an exempt reference table (`docs/NAMES.md`, 500 lines) WARNs (L10a), never FAILs
 T4 a grandfathered doc WARNs (L10b), never FAILs
 T5 a frozen doc WITHOUT the FROZEN footer WARNs L11; with it, PASS
 T6 current_plans() returns `<docs>/d1/INDEX.md` when it is `status: current`, and not a frozen cycle plan
 T7 the real repository: L10 PASS, L4 one current plan == docs/d1/INDEX.md, L8 PASS
"""
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import doc_lint as DL  # noqa: E402
import protocol  # noqa: E402

FM = "---\ntype: plan\nstatus: %s\ndate: 2026-10-02\n---\n"


def mk(d, name, status, n, footer=False):
    p = os.path.join(d, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    body = FM % status + "".join("line %d\n" % i for i in range(n - 5))
    if footer:
        body += "## FROZEN 2026-10-02 (card chat-D1) - index: `docs/d1/INDEX.md`\n"
    with open(p, "w", encoding="utf-8") as fh:
        fh.write(body)
    return p


def levels(check_prefix):
    return [r[0] for r in DL.RESULT if r[1].startswith(check_prefix)]


def main():
    res, n_fail, first = [], 0, None
    tmp = tempfile.mkdtemp(prefix="dl_d1_")
    try:
        def case(tag, ok, detail):
            nonlocal n_fail, first
            res.append(ok)
            print("%s %s | %s" % (tag, "PASS" if ok else "FAIL", detail), flush=True)
            if not ok:
                n_fail += 1
                first = first or tag

        a = mk(tmp, "over.md", "current", 401)
        del DL.RESULT[:]
        f, _, _ = DL.check_line_cap([a], ["docs/over.md"])
        case("T1", levels("L10 ") == ["FAIL"] and len(f) == 1, "current 401 lines -> %s" % levels("L10"))

        b = mk(tmp, "frozen.md", "frozen", 900, footer=True)
        del DL.RESULT[:]
        f, _, _ = DL.check_line_cap([b], ["docs/frozen.md"])
        case("T2", levels("L10 ") == ["PASS"] and not f, "frozen 900 lines -> %s" % levels("L10"))

        c = mk(tmp, "NAMES.md", "current", 500)
        del DL.RESULT[:]
        f, rw, _ = DL.check_line_cap([c], ["docs/NAMES.md"])
        case("T3", levels("L10 ") == ["PASS"] and levels("L10a") == ["WARN"] and not f, "exempt -> %s" % levels("L10"))

        g = mk(tmp, "gf.md", "current", 450)
        del DL.RESULT[:]
        f, _, gw = DL.check_line_cap([g], [DL.GRANDFATHERED[0]])
        case("T4", levels("L10 ") == ["PASS"] and levels("L10b") == ["WARN"] and not f, "grandfathered -> %s" % levels("L10"))

        nf = mk(tmp, "nofooter.md", "frozen", 50)
        del DL.RESULT[:]
        bad = DL.check_frozen_footer([nf, b])
        lv1 = levels("L11")
        del DL.RESULT[:]
        bad2 = DL.check_frozen_footer([b])
        case("T5", lv1 == ["WARN"] and len(bad) == 1 and levels("L11") == ["PASS"] and not bad2,
             "no footer -> %s, footer -> %s" % (lv1, levels("L11")))

        docs = os.path.join(tmp, "docs")
        mk(docs, "cycle27-plan.md", "frozen", 20, footer=True)
        idx = mk(docs, os.path.join("d1", "INDEX.md"), "current", 20)
        cur = DL.current_plans(docs)
        case("T6", cur == [idx], "current_plans(temp) -> %s" % [os.path.relpath(p, tmp) for p in cur])

        DL.run(skip_dispositions=True)
        l10 = levels("L10 ")
        l4 = [r for r in DL.RESULT if r[1].startswith("L4")]
        l8 = levels("L8 the current plan")
        ok7 = l10 == ["PASS"] and l4 and l4[0][0] == "PASS" and "docs/d1/INDEX.md" in l4[0][2] and l8 == ["PASS"]
        case("T7", ok7, "repo: L10 %s, L4 %s, L8 %s" % (l10, l4[0][2] if l4 else None, l8))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(protocol.result_line(protocol.make_result(len(res) - n_fail, n_fail, first, [])), flush=True)
    return 0 if n_fail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
