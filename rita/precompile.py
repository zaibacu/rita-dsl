import re
import logging


logger = logging.getLogger(__name__)


def handle_import(m):
    path = m.group("path")
    logger.debug("Importing: {}".format(path))
    with open(path, "r") as f:
        return f.read()


def precompile(raw):
    raw = re.sub(r"@import [\"'](?P<path>(\w|[/\-.])+)[\"']", handle_import, raw)
    return raw
