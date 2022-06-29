/*
GUI construction code is labeled with headers for each section,
so the code is searchable by looking for "[section-name]", where
section-name is the title of the GroupBox dispalyed in the GUI.

Example: search "[Chaos Recipe Rares]" to find the code that
builds the chaos recipe rares section of the GUI.
*/

#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%
SetBatchLines -1

Menu, Tray, Icon, DLF_icon.ico

; ---------------- Global Constants ----------------

; GUI window parameters
kWindowWidth := 1470
kWindowHeight := 866
kWindowTitle := "PoE Dynamic Loot Filter"

; Paths for backend cli target, input, and output
kBackendCliPath := "backend_cli.py"
kBackedCliOutputPath := "backend_cli.output"
kBackendCliLogPath := "backend_cli.log"
; TODO: This shouldn't be necessary, just get return code directly
kBackendCliExitCodePath := "backend_cli.exit_code"
kBackendCliInputPath := "backend_cli.input"

; Flask BaseTypes
kFlaskBaseTypesPath := "Resources/flask_base_types.txt"
kFlaskBaseTypesList := ReadFileLines(kFlaskBaseTypesPath)
; Splinter BaseTypes
kSplinterBaseTypesPath := "Resources/splinter_base_types.txt"
kSplinterBaseTypesList := ReadFileLines(kSplinterBaseTypesPath)

; ---------------- Global Variables ----------------

; List of backend function calls corresponding to changes that have
; occurred since last filter load or write.
g_general_basetypes_changes := []
g_flask_basetypes_changes := []
g_socket_patterns_changes := []
g_splinter_changes := []

; ---------------- General Helper Functions ----------------
DebugMessage(message) {
    MsgBox, , Debug Message, %message%
}

Quoted(s) {
    quote := """"
    return quote s quote
}

StartsWith(s, prefix) {
    return (SubStr(s, 1, StrLen(prefix)) == prefix)
}

StringJoin(list, delimeter) {
    result_string := ""
    for i, s in list {
        if (i > 1) {
            result_string := result_string delimeter
        }
        result_string := result_string s
    }
    return result_string
}

; Takes either a GUI element variable ("vMyGuiElement") or
; an HWND id ("HWNDhMyGuiElement"), and calls GuiGetControl
; with the appropriate syntax.
GuiControlGetHelper(id, warn_empty_output:=False) {
    StringLower, id, id
    output_value := ""
    ; For Gui variables, GuiControlGet does not require percent signs
    if (StartsWith(id, "v")) {
        variable_name := SubStr(id, 2)  ; trim starting "v"
        GuiControlGet output_value, , %variable_name%
    }
    ; For HWND ids, GuiControlGet does require percent signs
    else if (StartsWith(id, "hwnd")) {
        hwnd_id_name := SubStr(id, 5)  ; trim starting "hwnd"
        GuiControlGet output_value, , % %hwnd_id_name%
    }
    ; If no specific prefix, assume it's just a pre-trimmed variable name
    else {
        GuiControlGet output_value, , %variable_name%
    }
    ; Check if output is empty for debugging purposes
    if (warn_empty_output and (output_value == "")) {
        DebugMessage("Warning: output of GuiControlGetHelper(" id ") is empty")
    }
    return output_value
}

; Returns an array of strings containing the lines in the file (newlines removed)
ReadFileLines(filepath) {
    FileRead, file_contents, %filepath%
    return StrSplit(file_contents, "`r`n")
}

; Runs the given command in a hidden window, waits for it to complete,
; and then returns the received exit code: 0 = success, nonzero = failure.
RunCommand(command_string) {
    ; ComSpec contains the path to the command-line exe
    ; The "/c" parameter tells cmd to run the command, then exit (otherwise it would never exit)
    RunWait, % ComSpec " /c " command_string,  , Hide UseErrorLevel
    return ErrorLevel
}

; TODO: use GetPythonCommand() once below code is refactored
; For now, assumes the variable python_command contains the command
; to run the backend cli.
RunBackendCliFunction(function_call_string) {
    global python_command, kBackendCliLogPath
    exit_code := RunCommand(python_command " function_call_string")
    ; Handle nonzero exit code
    if (exit_code != "0") {
        FileRead, error_log, %kBackendCliLogPath%
        MsgBox, % "Python backend_cli.py encountered error:`n" error_log
    }
    return exit_code
}

; ---------------- PYTHON VERSION AND PATH CHECKING ----------------
; TODO: refactor as function GetPythonCommand
DeterminePythonCommand:
kPythonCommandTxtPath := "cache/python_command.txt"
FileRead, python_command, %kPythonCommandTxtPath%
If (python_command == ""){
    python_version_output_path := "python_version_output.txt"
    ; ComSpec contains the path to the command-line exe
    ; The "/c" parameter tells cmd to run the command, then exit (otherwise it would never exit)
    RunCommand("python --version > " python_version_output_path)
    FileRead, python_version_output, %python_version_output_path%
    if(SubStr(python_version_output, 1, 7) == "Python " and SubStr(python_version_output, 1, 8) >= 3){
        python_command := "python"
    }
    else{
        FileDelete, python_version_output.txt
        RunWait, %ComSpec% /c "py --version >python_version_output.txt" ,  , Hide
        FileRead, python_version_output, python_version_output.txt
        if(SubStr(python_version_output, 1, 7 ) == "Python " and SubStr(python_version_output, 1, 8) >= 3){
            python_command := "py"
        }
        else{
            FileDelete, python_version_output.txt
            RunWait, %ComSpec% /c "python3 --version >python_version_output.txt" ,  , Hide
            FileRead, python_version_output, python_version_output.txt
            if(SubStr(python_version_output, 1, 7) == "Python " and SubStr(python_version_output, 1, 8) >= 3){
                python_command := "python3"
            }
            else{
                MsgBox,  Error: The commands "python", "py", and "python3" were all unable to launch Python 3. Either Python 3 is not installed, Python 3 is not in the path, or the commands are aliased to other programs.
                FileDelete, python_version_output.txt
                ExitApp
            }
        }
    }
    FileDelete, python_version_output.txt
    FileAppend, %python_command%, %kPythonCommandTxtPath%
}
else{
    RunWait, %ComSpec% /c "%python_command% --version >python_version_output.txt" ,  , Hide
    FileRead, python_version_output, python_version_output.txt
    if(SubStr(python_version_output, 1, 7) != "Python " or SubStr(python_version_output, 8, 1) < 3){
        FileDelete, %kPythonCommandTxtPath%
        FileDelete, python_version_output.txt
        goto, DeterminePythonCommand
    }
    FileDelete, python_version_output.txt
}

; ---------------- DATA STORAGE INITIALIZATION ----------------

; Coloring for rares by slot (item slots copied from consts.py)
kChaosRecipeItemSlotToColorMap := {"Weapons" : "c80000", "Body Armours" : "ff00ff", "Helmets" : "ff7200"
    , "Gloves" : "ffe400", "Boots" : "00ff00", "Amulets" : "00ffff", "Rings" : "4100bd"
    , "Belts" : "0000c8"}

; RGB size tooltips
rgbtooltip := {"none" : "Hide everything", "small" : "2x2, 4x1, and 3x1"
    , "medium" : "3x2, 2x2, 4x1, and 3x1", "large" : "Show everything"}
rgbmap := {"none" : 1, "small" : 2, "medium" : 3, "large" : 4}
rgbmap_reversed := {1 : "none", 2: "small", 3: "medium", 4: "large"}

; Oil names, ordered from highest to lowest value
kOilBaseTypes := ["Tainted", "Golden", "Silver", "Opalescent", "Black", "Crimson", "Violet", "Indigo"
    , "Azure", "Teal", "Verdant", "Amber", "Sepia", "Clear"]

; Currency stack size options
cstack_input_dict := {1:1, 2:2, 4:3, 100:4}
cstack_input_dict_low := {1:1, 2:2, 4:3, 6:4, 100:5}
cstack_output_dict := {1:1, 2:2, 3:4, 4:100}
cstack_output_dict_low := {1:1, 2:2, 3:4, 4:6, 5:100}
cstack_options := ["1+", "2+", "4+", "6+", "Ø"]
cstack_values := [5, 5, 5, 5, 5, 5, 5, 5, 5]

; Load profiles from python client
profiles := []
FileDelete, %kBackendCliInputPath%
RunWait, %python_command% %kBackendCliPath% get_all_profile_names, , Hide
FileRead, exit_code, %kBackendCliExitCodePath%
if (exit_code == "1"){
    FileRead, error_log, %kBackendCliLogPath%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
FileRead, py_out_text, %kBackedCliOutputPath%
Loop, parse, py_out_text, `n, `r
{
    if(A_LoopField = "")
        continue
    profiles.push(A_LoopField)
}
active_profile := profiles[1]

if (active_profile == ""){
    MsgBox, No existing profiles found. Create a profile here, or run setup.py to get started
    goto, CreateProfile1
}

; ---------------- DATA LOADING ----------------
; Read starting filter data from python client
; REWRITE --------------------------------
curr_txt := []
curr_val := []
curr_val_start := []
; REWRITE ---------------------------
all_currency := ""
rare_dict := {"Weapons" : 1, "Body Armours" : 1, "Helmets" : 1, "Gloves" : 1, "Boots" : 1, "Amulets" : 1, "Rings" : 1, "Belts" : 1}
rare_GUI_ids := {"Weapons" : "Rare1", "Body Armours" : "Rare2", "Helmets" : "Rare3", "Gloves" : "Rare4", "Boots" : "Rare5", "Amulets" : "Rare6", "Rings" : "Rare7", "Belts" : "Rare8"}
fake_queue := []

; Build batch file to get all info
FileAppend, get_all_currency_tiers`nget_all_chaos_recipe_statuses`nget_hide_maps_below_tier`nget_currency_tier_min_visible_stack_size tportal`nget_currency_tier_min_visible_stack_size twisdom`nget_hide_essences_above_tier`nget_hide_unique_items_above_tier`nget_gem_min_quality`nget_rgb_item_max_size`nget_flask_min_quality`nget_lowest_visible_oil`n, %kBackendCliInputPath%
Loop, 9
{
    FileAppend, get_currency_tier_min_visible_stack_size %A_Index%`n, %kBackendCliInputPath%
}
FileAppend, get_hide_div_cards_above_tier`nget_hide_unique_maps_above_tier`n, %kBackendCliInputPath%
for key in kFlaskBaseTypeToVisibilitiesMap
{
    FileAppend, get_flask_visibility "%key%"`r`n, %kBackendCliInputPath%
    fake_queue.Push(key)
}

; Load all filter data from backend client
status_msg := "Filter Loaded Succesfully"
RunWait, %python_command% %kBackendCliPath% run_batch %active_profile%, , Hide
FileRead, exit_code, %kBackendCliExitCodePath%
if (exit_code == "1"){
    status_msg := "Filter Load Failed"
    FileRead, error_log, %kBackendCliLogPath%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
FileRead, py_out_text, %kBackedCliOutputPath%

; Parse batch output
prog := 0
Loop, parse, py_out_text, `n, `r
{
    if(A_LoopField = "")
        continue
    if(InStr(A_LoopField, "@"))
    {
        line := 0
        prog := prog + 1
        continue
    }
    Switch prog
    {
    Case 0:
        splits := StrSplit(A_LoopField, ";")
        curr_txt.Push(splits[1])
        curr_val.Push(splits[2])
        curr_val_start.Push(splits[2])
        all_currency .= splits[1] "|"
    Case 1:
        splits := StrSplit(A_LoopField, ";")
        rare_dict[splits[1]] := splits[2]
    Case 2:
        maphide := A_LoopField
    Case 3:
        portal_stack := cstack_input_dict_low[A_LoopField]
    Case 4:
        wisdom_stack := cstack_input_dict_low[A_LoopField]
    Case 5:
        esshide := A_LoopField
    Case 6:
        uniqhide := A_LoopField
    Case 7:
        gemmin := A_LoopField == -1? 21 : A_LoopField
    Case 8:
        rgbsize := A_LoopField
    Case 9:
        flaskmin := A_LoopField == -1? 21 : A_LoopField
    Case 10:
        oil_text := StrSplit(A_LoopField, " ")
        min_oil := -1
        for idx, val in kOilBaseTypes
        {
            if (val = oil_text[1])
                min_oil := idx
        }
    Case 11, 12, 13, 14, 15, 16, 17:
        cstack_values[prog-10] := cstack_input_dict[A_LoopField]
    Case 18, 19:
        cstack_values[prog-10] := cstack_input_dict_low[A_LoopField]
    Case 20:
        divmin := A_LoopField
    Case 21:
        unique_mapmin := A_LoopField
    Default:
        splits := StrSplit(A_LoopField, " ")
        kFlaskBaseTypeToVisibilitiesMap[fake_queue[prog - 21]] := [0,0]
        kBaseFlaskBaseTypeToVisibilitiesMap[fake_queue[prog - 21]] := [0,0]
        if (splits[1] = 1)
        {
            kFlaskBaseTypeToVisibilitiesMap[fake_queue[prog - 21]][1] := 1
            kBaseFlaskBaseTypeToVisibilitiesMap[fake_queue[prog - 21]][1] := 1
        }
        if (splits[2] = 1)
        {
            kFlaskBaseTypeToVisibilitiesMap[fake_queue[prog - 21]][2] := 1
            kBaseFlaskBaseTypeToVisibilitiesMap[fake_queue[prog - 21]][2] := 1
        }
    }
}

; Source: https://www.autohotkey.com/board/topic/72535-fnl-placeholder-placeholder-text-for-edit-controls/
;
; Placeholder() - by infogulch for AutoHotkey v1.1.05+
;
; to set up your edit control with a placeholder, call:
;   Placeholder(hwnd_of_edit_control, "your placeholder text")
;
; If called with only the hwnd, the function returns True if a
;   placeholder is being shown, and False if not.
;   isPlc := Placeholder(hwnd_edit)
;
; to remove the placeholder call with a blank text param
;   Placeholder(hwnd_edit, "")
;
; http://www.autohotkey.com/forum/viewtopic.php?p=482903#482903
;

Placeholder(wParam, lParam = "`r", msg = "") {
    static init := OnMessage(0x111, "Placeholder"), list := []

    if (msg != 0x111) {
        if (lParam == "`r")
            return list[wParam].shown
        list[wParam] := { placeholder: lParam, shown: false }
        if (lParam == "")
            return "", list.remove(wParam, "")
        lParam := wParam
        wParam := 0x200 << 16
    }
    if (wParam >> 16 == 0x200) && list.HasKey(lParam) && !list[lParam].shown ;EN_KILLFOCUS  :=  0x200
    {
        GuiControlGet, text, , %lParam%
        if (text == "")
        {
            ; Font line modified from original source to match UI
            Gui, Font, Ca0a0a0 s11 Norm, Segoe UI
            GuiControl, Font, %lParam%
            GuiControl,     , %lParam%, % list[lParam].placeholder
            list[lParam].shown := true
        }
    }
    else if (wParam >> 16 == 0x100) && list.HasKey(lParam) && list[lParam].shown ;EN_SETFOCUS := 0x100
    {
        Gui Font, c0xe3fff9 s11 Norm, Segoe UI  ; Modified from original source to match UI
        GuiControl, Font, %lParam%
        GuiControl,     , %lParam%
        list[lParam].shown := false
    }
}

; Example:
; Gui, Add, Edit, w300 hwndhEdit
; Gui, Add, Edit, wp r4 hwndhEdit2
; Placeholder(hEdit, "Enter some text")
; Placeholder(hEdit2, "Another text entry point")

; ----------- GUI CREATION / REBUILD -------------------
; Some Parts of GUI Generated by Auto-GUI 3.0.1

GuiBuild:
; ------------- Precomputation -------------
; Currency data
currtexts := ["", "", "", "", "", "", "", "", ""]
For idx in curr_txt {
    currtexts[curr_val[idx]] .= curr_txt[idx] "|"
}
Loop, 9 {
    currtexts[A_Index] := RegExReplace( currtexts[A_Index], "\|$" )
}
cstacktext := ""
cstacktext_less := ""
Loop, 5 {
    cstacktext .= cstack_options[A_Index] "|"
    if (A_Index != 4) {
        cstacktext_less .= cstack_options[A_Index] "|"
    }
}
cstacktext := RegExReplace( cstacktext, "\|$" )
; Less excludes 6-stacks for larger currencies which can only support 1,2,4, or none
cstacktext_less := RegExReplace( cstacktext_less, "\|$" )

; Profile data
for key, val in profiles
    ProfString .= val "|"
RTrim(ProfString, "|")

; Oil data
oilstr := ""
for key, val in kOilBaseTypes {
    oilstr .= val "|"
}
RTrim(oilstr, "|")
; ------------- End Precomputation -------------

; ------------- GUI Construction (Build GUI) Start -------------
; Set color themes
Gui Color, 0x111122, 0x111133
; Title
Gui Font, c0x00e8b2 s16 Bold, Segoe UI
Gui Add, Text, x192 y8 w556 h26 +0x200 +Center, PoE Dynamic Loot Filter

; ------------- Section: Profiles ------------
anchor_x := 1140, anchor_y := 12
Gui Font, c0x00e8b2 s14 Bold, Segoe UI
Gui Add, Text, x%anchor_x% y%anchor_y% w66 h36 +0x200, Profile:
; DropDownList
Gui Font, c0x00e8b2 s14 Norm, Segoe UI
x := anchor_x + 72, y := anchor_y + 0
Gui Add, DropDownList, x%x% y%y% w151 h36 gChangeProfile vProfileDDL Choose1, %ProfString%
; Create Button
Gui Font, c0x00e8b2 s14 Bold, Segoe UI
x := anchor_x + 232, y := anchor_y + 0
Gui Add, Button, x%x% y%y% w80 h34 gCreateProfile1, Create
; ------------- End Section: Profiles -------------

; ------------- Section: [Currency] -------------
anchor_x := 16, anchor_y := 48
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w484 h806, Currency
; Dividing lines
x := anchor_x + 8, y := anchor_y + 76
Gui Add, Text, x%x% y%y% w468 h0 +0x10  ; horizontal line above row 1
x := anchor_x + 8, y := anchor_y + 284
Gui Add, Text, x%x% y%y% w468 h0 +0x10  ; horizontal line between rows 1 and 2
x := anchor_x + 8, y := anchor_y + 492
Gui Add, Text, x%x% y%y% w468 h0 +0x10  ; horizontal line between rows 2 and 3
x := anchor_x + 8, y := anchor_y + 703
Gui Add, Text, x%x% y%y% w468 h0 +0x10  ; horizontal line above portal/wisdom scrolls
x := anchor_x + 162, y := anchor_y + 78
Gui Add, Text, x%x% y%y% w0 h628 +0x1 +0x10  ; vertical line between columns 1 and 2
x := anchor_x + 322, y := anchor_y + 78
Gui Add, Text, x%x% y%y% w0 h628 +0x1 +0x10  ; vertical line between column 2 and 3
x := anchor_x + 240, y := anchor_y + 705
Gui Add, Text, x%x% y%y% w0 h47 +0x1 +0x10  ; vertical line between portal/wisdom scrolls
; Find and move currency
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 60, y := anchor_y + 32
Gui Add, DropDownList, x%x% y%y% w270 +Sort gCurrencyFindDDL vFindCurrTier_in HWNDhFindCurrencyDdl, Select Currency Type...||%all_currency%
;Gui Font, c0x00e8b2 s11 Norm, Segoe UI
;x := anchor_x + 285, y := anchor_y + 33
;Gui Add, Edit, x%x% y%y% w36 h26 +0x200 vFindCurrTier_out +ReadOnly, T#
;Gui Font, c0x00e8b2 s11 Norm, Segoe UI
;x := anchor_x + 335, y := anchor_y + 33
;Gui Add, Text, x%x% y%y% w60 h26 +0x200, Move to:
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 344, y := anchor_y + 33
Gui Add, Text, x%x% y%y% w36 h26 +0x200, -->
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 375, y := anchor_y + 32
Gui Add, DropDownList, x%x% y%y% w43 gCurrencyMoveTier vCurrencyMoveTier_tier, T#||T1|T2|T3|T4|T5|T6|T7|T8|T9
; Tier blocks
tier_anchor_x := anchor_x + 16
tier_anchor_y := anchor_y + 84
tier_horizontal_spacing := 160
tier_vertical_spacing := 208
Loop 9 {
    tier := A_Index  ; A_Index starts at 1
    ; Positioning computations
    row_i := Mod(tier - 1, 3)
    col_i := (tier - 1) // 3
    loop_anchor_x := tier_anchor_x + row_i * tier_horizontal_spacing
    loop_anchor_y := tier_anchor_y + col_i * tier_vertical_spacing
    ; GUI elements
    Gui Font, c0x00e8b2 s11 Norm, Segoe UI
    x := loop_anchor_x + 0, y := loop_anchor_y + 0
    Gui Add, Text, x%x% y%y% w115 h28 +0x200, T%tier% Stack Size:
    x := loop_anchor_x + 92, y := loop_anchor_y + 0
    Gui Add, DropDownList, % "+AltSubmit vValueCurrencyDdlT" tier " x" x " y" y " w44 Choose"cstack_values[tier],  %cstacktext_less%
    Gui Font, c0x00e8b2 s10
    x := loop_anchor_x + 0, y := loop_anchor_y + 32
    Gui Add, ListBox, x%x% y%y% w135 h164 +Sort gCurrencyListBoxItemSelectedT%tier% vCurrTexts%tier% HWNDhCurrencyTierBoxT%tier%, % currtexts[tier]
}
; Portal scrolls
Gui Font, c0x00e8b2 s11, Segoe UI
x := anchor_x + 40, y := anchor_y + 711
Gui Add, Text, x%x% y%y% w115 h28 +0x200, Portal Stack Size:
x := anchor_x + 160, y := anchor_y + 711
Gui Add, DropDownList, +AltSubmit vValueCurrencyDdlTportal Choose%portal_stack% x%x% y%y% w48, % cstacktext
; Wisdom scrolls
Gui Font, c0x00e8b2 s11, Segoe UI
x := anchor_x + 272, y := anchor_y + 711
Gui Add, Text, x%x% y%y% w133 h28 +0x200, Wisdom Stack Size:
x := anchor_x + 408, y := anchor_y + 711
Gui Add, DropDownList, +AltSubmit vValueCurrencyDdlTwisdom Choose%wisdom_stack% x%x% y%y% w48, % cstacktext
; ------------- End Section: [Currency] -------------

; ------------- Section: [Splinter Stack Sizes] ------------
anchor_x := 20, anchor_y := 790
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w476 h60, Splinter Stack Sizes
; Splinter BaseType DDL (items roughly in order from least to most valuable, but grouped by legion/breach)
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 28, y := anchor_y + 24
Gui Add, DropDownList, x%x% y%y% w240 HWNDhSplinterTypeDdl, % "Select Splinter Type...||"StringJoin(kSplinterBaseTypesList, "|")
; Stack Size DDL
x := anchor_x + 272, y := anchor_y + 24
Gui Add, DropDownList, x%x% y%y% w48 HWNDhSplinterStackSizeDdl, 1+||2+|4+|8+
; Apply Button
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 350, y := anchor_y + 25
Gui Add, Button, x%x% y%y% w100 h26 gSplinterStackSizesApply, Apply
; ------------- End Section: [Splinter Stack Sizes] ------------

; ------------- Section: [Chaos Recipe Rares] -------------
anchor_x := 528, anchor_y := 48
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h169, Chaos Recipe Rares
; CheckBoxes
Gui Font, c0x00e8b2 s14 Norm, Segoe UI
x := anchor_x + 16, y := anchor_y + 32
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Weapons"] " " (rare_dict["Weapons"]? " Checked" : ""), Weapons
x := anchor_x + 16, y := anchor_y + 64
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Body Armours"] " "  (rare_dict["Body Armours"]? " Checked" : ""), Armours
x := anchor_x + 16, y := anchor_y + 96
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Helmets"] " "  (rare_dict["Helmets"]? " Checked" : ""), Helmets
x := anchor_x + 16, y := anchor_y + 128
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Gloves"] " "  (rare_dict["Gloves"]? " Checked" : ""), Gloves
x := anchor_x + 152, y := anchor_y + 32
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Boots"] " "  (rare_dict["Boots"]? " Checked" : ""), Boots
x := anchor_x + 152, y := anchor_y + 64
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Belts"] " "  (rare_dict["Belts"]? " Checked" : ""), Belts
x := anchor_x + 152, y := anchor_y + 96
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Rings"] " "  (rare_dict["Rings"]? " Checked" : ""), Rings
x := anchor_x + 152, y := anchor_y + 128
Gui Add, CheckBox, % "x" x " y" y " w123 h26 v" rare_GUI_ids["Amulets"] " "  (rare_dict["Amulets"]? " Checked" : ""), Amulets
; ------------- End Section: [Chaos Recipe Rares] -------------

; ------------- Section: [Hide Maps Below Tier] -------------
anchor_x := 528, anchor_y := 233
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h74, Regular Maps
; Text
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 16, y := anchor_y + 32
Gui Add, Text, x%x% y%y% w152 h28 +0x200, Hide Maps Below Tier:
; Edit & UpDown
x := anchor_x + 172, y := anchor_y + 32
Gui Add, Edit, x%x% y%y% w50 h28 vmaphideUD,
x := anchor_x + 214, y := anchor_y + 32
Gui Add, UpDown, x%x% y%y% w20 h28 Range0-17, % maphide
; ------------- End Section: [Hide Maps Below Tier] -------------

; ------------- Section: [General BaseTypes] ------------
anchor_x := 528, anchor_y := 323
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h256, General BaseTypes
; DDL
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 18, y := anchor_y + 36
Gui Add, Edit, x%x% y%y% w250 HWNDhGeneralBaseTypesEditBox
Placeholder(hGeneralBaseTypesEditBox, "Enter BaseType...")
; High ilvl checkbox and Add button
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 20, y := anchor_y + 68
Gui Add, CheckBox, x%x% y%y% h26 HWNDhGeneralBaseTypesRareCheckBox, Rare items only
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 202, y := anchor_y + 68
Gui Add, Button, x%x% y%y% w66 h26 gGeneralBaseTypesAdd, Add
; Text box and Remove button
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 14, y := anchor_y + 102
Gui Add, ListBox, x%x% y%y% w257 h110 HWNDhGeneralBaseTypesListBox +Sort AltSubmit
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 68, y := anchor_y + 212
Gui Add, Button, x%x% y%y% w144 h31 gGeneralBaseTypesRemove, Remove Selected
; ------------- End Section: [General BaseTypes] ------------

; ------------- Section: [Flask BaseTypes] ------------
anchor_x := 528, anchor_y := 595
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h236, Flask BaseTypes
; DDL
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 18, y := anchor_y + 36
Gui Add, DropDownList, x%x% y%y% w250 HWNDhFlaskDdl +Sort, % "Select Flask Type...||"StringJoin(kFlaskBaseTypesList, "|")
; High ilvl checkbox and Add button
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 20, y := anchor_y + 68
Gui Add, CheckBox, x%x% y%y% h26 HWNDhFlaskHighIlvlCheckBox, High ilvl (84+) only
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 202, y := anchor_y + 68
Gui Add, Button, x%x% y%y% w66 h26 gFlaskAdd, Add
; Text box and Remove button
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 14, y := anchor_y + 102
Gui Add, ListBox, x%x% y%y% w257 h90 HWNDhFlaskListBox +Sort, %flask_low%
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 68, y := anchor_y + 192
Gui Add, Button, x%x% y%y% w144 h31 gFlaskRemove, Remove Selected
; ------------- End Section: [Flask BaseTypes] ------------

; ------------- Section: [Tier Visibility] -------------
anchor_x := 844, anchor_y := 48
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h234, Tier Visibility
; Essences
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 16, y := anchor_y + 32
Gui Add, Text, x%x% y%y% w179 h28 +0x200, Hide Essences Below:
Gui Font, s10
x := anchor_x + 162, y := anchor_y + 34
Gui Add, DropDownList, +AltSubmit x%x% y%y% w111 vesshideDDL Choose%esshide%, T7 (Deafening)|T6 (Shrieking)|T5 (Screaming)|T4 (Wailing)|T3 (Weeping)|None
; Divination cards (variable name: divmin)
Gui Font, s11
x := anchor_x + 16, y := anchor_y + 72
Gui Add, Text, x%x% y%y% w185 h28 +0x200, Hide Div Cards Above Tier:
x := anchor_x + 200, y := anchor_y + 72
Gui Add, DropDownList, +AltSubmit x%x% y%y% w33 vdivminDDL Choose%divmin%, 1|2|3|4|5|6|7|8
; Unique items (variable name: uniqhide)
x := anchor_x + 16, y := anchor_y + 112
Gui Add, Text, x%x% y%y% w203 h28 +0x200, Hide Unique Items Above Tier:
x := anchor_x + 224, y := anchor_y + 112
Gui Add, DropDownList, +AltSubmit x%x% y%y% w33 vuniqhideDDL Choose%uniqhide%, 1|2|3|4|5
; Unique maps (variable name: unique_maphide)
x := anchor_x + 16, y := anchor_y + 152
Gui Add, Text, x%x% y%y% w206 h28 +0x200, Hide Unique Maps Above Tier:
x := anchor_x + 224, y := anchor_y + 152
Gui Add, DropDownList, +AltSubmit x%x% y%y% w33 vunique_mapminDDL Choose%unique_mapmin%, 1|2|3|4
; Oils (variable name: min_oil)
x := anchor_x + 16, y := anchor_y + 192
Gui Add, Text, x%x% y%y% w113 h28 +0x200, Hide Oils Below:
x := anchor_x + 130, y := anchor_y + 192
Gui Add, DropDownList, +AltSubmit x%x% y%y% w130 vmin_oilDDL Choose%min_oil%, %oilstr%
; ------------- End Section: [Tier Visibility] -------------

; ------------- Section: [Quality and RGB Items] ------------
anchor_x := 844, anchor_y := 298
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h152, Quality and RGB Items
; Quality gems
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 16, y := anchor_y + 32
Gui Add, Text, x%x% y%y% w120 h28 +0x200, Gem Min Quality:
x := anchor_x + 136, y := anchor_y + 32
Gui Add, Edit, x%x% y%y% w50 h28 vgemminUD,
x := anchor_x + 178, y := anchor_y + 32
Gui Add, UpDown, x%x% y%y% w20 h28 Range0-21, % gemmin
; Quality flasks
x := anchor_x + 16, y := anchor_y + 72
Gui Add, Text, x%x% y%y% w120 h28 +0x200, Flask Min Quality:
x := anchor_x + 136, y := anchor_y + 72
Gui Add, Edit, x%x% y%y% w50 h28 vflaskminUD,
x := anchor_x + 178, y := anchor_y + 72
Gui Add, UpDown, x%x% y%y% w20 h28 Range0-21, % flaskmin
; RGB items
x := anchor_x + 16, y := anchor_y + 112
Gui Add, Text, x%x% y%y% w136 h28 +0x200, RGB Max Item Size:
x := anchor_x + 152, y := anchor_y + 112
Gui Add, DropDownList,% "+AltSubmit x" x " y" y " w113 vrgbsizeDDL Choose" rgbmap[rgbsize], Hide All|Small|Medium|Large
; ------------- End Section: [Quality and RGB Items] ------------

; ------------- Section: [Socket Patterns] ------------
anchor_x := 1160, anchor_y := 64
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h256, Socket Patterns
; Edit
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 18, y := anchor_y + 36
Gui Add, Edit, x%x% y%y% w250 HWNDhSocketPatternsEditBox
Placeholder(hSocketPatternsEditBox, "Example: B-B-G-X")
; Item slot DDL and Add button
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 20, y := anchor_y + 68
Gui Add, DropDownList, x%x% y%y% HWNDhSocketPatternsItemSlotDdl, Any Item Slot||Weapons|Body Armours|Helmets|Gloves|Boots|Belts|Rings|Amulets
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 202, y := anchor_y + 68
Gui Add, Button, x%x% y%y% w66 h26 gSocketPatternsAdd, Add
; Text box and Remove button
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 14, y := anchor_y + 102
Gui Add, ListBox, x%x% y%y% w257 h110 HWNDhSocketPatternsListBox
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 68, y := anchor_y + 212
Gui Add, Button, x%x% y%y% w144 h31 gSocketPatternsRemove, Remove Selected
; ------------- End Section: [Socket Patterns] ------------


; ------------- Section: [Item-Rule Matching] -------------
anchor_x := 1160, anchor_y := 336
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h290, Item-Rule Matching
; Buttons & Edit
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 16, y := anchor_y + 36
Gui Add, Button, x%x% y%y% w254 h28 gClip_ , Find Rule Matching Clipboard
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
x := anchor_x + 16, y := anchor_y + 75
Gui Add, Edit, x%x% y%y% w254 h164 vMatchedRule +ReadOnly
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
x := anchor_x + 66, y := anchor_y + 246
Gui Add, Button, x%x% y%y% w154 h28 vChangeMatchedRuleButton gMatchedShowHide +Disabled, Change to "Hide"
; ------------- End Section: [Item-Rule Matching] -------------

; ------------- Section: [Filter Actions] -------------
anchor_x := 1160, anchor_y := 650
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h182, Filter Actions
; Status message box
Gui Font
Gui Font, c0x00e8b2 s11, Segoe UI
x := anchor_x + 16, y := anchor_y + 32
Gui Add, Edit, x%x% y%y% w254 h50 vGUIStatusMsg +ReadOnly -VScroll, %status_msg%
; Action buttons
Gui Font, c0x00e8b2 s11 Bold, Segoe UI
x := anchor_x + 32, y := anchor_y + 93
Gui Add, Button, x%x% y%y% w226 h32 gImport, Import Downloaded Filter
x := anchor_x + 32, y := anchor_y + 133
Gui Add, Button, x%x% y%y% w224 h31 gUpdate, [&W]rite Filter
; ------------- End Section: [Filter Actions] -------------

Gui Show, w%kWindowWidth% h%kWindowHeight%, %kWindowTitle%
Return

; ============================= GUI Response Code =============================

HandleCurrencyListBoxEvent(CtrlHwnd, GuiEvent, EventInfo, ErrLevel := "") {
    MsgBox, % "CtrlHwnd: " CtrlHwnd "`nGuiEvent " GuiEvent "`nEventInfo " EventInfo
}

; ------------- Section: [General BaseTypes] ------------

; set_basetype_visibility <base_type: str> <visibility_flag: int> <(optional) rare_only_flag: int>

GeneralBaseTypesAdd:
    GuiControlGet base_type, , %hGeneralBaseTypesEditBox%
    GuiControlGet rare_only_flag, , %hGeneralBaseTypesRareCheckBox%
    base_type := Trim(base_type)
    if ((base_type == "") or (base_type == "Enter BaseType...")) {
        return
    }
    ; Convert to corresponding backend function call and store it
    show_flag := 1
    backend_function_call := "set_basetype_visibility " Quoted(base_type) " " show_flag " " rare_only_flag
    g_general_basetypes_changes.push(backend_function_call)
    ; Convert to UI list box line and add
    list_box_line := "[" (rare_only_flag ? "Rare" : "Any") "] " base_type
    GuiControl, , %hGeneralBaseTypesListBox%, %list_box_line%  ; add new base type line
    GuiControl, , %hGeneralBaseTypesEditBox%  ; clear edit box
    return

GeneralBaseTypesRemove:
    ; Get raw text of selected item
    GuiControl -AltSubmit, %hGeneralBaseTypesListBox%
    GuiControlGet selected_item_text, , %hGeneralBaseTypesListBox%
    if (selected_item_text == "") {
        return
    }
    ; Get index of selected item
    GuiControl +AltSubmit, %hGeneralBaseTypesListBox%
    GuiControlGet, selected_item_index, , %hGeneralBaseTypesListBox%
    ; Parse text into base_type, rare_only_flag
    ; "[Rare] Hubris Circlet" -> ["", "Rare", " Hubris Circlet"]
    split_result := StrSplit(selected_item_text, ["[","]"])
    ; rare_only_flag := (split_result[2] != "Any")  ; AHK arrays are 1-indexed
    base_type := SubStr(split_result[3], 2)  ; substring starting at second character
    ; Convert to corresponding backend function call and store it
    ; Note: rare_only_flag is omitted when disabling a BaseType
    show_flag := 0
    backend_function_call := "set_basetype_visibility " Quoted(base_type) " " show_flag
    g_general_basetypes_changes.push(backend_function_call)
    Control, Delete, %selected_item_index%, , ahk_id %hGeneralBaseTypesListBox%
    return

; ------------- Section: [Flask BaseTypes] ------------

; set_flask_visibility <base_type: str> <visibility_flag: int> <(optional) high_ilvl_flag: int>

FlaskAdd:
    GuiControlGet base_type, , %hFlaskDdl%
    GuiControlGet high_ilvl_only_flag, , %hFlaskHighIlvlCheckBox%
    base_type := Trim(base_type)
    DebugMessage(base_type)
    if (base_type == "Select Flask Type...") {
        return
    }
    ; Convert to corresponding backend function call and store it
    show_flag := 1
    backend_function_call := "set_flask_visibility " Quoted(base_type) " " show_flag " " high_ilvl_only_flag
    g_flask_basetypes_changes.push(backend_function_call)
    ; Convert to UI list box line and add
    list_box_line := "[" (high_ilvl_only_flag ? "84+" : "Any") "] " base_type
    GuiControl, , %hFlaskListBox%, %list_box_line%  ; add new base type line
    return

FlaskRemove:
    ; Get raw text of selected item
    GuiControl -AltSubmit, %hFlaskListBox%
    GuiControlGet selected_item_text, , %hFlaskListBox%
    if (selected_item_text == "") {
        return
    }
    ; Get index of selected item
    GuiControl +AltSubmit, %hFlaskListBox%
    GuiControlGet, selected_item_index, , %hFlaskListBox%
    ; Parse text into base_type, high_ilvl_only_flag
    ; "[84+] Quicksilver Flask" -> ["", "84+", " Quicksilver Flask"]
    split_result := StrSplit(selected_item_text, ["[","]"])
    ; high_ilvl_only_flag := (split_result[2] != "Any")  ; AHK arrays are 1-indexed
    base_type := SubStr(split_result[3], 2)  ; substring starting at second character
    ; Convert to corresponding backend function call and store it
    ; Note: high_ilvl_only_flag is omitted when disabling a BaseType
    show_flag := 0
    backend_function_call := "set_flask_visibility " Quoted(base_type) " " show_flag
    g_flask_basetypes_changes.push(backend_function_call)
    Control, Delete, %selected_item_index%, , ahk_id %hFlaskListBox%
    return

; ------------- Section: [Socket Patterns] ------------

; add_remove_socket_rule <socket_string: str> <(optional) item_slot: str> <add_flag: bool>

SocketPatternsAdd:
    GuiControlGet socket_pattern, , %hSocketPatternsEditBox%
    GuiControlGet item_slot, , %hSocketPatternsItemSlotDdl%
    StringUpper socket_pattern, socket_pattern
    socket_pattern := Trim(socket_pattern)
    item_slot := Trim(item_slot)
    if (SubStr(item_slot, 1, 3) == "Any") {
        item_slot := "Any"
    }
    ; Convert to corresponding backend function call and store it
    add_flag := 1
    backend_function_call := "add_remove_socket_rule " Quoted(socket_pattern) " " Quoted(item_slot) " " add_flag
    g_general_basetypes_changes.push(backend_function_call)
    ; Convert to UI list box line and add
    list_box_line := "[" item_slot "] " socket_pattern
    GuiControl, , %hSocketPatternsListBox%, %list_box_line%  ; add new base type line
    GuiControl, , %hSocketPatternsEditBox%  ; clear edit box
    return

SocketPatternsRemove:
    ; Get raw text of selected item
    GuiControl -AltSubmit, %hSocketPatternsListBox%
    GuiControlGet selected_item_text, , %hSocketPatternsListBox%
    if (selected_item_text == "") {
        return
    }
    ; Get index of selected item
    GuiControl +AltSubmit, %hSocketPatternsListBox%
    GuiControlGet, selected_item_index, , %hSocketPatternsListBox%
    ; Parse text into socket_pattern, item_slot
    ; "[Body Armours] B-G-X-X" -> ["", "Body Armours", " B-G-X-X"]
    split_result := StrSplit(selected_item_text, ["[","]"])
    item_slot := split_result[2]  ; AHK arrays are 1-indexed
    socket_pattern := SubStr(split_result[3], 2)  ; substring starting at second character
    ; Convert to corresponding backend function call and store it
    add_flag := 0
    backend_function_call := "add_remove_socket_rule " Quoted(socket_pattern) " " Quoted(item_slot) " " add_flag
    g_socket_patterns_changes.push(backend_function_call)
    Control, Delete, %selected_item_index%, , ahk_id %hSocketPatternsListBox%
    return

; ------------- Section: [Splinter StackSizes] ------------

; set_splinter_min_visible_stack_size <base_type: str> <stack_size: int>

SplinterStackSizesApply:
    GuiControlGet base_type, , %hSplinterTypeDdl%
    GuiControlGet stack_size, , %hSplinterStackSizeDdl%
    if (base_type == "Select Splinter Type...") {
        return
    }
    stack_size := RTrim(stack_size, "+")
    ; Convert to corresponding backend function call and store it
    backend_function_call := "set_splinter_min_visible_stack_size " Quoted(base_type) " " stack_size
    g_splinter_changes.push(backend_function_call)
    GuiControl, Choose, %hSplinterTypeDdl%, 1
    return

; ------------- Section: [Currency Find and Move] ------------

DeselectCurrencyNotInTier(tier) {
    Loop, 9 {
        if (A_Index != tier) {
            ; GuiControl, Choose/ChooseString does *not* trigger associated gLabels
            GuiControl, Choose, CurrTexts%A_Index%, 0
        }
    }
}

; Display tier of currency in FindCurrTier_in ddl to FindCurrTier_out text
CurrencyFindDDL:
selected_currency_type := GuiControlGetHelper("vFindCurrTier_in")
For index, currency_type in curr_txt
{
    if (currency_type == selected_currency_type){
        tier := curr_val[index]
        GuiControl, , FindCurrTier_out, T%tier%
        ; GuiControl, Choose/ChooseString does *not* trigger associated gLabels
        ; Choose the Tier in the Tier DDL and the Currency in the corresponding tier's ListBox
        GuiControl, ChooseString, CurrencyMoveTier_tier, T%tier%
        GuiControl, ChooseString, CurrTexts%tier%, %selected_currency_type%
        DeselectCurrencyNotInTier(tier)
        return
    }
}
GuiControl, , FindCurrTier_out, T?
GuiControl, Choose, CurrencyMoveTier_tier, 1
return

; There should be a better way to do this, like hooking the GUI element up
; to a function and passing in the tier parameter. But this is just for PoC.
CurrencyListBoxItemSelectedT1:
tier := 1
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT2:
tier := 2
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT3:
tier := 3
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT4:
tier := 4
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT5:
tier := 5
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT6:
tier := 6
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT7:
tier := 7
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT8:
tier := 8
Goto CurrencyListBoxItemSelected
CurrencyListBoxItemSelectedT9:
tier := 9
Goto CurrencyListBoxItemSelected

CurrencyListBoxItemSelected:
; We want to select the corresponding item in the find currency DDL,
; and trigger the associated "Find" action.
; We also want to deselect any currency items selected in other tier boxes.
Loop, 9 {
    ; Select corresponding item in Find currency DDL
    if (A_Index == tier) {
        selected_item := GuiControlGetHelper("vCurrTexts" tier)
        ; Control, Choose/ChoseString string *does* trigger associated gLabels
        Control, ChooseString, %selected_item%, , ahk_id %hFindCurrencyDdl%
        DeselectCurrencyNotInTier(tier)
        break
    }
}
return

; Move currency selected in vFindCurrTier_in to tier selected in vCurrencyMoveTier_tier
CurrencyMoveTier:
currency_type := GuiControlGetHelper("vFindCurrTier_in")
target_tier := GuiControlGetHelper("vCurrencyMoveTier_tier")
; DebugMessage("Moving " currency_type " to tier " target_tier)
if (currency_type == "Select Currency Type..." or target_tier == "T#")
    return
dst_tier := LTrim(target_tier, "T")
src_tier := 0
for key, val in curr_txt
{
    if (val == currency_type){
        src_tier := curr_val[key]
        curr_val[key] := dst_tier
    }
}
currtexts := ["", "", "", "", "", "", "", "", ""]
For idx in curr_txt {
    currtexts[curr_val[idx]] .= curr_txt[idx] "|"
}
Loop, 9 {
    ; Isn't this just RTrim?
    currtexts[A_Index] := RegExReplace( currtexts[A_Index], "\|$" )
}
GuiControl, , % "CurrTexts" src_tier, % "|" currtexts[src_tier]
GuiControl, , % "CurrTexts" dst_tier, % "|" currtexts[dst_tier]
; Control, Choose/ChoseString string *does* trigger associated gLabels
hwnd_name = % hCurrencyTierBoxT%dst_tier%  ; some wizardry here but it works
Control, ChooseString, %currency_type%, , ahk_id %hwnd_name%,
return

; Clipboard Rule Matching
type_tag := ""
tier_tag := ""
rule := ""
Clip_:
; Reset Global Variables
type_tag := ""
tier_tag := ""
rule := ""
FileDelete, %kBackendCliInputPath%
FileDelete, %kBackedCliOutputPath%
FileAppend, % Clipboard, %kBackendCliInputPath%
RunWait, %python_command% %kBackendCliPath% get_rule_matching_item %active_profile%, , Hide
FileRead, exit_code, %kBackendCliExitCodePath%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Clipboard Match Failed"
    FileRead, error_log, %kBackendCliLogPath%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
    return
}
FileRead, py_out_text, %kBackedCliOutputPath%
if (py_out_text = "")
{
    GuiControl, , MatchedRule, Unable to Find Matching Rule
    return
}
GuiControl, , MatchedRule, %py_out_text%
idx := 0
Loop, parse, py_out_text, `n, `r
{
    if (idx = 0){
        splits := StrSplit(A_LoopField, ":")
        type_tag := splits[2]
        idx := 1
    }
    else if (idx = 1){
        splits := StrSplit(A_LoopField, ":")
        tier_tag := splits[2]
        idx := 2
    }
    else
        rule .= A_LoopField "`n"
}
if (InStr(py_out_text, "Show #")){
    GuiControl, , ChangeMatchedRuleButton, Change to "Hide"
    GuiControl, Enable, ChangeMatchedRuleButton
} else if (InStr(py_out_text, "Hide #")){
    GuiControl, , ChangeMatchedRuleButton, Change to "Show"
    GuiControl, Enable, ChangeMatchedRuleButton
}
return

MatchedShowHide:
GuiControlGet, ButtonText, , ChangeMatchedRuleButton
if (InStr(ButtonText, "Show")){
    visi := "show"
}
else{
    visi := "hide"
}
RunWait, %python_command% %kBackendCliPath% set_rule_visibility "%type_tag%" %tier_tag% %visi% %active_profile% , , Hide
FileRead, exit_code, %kBackendCliExitCodePath%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Rule Visibility Change Failed"
    FileRead, error_log, %kBackendCliLogPath%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
    return
}
GuiControl, , GUIStatusMsg , % "Rule Visibility Changed Successfully"
GuiControl, Disable, ChangeMatchedRuleButton
return

ChangeProfile:
Gui, Submit, NoHide
if (ProfileDDL == active_profile)
    return
RunWait, %python_command% %kBackendCliPath% set_active_profile %ProfileDDL%, , Hide
FileRead, exit_code, %kBackendCliExitCodePath%
if (exit_code == "1"){
    FileRead, error_log, %kBackendCliLogPath%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
Reload
ExitApp

CreateProfile1:
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

CreateProfile2:
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

2GuiClose:
Gui, 2: Destroy
return


; ==================== Update / Run Batch Code ====================

AddFunctionCallToBatch(function_call_string) {
    global kBackendCliInputPath
    FileAppend, %function_call_string%`n, %kBackendCliInputPath%
}

Update:
Gui, Submit, NoHide
; Erase backend_cli.input before writing
FileAppend, , %kBackendCliInputPath%
FileDelete, %kBackendCliInputPath%
; Currency Stack Sizes -- vValueCurrencyDDLT1-9 (+Tportal Twisdom) vs cstackvalues[1-9] and portal_stack , wisdom_stack
; cstack_output_dict(_low) provides output values
Loop, 9
{
    if (valueCurrencyDDLT%A_Index% != cstack_values[A_Index]){
        _low := A_Index > 7 ? "_low" : ""
        FileAppend, % "set_currency_tier_min_visible_stack_size " A_Index " " cstack_output_dict%_low%[valueCurrencyDDLT%A_Index%] "`n", %kBackendCliInputPath%
        cstack_values[A_Index] := valueCurrencyDDLT%A_Index%
    }
}
if (valueCurrencyDDLTwisdom != wisdom_stack){
    FileAppend, % "set_currency_tier_min_visible_stack_size twisdom " cstack_output_dict_low[valueCurrencyDDLTwisdom] "`n", %kBackendCliInputPath%
    wisdom_stack := valueCurrencyDDLTwisdom
}
if (valueCurrencyDDLTportal != portal_stack){
    FileAppend, % "set_currency_tier_min_visible_stack_size tportal " cstack_output_dict_low[valueCurrencyDDLTportal] "`n", %kBackendCliInputPath%
    portal_stack := valueCurrencyDDLTportal
}
; Currency Tiers -- Accurate already to curr_val and curr_val_start
For idx, name in curr_txt
{
    if (curr_val[idx] != curr_val_start[idx]){
        FileAppend, % "set_currency_to_tier """ curr_txt[idx] """ " curr_val[idx] "`n" , %kBackendCliInputPath%
        curr_val_start[idx] := curr_val[idx]
    }
}
; Rares -- rare_GUI_ids value compared vs rare_dict
For rare, value_name in rare_GUI_ids
{
    if (%value_name% != rare_dict[rare]){
        FileAppend, % "set_chaos_recipe_enabled_for """ rare """ " %value_name% "`n", %kBackendCliInputPath%
        rare_dict[rare] := %value_name%
    }
}
; General BaseTypes
for i, function_call_string in g_general_basetypes_changes {
    AddFunctionCallToBatch(function_call_string)
}
g_general_basetypes_changes := []
; Flask BaseTypes
for i, function_call_string in g_flask_basetypes_changes {
    AddFunctionCallToBatch(function_call_string)
}
g_flask_basetypes_changes := []
; Socket Patterns
for i, function_call_string in g_socket_patterns_changes {
    AddFunctionCallToBatch(function_call_string)
}
g_socket_patterns_changes := []
; Splinter StackSizes
for i, function_call_string in g_splinter_changes {
    AddFunctionCallToBatch(function_call_string)
}
g_splinter_changes := []
; Essences -- compare esshide vs esshideDDL
if (esshide != esshideDDL){
    FileAppend, % "set_hide_essences_above_tier " esshideDDL "`n", %kBackendCliInputPath%
    esshide := esshideDDL
}
; unique -- compare uniqhide vs uniqhideDDL
if (uniqhide != uniqhideDDL){
    FileAppend, % "set_hide_unique_items_above_tier " uniqhideDDL "`n", %kBackendCliInputPath%
    uniqhide := uniqhideDDL
}
; uniq map -- compare unique_mapmin vs unique_mapminDDL
if (unique_mapmin != unique_mapminDDL){
    FileAppend, % "set_hide_unique_maps_above_tier " unique_mapminDDL "`n", %kBackendCliInputPath%
    unique_mapmin := unique_mapminDDL
}
; div -- compare divmin vs divminDDL
if (divmin != divminDDL){
    FileAppend, % "set_hide_div_cards_above_tier " divminDDL "`n", %kBackendCliInputPath%
    divmin := divminDDL
}
; RGB -- compare rgbsize vs rgbsizeDDL
rgbnow := rgbmap_reversed[rgbsizeDDL]
if (rgbsize != rgbnow){
    FileAppend, % "set_rgb_item_max_size " rgbnow "`n", %kBackendCliInputPath%
    rgbsize := rgbnow
}
; OIL -- compare min_oil vs min_oilDDL
if (min_oil != min_oilDDL){
    FileAppend, % "set_lowest_visible_oil """ kOilBaseTypes[min_oilDDL] " Oil""`n", %kBackendCliInputPath%
    min_oil := min_oilDDL

}
; gem/flask quality -- compare gemmin vs gemminUD flaskmin vs flaskminUD
if (gemmin != gemminUD){
    gemout := gemminUD == 21? -1 : gemminUD
    FileAppend, % "set_gem_min_quality " gemout "`n", %kBackendCliInputPath%
    gemmin := gemminUD
}
if (flaskmin != flaskminUD){
    flaskout := flaskminUD == 21? -1 : flaskminUD
    FileAppend, % "set_flask_min_quality " flaskout "`n", %kBackendCliInputPath%
    flaskmin := flaskminUD
}
; map hide -- compare maphide vs maphideUD
if(maphide != maphideUD){
    FileAppend, % "set_hide_maps_below_tier " maphideUD "`n", %kBackendCliInputPath%
    maphide := maphideUD
}
GuiControl, , GUIStatusMsg , % "Filter Updating..."
RunWait, %python_command% %kBackendCliPath% run_batch %active_profile%, , Hide
FileRead, exit_code, %kBackendCliExitCodePath%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Filter Update Failed"
    FileRead, error_log, %kBackendCliLogPath%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
GuiControl, , GUIStatusMsg , % "Filter Updated Successfully"
MakePoeActive()
return

Import:
RunWait, %python_command% %kBackendCliPath% import_downloaded_filter %active_profile%,  , Hide
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

GuiEscape:
GuiClose:
ExitApp

; ============================= Helper Functions =============================

; Returns the HWND ID of the active window if it is owned by the PoE process,
; or 0 if it does not. Thus, the return value can be used in boolean contex
; to determine if PoE is the currently active window.
IsPoeActive() {
   return WinActive("ahk_exe PathOfExile.exe")
}

MakePoeActive() {
   WinActivate, ahk_exe PathOfExile.exe
}

IsDlfActive() {
    global kWindowTitle
    return WinActive(kWindowTitle " ahk_exe AutoHotkey.exe") != 0
}

MakeDlfActive() {
    global kWindowTitle
    WinActivate, %kWindowTitle% ahk_exe AutoHotkey.exe
}

; Sends a chat message by saving it to the clipboard and sending: Enter, Ctrl-v, Enter
; Backs up the clipboard and restores it after a short delay on a separate thread.
; (The clipboard cannot be restored immediately, or it will happen before the paste operation occurs.)
SendChatMessage(message_text, reply_flag := false) {
   global backup_clipboard
   backup_clipboard := clipboard
   clipboard := message_text
   BlockInput, On
   if (reply_flag) {
      Send, ^{Enter}^v{Enter}
   } else {
      Send, {Enter}^v{Enter}
   }
   BlockInput, Off
   SetTimer, RestoreClipboard, -50
}

RestoreClipboard() {
   global backup_clipboard
   clipboard := backup_clipboard
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
GoSub Update
return

; Reload Filter
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
F9::  ; $reload_filter_hotkey_line
if (IsPoeActive()) {
    SendChatMessage("/itemfilter DynamicLootFilter")
}
return