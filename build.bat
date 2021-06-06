@echo off
rmdir build /s /q
rmdir dist /s
python.exe -OO -m PyInstaller ^
    --windowed ^
    --icon images\icon.ico ^
    --exclude-module=tkinter ^
    --exclude-module=tk ^
    --exclude-module=FixTk ^
    --exclude-module=_tkinter ^
    --exclude-module=Tkinter ^
    --exclude-module=tcl ^
    --add-data images\icon.ico;. ^
    --add-data add-members.png;. ^
    --add-data LICENSE;. ^
    wlan-codes.py
cd dist
powershell Compress-Archive wlan-codes\* wlan-codes.zip