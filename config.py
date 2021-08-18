import os.path

# Loot filter file locations
kDownloadDirectory = 'FiltersDownload'
kPathOfExileDirectory = 'FiltersPathOfExile'
kDownloadedLootFilterFilename = 'BrandLeaguestart.filter'
kPathOfExileLootFilterFilename = 'AAA_DynamicLootFilter.filter'

# Combine directories and filenames for full paths (user can ignore this section)
kDownloadedLootFilterFullpath = os.path.join(kDownloadDirectory, kDownloadedLootFilterFilename)
kPathOfExileLootFilterFullpath = os.path.join(kPathOfExileDirectory, kPathOfExileLootFilterFilename)

# Loot filter options
kHideMapsBelowTier = 0
kAddChaosRecipeRules = True
kChaosRecipeWeaponClasses = ['Daggers', 'Wands']

