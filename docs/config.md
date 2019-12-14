# Config

Configuration is mostly applied per-rule-basis, meaning, that different rules can have different configuration while running from same process.

## Syntax

It is intended to do configuration from within the rule, like so:

```
!CONFIG("ignore_case", "Y")
```

First argument is config key, second value. `"1"`, `"Y"` and `"T"` results in `True`, `"0"`, `"N"`, `"F"` - in `False`

## Configurations

| Setting            | Default              | Description                                                                |
|--------------------|----------------------|----------------------------------------------------------------------------|
| implicit_punct     |`T`                   |Automatically adds punctuation characters `,.!:\;` to the rules             |
| ignore_case        |`T`                   |All rules are case-insensitive                                              |