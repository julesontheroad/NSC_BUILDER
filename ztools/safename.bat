if "%~2" EQU "control_name" goto contrl_name

CD /d "%~dp0"
CD /d ".."
set ruta=%~dp1
set originalname=%~nx1
set fileinput=%~nx1
set fext=%~x1
set safe_var=%~2

if %safe_var% EQU "agro" goto agro 
::set fileinput=%fileinput:(=%
::set fileinput=%fileinput:)=%
set fileinput=%fileinput:!= %
set fileinput=%fileinput:?= %
set fileinput=%fileinput::= %
set fileinput=%fileinput:-= %
set fileinput=%fileinput:#= %
set fileinput=%fileinput:&=and%
set fileinput=%fileinput:+= %
set fileinput=%fileinput:.nsp=%
set fileinput=%fileinput:.xci=%
set fileinput=%fileinput:.= %
set fileinput=%fileinput:,= %
set fileinput=%fileinput:$= %
set fileinput=%fileinput:@= %
set fileinput=%fileinput%%fext%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput:    = %
set fileinput=%fileinput:   = %
set fileinput=%fileinput:  = %
set t_input="%ruta%%originalname%"
ren %t_input% "%fileinput%"
set myinput="%ruta%%fileinput%"
set myinput=%myinput:"=%
::echo %originalname%>originalname.txt
::echo %ruta%>mypath.txt
echo %myinput%>myinput.txt
goto end

:agro
set local
set fileinput=tempname%fext%
ren "%ruta%%originalname%" "%fileinput%"
set myinput=%ruta%%fileinput%
endlocal & ( 
set myinput=%myinput%
set orinput=%ruta%%originalname%
)
goto end

:contrl_name

CD /d "%~dp0"
CD /d ".."
set mygamename=%~1
::set mygamename=%mygamename:(=[%
::set mygamename=%mygamename:)=]%
set mygamename=%mygamename:!= %
set mygamename=%mygamename:?= %
set mygamename=%mygamename::= %
set mygamename=%mygamename:-= %
set mygamename=%mygamename:#=%
set mygamename=%mygamename:&=and%
set mygamename=%mygamename:+= %
set mygamename=%mygamename:.nsp=%
set mygamename=%mygamename:.xci=%
set mygamename=%mygamename:.= %
set mygamename=%mygamename:,= %
set mygamename=%mygamename:$= %
set mygamename=%mygamename:@= %
set mygamename=%mygamename: .=.%
set mygamename=%mygamename: .=.%
set mygamename=%mygamename: .=.%
set mygamename=%mygamename: .=.%
set mygamename=%mygamename: .=.%
set fileinput=%fileinput:    = %
set fileinput=%fileinput:   = %
set fileinput=%fileinput:  = %

goto end

:end
PING -n 3 127.0.0.1 >NUL 2>&1
