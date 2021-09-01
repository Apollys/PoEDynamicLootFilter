import rule_parser

# item_text, rule_text, expected_result triplets
test_cases = [
# Simple chaos orb matching test
('''Item Class: Stackable Currency
Rarity: Currency
Chaos Orb
--------
Stack Size: 37/10
--------
Reforges a rare item with new random modifiers
--------
Right click this item then left click a rare item to apply it.
Shift click to unstack.''',

'''Show # $type->currency $tier->t4chaos
Class "Currency"
BaseType "Accelerating Catalyst" "Ancient Shard" "Awakened Sextant" "Chaos Orb" "Fertile Catalyst"
SetFontSize 45
SetTextColor 30 200 200 255
SetBorderColor 30 200 200 255
SetBackgroundColor 0 0 69
PlayEffect Blue
MinimapIcon 1 Blue Circle
PlayAlertSound 2 300''',

True),

# Chaos orb to "Veiled Chaos Orb" match test - should be False
('''Item Class: Stackable Currency
Rarity: Currency
Chaos Orb
--------
Stack Size: 37/10
--------
Reforges a rare item with new random modifiers
--------
Right click this item then left click a rare item to apply it.
Shift click to unstack.''',

'''Show # $type->currency $tier->t4chaos
Class "Currency"
BaseType "Ancient Shard" "Awakened Sextant" "Veiled Chaos Orb" "Fertile Catalyst"
SetFontSize 45
SetTextColor 30 200 200 255
SetBorderColor 30 200 200 255
SetBackgroundColor 0 0 69
PlayEffect Blue
MinimapIcon 1 Blue Circle
PlayAlertSound 2 300''',

False),

# Map test with hide maps below tier rule
('''Item Class: Maps
Rarity: Magic
Twinned Marshes Map of Impotence
--------
Map Tier: 11
Atlas Region: Glennach Cairns
Item Quantity: +32% (augmented)
Item Rarity: +19% (augmented)
Monster Pack Size: +12% (augmented)
--------
Item Level: 82
--------
Area contains two Unique Bosses
Players have 25% less Area of Effect
--------
Travel to this Map by using it in a personal Map Device. Maps can only be used once.''',

'''Hide $type->dlf_hide_maps_below_tier $tier->dlf_hide_maps_below_tier
Class Maps
ShapedMap False
MapTier < 13''',

True),

# False positive test for above
('''Item Class: Maps
Rarity: Normal
Terrace Map
--------
Map Tier: 16
Atlas Region: Tirn's End
--------
Item Level: 83
--------
Travel to this Map by using it in a personal Map Device. Maps can only be used once.''',

'''Hide $type->dlf_hide_maps_below_tier $tier->dlf_hide_maps_below_tier
Class Maps
ShapedMap False
MapTier < 13''',

False),

# Item level test (rare high level crafting bases rule)
('''Item Class: Boots
Rarity: Rare
Doom Pace
Sorcerer Boots
--------
Energy Shield: 60 (augmented)
--------
Requirements:
Level: 67
Int: 123
--------
Sockets: B-B B 
--------
Item Level: 65
--------
+11 to maximum Energy Shield
+115 to maximum Life
+57 to maximum Mana
+15% to Lightning Resistance
22% increased Stun and Block Recovery''',

'''Show $type->untagged_rule $tier->18
SetBorderColor 255 190 0 255
SetFontSize 45
ItemLevel >= 65
Rarity Rare
BaseType "Sorcerer Boots" "Sorcerer Gloves" "Crystal Belt" "Hubris Circlet" "Imbued Wand" "Opal Wand" "Void Sceptre" "Crystal Sceptre" "Abyssal Sceptre" "Opal Sceptre" "Platinum Sceptre" "Vaal Sceptre" "Carnal Sceptre" "Pagan Wand" "Heathen Wand" "Profane Wand" "Prophecy Wand" "Tornado Wand" "Crystal Wand" "Omen Wand" "Serpent Wand"
SetTextColor 255 190 0 255
SetBackgroundColor 36 39 19 255
PlayAlertSound 13 202
MinimapIcon 1 Yellow Cross
PlayEffect Yellow''',

True),

# Item level test - mismatch test (ilevel too low)
('''Item Class: Boots
Rarity: Rare
Doom Pace
Sorcerer Boots
--------
Energy Shield: 60 (augmented)
--------
Requirements:
Level: 67
Int: 123
--------
Sockets: B-B B 
--------
Item Level: 64
--------
+11 to maximum Energy Shield
+115 to maximum Life
+57 to maximum Mana
+15% to Lightning Resistance
22% increased Stun and Block Recovery''',

'''Show $type->untagged_rule $tier->18
SetBorderColor 255 190 0 255
SetFontSize 45
ItemLevel >= 65
Rarity Rare
BaseType "Sorcerer Boots" "Sorcerer Gloves" "Crystal Belt" "Hubris Circlet" "Imbued Wand" "Opal Wand" "Void Sceptre" "Crystal Sceptre" "Abyssal Sceptre" "Opal Sceptre" "Platinum Sceptre" "Vaal Sceptre" "Carnal Sceptre" "Pagan Wand" "Heathen Wand" "Profane Wand" "Prophecy Wand" "Tornado Wand" "Crystal Wand" "Omen Wand" "Serpent Wand"
SetTextColor 255 190 0 255
SetBackgroundColor 36 39 19 255
PlayAlertSound 13 202
MinimapIcon 1 Yellow Cross
PlayEffect Yellow''',

False)]

def Test():
    all_tests_passed = True
    for test_item, test_rule, expected_result in test_cases:
        item_lines = test_item.split('\n')
        item_name = item_lines[2] if item_lines[3].startswith('-') else ' '.join(item_lines[2:4])
        print('Running test for "{}", expecting match = {}'.format(
                item_name, expected_result))
        rule_lines = test_rule.split('\n')
        parsed_rule_lines = [rule_parser.ParseRuleLineGeneric(line) for line in rule_lines]
        match_flag = rule_parser.CheckRuleMatchesItem(parsed_rule_lines, item_lines)
        test_passed = (match_flag == expected_result)
        print(' -> match result = {}, test {}\n'.format(match_flag,
                'Passed!' if test_passed else 'Failed!'))
        all_tests_passed = all_tests_passed and test_passed
    if (all_tests_passed):
        print('All tests passed!')
    else:
        print('At least one test failed.')
# End Test

Test()


