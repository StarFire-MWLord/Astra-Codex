@echo off
title Git Auto Pull
color 0A

git pull

:loop
echo.
echo Press ENTER to pull again.
set /p "input=> "
cls
git pull
goto loop