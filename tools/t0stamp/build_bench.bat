@echo off
rem build_bench.bat - bench.exe (card 93-2), same MSVC toolchain as build.bat.
setlocal
cd /d "%~dp0"
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
cl /nologo /O2 /W3 /MT /Fe:bench.exe bench.c kernel32.lib /link /MACHINE:X64
set RC=%ERRORLEVEL%
del /q bench.obj 2>nul
echo BUILD_RC=%RC%
exit /b %RC%
