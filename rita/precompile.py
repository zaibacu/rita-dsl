import re
import logging

from functools import partial


logger = logging.getLogger(__name__)


MAX_DEPTH = 5


def handle_import(m, depth=0):
    path = m.group("path")
    logger.debug("Importing: {}".format(path))
    with open(path, "r") as f:
        return precompile(f.read(), depth+1)


def precompile(raw, depth=0):
    if depth > MAX_DEPTH:
        raise RuntimeError(
            "Maximum depth limit has been reached. "
            "Please check if you don't have cyclical imports"
        )

    raw = re.sub(
        r"@import\s+[\"'](?P<path>(\w|[/\-.])+)[\"']",
        partial(handle_import, depth=depth),
        raw
    )
    return raw
