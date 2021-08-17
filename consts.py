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

kChaosRecipeCategories = ['weapons',
                          'body_armours',
                          'helmets',
                          'gloves',
                          'boots',
                          'amulets',
                          'rings',
                          'belts']

kChaosRecipeBorderColors = {'weapons' : '200 0 0 255',
                            'body_armours' : '255 0 255 255',
                            'helmets' : '255 114 0 255',
                            'gloves' : '255 228 0 255',
                            'boots' : '0 255 0 255',
                            'amulets': '0 255 255 255',
                            'rings' : '65 0 189 255',
                            'belts' : '0 0 200 255'}

kChaosRecipeClasses = {'weapons' : '"Daggers" "Wands"',
                       'body_armours' : '"Body Armours"',
                       'helmets' : '"Helmets"',
                       'gloves' : '"Gloves"',
                       'boots' : '"Boots"',
                       'amulets': '"Amulets"',
                       'rings' : '"Rings"',
                       'belts' : '"Belts'}

kChaosRecipeMinimapIconSizeColorParams = {'weapons' : '2 Red',
                                          'body_armours' : '2 Pink',
                                          'helmets' : '2 Orange',
                                          'gloves' : '2 Yellow',
                                          'boots' : '2 Green',
                                          'amulets': '3 Cyan',
                                          'rings' : '3 Purple',
                                          'belts' : '2 Blue'}

kChaosRecipeMinimapIconType = 'Moon'

kChaosRecipeRuleStrings = [kChaosRecipeRuleTemplate.format(
                                   category,
                                   kChaosRecipeBorderColors[category],
                                   kChaosRecipeClasses[category],
                                   kChaosRecipeMinimapIconSizeColorParams[category],
                                   kChaosRecipeMinimapIconType)
                               for category in kChaosRecipeCategories]

