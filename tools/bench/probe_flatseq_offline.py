r"""probe_flatseq_offline.py - OFFLINE half of cycle-19 M1/M2/M4. No LabVIEW, no COM, no serial. Read-only.

REUSE CHECK (CLAUDE.md "before creating any new op/tool/recipe"):
  - tools/bench/census_dnc_property_ids.py  = the existing pattern for "build a property node per candidate id,
    read the data terminal name" -> reused verbatim in the ONLINE probe, not re-invented here.
  - gscript.report_all / node_terms / node_terms_uid / uids  = existing readers; no new op is built.
  - docs/vi-server-ids.json + docs/NAMES.md:215 = the short-name registry; consulted before any id is used.
  - tools/bench/d1_tunnel_sources.json = the already-measured 18 from-tunnel rows incl. the 14
    FlatSequenceInnerTunnel owners -> the M1 instance uids come from here, they are NOT re-measured.
  - tools/bench/motor_census_3state-ORIGINAL.json / _v6-workingcopy.json = the census's own output -> M4.

PREDICTION CONTRACT (offline):
  P1  tools/bench/d1_tunnel_sources.json exists and holds >= 14 rows whose owner class is
      'FlatSequenceInnerTunnel', each with a non-zero owner uid.   [if uids are 0 -> M1 part (b) has no instance
      to read and that is itself the answer]
  P2  the two motor_census json files both exist; the ORIGINAL one totals 97 call sites and 43 in scope.
  P3  exactly one of the two census json files contains a site with node uid 44036 on diagram 10.
  P4  no cached node/terminal census file on disk is keyed to the 3StateClamping ORIGINAL's md5
      (c39f36e0675339673b707c59f0784fee) - the caches were all taken on the V6 working copy.
"""
import glob
import hashlib
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "bench")
PROJ = os.path.dirname(ROOT)

ORIG_3STATE = os.path.join(os.path.dirname(os.path.dirname(PROJ)),
                           "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
V6 = os.path.join(PROJ, "Min_Track N beads V6_ParallelLoop.vi")


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERR {e}"


def jload(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def find_originals():
    print("== ORIGINALS ON DISK ==", flush=True)
    cands = []
    for pat in ("Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi",):
        for base in (PROJ, os.path.dirname(PROJ), os.path.dirname(os.path.dirname(PROJ))):
            p = os.path.join(base, pat)
            if os.path.exists(p):
                cands.append(p)
    for p in glob.glob(os.path.join(os.path.dirname(os.path.dirname(PROJ)), "**",
                                   "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi"), recursive=True):
        cands.append(p)
    seen = []
    for p in cands:
        rp = os.path.abspath(p)
        if rp not in seen:
            seen.append(rp)
            print(f"   3STATE {rp} md5={md5(rp)}", flush=True)
    if os.path.exists(V6):
        print(f"   V6     {os.path.abspath(V6)} md5={md5(V6)}", flush=True)
    return seen


def m1_instances():
    print("\n== M1a: the 14 FlatSequenceInnerTunnel rows already on disk ==", flush=True)
    p = os.path.join(BENCH, "d1_tunnel_sources.json")
    if not os.path.exists(p):
        print("   P1 FAIL: no d1_tunnel_sources.json", flush=True)
        return []
    d = jload(p)
    rows = d if isinstance(d, list) else d.get("rows", d)
    if isinstance(rows, dict):
        rows = list(rows.values())
    fs = []
    for r in rows:
        if not isinstance(r, dict):
            continue
        blob = json.dumps(r)
        if "FlatSequenceInnerTunnel" in blob:
            fs.append(r)
    print(f"   rows total={len(rows)}  FlatSequenceInnerTunnel rows={len(fs)}", flush=True)
    for r in fs[:20]:
        print(f"   ROW {json.dumps(r)[:300]}", flush=True)
    print(f"   P1 {'PASS' if len(fs) >= 14 else 'FAIL'} (>=14 rows)", flush=True)
    return fs


def m4_census():
    print("\n== M4: which VI is the census keyed to ==", flush=True)
    out = {}
    for tag, name in (("3STATE-ORIGINAL", "motor_census_3state-ORIGINAL.json"),
                      ("V6-WORKINGCOPY", "motor_census_v6-workingcopy.json"),
                      ("ALL", "motor_census_all.json")):
        p = os.path.join(BENCH, name)
        if not os.path.exists(p):
            print(f"   {tag}: MISSING {p}", flush=True)
            continue
        d = jload(p)
        blob = json.dumps(d)
        sites = None
        for k in ("sites", "call_sites", "rows"):
            if isinstance(d, dict) and k in d:
                sites = d[k]
                break
        if sites is None and isinstance(d, list):
            sites = d
        n = len(sites) if sites is not None else "?"
        vip = ""
        if isinstance(d, dict):
            for k in ("vi_path", "target", "vi", "path", "source_vi"):
                if k in d:
                    vip = str(d[k])
                    break
        inscope = None
        if isinstance(sites, list):
            inscope = sum(1 for s in sites if isinstance(s, dict) and s.get("in_scope") in (True, 1, "yes"))
            if inscope == 0:
                inscope = sum(1 for s in sites if isinstance(s, dict)
                              and str(s.get("kind", "")).upper() in ("COMMAND", "CONFIGURE", "ASSUMED_MOTION"))
        print(f"   {tag}: file_mtime={time.strftime('%Y-%m-%d %H:%M', time.localtime(os.path.getmtime(p)))} "
              f"sites={n} in_scope={inscope} vi_path_field={vip!r}", flush=True)
        if isinstance(d, dict):
            print(f"      top-level keys: {list(d.keys())[:15]}", flush=True)
        has44036 = "44036" in blob
        print(f"      contains uid 44036: {has44036}", flush=True)
        out[tag] = (d, sites)
        if isinstance(sites, list):
            for s in sites:
                if isinstance(s, dict) and (s.get("uid") == 44036 or s.get("node_uid") == 44036
                                            or str(s.get("uid")) == "44036"):
                    print(f"      SITE 44036 -> {json.dumps(s)[:400]}", flush=True)
    return out


def m4_caches():
    print("\n== M4b: cached node/terminal censuses on disk, and which md5 they are keyed to ==", flush=True)
    pats = ["main_vi_nodeterms.json", "d1_step0_census.json", "main_vi_*.json", "*nodeterms*.json",
            "*census*.json"]
    seen = set()
    for pat in pats:
        for p in sorted(glob.glob(os.path.join(BENCH, pat))):
            if p in seen:
                continue
            seen.add(p)
            try:
                d = jload(p)
            except Exception as e:
                print(f"   {os.path.basename(p)}: unreadable {e}", flush=True)
                continue
            blob = json.dumps(d)[:400000]
            keyed = []
            for h, tag in (("c39f36e0675339673b707c59f0784fee", "3STATE-ORIGINAL"),
                           ("2a78e17c449cacdaf5da389818526859", "V6-WORKINGCOPY")):
                if h in blob:
                    keyed.append(tag)
            vipaths = set()
            for k in ("vi_path", "target", "vi", "path", "source_vi", "md5"):
                if isinstance(d, dict) and k in d:
                    vipaths.add(f"{k}={str(d[k])[:120]}")
            age_d = (time.time() - os.path.getmtime(p)) / 86400.0
            print(f"   {os.path.basename(p):46s} size={os.path.getsize(p):>9d} age={age_d:5.2f}d "
                  f"md5-keyed={keyed or 'NONE'} {sorted(vipaths)}", flush=True)


def main():
    print("PREDICTION CONTRACT is in this file's docstring. Offline only: no LabVIEW, no COM, no serial.",
          flush=True)
    find_originals()
    m1_instances()
    m4_census()
    m4_caches()
    print("\nOFFLINE PROBE DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
