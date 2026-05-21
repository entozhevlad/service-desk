import argparse
import os
import sys
import asyncio
from pathlib import Path

from aiogram import Bot


def _load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def _required_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Environment variable {name} is required")
    return value


def build_ci_message(
    *,
    status: str,
    workflow: str,
    repository: str,
    branch: str,
    commit: str,
    run_url: str,
    job: str | None = None,
) -> str:
    lines = [
        f"CI/CD status: {status.upper()}",
        f"Repository: {repository}",
        f"Workflow: {workflow}",
        f"Branch: {branch}",
        f"Commit: {commit[:12]}",
    ]
    if job:
        lines.append(f"Job: {job}")
    lines.append(f"Run: {run_url}")
    return "\n".join(lines)


async def send_telegram_message(*, token: str, chat_id: str, text: str) -> None:
    bot = Bot(token=token)
    try:
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            disable_web_page_preview=True,
        )
    finally:
        await bot.session.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Send CI/CD status to Telegram")
    parser.add_argument("--status", required=True, help="success|failure|cancelled")
    parser.add_argument("--workflow", default=os.getenv("GITHUB_WORKFLOW", "CI"))
    parser.add_argument("--repository", default=os.getenv("GITHUB_REPOSITORY", "unknown"))
    parser.add_argument("--branch", default=os.getenv("GITHUB_REF_NAME", "unknown"))
    parser.add_argument("--commit", default=os.getenv("GITHUB_SHA", "unknown"))
    parser.add_argument("--run-url", default=os.getenv("GITHUB_RUN_URL", ""))
    parser.add_argument("--job", default=os.getenv("GITHUB_JOB", ""))
    parser.add_argument("--message", default="", help="Raw text message override")
    return parser.parse_args()


def main() -> int:
    _load_env_file(Path(__file__).resolve().parent / ".env")
    args = parse_args()
    token = _required_env("TELEGRAM_BOT_TOKEN")
    chat_id = _required_env("TELEGRAM_CHAT_ID")

    message = args.message.strip() or build_ci_message(
        status=args.status,
        workflow=args.workflow,
        repository=args.repository,
        branch=args.branch,
        commit=args.commit,
        run_url=args.run_url,
        job=args.job or None,
    )

    asyncio.run(send_telegram_message(token=token, chat_id=chat_id, text=message))
    print("Telegram notification sent")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
