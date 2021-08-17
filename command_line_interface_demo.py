'''
We will use command line arguments to allow the AHK frontend to delegate
tasks to the python backend.  The basic formatting can be something like:

 > python3 dynamic_loot_filter.py <task_type> <task_parameters>
 
For example, to change the tier of  Blessed Orb from tier 5 to tier 7, we
could use the following command:

 > python3 dynamic_loot_filter.py change_currency_tier "Blessed Orb" 5 7

Note the quotation marks allow parameters with spaces to be interpreted
as a single parameter.  Without quotation marks, spaces split parameters.

Try running this script with the following command to see the results:

 > python3 command_line_interface_demo.py change_currency_tier "Blessed Orb" 5 7
 command_line_interface_demo.py
 change_currency_tier
 Blessed Orb
 5
 7

'''

import sys

def main():
    for arg in sys.argv:
        print(arg)
        
main()
