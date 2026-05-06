from typing import Optional, List, Dict, Literal, Any, Union
from .discovery import find_ludusavi
from .core import LudusaviExecutor, LudusaviResponse


class Ludusavi:
    """
    The primary public API for Ludusavi.
    """

    def __init__(
        self,
        explicit_path: Optional[str] = None,
        config_dir: Optional[str] = None,
        no_manifest_update: bool = False,
    ):
        """
        Initialize the Ludusavi wrapper.

        Args:
            explicit_path: Path to the ludusavi binary or flatpak id.
            config_dir: Optional --config directory for Ludusavi.
            no_manifest_update: If True, appends --no-manifest-update to all calls.
        """
        self.command_prefix = find_ludusavi(explicit_path=explicit_path)

        # Add global options to prefix if they apply to the binary call
        # Note: --config and --no-manifest-update are global flags
        if config_dir:
            self.command_prefix.extend(["--config", config_dir])
        if no_manifest_update:
            self.command_prefix.append("--no-manifest-update")

        self.executor = LudusaviExecutor(self.command_prefix)

    # --- Metadata Group ---

    def version(self) -> str:
        """Get the Ludusavi version string."""
        response = self.executor.execute(["--version"], mode="TEXT")
        assert response is not None
        return response.data.strip()

    def schema(
        self,
        category: Literal["api-input", "api-output", "config", "general-output"],
        format: Literal["json", "yaml"] = "json",
    ) -> Union[str, Dict]:
        """Get the Ludusavi JSON/YAML schema for a specific category."""
        mode = "JSON" if format == "json" else "TEXT"
        response = self.executor.execute(
            ["schema", "--format", format, category], mode=mode, auto_api=False
        )
        assert response is not None
        return response.data

    def manifest_show(self) -> LudusaviResponse:
        """Get the full manifest data."""
        response = self.executor.execute(["manifest", "show"], mode="JSON")
        assert response is not None
        return response

    def manifest_update(self, force: bool = False) -> LudusaviResponse:
        """Update the manifest."""
        args = ["manifest", "update"]
        if force:
            args.append("--force")
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    def config_show(self) -> LudusaviResponse:
        """Show the current Ludusavi configuration."""
        response = self.executor.execute(["config", "show"], mode="JSON")
        assert response is not None
        return response

    def config_path(self) -> str:
        """Show the path to the Ludusavi configuration file."""
        response = self.executor.execute(["config", "path"], mode="TEXT")
        assert response is not None
        return response.data.strip()

    # --- Data Group ---

    def backup(
        self,
        games: Optional[List[str]] = None,
        preview: bool = False,
        path: Optional[str] = None,
        force: bool = False,
        wine_prefix: Optional[str] = None,
        sort: Optional[
            Literal["name", "name-rev", "size", "size-rev", "status", "status-rev"]
        ] = None,
        format: Optional[Literal["simple", "zip"]] = None,
        compression: Optional[Literal["none", "deflate", "bzip2", "zstd"]] = None,
        compression_level: Optional[int] = None,
        full_limit: Optional[int] = None,
        differential_limit: Optional[int] = None,
        cloud_sync: bool = False,
        no_cloud_sync: bool = False,
        dump_registry: bool = False,
        include_disabled: bool = False,
        ask_downgrade: bool = False,
        timeout: Optional[float] = None,  # Operations default to no timeout
    ) -> LudusaviResponse:
        """
        Back up data.
        """
        args = ["backup"]
        if preview:
            args.append("--preview")
        if path:
            args.extend(["--path", path])
        if force:
            args.append("--force")
        if wine_prefix:
            args.extend(["--wine-prefix", wine_prefix])
        if sort:
            args.extend(["--sort", sort])
        if format:
            args.extend(["--format", format])
        if compression:
            args.extend(["--compression", compression])
        if compression_level is not None:
            args.extend(["--compression-level", str(compression_level)])
        if full_limit is not None:
            args.extend(["--full-limit", str(full_limit)])
        if differential_limit is not None:
            args.extend(["--differential-limit", str(differential_limit)])
        if cloud_sync:
            args.append("--cloud-sync")
        if no_cloud_sync:
            args.append("--no-cloud-sync")
        if dump_registry:
            args.append("--dump-registry")
        if include_disabled:
            args.append("--include-disabled")
        if ask_downgrade:
            args.append("--ask-downgrade")

        if games:
            args.extend(games)

        response = self.executor.execute(args, mode="JSON", timeout=timeout)
        assert response is not None
        return response

    def restore(
        self,
        games: Optional[List[str]] = None,
        preview: bool = False,
        path: Optional[str] = None,
        force: bool = False,
        sort: Optional[
            Literal["name", "name-rev", "size", "size-rev", "status", "status-rev"]
        ] = None,
        backup_id: Optional[str] = None,
        cloud_sync: bool = False,
        no_cloud_sync: bool = False,
        dump_registry: bool = False,
        include_disabled: bool = False,
        ask_downgrade: bool = False,
        timeout: Optional[float] = None,
    ) -> LudusaviResponse:
        """
        Restore data.
        """
        args = ["restore"]
        if preview:
            args.append("--preview")
        if path:
            args.extend(["--path", path])
        if force:
            args.append("--force")
        if sort:
            args.extend(["--sort", sort])
        if backup_id:
            args.extend(["--backup", backup_id])
        if cloud_sync:
            args.append("--cloud-sync")
        if no_cloud_sync:
            args.append("--no-cloud-sync")
        if dump_registry:
            args.append("--dump-registry")
        if include_disabled:
            args.append("--include-disabled")
        if ask_downgrade:
            args.append("--ask-downgrade")

        if games:
            args.extend(games)

        response = self.executor.execute(args, mode="JSON", timeout=timeout)
        assert response is not None
        return response

    def backups_list(
        self, games: Optional[List[str]] = None, path: Optional[str] = None
    ) -> LudusaviResponse:
        """Show backups."""
        args = ["backups"]
        if path:
            args.extend(["--path", path])
        if games:
            args.extend(games)
        response = self.executor.execute(args, mode="JSON")
        assert response is not None
        return response

    def backups_edit(
        self,
        game: Optional[str] = None,
        path: Optional[str] = None,
        backup_id: Optional[str] = None,
        lock: bool = False,
        unlock: bool = False,
        comment: Optional[str] = None,
    ) -> LudusaviResponse:
        """Edit a backup."""
        args = ["backups", "edit"]
        if path:
            args.extend(["--path", path])
        if backup_id:
            args.extend(["--backup", backup_id])
        if lock:
            args.append("--lock")
        if unlock:
            args.append("--unlock")
        if comment:
            args.extend(["--comment", comment])
        if game:
            args.append(game)
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    # --- Integration Group ---

    def find(
        self,
        games: Optional[List[str]] = None,
        multiple: bool = False,
        path: Optional[str] = None,
        backup: bool = False,
        restore: bool = False,
        steam_id: Optional[str] = None,
        gog_id: Optional[str] = None,
        lutris_id: Optional[str] = None,
        normalized: bool = False,
        fuzzy: bool = False,
        disabled: bool = False,
        partial: bool = False,
    ) -> LudusaviResponse:
        """Find game titles."""
        args = ["find"]
        if multiple:
            args.append("--multiple")
        if path:
            args.extend(["--path", path])
        if backup:
            args.append("--backup")
        if restore:
            args.append("--restore")
        if steam_id:
            args.extend(["--steam-id", steam_id])
        if gog_id:
            args.extend(["--gog-id", gog_id])
        if lutris_id:
            args.extend(["--lutris-id", lutris_id])
        if normalized:
            args.append("--normalized")
        if fuzzy:
            args.append("--fuzzy")
        if disabled:
            args.append("--disabled")
        if partial:
            args.append("--partial")

        if games:
            args.extend(games)
        response = self.executor.execute(args, mode="JSON")
        assert response is not None
        return response

    def cloud_upload(self) -> LudusaviResponse:
        """Upload your local backups to the cloud."""
        response = self.executor.execute(["cloud", "upload"], mode="JSON")
        assert response is not None
        return response

    def cloud_download(self) -> LudusaviResponse:
        """Download your cloud backups."""
        response = self.executor.execute(["cloud", "download"], mode="JSON")
        assert response is not None
        return response

    def cloud_set(
        self,
        provider: Literal[
            "none", "custom", "box", "dropbox", "google-drive", "onedrive", "ftp", "smb", "webdav"
        ],
        options: Optional[List[str]] = None,
    ) -> LudusaviResponse:
        """Configure the cloud system to use."""
        args = ["cloud", "set", provider]
        if options:
            args.extend(options)
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    def bulk_api(self, input_data: Dict[str, Any]) -> LudusaviResponse:
        """Execute bulk requests using JSON input."""
        response = self.executor.execute(
            ["api"], mode="STDIN_JSON", input_data=input_data, auto_api=False
        )
        assert response is not None
        return response

    def wrap(self, command: List[str]) -> LudusaviResponse:
        """Wrap restore/backup around game execution."""
        args = ["wrap", "--"] + command
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    # --- Utilities ---

    def complete(self, shell: Literal["bash", "fish", "zsh", "powershell", "elvish"]) -> str:
        """Generate shell completion scripts."""
        response = self.executor.execute(["complete", shell], mode="TEXT")
        assert response is not None
        return response.data

    def open_gui(self, custom_game: Optional[str] = None):
        """Open the GUI."""
        args = ["gui"]
        if custom_game:
            args.extend(["--custom-game", custom_game])
        self.executor.execute(args, mode="SPAWN")
