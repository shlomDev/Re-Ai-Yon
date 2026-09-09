#define AppName "ReAion"
#define AppVersion "0.2.0"
#define AppPublisher "ReAion"
#define AppExeName "ReAion.exe"

[Setup]
AppId={{B7A3D1D0-2D13-4C11-A1E0-INTERVIEWCOPILOT}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\ReAion
DefaultGroupName={#AppName}
OutputBaseFilename=ReAion-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\ReAion\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autodesktop}\ReAion"; Filename: "{app}\{#AppExeName}"
Name: "{group}\ReAion"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch ReAion"; Flags: nowait postinstall skipifsilent
