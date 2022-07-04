import os.path

from consts import kCacheDirectory

kDefaultLogFilename = os.path.join(kCacheDirectory, 'log.log')

g_log_filename = ''

def InitializeLog(log_filename: str = kDefaultLogFilename):
    global g_log_filename
    g_log_filename = log_filename
    open(g_log_filename, 'w').close()
# End InitializeLog()

# Used to log any errors, warnings, or debug information
# item can be a string or anything convertible to string
def Log(item):
    global g_log_filename
    if (g_log_filename == ''):
        InitializeLog(kDefaultLogFilename)
    message: str = item if isinstance(item, str) else str(item)
    with open(g_log_filename, 'a') as log_file:
        log_file.write(message + '\n\n')
# End Log()
