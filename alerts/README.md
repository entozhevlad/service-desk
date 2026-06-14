# Telegram alerts for CI/CD

Скрипт `telegram_notifier.py` отправляет в Telegram статус pipeline и jobs из GitHub Actions.

## Локальная настройка

```bash
cd alerts
cp .env.example .env
# заполните TELEGRAM_BOT_TOKEN и TELEGRAM_CHAT_ID
uv sync
uv run python telegram_notifier.py --status success --message "test from local"
```

## GitHub Actions

В репозитории → Settings → Secrets and variables → Actions:

| Secret | Описание |
|--------|----------|
| `TELEGRAM_BOT_TOKEN` | Токен бота от [@BotFather](https://t.me/BotFather) |
| `TELEGRAM_CHAT_ID` | ID чата или канала |

Job `notify-telegram` в `.github/workflows/ci.yaml` запускается всегда (`if: always()`) и шлёт сводку по всем jobs.

## Как получить chat_id

1. Напишите боту любое сообщение.
2. Откройте `https://api.telegram.org/bot<TOKEN>/getUpdates`.
3. Возьмите `message.chat.id` из ответа.
