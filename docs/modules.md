# Modules

Modules are like plugins to the system, usually providing additional functionality at some cost - needs additional dependencies, supports only specific language etc.
That's why they are not included into the core system, but can be easily included into your rules.

eg.
```
!IMPORT("rita.modules.fuzzy")

FUZZY("squirrel") -> MARK("CRITTER")
```

**NOTE**: the import path can be any proper Python import. So this actually allows you to add extra functionality by not modifying RITA's source code.
More on that in [Extending section](./extend.md)

## Fuzzy

This is more as an example rather than proper module. The main goal is to generate possible misspelled variants of given word, so that match matches more cases. 
Very useful when dealing with actual natural language, eg. comments, social media posts. Word `you` can be automatically matched by proper `you` and `u`, `for` as `for` and `4` etc.

Usage:
```
!IMPORT("rita.modules.fuzzy")

FUZZY("squirrel") -> MARK("CRITTER")
```

## Pluralize

Takes list (or single) words, and creates plural version of each of these.

Requires: `inflect` library (`pip install inflect`) before using. Works only on english words.

Usage:

```
!IMPORT("rita.modules.pluralize")

vehicles={"car", "motorbike", "bicycle", "ship", "plane"}
{NUM, PLURALIZE(vehicles)}->MARK("VEHICLES")
```

## Tag

This module offers two new macros: `TAG` and `TAG_WORD`.


`TAG` is used for generating POS/TAG patterns based on a Regex
e.g. `TAG("^NN|^JJ")` for nouns or adjectives.

Works only with spaCy engine

Usage:

```
!IMPORT("rita.modules.tag")

{WORD*, TAG("^NN|^JJ")}->MARK("TAGGED_MATCH")
```

`TAG_WORD` is for generating TAG patterns with a word or a list.

e.g. match only "proposed" when it is in the sentence a verb (and not an adjective):

```
!IMPORT("rita.modules.tag")

TAG_WORD("^VB", "proposed")
```

or e.g. match a list of words only to verbs

```
!IMPORT("rita.modules.tag")

words = {"percived", "proposed"}
{TAG_WORD("^VB", words)?}->MARK("LABEL")
```