#Include consts.ahk
#Include general_helper.ahk
#Include gui_build.ahk  ; access constants defined in gui_build.ahk
#Include gui_helper.ahk
#Include poe_helper.ahk

; ========================== Profile ==========================

; Sets the active profile and reloads the script
ProfileDdlAction() {
	global g_active_profile
	target_profile := GuiControlGetHelper("vProfileDdl")
	if (target_profile == g_active_profile) {
		return
	}
	RunBackendCliFunction("set_active_profile " Quoted(target_profile))
	Reload
}

; =============================== HOTKEYS ======================================

; Assuming an input from ahk gui Hotkey entry box, this function
; will return True IFF all characters in the given string are modifer keys (control, alt, or shift)
ModifiersOnly(keys) {
	last_key := SubStr(keys, 0)
	Return last_key == "!" or last_key == "^" or last_key == "+"
}

; g-label for gui hotkey entry box
; A_GuiControl will ALWAYS be HotkeyN (N = 1,2...) when entering this function, where N is the updated hotkey
UpdateHotkey() {
	global g_ui_data_dict
	hotkey_box_index := SubStr(A_GuiControl, 0) ; Last char of A_GuiControl
	old_hotkey_split := StrSplit(g_ui_data_dict["hotkeys"][hotkey_box_index], ";")
	GuiControlGet, pressed, , %A_GuiControl% ; New inputted hotkey is assigned to variable pressed
	; If pressed blank, hotkey entry failed, restore Gui Entry with data from g_ui_data_dict
	if (pressed == ""){
		GuiControl, , %A_GuiControl%, % old_hotkey_split[2]
	}
	; confirm pressed is a complete hotkey then update g_ui_data_dict and call backend
	else if not ModifiersOnly(pressed) {
		function_name := RemovedSpaces(old_hotkey_split[1])
		; disable old hotkey, enable new hotkey, update dictionary and backend
		Hotkey, % old_hotkey_split[2], , off
		Hotkey, %pressed%, %function_name%
		g_ui_data_dict["hotkeys"][hotkey_box_index] := old_hotkey_split[1] ";" pressed
		RunBackendCliFunction("set_hotkey " Quoted(old_hotkey_split[1]) " " Quoted(pressed))
		ClearFocus()
	}
}

ClearFocus() {
	global hTitle
	GuiControl, Focus, %hTitle%
}

; ========================== Currency ==========================

; Helper function
; Uses "GuiControl, Choose/ChooseString", so it does *not* trigger associated gLabels
SelectCurrency(base_type) {
	global kNumCurrencyTiers
	global g_ui_data_dict
	tier := g_ui_data_dict["currency_to_tier_dict"][base_type]
	; Select in Currency DropDownList
	GuiControlSelectItem("HWNDhCurrencyNamesDdl", base_type)
	; Select in Currency Tier ListBox (and deselect others)
    Loop %kNumCurrencyTiers% {
		hwnd_id := "HWNDhCurrencyTierListBoxT" A_Index
        if (A_Index == tier) {
			GuiControlSelectItem(hwnd_id, base_type)
        } else {
            GuiControlDeselectAll(hwnd_id)
        }
    }
	; Select target tier
	GuiControlSelectItem("HWNDhCurrencyTargetTierDdl", "T" tier)
}

; Select currency in tier boxes (and deselect any others), display current tier in target tier DDL
CurrencyNamesDdlAction(hwnd_id) {
	global g_ui_data_dict
	base_type := GuiControlGetHelper(hwnd_id)
	SelectCurrency(base_type)
}

; Select currency in names DDL, display current tier in target tier DDL
CurrencyTierListBoxAction(hwnd_id) {
	base_type := GuiControlGetHelper(hwnd_id)
	SelectCurrency(base_type)
}

; Move currency to selected target tier, update current tier text
; Command syntax: set_currency_to_tier <base_type> <tier>
CurrencyTargetTierDdlAction() {
	global g_ui_data_dict, g_ui_changes
	base_type := Trim(GuiControlGetHelper("HWNDhCurrencyNamesDdl"))
	if (StartsWith(base_type, "Select ")) {
		return
	}
	target_tier := LTrim(GuiControlGetHelper("HWNDhCurrencyTargetTierDdl"), "T")
	initial_tier := g_ui_data_dict["currency_to_tier_dict"][base_type]
	g_ui_data_dict["currency_to_tier_dict"][base_type] := target_tier
	GuiControlRemoveItem("HWNDhCurrencyTierListBoxT" initial_tier, base_type)
	GuiControlAddItem("HWNDhCurrencyTierListBoxT" target_tier, base_type)
	SelectCurrency(base_type)
	; Create and store corresponding backend command
    backend_function_call := "set_currency_to_tier " Quoted(base_type) " " target_tier
    g_ui_changes.push(backend_function_call)
}

; Currency tier stack sizes do *not* have a gLabel

; Select corresponding stack size in stack size DDL
SplinterTypeDdlAction() {
	global g_ui_data_dict, kSplinterStackSizes
	base_type := GuiControlGetHelper("HWNDhSplinterTypeDdl")
	stack_size := g_ui_data_dict["splinter_min_visible_stack_sizes"][base_type]
	if (stack_size == "") {
		stack_size := 1
	}
	stack_size_index := Find(stack_size, kSplinterStackSizes)
	GuiControlSelectIndex("HWNDhSplinterStackSizeDdl", stack_size_index)
}

; Save new stack size threshold for select splinter type
; Command: set_splinter_min_visible_stack_size <base_type> <stack_size>
SplinterStackSizeDdlAction() {
	global g_ui_data_dict, g_ui_changes, kSplinterStackSizes
	base_type := Trim(GuiControlGetHelper("HWNDhSplinterTypeDdl"))
	stack_size_index := GuiControlGetHelper("HWNDhSplinterStackSizeDdl", get_index:=True)
	stack_size := kSplinterStackSizes[stack_size_index]
	if (StartsWith(base_type, "Select ")) {
		return
	}
    ; Update GUI internal state
	g_ui_data_dict["splinter_min_visible_stack_sizes"][base_type] := stack_size
    ; Convert to corresponding backend function call and store it
    backend_function_call := "set_splinter_min_visible_stack_size " Quoted(base_type) " " stack_size
    g_ui_changes.push(backend_function_call)
    return
}

; ========================== Chaos Recipe Items ==========================

; Chaos recipe rares do *not* have a gLabel

; ========================== Hide Maps Below Tier ==========================

; Hide maps below tier does *not* have a gLabel

; ========================== General BaseTypes ==========================

; Helper function
AddLineToGeneralBaseTypesListBox(base_type, rare_only_flag) {
    list_box_line := "[" (rare_only_flag ? "Rare" : "Any") "] " base_type
	GuiControlAddItem("HWNDhGeneralBaseTypesListBox", list_box_line)
}

; Command: set_basetype_visibility <base_type> <visibility_flag: int> <(optional) rare_only_flag: int>
GeneralBaseTypesAdd() {
	global g_ui_changes
	base_type := Trim(GuiControlGetHelper("HWNDhGeneralBaseTypesEditBox"))
	rare_only_flag := GuiControlGetHelper("HWNDhGeneralBaseTypesRareCheckBox")
    if ((base_type == "") or StartsWith(base_type, "Enter ")) {
        return
    }
    ; Convert to corresponding backend function call and store it
    show_flag := 1
    backend_function_call := "set_basetype_visibility " Quoted(base_type) " " show_flag " " rare_only_flag
    g_ui_changes.push(backend_function_call)
	AddLineToGeneralBaseTypesListBox(base_type, rare_only_flag)
}

GeneralBaseTypesRemove() {
	global g_ui_changes
	selected_item_text := Trim(GuiControlGetHelper("HWNDhGeneralBaseTypesListBox"))
    if (selected_item_text == "") {
        return
    }
    ; Parse text into base_type, rare_only_flag
    ; "[Rare] Hubris Circlet" -> ["", "Rare", " Hubris Circlet"]
    split_result := StrSplit(selected_item_text, ["[","]"])
    ; rare_only_flag := (split_result[2] != "Any")  ; AHK arrays are 1-indexed
    base_type := SubStr(split_result[3], 2)  ; substring starting at second character
    ; Convert to corresponding backend function call and store it
    ; Note: rare_only_flag is omitted when disabling a BaseType
    show_flag := 0
    backend_function_call := "set_basetype_visibility " Quoted(base_type) " " show_flag
    g_ui_changes.push(backend_function_call)
	GuiControlRemoveSelectedItem("HWNDhGeneralBaseTypesListBox")
}

; ========================== Flask BaseTypes ==========================

; Helper function
AddLineToFlaskBaseTypesListBox(base_type, high_ilvl_only_flag) {
    list_box_line := "[" (high_ilvl_only_flag ? "84+" : "Any") "] " base_type
	GuiControlAdditem("HWNDhFlaskListBox", list_box_line)
}

; Command: set_flask_visibility <base_type: str> <visibility_flag: int> <(optional) high_ilvl_flag: int>
FlaskAdd() {
	global g_ui_changes
	base_type := Trim(GuiControlGetHelper("HWNDhFlaskDdl"))
	high_ilvl_only_flag := GuiControlGetHelper("HWNDhFlaskHighIlvlCheckBox")
	if (StartsWith(base_type, "Select ")) {
		return
	}
    ; Convert to corresponding backend function call and store it
    show_flag := 1
    backend_function_call := "set_flask_visibility " Quoted(base_type) " " show_flag " " high_ilvl_only_flag
    g_ui_changes.push(backend_function_call)
    ; Convert to UI list box line and add
    list_box_line := "[" (high_ilvl_only_flag ? "84+" : "Any") "] " base_type
    AddLineToFlaskBaseTypesListBox(base_type, high_ilvl_only_flag)
}

FlaskRemove() {
	global g_ui_changes
	selected_item_text := Trim(GuiControlGetHelper("HWNDhFlaskListBox"))
    if (selected_item_text == "") {
        return
    }
    ; Parse text into base_type, high_ilvl_only_flag
    ; "[84+] Quicksilver Flask" -> ["", "84+", " Quicksilver Flask"]
    split_result := StrSplit(selected_item_text, ["[","]"])
    ; high_ilvl_only_flag := (split_result[2] != "Any")  ; AHK arrays are 1-indexed
    base_type := SubStr(split_result[3], 2)  ; substring starting at second character
    ; Convert to corresponding backend function call and store it
    ; Note: high_ilvl_only_flag is omitted when disabling a BaseType
    show_flag := 0
    backend_function_call := "set_flask_visibility " Quoted(base_type) " " show_flag
    g_ui_changes.push(backend_function_call)
	GuiControlRemoveSelectedItem("HWNDhFlaskListBox")
}

; ========================== Tier Visibilities ==========================

; Tier visibilities do *not* have associated gLabels

; ========================== Quality and RGB Items ==========================

; Quality and RGB items do *not* have associated gLabels

; ========================== Socket Patterns ==========================

; Helper function
AddLineToSocketPatternsListBox(socket_pattern, item_slot) {
    list_box_line := "[" item_slot "] " socket_pattern
	GuiControlAdditem("HWNDhSocketPatternsListBox", list_box_line)
	GuiControlClear("HWNDhSocketPatternsListBox")
}

; Command: add_remove_socket_rule <socket_string: str> v<(optional) item_slot: str> <add_flag: bool>
SocketPatternsAdd() {
	global g_ui_changes
	socket_pattern := Trim(GuiControlGetHelper("HWNDhSocketPatternsEditBox"))
	item_slot := Trim(GuiControlGetHelper("HWNDhSocketPatternsItemSlotDdl"))
    StringUpper socket_pattern, socket_pattern
    if (StartsWith(item_slot, "Any")) {
        item_slot := "Any"
    }
    ; Convert to corresponding backend function call and store it
    add_flag := 1
    backend_function_call := "add_remove_socket_rule " Quoted(socket_pattern) " " Quoted(item_slot) " " add_flag
    g_ui_changes.push(backend_function_call)
    AddLineToSocketPatternsListBox(socket_pattern, item_slot)
}

SocketPatternsRemove() {
	global g_ui_changes
	selected_item_text := Trim(GuiControlGetHelper("HWNDhSocketPatternsListBox"))
    if (selected_item_text == "") {
        return
    }
    ; Parse text into socket_pattern, item_slot
    ; "[Body Armours] B-G-X-X" -> ["", "Body Armours", " B-G-X-X"]
    split_result := StrSplit(selected_item_text, ["[","]"])
    item_slot := split_result[2]  ; AHK arrays are 1-indexed
    socket_pattern := SubStr(split_result[3], 2)  ; substring starting at second character
    ; Convert to corresponding backend function call and store it
    add_flag := 0
    backend_function_call := "add_remove_socket_rule " Quoted(socket_pattern) " " Quoted(item_slot) " " add_flag
    g_ui_changes.push(backend_function_call)
	GuiControlRemoveSelectedItem("HWNDhSocketPatternsListBox")
}

; ========================== Item-Rule Matching ==========================

FindRuleMatchingClipboard() {
	global kBackendCliInputPath, kBackendCliOutputPath
	global g_ui_data_dict, g_active_profile
	FileDelete, %kBackendCliInputPath%
	FileDelete, %kBackendCliOutputPath%
	FileAppend, %Clipboard%, %kBackendCliInputPath%
	RunBackendCliFunction("get_rule_matching_item " Quoted(g_active_profile))
	FileRead, backend_cli_output, %kBackendCliOutputPath%
	if (backend_cli_output == "") {
		GuiControlSetText("vStatusMessageEditBox", "Found no rule matching item")
		GuiControl, Disable, ChangeMatchedRuleVisibilityButton
		return
	}
	GuiControlSetText("vMatchedRuleTextBox", backend_cli_output)
	target_visibility := InStr(backend_cli_output, "Show") ? "Hide" : "Show"
	GuiControlSetText("vChangeMatchedRuleVisibilityButton", target_visibility " Rule")
	enable_or_disable := (target_visibility == "Hide") ? "Disable" : "Enable"
	GuiControl, Enable, ChangeMatchedRuleVisibilityButton
	; Parse type and tier tags to be passed in to backend set_rule_visibility command
	; The first two lines of output will be `type_tag:<type_tag>` and `tier_tag:<tier_tag>`
	backend_cli_output_lines := ReadFileLines(kBackendCliOutputPath)
	type_tag := StrSplit(backend_cli_output_lines[1], ":")[2]
	tier_tag := StrSplit(backend_cli_output_lines[2], ":")[2]
	g_ui_data_dict["matched_rule_tags"] := [type_tag, tier_tag]
}

; Command: set_rule_visibility <type_tag> <tier_tag> <visibility: {show, hide, disable}>
ChangeMatchedRuleVisibility() {
	global g_ui_data_dict, g_active_profile
	button_text := GuiControlGetHelper("vChangeMatchedRuleVisibilityButton")
	target_visibility := InStr(button_text, "Show") ? "show" : "hide"
	type_tag := g_ui_data_dict["matched_rule_tags"][1]
	tier_tag := g_ui_data_dict["matched_rule_tags"][2]
	command_string := "set_rule_visibility " Quoted(type_tag) " " Quoted(tier_tag) " " target_visibility
	exit_code := RunBackendCliFunction(command_string " " Quoted(g_active_profile))
	status_message := (exit_code == 0) ? "Rule " ((target_visibility == "Show") ? "shown!" : "hidden!") : "Error updating rule visibility"
	GuiControlSetText("vStatusMessageEditBox", status_message)
	FindRuleMatchingClipboard()
}

; ========================== Filter Actions ==========================

; Updates g_ui_data_dict and g_ui_changes to be consistent with all UI changes
; that have occurred since last filter write. This checks the following controls
; (those without gLabels), which store their state entirely in the GUI state:
;  - vCurrencyTierStackSizeDdlT%tier% (including tportal and twisdom)
;  - vChaosRecipeCheckBox%item_slot_no_spaces%
;  - HWNDhHideMapsEditBox
;  - vEssenceTierDdl
;  - vDivCardTierDdl
;  - vUniqueItemTierDdl
;  - vUniqueMapTierDdl
;  - vOilDdl
;  - vGemQualityEditBox
;  - vFlaskQualityEditBox
;  - vRgbSizeDdl
UpdateGuiStateVariables() {
	global kCurrencyStackSizeToTextTwd, kChaosRecipeItemSlots, kEssenseTiersToTextTwd, kBackendToFrontendRgbSizesTwd
	global g_ui_data_dict, g_ui_changes
	; Currency tier stack size DropDownList
	for _, tier in Concatenated(RangeArray(9), ["tportal", "twisdom"]) {
		ui_ddl_stack_size_text := GuiControlGetHelper("vCurrencyTierStackSizeDdlT" tier)
		ui_ddl_stack_size := kCurrencyStackSizeToTextTwd.GetKey(ui_ddl_stack_size_text)
		if (g_ui_data_dict["currency_tier_min_visible_stack_sizes"][tier] != ui_ddl_stack_size) {
			g_ui_data_dict["currency_tier_min_visible_stack_sizes"][tier] := ui_ddl_stack_size
			backend_cli_command := "set_currency_tier_min_visible_stack_size " tier " " ui_ddl_stack_size
			g_ui_changes.push(backend_cli_command)
		}
	}
	; Chaos recipe item check boxes
	for _, item_slot in kChaosRecipeItemSlots {
		item_slot_no_spaces := RemovedSpaces(item_slot)
		ui_checked_flag := GuiControlGetHelper("vChaosRecipeCheckBox" item_slot_no_spaces)
		if (g_ui_data_dict["chaos_recipe_statuses"][item_slot] != ui_checked_flag) {
			g_ui_data_dict["chaos_recipe_statuses"][item_slot] := ui_checked_flag
			backend_cli_command := "set_chaos_recipe_enabled_for " Quoted(item_slot) " " ui_checked_flag
			g_ui_changes.push(backend_cli_command)
		}
	}
	; Hide maps below tier
	ui_tier := GuiControlGetHelper("HWNDhHideMapsEditBox")
	if (g_ui_data_dict["hide_maps_below_tier"] != ui_tier) {
		g_ui_data_dict["hide_maps_below_tier"] := ui_tier
		backend_cli_command := "set_hide_maps_below_tier " ui_tier
		g_ui_changes.push(backend_cli_command)
	}
	; Hide essences above/below tier
	ui_tier_text := GuiControlGetHelper("vEssenceTierDdl")
	ui_tier := kEssenseTiersToTextTwd.GetKey(ui_tier_text)
	if (g_ui_data_dict["hide_essences_above_tier"] != ui_tier) {
		g_ui_data_dict["hide_essences_above_tier"] := ui_tier
		backend_cli_command := "set_hide_essences_above_tier " ui_tier
		g_ui_changes.push(backend_cli_command)
	}
	; Hide div cards above tier
	ui_tier := GuiControlGetHelper("vDivCardTierDdl")
	if (g_ui_data_dict["hide_div_cards_above_tier"] != ui_tier) {
		g_ui_data_dict["hide_div_cards_above_tier"] := ui_tier
		backend_cli_command := "set_hide_div_cards_above_tier " ui_tier
		g_ui_changes.push(backend_cli_command)
	}
	; Hide unique items above tier
	ui_tier := GuiControlGetHelper("vUniqueItemTierDdl")
	if (g_ui_data_dict["hide_unique_items_above_tier"] != ui_tier) {
		g_ui_data_dict["hide_unique_items_above_tier"] := ui_tier
		backend_cli_command := "set_hide_unique_items_above_tier " ui_tier
		g_ui_changes.push(backend_cli_command)
	}
	; Set unique maps above tier
	ui_tier := GuiControlGetHelper("vUniqueMapTierDdl")
	if (g_ui_data_dict["hide_unique_maps_above_tier"] != ui_tier) {
		g_ui_data_dict["hide_unique_maps_above_tier"] := ui_tier
		backend_cli_command := "set_hide_unique_maps_above_tier " ui_tier
		g_ui_changes.push(backend_cli_command)
	}
	; Set lowest visible oil
	ui_lowest_visible_oil := GuiControlGetHelper("vOilDdl")
	if (g_ui_data_dict["lowest_visible_oil"] != ui_lowest_visible_oil) {
		g_ui_data_dict["lowest_visible_oil"] := ui_lowest_visible_oil
		backend_cli_command := "set_lowest_visible_oil " Quoted(ui_lowest_visible_oil)
		g_ui_changes.push(backend_cli_command)
	}
	; Set gem min quality
	ui_gem_min_quality := GuiControlGetHelper("vGemQualityEditBox")
	if (g_ui_data_dict["gem_min_quality"] != ui_gem_min_quality) {
		g_ui_data_dict["gem_min_quality"] := ui_gem_min_quality
		backend_cli_command := "set_gem_min_quality " ui_gem_min_quality
		g_ui_changes.push(backend_cli_command)
	}
	; Set flask min quality
	ui_flask_min_quality := GuiControlGetHelper("vFlaskQualityEditBox")
	if (g_ui_data_dict["flask_min_quality"] != ui_flask_min_quality) {
		g_ui_data_dict["flask_min_quality"] := ui_flask_min_quality
		backend_cli_command := "set_flask_min_quality " ui_flask_min_quality
		g_ui_changes.push(backend_cli_command)
	}
	; Set rgb item max size
	rgb_size_ui_text := GuiControlGetHelper("vRgbSizeDdl")
	rgb_size_backend_string := kBackendToFrontendRgbSizesTwd.GetKey(rgb_size_ui_text)
	if (g_ui_data_dict["rgb_item_max_size"] != rgb_size_backend_string) {
		g_ui_data_dict["rgb_item_max_size"] := rgb_size_backend_string
		backend_cli_command := "set_rgb_item_max_size " rgb_size_backend_string
		g_ui_changes.push(backend_cli_command)
	}
}

UpdateFilter() {
	global kBackendCliInputPath
	global g_active_profile, g_ui_changes
	; Update g_ui_changes to contain changes whose state is reflected purely in UI state
	UpdateGuiStateVariables()
	; Setup backend cli batch call
    FileDelete, %kBackendCliInputPath%
    for i, function_call_string in g_ui_changes {
        AddFunctionCallToBatch(function_call_string)
    }
    exit_code := RunBackendCliFunction("run_batch " Quoted(g_active_profile))
	if (exit_code == 0) {
		g_ui_changes := []
	}
	status_message := (exit_code == 0) ? "Filter updated!" : "Error updating filter"
    UpdateStatusMessage(status_message "`n" ParseInfoMessages())
    return
}

; TODO: If downloaded filter is missing, check if input filter is present and load that if so.
ImportFilter() {
	global g_active_profile
    exit_code := RunBackendCliFunction("import_downloaded_filter " Quoted(g_active_profile))
    UpdateStatusMessage((exit_code == 0) ? "Imported downloaded filter!" : "Error importing downloaded filter")
    Reload  ; TODO: this will lose the status messages we just created here, ideally we shouldn't reload
}

ReloadUi() {
	Reload
}

MinimizeToTray() {
	Gui, Hide
	Menu, Tray, Delete, 1&  ; 1& indicates first item
	Menu, Tray, Insert, 1&, Restore from System Tray, RestoreFromTray
	Menu, Tray, Default, 1&
}

RestoreFromTray() {
	Gui, Show
	Menu, Tray, Delete, 1&  ; 1& indicates first item
	Menu, Tray, Insert, 1&, Minimize to System Tray, MinimizeToTray
	Menu, Tray, Default, 1&
}

Exit() {
	ExitApp
}