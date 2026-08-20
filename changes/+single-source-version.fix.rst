Package version is now defined once, in ``rita.__version__`` (a plain string), and extracted at build time via hatchling's dynamic version - previously ``pyproject.toml`` and ``rita/__init__.py`` each carried their own copy which could disagree.

The unused ``VERSION_PATCH`` environment variable suffix (which only ever affected the runtime string, never the built package metadata) was removed, and ``__version__`` changed from a tuple to the conventional string form.
