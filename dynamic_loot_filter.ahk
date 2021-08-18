#NoEnv
#SingleInstance Force
SendMode Input
SetWorkingDir %A_ScriptDir%

; File Paths for Python program/input/output
py_prog_path:= "backend_cli.py"
py_out_path:="backend_cli.output"
ahk_out_path:="ahkgui.output"

; Valid item types
curr_valid := ["Exalted Orb", "Orb of Alteration" , "Blessed Orb" , "Blacksmith's Whetstone" , "Armourer's Scrap" , "Glassblower's Bauble" , "Orb of Transmutation" , "Orb of Augmentation" , "Scroll of Wisdom" , "Portal Scroll" , "Chromatic Orb" , "Jeweller's Orb" , "Orb of Chance" , "Orb of Alchemy" , "Orb of Binding" , "Orb of Fusing" , "Vaal Orb" , "Orb of Horizons" , "Cartographer's Chisel" , "Regal Orb" , "Orb of Regret" , "Orb of Scouring" , "Gemcutter's Prism" ]
validstr := ""
for idx, val in curr_valid
	validstr .= "|" val
rare_valid := ["Weapons","Body Armours","Helmets","Gloves","Boots","Amulets","Rings","Belts"]
validstr2 := ""
for idx,val in rare_valid
	validstr2 .= "|" val

; Read starting filter data from python client
curr_txt := []
curr_ids := []
curr_val := []
rare_txt := []
rare_ids := []
rare_val := []
RunWait, python %py_prog_path% get_currency_tiers
FileRead, py_out_text, %py_out_path%
chaosflag := 0
Loop, parse, py_out_text, `n, `r
{
	If(A_LoopField = "")
		continue
	If(A_LoopField = "#Chaos"){
		chaosflag := 1
		continue
	}
	If(not chaosflag){
		splits := StrSplit(A_LoopField, ";")
		If(InStr(validstr, splits[1])){
			curr_txt.Push(splits[1])
			curr_val.Push(splits[2])
		}
	}
	Else{
		If(InStr(validstr2, splits[1]))
		{
			rare_txt.Push(splits[1])
			rare_val.Push(splits[2])
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

; Currency GUI 
Gui, Font, s10
; Text
For idx, val in curr_txt
{
	height := -10 + 20 * idx
	Gui, Add, Text, x10 y%height% grmbhack, % Format("{:-55}",val)
	Gui, Add, Text, % "backgroundtrans x" 180 " y" height " v" curr_ids[idx], % curr_val[idx]
}
; Buttons
Gui, Font, S8 norm, Arial
Gui, Add, Button, x130 y558 gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x10 y558 gCancel_ BackgroundTrans, Cancel
Gui, Add, Button, x72 y558 gRare_ BackgroundTrans, Rares
; Options
Gui, -border
Gui, Show, w200

; Rares Gui
Gui 2: Default
Gui, Font, s10
; Text
For idx, val in rare_txt
{
	height := -10 + 20  * idx
	Gui, Add, Text, x10 y%height% grmbhack, % Format("{:-55}", val)
	Gui, Add, Text, % "backgroundtrans x" 180 " y" height " v" rare_ids[idx], % rare_val[idx]
}
; Buttons
Gui, Font, S8 norm, Arial
Gui, Add, Button, x130 y558 gUpdate_ BackgroundTrans, Update
Gui, Add, Button, x10 y558 gCancel_ BackgroundTrans, Cancel
Gui, Add, Button, x64 y558 gCurr_ BackgroundTrans, Currency
; Options
Gui, -border
Gui, Show, Hide w200

; Non-Button Clicks
; Both RMB and LMB lead here
rmbhack:
GuiContextMenu:
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
		GuiControl,,% rare_ids[idx], % rare_val[idx] = 0? 0 : 1
		return
	}
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
return

; Write all filter modifications to one file, send it over to python
Update_:
Gui, Hide
FileDelete, %ahk_out_path%
for idx in curr_txt
{
	FileAppend, % curr_txt[idx] ":" curr_val[idx] "`r`n" , %ahk_out_path%
}
FileAppend, #Chaos`r`n, %ahk_out_path%
for idx in rare_txt
{
	FileAppend, % rare_txt[idx] ":" rare_val[idx] "`r`n", %ahk_out_path%
}
Run, python %py_prog_path% update_filter
ExitApp

Cancel_:
Gui, Hide
ExitApp
