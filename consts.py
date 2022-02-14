import itertools
import re

def InvertedDict(input_dict):
    return {value : key for key, value in input_dict.items()}

#=================================== Items ===================================

kRarityList = ['Normal', 'Magic', 'Rare', 'Unique']
kInverseRarityMap = {rarity : index for index, rarity in enumerate(kRarityList)}

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
'''#----------------------------------------------------
#   [{0}] {1}
#----------------------------------------------------'''

kSectionRePattern = re.compile(r'\[\d+\]+ .*')

kTypeTierTagTemplate = '$type->{} $tier->{}'

# ================================= Currency =================================

kCurrencyTypeTag = 'currency'

kCurrencyTierNames = {1 : 't1exalted',
                      2 : 't2divine',
                      3 : 't3annul',
                      4 : 't4chaos',
                      5 : 't5alchemy',
                      6 : 't6chrom',
                      7 : 't7chance',
                      8 : 't8trans',
                      9 : 't9armour',
                      10: 'tportal',
                      11: 'twisdom'}

kStackedCurrencyTags = {
    i : list(itertools.product(
        ('currency->stackedthree', 'currency->stackedsix'), ('t{}'.format(i), )))
        for i in range(1, 8)}
kStackedCurrencyTags[8] = list(itertools.product(
        ('currency->stackedsupplieshigh', ), ('t3', 't2', 't1')))
kStackedCurrencyTags[9] = list(itertools.product(
        ('currency->stackedsupplieslow', ), ('t3', 't2', 't1')))
# Use indices 10/11 for portal/wisdom scrolls
kStackedCurrencyTags[10] = list(itertools.product(
        ('currency->stackedsuppliesportal', ), ('t3', 't2', 't1')))
kStackedCurrencyTags[11] = list(itertools.product(
        ('currency->stackedsupplieswisdom', ), ('t3', 't2', 't1')))

kMaxCurrencyTier = len(kCurrencyTierNames) - 2

kCurrencyStackSizes = [1, 2, 4, 6]

kCurrencyTierNameToNumberMap = InvertedDict(kCurrencyTierNames)

# ================================= Map Tier =================================

# No idea if the ShapedMap matters, but NeverSink used it in his filters
kHideMapsBelowTierRuleTemplate = \
'''Hide # $type->dlf_hide_maps_below_tier $tier->dlf_hide_maps_below_tier
Class Maps
ShapedMap False
MapTier < {}'''

# ================================= Essences =================================

kNumEssenceTiers = 6
kEssenceTags = {
        i : ('currency->essence', 't{}'.format(i))
        for i in range(1, kNumEssenceTiers + 1)
}

# ================================ Div Cards =================================

kDivCardTierTags = ['t1', 't2', 't3', 't4c', 't4', 't5c', 't5', 'restex'] 
kDivCardTags = {
        i + 1 : ('divination', kDivCardTierTags[i])
        for i in range(len(kDivCardTierTags))
}
kNumDivCardTiers = len(kDivCardTierTags)

# =============================== Unique Items ===============================

kUniqueItemTierTags = ['t1', 't2', 't3', 'hideable2', 'hideable']
kUniqueItemTags = {
        i + 1 : ('uniques', kUniqueItemTierTags[i])
        for i in range(len(kUniqueItemTierTags))
}
kNumUniqueItemTiers = len(kUniqueItemTierTags)

# =============================== Unique Maps ================================

kUniqueMapTierTags = ['t1', 't2', 't3', 't4'] 
kUniqueMapTags = {
        i + 1 : ('uniques->maps', kUniqueMapTierTags[i])
        for i in range(len(kUniqueMapTierTags))
}
kNumUniqueMapTiers = len(kUniqueMapTierTags)

# ================================== Flasks ==================================

kFlaskRuleTemplate = \
'''# Show # $type->dlf_flasks $tier->dlf_flasks
# BaseType
# Rarity <= Magic
# SetFontSize 44
# SetBorderColor 50 200 125 255
# SetBackgroundColor 21 45 37
# PlayEffect Green Temp
# MinimapIcon 0 Green Raindrop'''

kHighIlvlFlaskRuleTemplate = \
'''# Show # $type->dlf_flasks $tier->dlf_flasks_high_ilvl
# BaseType
# ItemLevel >= 84
# Rarity <= Magic
# SetFontSize 44
# SetBorderColor 50 200 125 255
# SetBackgroundColor 21 45 37
# PlayEffect Green Temp
# MinimapIcon 0 Green Raindrop'''

# ================================== Archnemesis ==================================

kArchnemesisTierTags = ['t1', 't2', 't3', 'thide'] 
kArchnemesisTags = { i + 1 : ('dlf_archnemesis', kArchnemesisTierTags[i])
        for i in range(len(kArchnemesisTierTags))}
kNumArchnemesisTiers = len(kArchnemesisTierTags)

kArchnemesisRuleTemplates = [
'''# Show # $type->dlf_archnemesis $tier->t1
# ArchnemesisMod
# Class "Archnemesis Mod"
# SetFontSize 45
# SetTextColor 252 3 144 255
# SetBorderColor 252 3 144 255
# SetBackgroundColor 0 0 0 255
# PlayAlertSound 3 300
# PlayEffect Pink
# MinimapIcon 0 Pink Pentagon''',

'''# Show # $type->dlf_archnemesis $tier->t2
# ArchnemesisMod
# Class "Archnemesis Mod"
# SetFontSize 45
# SetTextColor 3 252 240 255
# SetBorderColor 3 252 240 255
# SetBackgroundColor 0 0 0 255
# PlayAlertSound 3 300
# PlayEffect Cyan
# MinimapIcon 0 Cyan Pentagon''',

'''# Show # $type->dlf_archnemesis $tier->t3
# ArchnemesisMod
# Class "Archnemesis Mod"
# SetFontSize 45
# SetTextColor 74 230 58 255
# SetBorderColor 74 230 58 255
# SetBackgroundColor 0 0 0 255
# PlayAlertSound 3 300
# PlayEffect Green
# MinimapIcon 0 Green Pentagon''',

'''# Hide # $type->dlf_archnemesis $tier->thide
# ArchnemesisMod
# Class "Archnemesis Mod"
# SetFontSize 30
# SetTextColor 74 230 58 255
# SetBorderColor 74 230 58 255
# SetBackgroundColor 0 0 0 255'''
]


# =============================== Chaos Recipe ===============================

# 0: tier tag (we will use the item slot for this)
# 1: item class
# 2: optional height condition (e.g. 'Height <= 3')
# 3: border color (space-separated rgba values)
# 4: minimap icon size (0 = largest, 1 = medium, 2 = small)
# 5: minimap icon color (color keyword)
kChaosRecipeRuleTemplate = \
'''Show # $type->dlf_chaos_recipe_rares $tier->{0}
ItemLevel >= 60
Rarity Rare
Class {1}{2}
Identified False
SetBorderColor {3}
SetFontSize 40
MinimapIcon {4} {5}'''

kChaosRecipeItemSlots = ['Weapons',
                         'Body Armours',
                         'Helmets',
                         'Gloves',
                         'Boots',
                         'Amulets',
                         'Rings',
                         'Belts']

kChaosRecipeItemSlotsMinusWeapons = kChaosRecipeItemSlots[1:]

kChaosRecipeItemSlotsInternal = ['WeaponsX', 'Weapons3'] + kChaosRecipeItemSlotsMinusWeapons

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

kChaosRecipeClasses = {'WeaponsX' : 'XXX_Unused',
                       'Weapons3' : 'XXX_Unused',
                       'Body Armours' : '"Body Armours"',
                       'Helmets' : '"Helmets"',
                       'Gloves' : '"Gloves"',
                       'Boots' : '"Boots"',
                       'Amulets': '"Amulets"',
                       'Rings' : '"Rings"',
                       'Belts' : '"Belts"'}

kChaosRecipeHeightConditions = {item_slot : (
        '\nHeight <= 3' if item_slot == 'Weapons3' else '')
        for item_slot in kChaosRecipeItemSlotsInternal}

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

# All non-weapon chaos recipe rules (weapons handled in function below)
kChaosRecipeRuleStrings = [kChaosRecipeRuleTemplate.format(
                                   kChaosRecipeTierTags[item_slot],
                                   kChaosRecipeClasses[item_slot],
                                   kChaosRecipeHeightConditions[item_slot],
                                   kChaosRecipeBorderColors[item_slot],
                                   kChaosRecipeMinimapIconSizeColorParams[item_slot],
                                   kChaosRecipeMinimapIconType)
                               for item_slot in kChaosRecipeItemSlotsMinusWeapons]

# Generate chaos recipe rule for 'WeaponsX' or 'Weapons3'
def GenerateChaosRecipeWeaponRule(item_slot: str, weapon_classes: str) -> str:
    if ((item_slot != 'WeaponsX') and (item_slot != 'Weapons3')):
        raise RuntimeError('item_slot must be either "WeaponsX" or "Weapons3"')
    return kChaosRecipeRuleTemplate.format(
               kChaosRecipeTierTags[item_slot],
               weapon_classes,
               kChaosRecipeHeightConditions[item_slot],
               kChaosRecipeBorderColors[item_slot],
               kChaosRecipeMinimapIconSizeColorParams[item_slot],
               kChaosRecipeMinimapIconType)
# End GenerateChaosRecipeWeaponRule

# List of all Flask BaseTypes
kAllFlaskTypes = [
        'Divine Life Flask', 'Eternal Life Flask', 'Divine Mana Flask', 'Eternal Mana Flask',
        'Hallowed Hybrid Flask', 'Quicksilver Flask', 'Bismuth Flask', 'Amethyst Flask',
        'Ruby Flask', 'Sapphire Flask', 'Topaz Flask', 'Aquamarine Flask',
        'Diamond Flask', 'Granite Flask', 'Jade Flask', 'Quartz Flask', 'Sulphur Flask',
        'Basalt Flask', 'Silver Flask', 'Stibnite Flask']

# RGB Item consts

kRgbTypeTag = 'endgamergb'

# maps size_string to (size_int, tier_tag_list)
kRgbSizesMap = {'none': (0, []),
                'small': (4, ['rgbsmall1', 'rgbsmall2']),
                'medium': (6, ['rgbmedium']),
                'large': (8, ['rgblarge'])}

# Blight Oils consts

kOilTypeTag = 'currency->oil'
kOilHideTierTag = 'restex'
kMaxOilTier = 4

kOilTierList = [
        ('Tainted Oil', 1), ('Golden Oil', 1),
        ('Silver Oil', 2), ('Opalescent Oil', 2),
        ('Black Oil', 3), ('Crimson Oil', 3), ('Violet Oil', 3), ('Indigo Oil', 3),
        ('Azure Oil', 4), ('Teal Oil', 4), ('Verdant Oil', 4), ('Amber Oil', 4),
        ('Sepia Oil', 4), ('Clear Oil', 4)]

