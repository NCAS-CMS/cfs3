import logging
import sys

# Direct ANSI color codes - works with cmd2 3.1.0+
ANSI_COLORS = {
    'green': '\033[92m',
    'blue': '\033[94m',
    'magenta': '\033[95m',
    'red': '\033[91m',
    'cyan': '\033[96m',
    'reset': '\033[0m'
}

def __style(string, col):
    """ Colour a string using ANSI codes """
    # Check if we're in a terminal that supports colors
    if sys.stdout and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
        color_code = ANSI_COLORS.get(col.lower(), '')
        if color_code:
            return f"{color_code}{string}\033[0m"
    return string

def _i(string, col='green'):
    """ Info string """
    return __style(string,col)
    
def _e(string, col='blue'):
    """ Entity string """
    return __style(string,col)

def _p(string, col='magenta'):
    """ Prompt String """
    return __style(string,col)

def _err(string,col='red'):
    return __style(string,col)

def _log(string,col='cyan'):
    return __style(string,col)

def fmt_size(num, suffix="B"):
    """ Take the sizes and humanize them """
    for unit in ("", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"):
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"

def fmt_date(adate):
    """ Take the reported date and humanize it"""
    return adate.strftime('%Y-%m-%d %H:%M:%S %Z')
    

class ColourFormatter(logging.Formatter):
    def format(self, record):
        message = super().format(record)
        if record.levelno >= logging.ERROR:
            return _err(message)
        else:
            return _log(message)