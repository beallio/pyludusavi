# Plan: Add Game Alias Feature

This plan defines the implementation of a new feature in the `Ludusavi` class that allows users to programmatically add game aliases to the Ludusavi configuration.

## Problem Definition
Ludusavi allows "aliasing" games (e.g., mapping a custom name to a manifest entry) via the `customGames` array in `config.yaml`. However, the CLI does not provide a direct command to add these aliases. The wrapper needs a robust way to perform this modification using only the Python Standard Library.

## Architecture & Strategy
Since Ludusavi uses YAML for its configuration but can export it as JSON via the `--api` flag, and since YAML is a superset of JSON, we can safely update the configuration by writing a JSON-formatted string back to the `config.yaml` file.

1. **Discovery**: Use `config_path()` to locate the active configuration file.
2. **Read**: Use `config_show()` to retrieve the current full configuration as a Python dictionary.
3. **Modify**: Update the `customGames` list within the dictionary.
4. **Write**: Overwrite the `config.yaml` file with the updated dictionary serialized as JSON.

## Implementation Tasks

### Phase 1: Test (RED)
- [ ] **Task 1.1: Create `tests/test_alias.py`**
    - Mock `config_path` and `config_show`.
    - Mock `builtins.open` to verify the write operation.
    - Test that `add_game_alias("My Game", "Official Title")` results in the correct data being written.

### Phase 2: Implementation (GREEN)
- [ ] **Task 2.1: Add `add_game_alias` to `src/pyludusavi/main.py`**
    - Signature: `def add_game_alias(self, name: str, alias: str) -> None:`
    - Logic:
      ```python
      path = self.config_path()
      config = self.config_show().data
      
      new_custom = {
          "name": name,
          "alias": alias,
          "files": [],
          "registry": [],
          "installDir": [],
          "winePrefix": []
      }
      
      # Avoid duplicates
      if not any(g.get("name") == name for g in config.get("customGames", [])):
          config.setdefault("customGames", []).append(new_custom)
          
      with open(path, "w", encoding="utf-8") as f:
          json.dump(config, f, indent=2)
      ```

### Phase 3: Validation
- [ ] **Task 3.1: Linting & Formatting**
    - Run `ruff` to ensure style compliance.
- [ ] **Task 3.2: Verification**
    - Verify that `lud.config_show()` reflects the change after the write.

## Dependency Requirements
- **Standard Library Only**: `json`, `builtins.open`.
