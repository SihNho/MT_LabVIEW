"""selftest_bgrun_reap_install.py - card 92-4 rule 1: replace tools/bgrun.py ATOMICALLY (write temp, os.replace),
never half-written, because a LabVIEW card may be running bgrun concurrently. Source = the edited candidate in the
session scratchpad (argv[1]); it is py_compiled first. Prints md5 before/after and a RESULT line."""
import hashlib
import os
import py_compile
import shutil
import sys

PROJECT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(PROJECT, "tools"))
import protocol  # noqa: E402


def md5(p):
    with open(p, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def main():
    src = sys.argv[1]
    dst = os.path.join(PROJECT, "tools", "bgrun.py")
    py_compile.compile(src, doraise=True)
    py_compile.compile(os.path.join(PROJECT, "tools", "bgrun_reap.py"), doraise=True)
    print("before:", md5(dst))
    tmp = dst + ".tmp92"
    shutil.copyfile(src, tmp)
    os.replace(tmp, dst)
    print("after: ", md5(dst), "src:", md5(src))
    ok = md5(dst) == md5(src)
    print(protocol.result_line(protocol.make_result(1 if ok else 0, 0 if ok else 1, None if ok else "md5 mismatch")))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
