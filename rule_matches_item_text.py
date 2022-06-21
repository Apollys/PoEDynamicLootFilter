from item import Item, RuleMatchesItem
from loot_filter_rule import LootFilterRule

from test_helper import AssertEqual, AssertTrue, AssertFalse

kHorizontalSeparator = \
        '================================================================================'
kHorizontalSeparatorThin = \
        '~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~'

kItemTextLargeStackChaos = \
'''Item Class: Stackable Currency
Rarity: Currency
Chaos Orb
--------
Stack Size: 7/10
--------
Reforges a rare item with new random modifiers
--------
Right click this item then left click a rare item to apply it.
Shift click to unstack.'''

kRuleTextLargeStackChaos = \
'''Show # $type->currency->stackedsix $tier->t2
StackSize >= 6
Class "Currency"
BaseType == "Ancient Orb" "Awakened Sextant" "Burial Medallion" "Chaos Orb" "Exalted Shard" "Exceptional Eldritch Ember" "Exotic Coinage" "Fertile Catalyst" "Grand Eldritch Ichor" "Orb of Annulment" "Prismatic Catalyst" "Tainted Blessing" "Tainted Chromatic Orb" "Tainted Orb of Fusing" "Unstable Catalyst" "Veiled Chaos Orb"
SetFontSize 45
SetTextColor 255 255 255 255
SetBorderColor 255 255 255 255
SetBackgroundColor 130 214 255 255
PlayAlertSound 1 300
PlayEffect Red
MinimapIcon 0 Red Circle'''

def TestRuleMatchesItem():
    item = Item(kItemTextLargeStackChaos)
    rule = LootFilterRule(kRuleTextLargeStackChaos)
    match_flag = RuleMatchesItem(rule, item)
    print(match_flag)
    print('TestRuleMatchesItem passed!')

def main():
    TestParseItemText()
    TestRuleMatchesItem()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()