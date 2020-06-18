0.5.0 (2020-06-18)
****************************

Features
--------

- Added `PREFIX` macro which allows to attach word in front of list items or words
  #47
- Allow to pass variables directly when doing `compile` and `compile_string`
  #51
- Allow to compile (and later load) rules using rita CLI while using standalone engine (spacy is already supported)
  #53
- Added ability to import rule files into rule file. Recursive import is supported as well.
  #55
- Added possibility to define pattern as a variable and reuse it in other patterns:

  Example:
  .. code-block:: RITA

      ComplexNumber = {NUM+, WORD("/")?, NUM?}

      {PATTERN(ComplexNumber), WORD("inches"), WORD("Height")}->MARK("HEIGHT")

      {PATTERN(ComplexNumber), WORD("inches"), WORD("Width")}->MARK("WIDTH")
  #64

Fix
---

- Fix issue with multiple wildcard words using standalone engine
  #46
- Don't crash when no rules are provided
  #50
- Fix Number and ANY-OF parsing
  #59
- Allow escape characters inside LITERAL
  #62


0.4.0 (2020-01-25)
****************************

Features
--------

- Support for deaccent. In general, if accented version of word is given, both deaccented and accented will be used to match. To turn iit off - `!CONFIG("deaccent", "N")`
  #38
- Added shortcuts module to simplify injecting into spaCy
  #42

Fix
---

- Fix issue regarding Spacy rules with `IN_LIST` and using case-sensitive mode. It was creating Regex pattern which is not valid spacy pattern
  #40


0.3.2 (2019-12-19)
***********************

Features
--------

- - Introduced `towncrier` to track changes
  - Added linter `flake8`
  - Refactored code to match `pep8`
  #32

Fix
---

- - Fix WORD split by `-`

  - Split by ` ` (empty space) as well

  - Coverage score increase
  #35


