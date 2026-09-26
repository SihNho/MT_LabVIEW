r"""diag_c103_wait_donor - card 103-1 P3 (PD215(b) op 41 route): a `Wait (ms)` DONOR for OpPrimCopyNested_v0, registered
exactly like Max & Min (diag_c100_verbs_build.prim_donor:200-229 - byte copy of an NI example under claudeDev, node FOUND by
label, lowest uid taken, md5 pinned) and its terminal rows READ with allterms.read_terms/OpAllTerms_v1 (diag_c100_6_maxmin).
PRIOR ART CHECKED: claudeDev\OpPrimDonor_v0.vi (= examples\Comparison\Max and Min.vi) is scanned FIRST (D0); only if it holds no
`Wait (ms)` are NI example candidates byte-copied, one file each (OpWaitDonor_cand<i>.vi), until the first hit; the hit is
re-copied as OpWaitDonor_v0.vi, candidates deleted after a LabVIEW kill. NI examples and vi.lib are only READ (rule 1).
PREDICTION: a hit exists among the candidates; its node carries exactly 2 terminal rows: sink `milliseconds to wait`, source
`millisecond timer value` (plan r7_wait); NI example bytes unchanged; LabVIEW gone at exit. No new op (handle rule n/a).
Writes tools/bench/facts_c103_donor.json and facts_c100_oplabels.json OpPrimCopyNested_v0.donors["Wait (ms)"].
    py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_c103_wait_donor.log -- py -u tools/bench/diag_c103_wait_donor.py"""
import hashlib, json, os, shutil, subprocess, sys, time                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P                                                               # noqa: E402
import gscript as g                                                                # noqa: E402
import allterms as AT                                                              # noqa: E402
import bench_prep                                                                  # noqa: E402

LAB_P = os.path.join(HERE, "facts_c100_oplabels.json")
CD = g.CLAUDEDEV
EX = r"C:\Program Files\National Instruments\LabVIEW 2026\examples"
DONOR = os.path.join(CD, "OpWaitDonor_v0.vi")
CANDS = [os.path.join(EX, p) for p in (
    r"Structures\Shift Registers and Tunnels\Running Average with Shift Registers.vi",
    r"Structures\Feedback Node\Feedback Node - Building an Array.vi",
    r"Synchronization\Notifier\Simple Notifier.vi",
    r"Structures\Case Structure\Case Structure - Selector Data Types.vi",
    r"Structures\Shift Registers and Tunnels\Loop Tunnel Modes.vi",
    r"Structures\Event Structure\Handling Mouse Wheel Events.vi")]
WANT = sorted([("milliseconds to wait", False), ("millisecond timer value", True)])
gates, out = [], {"candidates": []}


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)
    return ok


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def scan(path):
    """(hits [(uid, diagram_uid)], class map) - nodes labelled `Wait (ms)` on every diagram of `path`."""
    hits = []
    for d in g.report_all(path, "Diagram"):
        for r in g.node_labels(path, d["i"]):
            if (r["label"] or "").strip() == "Wait (ms)":
                hits.append((int(r["uid"]), int(d["uid"])))
    cls = dict((int(o["uid"]), o["class"]) for o in g.report_all(path, "Node"))
    return sorted(hits), cls


# run 1 (diag_c103_wait_donor.log:4): close_panel raised 0x47D on a VI whose panel the read ops never opened. Review
# archive/peer/2026-09-27-c103-wait-donor-closepanel.md: the close calls have no job (LabVIEW is killed before the re-copy and at
# exit) and a catch-all would hide RPC/modal errors -> every close_panel call is DELETED, nothing is swallowed.
def kill():
    g.reset()
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60)
    time.sleep(4)
    return "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()


def main():
    src, reg, made = None, None, []
    try:
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        h0 = bench_prep.labview_handles()
        prim = os.path.join(CD, "OpPrimDonor_v0.vi")
        m_prim = md5(prim)
        hits, _c = scan(prim)
        out["OpPrimDonor_v0"] = {"wait_hits": hits}
        print("  FACT D0 OpPrimDonor_v0.vi (Max and Min example copy) `Wait (ms)` hits: {0}".format(hits), flush=True)
        for i, ex in enumerate(CANDS):
            if not os.path.exists(ex):
                out["candidates"].append({"src": ex, "exists": False}); continue   # noqa: E702
            cp = os.path.join(CD, "OpWaitDonor_cand{0}.vi".format(i)); shutil.copyfile(ex, cp); made.append(cp)   # noqa: E702
            hits, cls = scan(cp)
            out["candidates"].append({"src": ex, "copy": cp, "hits": hits})
            print("  FACT candidate {0}: {1} `Wait (ms)` hits {2}".format(i, os.path.basename(ex), hits), flush=True)
            if hits:
                src = ex; u, d = hits[0]                                           # lowest uid, as Max & Min   # noqa: E702
                reg = {"src_copy": cp, "uid": u, "diagram": d, "class": cls.get(u)}; break   # noqa: E702
        if not gate("W1 a `Wait (ms)` node found by label in an NI example copy", reg, out["candidates"]):
            raise RuntimeError("no Wait (ms) donor among the candidates")
        out["handles"] = [h0, bench_prep.labview_handles()]
        gate("K1 LabVIEW gone before the re-copy (candidates unloadable)", kill())
        m_ex = md5(src)
        shutil.copyfile(src, DONOR); time.sleep(0.3)                               # noqa: E702
        for p in made:
            os.remove(p)
        gate("W2 OpWaitDonor_v0.vi is a byte copy of the NI example; candidate copies deleted",
             md5(DONOR) == m_ex and not any(os.path.exists(p) for p in made), (m_ex, src))
        bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702
        hits2, cls2 = scan(DONOR)
        gate("W3 the same uid/diagram in OpWaitDonor_v0.vi (uids persist in the file)",
             (reg["uid"], reg["diagram"]) in hits2, hits2)
        rows, _dt = AT.read_terms(DONOR, AT.OP_ALLTERMS_V1)
        mine = [r for r in rows if int(r["owner_uid"]) == reg["uid"]]
        got = sorted((r["term_name"], bool(r["is_source"])) for r in mine)
        out.update({"donor": DONOR, "md5": m_ex, "source": src, "uid": reg["uid"], "diagram": reg["diagram"],
                    "class": cls2.get(reg["uid"]), "rows": mine, "names": got, "names_match_plan": got == WANT,
                    "owner_class": sorted(set(r["owner_class"] for r in mine)), "all_hits": hits2})
        gate("W4 donor terminal rows == plan r7_wait (sink `milliseconds to wait`, source `millisecond timer value`)",
             got == WANT, (got, out["owner_class"], out["class"]))
        lab = json.load(open(LAB_P, encoding="utf-8"))
        lab["OpPrimCopyNested_v0"]["donors"]["Wait (ms)"] = {"donor": DONOR, "md5": m_ex, "uid": reg["uid"],
                                                             "diagram": reg["diagram"], "class": out["class"], "source": src}
        json.dump(lab, open(LAB_P, "w", encoding="utf-8"), indent=1)
        gate("R1 registered in facts_c100_oplabels.json OpPrimCopyNested_v0.donors['Wait (ms)']",
             "Wait (ms)" in json.load(open(LAB_P, encoding="utf-8"))["OpPrimCopyNested_v0"]["donors"])
        gate("R2 OpPrimDonor_v0.vi and the NI example bytes unchanged", md5(prim) == m_prim and md5(src) == m_ex)
    except Exception as e:                                                         # noqa: BLE001
        gate("X no exception", False, "{0}: {1}".format(type(e).__name__, str(e)[:300]))
    finally:
        gone = kill()
        gate("H LabVIEW gone at exit", gone)
        json.dump(out, open(os.path.join(HERE, "facts_c103_donor.json"), "w", encoding="utf-8"), indent=1, default=str)
    n = sum(1 for _l, ok in gates if ok)
    ff = next((lab for lab, ok in gates if not ok), None)
    print(P.result_line(P.make_result(n, len(gates) - n, ff)), flush=True)
    return 0 if ff is None else 1


if __name__ == "__main__":
    sys.exit(main())
