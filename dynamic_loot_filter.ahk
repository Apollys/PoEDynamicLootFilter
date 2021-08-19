#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; File Paths for Python program/input/output
py_prog_path:= "backend_cli.py"
py_out_path:="backend_cli.output"
ahk_out_path:="backend_cli.input"

; Valid item types
curr_valid := ["Exalted Orb", "Orb of Alteration" , "Blessed Orb" , "Blacksmith's Whetstone" , "Armourer's Scrap" , "Glassblower's Bauble" , "Orb of Transmutation" , "Orb of Augmentation" , "Scroll of Wisdom" , "Portal Scroll" , "Chromatic Orb" , "Jeweller's Orb" , "Orb of Chance" , "Orb of Alchemy" , "Orb of Binding" , "Orb of Fusing" , "Vaal Orb" , "Orb of Horizons" , "Cartographer's Chisel" , "Regal Orb" , "Orb of Regret" , "Orb of Scouring" , "Gemcutter's Prism" ]
validstr := ""
for idx, val in curr_valid
	validstr .= "|" val
rare_valid := ["Weapons","Body Armours","Helmets","Gloves","Boots","Amulets","Rings","Belts"]
validstr2 := ""
for idx,val in rare_valid
	validstr2 .= "|" val
; Coloring from consts.py
rare_colors := {"Weapons" : "c80000", "Body Armours" : "ff00ff", "Helmets" : "ff7200", "Gloves" : "ffe400", "Boots" : "00ff00", "Amulets" : "00ffff", "Rings" : "4100bd", "Belts" : "0000c8"}

; Read starting filter data from python client
curr_txt := []
curr_ids := []
curr_val := []
curr_val_start := []
rare_txt := []
rare_ids := []
rare_val := []
rare_val_start := []
RunWait, python %py_prog_path% get_all_currency_tiers
FileRead, py_out_text, %py_out_path%
chaosflag := 0
Loop, parse, py_out_text, `n, `r
{
	If(A_LoopField = "")
		continue
	splits := StrSplit(A_LoopField, ";")
	If(InStr(validstr, splits[1])){
		curr_txt.Push(splits[1])
		curr_val.Push(splits[2])
		curr_val_start.Push(splits[2])
	}
}
RunWait, python %py_prog_path% get_all_chaos_recipe_statuses
FileRead, py_out_text, %py_out_path%
Loop, parse, py_out_text, `n, `r
{
	If(A_LoopField = "")
		continue
	splits := StrSplit(A_LoopField, ";")
	If(InStr(validstr2, splits[1]))
	{
		rare_txt.Push(splits[1])
		rare_val.Push(splits[2])
		rare_val_start.Push(splits[2])
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

; Currency GUI 
Gui, Font, S18 cB0B0B0, Arial
; Text
For idx, val in curr_txt
{
	height := -20 + 25 * idx
	Gui, Add, Text, x10 y%height% grmbhack, % Format("{:-55}",val)
	Gui, Add, Text, % "backgroundtrans x" 280 " y" height " v" curr_ids[idx], % curr_val[idx]
}
; Buttons
Gui, Font, S10 norm bold, Arial
height := height + 28
Gui, Add, Button, x234 y%height% gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x10 y%height% gCancel_ BackgroundTrans, Cancel
Gui, Add, Button, x78 y%height% gRare_ BackgroundTrans, Chaos Rares
Gui, Add, Button, x182 y%height% gMisc_ BackgroundTrans, Misc
; Options
Gui, -border
Gui, Color, 606060
Gui, Show, w300

; Rares Gui
Gui 2: Default
Gui, Font, S18, Arial
; Text
For idx, val in rare_txt
{
	height := -30 + 40  * idx
	Gui, Font, % "c" rare_colors[val]
	Gui, Add, Text, x10 y%height% grmbhack, % Format("{:-55}", val)
	Gui, Font, S36, Wingdings
	Gui, Font, % "c" (rare_val[idx]? "Blue" : "Red")
	Gui, Add, Text, % "backgroundtrans x" 180 " y" (height - 15) " v" rare_ids[idx], % (rare_val[idx]? Chr(252) : Chr(251))
	Gui, Font, S18, Arial
}
; Buttons
height := height + 35
Gui, Font, S10 norm bold, Arial
Gui, Add, Button, x155 y%height% gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x8 y%height% gCancel_ BackgroundTrans, Cancel
Gui, Add, Button, x88 y%height% gCurr_ BackgroundTrans, Main
; Options
Gui, -border
Gui, Color, 606060
Gui, Show, Hide w220

; Misc GUI
Gui 3: Default
Gui, Font, S18 cB0B0B0, Arial
; Hide Map Tiers
maphide := 1
currhide := 1
Gui, Add, Text, x10 y10 grmbhack, % "Hide Maps Below Tier:                    "
Gui, Add, Text, x320 y10 w30 BackgroundTrans vMapTierHide, % maphide
; Hide Currency Tiers
Gui, Add, Text, x10 y40 grmbhack, % "Hide Currency Above Tier:                "
Gui, Add, Text, x320 y40 w30 BackgroundTrans vCurrTierHide, % currhide
; Buttons
height := 75
Gui, Font, S10 norm bold, Arial
Gui, Add, Button, x285 y%height% gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x8 y%height% gCancel_ BackgroundTrans, Cancel
Gui, Add, Button, x145 y%height% gCurr_ BackgroundTrans, Main
; Options
Gui, -border
Gui, Color, 606060
Gui, Show, Hide w350

; Non-Button Clicks
; Both RMB and LMB lead here
rmbhack:
GuiContextMenu:
2GuiContextMenu:
3GuiContextMenu:
control_ := RTrim(A_GuiControl)
For idx, val in curr_txt
{
	If (control_ = val)
	{
		GuiControlGet, current,,% curr_ids[idx]
		If (A_GuiEvent = "RightClick")
			current := Mod(current + 7, 9) + 1
		Else
			current := Mod(current, 9) + 1
		GuiControl,,% curr_ids[idx], % current
		curr_val[idx] := current
		return
	}
}
For idx, val in rare_txt
{
	If (control_ = val)
	{
		GuiControlGet, current,,% rare_ids[idx]
		rare_val[idx]:= !rare_val[idx]
		GuiControl, % "+c" (rare_val[idx]? "Blue" : "Red"), % rare_ids[idx]
		GuiControl,,% rare_ids[idx], % (rare_val[idx]? Chr(252) : Chr(251))
		return
	}
}
If (control_ = "Hide Maps Below Tier:")
{
	GuiControlGet, current,, MapTierHide
	If (A_GuiEvent = "RightClick")
		current := Mod(current + 12, 14) + 1
	Else
		current := Mod(current, 14) + 1
	GuiControl,, MapTierHide, % current
	return
}
If (control_ = "Hide Currency Above Tier:")
{
	GuiControlGet, current,, CurrTierHide
	If (A_GuiEvent = "RightClick")
		current := Mod(current + 7, 9) + 1
	Else
		current := Mod(current, 9) + 1
	GuiControl,, CurrTierHide, % current
	return
}
return

; Swap visible GUI
Rare_:
Gui, 2: Show, Restore
Gui, 1: Hide
return

Curr_:
Gui, 1: Show, Restore
Gui, 2: Hide
Gui, 3: Hide
return

Misc_:
Gui, 3: Show, Restore
Gui, 1: Hide
return

; Write all filter modifications to one file, send it over to python
Update_:
Gui, Hide
FileDelete, %ahk_out_path%
for idx in curr_txt
{
	if(curr_val[idx] != curr_val_start[idx])
		FileAppend, % "set_currency_tier " curr_txt[idx] " " curr_val[idx] "`r`n" , %ahk_out_path%
}
for idx in rare_txt
{
	if(rare_val[idx] != rare_val_start[idx])
		FileAppend, % "set_chaos_recipe_enabled_for "rare_txt[idx] " " rare_val[idx] "`r`n", %ahk_out_path%
}
; Weird that AHK needs this line, luckily program about to exit
Gui 3: Default
GuiControlGet, current_currhide,, CurrTierHide
GuiControlGet, current_maphide,, MapTierHide
if (current_currhide != currhide)
	FileAppend, % "set_hide_currency_above_tier " current_currhide "`r`n", %ahk_out_path%
if (current_maphide != maphide)
	FileAPpend, % "set_hide_map_below_tier " current_maphide "`r`n", %ahk_out_path%
Run, python %py_prog_path% batch_process
ExitApp

Cancel_:
Gui, Hide
ExitApp
