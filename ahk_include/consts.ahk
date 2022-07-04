#Include general_helper.ahk  ; ReadFileLines

kDlfIconPath := "DLF_icon.ico"

; Paths for backend cli target, input, and output
kBackendCliPath := "backend_cli.py"
kBackendCliInputPath := "backend_cli.input"
kBackendCliOutputPath := "backend_cli.output"
kBackendCliLogPath := "backend_cli.log"
; TODO: This shouldn't be necessary, just get return code directly
kBackendCliExitCodePath := "backend_cli.exit_code"

; Currency
kNumCurrencyTiers := 9

; Chaos Recipe (also used for Socket Patterns item slots)
kChaosRecipeItemSlots := ["Weapons", "Body Armours", "Helmets", "Gloves", "Boots", "Belts", "Rings", "Amulets"]

; Flask BaseTypes
kFlaskBaseTypesPath := "Resources\flask_base_types.txt"
kFlaskBaseTypesList := ReadFileLines(kFlaskBaseTypesPath)
; Splinter BaseTypes
kSplinterBaseTypesPath := "Resources\splinter_base_types.txt"
kSplinterBaseTypesList := ReadFileLines(kSplinterBaseTypesPath)

; Oil names, ordered from highest to lowest value
kOilBaseTypes := ["Tainted Oil", "Golden Oil", "Silver Oil", "Opalescent Oil", "Black Oil", "Crimson Oil", "Violet Oil", "Indigo Oil"
    , "Azure Oil", "Teal Oil", "Verdant Oil", "Amber Oil", "Sepia Oil", "Clear Oil"]