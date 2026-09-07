#define AppName "InterviewCopilot"
#define AppVersion "0.1.0"
#define AppPublisher "InterviewCopilot"
#define AppExeName "InterviewCopilot.exe"

[Setup]
AppId={{B7A3D1D0-2D13-4C11-A1E0-INTERVIEWCOPILOT}}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={autopf}\InterviewCopilot
DefaultGroupName={#AppName}
OutputBaseFilename=InterviewCopilot-Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=lowest
ArchitecturesInstallIn64BitMode=x64

[Files]
Source: "dist\InterviewCopilot\*"; DestDir: "{app}"; Flags: recursesubdirs ignoreversion

[Icons]
Name: "{autodesktop}\InterviewCopilot"; Filename: "{app}\{#AppExeName}"
Name: "{group}\InterviewCopilot"; Filename: "{app}\{#AppExeName}"

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch InterviewCopilot"; Flags: nowait postinstall skipifsilent
