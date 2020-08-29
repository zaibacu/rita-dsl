# Engines

In RITA what we call `engine` is a system we will compile rules to, and which will do the heavy lifting after that.

Currently there are three engines:

## spaCy

Activated by using `rita.compile(<rules_file>, use_engine="spacy")`

Using this engine, all of the RITA rules will be compiled into spaCy patterns, which can be natively used by spaCy in various scenarios.
Most often - to improve NER (Named Entity Recognition), by adding additional entities derived from your given rules

It requires to have spaCy package installed (`pip install spacy`) and to actually use it later, language model needs to be downloaded (`python -m spacy download <language_code>`)

## Standalone

Activated by using `rita.compile(<rules_file>, use_engine="standalone")`. It compiles into pure regex and can be used with zero dependencies.
By default, it uses Python `re` library. Since `0.5.10` version, you can give a custom regex implementation to use:
eg. regex package: `rita.compile(<rules_file>, use_engine="standalone", regex_impl=regex)`

It is very lightweight, very fast (compared to spaCy), however lacking in some functionality which only proper language model can bring:
- Patterns by entity (PERSON, ORGANIZATION, etc)
- Patterns by Lemmas
- Patterns by POS (Part Of Speech)

Only generic things, like WORD, NUMBER can be matched.


## Rust (new in `0.6.0`)

There's only an interface inside the code, engine itself is proprietary. 

In general it's identical to `standalone`, but differs in one crucial part - all of the rules are compiled into actual binary code and that provides large performance boost.
It is proprietary, because there are various caveats, engine itself is a bit more fragile and needs to be tinkered to be optimized to very specific case
(eg. few long texts with many matches vs a lot short texts with few matches).