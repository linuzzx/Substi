@echo off
pyinstaller -F --add-data "templates;templates" app.py 
del app.spec
del /Q /F build
rmdir /Q /S build
