import argparse

def get_session_id_from_cli() -> str | None:
    """Parses CLI arguments in search of --session-id."""
    parser = argparse.ArgumentParser(description="Azor the ChatDog — interactive terminal assistant! 🐶")
    parser.add_argument(
        '--session-id',
        type=str,
        default=None,
        help="Session ID to load and continue (e.g. a1b2c3d4 from a1b2c3d4-log.json)",
    )
    args = parser.parse_args()
    return args.session_id
