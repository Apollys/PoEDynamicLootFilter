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
rare_valid := ["WeaponsX", "Weapons3","Body Armours","Helmets","Gloves","Boots","Amulets","Rings","Belts"]
validstr2 := ""
for idx,val in rare_valid
	validstr2 .= "|" val
; Coloring from consts.py
rare_colors := {"WeaponsX" : "c80000", "Weapons3" : "c80000", "Body Armours" : "ff00ff", "Helmets" : "ff7200", "Gloves" : "ffe400", "Boots" : "00ff00", "Amulets" : "00ffff", "Rings" : "4100bd", "Belts" : "0000c8"}
; Flask stuff
flasks := {"Quicksilver Flask":[0,0], "Bismuth Flask":[0,0], "Amethyst Flask":[0,0], "Ruby Flask":[0,0], "Sapphire Flask":[0,0], "Topaz Flask":[0,0], "Aquamarine Flask":[0,0], "Diamond Flask":[0,0], "Jade Flask":[0,0], "Quartz Flask":[0,0], "Granite Flask":[0,0], "Sulphur Flask":[0,0], "Basalt Flask":[0,0], "Silver Flask":[0,0], "Stibnite Flask":[0,0], "Corundum Flask":[0,0], "Gold Flask":[0,0]}

; Read starting filter data from python client
curr_txt := []
curr_ids := []
curr_val := []
curr_val_start := []
rare_txt := []
rare_ids := []
rare_val := []
rare_val_start := []
FileDelete, %ahk_out_path%
FileAppend, get_all_currency_tiers`nget_all_chaos_recipe_statuses`nget_hide_map_below_tier`nget_currency_tier_visibility tportal`nget_currency_tier_visibility twisdom`nget_hide_currency_above_tier`n, %ahk_out_path%
RunWait, python %py_prog_path% run_batch , , Hide
FileRead, py_out_text, %py_out_path%
prog := 0
Loop, parse, py_out_text, `n, `r
{
	If(A_LoopField = "")
		continue
	If(InStr(A_LoopField, "@"))
	{
		prog := prog + 1
		continue
	}
	Switch prog
	{
	Case 0:
		splits := StrSplit(A_LoopField, ";")
		If(InStr(validstr, splits[1])){
			curr_txt.Push(splits[1])
			curr_val.Push(splits[2])
			curr_val_start.Push(splits[2])
		}
	Case 1:
		splits := StrSplit(A_LoopField, ";")
		If(InStr(validstr2, splits[1]))
		{
			rare_txt.Push(splits[1])
			rare_val.Push(splits[2])
			rare_val_start.Push(splits[2])
		}
	Case 2:
		maphide := A_LoopField
	Case 3:
		base_porthide := !A_LoopField
		PortalHide := base_porthide
	Case 4:
		base_wishide := !A_LoopField
		WisdomHide := base_wishide
	Case 5:
		currhide := A_LoopField
	}
}
fake_queue := []
FileDelete, %ahk_out_path%
For key in flasks
{
	FileAppend, is_flask_rule_enabled_for "%key%"`r`n, %ahk_out_path% 
	fake_queue.Push(key)
}
RunWait, python %py_prog_path% run_batch , , Hide
FileRead, py_out_text, %py_out_path%
idx := 1
Loop, parse, py_out_text, `n, `r
{
	If(A_LoopField = "")
		continue
	If(InStr(A_LoopField, "@"))
	{
		idx := idx + 1
		continue
	}
	flasks[fake_queue[idx]] := [A_LoopField, A_LoopField]
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
height:= 0
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
height := 0
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
Gui, Add, Text, x10 y10 grmbhack, % "Hide Maps Below Tier:                    "
Gui, Add, Text, x320 y10 w30 BackgroundTrans vMapTierHide, % maphide
; Hide Currency Tiers
Gui, Add, Text, x10 y40 grmbhack, % "Hide Currency Above Tier:                "
Gui, Add, Text, x320 y40 w30 BackgroundTrans vCurrTierHide, % currhide
; Portal/Wisdom
if (PortalHide)
	Gui, Font, Strike
Gui, Add, Text, x10 y70 grmbhack vPortalHide, Portal Scroll
Gui, Font, norm
if (WisdomHide)
	Gui, Font, Strike
Gui, Add, Text, x180 y70 grmbhack vWisdomHide, Wisdom Scroll
Gui, Font, norm
; Flask DDL
FlaskShow := -1
FlaskString := ""
for key, val in flasks
	FlaskString .= key "|"
RTrim(FlaskString, "|")
Gui, Add, DropDownList, x10 y100 vFlask gFlaskDDL, % FlaskString
Gui, Font, c606060
Gui, Add, Text, x285 y105 grmbhack, Hacky
Gui, Font, S36, Wingdings
Gui, Add, Text, backgroundtrans x285 w40 y93 vFlaskShow, 
; Buttons
height := 145
Gui, Font, cB0B0B0 S10 norm bold, Arial
Gui, Add, Button, x285 y%height% gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x8 y%height% gCancel_ BackgroundTrans, Cancel
Gui, Add, Button, x145 y%height% gCurr_ BackgroundTrans, Main
; Options
Gui, -border
Gui, Color, 606060
Gui, Show, Hide w350
return

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
		;GuiControlGet, current,,% curr_ids[idx]
		current := curr_val[idx]
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
		;GuiControlGet, current,,% rare_ids[idx]
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
		current := Mod(current + 14, 16) + 1
	Else
		current := Mod(current, 16) + 1
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
If (control_ = "Hacky" and not FlaskShow = -1)
{
	FlaskShow := !FlaskShow
	flasks[Flask][1] := FlaskShow
	GuiControl, % "+c" (FlaskShow? "Blue" : "Red"), FlaskShow
	GuiControl,, FlaskShow, % (FlaskShow? Chr(252) : Chr(251))
}
If (control_ = "PortalHide")
{
	Gui, Font, S18 cB0B0B0 norm, Arial
	PortalHide := !PortalHide
	if (PortalHide)
		Gui, Font, Strike
	GuiControl, Font, PortalHide
}
If (control_ = "WisdomHide")
{
	Gui, Font, S18 cB0B0B0 norm, Arial
	WisdomHide := !WisdomHide
	if (WisdomHide)
		Gui, Font, Strike
	GuiControl, Font, WisdomHide
}
return

; Flask Dropdown List
FlaskDDL:
Gui, Submit, NoHide
FlaskShow := flasks[Flask][1]
GuiControl, % "+c" (FlaskShow? "Blue" : "Red"), FlaskShow
GuiControl,, FlaskShow, % (FlaskShow? Chr(252) : Chr(251))
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
		FileAppend, % "set_currency_tier """ curr_txt[idx] """ " curr_val[idx] "`n" , %ahk_out_path%
	curr_val_start[idx] := curr_val[idx]
}
for idx in rare_txt
{
	if(rare_val[idx] != rare_val_start[idx])
		FileAppend, % "set_chaos_recipe_enabled_for """rare_txt[idx] """ " rare_val[idx] "`n", %ahk_out_path%
	rare_val_start[idx] := rare_val[idx]
}
; Weird that AHK needs this line, luckily program about to exit
; or not
Gui 3: Default
GuiControlGet, current_currhide,, CurrTierHide
GuiControlGet, current_maphide,, MapTierHide
if (current_currhide != currhide)
	FileAppend, % "set_hide_currency_above_tier " current_currhide "`n", %ahk_out_path%
 currhide := current_currhide
if (current_maphide != maphide)
	FileAppend, % "set_hide_map_below_tier " current_maphide "`n", %ahk_out_path%
maphide := current_maphide
if (base_porthide != PortalHide){
	FileAppend, % "set_currency_tier_visibility tportal " (PortalHide? "0":"1") "`n", %ahk_out_path%
}
base_porthide := PortalHide
if (base_wishide != WisdomHide){
	FileAppend, % "set_currency_tier_visibility twisdom " (WisdomHide? "0":"1") "`n", %ahk_out_path%
}
base_wishide := WisdomHide
for idx, val in flasks
{
;	MsgBox, % idx " " val[1] " " val[2]
	if (val[1] != val[2])
	{
		FileAppend, % "set_flask_rule_enabled_for """ idx """ " val[1] "`n", %ahk_out_path%
	}
}
RunWait, python %py_prog_path% run_batch , , Hide
Gui, 1: Hide
Gui, 2: Hide
Gui, 3: Hide
return
;ExitApp

Cancel_:
Gui, Hide
return
;ExitApp

F7::
Reload
ExitApp

F12::
Run, python %py_prog_path% import_downloaded_filter ,  , Hide
Reload
ExitApp