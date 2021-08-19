import logger
        
# Logs error and raises exception if variable is not an instance of required type
# Note: can use a tuple of types for required_type to give multiple options
def CheckType(variable, variable_name: str, required_type):
    if not isinstance(variable, required_type):
        required_type_name = (' or '.join(t.__name__ for t in required_type)
                              if isinstance(required_type, tuple)
                              else required_type.__name__)
        error_message: str = '{} has type: {}; required type(s): {}'.format(
                variable_name, type(variable).__name__, required_type_name)
        logger.Log('TypeError: ' + error_message)
        raise TypeError(error_message)
# End CheckType()
