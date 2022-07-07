/*
 * Defines general functionality related to types, tracebacks, and debugging.
 *  - Defines functions None() and IsNone() to work with objects of type "none"
 *  - Defines a function Type(var), which returns one of "integer", "float", "string", "object", "none"
 *  - Defines a function Repr(var), which returns a python-style string representation of var
 *  - Defines a function Traceback(), which returns a traceback message string
 *  - Defines a function CheckType(value, required_type, allow_empty_string:=False),
 *    which gives an error if value is not of requried type.
 *    Note: integer counts as a float or a string, and float counts as a string.
 */

; Ideally this would be a static class variable
global kNoneObject := {}

; Get the Singleton "None" object
None() {
	global kNoneObject
    return kNoneObject
}

; Check if a value is None
IsNone(value) {
	global kNoneObject
    return (value == kNoneObject)
}

; Returns one of "integer", "float", "string", "object", or "none".
; Note that "arrays" are just syntactic sugar for objects.
; Also, note that an empty variable has type "string". Only the None object defined above has type "none".
Type(value) {
    if (IsObject(value)) {
        return IsNone(value) ? "none" : "object"
    }
    ; Legacy syntax is required here
    if value is integer
        return "integer"
    else if value is float
        return "float"
    return "string"
}

; Returns the AHK expression string representing the given value.
; Note that "arrays" are just syntactic sugar for objects, so curly braces will be used.
Repr(value) {
    switch (Type(value)) {
		case "integer":
            return value
		case "float":
			return value
		case "string":
			return """" value """"
		case "none":
			return "{None}"
	}
    ; If it is none of the above, var is an object
    num_keys := 0
    repr_string := "{"
    for key, val in value {
        num_keys += 1
        if (num_keys > 1) {
            repr_string .= ", "
        }
        repr_string .= Repr(key) ": " Repr(val)
    }
    repr_string .= "}"
    return repr_string
}

; Modified significantly from: https://www.autohotkey.com/boards/viewtopic.php?t=6001
Traceback(levels_to_skip:=1) {
	traceback_array := []
	Loop {
		; offset: [...] or a negative offset from the top of the call stack
		offset := -(A_Index + levels_to_skip)
		e := Exception("", offset)
		if (e.What == offset) {
			break
		}
		; e has fields: What (name of function being called), File, Line
		; (e also has Message and Extra, but they seem to usually be empty)
		traceback_array.push(e)
	}
	traceback_message := "Traceback (most recent call last):"
	for i, e in traceback_array {
		SplitPath, % e.File, filename
		caller := (i < traceback_array.Length()) ? traceback_array[i + 1].What : "<global scope>"
		traceback_message .= "`n  file " filename ", in " caller ", line " e.Line ": " e.What "(...)"
	}
	return traceback_message
}

; Note: integer counts as a float or a string, and float counts as a string.
CheckType(value, required_type, allow_empty_string:=False) {
    value_type := Type(value)
    if ((value_type == "integer") and ((required_type == "float") or (required_type == "string"))) {
        return  ; Okay - integer counts as float or string
    } else if ((value_type == "float") and (required_type == "string")) {
        return  ; Okay - float counts as string
    } else if (value_type != required_type) {
		error_message := Traceback()
		error_message .= "`n`nError: required type <" required_type ">, but recieved: " Repr(value) " <" Type(value) ">"
		MsgBox, , CheckType Error, %error_message%
		ExitApp
	} else if ((value == "") and not allow_empty_string) {
		error_message := Traceback()
		error_message .= "`n`nError: nonempty string required, but recieved empty string"
		MsgBox, , CheckType Error, %error_message%
		ExitApp
    }
}

Test() {
    MsgBox % Repr(["hello", "goodbye", "fox"])

    value := "Hello"
    ; CheckType(value, "object")  ; should fail
    ; CheckType(nonexistent_variable, "string")  ; should fail
    CheckType({}, "object")  ; passes
    CheckType(5, "integer")  ; passes
    CheckType(5, "float")  ; passes
    CheckType(5, "string")  ; passes
    CheckType(5.2, "float")  ; passes
    CheckType(5.3, "string")  ; passes
    ; CheckType("three", "integer")  ; fails
    CheckType(None(), "none")
    ; CheckType("", "none")  ; should fail
}

; Test()