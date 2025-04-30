import platform
import inspect
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style, init
init(autoreset=True)

DEVICE_NAME = platform.node()
DEVICE_ALIAS = (
    "PC" if DEVICE_NAME == "GeForce-Watertoren" else
    "Raspberry" if DEVICE_NAME == "MrsRainbow" else
    DEVICE_NAME
)

TAGS = {
    "Agent": Fore.CYAN,
    "Ultrasonic": Fore.GREEN,
    "SoundEmitter": Fore.BLUE,
    "GCC": Fore.GREEN,
    "Vibes": Fore.MAGENTA,
    "VibeListener": Fore.YELLOW,
    "Launcher": Fore.BLACK,
    "ERROR": Fore.RED,
    "PC": Fore.LIGHTCYAN_EX,
    "Raspberry": Fore.LIGHTMAGENTA_EX,
}

def _format_tag(tag):
    tag_color = TAGS.get(tag, Fore.WHITE)
    padded = tag.ljust(20)
    return f"{tag_color}[{tag}]{' ' * (20 - len(tag))}{Style.RESET_ALL}"

def _timestamp():
    return datetime.now().strftime("%H:%M:%S")

def _split_message(message, max_length):
    words = message.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 > max_length:
            lines.append(current.strip())
            current = word + " "
        else:
            current += word + " "
    if current.strip():
        lines.append(current.strip())
    return lines

def log(tag, message):
    prefix = f"{_timestamp()} {_format_tag(tag)} "
    lines = _split_message(message, 100)
    for i, line in enumerate(lines):
        if i == 0:
            print(f"{prefix}{line}")
        else:
            print(f"{' ' * len(prefix)}{line}")

def log_error(tag, message):
    prefix = f"{_timestamp()} {Fore.RED}{_format_tag(tag)} ERROR:{Style.RESET_ALL} "
    lines = _split_message(message, 100)
    for i, line in enumerate(lines):
        if i == 0:
            print(f"{prefix}{line}")
        else:
            print(f"{' ' * len(prefix)}{line}")
