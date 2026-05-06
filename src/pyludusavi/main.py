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
        """
        Get the Ludusavi version string.

        Returns:
            str: The version string (e.g., "ludusavi 0.31.0").
        """
        response = self.executor.execute(["--version"], mode="TEXT")
        assert response is not None
        return response.data.strip()

    def schema(
        self,
        category: Literal["api-input", "api-output", "config", "general-output"],
        format: Literal["json", "yaml"] = "json",
    ) -> Union[str, Dict]:
        """
        Display schemas that Ludusavi uses.

        Args:
            category: The schema category to display.
            format: Output format (json or yaml).

        Returns:
            Union[str, Dict]: The requested schema.
        """
        mode = "JSON" if format == "json" else "TEXT"
        response = self.executor.execute(
            ["schema", "--format", format, category], mode=mode, auto_api=False
        )
        assert response is not None
        return response.data

    def manifest_show(self) -> LudusaviResponse:
        """
        Print the content of the manifest, including any custom entries.

        Returns:
            LudusaviResponse: The JSON response containing the manifest data.
        """
        response = self.executor.execute(["manifest", "show"], mode="JSON")
        assert response is not None
        return response

    def manifest_update(self, force: bool = False) -> LudusaviResponse:
        """
        Check for any manifest updates and download if available.
        By default, does nothing if the most recent check was within the last 24 hours.

        Args:
            force: Check again even if the most recent check was within the last 24 hours.

        Returns:
            LudusaviResponse: The raw text response from the update check.
        """
        args = ["manifest", "update"]
        if force:
            args.append("--force")
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    def config_show(self) -> LudusaviResponse:
        """
        Print the active configuration.

        Returns:
            LudusaviResponse: The JSON response containing the current configuration.
        """
        response = self.executor.execute(["config", "show"], mode="JSON")
        assert response is not None
        return response

    def config_path(self) -> str:
        """
        Print the path to the config file.

        Returns:
            str: The absolute path to Ludusavi's config.yaml.
        """
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

        This command automatically updates the manifest if necessary.

        Args:
            games: Only back up these specific games.
            preview: List out what would be included, but don't actually perform the operation.
            path: Directory in which to store the backup. It will be created if it does not already exist.
            force: Don't ask for confirmation.
            wine_prefix: Extra Wine/Proton prefix to check for saves. This should be a folder with
                an immediate child folder named "drive_c" (or another letter).
            sort: Sort the game list by different criteria.
            format: Format in which to store new backups (simple or zip).
            compression: Compression method to use for new zip backups.
            compression_level: Compression level to use for new zip backups.
                Valid ranges: 1 to 9 for deflate/bzip2, -7 to 22 for zstd.
            full_limit: Maximum number of full backups to retain per game (1-255).
            differential_limit: Maximum number of differential backups to retain per full backup (0-255).
            cloud_sync: Upload any changes to the cloud when the backup is complete.
            no_cloud_sync: Don't perform any cloud checks or synchronization.
            dump_registry: Include the serialized registry content in the output.
                Only includes the native Windows registry, not Wine.
            include_disabled: Include all disabled games.
            ask_downgrade: Ask what to do when a game's backup is newer than the live data.
                This option ignores force.
            timeout: Maximum time to wait for the process.

        Returns:
            LudusaviResponse: The JSON response from Ludusavi.
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

        Args:
            games: Only restore these specific games.
            preview: List out what would be included, but don't actually perform the operation.
            path: Directory containing a Ludusavi backup.
            force: Don't ask for confirmation.
            sort: Sort the game list by different criteria.
            backup_id: Restore a specific backup, using an ID returned by the `backups` command.
                This is only valid when restoring a single game.
            cloud_sync: Warn if the local and cloud backups are out of sync.
            no_cloud_sync: Don't perform any cloud checks or synchronization.
            dump_registry: Include the serialized registry content in the output.
            include_disabled: Include all disabled games.
            ask_downgrade: Ask what to do when a game's backup is older than the live data.
                This option ignores force.
            timeout: Maximum time to wait for the process.

        Returns:
            LudusaviResponse: The JSON response from Ludusavi.
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
        """
        Show backups.

        Args:
            games: Only report these specific games.
            path: Directory in which to find backups. When unset, this defaults to
                the restore path from the config file.

        Returns:
            LudusaviResponse: The JSON response containing the list of backups.
        """
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
        """
        Edit a backup.

        These changes are not automatically synced with the cloud, so you may want
        to use `cloud_upload()` afterward.

        Args:
            game: Which game to edit.
            path: Directory in which to find backups. When unset, this defaults to
                the restore path from the config file.
            backup_id: Edit a specific backup, using an ID returned by the `backups_list()` command.
                When not specified, this defaults to the latest backup.
            lock: Lock the backup to prevent deletion.
            unlock: Unlock the backup.
            comment: Add a comment to the backup.

        Returns:
            LudusaviResponse: The raw text response confirming the edit.
        """
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
        """
        Find game titles.

        Precedence: Steam ID -> GOG ID -> Lutris ID -> exact names -> normalized names.
        Once a match is found for one of these options, Ludusavi will stop looking
        and return that match, unless you set `multiple=True`, in which case,
        the results will be sorted by how well they match.

        Aliases will be resolved to the target title.
        This command automatically updates the manifest if necessary.

        Args:
            games: Look up game by an exact title. With multiple values, they will
                be checked in the order given.
            multiple: Keep looking for all potential matches, instead of stopping at the first match.
            path: Directory in which to find backups. When unset, this defaults to
                the restore path from the config file.
            backup: Ensure the game is recognized in a backup context.
            restore: Ensure the game is recognized in a restore context.
            steam_id: Look up game by a Steam ID.
            gog_id: Look up game by a GOG ID.
            lutris_id: Look up game by a Lutris slug.
            normalized: Look up game by an approximation of the title. Ignores capitalization,
                "edition" suffixes, year suffixes, and some special symbols.
                This may find multiple games for a single input.
            fuzzy: Look up games with fuzzy matching. This may find multiple games for a single input.
            disabled: Select games that are disabled.
            partial: Select games that have some saves disabled.

        Returns:
            LudusaviResponse: The JSON response containing the search results.
        """
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
        """
        Upload your local backups to the cloud, overwriting any existing cloud backups.

        Returns:
            LudusaviResponse: The JSON response confirming the upload.
        """
        response = self.executor.execute(["cloud", "upload"], mode="JSON")
        assert response is not None
        return response

    def cloud_download(self) -> LudusaviResponse:
        """
        Download your cloud backups, overwriting any existing local backups.

        Returns:
            LudusaviResponse: The JSON response confirming the download.
        """
        response = self.executor.execute(["cloud", "download"], mode="JSON")
        assert response is not None
        return response

    def cloud_set(
        self,
        provider: Literal[
            "none",
            "custom",
            "box",
            "dropbox",
            "google-drive",
            "onedrive",
            "ftp",
            "smb",
            "webdav",
        ],
        options: Optional[List[str]] = None,
    ) -> LudusaviResponse:
        """
        Configure the cloud system to use.

        Args:
            provider: The cloud provider to use.
            options: Provider-specific options.

        Returns:
            LudusaviResponse: The raw text response confirming the configuration.
        """
        args = ["cloud", "set", provider]
        if options:
            args.extend(options)
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    def bulk_api(self, input_data: Dict[str, Any]) -> LudusaviResponse:
        """
        Execute bulk requests using JSON input.

        Args:
            input_data: JSON data containing the bulk requests.
                Use the `schema('api-input')` command to see the format.

        Returns:
            LudusaviResponse: The JSON response containing the results for each request.
        """
        response = self.executor.execute(
            ["api"], mode="STDIN_JSON", input_data=input_data, auto_api=False
        )
        assert response is not None
        return response

    def wrap(self, command: List[str]) -> LudusaviResponse:
        """
        Wrap restore/backup around game execution.

        Args:
            command: Commands to launch the game.
                Example: `wrap(["./game.exe", "--windowed"])`

        Returns:
            LudusaviResponse: The raw text response confirming the wrap operation.
        """
        args = ["wrap", "--"] + command
        response = self.executor.execute(args, mode="TEXT")
        assert response is not None
        return response

    # --- Utilities ---

    def complete(self, shell: Literal["bash", "fish", "zsh", "powershell", "elvish"]) -> str:
        """
        Generate shell completion scripts.

        Args:
            shell: The shell for which to generate completions.

        Returns:
            str: The generated completion script.
        """
        response = self.executor.execute(["complete", shell], mode="TEXT")
        assert response is not None
        return response.data

    def open_gui(self, custom_game: Optional[str] = None):
        """
        Open the GUI.

        Args:
            custom_game: Open the custom game screen, then either create a new
                entry with this name or scroll to an existing entry.
        """
        args = ["gui"]
        if custom_game:
            args.extend(["--custom-game", custom_game])
        self.executor.execute(args, mode="SPAWN")

    def add_game_alias(self, name: str, alias: str) -> None:
        """
        Add a game alias to the Ludusavi configuration.

        This method updates the `customGames` section in `config.yaml` to map a
        custom name to an existing game in the manifest.

        Args:
            name: The custom name for the game.
            alias: The official title of the game as it appears in the manifest.
        """
        import json

        path = self.config_path()
        response = self.config_show()
        config = response.data

        new_custom = {
            "name": name,
            "alias": alias,
            "files": [],
            "registry": [],
            "installDir": [],
            "winePrefix": [],
        }

        # Avoid duplicates
        custom_games = config.setdefault("customGames", [])
        if not any(g.get("name") == name for g in custom_games):
            custom_games.append(new_custom)

        with open(path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
