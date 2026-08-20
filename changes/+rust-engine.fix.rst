Rust engine bindings overhaul (paired with the rita-rust-engine rewrite onto the pure-Rust ``regex`` crate - no more RE2/CRE2 system dependencies):

- ``RITA_RUST_LIB`` environment variable can point directly at the built shared library
- Unicode texts now report correct character offsets (the engine works in UTF-8 bytes; offsets are converted on the Python side)
- Result memory is freed after every ``execute()`` call and the context is released when the executor is garbage collected - previously both leaked
- ``save()``/``__iter__`` work on ``RustRuleExecutor`` (``raw_patterns`` was never set)
- Null results from the native library raise clear errors instead of crashing
