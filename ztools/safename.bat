CD /d "%~dp0"
set ruta=%~dp1
set originalname=%~nx1
set fileinput=%~nx1
set fext=%~x1
set fileinput=%fileinput:!=%
set fileinput=%fileinput:-=%
set fileinput=%fileinput:#=%
set fileinput=%fileinput:&=%
set fileinput=%fileinput:+=%
set fileinput=%fileinput:.nsp=%
set fileinput=%fileinput:.xci=%
set fileinput=%fileinput:.=%
set fileinput=%fileinput:,=%
set fileinput=%fileinput:+=%
set fileinput=%fileinput:$=%
set fileinput=%fileinput:@=a%
set fileinput=%fileinput:?=a%
set fileinput=%fileinput%%fext%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
set fileinput=%fileinput: .=.%
ren "%ruta%%originalname%" "%fileinput%"
set myinput=%ruta%%fileinput%
CD /d ".."
::echo %originalname%>originalname.txt
::echo %ruta%>mypath.txt
echo %myinput%>myinput.txt

:end
PING -n 3 127.0.0.1 >NUL 2>&1
