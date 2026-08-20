Standalone engine robustness overhaul:

- Regex metacharacters in ``WORD``, ``IN_LIST`` and phrase literals are now escaped, so values like ``C++`` or ``a.b`` match literally instead of being interpreted as regex
- Negation (``!``) on ``IN_LIST`` now works correctly (previously it required the listed words instead of rejecting them)
- Invalid rules and labels raise ``RuleCompileError`` at compile time instead of failing later during ``execute()`` with an obscure ``AttributeError``
- ``save()``/``load()`` round-trip now preserves the ``ignore_case`` setting via a config header line (old headerless files still load)
- Matching runs sequentially instead of via a thread pool: deterministic results, less overhead
- New ``match_timeout`` option (requires the third-party ``regex`` module as ``regex_impl``) guards against catastrophic backtracking
- Single-item lists are no longer exploded into individual characters
