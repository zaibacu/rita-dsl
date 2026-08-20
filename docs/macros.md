# Macros

`ARG = Literal | Macro | Variable`

`ARGS = Array of ARG`

| Name    | Arguments            | Modifiers | Description                                 |
|---------|----------------------|-----------|---------------------------------------------|
| ANY     |`None`                |`?` `*` `+`|Placeholder for any kind of text             |
| WORD    |`ARG`(Optional)       |`?` `*` `+`|Placeholder for any kind of word             |
| NUM     |`ARG`(Optional)       |`?` `*` `+`|Placeholder for any kind of number           |
| PUNCT   |`None`                |`?` `*` `+`|Placeholder for punctuation                  |
| POS     |`ARG`                 |`?` `*` `+`|Match by PartOfSpeech                        |
| LEMMA   |`ARG`                 |`?` `*` `+`|Match by Lemma                               |
| ENTITY  |`ARG`                 |`?` `*` `+`|Match by Entity Type, eg. `PERSON`           |
| PATTERN |`ARGS`                |`None`     |Wrapper for multiple of rules. **Covered by standard syntax, can be ignored**                |
| IN_LIST |`ARGS`                |`?` `*` `+`|Match by any of defined values               |
| PREFIX  |`ARGS`                |`None`     |Adds a prefix to next word or list           |
| LOAD    |`ARG`                 |`None`     |Load array from file. Each line = new element|
| MARK    |`ARG`                 |`None`     |Mark given pattern as a label                |
| ASSIGN  |`Literal`, `ARG`      |`None`     |Assign value to variable. **Covered by standard syntax, can be ignored**                     |
| EXEC  |`ARG`                   |`None`     |Execute macro. **Covered by standard syntax, can be ignored**                     |
| ANCHOR  |`Macro`               |`None`     |Required context token, excluded from the match result. See below|
| IMPORT  |`Literal`             |`None`     |Import custom module, allowing custom macros to be executed|
| CONFIG | `Literal`, `LITERAL`  |`None`     |Alows to modify config value                 |

## ANCHOR

An anchor token is a token the rule *depends on*, but which is **not included
in the match result**. Its position in the pattern decides its role: anchors
at the start of a pattern are required context *before* the match, anchors at
the end are required context *after* it.

```
{ANCHOR(WORD("price")), NUM}->MARK("VALUE")
```

`&` is a shortcut for `ANCHOR(...)` - the rule above can also be written as:

```
{&WORD("price"), NUM}->MARK("VALUE")
```

Given `"the price 42 is fine"`, this matches only when `price` precedes the
number, but the reported result is just `42`.

```
currencies = {"eur", "usd"}
{NUM, ANCHOR(IN_LIST(currencies))}->MARK("AMOUNT")
```

Given `"it costs 42 eur"`, the result is `42`; `"42 bananas"` does not match.

Anchors can wrap any regular token macro (`WORD`, `IN_LIST`, `NUM`, `REGEX`, ...)
and can carry the usual modifiers, eg. `ANCHOR(WORD("price")?)` or
`&WORD("price")?` for optional context.

Rules:

- Anchors are only allowed at the start and/or the end of a pattern -
  the match result must stay contiguous
- A rule cannot consist of anchors only
- `ANCHOR` cannot wrap `PATTERN`
- Supported by the `standalone` and `rust` engines; the `spacy` engine
  rejects rules with anchors (spaCy entity spans cannot exclude context tokens)
