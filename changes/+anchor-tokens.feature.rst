New ``ANCHOR`` macro - anchor tokens: required context the rule depends on, excluded from the match result.

.. code-block::

    {ANCHOR(WORD("price")), NUM}->MARK("VALUE")

matches ``"price 42"`` but reports just ``42``. Position decides the role: anchors at the start of a pattern are context before the match, anchors at the end are context after it. ``&`` works as a shortcut: ``{&WORD("price"), NUM}`` is equivalent. Supported by the standalone and rust engines.
