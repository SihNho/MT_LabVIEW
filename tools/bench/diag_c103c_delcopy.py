"""diag_c103c_delcopy - card 103-3 pass line 1 (PD216(f)): delete claudeDev\\D1_s1_dispA_20260927_022749.vi ONLY if its md5 == S1
(3e3d23cefd3a334001aa9d6156bf1aee). Touches no LabVIEW. PREDICTION: both md5 == 3e3d23ce...; file deleted; S1 unchanged."""
import hashlib, json, os, sys                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol                                                                    # noqa: E402
D = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S1 = "3e3d23cefd3a334001aa9d6156bf1aee"
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                      # noqa: E731
cp, s1 = os.path.join(D, "D1_s1_dispA_20260927_022749.vi"), os.path.join(D, "D1_s1_copy.vi")
gates = []
m_s1 = md5(s1); print("S1", s1, os.path.getsize(s1), m_s1); gates.append(m_s1 == S1)   # noqa: E702
if os.path.exists(cp):
    m_cp = md5(cp); print("COPY", cp, os.path.getsize(cp), m_cp)                  # noqa: E702
    ok = m_cp == S1 and m_s1 == S1
    if ok:
        os.remove(cp)
    print("DELETED" if ok else "KEPT (md5 mismatch)", cp, "exists after:", os.path.exists(cp))
    gates.append(ok and not os.path.exists(cp))
else:
    print("COPY absent:", cp); gates.append(True)                                  # noqa: E702
print("S1 after", md5(s1))
rl = getattr(protocol, "result_line", None)
out = {"schema": "result-line/1", "status": "PASS" if all(gates) else "FAIL", "gates": {"pass": sum(gates), "fail": len(gates) - sum(gates)},
       "first_fail": None if all(gates) else "md5 check", "artefacts": []}
print(rl(**out) if callable(rl) and False else "RESULT " + json.dumps(out))
