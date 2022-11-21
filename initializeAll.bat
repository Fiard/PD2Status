@echo off

echo cd %~dp0
cd /D %~dp0

call pythonpath . Python/SetupSymLinks.py
IF ERRORLEVEL 1 echo ERROR SetupSymLinks && exit /b %errorlevel%
