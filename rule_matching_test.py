from item import Item, RuleMatchesItem
from item_test import ParseTestCases
from loot_filter import InputFilterSource, LootFilter
from loot_filter_rule import LootFilterRule
import test_consts
from test_assertions import AssertEqual, AssertTrue, AssertFalse
import test_helper

# item_text, rule_text, expected_result triplets
kTestCases = [
# 6 Socket test
('''Item Class: Body Armours
Rarity: Rare
Morbid Carapace
Saint's Hauberk
--------
Armour: 672 (augmented)
Energy Shield: 134 (augmented)
--------
Requirements:
Level: 67
Str: 109
Int: 94
--------
Sockets: B-B-B-B B-R 
--------
Item Level: 81
--------
+5 to Armour
50% increased Armour and Energy Shield
+13 to maximum Energy Shield
+15 to maximum Mana
+42% to Cold Resistance
''',

'''Show # %DS3 $type->socketslinks $tier->6sockets
	Sockets >= 6
	Rarity <= Rare
	SetFontSize 45
	SetTextColor 255 255 255 255
	SetBorderColor 255 255 255 255
	SetBackgroundColor 0 112 106 255
	PlayAlertSound 2 300
	PlayEffect Grey
	MinimapIcon 2 Grey Hexagon
''',

True),

# 6 Link test
('''Item Class: Two Hand Axes
Rarity: Rare
Wrath Beak
Void Axe
--------
Two Handed Axe
Physical Damage: 98-149 (augmented)
Elemental Damage: 3-6 (augmented)
Critical Strike Chance: 6.00%
Attacks per Second: 1.25
Weapon Range: 13
--------
Requirements:
Level: 68
Str: 149
Dex: 76
--------
Sockets: G-R-R-R-R-R 
--------
Item Level: 81
--------
Adds 2 to 5 Physical Damage
Adds 3 to 6 Cold Damage
+10% to Global Critical Strike Multiplier
+182 to Accuracy Rating
--------
Note: ~price 8 chaos''',

'''Show # $type->6l $tier->wep
LinkedSockets 6
Rarity <= Rare
SetFontSize 45
SetTextColor 255 255 255 255
SetBorderColor 255 255 255 255
SetBackgroundColor 200 0 0 255
PlayAlertSound 1 300
PlayEffect Red
MinimapIcon 0 Red Diamond''',

True),

# Enlighten test - Gem lower level than rule requires
('''Item Class: Support Skill Gems
Rarity: Gem
Enlighten Support
--------
Support
Level: 1
--------
Requirements:
Level: 1
--------
Supports any skill gem. Once this gem reaches level 2 or above, will apply a mana multiplier to supported gems. Cannot support skills that don't come from gems.
--------
Experience: 54217488/226854909
--------
This is a Support Gem. It does not grant a bonus to your character, but to skills in sockets connected to it. Place into an item socket connected to a socket containing the Active Skill Gem you wish to augment. Right click to remove from a socket.
--------
Corrupted
--------
Note: ~price 1 exalted''',

'''Show # $type->gems-special $tier->exspeciale4
GemLevel >= 4
Class "Gems"
BaseType "Empower" "Enhance" "Enlighten"
SetFontSize 45
SetTextColor 0 0 125 255
SetBorderColor 0 0 125 255
SetBackgroundColor 255 255 255 255
PlayAlertSound 6 300
PlayEffect Red
MinimapIcon 0 Red Star''',

False),

# Simple chaos orb matching test
('''Item Class: Stackable Currency
Rarity: Currency
Chaos Orb
--------
Stack Size: 7/10
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

# "Chaos Orb" vs "Veiled Chaos Orb" - mismatch test
('''Item Class: Stackable Currency
Rarity: Currency
Chaos Orb
--------
Stack Size: 7/10
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

# Map Tier test
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

# Mismatch Map Tier test - map tier too high
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

False),

# Replica Unique test
('''Item Class: Body Armours
Rarity: Unique
Replica Farrul's Fur
Triumphant Lamellar
--------
Armour: 764 (augmented)
Evasion Rating: 959 (augmented)
--------
Requirements:
Level: 69
Str: 95
Dex: 116
--------
Sockets: R-R-G-R G 
--------
Item Level: 75
--------
101% increased Armour and Evasion
+98 to maximum Life
+2.00 seconds to Cat's Agility Duration
Aspect of the Cat has no Reservation
Gain up to your maximum number of Frenzy and Endurance Charges when you gain Cat's Agility
You have Onslaught while you have Cat's Agility
--------
"Attempt #120: the prototype has finally achieved power similar to the original
without breaking all the bones of the test subject. A rousing success."
--------
Note: ~price 20 exalted''',

'''Show # $type->uniques->replicas $tier->t1
Replica True
Rarity Unique
BaseType == "Chain Belt" "Cloth Belt" "Great Crown" "Leather Belt" "Ornate Quiver" "Relic Chambers Map" "Soldier Boots" "Synthesised Map" "Triumphant Lamellar"
SetFontSize 45
SetTextColor 175 96 37 255
SetBorderColor 175 96 37 255
SetBackgroundColor 255 255 255 255
PlayAlertSound 6 300
PlayEffect Red
MinimapIcon 0 Red Star''',

True),

# Influenced item test
('''Item Class: Shields
Rarity: Rare
Soul Weaver
Titanium Spirit Shield
--------
Quality: +20% (augmented)
Chance to Block: 25%
Energy Shield: 157 (augmented)
--------
Requirements:
Level: 70
Dex: 155
Int: 159
--------
Sockets: G-G-B 
--------
Item Level: 84
--------
Socketed Gems have 15% reduced Reservation
+109 to maximum Life
+48% to Fire Resistance
10% increased effect of Non-Curse Auras from your Skills
+67 to maximum Energy Shield (crafted)
--------
Shaper Item
Redeemer Item''',

'''Show # %D3 $type->rare->any $tier->any
	HasInfluence Crusader Elder Hunter Redeemer Shaper Warlord
	Rarity <= Rare
	SetFontSize 45
	SetTextColor 255 255 255 255
	SetBorderColor 255 255 255 255
	SetBackgroundColor 50 130 165
	PlayEffect Blue Temp''',
    
True),

# Mismatch influence test
('''Item Class: Shields
Rarity: Rare
Soul Weaver
Titanium Spirit Shield
--------
Quality: +20% (augmented)
Chance to Block: 25%
Energy Shield: 157 (augmented)
--------
Requirements:
Level: 70
Dex: 155
Int: 159
--------
Sockets: G-G-B 
--------
Item Level: 84
--------
Socketed Gems have 15% reduced Reservation
+109 to maximum Life
+48% to Fire Resistance
10% increased effect of Non-Curse Auras from your Skills
+67 to maximum Energy Shield (crafted)
--------
Shaper Item
Redeemer Item''',

'''Show # %D3 $type->rare->any $tier->any
	HasInfluence Crusader Elder Hunter Warlord
	Rarity <= Rare
	SetFontSize 45
	SetTextColor 255 255 255 255
	SetBorderColor 255 255 255 255
	SetBackgroundColor 50 130 165
	PlayEffect Blue Temp''',
    
False),

# None influence test - mismatch
('''Item Class: Shields
Rarity: Rare
Soul Weaver
Titanium Spirit Shield
--------
Quality: +20% (augmented)
Chance to Block: 25%
Energy Shield: 157 (augmented)
--------
Requirements:
Level: 70
Dex: 155
Int: 159
--------
Sockets: G-G-B 
--------
Item Level: 84
--------
Socketed Gems have 15% reduced Reservation
+109 to maximum Life
+48% to Fire Resistance
10% increased effect of Non-Curse Auras from your Skills
+67 to maximum Energy Shield (crafted)
--------
Shaper Item
Redeemer Item''',

'''Show # %D3 $type->rare->any $tier->any
	HasInfluence None
	Rarity <= Rare
	SetFontSize 45
	SetTextColor 255 255 255 255
	SetBorderColor 255 255 255 255
	SetBackgroundColor 50 130 165
	PlayEffect Blue Temp''',
    
False),

# None influence test - match
('''Item Class: Wands
Rarity: Rare
Phoenix Song
Imbued Wand
--------
Wand
Quality: +20% (augmented)
Physical Damage: 35-64 (augmented)
Elemental Damage: 60-103 (augmented), 49-85 (augmented), 9-164 (augmented)
Critical Strike Chance: 9.66% (augmented)
Attacks per Second: 1.68 (augmented)
--------
Requirements:
Level: 72
Str: 73
Int: 188 (unmet)
--------
Sockets: B-B-R 
--------
Item Level: 85
--------
37% increased Spell Damage (implicit)
--------
Adds 60 to 103 Fire Damage
Adds 49 to 85 Cold Damage
Adds 9 to 164 Lightning Damage
38% increased Critical Strike Chance
+38% to Global Critical Strike Multiplier
12% increased Attack Speed (crafted)
--------
Mirrored''',

'''Show # %D3 $type->rare->any $tier->any
	HasInfluence None
	Rarity <= Rare
	SetFontSize 45
	SetTextColor 255 255 255 255
	SetBorderColor 255 255 255 255
	SetBackgroundColor 50 130 165
	PlayEffect Blue Temp''',
    
True),
]

def TestRuleMatchesItem():
    for item_text, rule_text, expected_match_flag in kTestCases:
        # print(kHorizontalSeparator)
        # print()
        # print(item_text)
        # print(kHorizontalSeparatorThin)
        # print(rule_text)
        # print()
        item = Item(item_text)
        rule = LootFilterRule(rule_text)
        match_flag = RuleMatchesItem(rule, item)
        # print('match_flag = {}'.format(match_flag))
        # input()
        AssertEqual(expected_match_flag, match_flag)
    print('TestRuleMatchesItem passed!')

# Missing features and issues with rule-item matching:
#  - Magic items do not have their BaseType parsed (need BaseType list for this)
#  - Rules about Sockets only match the number, not the color (number of links work)
#  - All conditions in loot_filter_rule.kIgnoredRuleConditionKeywords are ignored
def TestGetRuleMatchingItem():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    test_cases = ParseTestCases(test_consts.kItemTestCasesInputFullpath)
    for item_text, _, matching_rule_lines in test_cases:
        item = Item(item_text)
        matched_rule = loot_filter.GetRuleMatchingItem(item)
        expected_matched_rule = LootFilterRule(matching_rule_lines)
        # Check that the matched rule matches expected rule by checking tags are equal
        AssertEqual((matched_rule.type_tag, matched_rule.tier_tag),
                (expected_matched_rule.type_tag, expected_matched_rule.tier_tag))
    print('TestGetRuleMatchingItem passed!')

def main():
    TestRuleMatchesItem()
    TestGetRuleMatchingItem()
    test_helper.TearDown()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()