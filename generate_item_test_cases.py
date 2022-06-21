import os.path
from typing import List

import file_helper
from item import Item
from item_test import kHorizontalSeparator, kHorizontalSeparatorThin
import test_consts

kTestItemsFilename = 'test_items.txt'
kTestItemsFullpath = os.path.join(test_consts.kTestResourcesDirectory, kTestItemsFilename)

kGeneratedTestCasesFilename = 'item_test_cases_generated.txt'
kGeneratedTestCasesFullpath = os.path.join(test_consts.kTestResourcesDirectory, kGeneratedTestCasesFilename)

# Returns a list of strings, each of which is the item text for an item.
def ParseSampleItemsTxt(input_filepath: str) -> List[str]:
    item_text_strings = []
    current_item_text_lines = []
    for line in file_helper.ReadFile(input_filepath, strip=True):
        if (line == ''):
            continue
        if (line.startswith(kHorizontalSeparator[:8])):
            if (len(current_item_text_lines) > 0):
                item_text_strings.append('\n'.join(current_item_text_lines))
            current_item_text_lines = []
        else:
            current_item_text_lines.append(line)
    return item_text_strings
# End ParseSampleItemsTxt

def main():
    item_text_strings = ParseSampleItemsTxt(kTestItemsFullpath)
    with open(kGeneratedTestCasesFullpath, 'w') as output_file:
        output_file.write(kHorizontalSeparator)
        for item_text in item_text_strings:
            output_file.write('\n\n' + item_text)
            output_file.write('\n\n' + kHorizontalSeparatorThin + '\n\n')
            item = Item(item_text)
            for k, v in item.properties_map.items():
                output_file.write('[{}], [{}]\n'.format(k, v))
            output_file.write('\n' + kHorizontalSeparator)
# End main

'''
Manual review of results:
 - Super weird edge case if cannot use item. See Phoenix Song.
 - Weird edge case for StackSize > 999: "Stack Size: 1,112/300"
'''

if (__name__ == '__main__'):
    main()