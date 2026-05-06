# Ludusavi Wrapper Specification

This document serves as the Source of Truth for the Ludusavi Python wrapper.

## Target Version
- **Ludusavi v0.31.0+**

## CLI Mapping & Output Contract

| Method | Subcommand | Mode | Output |
| :--- | :--- | :--- | :--- |
| `manifest_update()` | `manifest update` | TEXT | Raw stdout |
| `manifest_show()` | `manifest show` | JSON | Manifest dictionary |
| `backup()` | `backup` | JSON | Backup result dictionary |
| `restore()` | `restore` | JSON | Restore result dictionary |
| `backups_list()` | `backups` | JSON | List of backups |
| `backups_edit()` | `backups edit` | JSON | Edit confirmation |
| `find()` | `find` | JSON | Search result dictionary |
| `cloud_upload()` | `cloud upload` | JSON | Sync result dictionary |
| `cloud_download()` | `cloud download` | JSON | Sync result dictionary |
| `cloud_set()` | `cloud set` | TEXT | Raw stdout |
| `bulk_api()` | `api` | STDIN_JSON | Multi-response dictionary |
| `schema()` | `schema` | JSON/TEXT | Schema dictionary or raw text |
| `wrap()` | `wrap` | JSON | Execution result dictionary |
| `complete()` | `complete` | TEXT | Shell script string |
| `open_gui()` | `gui` | SPAWN | Non-blocking process |
| `version()` | `--version` | TEXT | "ludusavi X.Y.Z" |

## Version Drift & Compatibility Policy

1. **Unknown Fields**: The wrapper MUST NOT discard fields present in the CLI output that are not defined in the `TypedDict` models. These fields will be accessible via the `.raw` attribute of the `LudusaviResponse`.
2. **Hybrid Typing**: 
    - Top-level status fields (e.g., `errors`, `overall`) are considered **Stable** and will be strictly typed.
    - Deeply nested data (e.g., specific game metadata) will use `total=False` to avoid breaking changes when Ludusavi adds new properties.
3. **Execution Safety**:
    - The wrapper will not treat `stderr` as a failure unless the `returncode` is non-zero.
    - `LudusaviContractError` will be raised if a command expected to return JSON returns non-JSON data.
