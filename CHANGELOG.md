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


