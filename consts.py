import re

import config

def InvertedDict(input_dict):
    return {value : key for key, value in input_dict.items()}

# =================================== Misc ===================================

kTableOfContentsIdentifier = '[WELCOME] TABLE OF CONTENTS'
kDlfAddedRulesSectionGroupId = '9900'
kDlfAddedRulesSectionGroupName = 'Dynamic Loot Filter Added Rules'

kSectionGroupHeaderTemplate = \
'''#===============================================================================================================
# [[{}]] {}
#==============================================================================================================='''

# Note: added a few extra dashes from NeverSink's template here
# 0: Numerical section id code
# 1: Section name
kSectionHeaderTemplate = \
'''#------------------------------------------------
#   [{0}] {1}
#------------------------------------------------'''

kSectionRePattern = re.compile(r'\[\d+\]+ .*')

kTypeTierTagTemplate = '$type->{} $tier->{}'

# ================================= Currency =================================

kCurrencyTierNames = {1 : 't1exalted',
                      2 : 't2divine',
                      3 : 't3annul',
                      4 : 't4chaos',
                      5 : 't5alchemy',
                      6 : 't6chrom',
                      7 : 't7chance',
                      8 : 't8trans',
                      9 : 't9armour'}
                      
kMaxCurrencyTier = len(kCurrencyTierNames) + 1

kCurrencyTierNameToNumberMap = InvertedDict(kCurrencyTierNames)

# ================================= Map Tier =================================

# No idea if the ShapedMap matters, but NeverSink used it in his filters
kHideMapsBelowTierRuleTemplate = \
'''Hide $type->dlf_hide_maps_below_tier $tier->dlf_hide_maps_below_tier
Class Maps
ShapedMap False
MapTier < {}'''

# ================================== Flasks ==================================

kFlaskRuleTemplate = \
'''# Show # $type->dlf_flasks $tier->dlf_flasks
# Rarity <= Magic
# BaseType
# SetFontSize 44
# SetBorderColor 50 200 125 255
# SetBackgroundColor 21 45 37
# PlayEffect Green Temp
# MinimapIcon 0 Green Raindrop'''

# =============================== Chaos Recipe ===============================

# 0: tier tag (we will use the item slot for this)
# 1: item class
# 2: optional height condition (e.g. 'Height <= 3')
# 3: border color (space-separated rgba values)
# 4: minimap icon size (0 = largest, 1 = medium, 2 = small)
# 5: minimap icon color (color keyword)
kChaosRecipeRuleTemplate = \
'''Show $type->dlf_chaos_recipe_rares $tier->{0}
ItemLevel >= 60
Rarity Rare
Class {1}{2}
Identified False
SetBorderColor {3}
SetFontSize 40
MinimapIcon {4} {5}'''

kChaosRecipeItemSlots = ['WeaponsX',
                         'Weapons3',
                         'Body Armours',
                         'Helmets',
                         'Gloves',
                         'Boots',
                         'Amulets',
                         'Rings',
                         'Belts']

# Need no spaces in tier tags
kChaosRecipeTierTags = {'WeaponsX' : 'weapons_any_height',
                        'Weapons3' : 'weapons_max_height_3',
                        'Body Armours' : 'body_armours',
                        'Body Armours' : 'body_armours',
                        'Helmets' : 'helmets',
                        'Gloves' : 'gloves',
                        'Boots' : 'boots',
                        'Amulets': 'amulets',
                        'Rings' : 'rings',
                        'Belts' : 'belts'}
                        
kChaosRecipeTierToItemSlotMap = InvertedDict(kChaosRecipeTierTags)

kChaosRecipeWeaponClassesAnyHeightString = \
        '"' + '" "'.join(config.kChaosRecipeWeaponClassesAnyHeight) + '"'
kChaosRecipeWeaponClassesmaxHeight3String = \
        '"' + '" "'.join(config.kChaosRecipeWeaponClassesMaxHeight3) + '"'

kChaosRecipeClasses = {'WeaponsX' : kChaosRecipeWeaponClassesAnyHeightString,
                       'Weapons3' : kChaosRecipeWeaponClassesmaxHeight3String,
                       'Body Armours' : '"Body Armours"',
                       'Helmets' : '"Helmets"',
                       'Gloves' : '"Gloves"',
                       'Boots' : '"Boots"',
                       'Amulets': '"Amulets"',
                       'Rings' : '"Rings"',
                       'Belts' : '"Belts"'}

kChaosRecipeHeightConditions = {item_slot : (
        '\nHeight <= 3' if item_slot == 'Weapons3' else '')
        for item_slot in kChaosRecipeItemSlots}

kChaosRecipeBorderColors = {'WeaponsX' : '200 0 0 255',
                            'Weapons3' : '200 0 0 255',
                            'Body Armours' : '255 0 255 255',
                            'Helmets' : '255 114 0 255',
                            'Gloves' : '255 228 0 255',
                            'Boots' : '0 255 0 255',
                            'Amulets': '0 255 255 255',
                            'Rings' : '65 0 189 255',
                            'Belts' : '0 0 200 255'}

kChaosRecipeMinimapIconSizeColorParams = {'WeaponsX' : '1 Red',
                                          'Weapons3' : '1 Red',
                                          'Body Armours' : '1 Pink',
                                          'Helmets' : '1 Orange',
                                          'Gloves' : '1 Yellow',
                                          'Boots' : '1 Green',
                                          'Amulets': '0 Cyan',
                                          'Rings' : '0 Purple',
                                          'Belts' : '1 Blue'}

kChaosRecipeMinimapIconType = 'Moon'

kChaosRecipeRuleStrings = [kChaosRecipeRuleTemplate.format(
                                   kChaosRecipeTierTags[item_slot],
                                   kChaosRecipeClasses[item_slot],
                                   kChaosRecipeHeightConditions[item_slot],
                                   kChaosRecipeBorderColors[item_slot],
                                   kChaosRecipeMinimapIconSizeColorParams[item_slot],
                                   kChaosRecipeMinimapIconType)
                               for item_slot in kChaosRecipeItemSlots]

