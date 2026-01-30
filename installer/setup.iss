; Inno Setup Script for IFC Translate Tool
;
; Prerequisites:
;   1. Install Inno Setup 6.x (https://jrsoftware.org/isinfo.php)
;   2. Build application with PyInstaller first: pyinstaller ifc_translate.spec
;      This creates dist/IFC Translate Tool/ directory
;
; Build command (run from installer/ directory):
;   iscc setup.iss
;
; Output: installer/Output/IFC_Translate_Tool_Setup.exe

[Setup]
; Application identity
AppName=IFC Translate Tool
AppVersion=1.0.0
AppPublisher=IFC Translate Tool
AppPublisherURL=https://github.com/yourusername/ifc_translate_tool
AppSupportURL=https://github.com/yourusername/ifc_translate_tool
AppUpdatesURL=https://github.com/yourusername/ifc_translate_tool

; Installation directories
DefaultDirName={autopf}\IFC Translate Tool
DefaultGroupName=IFC Translate Tool
DisableProgramGroupPage=yes

; Output configuration
OutputBaseFilename=IFC_Translate_Tool_Setup
OutputDir=Output
Compression=lzma
SolidCompression=yes

; Modern wizard UI
WizardStyle=modern

; Uninstaller
UninstallDisplayIcon={app}\IFC Translate Tool.exe

; Architecture
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\dist\IFC Translate Tool\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\IFC Translate Tool"; Filename: "{app}\IFC Translate Tool.exe"
Name: "{group}\{cm:UninstallProgram,IFC Translate Tool}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\IFC Translate Tool"; Filename: "{app}\IFC Translate Tool.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\IFC Translate Tool.exe"; Description: "{cm:LaunchProgram,IFC Translate Tool}"; Flags: nowait postinstall skipifsilent
