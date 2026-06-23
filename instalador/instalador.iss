; Inno Setup Script - Sistema Campo Fértil
; Professional Windows Installer

#define MyAppName "Sistema Campo Fértil"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Sistema Campo Fértil"
#define MyAppURL ""
#define MyAppExeName "SistemaCampoFertil.exe"
#define MyAppAssocName MyAppName + " File"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
DefaultDirName={autopf}\{#MyAppName}
DisableProgramGroupPage=yes
DisableDirPage=auto
LicenseFile=
PrivilegesRequiredOverridesAllowed=dialog
OutputDir=.
OutputBaseFilename=SistemaCampoFertil_Instalador_v{#MyAppVersion}
SetupIconFile=icone.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
WizardImageFile=wizard_large.bmp
WizardSmallImageFile=wizard_small.bmp
ArchitecturesInstallIn64BitMode=x64compatible
MinVersion=10.0.17763
ShowLanguageDialog=no
LanguageDetectionMethod=uilanguage
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} - Sistema de Gestao Agropecuaria
VersionInfoCopyright=Copyright (C) 2026 {#MyAppPublisher}

[Languages]
Name: "portuguese"; MessagesFile: "compiler:Languages\Portuguese.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Messages]
portuguese.WizardLicense=Termos de Uso
portuguese.LicenseLabel=Por favor, leia os termos de uso antes de continuar.
portuguese.LicenseAccepted=Aceito os termos


[Tasks]
Name: "desktopicon"; Description: "Criar atalho na &Area de Trabalho"; GroupDescription: "Atalhos:"; Flags: checkablealone
Name: "quicklaunchicon"; Description: "Criar atalho no &Menu Iniciar"; GroupDescription: "Atalhos:"; Flags: checkablealone

[Files]
Source: "SistemaFazenda\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "icone.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: quicklaunchicon; WorkingDir: "{app}"; IconFilename: "{app}\icone.ico"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon; WorkingDir: "{app}"; IconFilename: "{app}\icone.ico"
Name: "{autoprograms}\Desinstalar {#MyAppName}"; Filename: "{uninstallexe}"; IconFilename: "{app}\icone.ico"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "Iniciar {#MyAppName}"; Flags: postinstall nowait skipifsilent shellexec; WorkingDir: "{app}"



[Dirs]
Name: "{app}"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify
Name: "{app}\data\nfs"; Permissions: users-modify

[Code]
procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    if MsgBox('Deseja remover todos os dados do sistema (banco de dados, configurações)?'#13#13'Se escolher "Nao", os dados serão preservados.', mbConfirmation, MB_YESNO) = IDYES then
    begin
      DelTree(ExpandConstant('{app}\data'), True, True, True);
    end;
  end;
end;
