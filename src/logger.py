""" Main logger module.
Initialise a logger object which can be imported and called from all modules.
The module initialise the logging level by reading the project config file. It also conveniently silence other imported
libraries loggers.

You can use the logger in your modules like this :
```python
from logger import logger
```
"""

import configparser
import logging
import os

from pathlib import Path

from common import parse_path

# Read config file
config = configparser.ConfigParser()
config.read(Path(__file__).parent.parent / "config.ini")

# Initialize logger
logger = logging.getLogger("Skyblog-Archiving")

# Set logging level
level = config["logging"]["level"].lower()
if level == "debug":
    level = logging.DEBUG
elif level == "info":
    level = logging.INFO
elif level == "warning":
    level = logging.WARNING
elif level == "error":
    level = logging.ERROR
elif level == "critical":
    level = logging.CRITICAL
else:
    raise ValueError(f'Unknown logging level "{level}".')
logger.setLevel(level=level)

# Set up the logging file
path_file_log = parse_path(config["logging"]["path_file_log"])
if os.path.dirname(path_file_log):
    os.makedirs(os.path.dirname(path_file_log), exist_ok=True)
format_logging = logging.Formatter(
    "%(asctime)s::%(name)s::[%(levelname)s]::%(message)s"
)

# Set up handlers
## File handler
handler_file = logging.FileHandler(filename=path_file_log, mode="w")
handler_file.setLevel(logging.DEBUG)
handler_file.setFormatter(format_logging)
logger.addHandler(hdlr=handler_file)

# Console handler
handler_console = logging.StreamHandler()
handler_console.setLevel(logging.DEBUG)
handler_console.setFormatter(format_logging)
logger.addHandler(hdlr=handler_console)
