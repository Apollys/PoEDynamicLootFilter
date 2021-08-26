# Profile name
kProfileName = 'DefaultProfile'

# Loot filter file locations
kDownloadDirectory = 'FiltersDownload'
kInputLootFilterDirectory = 'FiltersInput'
kPathOfExileDirectory = 'FiltersPathOfExile'
kDownloadedLootFilterFilename = 'BrandLeaguestart.filter'
kPathOfExileLootFilterFilename = 'AAA_DynamicLootFilter.filter'

# Remove filter from Downloads directory when importing?
# Filter will still be saved in Input directory regardless
kRemoveDownloadedFilter = False  # default will be True later, False for testing

# Loot filter options
kHideMapsBelowTier = 0
kAddChaosRecipeRules = True
kChaosRecipeWeaponClassesAnyHeight = ['Daggers', 'Rune Daggers', 'Wands']
kChaosRecipeWeaponClassesMaxHeight3 = ['Bows']

# ============== Derived Values and Fixed Constants - Do not modify below this line ==============

import os
import os.path

kProfileDirectory = 'Profiles'
kProfileFullpath = os.path.join(kProfileDirectory, kProfileName + '.profile')
kCustomRulesFullpath = os.path.join(kProfileDirectory, kProfileName + '.rules')

kDownloadedLootFilterFullpath = os.path.join(kDownloadDirectory, kDownloadedLootFilterFilename)
kInputLootFilterFullpath = os.path.join(kInputLootFilterDirectory, kDownloadedLootFilterFilename)
kPathOfExileLootFilterFullpath = os.path.join(kPathOfExileDirectory, kPathOfExileLootFilterFilename)

# Check that necessary files and directories exists, throw error if not
if (not os.path.isdir(kDownloadDirectory)):
    raise RuntimeError('download directory: "{}" does not exist'.format(kDownloadDirectory))
    
if (not os.path.isdir(kPathOfExileDirectory)):
    raise RuntimeError('download directory: "{}" does not exist'.format(kPathOfExileDirectory))

# Make other missing directories (for which their absence is not an error)
os.makedirs(kInputLootFilterDirectory, exist_ok = True) 

os.makedirs(kProfileDirectory, exist_ok = True) 

