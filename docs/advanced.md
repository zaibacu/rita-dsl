# Importing other rule files

When the corpus of rules becomes too large, it is possible to split it into multiple of files.
It can be done simply like this:

```
@import "<file path>"
```

Eg.:
```
@import "examples/simple-match.rita"
```

# Reusing patterns

You can define (since version 0.5.0+) pattern as a variable:

```
ComplexNumber = {NUM+, WORD("/")?, NUM?}

{PATTERN(ComplexNumber), WORD("inches"), WORD("Height")}->MARK("HEIGHT")
{PATTERN(ComplexNumber), WORD("inches"), WORD("Width")}->MARK("WIDTH")
```