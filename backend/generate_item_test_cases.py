from typing import List

import file_helper
from item import Item
from loot_filter import InputFilterSource, LootFilter
import test_consts
import test_helper

# Returns a list of strings, each of which is the item text for an item.
def ParseSampleItemsTxt(input_filepath: str) -> List[str]:
    item_text_strings = []
    current_item_text_lines = []
    for line in file_helper.ReadFile(input_filepath, strip=True):
        if (line == ''):
            continue
        if (line.startswith(test_consts.kHorizontalSeparator[:8])):
            if (len(current_item_text_lines) > 0):
                item_text_strings.append('\n'.join(current_item_text_lines))
            current_item_text_lines = []
        else:
            current_item_text_lines.append(line)
    return item_text_strings
# End ParseSampleItemsTxt

def main():
    test_helper.SetUp()
    loot_filter = LootFilter(test_consts.kTestProfileName, InputFilterSource.kDownload)
    item_text_strings = ParseSampleItemsTxt(test_consts.kTestItemsFullpath)
    with open(test_consts.kItemTestCasesGeneratedFullpath, 'w') as output_file:
        output_file.write(test_consts.kHorizontalSeparator)
        for item_text in item_text_strings:
            # Write item text
            output_file.write('\n\n' + item_text)
            output_file.write('\n\n' + test_consts.kHorizontalSeparatorThin + '\n\n')
            # Write item properties in sorted order for visual inspection and diff checking
            item = Item(item_text)
            for k, v in sorted(item.properties_map.items()):
                output_file.write('{} | {}\n'.format(k, v))
            output_file.write('\n' + test_consts.kHorizontalSeparatorThin + '\n\n')
            # Write matched rule text lines
            matched_rule = loot_filter.GetRuleMatchingItem(item)
            output_file.write('\n'.join(matched_rule.rule_text_lines))
            output_file.write('\n\n' + test_consts.kHorizontalSeparator)
    test_helper.TearDown()
# End main

'''
Manual review of results:
 - Super weird edge case if cannot use item. See Phoenix Song.
 - Weird edge case for StackSize > 999: "Stack Size: 1,112/300"
 - Issue with magic item BaseType parsing (known bug, need full BaseType list).
'''

if (__name__ == '__main__'):
    main()