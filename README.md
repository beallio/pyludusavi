# pyludusavi

A robust, type-safe Python wrapper for the [Ludusavi](https://github.com/mtkennerly/ludusavi) CLI.

## Features

- **100% CLI Coverage**: Supports all 16+ subcommands and 50+ flags.
- **Linux-First**: Native support for both local binaries and Flatpak.
- **Type-Safe**: Comprehensive `TypedDict` models for all JSON outputs (Python 3.12+).
- **Dual-Mode Execution**: Transparently handles binary vs. Flatpak command prefixing.
- **TDD-Backed**: High-quality implementation with an extensive regression suite.

## Installation

```bash
uv add pyludusavi
# or
pip install pyludusavi
```

## Quick Start

### Basic Initialization
The wrapper automatically discovers Ludusavi via `PATH` or Flatpak.

```python
from pyludusavi import Ludusavi

lud = Ludusavi()
print(f"Ludusavi version: {lud.version()}")
```

### Backing Up Games
Perform a preview scan or a full backup.

```python
# Preview a backup for a specific game
result = lud.backup(games=["The Witcher 3"], preview=True)

# Access typed data
for name, game in result.data["games"].items():
    print(f"Game: {name}, Status: {game['change']}")
```

### Searching for Games
Use Steam IDs or fuzzy matching to find games in the manifest.

```python
# Find by Steam ID
result = lud.find(steam_id="292030")

# Use fuzzy matching
result = lud.find(games=["Witcher"], fuzzy=True)
```

### Advanced Usage

#### Flatpak Support
If you have Ludusavi installed via Flatpak, `pyludusavi` detects it automatically. You can also specify a custom path or ID:

```python
lud = Ludusavi(explicit_path="com.github.mtkennerly.ludusavi")
```

#### Custom Config Directory
```python
lud = Ludusavi(config_dir="/home/user/my-ludusavi-config")
```

#### Bulk API
For performance-critical bulk operations, use the native `api` subcommand:

```python
payload = {
    "requests": [
        {"kind": "backup", "games": ["Game 1"]},
        {"kind": "backup", "games": ["Game 2"]}
    ]
}
lud.bulk_api(payload)
```

## Error Handling

- `LudusaviNotFoundError`: Raised if the executable or Flatpak isn't found.
- `LudusaviExecutionError`: Raised if the process exits with a non-zero code.
- `LudusaviContractError`: Raised if the CLI output is malformed or non-JSON when expected.

## License

MIT
