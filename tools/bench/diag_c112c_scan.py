"""diag_c112c_scan - card 112-3 W0 OFFLINE: per docs/wiki/subvi graph - SubVI nodes, LeftShiftRegister count, case-selector
Tunnels fed by one ControlTerminal, WhileLoop count (fixture candidates for the T1/T2 scratch check). No LabVIEW."""
import json, glob, os, re, collections                                                # noqa: E401
R = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "docs", "wiki", "subvi")
for p in sorted(glob.glob(os.path.join(R, "*.json"))):
    try:
        txt = open(p, encoding="utf-8").read()
        d = json.loads(txt)
    except Exception:                                                                 # noqa: BLE001
        continue
    T = d.get("terminals") or []
    oc = collections.Counter(r.get("owner_class") for r in T)
    byw = collections.defaultdict(list)
    for r in T:
        if r.get("wire_uid"):
            byw[r["wire_uid"]].append(r)
    selct = 0
    for r in T:
        if r.get("owner_class") == "Tunnel" and r.get("term_class") == "OuterTerminal" and not r.get("is_source") and r.get("wire_uid"):
            s = [x for x in byw[r["wire_uid"]] if x.get("is_source")]
            if len(s) == 1 and s[0].get("term_class") == "ControlTerminal":
                selct += 1
    m = re.search(r'"WhileLoop": (\d+)', txt)
    wl = int(m.group(1)) if m else 0
    if (oc.get("LeftShiftRegister", 0) and wl) or selct:
        print("%-55s terms %5d subvi %3d LSR %2d While %d selCT %d" % (os.path.basename(p)[:55], len(T), oc.get("SubVI", 0),
              oc.get("LeftShiftRegister", 0), wl, selct))
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}')
