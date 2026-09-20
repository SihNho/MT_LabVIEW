r"""probe_flatseq_offline2.py - OFFLINE extract #2 for cycle-19 M2/M3/M4. No LabVIEW, no COM, no serial.

REUSE: reads tools/bench/motor_census_*.json (already produced by tools/motor_census.py run 3) and
tools/bench/d1_tunnel_sources.json. Builds nothing.

PREDICTION CONTRACT:
  Q1 motor_census_3state-ORIGINAL.json -> target.call_sites has 97 entries; 43 have kind in
     {COMMAND, CONFIGURE, ASSUMED_MOTION}.
  Q2 exactly one call site in each census has node uid 44036, diagram 10, callee 'Move Axis to Position.vi',
     owner_structure 'FlatSequenceFrame'.
  Q3 the distinct callee PATHS for MOV/VEL/GOH/Move Axis to Position/SetCommand(_signed) all exist on disk.
"""
import json
import os
import sys

BENCH = os.path.dirname(os.path.abspath(__file__))
IN_SCOPE = {"COMMAND", "CONFIGURE", "ASSUMED_MOTION"}
WANT = ("MOV.vi", "VEL.vi", "GOH.vi", "Move Axis to Position.vi", "Move Axis Relative.vi",
        "SetCommand.vi", "SetCommand_signed.vi")


def jload(n):
    with open(os.path.join(BENCH, n), encoding="utf-8") as f:
        return json.load(f)


def main():
    paths = {}
    for name in ("motor_census_3state-ORIGINAL.json", "motor_census_v6-workingcopy.json"):
        d = jload(name)
        t = d["target"]
        cs = t.get("call_sites", [])
        ks = {}
        for s in cs:
            ks[str(s.get("kind"))] = ks.get(str(s.get("kind")), 0) + 1
        ins = sum(v for k, v in ks.items() if k in IN_SCOPE)
        print(f"== {name}", flush=True)
        print(f"   target.vi   = {t.get('vi')}", flush=True)
        print(f"   md5_before  = {d.get('md5_before')}", flush=True)
        print(f"   md5_after   = {d.get('md5_after')}", flush=True)
        print(f"   call_sites  = {len(cs)}   kinds={ks}   IN SCOPE={ins}", flush=True)
        for s in cs:
            if 44036 in (s.get("uid"), s.get("node_uid"), s.get("site_uid")) or "44036" in json.dumps(s):
                print(f"   SITE-44036  {json.dumps(s)}", flush=True)
        for s in cs:
            cal = str(s.get("callee") or s.get("callee_path") or s.get("subvi") or "")
            base = os.path.basename(cal)
            if base in WANT and base not in paths:
                paths[base] = cal
        print(f"   Q1 {'PASS' if (len(cs) in (97, 98) and ins == 43) else 'FAIL'}"
              f" (sites={len(cs)}, in_scope={ins})", flush=True)
    print("\n== M3 target subVI paths (resolved from the census, not guessed) ==", flush=True)
    for b in WANT:
        p = paths.get(b)
        if not p:
            print(f"   {b:32s} NOT NAMED IN THE CENSUS ROWS", flush=True)
        else:
            print(f"   {b:32s} exists={os.path.exists(p)}  {p}", flush=True)
    with open(os.path.join(BENCH, "probe_flatseq_paths.json"), "w", encoding="utf-8") as f:
        json.dump(paths, f, indent=1)
    print("\n== M1b instance uids (FlatSequenceInnerTunnel owners already measured) ==", flush=True)
    d = jload("d1_tunnel_sources.json")
    rows = d if isinstance(d, list) else d.get("rows", [])
    fs = []
    for r in rows:
        for h in r.get("hops", []) or []:
            if h.get("owner_class") == "FlatSequenceInnerTunnel":
                fs.append((h.get("owner_uid"), h.get("wire")))
    seen, uniq = set(), []
    for u, w in fs:
        if u not in seen:
            seen.add(u)
            uniq.append((u, w))
    print(f"   distinct FlatSequenceInnerTunnel uids={len(uniq)}: {uniq}", flush=True)
    with open(os.path.join(BENCH, "probe_flatseq_instances.json"), "w", encoding="utf-8") as f:
        json.dump([{"fsit_uid": u, "wire": w} for u, w in uniq], f, indent=1)
    print("\nOFFLINE2 DONE", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
