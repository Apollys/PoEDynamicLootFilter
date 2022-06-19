import simple_parser
from test_helper import AssertEqual, AssertTrue, AssertFalse

def TestParseFromTemplate():
    # Very simple parse: single item
    text = 'hello'
    template = '{}'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertTrue(success)
    AssertEqual(result, ['hello'])
    # Very simple parse: single item enclosed by other characters
    text = '[(quick brown fox)]'
    template = '[({})]'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertTrue(success)
    AssertEqual(result, ['quick brown fox'])
    # Multi item parse
    text = 'One (two three four) five'
    template = '{}({}){}'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertTrue(success)
    AssertEqual(result, ['One ', 'two three four', ' five'])
    # Mismatch test - text missing item
    text = '123.456.789'
    template = '{}.{}.{}.'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertFalse(success)
    # Mismatch test - text with extra item
    text = '123.456.789'
    template = '{}.{}.'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertFalse(success)
    # Multi item parse with ignored portions
    text = 'The quick (brown fox, jumps, over the) lazy dog'
    template = '{~}({},{~},{}){~}'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertTrue(success)
    AssertEqual(result, ['brown fox', ' over the'])
    # Match wildcard can match empty string
    text = ''
    template = '{}'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertTrue(success)
    AssertEqual(result, [''])
    # Ignore wildcard can match empty string
    text = '-Word-'
    template = '{~}-{}-{~}'
    success, result = simple_parser.ParseFromTemplate(text, template)
    AssertTrue(success)
    AssertEqual(result, ['Word'])
    # Rule tag parse
    type_tag = 'decorator->craftingrare'
    tier_tag = 'raredecoratorgear'
    text = 'Show # $type->{} $tier->{}'.format(type_tag, tier_tag)
    template = 'Show {~}$type->{} $tier->{} {~}'
    success, result = simple_parser.ParseFromTemplate(text + ' ', template)
    AssertTrue(success)
    AssertEqual(result, [type_tag, tier_tag])
    text = 'Show # $type->{} $tier->{} $other_tag other text'.format(type_tag, tier_tag)
    template = 'Show {~}$type->{} $tier->{} {~}'
    success, result = simple_parser.ParseFromTemplate(text + ' ', template)
    AssertTrue(success)
    AssertEqual(result, [type_tag, tier_tag])
    print('TestParseFromTemplate passed!')
# End TestParseFromTemplate
    
def TestParseEnclosedBy():
    # Basic case
    text = 'BaseType "Leather Belt" "Two-Stone Ring" "Agate Amulet"'
    result = simple_parser.ParseEnclosedBy(text, '"')
    AssertEqual(result, ['Leather Belt', 'Two-Stone Ring', 'Agate Amulet'])
    # Last item missing closing sequence
    text = 'The "quick" "brown fox" jumps over the "lazy dog '
    result = simple_parser.ParseEnclosedBy(text, '"', '"')
    AssertEqual(result, ['quick', 'brown fox'])
    # Multi-character enclosing sequence
    text = 'Hello ((beautiful)) universe'
    result = simple_parser.ParseEnclosedBy(text, '((', '))')
    AssertEqual(result, ['beautiful'])
    # Re-encounter opening sequence before closing sequence
    text = 'One [(two)] three [(four )[(five)]'
    result = simple_parser.ParseEnclosedBy(text, '[(', ')]')
    AssertEqual(result, ['two', 'four )[(five'])
    print('TestParseEnclosedBy passed!')
# End TestParseEnclosedBy

def TestIsInt():
    AssertTrue(simple_parser.IsInt('-5'))
    AssertFalse(simple_parser.IsInt('1.2'))
    AssertFalse(simple_parser.IsInt('314 days'))
    print('TestIsInt passed!')
# End TestIsInt

def TestParseInts():
    text = 'asdf45 re2 7432'
    result = simple_parser.ParseInts(text)
    AssertEqual(result, [45, 2, 7432])
# End TestParseInts

def main():
    TestParseFromTemplate()
    TestParseEnclosedBy()
    TestIsInt()
    TestParseInts()
    print('All tests passed!')

if (__name__ == '__main__'):
    main()