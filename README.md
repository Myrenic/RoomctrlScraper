# RoomctrlScraper

A Python-based scraper for Roomctrl, designed to run in a Docker container and send updates via Telegram.

We recently bought a new house that is currently under construction. This scraper monitors the Roomctrl web portal and provides updates if any new information appears.

---

## Docker Compose Setup

```yaml
version: "3.9"

services:
  roomctrlscraper:
    image: ghcr.io/myrenic/roomctrlscraper:latest
    environment:
      SCAN_INTERVAL_SECONDS: 120          # Interval between scrapes in seconds
      ROOMCTRL_EMAIL: ""                  # Your Roomctrl account email
      ROOMCTRL_PASSWORD: ""               # Your Roomctrl account password
      ROOMCTRL_INSTANCE_ENDPOINT: ""      # Roomctrl instance URL
      TELEGRAM_BOT_TOKEN: ""              # Optional: Telegram bot token for notifications
      TELEGRAM_CHAT_ID: ""                # Optional: Telegram chat ID to receive messages
````

---

## Usage

1. Fill in the environment variables in `docker-compose.yml`.
2. Start the scraper:

```bash
docker compose up -d
```

3. Logs can be viewed with:

```bash
docker compose logs -f roomctrlscraper
```

---

## Configuration

* **SCAN\_INTERVAL\_SECONDS**: Adjust how often the scraper polls Roomctrl.
* **Telegram Integration**: Both `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` must be set to receive notifications.

---

## Notes

* Make sure the Roomctrl credentials are correct.
* The scraper runs under a non-root user inside the container.