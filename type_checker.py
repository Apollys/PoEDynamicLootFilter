import logger
        
# Logs error and raises exception if variable is not an instance of required type
# Note: can use a tuple of types for required_type to give multiple options
def CheckType(variable, variable_name: str, required_type, required_inner_type=None):
    if (required_inner_type != None):
        CheckType2(variable, variable_name, required_type, required_inner_type)
    elif (not isinstance(variable, required_type)):
        required_type_name = (' or '.join(t.__name__ for t in required_type)
                              if isinstance(required_type, tuple)
                              else required_type.__name__)
        error_message: str = '{} has type: {}; required type(s): {}'.format(
                variable_name, type(variable).__name__, required_type_name)
        logger.Log('TypeError: ' + error_message)
        raise TypeError(error_message)
# End CheckType()

# Handle compound types, for example to check if something is a list of strings, use:
#  - required_outer_type = list
#  - required_inner_type = string
# For efficiency, only checks the type of the first item, we don't want to add too much overhead
def CheckType2(variable, variable_name: str, required_outer_type, required_inner_type):
    if (not isinstance(variable, required_outer_type)):
        required_type_name = (' or '.join(t.__name__ for t in required_outer_type)
                              if isinstance(required_outer_type, tuple)
                              else required_outer_type.__name__)
        error_message: str = '{} has type: {}; required type(s): {}'.format(
                variable_name, type(variable).__name__, required_type_name)
        logger.Log('TypeError: ' + error_message)
        raise TypeError(error_message)
    else:
        if (len(variable) == 0):
            return
        try:
            inner_value = next(iter(variable))
        except:
            error_message: str = '{} has type: {}; which is not an iterable type'.format(
                    variable_name, type(variable))
            logger.Log('TypeError: ' + error_message)
            raise TypeError(error_message)
        else:
            if (not isinstance(inner_value, required_inner_type)):
                required_type_name = (' or '.join(t.__name__ for t in required_inner_type)
                                      if isinstance(required_inner_type, tuple)
                                      else required_inner_type.__name__)
                error_message: str = '{} has inner type: {}; required inner type(s): {}'.format(
                        variable_name, type(inner_value).__name__, required_type_name)
                logger.Log('TypeError: ' + error_message)
                raise TypeError(error_message)
# End CheckType()

