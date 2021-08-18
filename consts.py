# =================================== Misc ===================================

kTableOfContentsIdentifier = '[WELCOME] TABLE OF CONTENTS'

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

kCurrencyTierNameToNumberMap = {value : key for key, value in kCurrencyTierNames.items()}

# =============================== Chaos Recipe ===============================

kChaosRecipeRuleTemplate = \
'''Show $type->chaos_recipe_rare $tier->{}
SetBorderColor {}
SetFontSize 40
ItemLevel >= 60
Rarity Rare
Class {}
MinimapIcon {} {}'''

kChaosRecipeCategories = ['Weapons',
                          'Body Armours',
                          'Helmets',
                          'Gloves',
                          'Boots',
                          'Amulets',
                          'Rings',
                          'Belts']

kChaosRecipeBorderColors = {'Weapons' : '200 0 0 255',
                            'Body Armours' : '255 0 255 255',
                            'Helmets' : '255 114 0 255',
                            'Gloves' : '255 228 0 255',
                            'Boots' : '0 255 0 255',
                            'Amulets': '0 255 255 255',
                            'Rings' : '65 0 189 255',
                            'Belts' : '0 0 200 255'}

kChaosRecipeClasses = {'Weapons' : '"Daggers" "Wands"',
                       'Body Armours' : '"Body Armours"',
                       'Helmets' : '"Helmets"',
                       'Gloves' : '"Gloves"',
                       'Boots' : '"Boots"',
                       'Amulets': '"Amulets"',
                       'Rings' : '"Rings"',
                       'Belts' : '"Belts'}

kChaosRecipeMinimapIconSizeColorParams = {'Weapons' : '2 Red',
                                          'Body Armours' : '2 Pink',
                                          'Helmets' : '2 Orange',
                                          'Gloves' : '2 Yellow',
                                          'Boots' : '2 Green',
                                          'Amulets': '3 Cyan',
                                          'Rings' : '3 Purple',
                                          'Belts' : '2 Blue'}

kChaosRecipeMinimapIconType = 'Moon'

kChaosRecipeRuleStrings = [kChaosRecipeRuleTemplate.format(
                                   category,
                                   kChaosRecipeBorderColors[category],
                                   kChaosRecipeClasses[category],
                                   kChaosRecipeMinimapIconSizeColorParams[category],
                                   kChaosRecipeMinimapIconType)
                               for category in kChaosRecipeCategories]

