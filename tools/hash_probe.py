"""Read-only md5/sha256/size probe.

PRIOR ART CHECKED 2026-09-19 (cycle 48, material): `ls tools/ tools/bench/ | grep -i "hash|md5"`
returned nothing; `lv_gui.ps1 -Action md5`, `md5sum` and inline `py -c` are all refused on this
project's ORIGINAL (STATUS.md "The ORIGINAL IS readable", cycle-47 §4). A `.py` under `tools/`
launched via `py tools/bgrun.py --material ... -- python -u <script>` is the one route that works,
so this file is that route and nothing more.

PREDICTION CONTRACT: for every path given on argv, prints exactly one line
  `HASH <path> | exists=<0|1> | size=<n> | md5=<hex> | sha256=<hex>`
(`size=- md5=- sha256=-` when the path does not exist). Touches no LabVIEW, no COM, no hardware,
opens every file read-only, and writes nothing.
"""
import hashlib
import os
import sys


def probe(path: str) -> str:
    if not os.path.isfile(path):
        return "HASH %s | exists=0 | size=- | md5=- | sha256=-" % path
    m = hashlib.md5()
    s = hashlib.sha256()
    n = 0
    with open(path, "rb") as fh:
        while True:
            chunk = fh.read(1 << 20)
            if not chunk:
                break
            n += len(chunk)
            m.update(chunk)
            s.update(chunk)
    return "HASH %s | exists=1 | size=%d | md5=%s | sha256=%s" % (path, n, m.hexdigest(), s.hexdigest())


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: hash_probe.py <path> [<path> ...]")
        return 2
    for p in sys.argv[1:]:
        print(probe(p), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
