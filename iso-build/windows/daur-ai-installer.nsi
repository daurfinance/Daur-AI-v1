; Daur-AI v2.0 Installer Script
; NSIS Modern User Interface

;--------------------------------
; Includes
!include "MUI2.nsh"
!include "FileFunc.nsh"

;--------------------------------
; General
Name "Daur-AI v2.0"
OutFile "Daur-AI-v2.0-Setup.exe"
Unicode True

; Default installation folder
InstallDir "$LOCALAPPDATA\Daur-AI"

; Get installation folder from registry if available
InstallDirRegKey HKCU "Software\Daur-AI" ""

; Request application privileges
RequestExecutionLevel user

;--------------------------------
; Variables
Var StartMenuFolder

;--------------------------------
; Interface Settings
!define MUI_ABORTWARNING
!define MUI_ICON "resources\icon.ico"
!define MUI_UNICON "resources\icon.ico"
!define MUI_WELCOMEFINISHPAGE_BITMAP "resources\welcome.bmp"
!define MUI_HEADERIMAGE
!define MUI_HEADERIMAGE_BITMAP "resources\header.bmp"
!define MUI_HEADERIMAGE_RIGHT

;--------------------------------
; Pages
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "docs\LICENSE.txt"
!insertmacro MUI_PAGE_COMPONENTS
!insertmacro MUI_PAGE_DIRECTORY

; Start Menu Folder Page Configuration
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "HKCU" 
!define MUI_STARTMENUPAGE_REGISTRY_KEY "Software\Daur-AI" 
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "Start Menu Folder"
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "Daur-AI"
!insertmacro MUI_PAGE_STARTMENU Application $StartMenuFolder

!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_WELCOME
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
!insertmacro MUI_UNPAGE_FINISH

;--------------------------------
; Languages
!insertmacro MUI_LANGUAGE "English"

;--------------------------------
; Installer Sections
Section "Daur-AI Core" SecCore
  SectionIn RO
  
  ; Set output path to the installation directory
  SetOutPath "$INSTDIR"
  
  ; Add files
  File /r "app\*.*"
  File /r "docs\*.*"
  File /r "resources\*.*"
  File "install.bat"
  
  ; Store installation folder
  WriteRegStr HKCU "Software\Daur-AI" "" $INSTDIR
  
  ; Create uninstaller
  WriteUninstaller "$INSTDIR\Uninstall.exe"
  
  ; Create shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
    CreateDirectory "$SMPROGRAMS\$StartMenuFolder"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Daur-AI.lnk" "$INSTDIR\app\main.py" "" "$INSTDIR\resources\icon.ico"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Documentation.lnk" "$INSTDIR\docs\README.md"
    CreateShortcut "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk" "$INSTDIR\Uninstall.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
  
  ; Create desktop shortcut
  CreateShortcut "$DESKTOP\Daur-AI.lnk" "$INSTDIR\app\main.py" "" "$INSTDIR\resources\icon.ico"
SectionEnd

Section "Python Dependencies" SecPython
  ; Install Python dependencies
  ExecWait 'python -m pip install --upgrade pip'
  ExecWait 'pip install -r "$INSTDIR\app\requirements.txt"'
SectionEnd

Section "Telegram Integration" SecTelegram
  ; Install Telegram integration
  ExecWait 'pip install python-telegram-bot'
SectionEnd

;--------------------------------
; Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecCore} "Core files required for Daur-AI to function."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecPython} "Python dependencies required for Daur-AI."
  !insertmacro MUI_DESCRIPTION_TEXT ${SecTelegram} "Integration with Telegram for remote control."
!insertmacro MUI_FUNCTION_DESCRIPTION_END

;--------------------------------
; Uninstaller Section
Section "Uninstall"
  ; Remove files and directories
  RMDir /r "$INSTDIR\app"
  RMDir /r "$INSTDIR\docs"
  RMDir /r "$INSTDIR\resources"
  Delete "$INSTDIR\install.bat"
  Delete "$INSTDIR\Uninstall.exe"
  RMDir "$INSTDIR"
  
  ; Remove shortcuts
  !insertmacro MUI_STARTMENU_GETFOLDER Application $StartMenuFolder
  Delete "$SMPROGRAMS\$StartMenuFolder\Daur-AI.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Documentation.lnk"
  Delete "$SMPROGRAMS\$StartMenuFolder\Uninstall.lnk"
  RMDir "$SMPROGRAMS\$StartMenuFolder"
  Delete "$DESKTOP\Daur-AI.lnk"
  
  ; Remove registry keys
  DeleteRegKey HKCU "Software\Daur-AI"
SectionEnd
