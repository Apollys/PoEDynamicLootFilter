# Profile name
kProfileName = 'DefaultProfile'

# Loot filter file locations
kDownloadDirectory = 'FiltersDownload'
kPathOfExileDirectory = 'FiltersPathOfExile'
kDownloadedLootFilterFilename = 'BrandLeaguestart.filter'
kPathOfExileLootFilterFilename = 'AAA_DynamicLootFilter.filter'

# Loot filter options
kHideMapsBelowTier = 0
kAddChaosRecipeRules = True
kChaosRecipeWeaponClassesAnyHeight = ['Daggers', 'Wands']
kChaosRecipeWeaponClassesMaxHeight3 = ['Bows']

# ============== Derived Values and Fixed Constants - Do not modify below this line ==============

import os
import os.path

kProfileDirectory = 'Profiles'
kProfileFilename = kProfileName + '.profile'
kProfileFullpath = os.path.join(kProfileDirectory, kProfileFilename)
os.makedirs(kProfileDirectory, exist_ok = True) 

kDownloadedLootFilterFullpath = os.path.join(kDownloadDirectory, kDownloadedLootFilterFilename)
kPathOfExileLootFilterFullpath = os.path.join(kPathOfExileDirectory, kPathOfExileLootFilterFilename)

