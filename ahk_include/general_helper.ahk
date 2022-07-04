; ========================== Generic Util ==========================

DebugMessage(message) {
    MsgBox, , Debug Message, %message%
}

; ========================== String Util ==========================

; AHK's object.Length() function is broken - in some scenarios it
; returns 0 when the container has many elements. (I think it has
; to do with nested containers.)
Length(container) {
	n := 0
	for key, value in container {
		n += 1
	}
	return n
}

; Returns an array of consecutive integers from start to end (inclusive)
; If only one parameter is passed, yields the range from 1 to given value.
RangeArray(start_or_end, optional_end:="") {
	start := start_or_end, end_inclusive := optional_end
	if (optional_end == "") {
		end_inclusive := start_or_end
		start := 1
	}
	result_list := []
	Loop % end_inclusive - start + 1 {
		result_list.push(start + A_Index - 1)  ; A_Index starts at 1
	}
	return result_list
}

; Returns the concatenation of two arrays
Concatenated(left_array, right_array) {
	concatenated_array := left_array
	for _, value in right_array {
		concatenated_array.push(value)
	}
	return concatenated_array
}

; Accepts either an array or a dict. Returns the key associated with target_value if found.
; To get the index of a value in a dict, use return_index:=True. (AHK dicts are actually ordered.)
Find(target_value, container, return_index:=False) {
	index := 1
	for key, value in container {
		if (value == target_value) {
			return return_index ? index : key
		}
	}
	DebugMessage("Error: " target_value " not found in container")
	DebugDictToString(container)
}

Quoted(s) {
    quote := """"
    return quote s quote
}

StartsWith(s, prefix) {
    return (SubStr(s, 1, StrLen(prefix)) == prefix)
}

; Returns values in the contained joined by delimeter, or keys joined by
; delimiter if join_keys is True.
Join(array_or_dict, delimeter, join_keys:=False) {
    result_string := ""
	index := 1
    for key, value in array_or_dict {
        if (index > 1) {
            result_string .= delimeter
        }
        result_string .= join_keys ? key : value
		index += 1
    }
    return result_string
}

RemovedSpaces(s) {
	s := StrReplace(s, " ")
	return s
}

ListToString(list) {
	return "[" Join(list, ", ") "]"
}

DebugDictToString(dict) {
	if (Length(dict) == 0) {
		return "empty container: {}"
	}
	result_string := "{"
	for key, value in dict {
		result_string .= "`n    " key ": " value
	}
	result_string .= "`n}"
	DebugMessage(result_string)
}

; ========================== File Util ==========================

; Returns an array of strings containing the lines in the file (newlines removed)
ReadFileLines(filepath) {
    FileRead, file_contents, %filepath%
    return StrSplit(file_contents, "`r`n")
}
