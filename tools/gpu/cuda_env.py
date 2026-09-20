"""cuda_env.py - make the pip-installed CUDA 11 libraries (nvidia-*-cu11 wheels) visible to CuPy on Windows: import this
BEFORE cupy.  The machine has no CUDA toolkit; driver 457.51 (CUDA 11.1) runs the 11.8 runtime through minor-version
compatibility."""
import glob
import os
import sys

_added = []
for d in glob.glob(os.path.join(sys.prefix, "Lib", "site-packages", "nvidia", "*", "bin")):
    if os.path.isdir(d):
        os.environ["PATH"] = d + os.pathsep + os.environ.get("PATH", "")
        try:
            os.add_dll_directory(d)
        except Exception:
            pass
        _added.append(d)
