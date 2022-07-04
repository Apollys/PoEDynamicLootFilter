; Returns an id that can be used in GuiControl commands:
;  - strips leading "v" off variable names
;  - strips leading "hwnd" off hwnd ids, and applies one level of variable name "dereferencing"
; Displays a warning if a control with the returned ID does not exist.
NormalizedId(hwnd_or_v_id) {
	StringLower normalized_id, hwnd_or_v_id
    if (StartsWith(normalized_id, "v")) {
        normalized_id := SubStr(normalized_id, 2)  ; trim starting "v"
    } else if (StartsWith(normalized_id, "hwnd")) {
        normalized_id := SubStr(normalized_id, 5)  ; trim starting "hwnd")
        normalized_id := %normalized_id%  ; "dereference" one level of variable name wrapping
    }
    ; Check corresponding control exists
    GuiControlGet, _, , %normalized_id%
    if (ErrorLevel != 0) {
		DebugMessage("Warning: could not find control with id: " hwnd_or_v_id)
	}
    return normalized_id
}

; Takes either a GUI element variable ("vMyGuiElement") or an HWND id ("HWNDhMyGuiElement"),
; and calls GuiGetControl with the appropriate syntax.
; Convention for AltSubmit: assumes AltSubmit is always initially off, and always ensures AltSubmit is
; off after this function call. (Can't always set AltSubmit off, some control types don't allow this option)
GuiControlGetHelper(id, get_index:=False) {
    normalized_id := NormalizedId(id)
    if (get_index) {
        GuiControl, +AltSubmit, %normalized_id%
    }
    GuiControlGet, output_value, , %normalized_id%
    if (get_index) {
        GuiControl, -AltSubmit, %normalized_id%
    }
    return output_value
}

; * I'm not sure which of the below functions require an hwnd_id, and which can
; be used with a v-Variable name. When in doubt, I named the parameter hwnd_id.

GuiControlAddItem(hwnd_id, new_item_text) {
    normalized_id := NormalizedId(hwnd_id)
    GuiControl, , %normalized_id%, %new_item_text%
}

; Note: this may only work for ListBox and ComboBoxes
GuiControlRemoveItemAtIndex(hwnd_id, index) {
    normalized_id := NormalizedId(hwnd_id)
	ahk_id_string := "ahk_id " normalized_id
    Control, Delete, %index%, , %ahk_id_string%
}

; Note: this may only work for ListBox and ComboBoxes
; Use ControlGet (Not GuiControlGet) to get full text of a ListBox, separated by "`n"
GuiControlRemoveItem(hwnd_id, item) {
    normalized_id := NormalizedId(hwnd_id)
	ahk_id_string := "ahk_id " normalized_id
    ControlGet, all_items_text, List, , , %ahk_id_string%
    items_list := StrSplit(all_items_text, "`n")
    for index, current_item in items_list {
        if (current_item == item) {
            GuiControlRemoveItemAtIndex(hwnd_id, index)
            return
        }
    }
}

; Note: this may only work for ListBox and ComboBoxes
GuiControlRemoveSelectedItem(hwnd_id) {
    normalized_id := NormalizedId(hwnd_id)
    selected_item_index := GuiControlGetHelper(normalized_id, get_index:=True)
    GuiControlRemoveItemAtIndex(hwnd_id, selected_item_index)
}

; Does *not* trigger associated gLabels
GuiControlSelectItem(hwnd_id, item_text) {
    normalized_id := NormalizedId(hwnd_id)
    GuiControl, ChooseString, %normalized_id%, %item_text%
}

; Does *not* trigger associated gLabels
GuiControlSelectIndex(hwnd_id, index) {
    normalized_id := NormalizedId(hwnd_id)
    GuiControl, Choose, %normalized_id%, %index%
}

; Does *not* trigger associated gLabels
GuiControlDeselectAll(hwnd_id) {
    normalized_id := NormalizedId(hwnd_id)
    GuiControl, Choose, %normalized_id%, 0
}

GuiControlSetText(id, text) {
    normalized_id := NormalizedId(id)
    GuiControl, , %normalized_id%, %text%

}

GuiControlClear(id) {
    GuiControlSetText(id, "")
}
