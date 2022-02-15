#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; File Paths for Python program/input/output
py_prog_path := "backend_cli.py"
py_out_path := "backend_cli.output"
ahk_out_path := "backend_cli.input"

; Valid currency BaseTypes
curr_valid := ["Exalted Orb", "Orb of Alteration", "Blessed Orb", "Blacksmith's Whetstone"
    , "Armourer's Scrap", "Glassblower's Bauble", "Orb of Transmutation", "Orb of Augmentation"
    , "Chromatic Orb", "Jeweller's Orb", "Orb of Chance", "Orb of Alchemy", "Orb of Binding"
    , "Orb of Fusing", "Vaal Orb", "Orb of Horizons", "Cartographer's Chisel", "Regal Orb"
    , "Orb of Regret", "Orb of Scouring" , "Gemcutter's Prism"]
validstr := ""
for idx, val in curr_valid
    validstr .= "|" val

; Valid rare item slots
rare_valid := ["WeaponsX", "Weapons3", "Body Armours", "Helmets", "Gloves", "Boots", "Amulets"
    , "Rings", "Belts"]
validstr2 := ""
for idx,val in rare_valid
    validstr2 .= "|" val

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

; RGB size tooltips
rgbtooltip := {"none" : "Hide everything", "small" : "2x2, 4x1, and 3x1"
    , "medium" : "3x2, 2x2, 4x1, and 3x1", "large" : "Show everything"}

; Oil names, ordered from highest to lowest value
oils := ["Tainted", "Golden", "Silver", "Opalescent", "Black", "Crimson", "Violet", "Indigo"
    , "Azure", "Teal", "Verdant", "Amber", "Sepia", "Clear"]

; Currency stack size options
cstack_options := ["All", "2", "4", "6", "None"]
cstack_values := [5, 5, 5, 5, 5, 5, 5, 5, 5]
cstack_values_base := [5, 5, 5, 5, 5, 5, 5, 5, 5]
options_idx := 1

; Flask ilvl options
flvl_options := ["None", "All", "84+"]

; Scroll stack sizes
base_portstack := 5
base_wisstack := 5
portal_stack := 5
wisdom_stack := 5

; Read starting filter data from python client
curr_txt := []
curr_ids := []
curr_val := []
curr_val_start := []
rare_txt := []
rare_ids := []
rare_val := []
rare_val_start := []
fake_queue := []
profiles := []
FileDelete, %ahk_out_path%
RunWait, python %py_prog_path% get_all_profile_names, , Hide
FileRead, py_out_text, %py_out_path%
Loop, parse, py_out_text, `n, `r
{
    if(A_LoopField = "")
        continue
    profiles.push(A_LoopField)
}
active_profile := profiles[1]

; Build batch file to get all info
FileAppend, get_all_currency_tiers`nget_all_chaos_recipe_statuses`nget_hide_maps_below_tier
    .`nget_stacked_currency_visibility tportal`nget_stacked_currency_visibility twisdom
    .`nget_hide_currency_above_tier`nget_hide_unique_items_above_tier`nget_gem_min_quality
    .`nget_rgb_item_max_size`nget_flask_min_quality`nget_lowest_visible_oil`n, %ahk_out_path%
Loop, 9
{
    FileAppend, get_stacked_currency_visibility %A_Index%`n, %ahk_out_path%
}
for key in flasks
{
    FileAppend, get_flask_visibility "%key%"`r`n, %ahk_out_path% 
    fake_queue.Push(key)
}

; Run batch
RunWait, python %py_prog_path% run_batch %active_profile%, , Hide
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
        if(InStr(validstr, splits[1])){
            curr_txt.Push(splits[1])
            curr_val.Push(splits[2])
            curr_val_start.Push(splits[2])
        }
    Case 1:
        splits := StrSplit(A_LoopField, ";")
        if(InStr(validstr2, splits[1]))
        {
            rare_txt.Push(splits[1])
            rare_val.Push(splits[2])
            rare_val_start.Push(splits[2])
        }
    Case 2:
        maphide := A_LoopField
    Case 3:
        line := line + 1
        splits := StrSplit(A_LoopField, ";")
        if (splits[2] = 1 And base_portstack = 5){
            base_portstack := line
            portal_stack := line
        }
    Case 4:
        line := line + 1
        splits := StrSplit(A_LoopField, ";")
        if (splits[2] = 1 And base_wisstack = 5){
            base_wisstack := line
            wisdom_stack := line
        }
    Case 5:
        currhide := A_LoopField
    Case 6:
        uniqhide := A_LoopField
    Case 7:
        gemmin := A_LoopField
        base_gemmin := gemmin
    Case 8:
        rgbsize := A_LoopField
        base_rgbsize := rgbsize
    Case 9:
        flaskmin := A_LoopField
        base_flaskmin := flaskmin
    Case 10:
        oil_text := StrSplit(A_LoopField, " ")
        min_oil := -1
        for idx, val in oils 
        {
            if (val = oil_text[1])
                min_oil := idx
        }
        base_min_oil := min_oil
    Case 11, 12, 13, 14, 15, 16, 17, 18, 19:
        line := line + 1
        splits := StrSplit(A_LoopField, ";")
        if (splits[2] = 1 And cstack_values[prog-10] = 5)
        {
            cstack_values[prog-10] := line
            cstack_values_base[prog-10] := line
        }
    Default:
        splits := StrSplit(A_LoopField, " ")
        if (splits[1] = 1)
        {
            flasks[fake_queue[prog - 19]] := [1,1]
        }
        else if (splits[2] = 1)
        {
            flasks[fake_queue[prog - 19]] := [2,2]
        }
        else
        {
            flasks[fake_queue[prog - 19]] := [0,0]
        }
    }
}

; Initialize GUI Handles for changing text items
for idx in curr_txt
{
    curr_ids.Push("curr_id_" idx)
}
for idx in rare_txt
{
    rare_ids.Push("rare_id_" idx)
}

; ****************************** GUI Start ******************************

GuiBuild:
; Currency
Gui, Font, S16 cB0B0B0 norm, Courier New
height := 0
for idx, val in curr_txt
{
    height := -20 + 25 * idx
    Gui, Add, Text, x250 y%height% grmbhack, % Format("{:-24}",val)
    Gui, Add, Text, % "backgroundtrans x" 545 " y" height " v" curr_ids[idx], % curr_val[idx]
}

; Update/Cancel buttons
Gui, Font, S20 cB0B0B0 norm bold, Courier New
;height := height - 32
height := 473
Gui, Add, Button, x867 y%height% gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x13 y%height% gCancel_ BackgroundTrans, Cancel

; Profiles DDL
Gui, Font, S18 cB0B0B0 norm bold, Courier New
ProfString := ""
for key, val in profiles
    ProfString .= val "|"
RTrim(ProfString, "|")
Gui, Add, DropDownList, w235 x5 y5 Choose1 vProf gProfDDL, % ProfString

; Chaos Recipe Rares
Gui, Font, S18 norm bold, Courier New
height := 0
for idx, val in rare_txt
{
    height := 10 + 40  * idx
    Gui, Font, % "c" rare_colors[val]
    Gui, Add, Text, backgroundtrans x10 y%height% grmbhack, % Format("{:-16}", val)
    Gui, Font, S36, Wingdings
    Gui, Font, % "c" (rare_val[idx]? "Blue" : "Red")
    Gui, Add, Text, % "w40 backgroundtrans x" 200 " y" (height - 10) " v" rare_ids[idx], % (rare_val[idx]? Chr(252) : Chr(251))
    Gui, Font, S18 norm bold, Courier New
}

; Misc
Gui, Font, S18 norm cB0B0B0, Courier New
height := 10

; Portal/Wisdom Scrolls
Gui, Add, Text, x590 y%height% w200 grmbhack vPortalHide, Portals:
Gui, Add, Text, x705 y%height% w100 BackgroundTrans grmbhack vPortalText
    , % cstack_options[portal_stack]
Gui, Add, Text, x800 y%height% w200 grmbhack vWisdomHide, Wisdoms:
Gui, Add, Text, x915 y%height% w100 BackgroundTrans grmbhack vWisdomText
    , % cstack_options[wisdom_stack]
height := height + 30

; Hide Maps Below Tier
Gui, Add, Text, x590 y%height% grmbhack BackgroundTrans, % "Hide Maps Below Tier:           "
Gui, Add, Text, x944 y%height% w40 BackgroundTrans vMapTierHide, % Format("{:2}", maphide)
height := height + 30

; Hide Unique Items Above Tier
Gui, Add, Text, x590 y%height% grmbhack BackgroundTrans, % "Hide Unique Items Above Tier:        "
Gui, Add, Text, x944 y%height% w40 BackgroundTrans vUniqTierHide, % Format("{:2}", uniqhide)
height := height + 30

; Hide Currency Above Tier
Gui, Add, Text, x590 y%height% grmbhack BackgroundTrans, % "Hide Currency Above Tier:       "
Gui, Add, Text, x944 y%height% w40 BackgroundTrans vCurrTierHide, % Format("{:2}", currhide)
height := height + 30

; Stacks only for Hidden Currency Tiers
Gui, Add, Text, x590 y%height% BackgroundTrans, % "Stacks - Tier:  Min Size:        "
Gui, Add, Text, x785 y%height% BackgroundTrans vStackTier grmbhack, % "X"
Gui, Add, Text, x940 y%height% w80 BackgroundTrans vStackSize grmbhack, % "N/A"
height := height + 30

; RGB Size
Gui, Add, Text, x590 y%height% grmbhack BackgroundTrans, % "RGB Items Shown:                "
Gui, Add, Text, x825 y%height% w100 BackgroundTrans vRGBHide, % Format("{:T}", rgbsize)
height:= height + 30

; Blight Oils
Gui, Add, Text, x590 y%height% grmbhack BackgroundTrans, % "Min Blight Oil:                  "
Gui, Add, Text, x805 y%height% w200 BackgroundTrans vBlightOil, % oils[min_oil]
height:= height + 30

; Quality Gems
Gui, Add, Text, x590 y%height% vgemtext, Minimum Gem Quality: %gemmin%`%
height := height + 30
Gui, Add, Slider, Range1-20 ToolTip NoTicks x590 y%height% gGemSlider vgemslider AltSubmit, % gemmin
Gui, Font, S12 bold 
height := height + 1
Gui, Add, Text, x860 y%height% gGemHA, Hide All
Gui, Font, S18 norm
height := height + 19

; Quality Flasks
Gui, Add, Text, x590 y%height% vflasktext, % "Minimum Flask Quality: " (flaskmin = -1 ? "N/A" 
    : flaskmin"`%")
height := height + 30
Gui, Add, Slider, Range1-20 ToolTip NoTicks x590 y%height% gFlaskSlider vflaskslider AltSubmit
    , % flaskmin
Gui, Font, S12 bold 
height := height + 1
Gui, Add, Text, x860 y%height% gFlaskHA, Hide All
Gui, Font, S18 norm
height := height + 19

; Flask DDL -------------- Current Options: All, 84+, Hide 
Gui, Add, Text, x590 y%height%, Show Specific Flasks:
height := height + 30
FlaskVal := -1
FlaskString := ""
for key, val in flasks
    FlaskString .= key "|"
RTrim(FlaskString, "|")
Gui, Add, DropDownList, x590 y%height% vFlask gFlaskDDL, % FlaskString
Gui, Font, c606060
Gui, Add, Text, % "x865 y" height + 4 " grmbhack", Hacky
Gui, Font, cB0B0B0
Gui, Add, Text, % "backgroundtrans x865 w80 y" height + 4 " vFlaskShow"

; Rule Matching
Gui, Font, S14 norm cB0B0B0, Courier New
height := height + 40
Gui, Add, Button, x590 y%height% gClip_, Find Rule Matching Clipboard

; Options
Gui, -border
Gui, Color, 606060
Gui, Show, w1000
return

; ************************************** GUI END **************************************

; Both RMB and LMB lead here
rmbhack:
GuiContextMenu:
control_ := RTrim(A_GuiControl)
for idx, val in curr_txt
{
    if (control_ = val)
    {
        ; GuiControlGet, current,,% curr_ids[idx]
        current := curr_val[idx]
        if (A_GuiEvent = "RightClick")
            current := (current = 1? 1 : current - 1)
        else
            current := (current = 9? 9 : current + 1)
        GuiControl, , % curr_ids[idx], % current
        curr_val[idx] := current
        return
    }
}
for idx, val in rare_txt
{
    if (control_ = val)
    {
        ; GuiControlGet, current,,% rare_ids[idx]
        rare_val[idx]:= !rare_val[idx]
        GuiControl, % "+c" (rare_val[idx]? "Blue" : "Red"), % rare_ids[idx]
        GuiControl, , % rare_ids[idx], % (rare_val[idx]? Chr(252) : Chr(251))
        return
    }
}
if (control_ = "Hide Maps Below Tier:")
{
    GuiControlGet, current,, MapTierHide
    if (A_GuiEvent = "RightClick")
        current := (current = 1? 1 : current - 1)
    else
        current := (current = 16? 16 : current + 1)
    GuiControl, , MapTierHide, % Format("{:2}", current)
    return
}
if (control_ = "Hide Currency Above Tier:")
{
    GuiControlGet, current,, CurrTierHide
    if (A_GuiEvent = "RightClick")
        current := (current = 1? 1 : current - 1)
    else
        current := (current = 9? 9 : current + 1)
    GuiControl, , CurrTierHide, % Format("{:2}", current)
    return
}
if (control_ = "StackTier")
{
    GuiControlGet, currmin,, CurrTierHide
    if (currmin = 9)
        return
    GuiControlGet, current,, StackTier
    temp := current
    if (current = "X")
        current := 9
    else
    {
        if (A_GuiEvent = "RightClick")
            current := (current = currmin +1 ? currmin + 1 : current - 1)
        else
            current := (current = 9? 9 : current + 1)
    }
    if (temp != current)
    {
        options_idx := (cstack_values[current] = 0? 5 : cstack_values[current])
        GuiControl, , StackSize, % cstack_options[options_idx]
    }
    GuiControl, , StackTier, % current
    return
}
if (control_ = "StackSize")
{
    GuiControlGet, stack,, StackTier
    if (stack = "X")
        return
    GuiControlGet, current,, StackSize
    if (current = "N/A")
    {
        current := "Hide"
        options_idx := 5
    }
    if (A_GuiEvent = "RightClick")
    {
        options_idx := (options_idx <= 2? 5 : options_idx - 1)
        if (stack <= 7 and options_idx = 4)
            options_idx := 3
    }
    else
    {
        options_idx := (options_idx >= 5? 2 : options_idx + 1)
        if (stack <= 7 and options_idx = 4)
            options_idx := 5
    }
    GuiControl, , StackSize, % cstack_options[options_idx]
    cstack_values[stack] := options_idx
    return
}
if (control_ = "Hide Unique Items Above Tier:")
{
    GuiControlGet, current,, UniqTierHide
    if (A_GuiEvent = "RightClick")
        current := (current <= 1? 1 : current - 1)
    else
        current := (current >= 5? 5 : current + 1)
    GuiControl, , UniqTierHide, % Format("{:2}", current)
    return
}
if (control_ = "Hacky" and not FlaskVal = -1)
{
    FlaskVal := Mod(FlaskVal + 1, 3)
    flasks[Flask][1] := FlaskVal
    GuiControl, , FlaskShow, % flvl_options[flasks[Flask][1] + 1]
}
if (control_ = "PortalHide")
{
    if (A_GuiEvent = "RightClick")
    {
        portal_stack := (portal_stack <= 1? 5 : portal_stack - 1)
    }
    else
    {
        portal_stack := (portal_stack >= 5? 1 : portal_stack + 1)
    }
    GuiControl, , PortalText, % cstack_options[portal_stack]
}
if (control_ = "WisdomHide")
{
    if (A_GuiEvent = "RightClick")
    {
        wisdom_stack := (wisdom_stack <= 1? 5 : wisdom_stack - 1)
    }
    else
    {
        wisdom_stack := (wisdom_stack >= 5? 1 : wisdom_stack + 1)
    }
    GuiControl, , WisdomText, % cstack_options[wisdom_stack]
}
if (control_ = "RGB Items Shown:")
{
    if (A_GuiEvent != "RightClick"){
        if (rgbsize = "medium")
            rgbsize := "large"
        if (rgbsize = "small")
            rgbsize := "medium"
        if (rgbsize = "none")
            rgbsize := "small"
    }else{
        if (rgbsize = "small")
            rgbsize := "none"
        if (rgbsize = "medium")
            rgbsize := "small"
        if (rgbsize = "large")
            rgbsize := "medium"
    }
    ToolTip, % rgbtooltip[rgbsize]
    SetTimer, RemoveToolTip, -2500
    GuiControl, , RGBHide, % Format("{:T}", rgbsize)
}
if (control_ = "Min Blight Oil:")
{
    if (A_GuiEvent = "RightClick")
        min_oil := min_oil > 1 ? min_oil - 1 : 1
    else
        min_oil := min_oil < 14 ? min_oil + 1 : 14
    GuiControl, , BlightOil, % oils[min_oil]
}
return

RemoveToolTip:
ToolTip
return

; Flask Dropdown List
FlaskDDL:
Gui, Submit, NoHide
FlaskVal := flasks[flask][1]
GuiControl, , FlaskShow, % flvl_options[flasks[flask][1] + 1]
return

; Profile Dropdown List
ProfDDL:
Gui, Submit, NoHide
if (Prof = active_profile)
    return
RunWait, python %py_prog_path% set_active_profile %Prof%, , Hide
Reload
ExitApp

; Gem Slider
GemSlider:
Gui, Submit, NoHide
gemmin := gemslider
GuiControl,, gemtext, Minimum Gem Quality: %gemmin%`%
return

; Flask Slider
FlaskSlider:
Gui, Submit, NoHide
flaskmin := flaskslider
GuiControl, , flasktext, Minimum Flask Quality: %flaskmin%`%
return

FlaskHA:
flaskmin := -1
GuiControl, , flasktext, Minimum Flask Quality: N/A
GuiControl, , flaskslider, 1
return

GemHA:
gemmin := -1
GuiControl, , gemtext, Minimum Gem Quality: N/A
GuiControl, , gemslider, 1
return

; ???
MsgBox(Message := "Press Ok to Continue.", Title := "", Type := 0, B1 := "", B2 := "", B3 := ""
        , Time := "") {
    if (Title = "")
        Title := A_ScriptName
    if (B1 != "") || (B2 != "") || (B3 != "")
        SetTimer, ChangeButtonNames, -10
    MsgBox, % Type, % Title, % Message, % Time
    Return

    ChangeButtonNames:
        IfWinNotExist, %Title%
            Return
        WinActivate, % Title
        ControlSetText, Button1, % (B1 = "") ? "Ok" : B1, % Title
        Try ControlSetText, Button2, % (B2 = "") ? "Cancel" : B2, % Title
        Try ControlSetText, Button3, % (B3 = "") ? "Close" : B3, % Title
    Return
}

; Clipboard Rule Matching
Clip_:
FileDelete, %ahk_out_path%
FileDelete, %py_out_path%
FileAppend, % Clipboard, %ahk_out_path%
RunWait, python %py_prog_path% get_rule_matching_item %active_profile%, , Hide
FileRead, py_out_text, %py_out_path%
if (py_out_text = "")
{
    MsgBox, No Matched Rule
    return
}
idx := 0
type_tag := ""
tier_tag := ""
rule := ""
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
visi := ""
if (InStr(py_out_text, "Show #")){
    MsgBox(rule, "Matched Rule" , 3 , "Hide", "Disable", "Show")
    IfMsgBox Yes
        visi := "hide"
    IfMsgBox No
        visi := "disable"
} else if (InStr(py_out_text, "Hide #")){
    MsgBox(rule, "Matched Rule" , 3 , "Show", "Disable", "Hide")
    IfMsgBox Yes
        visi := "show"
    IfMsgBox No
        visi := "disable"
} else {
    MsgBox(rule, "Matched Rule" , 3 , "Show", "Hide", "Disable")
    IfMsgBox Yes
        visi := "show"
    IfMsgBox No
        visi := "hide"
}
if (visi != ""){
    RunWait, python %py_prog_path% set_rule_visibility "%type_tag%" %tier_tag% %visi%
        . %active_profile%, , Hide
}
return

; Write all filter modifications to one file, send it over to python
Update_:
Gui, Hide
ToolTip
FileAppend, abc, %ahk_out_path%
FileDelete, %ahk_out_path%
for idx in curr_txt
{
    if (curr_val[idx] != curr_val_start[idx])
        FileAppend, % "set_currency_tier """ curr_txt[idx] """ " curr_val[idx] "`n" , %ahk_out_path%
    curr_val_start[idx] := curr_val[idx]
}
for idx in rare_txt
{
    if (rare_val[idx] != rare_val_start[idx])
        FileAppend, % "set_chaos_recipe_enabled_for """rare_txt[idx] """ " rare_val[idx] "`n", %ahk_out_path%
    rare_val_start[idx] := rare_val[idx]
}
GuiControlGet, current_currhide,, CurrTierHide
GuiControlGet, current_maphide,, MapTierHide
GuiControlGet, current_uniqhide,, UniqTierHide
if (current_currhide != currhide)
{
    FileAppend, % "set_hide_currency_above_tier" current_currhide "`n", %ahk_out_path%
    if (current_currhide > currhide)
    {
        Loop, % current_currhide - currhide
        {
            idx := currhide + A_Index
            FileAppend, % "set_currency_min_visible_stack_size " idx " 1`n", %ahk_out_path%
        }
    }
}
currhide := current_currhide
Loop, % 9 - currhide
{
    tier := % A_Index + currhide
    tierval := cstack_values[tier]
    if (tierval != cstack_values_base[tier])
    {
        stacksize := cstack_options[tierval]
        stacksize := (stacksize = "None"? "hide_all" : stacksize)
        FileAppend, % "set_currency_min_visible_stack_size " tier " " stacksize "`n", %ahk_out_path%
        cstack_values_base[tier] := tierval
    }
}
if (current_maphide != maphide)
    FileAppend, % "set_hide_maps_below_tier " current_maphide "`n", %ahk_out_path%
maphide := current_maphide
if (current_uniqhide != uniqhide)
    FileAppend, % "set_hide_unique_items_above_tier " current_uniqhide "`n", %ahk_out_path%
uniqhide := current_uniqhide
if (base_portstack != portal_stack){
    stacksize := cstack_options[portal_stack]
    stacksize := (stacksize = "None"? "hide_all" : stacksize)
    stacksize := (stacksize = "All"? "1" : stacksize)
    FileAppend, % "set_currency_min_visible_stack_size tportal " stacksize "`n", %ahk_out_path%
}
base_portstack := portal_stack
if (base_wisstack != wisdom_stack){
    stacksize := cstack_options[wisdom_stack]
    stacksize := (stacksize = "None"? "hide_all" : stacksize)
    stacksize := (stacksize = "All"? "1" : stacksize)
    FileAppend, % "set_currency_min_visible_stack_size twisdom " stacksize "`n", %ahk_out_path%
}
base_wisstack := wisdom_stack
if (base_gemmin != gemmin){
    FileAppend, % "set_gem_min_quality " gemmin "`n", %ahk_out_path%
}
base_gemmin := gemmin
if (base_flaskmin != flaskmin){
    FileAppend, % "set_flask_min_quality " flaskmin "`n", %ahk_out_path%
}
base_flaskmin := flaskmin
if (base_rgbsize != rgbsize){
    FileAppend, % "set_rgb_item_max_size " rgbsize "`n", %ahk_out_path%
}
base_rgbsize := rgbsize
if (min_oil != base_min_oil){
    FileAppend, % "set_lowest_visible_oil """ oils[min_oil] " Oil""`n", %ahk_out_path%
}
base_min_oil := min_oil
; TRANSLATE TO EXACT TIER
for idx, val in flasks
{
    if (val[1] != val[2])
    {
        if (val[1] == 0) ; hide
        {
            FileAppend, % "set_flask_visibility """ idx """ 0`n", %ahk_out_path%
            FileAppend, % "set_high_ilvl_flask_visibility """ idx """ 0`n", %ahk_out_path%
        }
        if (val[1] == 1) ; show all
        {
            FileAppend, % "set_flask_visibility """ idx """ 1`n", %ahk_out_path%
        }
        if (val[1] == 2) ; show high lvl
        {
            FileAppend, % "set_flask_visibility """ idx """ 0`n", %ahk_out_path%
            FileAppend, % "set_high_ilvl_flask_visibility """ idx """ 1`n", %ahk_out_path%
        }
    }
    val[2] := val[1]
}
RunWait, python %py_prog_path% run_batch %active_profile%, , Hide
Gui, Destroy
return
;ExitApp

Cancel_:
Gui, Destroy
ToolTip
for idx in curr_txt
{
    curr_val[idx] := curr_val_start[idx]
}
for idx in rare_txt
{
    rare_val[idx] := rare_val_start[idx]
}
for idx in cstack_values
{
    cstack_values[tier] := cstack_values_base[tier]
}
portal_stack := base_portstack 
wisdom_stack := base_wisstack
gemmin := base_gemmin
flaskmin := base_flaskmin
rgbsize := base_rgbsize
min_oil := base_min_oil
for idx, val in flasks
{
    val[1] := val[2]
}
return
;ExitApp

F7::
goto GuiBuild
;Reload
return
;ExitApp

F12::
RunWait, python %py_prog_path% import_downloaded_filter %active_profile%,  , Hide
Reload
ExitApp
