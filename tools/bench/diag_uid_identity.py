r"""diag_uid_identity.py - READ-ONLY. Cycle 20 step 2's FIRST measurement, run on its own because the op it was
bundled with is STOPPED.

WHY THIS FILE EXISTS SEPARATELY. `tools/recipes/build_opfstunnelterm_v0.py` carried this measurement as its
phase I1/I2. Its prior-art review (`archive/peer/2026-09-18-priorart-fstunnel-reader.md`) returned
`contradicted / unread-evidence / helper-exists / already-measured`, which armed the launch gate against that
recipe (`sha de04c05f5f65`), and cycle-20 Pre-decided 4 says a material session does not write the release. So
the BUILD does not run. This file contains **no build, no new op VI, no scratch VI and no edit of any kind** -
it opens VIs read-only through ops that already exist and answers the two questions that do not depend on the
stopped artifact:

  I1  WHICH VI does each fixture uid belong to? STATUS.md:59-61 records the motor census's 97/43 call sites keyed
      to the 3StateClamping ORIGINAL while every cached node/terminal index is keyed to the V6 COPY, so this is
      read from the machine, not assumed: for BOTH VIs, is 28343 a LoopTunnel, is 43605 a FlatSequenceOuterTunnel,
      is 44036 a SubVI?
  I2  the KNOWN-GOOD FIXTURE, through the ops that already exist: `gscript.tunnels()` (OpTunnels_v0) +
      `OpWireSource_v5` - does `LoopTunnel #28343` resolve to `Max Trans Pos.vi - 'Magnet position output'`
      (docs/frame-loop-wire-graph.md:264)?

REUSED, NOTHING REBUILT: gscript.uids/count (OpReportAll_v0), gscript.tunnels (OpTunnels_v0,
tools/bench/optunnels_labels.json), OpWireSource_v5 + tools/bench/opwiresource_v5_labels.json,
tools/bench/main_vi_nodeterms.json, main_vi_subvis.json, d1_step0_census.json,
build_opconstvalue_v1.fresh/lv_pid.

Cycle-20 Pre-decided 1: no motor move, no serial port, `motor_gate.py --execute` not called, no camera; both
originals' md5 BEFORE and AFTER; nothing saved.

PREDICTION CONTRACT:
  D0 both originals + the donor op are byte-identical before and after; handle count reported both ways.
  D1 for each VI the four traverse counts and the three uid memberships are REPORTED (a measurement, not a gate).
  D2 exactly one of the two VIs, or both, contain uid 28343 as a LoopTunnel - and the one that does resolves it
     to a source terminal owned by a SubVI named Max Trans Pos.vi with the tunnel's outer name
     'Magnet position output'.

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_uid_identity.log -- py -u tools/bench/diag_uid_identity.py

If the Bash allowlist in this environment refuses a command that does not START with `py tools/bgrun.py` (it did
on 2026-09-18), pass the material declaration as a TRAILING token instead - `guard_bash.MARKER_RE` matches
`MATERIAL=1` anywhere in the command string, and `bgrun` cannot take a shell env prefix because it execs an argv
list (tools/bgrun.py:112). This script ignores argv apart from echoing the declaration:

  py tools/bgrun.py --max-min 25 --log tools/bench/diag_uid_identity.log -- py -u tools/bench/diag_uid_identity.py MATERIAL=1
"""
import hashlib
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "recipes"))
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid  # noqa: E402

TRACKING = os.path.dirname(ROOT)
ORIG_3STATE = os.path.join(TRACKING, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
V6 = os.path.join(TRACKING, "Min_Track N beads V6_ParallelLoop.vi")
DONOR = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
V5_LABELS = os.path.join(HERE, "opwiresource_v5_labels.json")
NODETERMS = os.path.join(HERE, "main_vi_nodeterms.json")
SUBVIS = os.path.join(HERE, "main_vi_subvis.json")
CENSUS = os.path.join(HERE, "d1_step0_census.json")
OUT = os.path.join(HERE, "diag_uid_identity.json")

FIX_TUNNEL = 28343
FIX_TUNNEL_INDEX = 65      # d1_step0_census.json tunnels[] row carrying uid 28343
FSOT_UID = 43605           # probe_flatseq_walk_run2.log:82-83 - where the cycle-19 walk stopped
ASI_NODE = 44036           # d10 Nodes[1], ASI Move Axis to Position.vi

FILES = [ORIG_3STATE, V6, DONOR]
RES = {"gates": [], "identity": {}, "fixture": {}, "md5": {}, "handles": {}}
_ESEQ = [0]


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:240]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:400]})
    return bool(ok)


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        _ESEQ[0] += 1
        return f"ERR#{_ESEQ[0]} {e}"


def snapshot(tag):
    d = {p: md5(p) for p in FILES}
    RES["md5"][tag] = d
    print(f"\n-- md5 {tag} --", flush=True)
    for p, h in d.items():
        print(f"   {h}  {os.path.basename(p)}", flush=True)
    return d


def handles(tag):
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                              "Measure-Object -Property HandleCount -Sum).Sum"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        n = int(out) if out else 0
    except Exception as e:
        n = f"ERR {str(e)[:60]}"
    RES["handles"][tag] = n
    print(f"  HANDLES {tag}: {n}  (fresh baseline ~31,500)", flush=True)
    return n


def identity():
    print("\n================ I1  WHICH VI DOES EACH UID BELONG TO ================", flush=True)
    for name, path in (("V6 working copy", V6), ("3StateClamping ORIGINAL", ORIG_3STATE)):
        rec = {"path": path}
        print(f"\n   --- {name}\n       {path}", flush=True)
        for cls in ("Diagram", "LoopTunnel", "FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel", "SubVI", "Wire"):
            try:
                us = g.uids(path, cls)
                rec[cls] = {"count": len(us), "has_28343": FIX_TUNNEL in us,
                            "has_43605": FSOT_UID in us, "has_44036": ASI_NODE in us}
                print(f"       {cls:26s} n={len(us):5d}   28343={FIX_TUNNEL in us}   43605={FSOT_UID in us}   "
                      f"44036={ASI_NODE in us}", flush=True)
            except Exception as e:
                rec[cls] = f"EXC {str(e)[:170]}"
                print(f"       {cls:26s} RAISED {str(e)[:170]}", flush=True)
        RES["identity"][name] = rec
    try:
        nt = json.load(open(NODETERMS, encoding="utf-8"))
        RES["identity"]["nodeterms_json_vi"] = nt.get("vi")
        hit = [(dk, nd["n"]) for dk, v in nt["diagrams"].items() for nd in v.get("nodes", [])
               if nd["uid"] == ASI_NODE]
        print(f"\n   OFFLINE main_vi_nodeterms.json 'vi' = {nt.get('vi')}", flush=True)
        print(f"   OFFLINE   uid {ASI_NODE} appears there at (diagram, Nodes[]) {hit[:3]}", flush=True)
    except Exception as e:
        print(f"   OFFLINE main_vi_nodeterms.json EXC {str(e)[:140]}", flush=True)
    try:
        cen = json.load(open(CENSUS, encoding="utf-8"))
        row = [t for t in cen.get("tunnels", []) if t.get("uid") == FIX_TUNNEL]
        RES["identity"]["census_md5"] = cen.get("md5")
        print(f"   OFFLINE d1_step0_census.json md5 field = {cen.get('md5')}", flush=True)
        print(f"   OFFLINE   its row for LoopTunnel {FIX_TUNNEL}: {row[0] if row else 'ABSENT'}", flush=True)
    except Exception as e:
        print(f"   OFFLINE d1_step0_census.json EXC {str(e)[:140]}", flush=True)


def v5_read(vi5, lab, target, uid, term_index):
    for k in ("ownercls", "cls_back", "cast_class"):
        try:
            vi5.SetControlValue(lab[k], "POISON")
        except Exception:
            pass
    for k in ("uid_back", "owner_uid", "recip_wire"):
        try:
            vi5.SetControlValue(lab[k], 0)
        except Exception:
            pass
    try:
        vi5.SetControlValue(lab["is_source"], False)
    except Exception:
        pass
    vi5.SetControlValue("vi path", target)
    vi5.SetControlValue(lab["uid_in"], int(uid))
    vi5.SetControlValue(lab["term_index"], int(term_index))
    err = ""
    try:
        g._run(vi5)
        err = g._err(vi5, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:90]}"
    errs = " ".join(x for x in ((g._err(vi5, lab[k]) or "") for k in
                                ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO")
                                if k in lab) if x)[:200]
    r = {"i": term_index, "is_source": bool(vi5.GetControlValue(lab["is_source"])),
         "owner_class": vi5.GetControlValue(lab["ownercls"]),
         "owner_uid": int(vi5.GetControlValue(lab["owner_uid"])),
         "uid_back": int(vi5.GetControlValue(lab["uid_back"])),
         "cls_back": vi5.GetControlValue(lab["cls_back"]),
         "recip_wire": int(vi5.GetControlValue(lab["recip_wire"])), "err": err, "errs": errs}
    print(f"         Terms[{term_index}] src={r['is_source']} owner {r['owner_class']!r:.26} uid {r['owner_uid']} "
          f"recip={r['recip_wire']} err={r['err'][:50]!r} {r['errs'][:60]}", flush=True)
    return r


def fixture(target, vi5, lab):
    print("\n================ I2  the KNOWN-GOOD FIXTURE through the EXISTING ops ================", flush=True)
    rec = {"target": target}
    try:
        t = g.tunnels(target, FIX_TUNNEL_INDEX)
    except Exception as e:
        rec["tunnels_row"] = f"EXC {str(e)[:200]}"
        RES["fixture"] = rec
        print(f"   gscript.tunnels RAISED {str(e)[:200]}", flush=True)
        return must("D2 LoopTunnel #28343 -> Max Trans Pos.vi - 'Magnet position output'", False, rec["tunnels_row"])
    rec["tunnels_row"] = t
    print(f"   gscript.tunnels(target, {FIX_TUNNEL_INDEX}) -> uid {t['uid']} out_name {t['out_name']!r} "
          f"out_is_source {t['out_is_source']} out_wire {t['out_wire']} in_wires {t['in_wires']}", flush=True)
    if t["uid"] != FIX_TUNNEL:
        RES["fixture"] = rec
        return must("D2 LoopTunnel #28343 -> Max Trans Pos.vi - 'Magnet position output'", False,
                    f"traverse index {FIX_TUNNEL_INDEX} is uid {t['uid']}, not {FIX_TUNNEL}")
    print(f"   -> resolving the OUTER wire {t['out_wire']} with OpWireSource_v5", flush=True)
    rows = []
    for i in range(8):
        r = v5_read(vi5, lab, target, t["out_wire"], i)
        rows.append(r)
        if r["owner_uid"] == 0 and not r["is_source"] and r["owner_class"] in ("POISON", ""):
            break
    srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == int(t["out_wire"])]
    src = srcs[0] if srcs else None
    rec["rows"] = rows
    rec["outer_wire_source"] = src
    name = ""
    if src:
        try:
            sv = json.load(open(SUBVIS, encoding="utf-8"))
            name = str(sv.get("by_uid", {}).get(str(src["owner_uid"]), "NOT IN THE SUBVI CENSUS"))
        except Exception as e:
            name = f"(subvis lookup EXC {str(e)[:80]})"
    rec["subvi_lookup"] = name
    print(f"   SOURCE of wire {t['out_wire']}: {src}\n   subVI census says: {name}", flush=True)
    RES["fixture"] = rec
    ok = bool(src) and src["owner_class"] == "SubVI" and "Max Trans Pos" in name \
        and t["out_name"] == "Magnet position output"
    return must("D2 LoopTunnel #28343 -> Max Trans Pos.vi - 'Magnet position output'", ok,
                f"out_name {t['out_name']!r}; source {src}; lookup {name}")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT D0..D2 - see this file's docstring. READ-ONLY: no build, no op, no scratch VI.",
          flush=True)
    print(f"   material-session declaration present in the launch command: {'MATERIAL=1' in sys.argv}", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    before = snapshot("before")
    try:
        fresh()
        handles("after a fresh LabVIEW, before any work")
        lab = json.load(open(V5_LABELS, encoding="utf-8"))
        identity()
        must("D1 the identity measurement ran on both VIs", len(RES["identity"]) >= 2, str(list(RES["identity"])))
        vi5 = g.op(DONOR)
        fixture(V6, vi5, lab)
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        try:
            g.reset()
        except Exception:
            pass
        handles("after the run")
        after = snapshot("after")
        must("D0 both originals and the donor op are byte-identical before and after",
             all(before[p] == after[p] and not str(before[p]).startswith("ERR#") for p in FILES),
             str([os.path.basename(p) for p in FILES if before[p] != after[p]]))
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:52] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
