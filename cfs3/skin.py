import logging
import sys

# Try to find the best available styling method
_style_func = None

try:
    from cmd2 import Fg, ansi  # type: ignore
    def _style_old_cmd2(string, col):
        """ Colour a string with old cmd2 API """
        return ansi.style(string, fg=Fg[col.upper()])
    _style_func = _style_old_cmd2
except ImportError:
    # Newer cmd2 versions use different API
    try:
        from cmd2 import ansi  # type: ignore
        def _style_intermediate_cmd2(string, col):
            """ Colour a string with intermediate cmd2 API """
            return ansi.style(string, fg=col.lower())
        _style_func = _style_intermediate_cmd2
    except (ImportError, AttributeError):
        # cmd2 3.1.0+ - use ANSI codes directly
        try:
            if sys.stdout and hasattr(sys.stdout, 'isatty') and sys.stdout.isatty():
                # Terminal supports colors, use ANSI codes
                ANSI_COLORS = {
                    'green': '\033[92m',
                    'blue': '\033[94m',
                    'magenta': '\033[95m',
                    'red': '\033[91m',
                    'cyan': '\033[96m',
                    'reset': '\033[0m'
                }
                def _style_ansi_codes(string, col):
                    """ Colour a string using ANSI codes """
                    color_code = ANSI_COLORS.get(col.lower(), '')
                    if color_code:
                        return f"{color_code}{string}\033[0m"
                    return string
                _style_func = _style_ansi_codes
            else:
                # No terminal support, fallback to plain string
                def _style_plain(string, col):
                    """ Plain text, no coloring """
                    return string
                _style_func = _style_plain
        except Exception:
            # Final fallback if anything else fails
            def _style_fallback(string, col):
                """ Final fallback """
                return string
            _style_func = _style_fallback

# Double-check _style_func is set (should always be true)
if _style_func is None:
    def _style_none_fallback(string, col):
        """ Fallback if all else fails """
        return string
    _style_func = _style_none_fallback

def __style(string, col):
    """ Wrapper function that delegates to the appropriate style function """
    if _style_func is not None:
        return _style_func(string, col)
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