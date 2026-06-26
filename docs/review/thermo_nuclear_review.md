# Thermo-Nuclear Code Quality Review

### 1. Structural Regression / Missed Code-Judo Move (`main.py`)
**Status: BLOCKING**

The implementation in `main.py` is suffering from a massive amount of "spaghetti / branching complexity" due to repetitive argument marshaling. Methods like `wrap()`, `backup()`, `restore()`, and `find()` duplicate nearly identical 20-30 line blocks of `if some_flag: args.append("--some-flag")`. 

This pushes the file past 800 lines (dangerously close to the 1k limit) entirely with incidental complexity.

**The Code-Judo Move:**
Instead of centralizing the conditionals over and over again, reframe the model so the branches disappear entirely. Extract a helper (e.g., `_build_args(command, flags, options)`) or a kwargs mapper that programmatically translates boolean arguments to flags and scalar arguments to options.

For example, a unified helper like this:
```python
def _build_args(command: list[str], flags: dict[str, bool], options: dict[str, Any]) -> list[str]:
    args = list(command)
    for flag, enabled in flags.items():
        if enabled:
            args.append(flag)
    for opt, value in options.items():
        if value is not None:
            args.extend([opt, str(value)])
    return args
```
This single helper deletes over 150 lines of branching complexity across the class and makes the methods one or two lines long. **This is a blocker.** Please restructure the implementation to collapse these duplicate branches into a single clearer flow.

### 2. Ad-hoc Configuration Overwrites (`main.py:add_game_alias`)
**Status: BLOCKING**

The `add_game_alias` method reads the active configuration via `config_show()` (which returns a Python dict from the API's JSON output), modifies it, and then rewrites `config.yaml` using Python's `json.dumps()`.

While valid JSON is technically valid YAML, rewriting a user's `.yaml` configuration file with `json.dumps()` will entirely strip all formatting and comments, fundamentally changing the file format for any human maintaining it. This is brittle, ad-hoc, and highly destructive to the user's config.

If we must mutate the config file, we should either use a proper YAML parser that preserves comments (like `ruamel.yaml`) or push this responsibility to the Ludusavi binary itself. 

### 3. Thin Wrappers & Unnecessary Branching (`discovery.py`)
**Status: REFACTOR**

There are a few instances of unnecessary conditionals that add indirection without simplifying anything:

1. **`_verify()`**:
   ```python
   if env is None:
       result = subprocess.run(..., timeout=_DISCOVERY_VERIFY_TIMEOUT_SECONDS)
   else:
       result = subprocess.run(..., env=env, timeout=_DISCOVERY_VERIFY_TIMEOUT_SECONDS)
   ```
   This is a redundant branch. `subprocess.run(..., env=env)` inherently defaults to the parent process environment when `env=None`. This whole branch can be deleted, leaving just the direct flow.

2. **`_which()`**:
   ```python
   def _which(command: str, path: Optional[str]) -> Optional[str]:
       if path is None:
           return shutil.which(command)
       return shutil.which(command, path=path)
   ```
   Similarly, `shutil.which(..., path=path)` already falls back to `os.environ.get("PATH")` if `path=None`. You can drop the `if` and simply return `shutil.which(command, path=path)`.

### 4. Type Cleanliness & Ad-hoc Boundaries (`models.py`)
**Status: CONCERN**

`models.py` is relying heavily on `Dict[str, Any]` for core configuration structures in `ApiConfig` (`customGames`, `roots`, `backup`, `restore`, `cloud`, etc.).

While this works, it hides the real shape of the data and makes it harder to reason about the configuration API. Why do we need this `Any` cast-heavy contract? Can we make the boundaries more explicit by defining typed models for `roots`, `customGames`, etc.? If these are truly opaque pass-throughs, that's one thing, but if the Python code ever inspects them, they should be typed.

Additionally, `ApiErrorDetails` uses `total=False` alongside `Optional`. Unless the API explicitly emits `null` for these keys, you should prefer `NotRequired` (which is already imported and used elsewhere) over `Optional` to clarify whether a missing key vs an explicitly null key is expected.

---

**Approval Bar Summary:**
I cannot approve this in its current state. The implementation preserves a lot of incidental complexity in `main.py` when there is a plausible code-judo move that would delete it. Furthermore, the YAML config rewrite using JSON is a major maintainability concern.

Please extract an argument-marshaling helper to clean up the API methods, resolve the YAML destruction in `add_game_alias`, and remove the unnecessary branches in `discovery.py`.
