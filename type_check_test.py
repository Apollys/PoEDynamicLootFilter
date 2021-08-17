from typing import List

kLogFilename = 'test_debug_log.txt'
log_initialized = False

# === Helper Functions ===

# Used to log any errors, warnings, or debug information
# item can be a string or anything convertible to string
def Log(item):
    global log_initialized
    if (not log_initialized):
        open(kLogFilename, 'w').close()  # clear log file
        log_initialized = True
    message: str = item if isinstance(item, str) else str(item)
    with open(kLogFilename, 'a') as log_file:
        log_file.write(message + '\n')
# End Log()
        
# Logs error and raises exception if variable is not an instance of required type
# Note: can use a tuple of types for required_type to give multiple options
def CheckType(variable, variable_name: str, required_type):
    if not isinstance(variable, required_type):
        required_type_name = required_type.__name__ if type(required_type) == type else \
                ' or '.join(t.__name__ for t in required_type)
        error_message: str = '{} has type: {}; required type: {}'.format(
                variable_name, type(variable).__name__, required_type_name)
        Log('TypeError: ' + error_message)
        raise TypeError(error_message)
# End CheckType()

def main():
    x = [1, 2, 3]
    CheckType(x, 'x', (str, int))
    
main()
