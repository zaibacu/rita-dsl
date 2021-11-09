# Syntax guide

## The basic building blocks

You have `LITERAL` which is any kind of string behind quotes, eg.:

```
"Hello world!"
```

You have `MACRO` which is main backbone of everything.

Using parenthesis, you can pass arguments to macro:
```
LOAD("path/filename.txt") # Load a text file
```

if macro doesn't require any, you can simply call it

```
WORD # Declare, that you'll have any kind of word
```

Also, macro can have modifier (if it supports it)

```
WORD+ # Declare, that you'll have 1..N words
WORD* # Declare, that you'll have 0..N words
WORD? # Declare, that you'll have 1 or no words
WORD! # Declare, that you want to ignore this word
```

More examples

```
WORD("cat") # Declare, that you'll have exact word `cat`

{"red", "green", "blue"} # Declare array of words
```

**NOTE** All of the MACROS are spelled in capital letters

And finally you have `VARIABLE`. First you must declare it and later you can use just by spelling it's name

```
CarModels = LOAD("path/models.txt")

# ...

IN_LIST(CarModels) # Check if token is inside of list of car models we provided
```

If using directly inside macro, array can be writen with simple commas

```
IN_LIST("audi", "toyota", "bmw", "honda", "nissan", "ford")
```


For our declarations to make any sense, we need to build an expression. More on that in next topic.

## Expressions

This language is built on expressions. 
One expression means:

a) Single rule defining entity

b) Single variable declaration

Rule expression ends with an arrow `->`, eg.:

`WORD("something") -> MARK("SOMETHING_LABEL")`

with MACRO `MARK` we're assigning a label to rule

Variable declaration expression ends with equals sign `=`, eg.:
```
a = "Apple"
```

When building a rule, you may want to combine several rules into one, you can use array builder for that:

```
{IN_LIST({"red", "green", "blue", "white", "black", "silver", "brown"}), WORD("car")} -> MARK("CAR_COLOR")
```

we're saying: `If any of these color words are present in text and is followed by word "car", we assume this part can be labeled as "CAR_COLOR"`

## Logical variants

You can say, that your rule expects either `word1`, or `word2`. Usually this can be achieved by writing two separate rules, but there's easier way: 
```
{WORD("word1")|WORD("word2")}
```

Pipe character (`|`) marks a logical `OR` meaning that either right or left side can be matched. It works only on surface level, if you want nested logic - write separate rules.