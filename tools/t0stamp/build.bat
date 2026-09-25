@echo off
rem build.bat - t0stamp.dll (card 90-1). Compiler: MSVC 14.44 BuildTools 2022 x64 (same toolchain as tools/gpu/cuda/build.bat).
rem Output: tools\t0stamp\t0stamp.dll, then copied to claudeDev by selftest.py --install (never by this script).
setlocal
cd /d "%~dp0"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
cl /nologo /O2 /W4 /MT /LD /Fe:t0stamp.dll t0stamp.c kernel32.lib /link /MACHINE:X64
set RC=%ERRORLEVEL%
del /q t0stamp.obj t0stamp.exp 2>nul
echo BUILD_RC=%RC%
exit /b %RC%
