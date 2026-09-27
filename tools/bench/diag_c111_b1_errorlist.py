r"""diag_c111_b1_errorlist - card 111-1 (docs/d1-loop12-17-split-plan.md PD224(h)). Reads the FULL Error List of the saved
L2-B1 file, the owner loops of #11261 / #8323's terminal and wire 25618's ends, and attributes every item at COUNT level.
PRIOR ART (checked first): tools/errorlist_check.py main() (scratch copy, Ctrl+E, Ctrl+L, per-item double-click, bed md5,
Esc) is REUSED UNCHANGED - only lv_errorlist.read gets max_steps (new parameter, default 80 unchanged); owner reads =
build_d1_v0.owner_of (l2a1_facts_80.py:63); terminal rows = allterms.read_terms; item classes = diag_c110d_elcounts.py
KEYS; RBW wire ends = the stage log's `RBW ENDS` fact (diag_c110d_rbwends.py); L2-A3 licences = its expected file.
NEVER saves or runs a VI; the B1 file itself is never opened (two byte-identical scratch copies, both deleted).
PREDICTION CONTRACT:
  G0 lv_errorlist py_compile OK; G1 the reader ran with max_steps >= 150; G2 every errorlist_check gate True
  (all_items_read: items == the window's own N, expected 99); G3 c111 copy written, items == N; G4 wire 25618 present in
  the saved file with 2 ends, owner chains of #11261 and #8323 end at a loop or the top diagram; G5 every item in one
  class; G6 B1 md5 == b705728a...; G7 LabVIEW gone; G8 own scratch deleted. Attribution counts are FACTS, not gates.
  `offline <older read json>` = SELF-CHECK of the attribution code only (no LabVIEW): G2-G4 are printed as FACTS there,
  because they describe that older read and an owner file only the LabVIEW phase writes.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c111_b1_errorlist.log -- py -u tools/bench/diag_c111_b1_errorlist.py"""
import collections, glob, json, os, py_compile, re, shutil, subprocess, sys, time  # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
for _p in ("tools", os.path.join("tools", "bench"), os.path.join("tools", "recipes")):
    sys.path.insert(0, os.path.join(ROOT, _p))
import errorlist_check as EC, protocol                                             # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
BED, MD5, MAXSTEPS, WIRE, LOOPS = (EC.CLAUDEDEV + r"\D1_l2_b1_20260927_193100.vi", "b705728ab0714dc8179fc955283800f9", 180,
                                   25618, {637: "1.1", 10170: "1.2", 23041: "1.7"})
STEM = os.path.splitext(os.path.basename(BED))[0]
C111, C111RAW = os.path.join(B, "errorlist_%s_c111.json" % STEM), os.path.join(B, "errorlist_%s_c111_raw.json" % STEM)
FACTS, OWNJ = os.path.join(B, "facts_c111a_b1_errorlist.md"), os.path.join(B, "errorlist_%s_c111_owners.json" % STEM)
KEYS = [("buildarr", ["buildarr", "containsunwired"]), ("split1darr", ["split1darr", "containsunwired"]), ("bundle", ["bundle", "containsunwired"]),
        ("indexarr", ["indexarr", "containsunwired"]), ("replacearr", ["replacearr", "containsunwired"]), ("imagein", ["imagein", "notwi"]),
        ("subvi_not_wired", ["isnotwired"]), ("unwiredselector", ["unwiredselector"]), ("sr_unwired_inside", ["unwiredfrominsidetheloop"]),
        ("sr_type_undefined", ["datatypeisundefined"]), ("tunnel_to_input", ["outputlooptunnel"]), ("undirected_tunnel", ["undirectedtunnel"]),
        ("different_types", ["differenttypes"]), ("different_dims", ["differentdimensions"]),
        ("no_source", ["connectsoneormoredatasinksbuthasnosource"]), ("unconnected", ["completelyunconnectedwire"]), ("loose_ends", ["wirehaslooseends"])]
POOL = {"unconnected": "termless", "loose_ends": "source-only", "different_types": "src+sink", "different_dims": "src+sink",
        "no_source": "sink-only", "tunnel_to_input": "sink-only", "undirected_tunnel": "sink-LoopTunnel",
        "sr_unwired_inside": "sink-RSR", "sr_type_undefined": "sink-RSR"}
NODEKW = {"buildarr": "buildarray", "split1darr": "split1d", "bundle": "bundle", "indexarr": "indexarray", "replacearr": "replacearray"}
gates, T0, OFF = {}, time.time(), (sys.argv[1:2] == ["offline"])
SRC = sys.argv[2] if OFF and len(sys.argv) > 2 else None          # offline self-check on an OLDER read (no LabVIEW)
if SRC:
    FACTS = os.path.join(B, "facts_c111a_b1_errorlist_selfcheck.md")


def gate(k, ok, msg):
    gates[k] = bool(ok)
    print("%s  %s  %s" % ("PASS" if ok else "FAIL", k, str(msg)[:700]), flush=True)


def lv_count():
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq LabVIEW.exe"], capture_output=True, text=True)
    return r.stdout.lower().count("labview.exe")


try:
    py_compile.compile(os.path.join(ROOT, "tools", "lv_errorlist.py"), doraise=True); gate("G0_py_compile", True, "lv_errorlist.py")  # noqa: E702
except Exception as e:                                                             # noqa: BLE001
    gate("G0_py_compile", False, e)
gate("G6a_bed_md5_before", EC.md5(BED) == MD5, EC.md5(BED))
OWN = {}
if not OFF:
    EC._lv_imports()
    E, _orig, RD = EC.E, EC.E.read, {}

    def _read(*a, **k):
        k["max_steps"] = MAXSTEPS
        r = _orig(*a, **k); RD["max_steps"] = r.get("max_steps"); return r              # noqa: E702
    E.read, sys.argv = _read, [sys.argv[0], "--vi", BED]
    rc = EC.main()
    gate("G1_max_steps_param", (RD.get("max_steps") or 0) >= 150, RD)
    import gscript as g, allterms as AT, build_d1_v0 as BD                         # noqa: E401
    S = os.path.join(g.CLAUDEDEV, "_c111own_%s.vi" % time.strftime("%H%M%S"))
    shutil.copyfile(BED, S)
    try:
        g.open_panel(S); rows, _ = AT.read_terms(S)                                     # noqa: E702

        def chain(u):
            out = []
            for _n in range(10):
                c, o = BD.owner_of(S, u, strict=False)
                out.append([c, o])
                if not o or c in ("WhileLoop", "ForLoop", "TopLevelDiagram"):
                    break
                u = o
            return out
        t8323 = [r for r in rows if r["term_uid"] == 8323]
        OWN = {"wire": [r for r in rows if r["wire_uid"] == WIRE], "n11261": [r for r in rows if r["owner_uid"] == 11261],
               "t8323": t8323, "chain_11261": chain(11261), "chain_8323": chain(8323),
               "chain_8323_owner": chain(t8323[0]["owner_uid"]) if t8323 else None, "chain_23058": chain(23058)}
    except Exception as e:                                                         # noqa: BLE001
        OWN["error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    for f in (lambda: g.close_panel(S),):
        try:
            f()
        except Exception as e:                                                     # noqa: BLE001
            OWN["close_error"] = str(e)[:200]
    json.dump(OWN, open(OWNJ, "w", encoding="utf-8"), indent=1, default=str)
    subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True)
    for _i in range(15):
        if lv_count() == 0:
            break
        time.sleep(2)
    for _i in range(6):
        try:
            os.remove(S); break                                                    # noqa: E702
        except OSError:
            time.sleep(2)
    gate("G8_own_scratch_deleted", not os.path.exists(S), S)
    main = sorted(p for p in glob.glob(os.path.join(B, "errorlist_%s_2*.json" % STEM)) if not re.search(r"_(raw|reuse)\.json$", p))[-1]
    fresh = os.path.getmtime(main) > T0 and os.path.exists(main[:-5] + "_raw.json")   # review c111a-selfcheck: never copy an OLD read
    gate("G2a_fresh_read", fresh, (os.path.basename(main), rc))
    if not fresh:
        for p in (C111, C111RAW):
            if os.path.exists(p):
                os.remove(p)
        sys.exit(2)
    shutil.copyfile(main, C111); shutil.copyfile(main[:-5] + "_raw.json", C111RAW)   # noqa: E702
OWN = json.load(open(OWNJ, encoding="utf-8")) if os.path.exists(OWNJ) else {}
_m = os.path.join(B, SRC) if SRC else C111
M, items = json.load(open(_m, encoding="utf-8")), json.load(open(_m[:-5] + "_raw.json", encoding="utf-8"))["items"]
if SRC:     # self-check on an OLDER read: G2-G4 describe that read / an absent owner file, so they are FACTS here, not gates
    gate, _gate = (lambda k, ok, msg: print("FACT  %s (self-check, not gated) ok=%s %s" % (k, bool(ok), str(msg)[:300]), flush=True)), gate
gate("G2_errorlist_gates", M.get("gates") and all(M["gates"].values()), {"n": M.get("n_reported"), "items": M.get("item_count"), "gates": M.get("gates"), "src": M.get("stamp")})
gate("G3_c111_copy", len(items) == M.get("n_reported"), (os.path.basename(C111), len(items), M.get("n_reported")))
ch = lambda c: [x for x in (c or []) if x[0] in ("WhileLoop", "ForLoop", "TopLevelDiagram")]  # noqa: E731
gate("G4_wire_and_owners", len(OWN.get("wire") or []) == 2 and ch(OWN.get("chain_11261")) and ch(OWN.get("chain_8323_owner")),
     {k: OWN.get(k) for k in ("wire", "chain_11261", "chain_8323", "chain_8323_owner", "chain_23058", "error")})
if SRC:
    gate = _gate
# ---- attribution (offline) -------------------------------------------------------------------------------------------
L15 = next((x[1] for x in OWN.get("chain_23058") or [] if x[0] in ("WhileLoop", "ForLoop")), None)
if L15:
    LOOPS[L15] = "1.5"
plan = json.load(open(os.path.join(B, "plan_l2b1.json"), encoding="utf-8"))
ROWN = collections.defaultdict(set)
for r in plan["open_rows"]:
    ROWN[r["node"]].add("%s:%s" % (r["node"], r["term"]))
    for u in [int(x) for x in re.findall(r"#(\d+)", r["why"])]:
        if u != r["node"]:
            ROWN[u].add("%s:%s(cited #%d)" % (r["node"], r["term"], u))
base = json.load(open(os.path.join(ROOT, plan["finalized"]["base"]["path"]), encoding="utf-8"))
CLS = dict((int(o["uid"]), o["class"]) for o in base.get("objs") or [])
import jev_candidates as JC                                                        # noqa: E402
LAB = JC.node_labels_default()
lines = open(os.path.join(B, "stage_d1_l2b1_c110d.log"), encoding="utf-8", errors="replace").read().splitlines()
import ast                                                                         # noqa: E402
_el = next(ln for ln in lines if "FACT  RBW ENDS" in ln)
ENDS = ast.literal_eval(_el[_el.index("{"):])                                      # as diag_c110d_rbwends.py:23
exp3 = json.load(open(os.path.join(B, "errorlist_expected_D1_l2_a3_20260927_151224.json"), encoding="utf-8"))["expected"]
A3W = set()
for e in exp3:
    c = e["cite"].split(";")[0]
    if "RBW" not in c:                                   # open-row cites carry node uids / line numbers, not wires
        continue
    A3W |= set(int(x) for x in (re.findall(r"w(\d+)", c) or re.findall(r"\b(\d{2,5})\b", c.split("wires", 1)[-1])))
cnt, byk, unk = collections.Counter(), collections.defaultdict(list), []
for i, it in enumerate(items):
    n = EC.norm("%s %s %s" % (it.get("object") or "", it.get("raw") or "", it.get("detail") or ""))
    k = next((k for k, ks in KEYS if all(x in n for x in ks)), None)
    cnt[k or "UNCLASSIFIED"] += 1; byk[k or "UNCLASSIFIED"].append(i)             # noqa: E702
    if not k:
        unk.append((i, (it.get("raw") or "")[:90]))
gate("G5_every_item_one_class", not unk, unk)
a3 = collections.Counter()
for e in exp3:
    a3[next((k for k, ks in KEYS if ks[0] in "".join(e["norm_all"])), "?")] += int(e["count"])
print("L2-A3 class counts %s ; L2-A3 RBW wires %d %s" % (dict(a3), len(A3W), sorted(A3W)), flush=True)
pools = collections.defaultdict(list)
for w, ends in ENDS.items():
    src, snk = [x for x in ends if x[3]], [x for x in ends if not x[3]]
    k = "termless" if not ends else "source-only" if not snk else "sink-only" if not src else "src+sink"
    pools[k].append(w)
    for x in snk if k == "sink-only" else []:
        if x[1] in ("LoopTunnel", "RightShiftRegister"):
            pools["sink-LoopTunnel" if x[1] == "LoopTunnel" else "sink-RSR"].append((w, x[0]))
rowhit = lambda w: sorted(set(r for x in ENDS.get(w, []) for r in ROWN.get(x[0], ())))  # noqa: E731
wid = lambda x: x[0] if isinstance(x, tuple) else x                                # noqa: E731
A3LEFT = dict((pk, sum(1 for x in v if wid(x) in A3W)) for pk, v in pools.items())   # review c111a: credits <= wires still there
print("L2-A3 wires still in B1's RBW set per pool %s (L2-A3 class counts %s)" % (A3LEFT, dict(a3)), flush=True)
T, tot, USED, REUSED = [], collections.Counter(), set(), []
for k, _ks in KEYS:
    n = cnt.get(k, 0)
    if not n:
        continue
    lic3 = min(n, a3.get(k, 0))
    if k in POOL:                                          # a wire class: capped by the L2-A3 wires still present in its pool
        lic3 = min(lic3, A3LEFT.get(POOL[k], 0)); A3LEFT[POOL[k]] = A3LEFT.get(POOL[k], 0) - lic3   # noqa: E702
    rest, lo, why = n - lic3, [], ""
    if k in NODEKW:
        cand = sorted(u for u in ROWN if NODEKW[k] in EC.norm("%s %s" % (LAB.get(u, ""), CLS.get(u, ""))) and u != 2626)
        lo = ["#%d %s" % (u, sorted(ROWN[u])) for u in cand][:rest]; why = "open-row nodes of that kind (2626 counted in L2-A3)"
    elif k == "imagein" or k == "subvi_not_wired":
        lo = [r for r in sorted({x for s in ROWN.values() for x in s}) if EC.norm(r.split(":", 1)[1]) in "".join(EC.norm(items[i].get("raw")) for i in byk[k])][:rest]
        why = "open rows whose terminal name is in the item text"
    elif k in POOL:
        pk = POOL[k]; share = [kk for kk, p in POOL.items() if p == pk]                  # noqa: E702
        new = [x for x in pools[pk] if wid(x) not in A3W]
        good = [(x, rowhit(wid(x))) for x in new if rowhit(wid(x))]
        free = [(x, r) for x, r in good if wid(x) not in USED]                       # review c111a: no wire credited twice
        REUSED += [(k, wid(x)) for x, r in good if wid(x) in USED][:rest]
        lo = ["%s %s" % (x, r[:2]) for x, r in free][:rest]
        USED |= set(wid(x) for x, r in free[:rest])
        why = "B1-new %s RBW ends (%d new, %d with an open-row end, %d of them already credited to another class; pool shared by %s)" % (
            pk, len(new), len(good), len(good) - len(free), share)
    ua = rest - len(lo)
    tot["n"] += n; tot["a3"] += lic3; tot["open"] += len(lo); tot["ua"] += max(ua, 0)  # noqa: E702
    tot["ua_classlevel"] += 0 if a3.get(k) else max(ua, 0)
    T.append((k, n, lic3, lo, max(ua, 0), why + ("; class IN L2-A3 expected" if a3.get(k) else "; class NOT in L2-A3 expected")))
for k, n, l3, lo, ua, why in T:
    print("ATTR %-18s n %3d  L2-A3 %2d  open-row %2d  UNATTRIBUTED %2d  | %s | %s" % (k, n, l3, len(lo), ua, why, lo[:6]), flush=True)
print("ATTR TOTAL items %d = L2-A3 %d + open-row %d + UNATTRIBUTED %d (count-capped); UNATTRIBUTED if any count of an L2-A3 "
      "class counts as licensed: %d" % (tot["n"], tot["a3"], tot["open"], tot["ua"], tot["ua_classlevel"]), flush=True)
print("ATTR NOT CREDITED (wire already credited to another class, counted UNATTRIBUTED): %d %s" % (len(REUSED), REUSED), flush=True)
b11 = [(i, items[i].get("raw"), (items[i].get("show_error") or {}).get("bd_after")) for i in byk.get("buildarr", [])]
dt = [(i, items[i].get("raw"), (items[i].get("show_error") or {}).get("bd_after")) for k in ("different_types", "different_dims") for i in byk.get(k, [])]
md = ["# Card 111-1 - Error List of D1_l2_b1_20260927_193100.vi (md5 %s), full read" % MD5, "",
      "Source read: `%s` (+ `_raw`), window N %s, items %d, all gates %s. Log `tools/bench/diag_c111_b1_errorlist.log`." % (
          os.path.basename(C111), M.get("n_reported"), len(items), all((M.get("gates") or {}).values())), "",
      "## Owners (read from a byte-identical scratch of the saved file)", "",
      "- #11261 chain %s; #8323 row %s, its owner chain %s; loop 1.5 = %s; loop map %s" % (
          OWN.get("chain_11261"), [(r.get("owner_uid"), r.get("owner_class"), r.get("wire_uid")) for r in OWN.get("t8323") or []],
          OWN.get("chain_8323_owner"), L15, LOOPS),
      "- wire %d ends: %s" % (WIRE, [(r.get("owner_uid"), r.get("owner_class"), r.get("term_name"), r.get("is_source")) for r in OWN.get("wire") or []]),
      "- #11261 terminals: %s" % [(r.get("term_name"), r.get("is_source"), r.get("wire_uid")) for r in OWN.get("n11261") or []], "",
      "## Items that can be on #11261 / wire 25618 (text; double-click capture)", ""] + ["- item %s: %s -> %s" % x for x in b11 + dt] + [
      "", "## Attribution (count level; rule: L2-A3 class count first, then plan_l2b1 open rows by node kind / terminal name / "
      "B1-new RBW wire ends on an open-row node or a uid cited in its `why`; everything else UNATTRIBUTED)", "",
      "| class | n | L2-A3 | open-row | UNATTRIBUTED | rule / rows |", "|---|---|---|---|---|---|"] + [
      "| %s | %d | %d | %d | %d | %s: %s |" % (k, n, l3, len(lo), ua, why, "; ".join(str(x) for x in lo)) for k, n, l3, lo, ua, why in T] + [
      "", "**Totals:** items %d = L2-A3 %d + open-row %d + UNATTRIBUTED %d (count-capped). If any count of a class already in "
      "the L2-A3 expected file counts as licensed, UNATTRIBUTED = %d." % (tot["n"], tot["a3"], tot["open"], tot["ua"], tot["ua_classlevel"]),
      "", "Not credited because the wire was already credited to another class (one wire, one credit; review "
      "`archive/peer/2026-09-27-c111a-selfcheck.md` §1): %s. `unconnected` wires have no ends, so they can never match an open "
      "row; the attribution matches COUNTS, not item identities (no uid per item)." % REUSED]
open(FACTS, "w", encoding="utf-8").write("\n".join(md) + "\n")
gate("G6_bed_md5_after", EC.md5(BED) == MD5, EC.md5(BED))
gate("G7_labview_gone", lv_count() == 0, lv_count())
arts = [{"path": os.path.relpath(p, ROOT), "md5": EC.md5(p)} for p in (C111, C111RAW, OWNJ, FACTS, os.path.join(ROOT, "tools", "lv_errorlist.py")) if os.path.exists(p)]
n_pass = sum(1 for x in gates.values() if x); n_fail = len(gates) - n_pass           # noqa: E702
first = next((k for k, x in gates.items() if not x), None)
print("=== GATES: %d pass / %d fail%s ; %.0f s" % (n_pass, n_fail, "; failing: " + first if first else "", time.time() - T0))
print(protocol.result_line(protocol.make_result(n_pass, n_fail, first, arts)))
sys.exit(0 if n_fail == 0 else 1)
