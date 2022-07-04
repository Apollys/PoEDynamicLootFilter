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

InitializeProfiles() {
    global kBackendCliOutputPath
    global g_profiles, g_active_profile
    RunBackendCliFunction("get_all_profile_names")
    g_profiles := ReadFileLines(kBackendCliOutputPath)
    if (g_profiles.Length() == 0) {
        MsgBox, % "No existing profiles found. Create a profile here, or run setup.py to get started"
        CreateProfile1()
    }
    g_active_profile := g_profiles[1]
}

; ============================= To Refactor - Profile Creation =============================

CreateProfile1() {
    Gui, 2: Color, 0x111122
    Gui, 2: Font, c0x00e8b2 s16 Bold, Segoe UI
    Gui, 2: Add, Text, x8 y8 h26 +0x200, Profile Name
    Gui, 2: Add, Text, x8 y68 h26 +0x200, Downloaded Filter Directory
    Gui, 2: Add, Text, x8 y128 h26 +0x200, Downloaded Filter Name
    Gui, 2: Add, Text, x8 y188 h26 +0x200, Path of Exile Filter Directory
    Gui, 2: Add, Text, x8 y248 h26 +0x200, Output Filter Name
    Gui, 2: Font, s14, Segoe UI
    Gui, 2: Add, Checkbox, vRDF checked x8 y309 h26,
    Gui, 2: Add, Text, x28 y308 h26 w400, Remove Downloaded Filter on Import

    Gui, 2: Font, s12 norm cblack, Segoe UI
    Gui, 2: Add, Edit, x8 y38 h26 w434 vNewProfileName,
    Gui, 2: Add, Edit, x8 y98 h26 w434 vNewProfileDDir, C:\Users\...\Downloads
    Gui, 2: Add, Edit, x8 y158 h26 w434 vNewProfileDName,
    Gui, 2: Add, Edit, x8 y218 h26 w434 vNewProfilePoEDir, C:\Users\...\Documents\My Games\Path of Exile
    Gui, 2: Add, Edit, x8 y278 h26 w434 vNewProfilePoEName, (Optional)


    Gui, 2: Font, s14 Bold, Segoe UI
    Gui, 2: Add, Button, x163 y338 w124 h31 gCreateProfile2, Create
    Gui, 2: Show, w450 h378, PoE Dynamic Loot Filter
    Return
}

CreateProfile2() {
    Gui, 2: Submit, NoHide
    ; Erase backend_cli.input before writing
    FileAppend, abc, %kBackendCliInputPath%
    FileDelete, %kBackendCliInputPath%
    if (NewProfileName == ""){
        MsgBox, Profile Name Required!
        return
    }
    if (NewProfileDDir == ""){
        MsgBox, Downloads Directory Required!
        return
    }
    if (NewProfileDName == ""){
        MsgBox, Downloaded Filter Filename Required!
        return
    }
    if (NewProfilePoEDir == ""){
        MsgBox, Path of Exile Filter Directory Required!
        return
    }
    FileAppend, % "DownloadDirectory:" NewProfileDDir "`n" , %kBackendCliInputPath%
    FileAppend, % "PathOfExileDirectory:" NewProfilePoEDir "`n" , %kBackendCliInputPath%
    FileAppend, % "DownloadedLootFilterFilename:" NewProfileDName "`n", %kBackendCliInputPath%
    if (NewProfilePoEName != "(Optional)" and NewProfilePoEName != ""){
        FileAppend, % "OutputLootFilterFilename:" NewProfilePoEName "`n", %kBackendCliInputPath%
    }
    if (!RDF){
        FileAppend, % "RemoveDownloadedFilter:False`n", %kBackendCliInputPath%

    }
    Gui, 2: Destroy
    RunWait, %python_command% %kBackendCliPath% create_new_profile %NewProfileName%,  , Hide
    FileRead, exit_code, %kBackendCliExitCodePath%
    if (exit_code == "1"){
        GuiControl, , GUIStatusMsg , % "Profile Creation Failed"
        FileRead, error_log, %kBackendCliLogPath%
        MsgBox, % "Python backend_cli.py encountered error:`n" error_log
    }
    else if (exit_code == "-1")
        MsgBox, How did you get here?
    RunWait, %python_command% %kBackendCliPath% import_downloaded_filter %NewProfileName%,  , Hide
    FileRead, exit_code, %kBackendCliExitCodePath%
    if (exit_code == "1"){
        GuiControl, , GUIStatusMsg , % "Filter Import Failed"
        FileRead, error_log, %kBackendCliLogPath%
        MsgBox, % "Python backend_cli.py encountered error:`n" error_log
    }
    else if (exit_code == "-1")
        MsgBox, How did you get here?
    Reload
    ExitApp
}

2GuiClose() {
    Gui, 2: Destroy
    return
}

GuiEscape() {
    GuiClose()
}

GuiClose() {
    ExitApp
}

; ============================= Main Thread =============================

Main() {
    global g_ui_data_dict, g_active_profile
    InitializeProfiles()
    g_ui_data_dict := QueryAllFilterData(g_active_profile)
    QueryHotkeys(g_ui_data_dict)
    BuildGui(g_ui_data_dict)
}

; ================================== Hotkeys ==================================

; Toggle GUI
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
F7::  ; $toggle_gui_hotkey_line
    if (IsPoeActive()) {
        MakeDlfActive()
    } else if (IsDlfActive()) {
        MakePoeActive()
    }
    return

; Write Filter
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
F8::  ; $write_filter_hotkey_line
    UpdateFilter()
    return

; Reload Filter
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
F9::  ; $reload_filter_hotkey_line
    if (IsPoeActive()) {
        SendChatMessage("/itemfilter DynamicLootFilter")
    }
    return

; For efficient testing
Numpad0::Reload