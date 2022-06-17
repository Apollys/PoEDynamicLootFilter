from loot_filter_rule import RuleVisibility, LootFilterRule
from test_helper import AssertEqual, AssertTrue, AssertFalse

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
    rule = LootFilterRule(kInputRuleText)
    rule.RemoveBaseType('Splinter of Chayula')
    rule.RemoveBaseType('Splinter of Uul-Netol')
    rule.RemoveBaseType('Timeless Maraketh Splinter')
    rule.RemoveBaseType('Timeless Templar Splinter')
    AssertTrue(RuleVisibility.IsDisabled(rule.visibility))
    AssertTrue(all(line.strip().startswith('#') for line in rule.rule_text_lines))
    print('TestRemoveAllBaseTypes passed!')

def TestChangeVisibility():
    rule = LootFilterRule(kInputRuleText)
    rule.Hide()
    AssertEqual(rule.visibility, RuleVisibility.kHide)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Hide'))
    rule.Show()
    AssertEqual(rule.visibility, RuleVisibility.kShow)
    AssertTrue(rule.rule_text_lines[0].strip().startswith('Show'))
    rule.Hide()
    rule.Disable()
    AssertEqual(rule.visibility, RuleVisibility.kDisabledHide)
    AssertTrue(all(line.strip().startswith('#') for line in rule.rule_text_lines))
    AssertEqual('Hide' in rule.rule_text_lines[0], True)
    rule.Enable()
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

def main():
    TestAddRemoveBaseTypes()
    TestRemoveAllBaseTypes()
    TestChangeVisibility()
    TestChangeTags()
    TestModifyLine()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()