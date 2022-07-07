/*
GUI construction code is labeled with headers for each section,
so the code is searchable by looking for "[section-name]", where
section-name is the title of the GroupBox dispalyed in the GUI.

Example: search "[Chaos Recipe Rares]" to find the code that
builds the chaos recipe rares section of the GUI.
*/

; General AHK boilerplate settings
#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%
SetBatchLines -1  ; Run at full speed (do not sleep every n lines)

; Includes: note that we first include the ahk_include subdirectory
#Include %A_ScriptDir%\ahk_include
#Include backend_interface.ahk
#Include consts.ahk
#Include general_helper.ahk
#Include gui_build.ahk
#Include gui_helper.ahk
#Include gui_interaction.ahk
#Include gui_placeholder.ahk
#Include poe_helper.ahk

; Give script the DLF Icon
Menu, Tray, Icon, %kDlfIconPath%

; ============================= Global Variables =============================

; TODO - Refactor dependent code and remove this
python_command := GetPythonCommand()

; Profiles
g_profiles := []
g_active_profile := ""

; List of backend function calls corresponding to changes that have
; occurred since last filter load or write.
g_ui_changes := []

; Local GUI state data (may contain changes not yet applied to filter).
; See backend_interface.ahk for detailed outline of keys and values.
; Note: for elements whose state is fully contained in the current state of the UI,
; for example Chaos Recipe items, this ui_data_dict will not be updated when UI changes.
; Added by gui_interaction: "matched_rule_tags" -> [type_tag, tier_tag]
g_ui_data_dict := {}

; Run Main then wait for GUI input
Main()
Return

; ============================= Profile Helper Functions =============================

; Returns a flag indicating if there are any valid profiles
InitializeProfiles() {
    global kBackendCliOutputPath
    global g_profiles, g_active_profile
    RunBackendCliFunction("get_all_profile_names")
    g_profiles := ReadFileLines(kBackendCliOutputPath)
    if (Length(g_profiles) == 0) {
        CreateProfile1()
        return False
    }
    g_active_profile := g_profiles[1]
    return True
}

; ============================= To Refactor - Profile Creation =============================

CreateProfile1() {
	; Use global mode so vVariables and HWNDhIdentifiers created here end up global
	global
    Gui, 2: Color, 0x111122
    anchor_x := 8, anchor_y := 8
    h := 28, w := 434, button_w := 70, edit_w := w - button_w - 10
    spacing_y := h + 12
    x := anchor_x, y := anchor_y
    ; Title
    Gui, 2: Font, c0x00e8b2 s15 Bold, Segoe UI
    Gui, 2: Add, Text, x0 y%y% h%h% w%w% +Center, Create New Profile
    ; Profile Name
    y += spacing_y + 8
    Gui, 2: Font, c0x00e8b2 s14 Norm, Segoe UI
    Gui, 2: Add, Text, x%x% y%y% h%h% w%w%, Profile Name
    y += h
    Gui, 2: Font, cBlack s14 Norm, Segoe UI
    Gui, 2: Add, Edit, x%x% y%y% h32 w250 vNewProfileName
    ; Downloaded Filter Path
    y += spacing_y + 4
    Gui, 2: Font, c0x00e8b2 s14 Norm, Segoe UI
    Gui, 2: Add, Text, x%x% y%y% h%h% w%w%, Downloaded Filter Path
    y += h
    Gui, 2: Font, cBlack s12 Norm, Segoe UI
    placeholder_text := "C:\Users\...\Downloads\NeversinkStrict.Filter"
    Gui, 2: Add, Edit, x%x% y%y% h%h% w%edit_w% vNewProfileDownloadedFilterPath HWNDhNewProfileDownloadedFilterEdit, %placeholder_text%
    button_x := x + w - button_w
    Gui, 2: Font, c0x00e8b2 s10 Bold, Segoe UI
    Gui, 2: Add, Button, x%button_x% y%y% h%h% w%button_w% gBrowseDownloadDirectory, Browse
    ; Path of Exile Filters Directory
    y += spacing_y
    Gui, 2: Font, c0x00e8b2 s14 Norm, Segoe UI
    Gui, 2: Add, Text, x%x% y%y% h%h%, Path of Exile Filters Directory
    y += h
    Gui, 2: Font, cBlack s12 Norm, Segoe UI
    placeholder_text := "C:\Users\...\Documents\My Games\Path of Exile"
    Gui, 2: Add, Edit, x%x% y%y% h%h% w%edit_w% vNewProfilePoeFiltersDirectory HWNDhNewProfilePoeFiltersDirectoryEdit, %placeholder_text%
    button_x := x + w - button_w
    Gui, 2: Font, c0x00e8b2 s10 Bold, Segoe UI
    Gui, 2: Add, Button, x%button_x% y%y% h%h% w%button_w% gBrowsePoeDirectory, Browse
    ; Remove Downloaded Filter on Import
    y += spacing_y + 6
    Gui, 2: Font, c0x00e8b2 s14 Norm, Segoe UI
    Gui, 2: Add, Checkbox, vRemoveDownloadedFilter -Checked x%x% y%y% h26 w%w%, Remove downloaded filter on import
    ; Create Button
    y += spacing_y + 10
    Gui, 2: Font, s14 Bold, Segoe UI
    Gui, 2: Add, Button, x145 y%y% w150 h36 gCreateProfile2, Create
    ; Show UI
    Gui, 2: -Border
    Gui, 2: Show, w450 h378
    GUi, 1: Hide
    Return
}

BrowseDownloadDirectory() {
    FileSelectFile, selected_path, , , Select Downloaded Filter, Filter Files (*.filter)
    GuiControl, 2:, NewProfileDownloadedFilterPath, %selected_path%
    return
}

BrowsePoeDirectory() {
    FileSelectFolder, selected_directory, , , Select Path of Exile Filters Directory
    GuiControl, 2:, NewProfilePoeFiltersDirectory, %selected_directory%
    return
}

CreateProfile2() {
    global kBackendCliInputPath
    global NewProfileName, NewProfileDownloadedFilterPath, NewProfilePoeFiltersDirectory, RemoveDownloadedFilter
    Gui, 2: Submit, NoHide
    if (NewProfileName == ""){
        MsgBox, Missing profile name!
        return
    }
    if ((NewProfileDownloadedFilterPath == "") or InStr(NewProfileDownloadedFilterPath, "...")) {
        MsgBox, Missing downloaded filter path!
        return
    }
    if ((NewProfilePoeFiltersDirectory == "") or InStr(NewProfilePoeFiltersDirectory, "...")) {
        MsgBox, Missing Path of Exile filters directory!
        return
    }
    SplitPath, NewProfileDownloadedFilterPath, downloaded_filter_filename, download_directory
    FileDelete, %kBackendCliInputPath%
    FileAppend, % "DownloadDirectory:" download_directory "`n", %kBackendCliInputPath%
    FileAppend, % "DownloadedLootFilterFilename:" downloaded_filter_filename "`n", %kBackendCliInputPath%
    FileAppend, % "PathOfExileDirectory:" NewProfilePoeFiltersDirectory "`n", %kBackendCliInputPath%
    if (!RemoveDownloadedFilter){
        FileAppend, % "RemoveDownloadedFilter:False`n", %kBackendCliInputPath%

    }
    Gui, 2: Destroy
    backend_cli_command := "create_new_profile " NewProfileName
    exit_code := RunBackendCliFunction("create_new_profile " NewProfileName)
    if (exit_code != 0){
        UpdateStatusMessage("Profile Creation Failed")
    }
    Reload
}

2GuiEscape() {
    2GuiClose()
}

2GuiClose() {
    Gui, 2: Destroy
    Gui, 1: Show
    return
}

; Minimize the GUI on Escape
GuiEscape() {
    WinMinimize, A
}

GuiClose() {
    ExitApp
}

; ============================= Main Thread =============================

Main() {
    global g_ui_data_dict, g_active_profile
    profiles_exist_flag := InitializeProfiles()
    ; If no profiles exist, return from this thread and wait for profile creation GUI
    if (!profiles_exist_flag) {
        return
    }
    g_ui_data_dict := QueryAllFilterData(g_active_profile)
    QueryHotkeys(g_ui_data_dict)
    BuildGui(g_ui_data_dict)
}

; ================================== Hotkeys ==================================

; Toggle GUI
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
ToggleGUIHotkey() {  ; $toggle_gui_hotkey_line
    if (IsPoeActive()) {
        MakeDlfActive()
    } else if (IsDlfActive()) {
        MakePoeActive()
    }
}

; Write Filter
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
WriteFilterHotkey() {  ; $write_filter_hotkey_line
    UpdateFilter()
}

; Reload Filter
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
ReloadFilterHotkey() {  ; $reload_filter_hotkey_line
    if (IsPoeActive()) {
        SendChatMessage("/itemfilter DynamicLootFilter")
    }
}

; For efficient testing
Numpad0::Reload