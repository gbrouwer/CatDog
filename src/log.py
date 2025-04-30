
import platform
import inspect
from datetime import datetime
from colorama import Fore, Style, init
init(autoreset=True)

DEVICE_NAME = platform.node()

TAGS = {
    "Agent": Fore.CYAN,
    "Ultrasonic": Fore.GREEN,
    "SoundEmitter": Fore.MAGENTA,
    "GCC": Fore.BLUE,
    "Vibes": Fore.YELLOW,
    "ERROR": Fore.RED,
}

def _format_tag(tag):
    return f"{tag} on {DEVICE_NAME}" if tag else f"Unknown on {DEVICE_NAME}"

def _get_caller():
    stack = inspect.stack()
    if len(stack) >= 3:
        filename = stack[2].filename
        return Path(filename).stem
    return "UnknownScript"

def _timestamp():
    return datetime.now().strftime("%H:%M:%S")

def log(tag, message):
    color = TAGS.get(tag, Fore.WHITE)
    caller = _get_caller()
    print(f"{_timestamp()} {color}[{_format_tag(tag):<30}] ({caller}){Style.RESET_ALL} {message}")

def log_error(tag, message):
    caller = _get_caller()
    print(f"{_timestamp()} {Fore.RED}[{_format_tag(tag):<30}] ({caller}) ERROR:{Style.RESET_ALL} {message}")
