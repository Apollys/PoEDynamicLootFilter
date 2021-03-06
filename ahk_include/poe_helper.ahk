#Include general_helper.ahk

; Returns the HWND ID of the active window if it is owned by the PoE process,
; or 0 if it does not. Thus, the return value can be used in boolean contex
; to determine if PoE is the currently active window.
IsPoeActive() {
   return (WinActive("ahk_exe PathOfExile.exe") or WinActive("ahk_exe PathOfExileSteam.exe"))
}

MakePoeActive() {
   if (WinExist("ahk_exe PathOfExileSteam.exe"))
      WinActivate, ahk_exe PathOfExileSteam.exe
   else
      WinActivate, ahk_exe PathOfExile.exe
}

IsDlfActive() {
    global kWindowTitle
    return WinActive(kWindowTitle " ahk_exe AutoHotkey.exe") != 0
}

MakeDlfActive() {
    global kWindowTitle
    WinActivate, %kWindowTitle% ahk_exe AutoHotkey.exe
}

; Used for SendChatMessage below
RestoreClipboard() {
   global backup_clipboard
   clipboard := backup_clipboard
}

; Sends a chat message by saving it to the clipboard and sending: Enter, Ctrl-v, Enter
; Backs up the clipboard and restores it after a short delay on a separate thread.
; (The clipboard cannot be restored immediately, or it will happen before the paste operation occurs.)
SendChatMessage(message_text, reply_flag := false) {
   global backup_clipboard
   backup_clipboard := clipboard
   command_flag := StartsWith(message_text, "/")
   clipboard := command_flag ? SubStr(message_text, 2) : message_text
   BlockInput, On
   if (command_flag) {
      Send {Enter}/^v{Enter}
   } else if (reply_flag) {
      Send, ^{Enter}^v{Enter}
   } else {
      Send, {Enter}^v{Enter}
   }
   BlockInput, Off
   SetTimer, RestoreClipboard, -50
}