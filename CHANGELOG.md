0.7.0 (2021-02-02)
****************************

Features
--------

- `standalone` engine now will return submatches list containing start and end for each part of match
  #93
- Partially covered https://github.com/zaibacu/rita-dsl/issues/70

  Allow nested patterns, like:

  .. code-block::

      num_with_fractions = {NUM, WORD("-")?, IN_LIST(fractions)}
      complex_number = {NUM|PATTERN(num_with_fractions)}

      {PATTERN(complex_number)}->MARK("NUMBER")
  #95
- Submatches for rita-rust engine
  #96
- Regex module which allows to specify word pattern, eg. `REGEX(^a)` means word must start with letter "a"

  Implemented by: Roland M. Mueller (https://github.com/rolandmueller)
  #101
- ORTH module which allows you to specify case sensitive entry while rest of the rules ignores case. Used for acronyms and proper names

  Implemented by: Roland M. Mueller (https://github.com/rolandmueller)
  #102
- Additional macro for `tag` module, allowing to tag specific word/list of words

  Implemented by: Roland M. Mueller (https://github.com/rolandmueller)
  #103
- Added `names` module which allows to generate person names variations
  #105
- spaCy v3 Support
  #109

Fix
---

- Optimizations for Rust Engine

  - No need for passing text forward and backward, we can calculate from text[start:end]

  - Grouping and sorting logic can be done in binary code
  #88
- Fix NUM parsing bug
  #90
- Switch from `(^\s)` to `\b` when doing `IN_LIST`. Should solve several corner cases
  #91
- Fix floating point number matching
  #92
- revert #91 changes. Keep old way for word boundary
  #94


0.6.0 (2020-08-29)
****************************

Features
--------

- Implemented ability to alias macros, eg.:

  .. code-block::

      numbers = {"one", "two", "three"}
      @alias IN_LIST IL

      IL(numbers) -> MARK("NUMBER")

  Now using "IL" will actually call "IN_LIST" macro.
  #66
- introduce the TAG element as a module. Needs a new parser for the SpaCy translate.
  Would allow more flexible matching of detailed part-of-speech tag, like all adjectives or nouns: TAG("^NN|^JJ").

  Implemented by:
  Roland M. Mueller (https://github.com/rolandmueller)
  #81
- Add a new module for a PLURALIZE tag
  For a noun or a list of nouns, it will match any singular or plural word.

  Implemented by:
  Roland M. Mueller (https://github.com/rolandmueller)
  #82
- Add a new Configuration implicit_hyphon (default false) for automatically adding hyphon characters - to the rules.

  Implemented by:
  Roland M. Mueller (https://github.com/rolandmueller)
  #84
- Allow to give custom regex impl. By default `re` is used
  #86
- An interface to be able to use rust engine.

  In general it's identical to `standalone`, but differs in one crucial part - all of the rules are compiled into actual binary code and that provides large performance boost.
  It is proprietary, because there are various caveats, engine itself is a bit more fragile and needs to be tinkered to be optimized to very specific case
  (eg. few long texts with many matches vs a lot short texts with few matches).
  #87

Fix
---

- Fix `-` bug when it is used as stand alone word
  #71
- Fix regex matching, when shortest word is selected from IN_LIST
  #72
- Fix IN_LIST regex so that it wouldn't take part of word
  #75
- Fix IN_LIST operation bug - it was ignoring them
  #77
- Use list branching only when using spaCy Engine
  #80


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


