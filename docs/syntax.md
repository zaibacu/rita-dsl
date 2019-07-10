# Syntax guide

## The basic building blocks

You have `LITERAL` which is any kind of string behind quotes, eg.:

```
"Hello world!"
```

You have `MACRO` which is main backbone of everything.

You can

```
LOAD("path/filename.txt") # Load a text file
WORD # Declare, that you'll have any kind of word
WORD("cat") # Declare, that you'll have exact word `cat`
WORD+ # Declare, that you'll have 1..N words
WORD* # Declare, that you'll have 0..N words
WORD? # Declare, that you'll have 1 or no words
{"red", "green", "blue"} # Declare array of words
```

**NOTE** All of the MACROS are spelled in capital letters

And finally you have `VARIABLE`. First you must declare it and later you can use just by spelling it's name

```
CarModels = LOAD("path/models.txt")

# ...

IN_LIST(CarModels) # Check if token is inside of list of car models we provided
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
