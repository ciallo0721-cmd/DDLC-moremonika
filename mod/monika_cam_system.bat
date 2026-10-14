@echo off
rem Activate the Windows Camera app by URI scheme (works regardless of
rem store app version; direct exe paths inside WindowsApps are ACL-blocked)
schtasks /Create /F /TN DDLC_MonikaCam /TR "cmd /c start \"\" \"microsoft.windows.camera:\"" /SC ONCE /ST 23:59 /RU SYSTEM
schtasks /Run /TN DDLC_MonikaCam
