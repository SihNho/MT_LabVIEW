"""card 143-5 probe (offline, read-only): the rebased s03 plan's base and action 1. No LabVIEW."""
import hashlib, json, os                                                                    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))                     # noqa: E731
p = J("tools/bench/plan_ring_p4_s03v18.json")
fz = p["finalized"]
print("FACT a1", p["actions"][0]["id"], "src", p["actions"][0]["src"], "dst", p["actions"][0]["dst"])
print("FACT base", p["base"], "| finalized.base", fz["base"], "| rebase", fz.get("rebase"), "| plan_in", fz["plan_in"])
b = J(fz["base"]["path"])
print("FACT base doc md5(vi)", b.get("md5"), "vi", b.get("vi"), "fs_carried", {k: v for k, v in (b.get("fs_carried") or {}).items() if k in ("real_graph", "provisional")})
print("FACT base file md5", hashlib.md5(open(os.path.join(ROOT, fz["base"]["path"]), "rb").read()).hexdigest())
print("FACT final", p.get("final"), "open_rows_match", fz.get("open_rows_match"), "n actions", len(p["actions"]), "step_files", len(fz.get("step_files") or []),
      "end_cdiff_rows", len(fz.get("end_cdiff_rows") or []))
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 0, "fail": 0}, "first_fail": None, "artefacts": []}))
