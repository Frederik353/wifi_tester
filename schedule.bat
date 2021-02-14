@echo off
:loop
start "MyScript" python "speedtest.py" 
waitfor SomethingThatIsNeverHappening /t 2 2>NUL
taskkill /FI "WINDOWTITLE eq MyScript"
goto :loop