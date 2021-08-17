class Rule:
    def __init__(self, text):
        self.text = text
    
    def Disable(self):
        self.text = '#' + self.text
        
    def __repr__(self):
        return self.text
        
def main():
    ex_rule = Rule('Show Exalted Orb')
    rules_list = []
    rules_map_type = {}
    rules_map_tier = {}
    # ...
    rules_map_type['currency'] = ex_rule
    rules_map_tier['t1'] = ex_rule
    # ...
    found_rule = rules_map_tier['t1']
    found_rule.Disable()
    print(rules_map_type['currency'])
    
main()
