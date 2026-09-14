# Librus → Telegram: уведомления о домашних заданиях

Скрипт проверяет электронный дневник **Librus Synergia** и присылает новые домашние задания и объявления в Telegram-группу/канал. Написан для одного ребёнка (Даниил), но код не завязан жёстко на один аккаунт — второй ребёнок добавляется отдельным экземпляром клиента.

## Как это работает

1. Логинится в Librus через [`librus-apix`](https://github.com/RustySnek/librus-apix).
2. Забирает текущие домашние задания и объявления.
3. Сравнивает их с уже отправленными (файл `state/seen_daniil.json`).
4. Новые — отправляет в Telegram, остальные пропускает.
5. При самом первом запуске ничего не отправляет — просто запоминает текущее состояние (чтобы не завалить чат всей историей сразу).

Пример сообщения о домашнем задании:

```
НОВОЕ ДОМАШНЕЕ ЗАДАНИЕ

Przedmiot: Matematyka
Termin wykonania: 2026-09-08 wt.
Treść: zadanie 1a, c/12
zadanie 5/14
```

## Требования

- Python 3.10+
- Аккаунт в Librus Synergia (логин/пароль, не cookie — они протухают за день)
- Telegram-бот (создать через [@BotFather](https://t.me/BotFather)), добавленный администратором в целевую группу/канал

## Переменные окружения

Скопируйте `.env.example` в `.env` и заполните реальными значениями:

```
LIBRUS_USERNAME_DANIIL=...
LIBRUS_PASSWORD_DANIIL=...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_CHAT_ID=...
```

`TELEGRAM_CHAT_ID` для группы/канала можно узнать через Bot API:
```
curl -s "https://api.telegram.org/bot<TOKEN>/getUpdates"
```
(после того как бот добавлен в чат и там есть хотя бы одно сообщение) — искать `chat.id` в ответе.

**`.env` никогда не коммитить** — он в `.gitignore`.

## Запуск локально

```
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python main.py
```

## Хостинг по расписанию

### Docker на постоянно включённом устройстве (например, Raspberry Pi) — рекомендуемый вариант

```
docker compose up -d --build
docker compose logs -f
```

Расписание реализовано внутри контейнера (`scheduler.py`), часовой пояс задаётся переменной `TZ` в `Dockerfile` (по умолчанию `Europe/Warsaw`). `state/` подключён как volume — данные переживают пересборку контейнера.

### GitHub Actions — не работает, не использовать

В репозитории есть готовый workflow (`.github/workflows/homework-notifier.yml`), но на практике Librus блокирует или сильно ограничивает трафик с облачных IP-адресов GitHub-раннеров — запросы к Librus стабильно падают по таймауту. Файл оставлен в репозитории, но полагаться на него как на способ хостинга не стоит (подробности — в `CLAUDE.md`).

**Использовать нужно только один способ хостинга одновременно** — иначе уведомления задублируются.

## Структура проекта

```
main.py                              # точка входа: логин → fetch → diff → отправка → сохранение состояния
librus_client.py                     # обёртка над librus-apix
telegram_notify.py                   # отправка и форматирование сообщений в Telegram
scheduler.py                         # планировщик для Docker-варианта
state/seen_daniil.json               # состояние дедупликации (не в git)
.github/workflows/homework-notifier.yml   # планировщик для варианта с GitHub Actions
Dockerfile / docker-compose.yml      # для Docker-варианта
```

Подробности реализации и принятые решения — в `CLAUDE.md`.
