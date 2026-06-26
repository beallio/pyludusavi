from pyludusavi.models import LudusaviApiOutput


def test_models_import():
    assert LudusaviApiOutput


def test_api_output_optional_top_level_fields():
    # `games` is the only guaranteed key; the CLI omits the rest when empty.
    assert "games" in LudusaviApiOutput.__required_keys__
    for key in ("errors", "overall", "cloud"):
        assert key in LudusaviApiOutput.__optional_keys__


def test_api_output_accepts_games_only():
    out: LudusaviApiOutput = {"games": {}}
    assert out["games"] == {}


def test_api_error_details_keys_optional():
    from pyludusavi.models import ApiErrorDetails

    for key in ("cloudConflict", "cloudSyncFailed", "someGamesFailed", "unknownGames"):
        assert key in ApiErrorDetails.__optional_keys__
        assert key not in ApiErrorDetails.__required_keys__
