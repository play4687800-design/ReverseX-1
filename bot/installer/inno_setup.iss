#define MyAppName "ReverseX"
#define MyAppVersion "1.0"
#define MyAppPublisher "ReverseX Project"
#define MyAppExeName "ReverseX.exe"

[Setup]
AppId={{A0E7519C-7B5C-4C9C-A903-0F380B7F0F11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=dist
OutputBaseFilename=ReverseXSetup
ArchitecturesInstallIn64BitMode=x64
Compression=lzma2
SolidCompression=yes
SetupIconFile=..\assets\icons\reversex.ico
ChangesAssociations=yes

[Files]
Source: "..\dist\ReverseX\*"; DestDir: "{app}"; Flags: recursesubdirs

[Icons]
Name: "{group}\ReverseX"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\ReverseX"; Filename: "{app}\{#MyAppExeName}"

[Registry]
Root: HKCR; Subkey: ".stl"; ValueType: string; ValueData: "ReverseX.STL"; Flags: uninsdeletekey
Root: HKCR; Subkey: "ReverseX.STL"; ValueType: string; ValueData: "STL Model"
Root: HKCR; Subkey: "ReverseX.STL\shell\open\command"; ValueType: string; ValueData: """{app}\{#MyAppExeName}"" ""%1"""
