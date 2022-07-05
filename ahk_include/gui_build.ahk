#Include consts.ahk
#Include general_helper.ahk
#Include gui_interaction.ahk
#Include two_way_dict.ahk

; ========================== GUI Build Consts ==========================

; GUI window parameters
kWindowWidth := 1470
kWindowHeight := 866
kWindowTitle := "PoE Dynamic Loot Filter"
kBorderlessMode := True  ; disables drag-moving the window!

; Note: TWD = TwoWayDict (see two_way_dict.ahk)
; StackSize note: Tiers 1-7 do not have the 6+ StackSize option
kCurrencyStackSizeToTextTwd := new TwoWayDict({1: "1+", 2: "2+", 4: "4+", 6: "6+", "hide_all": "--"})
kCurrencyStackSizesText := Join(kCurrencyStackSizeToTextTwd.forward_dict, "|")
kSplinterStackSizes := [1, 2, 4, 8]
kSplinterStackSizesText := Join(kSplinterStackSizes, "+|") "+"  ; extra plus for last item
kEssenseTiersToTextTwd := new TwoWayDict({1: "T7 (Deafening)", 2: "T6 (Shrieking)", 3: "T5 (Screaming)", 4: "T4 (Wailing)", 5: "T3 (Weeping)", 6:"None"})
kEssenceTiersText := Join(kEssenseTiersToTextTwd.forward_dict, "|")
kDivCardTiersText := "1|2|3|4|5|6|7|8"
kUniqueItemTiersText := "1|2|3|4|5"
kUniqueMapTiersText := "1|2|3|4"
kFrontendRgbSizes := ["Hide All", "Small", "Medium", "Large"]
kBackendToFrontendRgbSizesTwd := new TwoWayDict({"none": "Hide All", "small": "Small", "medium": "Medium", "large": "Large"})
kRgbSizesText := Join(kFrontendRgbSizes, "|")

BuildGui(ui_data_dict) {
	; Use global mode so vVariables and HWNDhIdentifiers created here end up global
	global
	; global g_profiles, kBorderlessMode, kNumCurrencyTiers, kCurrencyStackSizesText, kChaosRecipeItemSlots, kSplinterStackSizes, kCurrencyStackSizeToTextTwd

	; Precomputation
	profile_ddl_text := Join(g_profiles, "|")
	currency_listbox_texts := {}  ; tier -> text
	Loop %kNumCurrencyTiers% {
		currency_listbox_texts[%A_Index%] := ""
	}
	for currency_name, tier in ui_data_dict["currency_to_tier_dict"] {
		currency_listbox_texts[tier] .= currency_name "|"
	}

	; Set color themes
	Gui Color, 0x111122, 0x111133
	; Title
	Gui Font, c0x00e8b2 s16 Bold, Segoe UI
	Gui Add, Text, x386 y8 w556 h26 +0x200 +Center, %kWindowTitle%

	; ------------- Section: Profiles ------------
	anchor_x := 1140, anchor_y := 12
	Gui Font, c0x00e8b2 s14 Bold, Segoe UI
	Gui Add, Text, x%anchor_x% y%anchor_y% w66 h36 +0x200, Profile:
	; DropDownList
	Gui Font, c0x00e8b2 s14 Norm, Segoe UI
	x := anchor_x + 72, y := anchor_y + 0
	Gui Add, DropDownList, x%x% y%y% w151 gProfileDdlAction vProfileDdl Choose1, %profile_ddl_text%
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
	currency_basetypes_text := Join(ui_data_dict["currency_to_tier_dict"], "|", join_keys:=True)
	Gui Add, DropDownList, x%x% y%y% w270 +Sort HWNDhCurrencyNamesDdl gCurrencyNamesDdlAction, % "             Select Currency Type...||"currency_basetypes_text
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 344, y := anchor_y + 33
	Gui Add, Text, x%x% y%y% w36 h26 +0x200, -->
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 375, y := anchor_y + 32
	Gui Add, DropDownList, x%x% y%y% w43 HWNDhCurrencyTargetTierDdl gCurrencyTargetTierDdlAction, T#||T1|T2|T3|T4|T5|T6|T7|T8|T9
	; Tier blocks
	tier_anchor_x := anchor_x + 16
	tier_anchor_y := anchor_y + 84
	tier_horizontal_spacing := 160
	tier_vertical_spacing := 208
	for _, tier in RangeArray(kNumCurrencyTiers) {
		; Positioning computations
		row_i := Mod(tier - 1, 3)
		col_i := (tier - 1) // 3
		loop_anchor_x := tier_anchor_x + row_i * tier_horizontal_spacing
		loop_anchor_y := tier_anchor_y + col_i * tier_vertical_spacing
		; Text parameters
		listbox_text := currency_listbox_texts[tier]
		selected_stacksize := ui_data_dict["currency_tier_min_visible_stack_sizes"][tier]
		selected_stacksize_text := kCurrencyStackSizeToTextTwd.GetValue(selected_stacksize)
		; GUI elements
		; StackSize note: Tiers 1-7 do not have the 6+ StackSize option
		stacksize_options_text := kCurrencyStackSizesText
		if (tier < 8) {
			stacksize_options_text := StrReplace(stacksize_options_text, "6+|")
		}
		Gui Font, c0x00e8b2 s11 Norm, Segoe UI
		x := loop_anchor_x + 0, y := loop_anchor_y + 0
		Gui Add, Text, x%x% y%y% w115 h28 +0x200, T%tier% Stack Size:
		x := loop_anchor_x + 92, y := loop_anchor_y + 0
		Gui Add, DropDownList, x%x% y%y% w44 vCurrencyTierStackSizeDdlT%tier%, %stacksize_options_text%
		GuiControlSelectItem("vCurrencyTierStackSizeDdlT" tier, selected_stacksize_text)
		Gui Font, c0x00e8b2 s10
		x := loop_anchor_x + 0, y := loop_anchor_y + 32
		Gui Add, ListBox, x%x% y%y% w135 h164 +Sort HWNDhCurrencyTierListBoxT%tier% gCurrencyTierListBoxAction, %listbox_text%
	}
	; Portal scrolls
	Gui Font, c0x00e8b2 s11, Segoe UI
	x := anchor_x + 40, y := anchor_y + 711
	Gui Add, Text, x%x% y%y% w115 h28 +0x200, Portal Stack Size:
	x := anchor_x + 160, y := anchor_y + 711
	selected_stacksize := ui_data_dict["currency_tier_min_visible_stack_sizes"]["tportal"]
	selected_stacksize_text := kCurrencyStackSizeToTextTwd.GetValue(selected_stacksize)
	Gui Add, DropDownList, x%x% y%y% w48 vCurrencyTierStackSizeDdlTtportal, %kCurrencyStackSizesText%
	GuiControlSelectItem("vCurrencyTierStackSizeDdlTtportal", selected_stacksize_text)
	; Wisdom scrolls
	Gui Font, c0x00e8b2 s11, Segoe UI
	x := anchor_x + 272, y := anchor_y + 711
	selected_stacksize := ui_data_dict["currency_tier_min_visible_stack_sizes"]["twisdom"]
	selected_stacksize_text := kCurrencyStackSizeToTextTwd.GetValue(selected_stacksize)
	Gui Add, Text, x%x% y%y% w133 h28 +0x200, Wisdom Stack Size:
	x := anchor_x + 408, y := anchor_y + 711
	Gui Add, DropDownList, x%x% y%y% w48 vCurrencyTierStackSizeDdlTtwisdom, %kCurrencyStackSizesText%
	GuiControlSelectItem("vCurrencyTierStackSizeDdlTtwisdom", selected_stacksize_text)
	; ------------- End Section: [Currency] -------------

	; ------------- Section: [Splinter Stack Sizes] ------------
	anchor_x := 20, anchor_y := 790
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w476 h60, Splinter Stack Sizes
	; Splinter BaseType DDL (items roughly in order from least to most valuable, but grouped by legion/breach)
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 82, y := anchor_y + 24
	Gui Add, DropDownList, x%x% y%y% w240 HWNDhSplinterTypeDdl gSplinterTypeDdlAction, % "           Select Splinter Type...||" Join(kSplinterBaseTypesList, "|")
	; Stack Size DDL
	x := anchor_x + 332, y := anchor_y + 24
	Gui Add, DropDownList, x%x% y%y% w48 Choose1 HWNDhSplinterStackSizeDdl gSplinterStackSizeDdlAction, %kSplinterStackSizesText%
	; ------------- End Section: [Splinter Stack Sizes] ------------

	; ------------- Section: [Chaos Recipe Rares] -------------
	anchor_x := 528, anchor_y := 48
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h169, Chaos Recipe Rares
	; CheckBoxes
	chaos_checkboxes_anchor_x := anchor_x + 16,
	chaos_checkboxes_anchor_y := anchor_y + 32
	horizontal_spacing := 156
	vertical_spacing := 32
	Loop % Length(kChaosRecipeItemSlots) {
		i := A_Index  ; A_Index starts at 1
		; Positioning computations
		col_i := (i - 1) // 4
		row_i := Mod(i - 1, 4)
		x := chaos_checkboxes_anchor_x + col_i * horizontal_spacing
		y := chaos_checkboxes_anchor_y + row_i * vertical_spacing
		w := (col_i == 0) ? horizontal_spacing : 100  ; extra width for "Body Armours"
		; Create UI element
		item_slot := kChaosRecipeItemSlots[i]
		enabled_flag := ui_data_dict["chaos_recipe_statuses"][item_slot]
		item_slot_no_spaces := RemovedSpaces(item_slot)
		checked_string := enabled_flag ? "Checked" : ""
		Gui Font, c0x00e8b2 s14 Norm, Segoe UI
		Gui Add, CheckBox, x%x% y%y% w%w% h26 %checked_string% vChaosRecipeCheckBox%item_slot_no_spaces%, %item_slot%
	}
	; ------------- End Section: [Chaos Recipe Rares] -------------

	; ------------- Section: [Hide Maps Below Tier] -------------
	anchor_x := 528, anchor_y := 233
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h74, Non-Unique Maps
	; Text
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 16, y := anchor_y + 32
	Gui Add, Text, x%x% y%y% w152 h28 +0x200, Hide Maps Below Tier:
	; Edit & UpDown
	x := anchor_x + 172, y := anchor_y + 32
	Gui Add, Edit, x%x% y%y% w50 h28 HWNDhHideMapsEditBox
	x := anchor_x + 214, y := anchor_y + 32
	Gui Add, UpDown, x%x% y%y% w20 h28 Range0-17, % ui_data_dict["hide_maps_below_tier"]
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
	Gui Add, ListBox, x%x% y%y% w257 h110 HWNDhGeneralBaseTypesListBox +Sort
	Gui Font, c0x00e8b2 s10 Bold, Segoe UI
	x := anchor_x + 68, y := anchor_y + 212
	Gui Add, Button, x%x% y%y% w144 h31 gGeneralBaseTypesRemove, Remove Selected
	; Populate ListBox from filter_data["visible_basetypes"] -> dict: {base_type -> rare_only_flag}
	for base_type, rare_only_flag in ui_data_dict["visible_basetypes"] {
		AddLineToGeneralBaseTypesListBox(base_type, rare_only_flag)
	}
	; ------------- End Section: [General BaseTypes] ------------

	; ------------- Section: [Flask BaseTypes] ------------
	anchor_x := 528, anchor_y := 595
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h236, Flask BaseTypes
	; DDL
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 18, y := anchor_y + 36
	Gui Add, DropDownList, x%x% y%y% w250 HWNDhFlaskDdl +Sort, % "              Select Flask Type...||" Join(kFlaskBaseTypesList, "|")
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
	Gui Add, ListBox, x%x% y%y% w257 h90 HWNDhFlaskListBox +Sort
	Gui Font, c0x00e8b2 s10 Bold, Segoe UI
	x := anchor_x + 68, y := anchor_y + 192
	Gui Add, Button, x%x% y%y% w144 h31 gFlaskRemove, Remove Selected
	; Populate ListBox from filter_data["visible_flasks"] -> dict: {base_type -> high_ilvl_only_flag}
	for base_type, high_ilvl_only_flag in ui_data_dict["visible_flasks"] {
		AddLineToFlaskBaseTypesListBox(base_type, high_ilvl_only_flag)
	}
	; ------------- End Section: [Flask BaseTypes] ------------

	; ------------- Section: [Tier Visibility] -------------
	anchor_x := 844, anchor_y := 48
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h234, Tier Visibility
	; Right align all DropDownLists
	right_edge_x := anchor_x + 274
	; Essences
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 16, y := anchor_y + 32
	Gui Add, Text, x%x% y%y% w179 h28 +0x200, Hide Essences Below:
	Gui Font, s10
	x := anchor_x + 164, y := anchor_y + 34, w := right_edge_x - x
	selected_tier_index := ui_data_dict["hide_essences_above_tier"]
	Gui Add, DropDownList, x%x% y%y% w%w% Choose%selected_tier_index% vEssenceTierDdl, %kEssenceTiersText%
	; Divination cards
	Gui Font, s11
	x := anchor_x + 16, y := anchor_y + 72
	Gui Add, Text, x%x% y%y% w185 h28 +0x200, Hide Div Cards Above Tier:
	x := anchor_x + 204, y := anchor_y + 72, w := right_edge_x - x
	selected_tier := ui_data_dict["hide_div_cards_above_tier"]
	Gui Add, DropDownList, x%x% y%y% w%w% Choose%selected_tier% vDivCardTierDdl, %kDivCardTiersText%
	; Unique items
	x := anchor_x + 16, y := anchor_y + 112
	Gui Add, Text, x%x% y%y% w203 h28 +0x200, Hide Unique Items Above Tier:
	x := anchor_x + 228, y := anchor_y + 112, w := right_edge_x - x
	selected_tier := ui_data_dict["hide_unique_items_above_tier"]
	Gui Add, DropDownList, x%x% y%y% w%w% Choose%selected_tier% vUniqueItemTierDdl, %kUniqueItemTiersText%
	; Unique maps
	x := anchor_x + 16, y := anchor_y + 152
	Gui Add, Text, x%x% y%y% w206 h28 +0x200, Hide Unique Maps Above Tier:
	x := anchor_x + 228, y := anchor_y + 152, w := right_edge_x - x
	selected_tier := ui_data_dict["hide_unique_maps_above_tier"]
	Gui Add, DropDownList, x%x% y%y% w%w% Choose%selected_tier% vUniqueMapTierDdl, %kUniqueMapTiersText%
	; Oils
	x := anchor_x + 16, y := anchor_y + 192
	Gui Add, Text, x%x% y%y% w113 h28 +0x200, Hide Oils Below:
	x := anchor_x + 134, y := anchor_y + 192, w := right_edge_x - x
	lowest_visible_oil := ui_data_dict["lowest_visible_oil"]
	lowest_visible_oil_index := Find(lowest_visible_oil, kOilBaseTypes)
	Gui Add, DropDownList, x%x% y%y% w%w% Choose%lowest_visible_oil_index% vOilDdl, % Join(kOilBaseTypes, "|")
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
	Gui Add, Edit, x%x% y%y% w50 h28 vGemQualityEditBox
	x := anchor_x + 178, y := anchor_y + 32
	gem_min_quality := ui_data_dict["gem_min_quality"]
	Gui Add, UpDown, x%x% y%y% w20 h28 Range0-21, %gem_min_quality%
	; Quality flasks
	x := anchor_x + 16, y := anchor_y + 72
	Gui Add, Text, x%x% y%y% w120 h28 +0x200, Flask Min Quality:
	x := anchor_x + 136, y := anchor_y + 72
	Gui Add, Edit, x%x% y%y% w50 h28 vFlaskQualityEditBox,
	x := anchor_x + 178, y := anchor_y + 72
	flask_min_quality := ui_data_dict["flask_min_quality"]
	Gui Add, UpDown, x%x% y%y% w20 h28 Range0-21, %flask_min_quality%
	; RGB items
	x := anchor_x + 16, y := anchor_y + 112
	Gui Add, Text, x%x% y%y% w136 h28 +0x200, RGB Item Max Size:
	x := anchor_x + 152, y := anchor_y + 112
	rgb_item_max_size := kBackendToFrontendRgbSizesTwd.GetValue(ui_data_dict["rgb_item_max_size"])
	selected_item_size_index := Find(rgb_item_max_size, kFrontendRgbSizes)
	Gui Add, DropDownList, x%x% y%y% w113 Choose%selected_item_size_index% vRgbSizeDdl, %kRgbSizesText%
	; ------------- End Section: [Quality and RGB Items] ------------

	; ------------- Section: [Socket Patterns] ------------
	anchor_x := 844, anchor_y := 575
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
	Gui Add, DropDownList, x%x% y%y% HWNDhSocketPatternsItemSlotDdl, % "Any Item Slot||" Join(kChaosRecipeItemSlots, "|")
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
	; Populate ListBox from filter_data["socket_rules"] -> dict: {socket_string + ";" + item_slot -> True}
	for socket_string_item_slot, _ in ui_data_dict["socket_rules"] {
		split_result := StrSplit(socket_string_item_slot, ";")
		AddLineToSocketPatternsListBox(split_result[1], split_result[2])
	}
	; ------------- End Section: [Socket Patterns] ------------

	; ------------- Section: Reload UI -------------
	anchor_x := 1160, anchor_y := 64
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h64, % "Reload UI"
	x := anchor_x + 70, y:= anchor_y + 22
	Gui Add, Button, x%x% y%y% w140 h28 gReloadUi, % "Reload UI"
	; ------------- Section: Reload UI -------------

	; ------------- Section: Hotkeys -------------
	anchor_x := 1160, anchor_y := 144
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h128, Hotkeys
	x := anchor_x + 8, y:= anchor_y + 28, x2 := anchor_x + 168
	spacing_y := 30
	for idx, hotkey_line in ui_data_dict["hotkeys"] {
		Gui Font, c0x00e8b2 s13 Norm, Segoe UI
		split_hotkey_line := StrSplit(hotkey_line, ";")
		Gui Add, Text, vHotkeyText%idx% x%x% y%y% w160 h32, % split_hotkey_line[1] ":"
		Gui Font, c0x00e8b2 s11 Norm, Segoe UI
		Gui Add, Hotkey, vHotkey%idx% x%x2% y%y% w110 gUpdateHotkey, % split_hotkey_line[2]
		function_name := RemovedSpaces(split_hotkey_line[1])
		Hotkey, % split_hotkey_line[2], % function_name
		y += spacing_y
	}
	; ------------- End Section: Hotkeys -------------

	; ------------- Section: [Item-Rule Matching] -------------
	anchor_x := 1160, anchor_y := 290
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h290, Item-Rule Matching
	; Buttons & Edit
	Gui Font, c0x00e8b2 s10 Bold, Segoe UI
	x := anchor_x + 16, y := anchor_y + 36
	Gui Add, Button, x%x% y%y% w254 h28 gFindRuleMatchingClipboard, Find Rule Matching Clipboard
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 16, y := anchor_y + 75
	Gui Add, Edit, x%x% y%y% w254 h164 vMatchedRuleTextBox +ReadOnly
	Gui Font, c0x00e8b2 s10 Bold, Segoe UI
	x := anchor_x + 66, y := anchor_y + 246
	Gui Add, Button, x%x% y%y% w154 h28 +Disabled vChangeMatchedRuleVisibilityButton gChangeMatchedRuleVisibility, Change to "Hide"
	; ------------- End Section: [Item-Rule Matching] -------------

	; ------------- Section: [Filter Actions] -------------
	anchor_x := 1160, anchor_y := 602
	; GroupBox
	Gui Font, c0x00e8b2 s10 Bold
	Gui Add, GroupBox, x%anchor_x% y%anchor_y% w288 h252, Filter Actions
	; Status message box
	Gui Font, c0x00e8b2 s11 Norm, Segoe UI
	x := anchor_x + 16, y := anchor_y + 32
	Gui Add, Text, x%x% y%y% w250 h38, Status Message:
	Gui Font, c0x00e8b2 s11, Segoe UI
	x := anchor_x + 16, y := anchor_y + 58
	Gui Add, Edit, x%x% y%y% w254 h90 +ReadOnly -VScroll vStatusMessageEditBox, Filter loaded successfully!
	; Action buttons
	Gui Font, c0x00e8b2 s11 Bold, Segoe UI
	x := anchor_x + 32, y := anchor_y + 163
	Gui Add, Button, x%x% y%y% w226 h32 gImportFilter, Import Downloaded Filter
	x := anchor_x + 32, y := anchor_y + 203
	Gui Add, Button, x%x% y%y% w224 h31 gUpdateFilter, [&W]rite Filter
	; ------------- End Section: [Filter Actions] -------------

	if (kBorderlessMode) {
		Gui -Border  ; disables drag-moving the window!
	}
	Gui Show, w%kWindowWidth% h%kWindowHeight%, %kWindowTitle%
	Return
}

UpdateStatusMessage(new_status_message) {
	GuiControl, , StatusMessageEditBox, %new_status_message%
}
