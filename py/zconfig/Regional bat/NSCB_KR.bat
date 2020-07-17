@ECHO OFF
:TOP_INIT
set "prog_dir=%~dp0"
set "bat_name=%~n0"
set "ofile_name=%bat_name%_options.cmd"
Title NSC_Builder v0.88 -- Profile: %ofile_name% -- by JulesOnTheRoad
set "list_folder=%prog_dir%lists"
::-----------------------------------------------------
::이 옵션을 다른 옵션 파일과 연결되도록 편집하십시오.
::-----------------------------------------------------
set "op_file=%~dp0zconfig\%ofile_name%"

::-----------------------------------------------------
::옵션 파일로부터 복사 옵션
::-----------------------------------------------------
setlocal
if exist "%op_file%" call "%op_file%"
endlocal & (
REM VARIABLES
set "safe_var=%safe_var%"
set "vrepack=%vrepack%"
set "vrename=%vrename%"
set "fi_rep=%fi_rep%"
set "zip_restore=%zip_restore%"
set "manual_intro=%manual_intro%"
set "va_exit=%va_exit%"
set "skipRSVprompt=%skipRSVprompt%"
set "oforg=%oforg%"
set "NSBMODE=%NSBMODE%"
set "romaji=%romaji%"
REM set "trn_skip=%trn_skip%"
REM set "updx_skip=%updx_skip%"
REM set "ngx_skip=%ngx_skip%"

REM Copy function
set "pycommand=%pycommand%"
set "buffer=%buffer%"
set "nf_cleaner=%nf_cleaner%"
set "patchRSV=%patchRSV%"
set "vkey=%vkey%"
set "capRSV=%capRSV%"
set "fatype=%fatype%"
set "fexport=%fexport%"
set "skdelta=%skdelta%"
REM PROGRAMS
set "nut=%nut%"
set "xci_lib=%xci_lib%"
set "nsp_lib=%nsp_lib%"
set "zip=%zip%"
set "hacbuild=%hacbuild%"
set "listmanager=%listmanager%"
set "batconfig=%batconfig%"
set "batdepend=%batdepend%"
set "infobat=%infobat%"
REM FILES
set "uinput=%uinput%"
set "dec_keys=%dec_keys%"
REM FOLDERS
set "w_folder=%~dp0%w_folder%"
set "fold_output=%fold_output%"
set "zip_fold=%~dp0%zip_fold%"
)
::-----------------------------------------------------
::절대 경로 설정
::-----------------------------------------------------
::전체 경로 프로그램하기
if exist "%~dp0%nut%" set "nut=%~dp0%nut%"
if exist "%~dp0%xci_lib%"  set "xci_lib=%~dp0%xci_lib%"
if exist "%~dp0%nsp_lib%"  set "nsp_lib=%~dp0%nsp_lib%"
if exist "%~dp0%zip%"  set "zip=%~dp0%zip%"

if exist "%~dp0%hacbuild%"  set "hacbuild=%~dp0%hacbuild%"
if exist "%~dp0%listmanager%"  set "listmanager=%~dp0%listmanager%"
if exist "%~dp0%batconfig%"  set "batconfig=%~dp0%batconfig%"
if exist "%~dp0%batdepend%"  set "batdepend=%~dp0%batdepend%"
if exist "%~dp0%infobat%"  set "infobat=%~dp0%infobat%"
::중요한 파일 전체 경로
if exist "%~dp0%uinput%"  set "uinput=%~dp0%uinput%"
if exist "%~dp0%dec_keys%"  set "dec_keys=%~dp0%dec_keys%"
::폴더 출력
CD /d "%~dp0"
if not exist "%fold_output%" MD "%fold_output%"
if not exist "%fold_output%" MD "%~dp0%fold_output%"
if exist "%~dp0%fold_output%"  set "fold_output=%~dp0%fold_output%"
::-----------------------------------------------------
::많은 검사
::-----------------------------------------------------
::옵션 파일 확인
if not exist "%op_file%" ( goto missing_things )
::프로그램 확인
if not exist "%nut%" ( goto missing_things )
if not exist "%xci_lib%" ( goto missing_things )
if not exist "%nsp_lib%" ( goto missing_things )
if not exist "%zip%" ( goto missing_things )

if not exist "%hacbuild%" ( goto missing_things )
if not exist "%listmanager%" ( goto missing_things )
if not exist "%batconfig%" ( goto missing_things )
if not exist "%infobat%" ( goto missing_things )
::중요한 파일 확인
if not exist "%dec_keys%" ( goto missing_things )
::-----------------------------------------------------
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1

::사용자가 폴더 또는 파일을 드래그하고 있는지 확인
if "%~1"=="" goto manual
if "%vrepack%" EQU "nodelta" goto aut_rebuild_nodeltas
if "%vrepack%" EQU "rebuild" goto aut_rebuild_nsp
dir "%~1\" >nul 2>nul
if not errorlevel 1 goto folder
if exist "%~1\" goto folder
goto file

:folder
if "%fi_rep%" EQU "multi" goto folder_mult_mode
if "%fi_rep%" EQU "baseid" goto folder_packbyid
goto folder_ind_mode

::자동 모드. 개별 리팩 처리 옵션.
:folder_ind_mode
rem if "%fatype%" EQU "-fat fat32" goto folder_ind_mode_fat32
call :program_logo
echo --------------------------------------
echo 자동 모드. 개별 재포장이 설정 됨
echo --------------------------------------
echo.
::*************
::NSP 파일 용
::*************
for /r "%~1" %%f in (*.nsp) do (
set "target=%%f"
if exist "%w_folder%" RD /s /q "%w_folder%" >NUL 2>&1

set "filename=%%~nf"
set "orinput=%%f"
set "showname=%orinput%"

MD "%w_folder%"
REM echo %safe_var%>safe.txt
call :squirrell

if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
REM setlocal enabledelayedexpansion
REM set vpack=!vrepack!
REM endlocal & ( set "vpack=!vrepack!" )

REM if "%trn_skip%" EQU "true" ( call :check_titlerights )
if "%vrename%" EQU "true" ( call :addtags_from_nsp )

if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%%f" )
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%%f" )
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%%f" )

if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
)

::XCI 파일 용
for /r "%~1" %%f in (*.xci) do (
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
set "filename=%%~nf"
set "orinput=%%f"
set "showname=%orinput%"

MD "%w_folder%"
call :getname
if "%vrename%" EQU "true" ( call :addtags_from_xci )

if "%vrepack%" EQU "nsp" (  %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%%f" )
if "%vrepack%" EQU "xci" (  %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%%f" )
if "%vrepack%" EQU "both" (  %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%%f" )

if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto aut_exit_choice

:folder_ind_mode_fat32
CD /d "%prog_dir%"
call :program_logo
echo --------------------------------------
echo 자동 모드. 개별 재포장이 설정 됨
echo --------------------------------------
echo.
::*************
::NSP 파일 용
::*************
for /r "%~1" %%f in (*.nsp) do (
set "target=%%f"
if exist "%w_folder%" RD /s /q "%w_folder%" >NUL 2>&1

MD "%w_folder%"
MD "%w_folder%\secure"

set "filename=%%~nf"
set "orinput=%%f"
set "showname=%orinput%"
call :processing_message
REM echo %safe_var%>safe.txt
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
REM setlocal enabledelayedexpansion
REM set vpack=!vrepack!
REM endlocal & ( set "vpack=!vrepack!" )

REM if "%trn_skip%" EQU "true" ( call :check_titlerights )
if "%vrename%" EQU "true" ( call :addtags_from_nsp )

if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
)

::XCI 파일 용
for /r "%~1" %%f in (*.xci) do (
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
set "filename=%%~nf"
set "orinput=%%f"
set "showname=%orinput%"
call :processing_message
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo -------------------------------------
echo xci에서 보안 파티션 추출하기
echo -------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
echo 완료
if "%vrename%" EQU "true" ( call :addtags_from_xci )
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
MD "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xc*"  "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto aut_exit_choice

::자동 모드. 멀티팩 처리 옵션..
:folder_mult_mode
rem if "%fatype%" EQU "-fat fat32" goto folder_mult_mode_fat32
call :program_logo
echo --------------------------------------
echo 자동 모드. 멀티-리패킹이 설정 됨
echo --------------------------------------
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
if exist "%prog_dir%mlist.txt" del "%prog_dir%mlist.txt" >NUL 2>&1

echo - 파일목록 생성
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%mlist.txt" -ff "%~1"
echo   완료

if "%vrepack%" EQU "nsp" echo ......................................
if "%vrepack%" EQU "nsp" echo NSP에 폴더 내용 리패키징
if "%vrepack%" EQU "nsp" echo ......................................
if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "nsp" echo.

if "%vrepack%" EQU "xci" echo ......................................
if "%vrepack%" EQU "xci" echo XCI에 폴더 내용 리패키징
if "%vrepack%" EQU "xci" echo ......................................
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "xci" echo.

if "%vrepack%" EQU "both" echo ......................................
if "%vrepack%" EQU "both" echo NSP에 폴더 내용 리패키징
if "%vrepack%" EQU "both" echo ......................................
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" echo.

if "%vrepack%" EQU "both" echo ......................................
if "%vrepack%" EQU "both" echo XCI에 폴더 내용 리패키징
if "%vrepack%" EQU "both" echo ......................................
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" echo.

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -tfile "%w_folder%\filename.txt" -ifo "%w_folder%\archfolder" -archive "%gefolder%" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
call :thumbup
goto aut_exit_choice

:folder_mult_mode_fat32
CD /d "%prog_dir%"
call :program_logo
echo --------------------------------------
echo 자동 모드. 멀티-리패키징이 설정 됨
echo --------------------------------------
echo.
set "filename=%~n1"
set "orinput=%~f1"
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
set "end_folder=%filename%"
set "filename=%filename%[multi]"
::NSP 파일 용
for /r "%~1" %%f in (*.nsp) do (
set "showname=%orinput%"
call :processing_message
::echo %safe_var%>safe.txt
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
if "%zip_restore%" EQU "true" ( set "ziptarget=%%f" )
if "%zip_restore%" EQU "true" ( call :makezip )
)

::XCI 파일 용
for /r "%~1" %%f in (*.xci) do (
echo ------------------------------------
echo xci에서 보안 파티션 추출하기
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%%f"
echo 완료
)
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto aut_exit_choice

:folder_packbyid
rem if "%fatype%" EQU "-fat fat32" goto folder_mult_mode_fat32
call :program_logo
echo --------------------------------------
echo 자동 모드. packing-by-id가 설정 됨
echo --------------------------------------
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
if exist "%prog_dir%mlist.txt" del "%prog_dir%mlist.txt" >NUL 2>&1
set "mlistfol=%list_folder%\a_multi"
if not exist "%list_folder%" MD "%list_folder%" >NUL 2>&1
if not exist "%mlistfol%" MD "%mlistfol%" >NUL 2>&1

echo - 파일목록 생성
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%mlist.txt" -ff "%~1"
echo   완료
echo - 파일목록 나누기
%pycommand% "%nut%" -splid "%mlistfol%" -tfile "%prog_dir%mlist.txt"
if "%vrepack%" EQU "nsp" set "vrepack=cnsp"
if "%vrepack%" EQU "both" set "vrepack=cboth"
goto m_process_jobs2

:aut_rebuild_nodeltas
call :program_logo
echo --------------------------------------
echo 자동 모드. 델타 없이 리빌드
echo --------------------------------------
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
if exist "%prog_dir%list.txt" del "%prog_dir%list.txt" >NUL 2>&1
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%list.txt" -ff "%~1"
echo   완료
goto s_KeyChange_skip

:aut_rebuild_nsp
call :program_logo
echo --------------------------------------
echo 자동 모드. nsp를 cnmt 오더로 리빌드
echo --------------------------------------
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
if exist "%prog_dir%list.txt" del "%prog_dir%list.txt" >NUL 2>&1
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%list.txt" -ff "%~1"
echo   완료
goto s_KeyChange_skip

:file
call :program_logo
if "%~x1"==".nsp" ( goto nsp )
if "%~x1"==".xci" ( goto xci )
if "%~x1"==".*" ( goto other )
:other
echo 올바른 파일을 드래그하지 않았습니다. 프로그램은 xci 또는 nsp 파일 만 허용합니다.
echo 수동 모드로 리다이렉션됩니다.
pause
goto manual

:nsp
rem if "%fatype%" EQU "-fat fat32" goto file_nsp_fat32
set "orinput=%~f1"
set "filename=%~n1"
set "target=%~1"
set "showname=%orinput%"

if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell

if "%zip_restore%" EQU "true" ( set "ziptarget=%~1" )
if "%zip_restore%" EQU "true" ( call :makezip )
MD "%w_folder%"
call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp

if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%~1" )
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%~1" )
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%~1"  )

if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
goto aut_exit_choice

:file_nsp_fat32
CD /d "%prog_dir%"
set "orinput=%~f1"
set "filename=%~n1"
set "target=%~1"
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%~1"
if "%zip_restore%" EQU "true" ( set "ziptarget=%~1" )
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp
::echo "%vrepack%"
::echo "%nsp_lib%"
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
goto aut_exit_choice

:xci
rem if "%fatype%" EQU "-fat fat32" goto file_xci_fat32
set "filename=%~n1"
set "orinput=%~f1"
set "showname=%orinput%"

if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname

if "%vrename%" EQU "true" call :addtags_from_xci

if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%~1" )
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%~1" )
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%~1"  )

MD "%fold_output%\" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
goto aut_exit_choice

:file_xci_fat32
CD /d "%prog_dir%"
set "filename=%~n1"
set "orinput=%~f1"
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo ------------------------------------
echo xci에서 보안 파티션 추출하기
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%~1"
echo 완료
if "%vrename%" EQU "true" call :addtags_from_xci
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xc*"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
goto aut_exit_choice

:aut_exit_choice
if /i "%va_exit%"=="true" echo 프로그램은 지금 닫을 것입니다.
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo "0" 모드 선택 돌아가기
echo "1" 프로그램 종료
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto aut_exit_choice
exit
:manual
endlocal
cls
call :program_logo
echo ********************************
echo 수동 모드로 진입했습니다.
echo ********************************
if "%manual_intro%" EQU "indiv" ( goto normalmode )
if "%manual_intro%" EQU "multi" ( goto multimode )
if "%manual_intro%" EQU "split" ( goto SPLMODE )
::if "%manual_intro%" EQU "update" ( goto UPDMODE )
goto manual_Reentry

:manual_Reentry
cls
if "%NSBMODE%" EQU "legacy" call "%prog_dir%ztools\LEGACY.bat"
call :program_logo
ECHO .......................................................
echo "1" 개별적 파일 처리
echo "2" 멀티-팩 모드
echo "3" 멀티-콘텐츠 분할 모드
echo "4" 파일-정보 모드
echo "5" 데이터베이스 빌드 모드
echo "6" 어드밴스 모드
echo "0" 구성 모드
echo.
echo "L" 레거시 모드
echo .......................................................
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="1" goto normalmode
if /i "%bs%"=="2" goto multimode
if /i "%bs%"=="3" goto SPLMODE
if /i "%bs%"=="4" goto INFMODE
if /i "%bs%"=="5" goto DBMODE
if /i "%bs%"=="6" goto ADVmode
if /i "%bs%"=="L" goto LegacyMode
if /i "%bs%"=="0" goto OPT_CONFIG
goto manual_Reentry

:ADVmode
call "%prog_dir%ztools\ADV.bat"
goto manual_Reentry
:LegacyMode
call "%prog_dir%ztools\LEGACY.bat"
goto manual_Reentry
REM //////////////////////////////////////////////////
REM /////////////////////////////////////////////////
REM START OF MANUAL MODE. INDIVIDUAL PROCESSING
REM /////////////////////////////////////////////////
REM ////////////////////////////////////////////////
:normalmode
cls
call :program_logo
echo -----------------------------------------------
echo 개별적인 처리가 활성화되었습니다.
echo -----------------------------------------------
if exist "list.txt" goto prevlist
goto manual_INIT
:prevlist
set conta=0
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del list.txt )
endlocal
if not exist "list.txt" goto manual_INIT
ECHO .......................................................
ECHO 이전 목록이 발견되었습니다. 무엇을 하고 싶습니까?
:prevlist0
ECHO .......................................................
echo "1" 이전 목록에서 자동 시작 처리
echo "2" 목록을 지우고 새 목록 작성
echo "3" 이전 목록 작성을 계속
echo .......................................................
echo 참고: 3을 누르면 파일 처리를 시작하기 전에 이전 목록이
echo 표시되며 목록에서 항목을 추가 및 삭제할 수 있습니다.
echo
echo.
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="3" goto showlist
if /i "%bs%"=="2" goto delist
if /i "%bs%"=="1" goto start_cleaning
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo 나쁜 선택
goto prevlist0
:delist
del list.txt
cls
call :program_logo
echo -----------------------------------------------
echo 개별적인 처리가 활성화되었습니다.
echo -----------------------------------------------
echo ..................................
echo 새 목록을 시작하기로 결정했습니다.
echo ..................................
:manual_INIT
endlocal
ECHO ***********************************************
echo 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ***********************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto manual_Reentry
goto checkagain
echo.
:checkagain
echo 무엇을 하고 싶습니까?
echo ................................................................................
echo "다른 파일 또는 폴더를 드래그하고 목록에 항목을 추가하려면 ENTER 키를 누릅니다."
echo.
echo "1" 프로세스 시작
echo "e" 종료
echo "i" 처리 할 파일 목록 보기
echo "r" 일부 파일을 제거 (하단에서부터 계산)
echo "z" 전체 목록을 제거
echo ................................................................................
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%list.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" goto start_cleaning
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto showlist
if /i "%eval%"=="r" goto r_files
if /i "%eval%"=="z" del list.txt

goto checkagain

:r_files
set /p bs="(하단에서) 삭제할 파일 수를 입력하십시오: "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:update_list1
if !pos1! GTR !pos2! ( goto :update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :update_list1
:update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<list.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>list.txt.new
endlocal
move /y "list.txt.new" "list.txt" >nul
endlocal

:showlist
cls
call :program_logo
echo -------------------------------------------------
echo 개별적인 처리가 활성화되었습니다.
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                 처리 할 파일
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (list.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo 처리 할 !conta! 파일을 추가했습니다.
echo .................................................
endlocal

goto checkagain

:s_cl_wrongchoice
echo 틀린 선택
echo ............
:start_cleaning
echo *******************************************************
echo 선택한 파일을 처리한 후 수행할 작업을 선택하십시오.
echo *******************************************************
echo "1" nsp로 목록을 리팩
echo "2" xci로 목록을 리팩
echo "3" nsp와 xci로 목록을 리팩
echo.
echo 특수 옵션:
echo "4" nsp 파일에서 델타를 삭제
echo "5" xci 또는 nsp 파일의 이름 변경
echo "6" xci supertrimmer
echo "7" nsp를 cnmt 오더로 리빌드
echo "8" 파일을 확인
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if /i "%bs%"=="4" set "vrepack=nodelta"
if /i "%bs%"=="4" goto s_KeyChange_skip
if /i "%bs%"=="5" set "vrepack=renamef"
if /i "%bs%"=="5" goto rename
if /i "%bs%"=="6" set "vrepack=xci_supertrimmer"
if /i "%bs%"=="6" goto s_KeyChange_skip
if /i "%bs%"=="7" set "vrepack=rebuild"
if /i "%bs%"=="7" goto s_KeyChange_skip
if /i "%bs%"=="8" set "vrepack=verify"
if /i "%bs%"=="8" goto s_vertype
if %vrepack%=="none" goto s_cl_wrongchoice
:s_RSV_wrongchoice
if /i "%skipRSVprompt%"=="true" set "patchRSV=-pv false"
if /i "%skipRSVprompt%"=="true" goto s_KeyChange_skip
echo *******************************************************
echo 필수 시스템 버전을 패치하고 싶습니까?
echo *******************************************************
echo 패치를 선택하면 nca 암호화와 일치하도록 설정되므로
echo 필요할 경우 시스템을 업데이트하라는 메시지만 표시
echo 됩니다.
echo.
echo "0" 필수 시스템 버전을 패치하지 않음
echo "1" 필요한 시스템 버전 "패치"
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "patchRSV=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto s_RSV_wrongchoice
if /i "%bs%"=="0" goto s_KeyChange_skip

:s_KeyChange_wrongchoice
echo *******************************************************
echo 최대 키 생성\RSV 허용 설정
echo *******************************************************
echo 선택한 키 생성에 따라 RSG는 해당 키 생성 범위로 낮춰지며
echo 읽기 키 생성 값이 프로그램에 지정된 값보다 큰 경우에 발생
echo 합니다.
echo
echo 이 작업은 항상 펌웨어 요구를 낮추기 위해 노력하지 않습니다.
echo.
echo "f" 키 생성을 변경하지 않음
echo "0" 최상위 키 생성을 0으로 변경 (FW 1.0)
echo "1" 최상위 키 생성을 1로 변경 (FW 2.0-2.3)
echo "2" 최상위 키 생성을 2로 변경 (FW 3.0)
echo "3" 최상위 키 생성을 3으로 변경 (FW 3.0.1-3.02)
echo "4" 최상위 키 생성을 4로 변경 (FW 4.0.0-4.1.0)
echo "5" 최상위 키 생성을 5로 변경 (FW 5.0.0-5.1.0)
echo "6" 최상위 키 생성을 6으로 변경 (FW 6.0.0-6.1.0)
echo "7" 최상위 키 생성을 7로 변경 (FW 6.2.0)
echo "8" 최상위 키 생성을 8로 변경 (FW 7.0.0-8.0.1)
echo "9" 최상위 키 생성을 9로 변경 (FW 8.1.0)
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "vkey=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="f" set "vkey=-kp false"
if /i "%bs%"=="0" set "vkey=-kp 0"
if /i "%bs%"=="0" set "capRSV=--RSVcap 0"
if /i "%bs%"=="1" set "vkey=-kp 1"
if /i "%bs%"=="1" set "capRSV=--RSVcap 65796"
if /i "%bs%"=="2" set "vkey=-kp 2"
if /i "%bs%"=="2" set "capRSV=--RSVcap 201327002"
if /i "%bs%"=="3" set "vkey=-kp 3"
if /i "%bs%"=="3" set "capRSV=--RSVcap 201392178"
if /i "%bs%"=="4" set "vkey=-kp 4"
if /i "%bs%"=="4" set "capRSV=--RSVcap 268435656"
if /i "%bs%"=="5" set "vkey=-kp 5"
if /i "%bs%"=="5" set "capRSV=--RSVcap 335544750"
if /i "%bs%"=="6" set "vkey=-kp 6"
if /i "%bs%"=="6" set "capRSV=--RSVcap 402653494"
if /i "%bs%"=="7" set "vkey=-kp 7"
if /i "%bs%"=="7" set "capRSV=--RSVcap 404750336"
if /i "%bs%"=="8" set "vkey=-kp 8"
if /i "%bs%"=="8" set "capRSV=--RSVcap 469762048"
if /i "%bs%"=="9" set "vkey=-kp 9"
if /i "%bs%"=="9" set "capRSV=--RSVcap 537919488"
if /i "%vkey%"=="none" echo 틀린 선택
if /i "%vkey%"=="none" goto s_KeyChange_wrongchoice
goto s_KeyChange_skip

:s_vertype
echo *******************************************************
echo 검증 유형
echo *******************************************************
echo 이것은 검증의 수준을 선택합니다.
echo 암호 해독  - 읽을 수 있는 파일, 티켓이 정확함
echo              파일이 없습니다.
echo 서명       - 닌텐도 Sig1에 대한 검증의 헤더
echo              NSCB 수정에 대한 원래 헤더를 계산
echo 해쉬       - 파일의 현재 및 원래 해시를 확인하고
echo              파일 이름과 일치
echo.
echo 참고: 파일 스트림 방법을 통해 원격 서비스의 파일을 읽는 경우
echo 암호 해독 또는 서명을 사용하는 것이 좋습니다.
echo.
echo "1" 암호 해독 검증 사용 (빠름)
echo "2" 암호 해독 + 서명 확인 (빠름)
echo "3" 암호 해독 + 서명 + 해시 검증 (느림)
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "verif=none"
if /i "%bs%"=="b" goto checkagain
if /i "%bs%"=="1" set "verif=lv1"
if /i "%bs%"=="2" set "verif=lv2"
if /i "%bs%"=="3" set "verif=lv3"
if /i "%verif%"=="none" echo 틀린 선택
if /i "%verif%"=="none" echo.
if /i "%verif%"=="none" goto s_vertype

:s_KeyChange_skip
cls
call :program_logo
for /f "tokens=*" %%f in (list.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
set "ziptarget=%%f"

if "%%~nxf"=="%%~nf.nsp" call :nsp_manual
if "%%~nxf"=="%%~nf.xci" call :xci_manual
%pycommand% "%nut%" --strip_lines "%prog_dir%list.txt"
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto s_exit_choice

:rename
:s_rename_wrongchoice1
echo.
echo *******************************************************
echo 이름 바꾸기의 유형
echo *******************************************************
echo 일반 모드:
echo "1" 항상 이름 바꾸기
echo "2" [TITLEID]가 있는 경우 이름을 바꾸지 않음
echo "3" [TITLEID]가 계산된 것과 동일하면 이름을 변경하지 않음
echo "4" ID 만 추가
echo "5" ADD ID + 태크 추가, [까지 이름 유지
echo.
echo 지우기 태그:
echo "6" 파일 이름에서 [] 태그 삭제
echo "7" 파일 이름에서 () 태그 삭제
echo "8" 파일 이름에서 []와 () 태그 삭제
echo "9" 처음 [에서 타이틀 삭제
echo "10" 처음 (에서 타이틀 삭제
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "0"을 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "renmode=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="1" set "renmode=force"
if /i "%bs%"=="1" set "oaid=false"
if /i "%bs%"=="2" set "renmode=skip_corr_tid"
if /i "%bs%"=="2" set "oaid=false"
if /i "%bs%"=="3" set "renmode=skip_if_tid"
if /i "%bs%"=="3" set "oaid=false"
if /i "%bs%"=="4" set "renmode=skip_corr_tid"
if /i "%bs%"=="4" set "oaid=true"
if /i "%bs%"=="5" set "renmode=skip_corr_tid"
if /i "%bs%"=="5" set "oaid=idtag"

if /i "%bs%"=="6" set "tagtype=[]"
if /i "%bs%"=="6" goto filecleantags
if /i "%bs%"=="7" set "tagtype=()"
if /i "%bs%"=="7" goto filecleantags
if /i "%bs%"=="8" set "tagtype=false"
if /i "%bs%"=="8" goto filecleantags
if /i "%bs%"=="9" set "tagtype=["
if /i "%bs%"=="9" goto filecleantags
if /i "%bs%"=="10" set "tagtype=("
if /i "%bs%"=="10" goto filecleantags

if /i "%renmode%"=="none" echo 틀린 선택
if /i "%renmode%"=="none" goto s_rename_wrongchoice1
echo.
:s_rename_wrongchoice2
echo *******************************************************
echo 버전 번호 추가
echo *******************************************************
echo 파일 이름에 콘텐츠 버전 번호를 추가합니다.
echo.
echo "1" 버전 번호 추가
echo "2" 버전 번호 추가 안함
echo "3" VERSION=0인 경우 xci에 버전 추가 안함
echo.
ECHO *********************************************
echo 또는 "b" 이름 바꾸기 유형
echo 또는 "0" 목록 옵션으로 돌아가기
ECHO *********************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "nover=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice1
if /i "%bs%"=="1" set "nover=false"
if /i "%bs%"=="2" set "nover=true"
if /i "%bs%"=="3" set "nover=xci_no_v0"
if /i "%nover%"=="none" echo WRONG CHOICE
if /i "%nover%"=="none" goto s_rename_wrongchoice2
echo.
:s_rename_wrongchoice3
echo *******************************************************
echo 언어 문자열 추가
echo *******************************************************
echo 게임 및 업데이트 용 언어 태그 추가
echo.
echo "1" 언어 문자열 추가 안함
echo "2" 언어 문자열 추가
echo.
echo 참고: dlc에서 언어를 읽을 수 없으므로 이 옵션은 영향을
echo 미치지 않습니다.
echo.
ECHO *********************************************
echo 또는 "b" 버전 번호 추가
echo 또는 "0" 목록 옵션으로 돌아가기
ECHO *********************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "addlangue=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice2
if /i "%bs%"=="1" set "addlangue=false"
if /i "%bs%"=="2" set "addlangue=true"
if /i "%addlangue%"=="none" echo 틀린 선택
if /i "%addlangue%"=="none" goto s_rename_wrongchoice3
echo.
:s_rename_wrongchoice4
echo *******************************************************
echo DLC 이름 유지
echo *******************************************************
echo 태그없이 이름을 유지하거나 DLC NUMBER X를 이름으로 사용.
echo 참고: 이 방법은 dlc 이름을 파일에서 읽을 수 없으므로 dlc
echo 번호에서만 읽을 수 있습니다.
echo.
echo "1" 기본이름 유지
echo "2" DLC 번호 이름 바꾸기
echo "3" 기본이름 유지와 태그와 같이 DLC 번호 추가
echo.
ECHO *********************************************
echo 또는 "b" DLC 이름 추가
echo 또는 "0" 목록 옵션으로 돌아가기
ECHO *********************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "dlcrname=none"
if /i "%bs%"=="0" goto checkagain
if /i "%bs%"=="b" goto s_rename_wrongchoice3
if /i "%bs%"=="1" set "dlcrname=false"
if /i "%bs%"=="2" set "dlcrname=true"
if /i "%bs%"=="3" set "dlcrname=tag"
if /i "%dlcrname%"=="none" echo 틀린 선택
if /i "%dlcrname%"=="none" goto s_rename_wrongchoice4
echo.
cls
call :program_logo
for /f "tokens=*" %%f in (list.txt) do (
%pycommand% "%nut%" -renf "single" -tfile "%prog_dir%list.txt" -t xci nsp -renm %renmode% -nover %nover% -oaid %oaid% -addl %addlangue% -dlcrn %dlcrname%
%pycommand% "%nut%" --strip_lines "%prog_dir%list.txt"
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto s_exit_choice

:filecleantags
cls
call :program_logo
for /f "tokens=*" %%f in (list.txt) do (
%pycommand% "%nut%" -cltg "single" -tfile "%prog_dir%list.txt" -t xci nsp -tgtype "%tagtype%"
%pycommand% "%nut%" --strip_lines "%prog_dir%list.txt"
call :contador_NF
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto s_exit_choice

:s_exit_choice
if exist list.txt del list.txt
if /i "%va_exit%"=="true" echo 프로그램은 지금 닫을 것입니다
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo "0" 모드 선택 돌아가기
echo "1" 프로그램 종료
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto s_exit_choice

:nsp_manual
rem if "%fatype%" EQU "-fat fat32" goto nsp_manual_fat32
rem set "filename=%name%"
rem set "showname=%orinput%"
if "%zip_restore%" EQU "true" ( call :makezip )
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
call :squirrell

if "%vrename%" EQU "true" call :addtags_from_nsp

if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "nodelta" ( %pycommand% "%nut%" %buffer% --xml_gen "true" -o "%w_folder%" -tfile "%prog_dir%list.txt" --erase_deltas "")
if "%vrepack%" EQU "rebuild" ( %pycommand% "%nut%" %buffer% %skdelta% --xml_gen "true" -o "%w_folder%" -tfile "%prog_dir%list.txt" --rebuild_nsp "")
if "%vrepack%" EQU "verify" ( %pycommand% "%nut%" %buffer% -vt "%verif%" -tfile "%prog_dir%list.txt" -v "")
if "%vrepack%" EQU "verify" ( goto end_nsp_manual )

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
call :delay
goto end_nsp_manual

:nsp_manual_fat32
CD /d "%prog_dir%"
set "filename=%name%"
set "showname=%orinput%"
call :processing_message

if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
call :squirrell

if "%vrepack%" EQU "zip" ( goto nsp_just_zip )

%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"

:nsp_just_zip
if "%zip_restore%" EQU "true" ( call :makezip )
call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "repack" "%w_folder%" "%%f")
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" "%%f")
setlocal enabledelayedexpansion
if "%zip_restore%" EQU "true" ( goto :nsp_just_zip2 )
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
:nsp_just_zip2
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
call :delay
goto end_nsp_manual

:end_nsp_manual
exit /B

:xci_manual
rem if "%fatype%" EQU "-fat fat32" goto xci_manual_fat32
::FOR XCI FILES
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"

set "filename=%name%"
set "showname=%orinput%"

if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "nsp" -dc "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "xci" -dc "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -o "%w_folder%" -t "both" -dc "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "xci_supertrimmer" ( %pycommand% "%nut%" %buffer% -o "%w_folder%" -xci_st "%orinput%" -tfile "%prog_dir%list.txt")
if "%vrepack%" EQU "verify" ( %pycommand% "%nut%" %buffer% -vt "%verif%" -tfile "%prog_dir%list.txt" -v "")
if "%vrepack%" EQU "verify" ( goto end_xci_manual )

if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1

move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\%filename%.nsp" )

RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
call :delay
goto end_xci_manual

:xci_manual_fat32
CD /d "%prog_dir%"
::FOR XCI FILES
cls
if "%vrepack%" EQU "zip" ( goto end_xci_manual )
set "filename=%name%"
call :program_logo
set "showname=%orinput%"
call :processing_message
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
MD "%w_folder%\secure"
call :getname
echo ------------------------------------
echo xci에서 보안 파티션 추출하기
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo 완료
if "%vrename%" EQU "true" call :addtags_from_xci
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xci"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.xc*"  "%fold_output%\!end_folder!" >NUL 2>&1
move  "%w_folder%\*.nsp"  "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
echo 완료
call :thumbup
call :delay
goto end_xci_manual

:end_xci_manual
exit /B

:contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (list.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo 여전히 처리할 !conta! 파일
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:: MULTI-MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////

:multimode
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1
if exist "%list_folder%\a_multi" RD /S /Q "%list_folder%\a_multi" >NUL 2>&1
cls
call :program_logo
echo -----------------------------------------------
echo 멀티 리팩 모드 활성화되었습니다
echo -----------------------------------------------
if exist "mlist.txt" del "mlist.txt"
:multi_manual_INIT
endlocal
set skip_list_split="false"
set "mlistfol=%list_folder%\m_multi"
echo 목록을 만들려면 파일이나 폴더를 드래그하십시오.
echo 참고: 각 dile\folder를 드래그 한 후에는 Enter 키를 누르십시오.
echo.
ECHO ***********************************************
echo "1" 이전에 저장된 작업을 처리
echo "0" 모드 선택 메뉴 돌아가기
ECHO ***********************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%mlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal
if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" set skip_list_split="true"
if /i "%eval%"=="1" goto multi_start_cleaning
goto multi_checkagain
echo.
:multi_checkagain
set "mlistfol=%list_folder%\a_multi"
echo 무엇을 하고 싶습니까?
echo ................................................................................
echo "다른 파일 또는 폴더를 드래그하고 목록에 항목을 추가하려면 ENTER 키를 누릅니다."
echo.
echo "1" 현재 목록 처리를 시작
echo "2" 저장된 목록에 추가하고 처리
echo "3" 나중에 저장할 수 있도록 목록 저장
REM echo Input "2" to set a custom logo from a nsp/nca
echo.
echo "e" 종료
echo "i" 처리할 파일 목록 보기
echo "r" 일부 파일 삭제 (하단에서부터 계산)
echo "z" 전체 목록 삭제
echo ................................................................................
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%mlist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" set "mlistfol=%list_folder%\a_multi"
if /i "%eval%"=="1" goto multi_start_cleaning
if /i "%eval%"=="2" set "mlistfol=%list_folder%\m_multi"
if /i "%eval%"=="2" goto multi_start_cleaning
if /i "%eval%"=="3" set "mlistfol=%list_folder%\m_multi"
if /i "%eval%"=="3" goto multi_saved_for_later
REM if /i "%eval%"=="2" goto multi_set_clogo
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto multi_showlist
if /i "%eval%"=="r" goto multi_r_files
if /i "%eval%"=="z" del mlist.txt

goto multi_checkagain

:multi_saved_for_later
if not exist "%list_folder%" MD "%list_folder%" >NUL 2>&1
if not exist "%mlistfol%" MD "%mlistfol%" >NUL 2>&1
echo 다른 시간에 작업 목록 저장
echo ......................................................................
echo "1" MERGE 작업으로 목록을 저장 (단일 다중 파일 목록)
echo "2" 파일의 baseid에 의해 여러 작업으로 목록을 저장
echo.
ECHO *******************************************
echo "b" 목록 작성을 계속
echo "0" 선택 메뉴로 돌아가기
ECHO *******************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto multi_saved_for_later1
if /i "%bs%"=="2" ( %pycommand% "%nut%" -splid "%mlistfol%" -tfile "%prog_dir%mlist.txt" )
if /i "%bs%"=="2" del "%prog_dir%mlist.txt"
if /i "%bs%"=="2" goto multi_saved_for_later2
echo 틀린 선택!!
goto multi_saved_for_later
:multi_saved_for_later1
echo.
echo 작업의 이름을 선택하십시오
echo ......................................................................
echo 목록은 목록 폴더에서 선택한 이름으로 저장됩니다.
echo (경로는 "프로그램의 폴더\list\m_multi"입니다)
echo.
set /p lname="목록 작업의 입력 이름: "
set lname=%lname:"=%
move /y "%prog_dir%mlist.txt" "%mlistfol%\%lname%.txt" >nul
echo.
echo 작업이 저장되었습니다!!!
:multi_saved_for_later2
echo.
echo "0" 모드 선택 돌아가기
echo "1" 다른 작업 생성
echo "2" 프로그램 종료
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" echo.
if /i "%bs%"=="1" echo CREATE ANOTHER JOB
if /i "%bs%"=="1" goto multi_manual_INIT
if /i "%bs%"=="1" goto salida
goto multi_saved_for_later2

:multi_r_files
set /p bs="(하단에서) 삭제할 파일 수를 입력하십시오: "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:multi_update_list1
if !pos1! GTR !pos2! ( goto :multi_update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :multi_update_list1
:multi_update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<mlist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>mlist.txt.new
endlocal
move /y "mlist.txt.new" "mlist.txt" >nul
endlocal

:multi_showlist
cls
call :program_logo
echo -------------------------------------------------
echo 멀티 리 팩 모드 활성화되었습니다
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                   처리할 파일
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (mlist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo 처리할 !conta! 파일을 추가했습니다
echo .................................................
endlocal

goto multi_checkagain

:m_cl_wrongchoice
echo 틀린 선택
echo ............
:multi_start_cleaning
echo *******************************************************
echo 선택한 파일을 처리한 후 수행할 작업을 선택하십시오.
echo *******************************************************
echo 표준 비밀 옵션:
echo "1" 티켓없이 NSP로 목록 리팩
echo "2" XCI로 목록 리팩
echo "3" T-NSP 및 XCI로 목록 리팩
echo.
echo 특수 옵션:
echo "4" 수정되지 않은 eshop nca 파일과 함꼐하는 NSP
echo "5" NSP-U와 XCI로 리팩 목록
echo.
ECHO *************************************************
echo 또는 옵션 목록으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="1" set "vrepack=cnsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=cboth"

if /i "%bs%"=="4" set "vrepack=nsp"
if /i "%bs%"=="4" set "skipRSVprompt=true"
if /i "%bs%"=="5" set "vrepack=both"

if %vrepack%=="none" goto m_cl_wrongchoice
:m_RSV_wrongchoice
if /i "%skipRSVprompt%"=="true" set "patchRSV=-pv false"
if /i "%skipRSVprompt%"=="true" set "vkey=-kp false"
if /i "%skipRSVprompt%"=="true" goto m_KeyChange_skip
echo *******************************************************
echo 필수 시스템 버전을 패치하고 싶습니까?
echo *******************************************************
echo 패치를 선택하면 nca 암호와 일치하도록 설정되므로
echo 필요할 경우 시스템을 업데이트하라는 메시지만 표시
echo 됩니다.
echo.
echo "0" 필수 시스템 버전을 패치하지 않음
echo "1" 필요한 시스템 버전 "패치"
echo.
ECHO *************************************************
echo 또는 옵션 목록으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set patchRSV=none
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="0" set "patchRSV=-pv false"
if /i "%bs%"=="0" set "vkey=-kp false"
if /i "%bs%"=="1" set "patchRSV=-pv true"
if /i "%patchRSV%"=="none" echo WRONG CHOICE
if /i "%patchRSV%"=="none" goto m_RSV_wrongchoice
if /i "%bs%"=="0" goto m_KeyChange_skip

:m_KeyChange_wrongchoice
echo *******************************************************
echo 최대 키 생성\RSV 허용 설정
echo *******************************************************
echo 선택한 키 생성에 따라 RSG는 해당 키 생성 범위로 낮춰지며
echo 읽기 키 생성 값이 프로그램에 지정된 값보다 큰 경우에 발생
echo 합니다.
echo
echo 이 작업은 항상 펌웨어 요구를 낮추기 위해 노력하지 않습니다.
echo.
echo "f" 키 생성을 변경하지 않음
echo "0" 최상위 키 생성을 0으로 변경 (FW 1.0)
echo "1" 최상위 키 생성을 1로 변경 (FW 2.0-2.3)
echo "2" 최상위 키 생성을 2로 변경 (FW 3.0)
echo "3" 최상위 키 생성을 3으로 변경 (FW 3.0.1-3.02)
echo "4" 최상위 키 생성을 4으로 변경 (FW 4.0.0-4.1.0)
echo "5" 최상위 키 생성을 5로 변경 (FW 5.0.0-5.1.0)
echo "6" 최상위 키 생성을 6으로 변경 (FW 6.0.0-6.1.0)
echo "7" 최상위 키 생성을 7로 변경 (FW 6.2.0)
echo "8" 최상위 키 생성을 8로 변경 (FW 7.0.0-8.0.1)
echo "9" 최상위 키 생성을 9로 변경 (FW 8.1.0)
echo.
ECHO *************************************************
echo 또는 옵션 목록으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set "vkey=none"
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="f" set "vkey=-kp false"
if /i "%bs%"=="0" set "vkey=-kp 0"
if /i "%bs%"=="0" set "capRSV=--RSVcap 0"
if /i "%bs%"=="1" set "vkey=-kp 1"
if /i "%bs%"=="1" set "capRSV=--RSVcap 65796"
if /i "%bs%"=="2" set "vkey=-kp 2"
if /i "%bs%"=="2" set "capRSV=--RSVcap 201327002"
if /i "%bs%"=="3" set "vkey=-kp 3"
if /i "%bs%"=="3" set "capRSV=--RSVcap 201392178"
if /i "%bs%"=="4" set "vkey=-kp 4"
if /i "%bs%"=="4" set "capRSV=--RSVcap 268435656"
if /i "%bs%"=="5" set "vkey=-kp 5"
if /i "%bs%"=="5" set "capRSV=--RSVcap 335544750"
if /i "%bs%"=="6" set "vkey=-kp 6"
if /i "%bs%"=="6" set "capRSV=--RSVcap 402653494"
if /i "%bs%"=="7" set "vkey=-kp 7"
if /i "%bs%"=="7" set "capRSV=--RSVcap 404750336"
if /i "%bs%"=="8" set "vkey=-kp 8"
if /i "%bs%"=="8" set "capRSV=--RSVcap 469762048"
if /i "%bs%"=="9" set "vkey=-kp 9"
if /i "%bs%"=="9" set "capRSV=--RSVcap 537919488"
if /i "%vkey%"=="none" echo WRONG CHOICE
if /i "%vkey%"=="none" goto m_KeyChange_wrongchoice

:m_KeyChange_skip
if not exist "%list_folder%" MD "%list_folder%" >NUL 2>&1
if not exist "%mlistfol%" MD "%mlistfol%" >NUL 2>&1
if %skip_list_split% EQU "true" goto m_process_jobs
echo *******************************************************
echo 어떻게 파일 처리 방법을 하기 원합니까?
echo *******************************************************
echo 분리 된 기본 ID 모드는 각 게임에 해당하는 콘텐츠를 식별
echo 하고 동일한 목록 파일에서 여러 개의 멀티-xci 또는 멀티
echo nsp를 만들 수 있습니다.
echo.
echo "1" 모든 파일을 단일 파일에 병합
echo "2" baseid로 다중 파일에 분리
echo.
ECHO *************************************************
echo 또는 옵션 목록으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="b" goto multi_checkagain
if /i "%bs%"=="1" move /y "%prog_dir%mlist.txt" "%mlistfol%\mlist.txt" >nul
if /i "%bs%"=="1" goto m_process_jobs
if /i "%bs%"=="2" goto m_split_merge
goto m_KeyChange_skip

:m_split_merge
cls
call :program_logo
%pycommand% "%nut%" -splid "%mlistfol%" -tfile "%prog_dir%mlist.txt"
goto m_process_jobs2
:m_process_jobs
cls
:m_process_jobs2
dir "%mlistfol%\*.txt" /b  > "%prog_dir%mlist.txt"
rem if "%fatype%" EQU "-fat fat32" goto m_process_jobs_fat32

for /f "tokens=*" %%f in (mlist.txt) do (
set "listname=%%f"
if "%vrepack%" EQU "cnsp" call :program_logo
if "%vrepack%" EQU "cnsp" call :m_split_merge_list_name
if "%vrepack%" EQU "cnsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "xci" call :program_logo
if "%vrepack%" EQU "xci" call :m_split_merge_list_name
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "nsp" call :program_logo
if "%vrepack%" EQU "nsp" call :m_split_merge_list_name
if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "cboth" call :program_logo
if "%vrepack%" EQU "cboth" call :m_split_merge_list_name
if "%vrepack%" EQU "cboth" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "cboth" call :program_logo
if "%vrepack%" EQU "cboth" call :m_split_merge_list_name
if "%vrepack%" EQU "cboth" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "both" call :program_logo
if "%vrepack%" EQU "both" call :m_split_merge_list_name
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" call :program_logo
if "%vrepack%" EQU "both" call :m_split_merge_list_name
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%mlistfol%\%%f" -roma %romaji% -dmul "calculate" )
%pycommand% "%nut%" --strip_lines "%prog_dir%mlist.txt"
if exist "%mlistfol%\%%f" del "%mlistfol%\%%f"
call :multi_contador_NF
)

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%"
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -tfile "%w_folder%\filename.txt" -ifo "%w_folder%\archfolder" -archive "%gefolder%" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
if exist "%mlistfol%" RD /S /Q "%mlistfol%" >NUL 2>&1
if exist mlist.txt del mlist.txt
goto m_exit_choice

:m_process_jobs_fat32
CD /d "%prog_dir%"
set "finalname=tempname"
cls
call :program_logo
for /f "tokens=*" %%f in (mlist.txt) do (
set "listname=%%f"
set "list=%mlistfol%\%%f"
call :m_split_merge_list_name
call :m_process_jobs_fat32_2
%pycommand% "%nut%" --strip_lines "%prog_dir%mlist.txt"
if exist "%mlistfol%\%%f" del "%mlistfol%\%%f"
call :multi_contador_NF
)
goto m_exit_choice
:m_process_jobs_fat32_2
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
copy "%list%" "%w_folder%\list.txt" >NUL 2>&1
for /f "usebackq tokens=*" %%f in ("%w_folder%\list.txt") do (
echo %%f
set "name=%%~nf"
set "filename=tempname"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :multi_nsp_manual
if "%%~nxf"=="%%~nf.xci" call :multi_xci_manual
)
if exist "%w_folder%\list.txt" del "%w_folder%\list.txt"
if "%vrepack%" EQU "cnsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "cboth" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "cboth" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )
RD /S /Q "%w_folder%\secure" >NUL 2>&1
RD /S /Q "%w_folder%\normal" >NUL 2>&1
if exist "%w_folder%\archfolder" goto m_process_jobs_fat32_3
if exist "%w_folder%\*.xc*" goto m_process_jobs_fat32_4
if exist "%w_folder%\*.ns*" goto m_process_jobs_fat32_4
if exist "%w_folder%\tempname.*" goto m_process_jobs_fat32_4
:m_process_jobs_fat32_3
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\tempname.nsp" )
endlocal
dir "%fold_output%\tempname.*" /b  > "%w_folder%\templist.txt"
for /f "usebackq tokens=*" %%f in ("%w_folder%\templist.txt") do (
%pycommand% "%nut%" -roma %romaji% --renameftxt "%fold_output%\%%f" -tfile "%list%"
if exist "%w_folder%\templist.txt" del "%w_folder%\templist.txt"
)

if exist "%w_folder%\*.xc*" goto m_process_jobs_fat32_4
if exist "%w_folder%\*.ns*" goto m_process_jobs_fat32_4
RD /S /Q "%w_folder%" >NUL 2>&1
exit /B

:m_process_jobs_fat32_4
dir "%w_folder%\tempname.*" /b  > "%w_folder%\templist.txt"
for /f "usebackq tokens=*" %%f in ("%w_folder%\templist.txt") do (
%pycommand% "%nut%" -roma %romaji% --renameftxt "%w_folder%\%%f" -tfile "%list%"
)
setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%" >NUL 2>&1
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
exit /B

:m_split_merge_list_name
echo *******************************************************
echo %listname% 목록 처리
echo *******************************************************
exit /B

:m_normal_merge
rem if "%fatype%" EQU "-fat fat32" goto m_KeyChange_skip_fat32
REM For the current beta the filenames are calculted. This code remains commented for future reintegration
rem echo *******************************************************
rem echo ENTER FINAL FILENAME FOR THE OUTPUT FILE
rem echo *******************************************************
rem echo.
rem echo Or Input "b" to return to the option list
rem echo.
rem set /p bs="Please type the name without extension: "
rem set finalname=%bs:"=%
rem if /i "%finalname%"=="b" goto multi_checkagain

cls
if "%vrepack%" EQU "cnsp" call :program_logo
if "%vrepack%" EQU "cnsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "xci" call :program_logo
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "nsp" call :program_logo
if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "cboth" call :program_logo
if "%vrepack%" EQU "cboth" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "cboth" call :program_logo
if "%vrepack%" EQU "cboth" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t cnsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

if "%vrepack%" EQU "both" call :program_logo
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t nsp -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )
if "%vrepack%" EQU "both" call :program_logo
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% %fatype% %fexport% %skdelta% -t xci -o "%w_folder%" -tfile "%prog_dir%mlist.txt" -roma %romaji% -dmul "calculate" )

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -tfile "%w_folder%\filename.txt" -ifo "%w_folder%\archfolder" -archive "%gefolder%" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
goto m_exit_choice

:m_KeyChange_skip_fat32
CD /d "%prog_dir%"
echo *******************************************************
echo 출력 파일의 최종 파일 이름 입력
echo *******************************************************
echo.
echo 또는 옵션 목록으로 돌아가려면 "b"를 입력하십시오.
echo.
set /p bs="확장명없이 이름을 입력하십시오: "
set finalname=%bs:"=%
if /i "%finalname%"=="b" goto multi_checkagain

cls
call :program_logo
for /f "tokens=*" %%f in (mlist.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :multi_nsp_manual
if "%%~nxf"=="%%~nf.xci" call :multi_xci_manual
%pycommand% "%nut%" --strip_lines "%prog_dir%mlist.txt"
call :multi_contador_NF
)
set "filename=%finalname%"
set "end_folder=%finalname%"
set "filename=%finalname%[multi]"
::pause
if "%vrepack%" EQU "nsp" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "xci" ( call "%xci_lib%" "repack" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%nsp_lib%" "convert" "%w_folder%" )
if "%vrepack%" EQU "both" ( call "%xci_lib%" "repack" "%w_folder%" )

setlocal enabledelayedexpansion
if not exist "%fold_output%" MD "%fold_output%" >NUL 2>&1
set "gefolder=%fold_output%\!end_folder!"
if "%oforg%" EQU "inline" ( set "gefolder=%fold_output%" )
MD "%gefolder%" >NUL 2>&1
move "%w_folder%\*.xci" "%gefolder%" >NUL 2>&1
move  "%w_folder%\*.xc*" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.nsp" "%gefolder%" >NUL 2>&1
move "%w_folder%\*.ns*" "%gefolder%" >NUL 2>&1
if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%gefolder%\%filename%.nsp" )
endlocal
RD /S /Q "%w_folder%" >NUL 2>&1
goto m_exit_choice

:m_exit_choice
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
if exist mlist.txt del mlist.txt
if /i "%va_exit%"=="true" echo 프로그램은 지금 닫을 것입니다.
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo "0" 모드 선택 돌아가기
echo "1" 프로그램 종료
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto m_exit_choice


:multi_nsp_manual
set "showname=%orinput%"
call :processing_message
call :squirrell
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo 완료
call :thumbup
call :delay
exit /B

:multi_xci_manual
::FOR XCI FILES
set "showname=%orinput%"
call :processing_message
MD "%w_folder%" >NUL 2>&1
MD "%w_folder%\secure" >NUL 2>&1
MD "%w_folder%\normal" >NUL 2>&1
MD "%w_folder%\update" >NUL 2>&1
call :getname
echo ------------------------------------
echo xci에서 보안 파티션 추출하기
echo ------------------------------------
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\secure" %nf_cleaner% "%orinput%"
echo 완료
call :thumbup
call :delay
exit /B

:multi_contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (mlist.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo 여전히 처리할 !conta! 파일
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

REM the logo function has been disabled temporarly for the current beta, the code remains here
REM unaccessed for future modification and reintegration
:multi_set_clogo
cls
call :program_logo
echo ------------------------------------------
echo 커스텀 로고 또는 주요한 게임 설정
echo ------------------------------------------
echo 멀티 게임 xci로 표시됩니다.
echo 현재 커스텀 로고 및 이름은 nsp 또는 nca 제어를 드래그를 위해 설정됩니다.
echo 그런 식으로 프로그램은 정상 파티션에서 nca 컨트롤을 복사합니다.
echo 커스텀 로고를 추가하지 않으면 로고가 게임 중 하나에서 설정됩니다.
echo ..........................................
echo 목록 빌더로 돌아가려면 "b"를 입력하십시오.
echo ..........................................
set /p bs="윈도우 위에 NSP 또는 NCA 파일을 드래그하고 Enter 키를 누릅니다: "
set bs=%bs:"=%
if /i "%bs%"=="b" ( goto multi_checkagain )
if exist "%bs%" ( goto multi_checklogo )
goto multi_set_clogo

:multi_checklogo
if exist "%~dp0logo.txt" del "%~dp0logo.txt" >NUL 2>&1
echo %bs%>"%~dp0hlogo.txt"
FINDSTR /L ".nsp" "%~dp0hlogo.txt" >"%~dp0logo.txt"
FINDSTR /L ".nca" "%~dp0hlogo.txt" >>"%~dp0logo.txt"
set /p custlogo=<"%~dp0logo.txt"
del "%~dp0hlogo.txt"
::echo %custlogo%
for /f "usebackq tokens=*" %%f in ( "%~dp0logo.txt" ) do (
set "logoname=%%~nxf"
if "%%~nxf"=="%%~nf.nsp" goto ext_log
if "%%~nxf"=="%%~nf.nca" goto check_log
)

:ext_log
del "%~dp0logo.txt"
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
if exist "%w_folder%\normal" RD /S /Q "%w_folder%\normal" >NUL 2>&1

%pycommand% "%nut%" --nsptype "%custlogo%">"%w_folder%\nsptype.txt"
set /p nsptype=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt"
if "%nsptype%" EQU "DLC" echo.
if "%nsptype%" EQU "DLC" echo ---NSP DOESN'T HAVE A CONTROL NCA---
if "%nsptype%" EQU "DLC" echo.
if "%nsptype%" EQU "DLC" ( goto multi_set_clogo )
MD "%w_folder%\normal" >NUL 2>&1
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\normal" --NSP_copy_nca_control "%custlogo%"
echo ................
echo "추출된 로고"
echo ................
echo.
goto multi_checkagain

:check_log
del "%~dp0logo.txt"
if not exist "%w_folder%" MD "%w_folder%" >NUL 2>&1
if exist "%w_folder%\normal" RD /S /Q "%w_folder%\normal" >NUL 2>&1
%pycommand% "%nut%" --ncatype "%custlogo%">"%w_folder%\ncatype.txt"
set /p ncatype=<"%w_folder%\ncatype.txt"
del "%w_folder%\ncatype.txt"
if "%ncatype%" NEQ "Content.CONTROL" echo.
if "%ncatype%" NEQ "Content.CONTROL" echo ---NCA는 제어 유형이 아닙니다---
if "%ncatype%" NEQ "Content.CONTROL" echo.
if "%ncatype%" NEQ "Content.CONTROL" ( goto multi_set_clogo )
MD "%w_folder%\normal" >NUL 2>&1
copy "%custlogo%" "%w_folder%\normal\%logoname%"
echo.
goto multi_checkagain
exit


::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
::SPLITTER MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////

:SPLMODE
cls
call :program_logo
if exist %w_folder% RD /S /Q "%w_folder%" >NUL 2>&1
echo -----------------------------------------------
echo 분할 모드 작동
echo -----------------------------------------------
if exist "splist.txt" goto sp_prevlist
goto sp_manual_INIT
:sp_prevlist
set conta=0
for /f "tokens=*" %%f in (splist.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del splist.txt )
endlocal
if not exist "splist.txt" goto sp_manual_INIT
ECHO .......................................................
ECHO 이전 목록이 발견되었습니다. 무엇을 하고 싶습니까?
:sp_prevlist0
ECHO .......................................................
echo "1" 이전 목록에서 자동 시작 처리
echo "2" 목록을 지우고 새 목록 작성
echo "3" 이전 목록 작성 계속
echo .......................................................
echo 참고: 3을 누르면 파일 처리를 시작하기 전에 이전 목록이
echo 표시되고 목록에서 항목을 추가 및 삭제할 수 있습니다.
echo
echo.
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="3" goto sp_showlist
if /i "%bs%"=="2" goto sp_delist
if /i "%bs%"=="1" goto sp_start_cleaning
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo BAD CHOICE
goto sp_prevlist0
:sp_delist
del splist.txt
cls
call :program_logo
echo -----------------------------------------------
echo 분할 모드가 활성화되었습니다
echo -----------------------------------------------
echo ......................................
echo 새로운 목록을 시작하기로 결정했습니다.
echo ......................................
:sp_manual_INIT
endlocal
ECHO ***********************************************
echo 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ***********************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%splist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry

echo.
:sp_checkagain
echo 무엇을 하고 싶습니까?
echo ...............................................................................
echo "다른 파일 또는 폴더를 드래그하고 목록에 항목을 추가하려면 ENTER 키를 누릅니다"
echo.
echo "1" 프로세스 시작
echo "e" 종료
echo "i" 처리할 파일 목록 보기
echo "r" 일부 파일을 삭제 (하단에서부터 계산)
echo "z" 전체 목록을 삭제
echo ...............................................................................
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
%pycommand% "%nut%" -t nsp xci -tfile "%prog_dir%splist.txt" -uin "%uinput%" -ff "uinput"
set /p eval=<"%uinput%"
set eval=%eval:"=%
setlocal enabledelayedexpansion
echo+ >"%uinput%"
endlocal

if /i "%eval%"=="0" goto manual_Reentry
if /i "%eval%"=="1" goto sp_start_cleaning
if /i "%eval%"=="e" goto salida
if /i "%eval%"=="i" goto sp_showlist
if /i "%eval%"=="r" goto sp_r_files
if /i "%eval%"=="z" del splist.txt

goto sp_checkagain

:sp_r_files
set /p bs="(하단에서) 삭제할 파일 수를 입력하십시오: "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:sp_update_list1
if !pos1! GTR !pos2! ( goto :sp_update_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :sp_update_list1
:sp_update_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<splist.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>splist.txt.new
endlocal
move /y "splist.txt.new" "splist.txt" >nul
endlocal

:sp_showlist
cls
call :program_logo
echo -------------------------------------------------
echo 불할 모드가 활성화되었습니다
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                   처리할 파일
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (splist.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo 처리할 !conta! 파일을 추가했습니다.
echo .................................................
endlocal

goto sp_checkagain

:sp_cl_wrongchoice
echo 틀린 선택
echo ............
:sp_start_cleaning
echo *******************************************************
echo 선택한 파일을 처리한 후 수행할 작업을 선택하십시오.
echo *******************************************************
echo "1" nsp로 목록 리팩
echo "2" xci로 목록 리팩
echo "3" nsp와 xci로 목록 리팩
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "b"를 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="b" goto sp_checkagain
if /i "%bs%"=="1" set "vrepack=nsp"
if /i "%bs%"=="2" set "vrepack=xci"
if /i "%bs%"=="3" set "vrepack=both"
if %vrepack%=="none" goto sp_cl_wrongchoice
cls
call :program_logo
for /f "tokens=*" %%f in (splist.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "end_folder=%%~nf"
set "orinput=%%f"
if "%%~nxf"=="%%~nf.nsp" call :split_content
if "%%~nxf"=="%%~nf.NSP" call :split_content
if "%%~nxf"=="%%~nf.xci" call :split_content
if "%%~nxf"=="%%~nf.XCI" call :split_content
%pycommand% "%nut%" --strip_lines "%prog_dir%splist.txt"
setlocal enabledelayedexpansion
if exist "%fold_output%\!end_folder!" RD /S /Q "%fold_output%\!end_folder!" >NUL 2>&1
MD "%fold_output%\!end_folder!" >NUL 2>&1
move "%w_folder%\*.xci" "%fold_output%\!end_folder!\" >NUL 2>&1
move "%w_folder%\*.xc*" "%fold_output%\!end_folder!\" >NUL 2>&1
move "%w_folder%\*.nsp" "%fold_output%\!end_folder!\" >NUL 2>&1
move "%w_folder%\*.ns*" "%fold_output%\!end_folder!\" >NUL 2>&1
if exist "%w_folder%\archfolder" ( %pycommand% "%nut%" -ifo "%w_folder%\archfolder" -archive "%fold_output%\!end_folder!\%filename%.nsp" )
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
endlocal
call :sp_contador_NF
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
:SPLIT_exit_choice
if exist splist.txt del splist.txt
if /i "%va_exit%"=="true" echo 프로그램은 지금 닫을 것입니다.
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo "0" 모드 선택 돌아가기
echo "1" 프로그램 종료
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto SPLIT_exit_choice

:split_content
rem if "%fatype%" EQU "-fat fat32" goto split_content_fat32
set "showname=%orinput%"
set "sp_repack=%vrepack%"
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
call :processing_message
call :squirrell
if "%vrepack%" EQU "nsp" ( %pycommand% "%nut%" %buffer% -o "%w_folder%" %fatype% %fexport% -t "nsp" -dspl "%orinput%" -tfile "%prog_dir%splist.txt")
if "%vrepack%" EQU "xci" ( %pycommand% "%nut%" %buffer% -o "%w_folder%" %fatype% %fexport% -t "xci" -dspl "%orinput%" -tfile "%prog_dir%splist.txt")
if "%vrepack%" EQU "both" ( %pycommand% "%nut%" %buffer% -o "%w_folder%" %fatype% %fexport% -t "both" -dspl "%orinput%" -tfile "%prog_dir%splist.txt")

call :thumbup
call :delay
exit /B

:split_content_fat32
CD /d "%prog_dir%"
set "showname=%orinput%"
set "sp_repack=%vrepack%"
if exist "%w_folder%" RD /S /Q  "%w_folder%" >NUL 2>&1
MD "%w_folder%" >NUL 2>&1
call :processing_message
call :squirrell
%pycommand% "%nut%" %buffer% -o "%w_folder%" --splitter "%orinput%" -pe "secure"
for /f "usebackq tokens=*" %%f in ("%w_folder%\dirlist.txt") do (
setlocal enabledelayedexpansion
rem echo "!sp_repack!"
set "tfolder=%%f"
set "fname=%%~nf"
set "test=%%~nf"
set test=!test:[DLC]=!
rem echo !test!
rem echo "!test!"
rem echo "!fname!"
if "!test!" NEQ "!fname!" ( set "sp_repack=nsp" )
rem echo "!sp_repack!"
set "test=%%~nf"
set test=!test:[UPD]=!
rem echo !test!
rem echo "!test!"
rem echo "!fname!"
if "!test!" NEQ "!fname!" ( set "sp_repack=nsp" )
rem echo "!sp_repack!"
if "!sp_repack!" EQU "nsp" ( call "%nsp_lib%" "sp_convert" "%w_folder%" "!tfolder!" "!fname!" )
if "!sp_repack!" EQU "xci" ( call "%xci_lib%" "sp_repack" "%w_folder%" "!tfolder!" "!fname!" )
if "!sp_repack!" EQU "both" ( call "%nsp_lib%" "sp_convert" "%w_folder%" "!tfolder!" "!fname!" )
if "!sp_repack!" EQU "both" ( call "%xci_lib%" "sp_repack" "%w_folder%" "!tfolder!" "!fname!" )
endlocal
%pycommand% "%nut%" --strip_lines "%prog_dir%dirlist.txt"
)
del "%w_folder%\dirlist.txt" >NUL 2>&1

call :thumbup
call :delay
exit /B

:sp_contador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (splist.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo 아직도 처리할 !conta! 파일
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B

::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:: DB-MODE
::///////////////////////////////////////////////////
::///////////////////////////////////////////////////
:DBMODE
cls
call :program_logo
echo -----------------------------------------------
echo 데이터베이스 생성 모드 활성화되었습니다
echo -----------------------------------------------
if exist "DBL.txt" goto DBprevlist
goto DBmanual_INIT
:DBprevlist
set conta=0
for /f "tokens=*" %%f in (DBL.txt) do (
echo %%f
) >NUL 2>&1
setlocal enabledelayedexpansion
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
) >NUL 2>&1
if !conta! LEQ 0 ( del DBL.txt )
endlocal
if not exist "DBL.txt" goto DBmanual_INIT
ECHO .......................................................
ECHO 이전 목록이 발견되었습니다. 뭐엇을 하고 싶습니까?
:DBprevlist0
ECHO .......................................................
echo "1" 이전 목록에서 자동 시작 처리
echo "2" 목록을 지우고 새 목록 작성
echo "3" 이전 목록 작성을 계속
echo .......................................................
echo 참고: 3을 누르면 파일 처리를 시작하기 전에 이전 목록이
echo 표시되며 목록에서 항목을 추가 및 삭제할 수 있습니다.
echo
echo.
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="3" goto DBshowlist
if /i "%bs%"=="2" goto DBdelist
if /i "%bs%"=="1" goto DBstart_cleaning
if /i "%bs%"=="0" goto manual_Reentry
echo.
echo 나쁜 선택
goto DBprevlist0
:DBdelist
del DBL.txt
cls
call :program_logo
echo -----------------------------------------------
echo 개별적인 처리가 활성화되었습니다.
echo -----------------------------------------------
echo ..................................
echo 새 목록을 시작하기로 결정했습니다.
echo ..................................
:DBmanual_INIT
endlocal
ECHO ***********************************************
echo 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ***********************************************
echo.
set /p bs="윈도우 위로 파일이나 폴더를 드래그하여 ENTER를 누르십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
set "targt=%bs%"
dir "%bs%\" >nul 2>nul
if not errorlevel 1 goto DBcheckfolder
if exist "%bs%\" goto DBcheckfolder
goto DBcheckfile
:DBcheckfolder
%pycommand% "%nut%" -t nsp xci nsx -tfile "%prog_dir%DBL.txt" -ff "%targt%"
goto DBcheckagain
:DBcheckfile
%pycommand% "%nut%" -t nsp xci nsx -tfile "%prog_dir%DBL.txt" -ff "%targt%"
goto DBcheckagain
echo.
:DBcheckagain
echo 무엇을 하고 싶습니까?
echo ................................................................................
echo "다른 파일 또는 폴더를 드래그하고 목록에 항목을 추가하려면 ENTER 키를 누릅니다."
echo.
echo "1" 프로세스 시작
echo "e" 종료
echo "i" 처리할 파일 목록 보기
echo "r" 일부 파일 삭제 (하단에서부터 계산)
echo "z" 전체 목록 삭제
echo ................................................................................
ECHO ****************************************************
echo 또는 모드 선택 메뉴로 돌아가려면 "0"을 입력하십시오.
ECHO ****************************************************
echo.
set /p bs="파일/폴더 드래그 또는 옵션 설정: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto DBstart_cleaning
if /i "%bs%"=="e" goto DBsalida
if /i "%bs%"=="i" goto DBshowlist
if /i "%bs%"=="r" goto DBr_files
if /i "%bs%"=="z" del DBL.txt
set "targt=%bs%"
dir "%bs%\" >nul 2>nul
if not errorlevel 1 goto DBcheckfolder
if exist "%bs%\" goto DBcheckfolder
goto DBcheckfile
goto DBsalida

:DBr_files
set /p bs="(하단에서) 삭제할 파일 수를 입력하십시오: "
set bs=%bs:"=%

setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)

set /a pos1=!conta!-!bs!
set /a pos2=!conta!
set string=

:DBupdate_list1
if !pos1! GTR !pos2! ( goto :DBupdate_list2 ) else ( set /a pos1+=1 )
set string=%string%,%pos1%
goto :DBupdate_list1
:DBupdate_list2
set string=%string%,
set skiplist=%string%
Set "skip=%skiplist%"
setlocal DisableDelayedExpansion
(for /f "tokens=1,*delims=:" %%a in (' findstr /n "^" ^<DBL.txt'
) do Echo=%skip%|findstr ",%%a," 2>&1>NUL ||Echo=%%b
)>DBL.txt.new
endlocal
move /y "DBL.txt.new" "DBL.txt" >nul
endlocal

:DBshowlist
cls
call :program_logo
echo -------------------------------------------------
echo 개별적인 처리가 활성화되었습니다.
echo -------------------------------------------------
ECHO -------------------------------------------------
ECHO                    처리할 파일
ECHO -------------------------------------------------
for /f "tokens=*" %%f in (DBL.txt) do (
echo %%f
)
setlocal enabledelayedexpansion
set conta=
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)
echo .................................................
echo 처리할 !conta! 파일을 추가했습니다
echo .................................................
endlocal

goto DBcheckagain

:DBs_cl_wrongchoice
echo wrong choice
echo ............
:DBstart_cleaning
echo *******************************************************
echo 선택한 파일을 처리한 후 수행할 작업을 선택하십시오.
echo *******************************************************
echo "1" NUTDB 데이터베이스 생성
echo "2" 확장 데이터베이스 생성
echo "3" 키가 없는 데이터베이스 생성 (확장)
echo "4" 간단한 데이터베이스 생성
echo "5" 위의 모든 4 개의 데이터베이스 생성
echo "Z" ZIP 파일 만들기
echo.
ECHO *************************************************
echo 또는 목록 옵션으로 돌아가려면 "0"을 입력하십시오.
ECHO *************************************************
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
set vrepack=none
if /i "%bs%"=="0" goto DBcheckagain
if /i "%bs%"=="Z" set "vrepack=zip"
if /i "%bs%"=="Z" goto DBs_start
if /i "%bs%"=="1" set "dbformat=nutdb"
if /i "%bs%"=="1" goto DBs_GENDB
if /i "%bs%"=="2" set "dbformat=extended"
if /i "%bs%"=="2" goto DBs_GENDB
if /i "%bs%"=="3" set "dbformat=keyless"
if /i "%bs%"=="3" goto DBs_GENDB
if /i "%bs%"=="4" set "dbformat=simple"
if /i "%bs%"=="4" goto DBs_GENDB
if /i "%bs%"=="5" set "dbformat=all"
if /i "%bs%"=="5" goto DBs_GENDB
if %vrepack%=="none" goto DBs_cl_wrongchoice

:DBs_start
cls
call :program_logo
for /f "tokens=*" %%f in (DBL.txt) do (
set "name=%%~nf"
set "filename=%%~nxf"
set "orinput=%%f"
set "ziptarget=%%f"
if "%vrepack%" EQU "zip" ( set "zip_restore=true" )
if "%%~nxf"=="%%~nf.nsp" call :DBnsp_manual
if "%%~nxf"=="%%~nf.nsx" call :DBnsp_manual
if "%%~nxf"=="%%~nf.NSP" call :DBnsp_manual
if "%%~nxf"=="%%~nf.NSX" call :DBnsp_manual
if "%%~nxf"=="%%~nf.xci" call :DBnsp_manual
if "%%~nxf"=="%%~nf.XCI" call :DBnsp_manual
%pycommand% "%nut%" --strip_lines "%prog_dir%DBL.txt"
call :DBcontador_NF
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
:DBs_exit_choice
if exist DBL.txt del DBL.txt
if /i "%va_exit%"=="true" echo 프로그램은 지금 닫을 것입니다.
if /i "%va_exit%"=="true" ( PING -n 2 127.0.0.1 >NUL 2>&1 )
if /i "%va_exit%"=="true" goto salida
echo.
echo "0" 모드 선택 돌아가기
echo "1" 프로그램 종료
echo.
set /p bs="선택 사항을 입력하십시오: "
set bs=%bs:"=%
if /i "%bs%"=="0" goto manual_Reentry
if /i "%bs%"=="1" goto salida
goto s_exit_choice

:DBnsp_manual
set "filename=%name%"
set "showname=%orinput%"
if exist "%w_folder%" rmdir /s /q "%w_folder%" >NUL 2>&1
MD "%w_folder%"
call :squirrell

if "%vrepack%" EQU "zip" ( goto nsp_just_zip )

:DBnsp_just_zip
if "%zip_restore%" EQU "true" ( call :makezip )
rem call :getname
if "%vrename%" EQU "true" call :addtags_from_nsp
if "%zip_restore%" EQU "true" ( goto :nsp_just_zip2 )

:DBnsp_just_zip2

if exist "%w_folder%\*.zip" ( MD "%zip_fold%" ) >NUL 2>&1
move "%w_folder%\*.zip" "%zip_fold%" >NUL 2>&1
RD /S /Q "%w_folder%" >NUL 2>&1

echo 완료
call :thumbup
call :delay

:DBend_nsp_manual
exit /B

:DBs_GENDB
for /f "tokens=*" %%f in (DBL.txt) do (
set "orinput=%%f"
set "db_file=%prog_dir%INFO\%dbformat%_DB.txt"
set "dbdir=%prog_dir%INFO\"
call :DBGeneration
%pycommand% "%nut%" --strip_lines "%prog_dir%DBL.txt"
call :DBcontador_NF
)
ECHO ---------------------------------------------------
ECHO ********** 모든 파일이 처리되었습니다! ************
ECHO ---------------------------------------------------
goto DBs_exit_choice

:DBGeneration
if not exist "%dbdir%" MD "%dbdir%">NUL 2>&1
%pycommand% "%nut%" --dbformat "%dbformat%" -dbfile "%db_file%" -tfile "%prog_dir%DBL.txt" -nscdb "%orinput%"
exit /B

:DBcontador_NF
setlocal enabledelayedexpansion
set /a conta=0
for /f "tokens=*" %%f in (DBL.txt) do (
set /a conta=!conta! + 1
)
echo ...................................................
echo 여전히 처리할 !conta! 파일
echo ...................................................
PING -n 2 127.0.0.1 >NUL 2>&1
set /a conta=0
endlocal
exit /B


::///////////////////////////////////////////////////
::NSCB FILE INFO MODE
::///////////////////////////////////////////////////
:INFMODE
call "%infobat%" "%prog_dir%"
cls
goto TOP_INIT

::///////////////////////////////////////////////////
::NSCB_options.cmd configuration script
::///////////////////////////////////////////////////
:OPT_CONFIG
call "%batconfig%" "%op_file%" "%listmanager%" "%batdepend%"
cls
goto TOP_INIT


::///////////////////////////////////////////////////
::SUBROUTINES
::///////////////////////////////////////////////////

:squirrell
echo                    ,;:;;,
echo                   ;;;;;
echo           .=',    ;:;;:,
echo          /_', "=. ';:;:;
echo          @=:__,  \,;:;:'
echo            _(\.=  ;:;;'
echo           `"_(  _/="`
echo            `"'
exit /B

:program_logo

ECHO                                        __          _ __    __
ECHO                  ____  _____ ____     / /_  __  __(_) /___/ /__  _____
ECHO                 / __ \/ ___/ ___/    / __ \/ / / / / / __  / _ \/ ___/
ECHO                / / / (__  ) /__     / /_/ / /_/ / / / /_/ /  __/ /
ECHO               /_/ /_/____/\___/____/_.___/\__,_/_/_/\__,_/\___/_/
ECHO                              /_____/
ECHO -------------------------------------------------------------------------------------
ECHO                             닌텐도 스위치 클리너 및 빌더
ECHO                            (XCI 다중 콘텐츠 빌더 및 기타)
ECHO -------------------------------------------------------------------------------------
ECHO =============================    JULESONTHEROAD 제작    =============================
ECHO -------------------------------------------------------------------------------------
ECHO "                             다람쥐의 지원을 받는 NSCB                             "
ECHO "                      BLAWAR 및 LUCA FRAGA 작업을 기반으로 작업                    "
ECHO                                   버전 0.88 (신규)
ECHO -------------------------------------------------------------------------------------
ECHO Program의 github: https://github.com/julesontheroad/NSC_BUILDER
ECHO Blawar의 github:  https://github.com/blawar
ECHO Luca Fraga의 github: https://github.com/LucaFraga
ECHO -------------------------------------------------------------------------------------
exit /B

:delay
PING -n 2 127.0.0.1 >NUL 2>&1
exit /B

:thumbup
echo.
echo    /@
echo    \ \
echo  ___\ \
echo (__O)  \
echo (____@) \
echo (____@)  \
echo (__o)_    \
echo       \    \
echo.
echo 즐거운 시간이 되길 바랍니다.
echo.
exit /B

:getname

if not exist %w_folder% MD %w_folder% >NUL 2>&1

set filename=%filename:[nap]=%
set filename=%filename:[xc]=%
set filename=%filename:[nc]=%
set filename=%filename:[rr]=%
set filename=%filename:[xcib]=%
set filename=%filename:[nxt]=%
set filename=%filename:[Trimmed]=%
echo %filename% >"%w_folder%\fname.txt"

::deletebrackets
for /f "usebackq tokens=1* delims=[" %%a in ("%w_folder%\fname.txt") do (
    set end_folder=%%a)
echo %end_folder%>"%w_folder%\fname.txt"
::deleteparenthesis
for /f "usebackq tokens=1* delims=(" %%a in ("%w_folder%\fname.txt") do (
    set end_folder=%%a)
echo %end_folder%>"%w_folder%\fname.txt"
::I also wanted to remove_(
set end_folder=%end_folder:_= %
set end_folder=%end_folder:~0,-1%
del "%w_folder%\fname.txt" >NUL 2>&1
if "%vrename%" EQU "true" ( set "filename=%end_folder%" )
exit /B

:makezip
echo.
echo %ziptarget%에 대한 zip 만들기
echo.
%pycommand% "%nut%" %buffer% %patchRSV% %vkey% %capRSV% -o "%w_folder%\zip" --zip_combo "%ziptarget%"
%pycommand% "%nut%" -o "%w_folder%\zip" --NSP_c_KeyBlock "%ziptarget%"
%pycommand% "%nut%" --nsptitleid "%ziptarget%" >"%w_folder%\nsptitleid.txt"
if exist "%w_folder%\secure\*.dat" ( move "%w_folder%\secure\*.dat" "%w_folder%\zip" ) >NUL 2>&1

set /p titleid=<"%w_folder%\nsptitleid.txt"
del "%w_folder%\nsptitleid.txt" >NUL 2>&1
%pycommand% "%nut%" --nsptype "%ziptarget%" >"%w_folder%\nsptype.txt"
set /p type=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt" >NUL 2>&1
%pycommand% "%nut%" --ReadversionID "%ziptarget%">"%w_folder%\nspversion.txt"
set /p verID=<"%w_folder%\nspversion.txt"
set "verID=V%verID%"
del "%w_folder%\nspversion.txt" >NUL 2>&1
if "%type%" EQU "BASE" ( set "ctag=" )
if "%type%" EQU "UPDATE" ( set ctag=[UPD] )
if "%type%" EQU "DLC" ( set ctag=[DLC] )
%pycommand% "%nut%" -i "%ziptarget%">"%w_folder%\zip\fileinfo[%titleid%][%verID%]%ctag%.txt"
%pycommand% "%nut%" --filelist "%ziptarget%">"%w_folder%\zip\ORIGINAL_filelist[%titleid%][%verID%]%ctag%.txt"
"%zip%" -ifo "%w_folder%\zip" -zippy "%w_folder%\%titleid%[%verID%]%ctag%.zip"
RD /S /Q "%w_folder%\zip" >NUL 2>&1
exit /B

:processing_message
echo Processing %showname%
echo.
exit /B

:check_titlerights
%pycommand% "%nut%" --nsp_htrights "%target%">"%w_folder%\trights.txt"
set /p trights=<"%w_folder%\trights.txt"
del "%w_folder%\trights.txt" >NUL 2>&1
if "%trights%" EQU "TRUE" ( goto ct_true )
if "%vrepack%" EQU "nsp" ( set "vpack=none" )
if "%vrepack%" EQU "both" ( set "vpack=xci" )
:ct_true
exit /B


:addtags_from_nsp
%pycommand% "%nut%" --nsptitleid "%orinput%" >"%w_folder%\nsptitleid.txt"
set /p titleid=<"%w_folder%\nsptitleid.txt"
del "%w_folder%\nsptitleid.txt" >NUL 2>&1
%pycommand% "%nut%" --nsptype "%orinput%" >"%w_folder%\nsptype.txt"
set /p type=<"%w_folder%\nsptype.txt"
del "%w_folder%\nsptype.txt" >NUL 2>&1
if "%type%" EQU "BASE" ( set filename=%filename%[%titleid%][v0] )
if "%type%" EQU "UPDATE" ( set filename=%filename%[%titleid%][UPD] )
if "%type%" EQU "DLC" ( set filename=%filename%[%titleid%][DLC] )

exit /B
:addtags_from_xci
dir "%w_folder%\secure\*.cnmt.nca" /b  >"%w_folder%\ncameta.txt"
set /p ncameta=<"%w_folder%\ncameta.txt"
del "%w_folder%\ncameta.txt" >NUL 2>&1
set "ncameta=%w_folder%\secure\%ncameta%"
%pycommand% "%nut%" --ncatitleid "%ncameta%" >"%w_folder%\ncaid.txt"
set /p titleid=<"%w_folder%\ncaid.txt"
del "%w_folder%\ncaid.txt"
echo [%titleid%]>"%w_folder%\titleid.txt"

FINDSTR /L 000] "%w_folder%\titleid.txt">"%w_folder%\isbase.txt"
set /p c_base=<"%w_folder%\isbase.txt"
del "%w_folder%\isbase.txt"
FINDSTR /L 800] "%w_folder%\titleid.txt">"%w_folder%\isupdate.txt"
set /p c_update=<"%w_folder%\isupdate.txt"
del "%w_folder%\isupdate.txt"

set ttag=[DLC]

if [%titleid%] EQU %c_base% set ttag=[v0]
if [%titleid%] EQU %c_update% set ttag=[UPD]

set filename=%filename%[%titleid%][%ttag%]
del "%w_folder%\titleid.txt"
exit /B

:missing_things
call :program_logo
echo ....................................
echo 다음과 같은 것들이 누락되었습니다. :
echo ....................................
echo.
if not exist "%op_file%" echo - 구성 파일이 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%nut%" echo - "nut_RTR.py"가 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%xci_lib%" echo - "XCI.bat"이 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%nsp_lib%" echo - "NSP.bat"이 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%zip%" echo - "7za.exe"가 올바르게 지정되지 않았거나 누락되었습니다.

if not exist "%hacbuild%" echo - "hacbuild.exe"가 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%listmanager%" echo - "listmanager.py"가 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%batconfig%" echo - "NSCB_config.bat"이 올바르게 지정되지 않았거나 누락되었습니다.
if not exist "%infobat%" echo - "info.bat"이 올바르게 지정되지 않았거나 누락되었습니다.
::File full route
if not exist "%dec_keys%" echo - "keys.txt"가 올바르게 지정되지 않았거나 누락되었습니다.
echo.
pause
echo 프로그램이 지금 종료됩니다.
PING -n 2 127.0.0.1 >NUL 2>&1
goto salida
:salida
::pause
exit
