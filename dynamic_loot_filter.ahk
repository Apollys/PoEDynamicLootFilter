#SingleInstance Force
#NoEnv
SetWorkingDir %A_ScriptDir%
SetBatchLines -1

Menu, Tray, Icon, DLF_icon.ico

; ----------- PYTHON VERSION AND PATH CHECKING ----------------
PythonChecks:
FileRead, pyth_path, python_path.txt
If (pyth_path == ""){
    RunWait, %ComSpec% /c "python --version >python_check.txt" ,  , Hide
    FileRead, python_check, python_check.txt
    if(SubStr(python_check, 1, 7) == "Python " and SubStr(python_check, 1, 8) >= 3){
        pyth_path := "python"
    }
    else{
        FileDelete, python_check.txt
        RunWait, %ComSpec% /c "py --version >python_check.txt" ,  , Hide
        FileRead, python_check, python_check.txt
        if(SubStr(python_check, 1, 7 ) == "Python " and SubStr(python_check, 1, 8) >= 3){
            pyth_path := "py"
        }
        else{
            FileDelete, python_check.txt
            RunWait, %ComSpec% /c "python3 --version >python_check.txt" ,  , Hide
            FileRead, python_check, python_check.txt
            if(SubStr(python_check, 1, 7) == "Python " and SubStr(python_check, 1, 8) >= 3){
                pyth_path := "python3"
            }
            else{
                MsgBox,  Error: The commands "python", "py", and "python3" were all unable to launch Python 3.  This may be caused because python is not in the Windows path, or because the listed commands is aliased to another program.
                FileDelete, python_check.txt
                ExitApp
            }
        }
    }
    FileDelete, python_check.txt
    FileAppend, %pyth_path%, python_path.txt
}
else{
    RunWait, %ComSpec% /c %pyth_path% " --version >python_check.txt" ,  , Hide
    FileRead, python_check, python_check.txt
    if(SubStr(python_check, 1, 7) != "Python " or SubStr(python_check, 8, 1) < 3){
        FileDelete, python_path.txt
        FileDelete, python_check.txt
        goto, PythonChecks
    }
    FileDelete, python_check.txt
}

pyth_path := "python"

; ------------ DATA STORAGE INITIALIZATION -------------

; File Paths for Python program/input/output
py_prog_path := "backend_cli.py"
py_out_path := "backend_cli.output"
py_log_path := "backend_cli.log"
py_exit_code_path := "backend_cli.exit_code"
ahk_out_path := "backend_cli.input"


; Coloring for rares by slot (copied from consts.py)
rare_colors := {"Weapons" : "c80000", "Body Armours" : "ff00ff", "Helmets" : "ff7200"
    , "Gloves" : "ffe400", "Boots" : "00ff00", "Amulets" : "00ffff", "Rings" : "4100bd"
    , "Belts" : "0000c8"}

; Flask BaseTypes and show flags
flasks := {"Divine Life Flask" : [0, 0], "Eternal Mana Flask" : [0, 0]
    , "Quicksilver Flask" : [0, 0], "Bismuth Flask" : [0, 0], "Amethyst Flask" : [0, 0]
    , "Ruby Flask" : [0, 0], "Sapphire Flask" : [0, 0], "Topaz Flask" : [0, 0]
    , "Aquamarine Flask" : [0, 0], "Diamond Flask" : [0, 0], "Jade Flask" : [0, 0]
    , "Quartz Flask" : [0, 0], "Granite Flask" : [0, 0], "Sulphur Flask" : [0, 0]
    , "Basalt Flask" : [0, 0], "Silver Flask" : [0, 0], "Stibnite Flask" : [0, 0]
    , "Corundum Flask" : [0, 0], "Gold Flask" : [0, 0]}
base_flasks := {"Divine Life Flask" : [0, 0], "Eternal Mana Flask" : [0, 0]
    , "Quicksilver Flask" : [0, 0], "Bismuth Flask" : [0, 0], "Amethyst Flask" : [0, 0]
    , "Ruby Flask" : [0, 0], "Sapphire Flask" : [0, 0], "Topaz Flask" : [0, 0]
    , "Aquamarine Flask" : [0, 0], "Diamond Flask" : [0, 0], "Jade Flask" : [0, 0]
    , "Quartz Flask" : [0, 0], "Granite Flask" : [0, 0], "Sulphur Flask" : [0, 0]
    , "Basalt Flask" : [0, 0], "Silver Flask" : [0, 0], "Stibnite Flask" : [0, 0]
    , "Corundum Flask" : [0, 0], "Gold Flask" : [0, 0]}
_high := 0

; RGB size tooltips
rgbtooltip := {"none" : "Hide everything", "small" : "2x2, 4x1, and 3x1"
    , "medium" : "3x2, 2x2, 4x1, and 3x1", "large" : "Show everything"}
rgbmap := {"none" : 1, "small" : 2, "medium" : 3, "large" : 4}
rgbmap_reversed := {1 : "none", 2: "small", 3: "medium", 4: "large"}

; Oil names, ordered from highest to lowest value
oils := ["Tainted", "Golden", "Silver", "Opalescent", "Black", "Crimson", "Violet", "Indigo"
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
FileDelete, %ahk_out_path%
RunWait, %pyth_path% %py_prog_path% get_all_profile_names, , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
FileRead, py_out_text, %py_out_path%
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

; -------------- DATA LOADING -------------------------------
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
FileAppend, get_all_currency_tiers`nget_all_chaos_recipe_statuses`nget_hide_maps_below_tier`nget_currency_tier_min_visible_stack_size tportal`nget_currency_tier_min_visible_stack_size twisdom`nget_hide_essences_above_tier`nget_hide_unique_items_above_tier`nget_gem_min_quality`nget_rgb_item_max_size`nget_flask_min_quality`nget_lowest_visible_oil`n, %ahk_out_path%
Loop, 9
{
    FileAppend, get_currency_tier_min_visible_stack_size %A_Index%`n, %ahk_out_path%
}
FileAppend, get_hide_div_cards_above_tier`nget_hide_unique_maps_above_tier`n, %ahk_out_path%
for key in flasks
{
    FileAppend, get_flask_visibility "%key%"`r`n, %ahk_out_path% 
    fake_queue.Push(key)
}

; Load all filter data from backend client
status_msg := "Filter Loaded Succesfully"
RunWait, %pyth_path% %py_prog_path% run_batch %active_profile%, , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    status_msg := "Filter Load Failed"
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
FileRead, py_out_text, %py_out_path%

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
        for idx, val in oils 
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
        flasks[fake_queue[prog - 21]] := [0,0]
        base_flasks[fake_queue[prog - 21]] := [0,0]
        if (splits[1] = 1)
        {
            flasks[fake_queue[prog - 21]][1] := 1
            base_flasks[fake_queue[prog - 21]][1] := 1
        }
        if (splits[2] = 1)
        {
            flasks[fake_queue[prog - 21]][2] := 1
            base_flasks[fake_queue[prog - 21]][2] := 1
        }
    }
}
; PROBABLY UNNECESSARY VARIABLES WITH NEW UI
;base_maphide := maphide
;base_portstack := portal_stack
;base_wisstack := wisdom_stack
;base_esshide := esshide
;base_uniqhide := uniqhide
;base_gemmin := gemmin
;base_rgbsize := rgbsize
;base_flaskmin := flaskmin
;base_min_oil := min_oil
;base_divmin := divmin
;base_unique_mapmin := unique_mapmin


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

; Flask data
flask_avail1 := ""
flask_avail2 := ""
flask_high := ""
flask_low := ""
for flask, arr in flasks
{
    if (arr[2] == 1)
        flask_high .= flask "|"
    else
        flask_avail2 .= flask "|"
    if (arr[1] == 1)
        flask_low .= flask "|"
    else
        flask_avail1 .= flask "|"
}
RTrim(flask_avail1, "|")
RTrim(flask_avail2, "|")
RTrim(flask_high, "|")
RTrim(flask_low, "|")

; Oil data
oilstr := ""
for key, val in oils {
    oilstr .= val "|"
}
RTrim(oilstr, "|")
; ------------- End Precomputation -------------

; ------------- GUI Construction Start -------------
; Set color themes
Gui Color, 0x111122, 0x111133
; Title
Gui Font, c0x00e8b2 s16 Bold, Segoe UI
Gui Add, Text, x192 y8 w556 h26 +0x200 +Center, PoE Dynamic Loot Filter

; ------------- Section: Profiles ------------
Gui Font, c0x00e8b2 s12 Bold, Segoe UI
Gui Add, Text, x845 y8 w61 h29 +0x200, Profile:
; DropDownList
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, DropDownList, x905 y8 w151 gChangeProfile vProfileDDL Choose1, %ProfString%
; Create Button
Gui Font, c0x00e8b2 s11 Bold, Segoe UI
Gui Add, Button, x1060 y9 w60 h26 gCreateProfile1, Create
; ------------- End Section: Profiles -------------

; ------------- Section: Currency -------------
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x16 y48 w483 h783, Currency
; Dividing lines
Gui Add, Text, x24 y160 w468 h0 +0x10  ; horizontal line above row 1
Gui Add, Text, x24 y368 w468 h0 +0x10  ; horizontal line between rows 1 and 2
Gui Add, Text, x24 y576 w468 h0 +0x10  ; horizontal line between rows 2 and 3
Gui Add, Text, x178 y168 w0 h610 +0x1 +0x10  ; vertical line between columns 1 and 2
Gui Add, Text, x24 y784 w468 h0 +0x10  ; horizontal line above portal/wisdom scrolls
Gui Add, Text, x256 y792 w0 h34 +0x1 +0x10  ; vertical line between portal/wisdom scrolls
; Find tier of currency
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
Gui Add, Text, x32 y80 w147 h30 +0x200 +Right, Find Tier of Currency:
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, DropDownList, x186 y80 w188 +Sort gCurrencyFindDDL vFindCurrTier_in, %all_currency%
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
Gui Add, Text, x384 y80 w16 h28 +0x200, ->
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Text, x408 y81 w40 h26 +0x200 vFindCurrTier_out, [Tier]
; Move currency to tier
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
Gui Add, Text, x32 y120 w148 h28 +0x200 +Right, Move Currency to Tier:
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, DropDownList, x184 y120 w191 +Sort vCurrencyMoveTier_curr, %all_currency%
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
Gui Add, Text, x384 y120 w16 h28 +0x200, ->
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, DropDownList, x408 y120 w41 vCurrencyMoveTier_tier, T1|T2|T3|T4|T5|T6|T7|T8|T9
; Go Button
Gui Font, c0x00e8b2 s10 Bold, Segoe UI
Gui Add, Button, x456 y121 w32 h26 gCurrencyMoveTier, Go
; T1 block
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Text, x32 y168 w115 h28 +0x200, T1 Stack Size:
Gui Add, DropDownList, % "+AltSubmit vValueCurrencyDdlT1 x124 y168 w44 Choose"cstack_values[1],  %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x32 y197 w135 h164 +Sort vCurrTexts1, % currtexts[1]
; T2 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x192 y168 w115 h28 +0x200, T2 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT2 x284 y168 w44 Choose"cstack_values[2], %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x192 y197 w135 h164 +Sort vCurrTexts2, % currtexts[2]
; T3 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x338 y168 w0 h610 +0x1 +0x10  ; vertical line between column 2 and 3
Gui Add, Text, x352 y168 w115 h28 +0x200, T3 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT3 x444 y168 w44 Choose"cstack_values[3], %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x352 y197 w135 h164 +Sort vCurrTexts3, % currtexts[3]
; T4 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x32 y376 w115 h28 +0x200, T4 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT4 x124 y376 w44 Choose"cstack_values[4], %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x32 y405 w135 h164 +Sort vCurrTexts4, % currtexts[4]
; T5 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x192 y376 w115 h28 +0x200, T5 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT5 x284 y376 w44 Choose"cstack_values[5], %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x192 y405 w135 h164 +Sort vCurrTexts5, % currtexts[5]
; T6 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x352 y376 w115 h28 +0x200, T6 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT6 x444 y376 w44 Choose"cstack_values[6], %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x352 y405 w135 h164 +Sort vCurrTexts6, % currtexts[6]
; T7 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x32 y584 w115 h28 +0x200, T7 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT7 x124 y584 w44 Choose"cstack_values[7], %cstacktext_less%
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x32 y613 w135 h164 +Sort vCurrTexts7, % currtexts[7]
; T8 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x192 y584 w115 h28 +0x200, T8 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT8 x284 y584 w44 Choose"cstack_values[8], %cstacktext%  
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x192 y613 w135 h164 +Sort vCurrTexts8, % currtexts[8]
; T9 block
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x352 y584 w115 h28 +0x200, T9 Stack Size:
Gui Add, DropDownList,% "+AltSubmit vValueCurrencyDdlT9 x444 y584 w44 Choose"cstack_values[9], %cstacktext%  
Gui Font, c0x00e8b2 s10
Gui Add, ListBox, x352 y613 w135 h164 +Sort vCurrTexts9, % currtexts[9]  
; Portal scrolls
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x56 y792 w115 h28 +0x200, Portal Stack Size:
Gui Add, DropDownList, +AltSubmit vValueCurrencyDdlTportal Choose%portal_stack% x176 y792 w48, % cstacktext
; Wisdom scrolls
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Text, x288 y792 w133 h28 +0x200, Wisdom Stack Size:
Gui Add, DropDownList, +AltSubmit vValueCurrencyDdlTwisdom Choose%wisdom_stack% x424 y792 w48, % cstacktext
; ------------- End Section: Currency -------------

; ------------- Section: Chaos Rares -------------
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x528 y48 w285 h169, Chaos Recipe Rares
; CheckBoxes
Gui Font, c0x00e8b2 s14 Norm, Segoe UI
Gui Add, CheckBox, % "x544 y80 w123 h26 v" rare_GUI_ids["Weapons"] " " (rare_dict["Weapons"]? " Checked" : ""), Weapons
Gui Add, CheckBox, % "x544 y112 w123 h26 v" rare_GUI_ids["Body Armours"] " "  (rare_dict["Body Armours"]? " Checked" : ""), Armours
Gui Add, CheckBox, % "x544 y176 w123 h26 v" rare_GUI_ids["Gloves"] " "  (rare_dict["Gloves"]? " Checked" : ""), Gloves
Gui Add, CheckBox, % "x544 y144 w123 h26 v" rare_GUI_ids["Helmets"] " "  (rare_dict["Helmets"]? " Checked" : ""), Helmets
Gui Add, CheckBox, % "x680 y80 w123 h26 v" rare_GUI_ids["Boots"] " "  (rare_dict["Boots"]? " Checked" : ""), Boots
Gui Add, CheckBox, % "x680 y112 w123 h26 v" rare_GUI_ids["Belts"] " "  (rare_dict["Belts"]? " Checked" : ""), Belts
Gui Add, CheckBox, % "x680 y144 w123 h26 v" rare_GUI_ids["Rings"] " "  (rare_dict["Rings"]? " Checked" : ""), Rings
Gui Add, CheckBox, % "x680 y176 w123 h26 v" rare_GUI_ids["Amulets"] " "  (rare_dict["Amulets"]? " Checked" : ""), Amulets
; ------------- End Section: Chaos Rares -------------

; ------------- Section: Flasks ------------
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x528 y232 w286 h427, Flask BaseTypes
; Any ItemLevel flasks
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Text, x544 y264 w101 h28 +0x200, Any ItemLevel:
Gui Add, DropDownList, x648 y264 w153 vFlaskAvailDDL1 gAddFlaskAny, Add...||%flask_avail1%
Gui Add, ListBox, x544 y296 w257 h104 vFlaskListAny +Sort, %flask_low%
Gui Add, Button, x592 y408 w144 h31 gRemoveFlaskAny, Remove Selected
; Divider
Gui Add, Text, x536 y448 w270 h0 +0x10  ; horizontal line between flask sections
; High ItemLevel flasks
Gui Add, Text, x544 y464 w108 h28 +0x200, High ItemLevel:
Gui Add, DropDownList, x650 y464 w151 vFlaskAvailDDL2 gAddFlaskHigh, Add...||%flask_avail2%
Gui Add, ListBox, x544 y496 w257 h104 vFlaskListHigh +Sort, %flask_high%
Gui Add, Button, x592 y608 w144 h31 gRemoveFlaskHigh, Remove Selected
; ------------- End Section: Flasks ------------

; ------------- Section: Quality and RGB Items ------------
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x528 y674 w286 h152, Quality and RGB Items
; Quality gems
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Text, x544 y706 w120 h28 +0x200, Gem Min Quality:
Gui Add, Edit, x664 y706 w50 h28 vgemminUD,
Gui Add, UpDown, x706 y706 w20 h28 Range0-21, % gemmin
; Quality flasks
Gui Add, Text, x544 y746 w120 h28 +0x200, Flask Min Quality:
Gui Add, Edit, x664 y746 w50 h28 vflaskminUD,
Gui Add, UpDown, x706 y746 w20 h28 Range0-21, % flaskmin
; RGB items
Gui Add, Text, x544 y786 w136 h28 +0x200, RGB Max Item Size: 
Gui Add, DropDownList,% "+AltSubmit x680 y786 w113 vrgbsizeDDL Choose" rgbmap[rgbsize], Hide All|Small|Medium|Large
; ------------- End Section: Quality and RGB Items ------------

; ------------- Section: Hide Maps Below Tier -------------
; GroupBox
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x840 y56 w288 h74, Regular Maps
; Text
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Text, x856 y88 w152 h28 +0x200, Hide Maps Below Tier:
; Edit & UpDown
Gui Add, Edit, x1012 y88 w50 h28 vmaphideUD, 
Gui Add, UpDown, x1054 y88 w20 h28 Range0-17, % maphide
; ------------- End Section: Hide Maps Below Tier -------------

; ------------- Section: Misc Tier Visibilities -------------
Gui Add, GroupBox, x840 y144 w288 h234, Tier Visibility
; Essences
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Text, x856 y176 w179 h28 +0x200, Hide Essences Below:
Gui Font, s10
Gui Add, DropDownList, +AltSubmit x1002 y178 w111 vesshideDDL Choose%esshide%, T7 (Deafening)|T6 (Shrieking)|T5 (Screaming)|T4 (Wailing)|T3 (Weeping)|None
; Divination cards (variable name: divmin)
Gui Font, s11
Gui Add, Text, x856 y216 w185 h28 +0x200, Hide Div Cards Above Tier:
Gui Add, DropDownList, +AltSubmit x1040 y216 w33 vdivminDDL Choose%divmin%, 1|2|3|4|5|6|7|8
; Unique items (variable name: uniqhide)
Gui Add, Text, x856 y256 w203 h28 +0x200, Hide Unique Items Above Tier:
Gui Add, DropDownList, +AltSubmit x1064 y256 w33 vuniqhideDDL Choose%uniqhide%, 1|2|3|4|5
; Unique maps (variable name: unique_maphide)
Gui Add, Text, x856 y296 w206 h28 +0x200, Hide Unique Maps Above Tier:
Gui Add, DropDownList, +AltSubmit x1064 y296 w33 vunique_mapminDDL Choose%unique_mapmin%, 1|2|3|4
; Oils (variable name: min_oil)
Gui Add, Text, x856 y336 w113 h28 +0x200, Hide Oils Below:
Gui Add, DropDownList, +AltSubmit x968 y336 w130 vmin_oilDDL Choose%min_oil%, %oilstr%
; ------------- End Section: Misc Tier Visibilities -------------

; ------------- Section: Find Rule Matching Item -------------
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x840 y394 w288 h240, Rule Matching
Gui Font, c0x00e8b2 s11 Norm, Segoe UI
Gui Add, Button, x856 y430 w254 h28 gClip_ , Find Rule Matching Clipboard
Gui Add, Edit, x856 y475 w254 h100 vMatchedRule +ReadOnly, N/A
Gui Add, Button, x906 y590 w154 h28 vChangeMatchedRuleButton gMatchedShowHide +Disabled, Change to "Hide"
; ------------- End Section: Find Rule Matching Item -------------

; ------------- Section: Filter Actions Box -------------
Gui Font, c0x00e8b2 s10 Bold
Gui Add, GroupBox, x840 y660 w288 h170, Filter Actions
; Status message box
Gui Font
Gui Font, c0x00e8b2 s11, Segoe UI
Gui Add, Edit, x856 y685 w254 h50 vGUIStatusMsg +ReadOnly -VScroll, %status_msg%
; Action buttons
Gui Font, c0x00e8b2 s11 Bold, Segoe UI
Gui Add, Button, x872 y745 w226 h32 gImport, &Re-Import Filter
Gui Add, Button, x872 y785 w224 h31 gUpdate, &Write Filter && Close UI
; ------------- End Section: Filter Actions Box -------------

Gui Show, w1144 h844, PoE Dynamic Loot Filter
Return

HandleCurrencyListBoxEvent(CtrlHwnd, GuiEvent, EventInfo, ErrLevel := "") {
    MsgBox, % "CtrlHwnd: " CtrlHwnd "`nGuiEvent " GuiEvent "`nEventInfo " EventInfo
}

; _add = 0 for remove, 1 for add
; _level = 1 for high, 0 for any
ModifyFlaskState(_add, _level, _flask){
    global flasks, FlaskAvailDDL1, FlaskAvailDDL2, FlaskListAny, FlaskListHigh
    flasks[_flask][_level+1] := _add
    flask_avail1 := ""
    flask_avail2 := ""
    flask_high := ""
    flask_low := ""
    for flask, arr in flasks
    {
        if (arr[2] == 1)
            flask_high .= flask "|"
        else
            flask_avail2 .= flask "|"
        if (arr[1] == 1)
            flask_low .= flask "|"
        else
            flask_avail1 .= flask "|"
    }
    RTrim(flask_avail1, "|")
    RTrim(flask_avail2, "|")
    RTrim(flask_high, "|")
    RTrim(flask_low, "|")
    GuiControl, , FlaskAvailDDL1,  |Add...||%flask_avail1%
    GuiControl, , FlaskAvailDDL2,  |Add...||%flask_avail2%
    GuiControl, , FlaskListAny, |%flask_low%
    GuiControl, , FlaskListHigh, |%flask_high%
}

; Add/remove flask to either list
RemoveFlaskHigh:
_high := 1
RemoveFlaskAny:
Gui, Submit, NoHide
if (_high == 1){
    flask_move := FlaskListHigh
}
else{
    flask_move := FlaskListAny
}
if (flask_move == "")
    return
ModifyFlaskState(0, _high, flask_move)
_high := 0
return

AddFlaskHigh:
_high := 1
AddFlaskAny:
Gui, Submit, NoHide
if (_high == 1){
    flask_move := FlaskAvailDDL2
}
else{
    flask_move := FlaskAvailDDL1
}
if (flask_move == "Add...")
    return
ModifyFlaskState(1, _high, flask_move)
_high := 0
return


; Display tier of currency in FindCurrTier_in ddl to FindCurrTier_out text
CurrencyFindDDL:
Gui, Submit, NoHide
For key, val in curr_txt
{
    if (val == FindCurrTier_in){
        GuiControl, , FindCurrTier_out, % "T" curr_val[key]
        return
    }
}
GuiControl, , FindCurrTier_out, Not Found
return

; move currency CurrencyMoveTier_curr to tier CurrencyMoveTier_tier
CurrencyMoveTier:
Gui, Submit, NoHide
if (CurrencyMoveTier_curr == "" or CurrencyMoveTier_tier == "")
    return
dst_tier := LTrim(CurrencyMoveTier_tier, "T")
src_tier := 0
for key, val in curr_txt
{
    if (val == CurrencyMoveTier_curr){
        src_tier := curr_val[key]
        curr_val[key] := dst_tier
    }
}
currtexts := ["", "", "", "", "", "", "", "", ""]
For idx in curr_txt {
    currtexts[curr_val[idx]] .= curr_txt[idx] "|"
}
Loop, 9 {
    currtexts[A_Index] := RegExReplace( currtexts[A_Index], "\|$" )
}
GuiControl, , % "CurrTexts" src_tier, % "|" currtexts[src_tier]
GuiControl, , % "CurrTexts" dst_tier, % "|" currtexts[dst_tier]
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
FileDelete, %ahk_out_path%
FileDelete, %py_out_path%
FileAppend, % Clipboard, %ahk_out_path%
RunWait, %pyth_path% %py_prog_path% get_rule_matching_item %active_profile%, , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Clipboard Match Failed"
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
    return
}
FileRead, py_out_text, %py_out_path%
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
RunWait, %pyth_path% %py_prog_path% set_rule_visibility "%type_tag%" %tier_tag% %visi% %active_profile% , , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Rule Visibility Change Failed"
    FileRead, error_log, %py_log_path%
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
RunWait, %pyth_path% %py_prog_path% set_active_profile %ProfileDDL%, , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    FileRead, error_log, %py_log_path%
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
FileAppend, abc, %ahk_out_path%
FileDelete, %ahk_out_path%
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
FileAppend, % "DownloadDirectory:" NewProfileDDir "`n" , %ahk_out_path%
FileAppend, % "PathOfExileDirectory:" NewProfilePoEDir "`n" , %ahk_out_path%
FileAppend, % "DownloadedLootFilterFilename:" NewProfileDName "`n", %ahk_out_path%
if (NewProfilePoEName != "(Optional)" and NewProfilePoEName != ""){
    FileAppend, % "OutputLootFilterFilename:" NewProfilePoEName "`n", %ahk_out_path%
}
if (!RDF){
    FileAppend, % "RemoveDownloadedFilter:False`n", %ahk_out_path%
    
}
Gui, 2: Destroy
RunWait, %pyth_path% %py_prog_path% create_new_profile %NewProfileName%,  , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Profile Creation Failed"
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
RunWait, %pyth_path% %py_prog_path% import_downloaded_filter %NewProfileName%,  , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Filter Import Failed"
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
Reload
ExitApp

2GuiClose:
Gui, 2: Destroy
return


Update:
Gui, Submit, NoHide
; Erase backend_cli.input before writing
FileAppend, abc, %ahk_out_path%
FileDelete, %ahk_out_path%
; Currency Stack Sizes -- vValueCurrencyDDLT1-9 (+Tportal Twisdom) vs cstackvalues[1-9] and portal_stack , wisdom_stack
; cstack_output_dict(_low) provides output values
Loop, 9
{
    if (valueCurrencyDDLT%A_Index% != cstack_values[A_Index]){
        _low := A_Index > 7 ? "_low" : ""
        FileAppend, % "set_currency_tier_min_visible_stack_size " A_Index " " cstack_output_dict%_low%[valueCurrencyDDLT%A_Index%] "`n", %ahk_out_path%
        cstack_values[A_Index] := valueCurrencyDDLT%A_Index%
    }
}
if (valueCurrencyDDLTwisdom != wisdom_stack){
    FileAppend, % "set_currency_tier_min_visible_stack_size twisdom " cstack_output_dict_low[valueCurrencyDDLTwisdom] "`n", %ahk_out_path%
    wisdom_stack := valueCurrencyDDLTwisdom
}
if (valueCurrencyDDLTportal != portal_stack){
    FileAppend, % "set_currency_tier_min_visible_stack_size tportal " cstack_output_dict_low[valueCurrencyDDLTportal] "`n", %ahk_out_path%
    portal_stack := valueCurrencyDDLTportal
}
; Currency Tiers -- Accurate already to curr_val and curr_val_start
For idx, name in curr_txt
{
    if (curr_val[idx] != curr_val_start[idx]){
        FileAppend, % "set_currency_to_tier """ curr_txt[idx] """ " curr_val[idx] "`n" , %ahk_out_path%
        curr_val_start[idx] := curr_val[idx]
    }
}
; Rares -- rare_GUI_ids value compared vs rare_dict
For rare, value_name in rare_GUI_ids
{
    if (%value_name% != rare_dict[rare]){
        FileAppend, % "set_chaos_recipe_enabled_for """ rare """ " %value_name% "`n", %ahk_out_path%
        rare_dict[rare] := %value_name% 
    }
}
; Flasks -- accurate already to flasks vs base_flasks
for flask in flasks
{
    if (flasks[flask][2] != base_flasks[flask][2]){
        FileAppend, % "set_high_ilvl_flask_visibility """ flask """ " flasks[flask][2] "`n", %ahk_out_path%
        base_flasks[flask][2] := flasks[flask][2]
    }
    if (flasks[flask][1] != base_flasks[flask][1]){
        FileAppend, % "set_flask_visibility """ flask """ " flasks[flask][1] "`n", %ahk_out_path%
        base_flasks[flask][1] := flasks[flask][1]
    }
}
; Essences -- compare esshide vs esshideDDL
if (esshide != esshideDDL){
    FileAppend, % "set_hide_essences_above_tier " esshideDDL "`n", %ahk_out_path%
    esshide := esshideDDL
}
; unique -- compare uniqhide vs uniqhideDDL
if (uniqhide != uniqhideDDL){
    FileAppend, % "set_hide_unique_items_above_tier " uniqhideDDL "`n", %ahk_out_path%
    uniqhide := uniqhideDDL
}
; uniq map -- compare unique_mapmin vs unique_mapminDDL
if (unique_mapmin != unique_mapminDDL){
    FileAppend, % "set_hide_unique_maps_above_tier " unique_mapminDDL "`n", %ahk_out_path%
    unique_mapmin := unique_mapminDDL
}
; div -- compare divmin vs divminDDL
if (divmin != divminDDL){
    FileAppend, % "set_hide_div_cards_above_tier " divminDDL "`n", %ahk_out_path%
    divmin := divminDDL
}
; RGB -- compare rgbsize vs rgbsizeDDL
rgbnow := rgbmap_reversed[rgbsizeDDL]
if (rgbsize != rgbnow){
    FileAppend, % "set_rgb_item_max_size " rgbnow "`n", %ahk_out_path%
    rgbsize := rgbnow 
}
; OIL -- compare min_oil vs min_oilDDL
if (min_oil != min_oilDDL){
    FileAppend, % "set_lowest_visible_oil """ oils[min_oilDDL] " Oil""`n", %ahk_out_path%
    min_oil := min_oilDDL
    
}
; gem/flask quality -- compare gemmin vs gemminUD flaskmin vs flaskminUD
if (gemmin != gemminUD){
    gemout := gemminUD == 21? -1 : gemminUD
    FileAppend, % "set_gem_min_quality " gemout "`n", %ahk_out_path%
    gemmin := gemminUD
}
if (flaskmin != flaskminUD){
    flaskout := flaskminUD == 21? -1 : flaskminUD
    FileAppend, % "set_flask_min_quality " flaskout "`n", %ahk_out_path%
    flaskmin := flaskminUD
}
; map hide -- compare maphide vs maphideUD
if(maphide != maphideUD){
    FileAppend, % "set_hide_maps_below_tier " maphideUD "`n", %ahk_out_path%
    maphide := maphideUD
}
GuiControl, , GUIStatusMsg , % "Filter Updating..."
RunWait, %pyth_path% %py_prog_path% run_batch %active_profile%, , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Filter Update Failed"
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
GuiControl, , GUIStatusMsg , % "Filter Updated Successfully"
WinActivate, Path of Exile
return
    
Import:
RunWait, %pyth_path% %py_prog_path% import_downloaded_filter %active_profile%,  , Hide
FileRead, exit_code, %py_exit_code_path%
if (exit_code == "1"){
    GuiControl, , GUIStatusMsg , % "Filter Import Failed"
    FileRead, error_log, %py_log_path%
    MsgBox, % "Python backend_cli.py encountered error:`n" error_log
}
else if (exit_code == "-1")
    MsgBox, How did you get here?
Reload
ExitApp

GuiEscape:
GuiClose:
ExitApp

; Toggle GUI
; Note: the `gui_hotkey_line` tag below is used for setting the hotkey in python,
; it must always be on the same line as the GUI toggle hotkey (and nowhere else).
F8::  ; $gui_hotkey_line
WinGetActiveTitle, active
if (active == "Path of Exile")
    WinActivate, PoE Dynamic Loot Filter
else if (active == "PoE Dynamic Loot Filter")
    WinActivate, Path of Exile
return