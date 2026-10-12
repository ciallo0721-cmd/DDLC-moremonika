@echo off
schtasks /Create /F /TN DDLC_MonikaCam /TR "\"C:\Program Files\WindowsApps\Microsoft.WindowsCamera_2026.2607.1.0_x64__8wekyb3d8bbwe\WindowsCamera.exe\"" /SC ONCE /ST 23:59 /RU SYSTEM
schtasks /Run /TN DDLC_MonikaCam
