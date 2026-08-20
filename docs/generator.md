# Rule Generator

`rita-generate` builds a minimal ruleset from annotated examples, so you can
bootstrap rules from data instead of writing them by hand.

## Input

A CSV file where every row holds three columns:

1. raw text
2. the span inside that text which should be marked
3. the label to mark it with

```csv
text,span,label
I really like apples,apples,FRUIT
She likes oranges a lot,oranges,FRUIT
The price is 42 eur today,42 eur,AMOUNT
It costs 7 usd,7 usd,AMOUNT
He drives a big red car,big red car,VEHICLE
She has a red car,red car,VEHICLE
```

A `text,span,label` header row is optional and ignored.

A ready-made example ships with the repository at
[`examples/rule-generator.csv`](https://github.com/zaibacu/rita-dsl/blob/master/examples/rule-generator.csv):

```sh
rita-generate -f examples/rule-generator.csv
```

## Usage

```sh
rita-generate -f examples.csv -o rules.rita
```

Without `-o` the ruleset is printed to stdout. Other flags:
`--delimiter` for non-comma CSVs, `--no-validate` to skip the validation
pass, `--debug` for verbose logging.

## What it does

- Spans are tokenized into words, numbers and punctuation
- Spans with the same label and token shape merge into **one rule**:
  positions with several observed values become an `IN_LIST`,
  number positions with several values become a generic `NUM`
- A shape equal to another shape with one extra token folds into it,
  the extra token becoming optional (`?`)

The example above generates:

```
amount_list_0 = {"eur", "usd"}
fruit_list_1 = {"apples", "oranges"}

{WORD("big")?, WORD("red"), WORD("car")}->MARK("VEHICLE")
{NUM, IN_LIST(amount_list_0)}->MARK("AMOUNT")
{IN_LIST(fruit_list_1)}->MARK("FRUIT")
```

## Validation

By default the generated ruleset is compiled with the standalone engine and
executed against every input text - each row's span must come back with the
right label. Rows which cannot be used (span missing from the text, invalid
label, wrong column count) are reported to stderr and skipped. The exit code
is `0` only with full coverage.
