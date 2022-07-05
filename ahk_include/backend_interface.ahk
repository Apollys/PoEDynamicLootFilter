#Include consts.ahk
#Include general_helper.ahk

kPossiblePythonCommands := ["python", "python3", "py"]

; Runs the given command in a hidden window, waits for it to complete,
; and then returns the received exit code: 0 = success, nonzero = failure.
RunCommand(command_string) {
    ; ComSpec contains the path to the command-line exe
    ; The "/c" parameter tells cmd to run the command, then exit (otherwise it would never exit)
    RunWait, % ComSpec " /c " command_string,  , Hide UseErrorLevel  ; ErrorLevel now contains exit code
    return ErrorLevel
}

GetPythonCommand() {
	static python_command := ""
	global kPossiblePythonCommands
	if (python_command != "") {
		return python_command
	}
	python_version_output_path := A_WorkingDir "\" kCacheDirectory "\python_version_output.txt"
	for _, possible_python_command in kPossiblePythonCommands {
		command_string := possible_python_command " --version > " Quoted(python_version_output_path)
		exit_code := RunCommand(command_string)
		if (exit_code != 0) {
			continue
		}
		FileRead, python_version_output, %python_version_output_path%
		FileDelete, %python_version_output_path%
		if (StartsWith(python_version_output, "Python 3.")) {
			python_command := possible_python_command
			return python_command
		}
	}
	MsgBox, % "Error: The commands [" ListToString(kPossiblePythonCommands) "] were all unable to launch Python 3."
			. "  Either Python 3 is not installed, Python 3 is not in the path, or the commands are aliased to other programs."
	ExitApp
}

RunBackendCliFunction(function_call_string) {
    global kBackendCliPath, kBackendCliLogPath
	command_string := GetPythonCommand() " " kBackendCliPath " " function_call_string
	; DebugMessage(command_string)
	RunWait, %command_string%, , Hide UseErrorLevel
	exit_code := ErrorLevel  ; other commands may modify ErrorLevel at any time
    ; Handle nonzero exit code
    if (exit_code != 0) {
        FileRead, error_log, %kBackendCliLogPath%
        MsgBox, % "Error running command: " command_string "`n`n" error_log
    }
    return exit_code
}

AddFunctionCallToBatch(function_call_string) {
    global kBackendCliInputPath
    FileAppend, %function_call_string%`n, %kBackendCliInputPath%
}

; Parses output_lines starting at the given line_index until next "@" line is reached.
; After function returns, line_index will point to the line *after* the terminating "@".
; Returns dict of (key, value) pairs formed by splitting lines on the separator.
; If the separator does not exist in a given line, the full line will be the key, and default_value the value.
ParseBackendOutputLinesAsDict(output_lines, ByRef line_index:=1, separator=";", default_value:=True) {
	parsed_lines_dict := {}
	while ((line_index <= Length(output_lines)) and (output_lines[line_index] != "@")) {
		if (output_lines[line_index] != "") {
			if (InStr(output_lines[line_index], separator)) {
				split_result := StrSplit(output_lines[line_index], separator)
				parsed_lines_dict[split_result[1]] := split_result[2]
			} else {
				parsed_lines_dict[output_lines[line_index]] := default_value
			}
		}
		line_index += 1
	}
	line_index += 1
	return parsed_lines_dict
}

; Queries the backend_cli for all filter data corresponding to the given profile.
; Returns a dict of keywords to corresponding data structures (or empty dict if failed):
;  - "currency_to_tier_dict" -> dict: {base_type -> tier}
;  - "currency_tier_min_visible_stack_sizes" -> dict {tier -> stack_size}
;	  - tier may be "tportal", "twisdom", stack_size may be "hide_all"
;  - "splinter_min_visible_stack_sizes" -> dict: {base_type -> stack_size}
;  - "chaos_recipe_statuses" -> dict: {item_slot -> enabled_flag}
;  - "hide_maps_below_tier" -> tier
;  - "hide_essences_above_tier" -> tier
;  - "hide_div_cards_above_tier" -> tier
;  - "hide_unique_items_above_tier" -> tier
;  - "hide_unique_maps_above_tier" -> tier
;  - "lowest_visible_oil" -> oil_name
;  - "visible_basetypes" -> dict: {base_type -> rare_only_flag}
;  - "visible_flasks" -> dict: {base_type -> high_ilvl_only_flag}
;  - "socket_rules" -> dict: {socket_string + ";" + item_slot -> True}  (because I don't see a builtin set type)
;  - "gem_min_quality" -> gem_min_quality
;  - "flask_min_quality" -> flask_min_quality
;  - "rgb_item_max_size" -> rgb_item_max_size
;
; Note: function below adds one more: "hotkeys" -> array: {<hotkey_identifier>;<hotkey_string>}
QueryAllFilterData(profile) {
	success_flag := True
	; Build backend_cli input query
	global kBackendCliInputPath, kBackendCliOutputPath, kNumCurrencyTiers
	FileDelete, %kBackendCliInputPath%
	AddFunctionCallToBatch("get_all_currency_tiers")
	AddFunctionCallToBatch("get_all_currency_tier_min_visible_stack_sizes")
	AddFunctionCallToBatch("get_all_splinter_min_visible_stack_sizes")
	AddFunctionCallToBatch("get_all_chaos_recipe_statuses")
	AddFunctionCallToBatch("get_hide_maps_below_tier")
	AddFunctionCallToBatch("get_hide_essences_above_tier")
	AddFunctionCallToBatch("get_hide_div_cards_above_tier")
	AddFunctionCallToBatch("get_hide_unique_items_above_tier")
	AddFunctionCallToBatch("get_hide_unique_maps_above_tier")
	AddFunctionCallToBatch("get_lowest_visible_oil")
	AddFunctionCallToBatch("get_all_visible_basetypes")
	AddFunctionCallToBatch("get_all_visible_flasks")
	AddFunctionCallToBatch("get_all_added_socket_rules")
	AddFunctionCallToBatch("get_gem_min_quality")
	AddFunctionCallToBatch("get_flask_min_quality")
	AddFunctionCallToBatch("get_rgb_item_max_size")
	; Call run_batch
	exit_code := RunBackendCliFunction("run_batch " profile)
	if (exit_code != 0) {
		ExitApp
	}
	; Parse backend_cli output
	output_lines := ReadFileLines(kBackendCliOutputPath)
	filter_data := {}
	line_index := 1
	filter_data["currency_to_tier_dict"] := ParseBackendOutputLinesAsDict(output_lines, line_index)
	filter_data["currency_tier_min_visible_stack_sizes"] := ParseBackendOutputLinesAsDict(output_lines, line_index)
	filter_data["splinter_min_visible_stack_sizes"] := ParseBackendOutputLinesAsDict(output_lines, line_index)
	filter_data["chaos_recipe_statuses"] := ParseBackendOutputLinesAsDict(output_lines, line_index)
	; Various item tiering
	filter_data["hide_maps_below_tier"] := output_lines[line_index]
	line_index += 2
	filter_data["hide_essences_above_tier"] := output_lines[line_index]
	line_index += 2
	filter_data["hide_div_cards_above_tier"] := output_lines[line_index]
	line_index += 2
	filter_data["hide_unique_items_above_tier"] := output_lines[line_index]
	line_index += 2
	filter_data["hide_unique_maps_above_tier"] := output_lines[line_index]
	line_index += 2
	filter_data["lowest_visible_oil"] := output_lines[line_index]
	line_index += 2
	; BaseTypes
	filter_data["visible_basetypes"] := ParseBackendOutputLinesAsDict(output_lines, line_index)
	filter_data["visible_flasks"] := ParseBackendOutputLinesAsDict(output_lines, line_index)
	; For socket patterns, use a separator we know doesn't exist - (socket_string, item_slot) pair is the key
	filter_data["socket_rules"] := ParseBackendOutputLinesAsDict(output_lines, line_index, separator:="*")
	; Quality thresholds
	filter_data["gem_min_quality"] := output_lines[line_index]
	line_index += 2
	filter_data["flask_min_quality"] := output_lines[line_index]
	line_index += 2
	filter_data["rgb_item_max_size"] := output_lines[line_index]
	line_index += 2
	return filter_data
}

QueryHotkeys(ByRef ui_data_dict) {
	global kBackendCliOutputPath
	; Outputs a sequence of lines, each formatted as <hotkey_identifier>;<hotkey_string>
	RunBackendCliFunction("get_all_hotkeys")
	output_lines := ReadFileLines(kBackendCliOutputPath)
	ui_data_dict["hotkeys"] := output_lines
}
