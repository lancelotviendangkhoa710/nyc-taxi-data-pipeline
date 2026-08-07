@echo off
cd /d "%~dp0dbt"
call ..\.venv\Scripts\activate.bat
echo Running DBT Models...
dbt run
echo Running DBT Tests...
dbt test
pause
