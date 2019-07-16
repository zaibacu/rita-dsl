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
| LOAD    |`ARG`                 |`None`     |Load array from file. Each line = new element|
| MARK    |`ARG`                 |`None`     |Mark given pattern as a label                |
| ASSIGN  |`Literal`, `ARG`      |`None`     |Assign value to variable. **Covered by standard syntax, can be ignored**                     |
| EXEC  |`ARG`                   |`None`     |Execute macro. **Covered by standard syntax, can be ignored**                     |
| IMPORT  |`Literal`             |`None`     |Import custom module, allowing custom macros to be executed|
