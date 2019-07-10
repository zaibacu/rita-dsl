# Syntax guide

## The basic building blocks

You have `LITERAL` which is any kind of string behind quotes, eg.:

```
"Hello world!"
```

You have `MACRO` which is main backbone of everything.

You can

```
LOAD{"path/filename.txt"} # Load a text file
WORD # Declare, that you'll have any kind of word
WORD{"cat"} # Declare, that you'll have exact word `cat`
WORD+ # Declare, that you'll have 1..N words
WORD* # Declare, that you'll have 0..N words
WORD? # Declare, that you'll have 1 or no words
```

* NOTE * All of the MACROS are spelled in capital letters

And finally you have `VARIABLE`. First you must declare it and later you can use just by spelling it's name

```
CarModels = LOAD{"path/models.txt"}

# ...

IN_LIST{CarModels} # Check if token is inside of list of car models we provided
```

