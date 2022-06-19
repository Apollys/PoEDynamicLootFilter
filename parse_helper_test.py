import parse_helper

import consts
from test_helper import AssertEqual, AssertTrue, AssertFalse

kLinesWithTableOfContentsStart = \
'''# GITHUB:  NeverSinkDev

#===============================================================================================================
# [WELCOME] TABLE OF CONTENTS + QUICKJUMP TABLE
#===============================================================================================================
# [[0100]] OVERRIDE AREA 1 - Override ALL rules here
# [[0100]] Global overriding rules
# [[0200]] High tier influenced items'''

def TestIsSubstringInLines():
    AssertTrue(parse_helper.IsSubstringInLines(
            consts.kTableOfContentsIdentifier, kLinesWithTableOfContentsStart))
    text_lines = kLinesWithTableOfContentsStart.split('\n')
    AssertTrue(parse_helper.IsSubstringInLines(
            consts.kTableOfContentsIdentifier, text_lines))
    print('IsSubstringInLines passed!')

def main():
    TestIsSubstringInLines()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()