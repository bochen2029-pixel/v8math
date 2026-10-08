@echo off
rem build-msvc.cmd: compile netlib fdlibm 5.3 with MSVC x64 (prefixed symbols), then run the
rem Node-vs-fdlibm-vs-CRT bit comparison and the v8math check. Produces build-msvc-x64\fdlibm.lib,
rem verify\result_fdlibm_msvc_x64.txt and verify\result_v8math_msvc_x64.txt. Exit code = v8math result.
rem Needs Visual Studio 2022 (edit the vcvars64 path below for another edition) and node on PATH.
setlocal
set VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvars64.bat
if not exist "%VCVARS%" set VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Auxiliary\Build\vcvars64.bat
if not exist "%VCVARS%" set VCVARS=C:\Program Files\Microsoft Visual Studio\2022\Enterprise\VC\Auxiliary\Build\vcvars64.bat
if not exist "%VCVARS%" set VCVARS=C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat
call "%VCVARS%" >nul 2>&1
if errorlevel 1 ( echo vcvars64 failed & exit /b 1 )
cd /d "%~dp0"
set OUT=build-msvc-x64
if not exist %OUT%\obj mkdir %OUT%\obj
echo === compiling fdlibm 5.3 (netlib) with MSVC x64, _IEEE_LIBM, prefixed symbols ===
cl /nologo /c /O2 /fp:strict /Zc:__STDC__ /W1 /D_IEEE_LIBM /D__LITTLE_ENDIAN /FI"%~dp0fdlibm_rename.h" /Fo%OUT%\obj\ src\e_*.c src\k_*.c src\s_*.c src\w_*.c
if errorlevel 1 ( echo compile failed & exit /b 1 )
lib /nologo /out:%OUT%\fdlibm.lib %OUT%\obj\*.obj
if errorlevel 1 ( echo lib failed & exit /b 1 )
echo === reference values from Node ===
node verify\gen_ref.js verify\ref_node.txt 20000
if errorlevel 1 ( echo gen_ref failed & exit /b 1 )
echo === fdlibm and CRT against Node (pow is expected to differ for fdlibm, see README) ===
rem /MT on purpose: node.exe links the UCRT statically, and the static libucrt and ucrtbase.dll round
rem pow differently in about 0.03% of cases; only the static runtime reproduces node.exe exactly.
cl /nologo /O2 /MT /fp:strict /W3 /Fo%OUT%\ /Fe%OUT%\verify_fdlibm.exe verify\verify_fdlibm.c %OUT%\fdlibm.lib
if errorlevel 1 ( echo harness build failed & exit /b 1 )
%OUT%\verify_fdlibm.exe verify\ref_node.txt > verify\result_fdlibm_msvc_x64.txt
type verify\result_fdlibm_msvc_x64.txt
echo === v8math against Node ===
rem note: a quoted path must not end in a backslash (it would escape the quote), hence the trailing dots
cl /nologo /O2 /MT /fp:strict /EHsc /std:c++17 /W3 /I"%~dp0..\include" /I"%~dp0." /Fo%OUT%\ /Fe%OUT%\verify_v8math.exe verify\verify_v8math.cpp %OUT%\fdlibm.lib
if errorlevel 1 ( echo v8math harness build failed & exit /b 1 )
%OUT%\verify_v8math.exe verify\ref_node.txt > verify\result_v8math_msvc_x64.txt
set RC=%errorlevel%
type verify\result_v8math_msvc_x64.txt
exit /b %RC%
