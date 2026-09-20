"""cpu_topology.py - logical-processor -> physical-core mapping on Windows (GetLogicalProcessorInformation), no
Sysinternals needed. Prints each core's LP mask and the affinity mask that removes exactly ONE physical core (the
last one). Used by g9_affinity_run.py; peer review archive/peer/2026-09-14-g9-five-core-plan.md ("derive the mask
from the actual topology, not from an assumed numbering").
  py tools/bench/cpu_topology.py
"""
import ctypes
import ctypes.wintypes as wt
import json
import sys

RelationProcessorCore = 0


class CACHE_DESCRIPTOR(ctypes.Structure):
    _fields_ = [("Level", ctypes.c_ubyte), ("Associativity", ctypes.c_ubyte), ("LineSize", wt.WORD),
                ("Size", wt.DWORD), ("Type", ctypes.c_int)]


class _U(ctypes.Union):
    _fields_ = [("Flags", ctypes.c_ubyte), ("NodeNumber", wt.DWORD), ("Cache", CACHE_DESCRIPTOR),
                ("Reserved", ctypes.c_ulonglong * 2)]


class SLPI(ctypes.Structure):
    _fields_ = [("ProcessorMask", ctypes.c_size_t), ("Relationship", ctypes.c_int), ("u", _U)]


def cores():
    k32 = ctypes.windll.kernel32
    n = wt.DWORD(0)
    k32.GetLogicalProcessorInformation(None, ctypes.byref(n))
    count = n.value // ctypes.sizeof(SLPI)
    buf = (SLPI * count)()
    if not k32.GetLogicalProcessorInformation(buf, ctypes.byref(n)):
        raise OSError("GetLogicalProcessorInformation failed")
    out = []
    for e in buf:
        if e.Relationship == RelationProcessorCore:
            m = int(e.ProcessorMask)
            out.append({"mask": m, "lps": [i for i in range(64) if m >> i & 1]})
    return sorted(out, key=lambda c: c["lps"][0])


def main():
    cs = cores()
    all_mask = sum(c["mask"] for c in cs)
    minus_one = all_mask & ~cs[-1]["mask"]
    print(json.dumps({"cores": cs, "all_mask": hex(all_mask), "minus_one_core_mask": hex(minus_one),
                      "removed_core_lps": cs[-1]["lps"]}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
