"""
Farzana PC essentials reader (read-only).

  uv run python -m farzana.pc_reader --watch ~/FarzanaInbox --vault ./vault
  uv run python -m farzana.pc_reader --once --watch ~/FarzanaInbox --vault ./vault
  uv run farzana pc-reader --watch ~/FarzanaInbox

Drop .ics / .eml / .md / .txt into the watch folder.
Farzana only **reads** them into vault/pc/ — never sends mail or books calendar.
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="farzana.pc_reader",
        description="Read-only PC essentials → Farzana vault (ICS / EML / MD).",
    )
    parser.add_argument(
        "--watch",
        "-w",
        type=Path,
        required=True,
        help="Folder where you drop calendar/mail/file exports",
    )
    parser.add_argument(
        "--vault",
        "-v",
        type=Path,
        default=None,
        help="Vault root (default: VAULT_PATH from .env or ./vault)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Scan once and exit (no loop)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=15.0,
        help="Poll interval seconds when watching (default 15)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Debug logging",
    )
    args = parser.parse_args(argv)

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    vault = args.vault
    if vault is None:
        try:
            from farzana.core.config import get_settings

            get_settings.cache_clear()
            vault = get_settings().vault_path
        except Exception:
            vault = Path("./vault")

    from farzana.pc_reader.watch import scan_folder, watch_loop

    if args.once:
        try:
            results = scan_folder(args.watch, vault)
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 1
        if not results:
            print("No new files to ingest.")
        else:
            print(f"Ingested {len(results)} file(s):")
            for p in results:
                print(f"  → {p}")
        return 0

    print("Farzana PC reader — read-only essentials")
    print(f"  watch: {args.watch.expanduser()}")
    print(f"  vault: {vault}")
    print("  Drop .ics / .eml / .md / .txt  |  Ctrl+C to stop")
    print("  Farzana never sends mail or books events.")
    try:
        watch_loop(args.watch, vault, interval_sec=args.interval, once=False)
    except KeyboardInterrupt:
        print("\nStopped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
