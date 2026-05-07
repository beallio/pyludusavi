# Plan: Get Game Alias Feature

This plan defines the implementation of a new feature in the `Ludusavi` class that allows users to retrieve the target title for a given game name from the configuration.

## Problem Definition
After adding an alias via `add_game_alias`, users need a way to check which official title a custom name points to.

## Architecture & Strategy
1. **Source**: The `customGames` section of the Ludusavi configuration.
2. **Logic**:
    - Retrieve the current configuration via `config_show()`.
    - Iterate through the `customGames` list.
    - If an entry's `name` matches the input, return its `alias` field.
    - Return `None` if no match is found.

## Implementation Tasks

### Phase 1: Test (RED)
- [ ] **Task 1.1: Update `tests/test_alias.py`**
    - Add `test_get_game_alias_found`: Returns the alias when the name exists.
    - Add `test_get_game_alias_not_found`: Returns `None` when the name does not exist.

### Phase 2: Implementation (GREEN)
- [ ] **Task 2.1: Add `get_game_alias` to `src/pyludusavi/main.py`**
    - Signature: `def get_game_alias(self, name: str) -> Optional[str]:`
    - Implementation:
      ```python
      config = self.config_show().data
      for game in config.get("customGames", []):
          if game.get("name") == name:
              return game.get("alias")
      return None
      ```

### Phase 3: Validation
- [ ] **Task 3.1: Quality Checks**
    - Run `ruff` and `pytest`.
