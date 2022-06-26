from loot_filter_rule import RuleVisibility, LootFilterRule
from test_assertions import AssertEqual, AssertTrue, AssertFalse

kCommentBlockText = \
'''#===============================================================================================================
# NeverSink's Indepth Loot Filter - for Path of Exile
#===============================================================================================================
# VERSION:  8.6.0
# TYPE:     1-REGULAR
# STYLE:    DEFAULT
# AUTHOR:   NeverSink
# BUILDNOTES: Filter generated with NeverSink's FilterpolishZ and the domainlanguage Exo.
# xShow'''

kInputRuleText = \
'''# Splinter stacks rule
# Let's add a second comment line for testing
Show # %HS4 $type->currency->stackedsplintershigh $tier->t3
StackSize >= 2
Class "Currency"
BaseType "Splinter of Chayula" "Splinter of Uul-Netol" "Timeless Maraketh Splinter" "Timeless Templar Splinter"
SetFontSize 45
SetTextColor 0 255 255 255
SetBorderColor 0 255 255 255
SetBackgroundColor 45 0 108 255
PlayEffect Purple
MinimapIcon 0 Purple Kite
PlayAlertSound 2 300'''

kCommentedRuleText = \
'''#Hide  # $type->jewels->clustereco $tier->n6_i75_t1
#	ItemLevel >= 75
#	Rarity <= Rare
#	EnchantmentPassiveNum 6
#	BaseType "Medium Cluster Jewel"
#	SetFontSize 45
#	SetTextColor 150 0 255 255
#	SetBorderColor 240 100 0 255
#	SetBackgroundColor 255 255 255 255
#	PlayEffect Red
#	MinimapIcon 0 Red Star
#PlayAlertSound 1 300'''

kEmptyBaseTypeRuleText = \
'''#Show  # %HS3 $type->currency->stackedthree $tier->t6
#       StackSize >= 3
#       Class "Currency"
#       SetFontSize 45
#       SetTextColor 30 200 200 255
#       SetBorderColor 30 200 200 255
#       SetBackgroundColor 0 0 69
#       MinimapIcon 2 Cyan Raindrop
#PlayAlertSound 2 300
#DisableDropSound True'''

kRepeatedKeywordRuleText = \
'''Show # $type->dlf_chaos_recipe_rares $tier->amulets
ItemLevel >= 60
ItemLevel < 75
Rarity Rare
Class "Amulets"
Identified False
SetBorderColor 0 255 255 255
SetBackgroundColor 120 20 20 80
SetFontSize 40
MinimapIcon 0 Cyan Moon'''

def TestIsParsableAsRule():
    AssertFalse(LootFilterRule.IsParsableAsRule(kCommentBlockText))
    AssertTrue(LootFilterRule.IsParsableAsRule(kInputRuleText))
    AssertTrue(LootFilterRule.IsParsableAsRule(kCommentedRuleText))
    print('TestIsParsableAsRule passed!')

def TestBasicRuleParse():
    rule = LootFilterRule(kInputRuleText)
    AssertEqual(rule.visibility, RuleVisibility.kShow)
    AssertEqual(rule.type_tag, 'currency->stackedsplintershigh')
    AssertEqual(rule.tier_tag, 't3')
    rule = LootFilterRule(kCommentedRuleText)
    AssertEqual(rule.visibility, RuleVisibility.kDisabledHide)
    AssertEqual(rule.type_tag, 'jewels->clustereco')
    AssertEqual(rule.tier_tag, 'n6_i75_t1')
    print('TestBasicRuleParse passed!')

def TestAddRemoveBaseTypes():
    rule = LootFilterRule(kInputRuleText)
    rule.AddBaseType('Simulacrum Splinter')
    rule.RemoveBaseType('Splinter of Uul-Netol')
    _, rule_base_type_list = rule.parsed_lines_hll['BaseType']
    rule_text = '\n'.join(rule.rule_text_lines)
    AssertTrue('Simulacrum Splinter' in rule_base_type_list)
    AssertTrue('Simulacrum Splinter' in rule_text)
    AssertFalse('Splinter of Uul-Netol' in rule_base_type_list)
    AssertFalse('Splinter of Uul-Netol' in rule_text)
    print('TestAddRemoveBaseTypes passed!')

def TestRemoveAllBaseTypes():
    # Remove individually
    rule = LootFilterRule(kInputRuleText)
    rule.RemoveBaseType('Splinter of Chayula')
    rule.RemoveBaseType('Splinter of Uul-Netol')
    rule.RemoveBaseType('Timeless Maraketh Splinter')
    rule.RemoveBaseType('Timeless Templar Splinter')
    AssertTrue(RuleVisibility.IsDisabled(rule.visibility))
    AssertTrue(all(line.strip().startswith('#') for line in rule.rule_text_lines))
    # Use ClearBaseTypeList
    rule = LootFilterRule(kInputRuleText)
    rule.ClearBaseTypeList()
    AssertTrue(RuleVisibility.IsDisabled(rule.visibility))
    AssertTrue(all(line.strip().startswith('#') for line in rule.rule_text_lines))
    print('TestRemoveAllBaseTypes passed!')

def TestChangeVisibility():
    rule = LootFilterRule(kInputRuleText)
    # Use Show/Hide/Disable funtions
    # Hide
    rule.Hide()
    AssertEqual(rule.visibility, RuleVisibility.kHide)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Hide'))
    # Show
    rule.Show()
    AssertEqual(rule.visibility, RuleVisibility.kShow)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Show'))
    # Hide then Disable
    rule.Hide()
    rule.Disable()
    AssertEqual(rule.visibility, RuleVisibility.kDisabledHide)
    AssertTrue(all(line.strip().startswith('#') for line in rule.rule_text_lines))
    AssertEqual('Hide' in rule.rule_text_lines[0], True)
    # Enable
    rule.Enable()
    AssertEqual(rule.visibility, RuleVisibility.kHide)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Hide'))
    # Use SetVisibility directly
    # RuleVisibility.kShow
    rule.SetVisibility(RuleVisibility.kShow)
    AssertEqual(rule.visibility, RuleVisibility.kShow)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Show'))
    # RuleVisibility.kDisabledAny
    rule.SetVisibility(RuleVisibility.kDisabledAny)
    AssertTrue(RuleVisibility.IsDisabled(rule.visibility))
    AssertTrue(all(line.strip().startswith('#') for line in rule.rule_text_lines))
    # RuleVisibility.kHide
    rule.SetVisibility(RuleVisibility.kHide)
    AssertEqual(rule.visibility, RuleVisibility.kHide)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Hide'))
    print('TestChangeVisibility passed!')
    
def TestChangeTags():
    rule = LootFilterRule(kInputRuleText)
    rule.SetTypeTierTags('hello', 'universe')
    AssertTrue(' $type->hello ' in rule.rule_text_lines[0])
    AssertTrue(' $tier->universe' in rule.rule_text_lines[0])
    print('TestChangeTags passed!')

def TestModifyLine():
    rule = LootFilterRule(kInputRuleText)
    rule.ModifyLine('MinimapIcon', '', ['0', 'Cyan', 'Moon'])
    rule_text = '\n'.join(rule.rule_text_lines)
    AssertTrue(rule.parsed_lines_hll['MinimapIcon'] == ('', ['0', 'Cyan', 'Moon']))
    AssertTrue('MinimapIcon 0 Cyan Moon' in rule_text)
    print('TestModifyLine passed!')

def TestEmptyBaseTypeList():
    rule = LootFilterRule(kEmptyBaseTypeRuleText)
    rule.ClearBaseTypeList()
    added_base_type = 'Orb of Alteration'
    rule.AddBaseType(added_base_type)
    AssertTrue(added_base_type in rule.GetBaseTypeList())
    AssertTrue(RuleVisibility.IsDisabled(rule.visibility))
    print('TestEmptyBaseTypeList passed!')

def TestRepeatedKeyword():
    rule = LootFilterRule(kRepeatedKeywordRuleText)
    print('TestRepeatedKeyword passed!')
    
def main():
    TestIsParsableAsRule()
    TestBasicRuleParse()
    TestAddRemoveBaseTypes()
    TestRemoveAllBaseTypes()
    TestChangeVisibility()
    TestChangeTags()
    TestModifyLine()
    TestEmptyBaseTypeList()
    TestRepeatedKeyword()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()