"""probe_env.py - card 90-1 step-0 facts: compiler, LabVIEW bitness, existing CLFN ops, LabVIEW process. Read-only."""
import os, glob, struct, subprocess, sys, platform
print("cl:", glob.glob('C:/Program Files*/Microsoft Visual Studio/*/*/VC/Tools/MSVC/*/bin/Hostx64/x64/cl.exe'))
print("vcvars:", glob.glob('C:/Program Files*/Microsoft Visual Studio/*/*/VC/Auxiliary/Build/vcvars64.bat'))
print("nvcc:", glob.glob('C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/*/bin/nvcc.exe'))
p = r'C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe'
b = open(p, 'rb').read(4096); pe = struct.unpack_from('<I', b, 60)[0]
print('LabVIEW.exe PE Machine=0x%X (0x8664=x64, 0x14C=x86)' % struct.unpack_from('<H', b, pe + 4)[0])
print("python:", sys.version, platform.architecture())
cd = 'C:/Program Files/National Instruments/LabVIEW 2026/user.lib/claudeDev'
print("claudeDev matches:", [f for f in os.listdir(cd) if 't0stamp' in f.lower() or 'clfn' in f.lower() or f.startswith('FPTARGET')])
print("labview procs:", [l for l in subprocess.run('tasklist', capture_output=True, text=True).stdout.splitlines() if 'labview' in l.lower()])
