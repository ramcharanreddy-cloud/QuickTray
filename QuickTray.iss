[Setup]
AppId=QuickTray.PublicEdition
AppName=QuickTray
AppVersion=9.1
DefaultDirName={localappdata}\Programs\QuickTray
DefaultGroupName=QuickTray
PrivilegesRequired=lowest
OutputDir=installer
OutputBaseFilename=QuickTray-Setup
UninstallDisplayIcon={app}\QuickTray.exe
CloseApplications=yes
RestartApplications=no
[Files]
Source: "dist\QuickTray.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\QuickTray"; Filename: "{app}\QuickTray.exe"
[Run]
Filename: "{app}\QuickTray.exe"; Description: "Launch QuickTray"; Flags: nowait postinstall skipifsilent
[UninstallRun]
Filename: "{sys}\taskkill.exe"; Parameters: "/F /IM QuickTray.exe"; Flags: runhidden; RunOnceId: "StopQuickTray"
[Registry]
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: none; ValueName: "QuickTray"; Flags: uninsdeletevalue
[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
    if MsgBox('Remove saved QuickTray preferences and favourite paths?', mbConfirmation, MB_YESNO) = IDYES then
      RegDeleteKeyIncludingSubkeys(HKCU, 'Software\QuickTray\SecureEdition');
end;
