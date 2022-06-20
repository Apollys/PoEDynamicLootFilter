import itertools
import os.path
import re

import file_helper

def InvertedDict(input_dict):
    return {value : key for key, value in input_dict.items()}

kDlfVersion = '1.1.0'

#=================================== Items ===================================

kRarityList = ['Normal', 'Magic', 'Rare', 'Unique']
kInverseRarityMap = {rarity : index for index, rarity in enumerate(kRarityList)}

# =================================== Misc ===================================

kDlfHeaderTemplate = \
'''#==============================================================================================================#
# PoE Dynamic Loot Filter: This filter has been modified by Dynamic Loot Filter version {}.                 #
#==============================================================================================================#'''

kDlfHeaderKey = ('dlf_header', 'dlf_header')

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
'''#-------------------------------------------------------------------------------
#   [{0}] {1}
#-------------------------------------------------------------------------------'''

kSectionRePattern = re.compile(r'\[\d+\]+ .*')

kTypeTierTagTemplate = '$type->{} $tier->{}'

kUntaggedRuleTypeTag = 'untagged_rule'

# ================================= Currency =================================

kUnstackedCurrencyTierTags = ['t1exalted', 't2divine', 't3annul', 't4chaos', 't5alchemy',
        't6chrom', 't7chance', 't8trans', 't9armour', 'tportal', 'twisdom']

kNumCurrencyTiersIncludingScrolls = len(kUnstackedCurrencyTierTags)
kNumCurrencyTiersExcludingScrolls = kNumCurrencyTiersIncludingScrolls - 2

# Concatenating dictionaries in python, from a StackOverflow comment:
# "1={1:2,3:4}; d2={5:6,7:9}; d3={10:8,13:22}; d4 = {**d1, **d2, **d3}"
# <https://stackoverflow.com/a/1784128/7022459>
kCurrencyTierStringToIntMap = dict(
    { str(i) : i for i in range(1, kNumCurrencyTiersExcludingScrolls + 1) },
    tportal = kNumCurrencyTiersExcludingScrolls + 1,
    twisdom = kNumCurrencyTiersExcludingScrolls + 2
)

def GenerateStackedCurrencyTags():
    stacked_currency_tags = {
        i : list(itertools.product(
            ('currency->stackedthree', 'currency->stackedsix'), ('t{}'.format(i), )))
            for i in range(1, 8)}
    stacked_currency_tags[8] = list(itertools.product(
            ('currency->stackedsupplieshigh', ), ('t3', 't2', 't1')))
    stacked_currency_tags[9] = list(itertools.product(
            ('currency->stackedsupplieslow', ), ('t3', 't2', 't1')))
    # Use indices 10/11 for portal/wisdom scrolls
    stacked_currency_tags[10] = list(itertools.product(
            ('currency->stackedsuppliesportal', ), ('t3', 't2', 't1')))
    stacked_currency_tags[11] = list(itertools.product(
            ('currency->stackedsupplieswisdom', ), ('t3', 't2', 't1')))
    return stacked_currency_tags
# End GenerateStackedCurrencyTags

kStackedCurrencyTags = GenerateStackedCurrencyTags()

kCurrencyStackSizes = [1, 2, 4, 6, 100]  # 100 as a sentinel for hide_all

kCurrencyStackSizesByTier = {
    tier : kCurrencyStackSizes[ : len(kStackedCurrencyTags[tier]) + 1]
    for tier in range(1, kNumCurrencyTiersIncludingScrolls + 1)
}

kCurrencyStackSizeStringToIntMap = {
    **{ s : int(s) for s in (str(i) for i in kCurrencyStackSizes) }, **{ 'hide_all' : 100}}

# kUnifiedCurrencyTags[tier][stack_size] -> (type_tag, tier_tag)
kUnifiedCurrencyTags = { tier :
    { stack_size :
        (kStackedCurrencyTags[tier][i - 1] if stack_size > 1
        else ('currency', kUnstackedCurrencyTierTags[tier - 1]))
        for i, stack_size in enumerate(kCurrencyStackSizesByTier[tier])
    } for tier in range(1, kNumCurrencyTiersIncludingScrolls + 1)
}

# ================================= Map Tier =================================

kHideMapsBelowTierTags = ('dlf_hide_maps_below_tier', 'dlf_hide_maps_below_tier')

# No idea if the ShapedMap matters, but NeverSink used it in his filters
kHideMapsBelowTierRuleTemplate = \
'''Hide # $type->{} $tier->{}
Class Maps
ShapedMap False
Rarity ! Unique
MapTier < {}'''.format(*kHideMapsBelowTierTags, '{}')

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

# ================================== BaseTypes ==================================

kBaseTypeTypeTag = 'dlf_base_types'
kBaseTypeTierTagRare = 'rare'
kBaseTypeTierTagAny = 'any_non_unique'

kBaseTypeRuleTemplateRare = \
'''# Show # $type->{} $tier->{}
# Rarity == Rare
# SetFontSize 44
# PlayEffect Yellow Temp'''.format(kBaseTypeTypeTag, kBaseTypeTierTagRare)

kBaseTypeRuleTemplateAny = \
'''# Show # $type->{} $tier->{}
# Rarity ! Unique
# SetFontSize 44
# PlayEffect White Temp'''.format(kBaseTypeTypeTag, kBaseTypeTierTagAny)

# ================================== Flasks ==================================

kFlaskRuleTemplate = \
'''# Show # $type->dlf_flasks $tier->dlf_flasks
# Rarity <= Magic
# SetFontSize 44
# SetBorderColor 50 200 125 255
# SetBackgroundColor 21 45 37
# PlayEffect Green Temp
# MinimapIcon 0 Green Raindrop'''

kHighIlvlFlaskRuleTemplate = \
'''# Show # $type->dlf_flasks $tier->dlf_flasks_high_ilvl
# ItemLevel >= 84
# Rarity <= Magic
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

kChaosRecipeTypeTag = 'dlf_chaos_recipe_rares'

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
kFlaskBaseTypesTxtFilepath = os.path.join('Resources', 'flask_base_types.txt')
kAllFlaskTypes = file_helper.ReadFile(kFlaskBaseTypesTxtFilepath, strip=True)

# Quality Gems and Flasks tags

kQualityGemsTypeTag = 'gems-generic'

kQualityFlasksTypeTag = 'endgameflasks'

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

