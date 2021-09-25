    def ParseLootFilterRules(self) -> None:
        '''
        This function parses the rules of the loot filter into the following data structures:
         - self.section_map: OrderedDict[id: str, name: str]
         - self.inverse_section_map: Dict[name: str, id: str]
         - self.rules_start_line_index: int
         - self.section_rule_map: OrderedDict[section_name: str, List[LootFilterRule]]
         - self.line_index_rule_map: OrderedDict[line_index: int, LootFilterRule]
         - self.rule_list: List[LootFilterRule]
         - self.type_tier_rule_map: 2d dict - (type_tag, tier_tag) maps to a unique LootFilterRule
           Note: parser ensures that (type_tag, tier_tag) forms a unique key for rules
           Example: self.type_tier_rule_map['currency']['t1'] 
        '''
        # Initialize data structures to store parsed data
        self.section_map: OrderedDict[str, str] = {}  # maps ids to names
        self.inverse_section_map: Dict[str, str] = {}  # maps names to ids
        self.section_rule_map: OrderedDict[str, List[LootFilterRule]] = OrderedDict()
        self.line_index_rule_map: OrderedDict[int, LootFilterRule] = OrderedDict()
        self.rule_list: List[LootFilterRule] = []
        self.type_tier_rule_map = {}
        # Set up parsing loop
        in_rule: bool = False
        current_rule_lines: List[str] = []
        current_section_id: str = ''
        current_section_group_prefix: str = ''
        untagged_rule_count: int = 0
        for line_index in range(self.rules_start_line_index, len(self.text_lines)):
            line: str = self.text_lines[line_index]
            if (not in_rule):
                # Case: encountered new section or section group
                if (helper.IsSectionOrGroupDeclaration(line)):
                    is_section_group, section_id, section_name = \
                            helper.ParseSectionDeclarationLine(line)
                    if (is_section_group):
                        current_section_group_prefix = '[' + section_name + '] '
                    else:
                        section_name = current_section_group_prefix + section_name
                    section_id = helper.MakeUniqueId(section_id, self.section_map)
                    self.section_map[section_id] = section_name
                    self.inverse_section_map[section_name] = section_id
                    self.section_rule_map[section_id] = []
                    current_section_id = section_id
                # Case: encountered new rule
                elif (helper.IsRuleStart(self.text_lines, line_index)):
                    in_rule = True
                    current_rule_lines.append(line)
            else:  # in_rule
                if (line == ''):  # end of rule
                    rule_start_line_index: int = line_index - len(current_rule_lines)
                    new_rule = LootFilterRule(current_rule_lines, rule_start_line_index)
                    # Add rule to section rule map
                    self.section_rule_map[current_section_id].append(new_rule)
                    # Add rules to line index rule map
                    self.line_index_rule_map[rule_start_line_index] = new_rule
                    # Generate unique type-tier tag pair if no tags
                    # (For now we assume it either has both or none)
                    if ((new_rule.type_tag == '') and (new_rule.tier_tag == '')):
                        new_rule.type_tag = 'untagged_rule'
                        new_rule.tier_tag = str(untagged_rule_count)
                        untagged_rule_count += 1
                        current_rule_lines[0] += ' # ' + consts.kTypeTierTagTemplate.format(
                                new_rule.type_tag, new_rule.tier_tag)
                    # Add rule to rule list
                    self.rule_list.append(new_rule)
                    # Add rule to type tier rule map
                    if (new_rule.type_tag not in self.type_tier_rule_map):
                        self.type_tier_rule_map[new_rule.type_tag] = {}
                    self.type_tier_rule_map[new_rule.type_tag][new_rule.tier_tag] = new_rule
                    in_rule = False
                    current_rule_lines = []
                else:
                    current_rule_lines.append(line)
    # End ParseLootFilterRules
