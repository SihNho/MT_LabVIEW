@echo off
rem build.bat - compile mt_track.cu into mt_track.dll (CUDA 12.6 + MSVC 2022 Build Tools), sm_75 = RTX 2060
call "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat" >nul
set CUDA_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v12.6
set PATH=%CUDA_PATH%\bin;%PATH%
nvcc --version
nvcc -O2 -arch=sm_75 -allow-unsupported-compiler -Xcompiler "/MD /O2 /wd4819 /utf-8" -Xlinker "/DEF:mt_track.def" -shared -o mt_track.dll mt_track.cu -lcufft -luser32 2>&1
if errorlevel 1 (echo BUILD FAILED & exit /b 1)
dir mt_track.dll
echo BUILD OK
