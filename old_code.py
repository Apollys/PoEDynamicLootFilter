    # [DEPRECATED] It turns out the table of contents can't really be trusted to
    # match the loot filter exactly or contain all the sections the loot filter contains.   
    def ParseTableOfContents(self, loot_filter_lines: List[str]) -> None:
        '''
        Parse the Table of Contents, generating the following data:
         - # self.section_group_map: Dict[id: str, name: str]
         - self.section_map: OrderedDict[id: str, name: str]
         - self.inverse_section_map: Dict[name: str, id: str]
         - self.table_of_contents_end_line_index: int
        
        Notes:
         - Section names will have section group names prepended in brackets, e.g.:
           - "[High tier influenced items] Crusader"
           - This is so searching by keywords in section names will work better
         - Section groups are denoted by doube brackets, "[[Uniques]]", whereas sections
           are denoted by single bractes, "Tier 1 uniques", in the table of contents
        '''
        CheckType(loot_filter_lines, 'loot_filter_lines', list)
        # self.section_group_map: Dict[str, str] = {}  # maps ids to names
        self.section_map: OrderedDict[str, str] = {}  # maps ids to names
        self.inverse_section_map: Dict[str, str] = {}  # maps names to ids
        self.table_of_contents_end_line_index: int = 0
        # Regex patterns - double brackets for section groups, single brackets for sections
        section_group_re_pattern = re.compile(r'\[\[\d+\]\] .*')
        section_re_pattern = re.compile(r'\[\d+\] .*')
        found_start: bool = False
        done: bool = False
        current_section_group_prefix: str = ''
        for line_index in range(len(loot_filter_lines)):
            line: str = loot_filter_lines[line_index]
            section_group_re_search_result = section_group_re_pattern.search(line)
            section_re_search_result = section_re_pattern.search(line)
            if ('[WELCOME] TABLE OF CONTENTS' in line):
                found_start = True
            elif(not found_start):
                continue
            # Blank line indicates end of table of contents
            elif (line == ''):
                self.table_of_contents_end_line_index = line_index
                break
            elif (section_group_re_search_result):
                s: str = section_group_re_search_result.group()
                id_start_index = FindFirstMatchingPredicate(s, str.isdigit)
                id_end_index = s.find(']')
                name_start_index = id_end_index + 3
                id_ = s[id_start_index : id_end_index]  # id_ here because id is keyword
                name = s[name_start_index :]
                self.section_map[id_] = name
                self.inverse_section_map[name] = id_
                current_section_group_prefix = '[' + name + '] '
            elif (section_re_search_result):
                s: str = section_re_search_result.group()
                id_start_index = FindFirstMatchingPredicate(s, str.isdigit)
                id_end_index = s.find(']')
                name_start_index = id_end_index + 2
                id_ = s[id_start_index : id_end_index]  # id_ here because id is keyword
                name = current_section_group_prefix + s[name_start_index :]
                self.section_map[id_] = name
                self.inverse_section_map[name] = id_
    # End ParseTableOfContents()
