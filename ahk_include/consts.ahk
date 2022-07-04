#Include general_helper.ahk  ; ReadFileLines

kDlfIconPath := "DLF_icon.ico"

; Directories (must be synced with consts.py)
kBackendDirectory := "backend"
kCacheDirectory := "cache"
kResourcesDirectory := "resources"

; Paths for backend cli target, input, and output
kBackendCliPath := kBackendDirectory "\backend_cli.py"
kBackendCliInputPath := kCacheDirectory "\backend_cli.input"
kBackendCliOutputPath := kCacheDirectory "\backend_cli.output"
kBackendCliLogPath := kCacheDirectory "\backend_cli.log"

; Currency
kNumCurrencyTiers := 9

; Chaos Recipe (also used for Socket Patterns item slots)
kChaosRecipeItemSlots := ["Weapons", "Body Armours", "Helmets", "Gloves", "Boots", "Belts", "Rings", "Amulets"]

; Flask BaseTypes
kFlaskBaseTypesPath := kResourcesDirectory "\flask_base_types.txt"
kFlaskBaseTypesList := ReadFileLines(kFlaskBaseTypesPath)
; Splinter BaseTypes
kSplinterBaseTypesPath := kResourcesDirectory "\splinter_base_types.txt"
kSplinterBaseTypesList := ReadFileLines(kSplinterBaseTypesPath)

; Oil names, ordered from highest to lowest value
kOilBaseTypes := ["Tainted Oil", "Golden Oil", "Silver Oil", "Opalescent Oil", "Black Oil", "Crimson Oil", "Violet Oil", "Indigo Oil"
    , "Azure Oil", "Teal Oil", "Verdant Oil", "Amber Oil", "Sepia Oil", "Clear Oil"]