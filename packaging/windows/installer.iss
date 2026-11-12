; Inno Setup Script for GDrive Manager
; Build target: GDriveManager-Setup-x64.exe

#define MyAppName "GDrive Manager"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "GDrive Manager Contributors"
#define MyAppURL "https://github.com/mohit/gdrive-manager"
#define MyAppExeName "GDriveManager.exe"

[Setup]
AppId={{E1B3E08A-32D9-4BF5-8E7B-7F9C623048A1}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
LicenseFile=..\..\LICENSE
OutputDir=..\..\dist
OutputBaseFilename=GDriveManager-Setup-x64
SetupIconFile=..\..\assets\branding\icon.ico
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=dialog
UninstallDisplayIcon={app}\{#MyAppExeName}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Setup
VersionInfoProductTextVersion={#MyAppVersion}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "startupicon"; Description: "Launch {#MyAppName} automatically on Windows startup"; GroupDescription: "System Integration:"; Flags: unchecked

[Files]
Source: "..\..\dist\GDriveManager\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; IconFilename: "{app}\_internal\assets\branding\icon.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; IconFilename: "{app}\_internal\assets\branding\icon.ico"
Name: "{userstartup}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: startupicon; IconFilename: "{app}\_internal\assets\branding\icon.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[Code]
function IsWinFspInstalled(): Boolean;
begin
  Result := RegKeyExists(HKLM, 'SOFTWARE\WinFsp') or
            RegKeyExists(HKLM, 'SOFTWARE\WOW6432Node\WinFsp') or
            DirExists('C:\Program Files\WinFsp') or
            DirExists('C:\Program Files (x86)\WinFsp');
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if not IsWinFspInstalled() then
    begin
      MsgBox('Note: WinFsp was not detected on this system.' + #13#10 + #13#10 +
             'GDrive Manager requires WinFsp for virtual drive streaming (mounting Google Drive as G:, H:, etc.).' + #13#10 + #13#10 +
             'You can install WinFsp at any time using Windows Package Manager:' + #13#10 +
             '  winget install WinFsp.WinFsp' + #13#10 + #13#10 +
             'Offline synchronization and transfers remain fully functional without WinFsp.',
             mbInformation, MB_OK);
    end;
  end;
end;
