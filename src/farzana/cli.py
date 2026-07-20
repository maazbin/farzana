"""
Farzana CLI

  uv run farzana           # register webhook from .env PUBLIC_BASE_URL + start :8000
  uv run farzana --reload
  uv run farzana health
  uv run farzana serve --no-webhook   # API only
  uv run farzana worker
  uv run farzana pc-reader --watch ~/FarzanaInbox --once
"""

from __future__ import annotations

import argparse
import sys


def _settings():
    from farzana.core.config import get_settings

    get_settings.cache_clear()
    return get_settings()


def _register_webhook_quiet() -> int:
    """0 ok, 1 config error, 2 network error."""
    from farzana.services.telegram import (
        TelegramNetworkError,
        register_webhook_from_settings,
    )

    settings = _settings()
    if not settings.telegram_bot_token:
        print("ERROR: TELEGRAM_BOT_TOKEN missing in .env")
        return 1
    if not settings.public_base_url.strip():
        print("ERROR: PUBLIC_BASE_URL missing in .env")
        print("  Put your public https base there (whatever exposes this machine), e.g.")
        print("  PUBLIC_BASE_URL=https://xxxx.example.com")
        return 1
    if not settings.owner_user_id:
        print("WARNING: TELEGRAM_USER_ID empty — everyone will be denied")

    try:
        line = register_webhook_from_settings(settings)
        print("Webhook OK:", line)
        return 0
    except TelegramNetworkError as e:
        print("ERROR: Telegram network")
        print(str(e))
        return 2
    except Exception as e:
        print(f"ERROR: {e}")
        return 1


def _cmd_serve(args: argparse.Namespace) -> int:
    import uvicorn

    if not args.no_webhook:
        print("Registering Telegram webhook from PUBLIC_BASE_URL …")
        code = _register_webhook_quiet()
        if code != 0:
            if args.force:
                print("Continuing without webhook (--force).")
            else:
                print("Fix .env / network, or: uv run farzana --force")
                return code
    else:
        print("Skipping webhook (--no-webhook).")

    print(f"Farzana API → http://127.0.0.1:{args.port}")
    print("Message your bot on Telegram. Ctrl+C to stop.")
    uvicorn.run(
        "farzana.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
    return 0


def _cmd_webhook(_args: argparse.Namespace) -> int:
    return _register_webhook_quiet()


def _cmd_worker(args: argparse.Namespace) -> int:
    from farzana.workers.celery_app import celery_app

    pool = args.pool
    if pool == "auto":
        pool = "solo" if sys.platform == "win32" else "prefork"

    celery_app.worker_main(
        [
            "worker",
            f"--loglevel={args.loglevel}",
            f"--concurrency={args.concurrency}",
            f"--pool={pool}",
        ]
    )
    return 0


def _cmd_health(_args: argparse.Namespace) -> int:
    from farzana.services import vault as vault_io

    s = _settings()
    vault_io.ensure_vault(s.vault_path)
    print("product     : Farzana")
    print("env         :", s.app_env)
    print("vault       :", s.vault_path.resolve())
    print("telegram    :", "yes" if s.telegram_bot_token else "NO")
    print("openai      :", "yes" if s.openai_api_key else "NO")
    print("owner_id    :", s.owner_user_id or "NOT SET")
    print("eager       :", s.celery_task_always_eager)
    print("public_url  :", s.public_base_url or "(set PUBLIC_BASE_URL in .env)")
    print("webhook_url :", s.webhook_url or "(needs PUBLIC_BASE_URL)")
    return 0


def _cmd_pc_reader(args: argparse.Namespace) -> int:
    """Read-only PC essentials → vault (ICS / EML / MD drops)."""
    from farzana.pc_reader.__main__ import main as pc_main

    argv: list[str] = ["--watch", str(args.watch)]
    if args.vault:
        argv.extend(["--vault", str(args.vault)])
    if args.once:
        argv.append("--once")
    if args.interval != 15.0:
        argv.extend(["--interval", str(args.interval)])
    if args.verbose:
        argv.append("--verbose")
    return pc_main(argv)


def main(argv: list[str] | None = None) -> None:
    raw = list(sys.argv[1:] if argv is None else argv)

    known = {"serve", "webhook", "worker", "health", "pc-reader", "-h", "--help"}
    if not raw:
        raw = ["serve"]
    elif raw[0] not in known:
        raw = ["serve", *raw]

    parser = argparse.ArgumentParser(
        prog="farzana",
        description="Farzana — the aide who listens carefully",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_serve = sub.add_parser(
        "serve",
        help="Webhook from PUBLIC_BASE_URL + API on :8000 (default)",
    )
    p_serve.add_argument("--host", default="0.0.0.0")
    p_serve.add_argument("--port", type=int, default=8000)
    p_serve.add_argument("--reload", action="store_true")
    p_serve.add_argument(
        "--no-webhook",
        action="store_true",
        help="Only start API; do not call Telegram setWebhook",
    )
    p_serve.add_argument(
        "--force",
        action="store_true",
        help="Start API even if webhook registration fails",
    )
    p_serve.set_defaults(func=_cmd_serve)

    p_webhook = sub.add_parser("webhook", help="Only register webhook from .env")
    p_webhook.set_defaults(func=_cmd_webhook)

    p_worker = sub.add_parser("worker", help="Celery worker")
    p_worker.add_argument("--concurrency", type=int, default=1)
    p_worker.add_argument("--loglevel", default="INFO")
    p_worker.add_argument("--pool", default="auto")
    p_worker.set_defaults(func=_cmd_worker)

    p_health = sub.add_parser("health", help="Check .env")
    p_health.set_defaults(func=_cmd_health)

    p_pc = sub.add_parser(
        "pc-reader",
        help="Read-only PC essentials (ICS/EML/MD) → vault — never send/book",
    )
    p_pc.add_argument(
        "--watch",
        "-w",
        required=True,
        help="Folder where you drop calendar/mail/file exports",
    )
    p_pc.add_argument(
        "--vault",
        "-v",
        default=None,
        help="Vault root (default: VAULT_PATH from .env)",
    )
    p_pc.add_argument(
        "--once",
        action="store_true",
        help="Scan once and exit",
    )
    p_pc.add_argument(
        "--interval",
        type=float,
        default=15.0,
        help="Poll seconds when watching (default 15)",
    )
    p_pc.add_argument("--verbose", action="store_true")
    p_pc.set_defaults(func=_cmd_pc_reader)

    args = parser.parse_args(raw)
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
