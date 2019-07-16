# Extending

Custom modules can be loaded via `!IMPORT(<module_path>)`

Example of basic fuzzy matcher:

```
!IMPORT("rita.modules.fuzzy")

FUZZY("squirrel") -> MARK("CRITTER")
```

Code can be seen in: [fuzzy.py](https://github.com/zaibacu/rita-dsl/blob/master/rita/modules/fuzzy.py)

After import is done, custom macros defined in imported module can be executed. 

## Interface for custom Macro

Each macro must have atleast two arguments 

- `op` - custom handling of `?`, `*` and `+` operators. If it has no use, argument can be defined as `def <macro>(*args, op=None)` and simply ignored inside code

- `context` - context is either `dict` or `list` type used to store results

All other arguments should be defined at the start
